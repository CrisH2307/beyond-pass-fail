# Scripts

## Environment

- Python 3.10 or newer.
- Standard library for everything except Figure 4, which needs matplotlib.
- Install: `python3 -m pip install -r requirements.txt`

## Run order

Scripts read only files in `../data/`. They can run in any order, but this order is the easiest to follow:

1. `python3 scripts/01_kappa.py`: inter-rater agreement (before discussion).
2. `python3 scripts/02_rq1.py`: RQ1 shares, Clopper-Pearson intervals, failure kinds, Nebius audit. Writes `results/rq1.md`.
3. `python3 scripts/03_rq2.py`: RQ2 Table II and ends-on-own rates. Writes `results/rq2.md`.
4. `python3 scripts/04_rq3.py`: RQ3 resolve rates, bootstrap intervals, per-system medians. Writes `results/rq3.md`.
5. `python3 scripts/05_figure4.py`: Figure 4. Writes `results/figure4.pdf` and `.png`.
6. `python3 scripts/verify.py`: runs 01 to 04 and compares every number with the paper. Exit code 0 means every check passes.

## Verifying the outputs

`verify.py` prints one line per check: the value the scripts produce, the value in the paper, and PASS or FAIL.
Percentages are compared at one decimal place. Counts and interval endpoints are compared exactly.
The last lines list the items that are not checked here (see the top-level README, section 5).

## Scripts that rebuild the data

`build_derived.py` rebuilds `../data/` from the authors' working folders. It needs those folders and `pyarrow`
(for the SWE-bench gold patches). It is not needed to reproduce the paper's numbers.

## Notes on the code

- All paths are relative to the script's folder. Nothing refers to a personal computer.
- Bootstraps use `random.Random(20260925)` and 10,000 redraws, in the same order as the original analysis.
- Clopper-Pearson intervals use bisection on the binomial CDF (exact, two-sided, 95%).
- `common.py` holds the shared helpers. Each numbered script exposes a `main()` function that `verify.py` calls.
