# AL5D AI Key Fetcher
Python keyboard and natural-language voice control for three physical keys using an SSC-32U-compatible serial controller.

## Setup
- Install Python and dependencies: `python -m pip install -r requirements.txt`.
- Run `python AL5D_Key_Fetcher.py` on macOS (uses `say`).
- Voice or conversational input requires an OpenAI API key (environment variable or masked popup).
- Select keyboard mode or microphone mode. A/B/C select the named key, Q exits. In voice mode say “Get me Key B”.

## Calibration and safety
Simulation is enabled by default. Key A uses the original coordinates; B and C are intentionally unset. Calibrate each start, pickup and return path, gripper limits, and verify physical clearance before setting the corresponding VERIFIED flag and disabling DRY_RUN. Confirm the serial port and compatible controller firmware. Start only from a known safe pose, with clear workspace and accessible physical power cutoff. Serial commands do not provide grip or position feedback. The program's confirmation is not an emergency stop. The gripper remains closed after retrieval. Safely remove the key before confirming REMOVED (keyboard R or voice “key removed”). Do not force the gripper. Real movement requires typed EXECUTE. No hardware testing has been performed.
