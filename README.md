# AL5D AI Key Retrieval System

Python application for controlling an AL5D robotic arm through an SSC-32U serial controller. Keyboard commands and AI-assisted voice commands select one of three configurable pickup-and-return profiles.

## Setup

Requires Python 3, an AL5D arm, SSC-32U, USB serial connection and suitable power supply. Voice control also requires a microphone, internet access and an OpenAI API key. Spoken output uses macOS `say`.

```bash
python3 -m pip install -r requirements.txt
python3 GDIP_CODE.py
```

Set `PORT` to the actual controller port. The program defaults to hardware mode; set `DRY_RUN = True` to test without moving the arm. Keep the workspace clear, verify the motion path and empty the gripper before each request. Enter the API key privately when prompted; never commit it.

## Controls

Choose 1 for keyboard or 2 for microphone. A, B and C select the corresponding physical key profile; Q exits. Example voice command: “Bring me Key B.” Green indicates ready/completed, red retrieving, yellow returning.

## Software testing

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pytest -q
```

Tests run offline with simulated or mocked hardware and API responses. See [test results](documentation/Test_Results.md).

## Limitations

All three profiles currently use identical servo coordinates; distinct key positions require calibration. The system has no key-presence sensor or collision detection. Sequence completion does not prove successful pickup. No automatic key-removal confirmation is implemented. Generic pulse-width checks are not mechanical safety limits. Physical tests and live voice recognition must be verified separately. Closing the serial connection does not guarantee a moving servo stops.
