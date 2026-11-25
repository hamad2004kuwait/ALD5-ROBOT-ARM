import os
import time
import wave
import tempfile
import subprocess
import re
from getpass import getpass


# Robot settings (SSC-32U protocol)
PORT = "/dev/cu.usbserial-A10LLRB7"
BAUD = 115200
DRY_RUN = False  # Hardware mode; True enables simulation
MOVE_TIME = 1000
WAIT_TIME = 0.5

# Joint order: Base, Shoulder, Elbow, Wrist, Wrist Rotate
A_START = [1500, 1500, 1500, 1500, 1500]
A_PICK = [1800, 1700, 1000, 2000, 1500]
A_RETURN = [1500, 1500, 1500, 1500, 1500]
B_START = [1500, 1500, 1500, 1500, 1500]
B_PICK = [1800, 1700, 1000, 2000, 1500]
B_RETURN = [1500, 1500, 1500, 1500, 1500]
C_START = [1500, 1500, 1500, 1500, 1500]
C_PICK = [1800, 1700, 1000, 2000, 1500]
C_RETURN = [1500, 1500, 1500, 1500, 1500]
KEYS = {
    "A": (A_START, A_PICK, A_RETURN),
    "B": (B_START, B_PICK, B_RETURN),
    "C": (C_START, C_PICK, C_RETURN),
}
GRIP_OPEN = 1500
GRIP_CLOSED = 2500
GREEN_LED = 31
RED_LED = 29
YELLOW_LED = 28
LED_ACTIVE_HIGH = True

def connect_ai():

    api_key = os.getenv(
        "OPENAI_API_KEY", ""
    ).strip()

    if not api_key:
        api_key = getpass("OpenAI API key: ").strip()

    if not api_key:

        raise SystemExit(
            "No OpenAI API key entered."
        )

    from openai import OpenAI
    client = OpenAI(
        api_key=api_key.strip(),
        timeout=40.0,
        max_retries=0
    )

    return client



def speak(message):

    print("\nASSISTANT:", message)

    try:
        subprocess.run(["say", str(message)], check=False)
    except OSError:
        pass  # Text remains available if macOS speech is unavailable.



def listen(client):

    import sounddevice as sd
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

def named_keys(instruction):
    text = instruction.lower()
    found = set(re.findall(r"\bkey\s+([a-z])\b", text))
    found.update(letter for word, letter in (("first", "a"), ("second", "b"), ("third", "c")) if re.search(rf"\b{word}\s+key\b", text))
    return {letter.upper() for letter in found}


def ask_ai(client, instruction):
    # Fail closed on obvious ambiguity and negative commands.
    text = instruction.strip().lower()
    if not text or re.search(r"\b(?:do not|don't|dont|never|not|cancel|stop)\b", text):
        return "INVALID"
    keys = named_keys(text)
    if len(keys) > 1 or keys - set(KEYS) or re.search(r"\b(?:all|both|every)\s+(?:three\s+)?keys\b|\bkey\s+[abc]\s*(?:,|and|or)\s*[abc]\b", text):
        return "INVALID"
    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions="""Classify the AL5D physical key retrieval request.
Return exactly one of A, B, C, CHAT, INVALID.
A/B/C: explicit request to fetch, grab, pick up or bring that named key.
Examples: 'Get me Key A' -> A; 'Can you grab key B?' -> B;
'I need the third key' -> C. First/second/third mean A/B/C.
CHAT: general conversation or hypothetical questions.
INVALID: ambiguous, multiple keys, unsupported actions or missing key identity.
Negated, hypothetical, conditional or quoted requests must not cause movement. Never infer a key when unspecified. Never generate servo commands.""",
        input=instruction,
    )
    decision = response.output_text.strip().upper()
    if decision in KEYS:
        if keys != {decision} or re.search(r"\b(?:if|imagine|suppose|hypothetically|what happens|what would)\b", text):
            return "INVALID"
    return decision if decision in {"A", "B", "C", "CHAT", "INVALID"} else "INVALID"

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



def send(robot, command):

    if robot is None:
        if not DRY_RUN:
            raise RuntimeError("Robot is not connected.")

        print(
            "SIMULATION:",
            command.strip()
        )

        return

    payload = command.encode("ascii")
    if robot.write(payload) != len(payload):
        raise OSError("Incomplete serial write")

    robot.flush()



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



def servo(robot, channel, position):

    if type(channel) is not int or not 0 <= channel <= 5:
        raise ValueError("Invalid servo channel")
    if type(position) is not int:

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



def move(robot, positions, reverse=False):

    if len(positions) != 5 or any(type(v) is not int or not 600 <= v <= 2600 for v in positions):

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

def check_action(key):
    if key not in KEYS:
        raise ValueError("Unsupported key")
    for pose in KEYS[key]:
        if len(pose) != 5 or any(type(v) is not int or not 600 <= v <= 2600 for v in pose):
            raise ValueError(f"Key {key}: calibrate all five joint positions first.")

    for value in (GRIP_OPEN, GRIP_CLOSED):
        if type(value) is not int or not 600 <= value <= 2600:
            raise ValueError("Invalid gripper position.")


def pickup(robot, key):
    check_action(key)
    start, target, returned = KEYS[key]
    leds(robot, "RED")
    move(robot, start)
    open_gripper(robot)
    move(robot, target)
    close_gripper(robot)
    leds(robot, "YELLOW")
    move(robot, returned, reverse=True)
    leds(robot, "GREEN")
    print(f"Key {key}: pickup and return sequence completed.")


def main():
    print("AL5D AI ROBOT ARM | KEY A / KEY B / KEY C")
    mode = input("1 - Keyboard\n2 - Microphone\nChoose: ").strip()
    if mode not in {"1", "2"}:
        return
    client = connect_ai() if mode == "2" else None
    robot = None
    try:
        if not DRY_RUN:
            import serial
            robot = serial.Serial(PORT, BAUD, timeout=1, write_timeout=2)
            time.sleep(1)
        else:
            print("SIMULATION MODE")
        leds(robot, "GREEN")
        while True:
            if mode == "1":
                message = input("\nA - Key A | B - Key B | C - Key C\nQ - Quit\nOr type a question: ").strip()
            else:
                try:
                    message = listen(client)
                except Exception as error:
                    print("Microphone/transcription error:", type(error).__name__)
                    continue
            if not message:
                continue
            normalized = message.strip().lower().rstrip(".!?")
            if normalized in {"q", "quit", "exit", "stop program"}:
                break
            if mode == "1" and message.upper() in KEYS:
                action = message.upper()
            else:
                if client is None:
                    client = connect_ai()
                try:
                    action = ask_ai(client, message)
                except Exception as error:
                    print("AI request failed:", type(error).__name__)
                    continue
            print("AI DECISION:", action)
            if action == "CHAT":
                try:
                    chat(client, message)
                except Exception as error:
                    print("AI chat failed:", type(error).__name__)
            elif action == "INVALID":
                speak("Please specify Key A, Key B or Key C.")
            elif action in KEYS:
                check_action(action)
                speak(f"Retrieving Key {action}.")
                # Stop the session on movement errors; do not allow another pickup
                # when the physical position or gripper state is unknown.
                pickup(robot, action)
                speak(f"Key {action} pickup and return sequence {'simulated' if DRY_RUN else 'completed'}.")
    finally:
        if robot is not None:
            try:
                leds(robot, "OFF")
            except Exception:
                pass
            finally:
                robot.close()
        print("PROGRAM CLOSED")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Program interrupted. Check the robot before restarting.")
    except Exception as error:
        print("ERROR:", type(error).__name__, error)
        print("Check robot position and gripper before restarting.")
