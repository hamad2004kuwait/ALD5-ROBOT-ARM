# Software test results

Local automated run (Python 3.13, mocked hardware/API; not a physical test).

```text
..................................................                       [100%]
================================ tests coverage ================================
_______________ coverage: platform linux, python 3.13.5-final-0 ________________

Name                  Stmts   Miss  Cover   Missing
---------------------------------------------------
AL5D_Key_Fetcher.py     244     67    73%   42-62, 68-73, 79-174, 211-235, 297-303, 443, 449-451, 485-488, 490, 502-503, 511, 516-522
---------------------------------------------------
TOTAL                   244     67    73%
50 passed in 0.19s

```

Initial run: 49 passed, 1 failed. The article “a” was confused with Key A; corrected and regression-tested.

Live hardware, real voice recognition, timing and reliability: NOT RUN. Record individual trials in hardware_trials.csv; do not report simulated results as measured performance. Coverage measures executed Python statements, not physical safety or AI accuracy.
