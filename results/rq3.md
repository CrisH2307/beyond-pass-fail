## RQ3, Nebius (per-issue resolve rate, mean over issues, 95% bootstrap CI)
- Consensus audit (primary): blocking 155/360 (43.1%); resolve blocking 0.6 vs none 17.1 (n = 168); diff -16.5 [-20.8, -12.3]
    per system (3): failures on blocking median 28.3 (range 13.2-37.2); gain median +6.5 (range +3.3, +6.5)
- R1 audit before discussion: blocking 185/360 (51.4%); resolve blocking 0.4 vs none 18.6 (n = 154); diff -18.2 [-22.9, -13.9]
    per system (3): failures on blocking median 37.3 (range 23.7-46.7); gain median +9.3 (range +5.2, +9.3)
- R3 audit before discussion: blocking 144/360 (40.0%); resolve blocking 0.7 vs none 16.8 (n = 167); diff -16.1 [-20.5, -11.9]
    per system (3): failures on blocking median 27.2 (range 13.2-35.2); gain median +6.0 (range +3.3, +6.1)

## RQ3, SWE-bench (OpenAI severity as blocking proxy, 24 submissions)
- Severe tasks 1039/1699; resolve severe 11.9 vs none 37.4 (n = 382); diff -25.5 [-28.2, -22.8]
    per system (24): failures on severe median 68.1 (range 61.2-80.6); gain median +14.2 (range +0.1, +25.6)

## RQ3, Terminal-Bench (description only; no bootstrap, as in the paper)
- Blocking tasks in the audit: 15 of 89
- Runs on blocking tasks: 290
- Resolve (pass) rate, mean of task rates: blocking 10.2 vs none 40.9; diff -30.6
- Per system (21): failures on blocking median 21.7 (range 17.1-25.9); gain median +4.4 (range +2.4, +7.1)

