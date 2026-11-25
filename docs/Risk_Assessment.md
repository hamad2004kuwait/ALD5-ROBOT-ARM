# Preliminary risk assessment (not signed off)

Scale: likelihood (L) and severity (S), 1–5; risk = L×S. Suggested bands: 1–4 low, 5–9 medium, 10–16 high, 17–25 very high. Ratings are provisional before controls; residual scores require physical assessment.

| Hazard | L | S | Score | Controls / verification |
|---|---:|---:|---:|---|
| Pinch/crush at joints or gripper | 3 | 4 | 12 | Clear work envelope, supervision, accessible isolation |
| Joint collision or overtravel | 3 | 4 | 12 | Per-joint calibration, verified paths, conservative speeds |
| Dropped key | 3 | 2 | 6 | Clear landing area, visual verification |
| Misclassified voice command | 3 | 4 | 12 | Allowlist, ambiguity checks, manual confirmation |
| Communication loss or interrupted motion | 3 | 4 | 12 | Stop further commands, isolate power, inspect before restart |
| Electrical fault or overheating | 2 | 4 | 8 | Correct rated supply, wiring inspection, current protection |
| Exposed API credentials | 2 | 3 | 6 | Environment variable or masked prompt; never commit secrets |
| Audio privacy | 2 | 2 | 4 | Inform participants; audio sent to transcription service; temporary local file removed |

Owner: project operator. Supervisor approval, residual risk and laboratory-specific requirements pending. Simulation is not physical safety certification.
