# Verification and validation plan

Automated tests: `python -m pytest -q --cov=AL5D_Key_Fetcher --cov-report=term-missing`.
Mocks replace the serial controller and AI service. Test categories: unit, boundary, edge case, regression, simulated integration. Live API, microphone, physical travel and gripper behavior require separate tests.

| ID | Physical / live test | Proposed acceptance criterion |
|---|---|---|
| HW01 | Calibrate A, B and C individually | No collisions or joint binding; approved poses recorded |
| HW02 | Keyboard A/B/C, 10 trials each | 9/10 or better per key; no unsafe motion |
| HW03 | Voice A/B/C, 10 trials each | 9/10 or better per key; no wrong-key movement |
| HW04 | Silence, noise, negation, hypothetical, unknown and multiple keys | Zero unintended motion; conduct with motors isolated first |
| HW05 | Verify LED transitions and return poses | Correct sequence on every trial |
| HW06 | Key already held | Second pickup blocked until manual removal confirmed |
| HW07 | API/network/microphone failure | No new movement; clear failure report |
| HW08 | Serial loss and interruption | No further commands; verify isolation and supervised recovery, initially unloaded |
| HW09 | Measure recognition and retrieval times | Record individual times; report median and range |
| HW10 | User acceptance demonstration | Operator can fetch each key and reject ambiguous requests |

Targets above are proposed, not university requirements. Confirm with supervisor. Never induce a live fault with a person or fragile object in reach. Record every failure; retest after corrections.
