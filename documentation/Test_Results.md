# Test results

## Automated software verification

Automated testing was conducted on the repository's GDIP_CODE.py using Python and pytest, achieving 49 passed, 0 failed. The automated tests utilised simulated operation, mocked serial communication and API responses to verify software functionality. Additional physical hardware and live-service validation was conducted separately using the AL5D robotic arm, with all eight validation tests successfully passed.

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
| H05 | Invalid voice input | No movement | Pass |
| H06 | Repeat retrieval with empty gripper | Consistent pickup and return | Pass |
| H07 | LED indicators | Red, yellow, green in order | Pass |
| H08 | Retrieval duration | Record seconds for each trial | Pass |

All physical and live-service validation tests were successfully completed and verified on the physical AL5D robotic arm. All eight tests passed, confirming that the system meets the specified functional requirements. The results documented above reflect the current system revision.
