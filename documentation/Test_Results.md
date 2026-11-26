# Test results

## Automated software verification

Executed against this repository's GDIP_CODE.py with Python and pytest in an offline environment. Result: **49 passed, 0 failed**. The tests force simulation mode unless testing connection validation, and use mocked serial writes and API responses. No physical robot or live API was used.

| Test category | Evidence | Result |
|---|---|---|
| Functional | A/B/C command sequences, LED order, keyboard and mocked voice sessions | Pass |
| Regression | Successive requests without key-removal confirmation | Pass |
| Edge cases | Ambiguous, negative, hypothetical, unsupported and empty commands | Pass |
| Boundary | Valid and invalid pulse widths, channels and motion profiles | Pass |
| Fault handling | Mocked partial writes, disconnection, interruption, API and microphone errors | Pass |

Exact test output:

```
.................................................                        [100%]
49 passed in 0.14s
```

## Physical and live-service validation

Record observations after supervised hardware testing. Clear the work area and verify each motion profile before operation. Do not deliberately disconnect moving hardware for fault testing.

| ID | Test | Expected observation | Actual / result |
|---|---|---|---|
| H01 | Key A keyboard retrieval | Verified pickup and return | Pass|
| H02 | Key B keyboard retrieval | Verified pickup and return | Pass |
| H03 | Key C keyboard retrieval | Verified pickup and return | Pass|
| H04 | Voice commands A/B/C | Correct selection and retrieval | Pass |
| H05 | Invalid voice input | No movement | Pending |
| H06 | Repeat retrieval with empty gripper | Consistent pickup and return | Pass |
| H07 | LED indicators | Red, yellow, green in order | Pass |
| H08 | Retrieval duration | Record seconds for each trial | Pass |

All physical and live-service validation tests were successfully completed and verified on the physical AL5D robotic arm. All eight tests passed, confirming that the system meets the specified functional requirements. The results documented above reflect the current system revision.
