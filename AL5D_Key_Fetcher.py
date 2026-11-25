import os
import time
import wave
import tempfile
import subprocess
import tkinter as tk

from tkinter import simpledialog

import serial
import sounddevice as sd

from openai import OpenAI


# ==================================================
# 1. ROBOT SETTINGS
# ==================================================

PORT = "/dev/cu.usbserial-A10LLRB7"

BAUD = 115200

# False = Real robot
# True = Simulation

DRY_RUN = False

# Only set True after physically verifying movements

PICK_VERIFIED = True
DROP_VERIFIED = True

# Servo movement time in milliseconds

MOVE_TIME = 1000

# Pause between movements in seconds

WAIT_TIME = 0.5


# ==================================================
# 2. OPTION A - PICK UP KEY AND HOLD IT
# ==================================================

# Joint order:
# Base, Shoulder, Elbow, Wrist, Wrist Rotate

A_START = [
    1500,
    1500,
    1500,
    1500,
    1500
]

A_PICK = [
    1800,
    1700,
    1000,
    2000,
    1500
]

A_RETURN = [
    1500,
    1500,
    1500,
    1500,
    1500
]


# ==================================================
# 3. OPTION B - PICK UP AND DELIVER KEY
# ==================================================

B_START = [
    1500,
    1500,
    1500,
    1500,
    1500
]

B_PICK = [
    1800,
    1700,
    1000,
    2000,
    1500
]

# Delivery position
# Calibrate according to your robot setup

B_DELIVER = [
    1500,
    1500,
    1500,
    1500,
    1500
]

B_RETURN = [
    1500,
    1500,
    1500,
    1500,
    1500
]


# ==================================================
# 4. GRIPPER SETTINGS
# ==================================================

# Channel 5

GRIP_OPEN = 1500

GRIP_CLOSED = 2500


# ==================================================
# 5. LED SETTINGS
# ==================================================

GREEN_LED = 31

RED_LED = 29

YELLOW_LED = 28

# True = HIGH turns LED on
# False = LOW turns LED on

LED_ACTIVE_HIGH = True


# ==================================================
# 6. CONNECT TO OPENAI
# ==================================================

def connect_ai():

    api_key = os.getenv(
        "OPENAI_API_KEY", ""
    ).strip()

    if not api_key:

        root = tk.Tk()

        root.withdraw()

        api_key = simpledialog.askstring(
            "AL5D AI Robot",
            "Enter your OpenAI API key:",
            show="*",
            parent=root
        )

        root.destroy()

    if not api_key:

        raise SystemExit(
            "No OpenAI API key entered."
        )

    client = OpenAI(
        api_key=api_key.strip(),
        timeout=40.0,
        max_retries=0
    )

    return client


# ==================================================
# 7. AI TEXT TO SPEECH
# ==================================================

def speak(message):

    print("\nASSISTANT:", message)

    subprocess.run(
        ["say", str(message)],
        check=False
    )


# ==================================================
# 8. MICROPHONE RECORDING
# ==================================================

def listen(client):

    print("\nMICROPHONE MODE")

    input(
        "Press ENTER to begin recording..."
    )

    duration = 5

    # Use the default microphone

    device = sd.query_devices(
        kind="input"
    )

    sample_rate = int(
        device["default_samplerate"]
    )

    print(
        "\nRecording for 5 seconds. Speak now!"
    )

    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16"
    )

    sd.wait()

    print("Recording completed!")

    if not audio.any():

        print(
            "No microphone audio received."
        )

        return ""

    with tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    ) as temp:

        filename = temp.name

    try:

        with wave.open(
            filename, "wb"
        ) as wav:

            wav.setnchannels(1)

            wav.setsampwidth(2)

            wav.setframerate(
                sample_rate
            )

            wav.writeframes(
                audio.tobytes()
            )

        print(
            "\nConverting speech to text..."
        )

        with open(
            filename, "rb"
        ) as file:

            result = (
                client.audio.transcriptions.create(
                    model="gpt-4o-mini-transcribe",
                    file=file
                )
            )

        instruction = result.text.strip()

        print(
            "\nYOU SAID:",
            instruction
        )

        return instruction

    finally:

        if os.path.exists(filename):

            os.remove(filename)


# ==================================================
# 9. AI TASK CLASSIFICATION
# ==================================================

def ask_ai(client, instruction):

    response = client.responses.create(

        model="gpt-4.1-mini",

        instructions="""
        You are the task classifier for an
        AL5D robotic key-fetching assistant.

        Classify the user's instruction into
        exactly ONE of four categories:

        PICK_ONLY:
        Explicit request to pick up or hold
        a key without delivering it.

        PICK_AND_DROP:
        Explicit request to pick up, deliver,
        drop off, or release a key.

        CHAT:
        General questions, greetings,
        explanations, jokes or conversation.

        INVALID:
        Unclear instructions or unsupported
        physical robot actions.

        Respond with exactly one category name.

        Never classify hypothetical questions
        about the robot as movement commands.

        Never generate servo coordinates.
        """,

        input=instruction
    )

    decision = (
        response.output_text.strip().upper()
    )

    if decision in (
        "PICK_ONLY",
        "PICK_AND_DROP",
        "CHAT"
    ):

        return decision

    return "INVALID"


# ==================================================
# 10. GENERAL AI CONVERSATION
# ==================================================

def chat(client, question):

    response = client.responses.create(

        model="gpt-4.1-mini",

        instructions="""
        You are a friendly voice assistant
        integrated into an AL5D robot.

        Answer questions naturally.

        Keep answers reasonably short
        because they will be spoken aloud.

        Do not claim to have physically moved
        the robot unless movement was executed.

        Do not generate motor commands.
        """,

        input=question
    )

    answer = response.output_text.strip()

    speak(answer)


# ==================================================
# 11. SEND COMMANDS TO ROBOT
# ==================================================

def send(robot, command):

    if robot is None:

        print(
            "SIMULATION:",
            command.strip()
        )

        return

    robot.write(
        command.encode("ascii")
    )

    robot.flush()


# ==================================================
# 12. LED CONTROL
# ==================================================

def leds(robot, status):

    on = (
        "H"
        if LED_ACTIVE_HIGH
        else "L"
    )

    off = (
        "L"
        if LED_ACTIVE_HIGH
        else "H"
    )

    # Turn off all LEDs first

    for channel in (
        GREEN_LED,
        RED_LED,
        YELLOW_LED
    ):

        send(
            robot,
            f"#{channel}{off}\r"
        )

    if status == "GREEN":

        channel = GREEN_LED

    elif status == "RED":

        channel = RED_LED

    elif status == "YELLOW":

        channel = YELLOW_LED

    elif status == "OFF":

        return

    else:

        raise ValueError(
            "Unknown LED status"
        )

    send(
        robot,
        f"#{channel}{on}\r"
    )

    print(
        "LED:",
        status
    )


# ==================================================
# 13. MOVE ONE SERVO
# ==================================================

def servo(robot, channel, position):

    if not isinstance(position, int):

        raise ValueError(
            "Servo position must be an integer"
        )

    if not 600 <= position <= 2600:

        raise ValueError(
            "Servo position outside limits"
        )

    command = (
        f"#{channel}P{position}T{MOVE_TIME}\r"
    )

    print(
        f"SERVO {channel}: {position}"
    )

    send(
        robot,
        command
    )

    if robot is not None:

        time.sleep(
            MOVE_TIME / 1000
        )


# ==================================================
# 14. MOVE ROBOT TO A POSITION
# ==================================================

def move(robot, positions, reverse=False):

    if len(positions) != 5:

        raise ValueError(
            "Position must contain 5 values"
        )

    if reverse:

        channels = range(
            4, -1, -1
        )

    else:

        channels = range(5)

    for channel in channels:

        servo(
            robot,
            channel,
            positions[channel]
        )

        if robot is not None:

            time.sleep(
                WAIT_TIME
            )


# ==================================================
# 15. GRIPPER CONTROL
# ==================================================

def open_gripper(robot):

    print(
        "\nOPENING GRIPPER"
    )

    servo(
        robot,
        5,
        GRIP_OPEN
    )


def close_gripper(robot):

    print(
        "\nCLOSING GRIPPER"
    )

    servo(
        robot,
        5,
        GRIP_CLOSED
    )


# ==================================================
# 16. OPTION A - PICK UP AND HOLD
# ==================================================

def option_a(robot):

    print(
        "\n================================"
    )

    print(
        "OPTION A: PICK UP AND HOLD"
    )

    print(
        "================================"
    )

    leds(
        robot,
        "RED"
    )

    # Move to starting position

    print(
        "\nMOVING TO START"
    )

    move(
        robot,
        A_START
    )

    # Open gripper

    open_gripper(robot)

    # Move toward key

    print(
        "\nMOVING TO KEY"
    )

    move(
        robot,
        A_PICK
    )

    # Grab key

    close_gripper(robot)

    # Return home while holding key

    print(
        "\nRETURNING HOME WITH KEY"
    )

    move(
        robot,
        A_RETURN,
        reverse=True
    )

    # Keep gripper closed

    leds(
        robot,
        "GREEN"
    )

    if robot is None:

        speak(
            "Pickup sequence simulated."
        )

    else:

        speak(
            "I picked up the key "
            "and I am holding it."
        )

    print(
        "\nOPTION A COMPLETE!"
    )


# ==================================================
# 17. OPTION B - PICK UP AND DELIVER
# ==================================================

def option_b(robot):

    print(
        "\n================================"
    )

    print(
        "OPTION B: PICK UP AND DELIVER"
    )

    print(
        "================================"
    )

    leds(
        robot,
        "RED"
    )

    # Move to starting position

    print(
        "\nMOVING TO START"
    )

    move(
        robot,
        B_START
    )

    # Open gripper

    open_gripper(robot)

    # Move toward key

    print(
        "\nMOVING TO KEY"
    )

    move(
        robot,
        B_PICK
    )

    # Grab key

    close_gripper(robot)

    # Change LED to yellow

    leds(
        robot,
        "YELLOW"
    )

    # Move to delivery position

    print(
        "\nMOVING TO DELIVERY POSITION"
    )

    move(
        robot,
        B_DELIVER,
        reverse=True
    )

    # Release key

    open_gripper(robot)

    # Return home

    print(
        "\nRETURNING HOME"
    )

    move(
        robot,
        B_RETURN
    )

    leds(
        robot,
        "GREEN"
    )

    if robot is None:

        speak(
            "Delivery sequence simulated."
        )

    else:

        speak(
            "I have delivered the key."
        )

    print(
        "\nOPTION B COMPLETE!"
    )


# ==================================================
# 18. CHECK ROBOT SETTINGS
# ==================================================

def check_action(action):

    positions = [
        A_START,
        A_PICK,
        A_RETURN,
        B_START,
        B_PICK,
        B_DELIVER,
        B_RETURN
    ]

    for position in positions:

        if len(position) != 5:

            raise ValueError(
                "Every position needs 5 values"
            )

        for value in position:

            if (
                type(value) is not int
                or not 600 <= value <= 2600
            ):

                raise ValueError(
                    "Invalid servo position"
                )

    if DRY_RUN:

        return

    if not PICK_VERIFIED:

        raise RuntimeError(
            "Pickup has not been verified"
        )

    if (
        action == "PICK_AND_DROP"
        and not DROP_VERIFIED
    ):

        raise RuntimeError(
            "Delivery has not been verified"
        )


# ==================================================
# 19. MAIN PROGRAM
# ==================================================

def main():

    print(
        "\n==================================="
    )

    print(
        "       AL5D AI ROBOT ARM"
    )

    print(
        "==================================="
    )

    client = connect_ai()

    print(
        "\nChoose input method:"
    )

    print(
        "1 - Keyboard"
    )

    print(
        "2 - Microphone"
    )

    mode = input(
        "\nChoose: "
    ).strip()

    if mode not in (
        "1",
        "2"
    ):

        print(
            "Invalid input mode"
        )

        return

    robot = None

    try:

        # Connect to SSC-32U

        if not DRY_RUN:

            print(
                "\nConnecting to SSC-32U..."
            )

            robot = serial.Serial(
                PORT,
                BAUD,
                timeout=1
            )

            time.sleep(1)

            print(
                "\nROBOT CONNECTED!"
            )

        else:

            print(
                "\nSIMULATION MODE ENABLED"
            )

        # Green means ready

        leds(
            robot,
            "GREEN"
        )

        # ==================================
        # MAIN CONTROL LOOP
        # ==================================

        while True:

            # ==================================
            # KEYBOARD MODE
            # ==================================

            if mode == "1":

                print(
                    "\n==================================="
                )

                print(
                    "         ROBOT OPTIONS"
                )

                print(
                    "==================================="
                )

                print(
                    "A - Pick up key and HOLD it"
                )

                print(
                    "B - Pick up key and DELIVER it"
                )

                print(
                    "Q - Quit program"
                )

                print(
                    "\nYou can also type a question"
                )

                print(
                    "to talk to the AI assistant."
                )

                print(
                    "==================================="
                )

                message = input(
                    "\nSelect A, B, Q or type a question: "
                ).strip()

            # ==================================
            # MICROPHONE MODE
            # ==================================

            else:

                message = listen(
                    client
                )

            if not message:

                continue

            # Exit

            if message.lower() in (
                "q",
                "quit",
                "exit",
                "stop program"
            ):

                break

            # ==================================
            # CLASSIFY INSTRUCTION
            # ==================================

            if message.upper() == "A":

                action = "PICK_ONLY"

            elif message.upper() == "B":

                action = "PICK_AND_DROP"

            else:

                print(
                    "\nContacting OpenAI..."
                )

                action = ask_ai(
                    client,
                    message
                )

            print(
                "\nAI DECISION:",
                action
            )

            # ==================================
            # GENERAL CONVERSATION
            # ==================================

            if action == "CHAT":

                chat(
                    client,
                    message
                )

            # ==================================
            # INVALID INSTRUCTION
            # ==================================

            elif action == "INVALID":

                speak(
                    "I cannot perform that movement."
                )

            # ==================================
            # OPTION A
            # ==================================

            elif action == "PICK_ONLY":

                try:

                    check_action(
                        action
                    )

                    if not DRY_RUN:

                        print(
                            "\nOPTION A SELECTED"
                        )

                        print(
                            "Pick up and hold the key."
                        )

                        confirm = input(
                            "\nType EXECUTE to move: "
                        )

                        if confirm.strip() != "EXECUTE":

                            print(
                                "\nMovement cancelled."
                            )

                            continue

                    option_a(
                        robot
                    )

                except Exception as error:

                    print(
                        "\nROBOT ERROR:",
                        error
                    )

                    leds(
                        robot,
                        "GREEN"
                    )

            # ==================================
            # OPTION B
            # ==================================

            elif action == "PICK_AND_DROP":

                try:

                    check_action(
                        action
                    )

                    if not DRY_RUN:

                        print(
                            "\nOPTION B SELECTED"
                        )

                        print(
                            "Pick up and deliver the key."
                        )

                        confirm = input(
                            "\nType EXECUTE to move: "
                        )

                        if confirm.strip() != "EXECUTE":

                            print(
                                "\nMovement cancelled."
                            )

                            continue

                    option_b(
                        robot
                    )

                except Exception as error:

                    print(
                        "\nROBOT ERROR:",
                        error
                    )

                    leds(
                        robot,
                        "GREEN"
                    )

    finally:

        if robot is not None:

            leds(
                robot,
                "OFF"
            )

            robot.close()

        print(
            "\nPROGRAM CLOSED"
        )


# ==================================================
# 20. START PROGRAM
# ==================================================

if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print(
            "\nProgram stopped."
        )

        print(
            "Check the robot before restarting."
        )

    except Exception as error:

        print(
            "\nERROR:",
            type(error).__name__,
            error
        )