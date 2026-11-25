# User manual

1. Create a Python virtual environment and install `requirements.txt`.
2. Run `python AL5D_Key_Fetcher.py` in VS Code. Simulation is enabled by default.
3. Choose keyboard (1) or microphone (2). Voice requires an OpenAI API key and microphone permission. The terminal API key prompt hides input.
4. Select A/B/C or say “Pick up Key A”, “Bring me Key B”, or “I need the third key”. B/C are blocked until calibrated. General questions do not execute servo commands.
5. For real hardware, confirm controller/port, inspect wiring and approve poses and limits under supervision before setting VERIFIED and disabling DRY_RUN. Type EXECUTE only when the area is clear.
6. After a key is retrieved, safely remove it using the approved laboratory procedure; use R (or say “key removed”) and type REMOVED to confirm. Never force a powered gripper.
7. Q quits. On a fault, isolate power as appropriate and inspect before restarting. Quitting does not de-energize servos.
