# Replication package: "Beyond Pass/Fail: Separating Agent Errors from Unspecified Requirements in Coding-Agent Failures"

This package reproduces the tables, the figure, and the inline statistics of the paper from derived data.
It runs on Python 3.10 or newer. Only matplotlib is needed outside the standard library.

## 1. What the study does

Coding agents fail on benchmark tasks for two different reasons. Sometimes the agent does not do something the
task text asks for (an explicit requirement failure). Sometimes the hidden tests check something the task text
never states (an implicit requirement). We label failed runs on three sources, and we audit tasks for hidden
requirements that block a correct solution.

| Source | Failed runs labeled | Tasks audited | Role in the paper |
|---|---:|---:|---|
| Terminal-Bench (FaaP runs) | 411 (311 census + 100 random, weighted 873/100 to 1,184 failed runs) | 89 | RQ1, RQ2, RQ3 |
| Nebius SWE-agent runs | 360 labeled runs | 360 audited issues (70 disagreements resolved) | RQ1, RQ3 |
| SWE-bench (24 submissions) | 320 labeled runs (plus 40-task calibration audit) | 1,699 tasks rated by OpenAI (proxy) | RQ1, RQ2, RQ3 |

Research questions (short form):
- **RQ1.** How often is the broken requirement explicit, implicit, or neither?
- **RQ2.** How do explicit and implicit failures unfold in the agent's run (which file is edited, how much code, how the run ends)?
- **RQ3.** How often do benchmark tasks have blocking hidden requirements, and how much do they lower resolve rates?

## 2. Directory layout

```
replication_package/
  README.md                 this file
  LICENSE                   MIT license for the code in scripts/
  DATA_LICENSE.md           CC BY 4.0 for the files in data/
  requirements.txt          matplotlib (Figure 4 only)
  protocols/
    ANNOTATION_PROTOCOL.md  run-lane labeling, task-lane audit, adjudication
    ANALYSIS_PLANS.md       frozen analysis plans, tags, and documented deviations
  data/
    README.md               data dictionary, sample sizes, rater mapping
    run_labels/             run-level labels (Terminal-Bench, Nebius, SWE-bench)
    task_audits/            task-level audits, calibration audit, disagreement resolution
    telemetry_and_scores/   derived metrics: patch metrics, run outcomes, OpenAI ratings, resolved lists
  scripts/
    README.md               environment, run order, verification
    common.py               shared helpers (paths, Clopper-Pearson, kappa)
    01_kappa.py             inter-rater agreement (before discussion)
    02_rq1.py               RQ1 shares, intervals, failure kinds, Nebius audit
    03_rq2.py               RQ2 patch metrics (Table II) and ends-on-own rates
    04_rq3.py               RQ3 resolve rates, bootstrap intervals, per-system gains
    05_figure4.py           Figure 4
    verify.py               runs 01 to 04 and checks every number against the paper
    build_derived.py        rebuilds data/ from the authors' raw working folders (not needed to reproduce)
  results/                  written by the scripts (tables as Markdown, figure as PDF and PNG)
```

## 3. Mapping: every table, figure and statistic to its script and data

### Tables

| Paper item | What it shows | Script | Data file(s) |
|---|---|---|---|
| Table I | Sample sizes: failed runs, labeled runs, audited tasks, total | `verify.py` (Table I checks), `02_rq1.py` | `data/run_labels/*.csv`, `data/task_audits/*.csv`, `data/telemetry_and_scores/nebius_run_outcomes.csv` |
| Table II | SWE-bench patch metrics by failure kind (reference file, other file, scratch file, lines) and ends-on-own rates | `03_rq2.py` | `data/telemetry_and_scores/swebench_run_patch_metrics.csv`, `data/run_labels/swebench_run_labels.csv`, `data/run_labels/nebius_run_labels.csv` |
| Table III | Blocking tasks, resolve rates on blocking and other tasks, difference with CI, per-system medians and ranges | `04_rq3.py` | `data/task_audits/nebius_task_audit_consensus_N001-N360.csv`, `data/telemetry_and_scores/nebius_run_outcomes.csv`, `data/telemetry_and_scores/swebench_openai_severity.csv`, `data/telemetry_and_scores/swebench_resolved_by_submission.csv`, `data/task_audits/terminal_bench_task_audit.csv`, `data/telemetry_and_scores/terminal_bench_run_outcomes.csv` |

### Figure

| Paper item | Script | Output |
|---|---|---|
| Figure 4 | `05_figure4.py` | `results/figure4.pdf`, `results/figure4.png` (reads the numbers from `02_rq1.py`) |

### Inline statistics

| Statistic in the paper | Script | Verified |
|---|---|---|
| Terminal-Bench Explicit 30.1% [24.4, 37.0], Implicit 5.5% [4.7, 8.7], Other 64.1% [57.1, 69.9] | `02_rq1.py` | yes |
| Nebius Explicit 17.2%, Implicit 15.8% [12.2, 20.0], Other 66.9%; incorrect fix 32.8%, no fix 34.2% | `02_rq1.py` | yes |
| SWE-bench Explicit 11.6%, Implicit 23.8% [19.2, 28.8], Other 64.7%; incorrect fix 40.9%, no fix 23.8% | `02_rq1.py` | yes |
| Nebius audit: implicit requirement in 53.3% (192 issues); blocking 155 (43.1%) | `02_rq1.py` | yes |
| Run-label kappa: Nebius 0.73, SWE-bench 0.76 (agreement 87.2% and 87.8%) | `01_kappa.py` | yes |
| Audit kappa: implicit 0.83, blocking 0.71 | `01_kappa.py` | yes |
| SWE-bench calibration: kappa vs OpenAI 0.15 (R1) and 0.38 (R3); OpenAI severe 22 of 40 | `01_kappa.py` | yes |
| 70 audit disagreements; R1 changed 46, R3 changed 17, both 7 | `verify.py` (from `task_audits/nebius_disagreement_resolution.csv`) | yes |
| RQ2 Table II values and ends-on-own rates (SWE-bench and Nebius) | `03_rq2.py` | yes |
| RQ3 Nebius: 155/360 blocking, 0.6 vs 17.1, diff -16.5 [-20.8, -12.3]; per-system median 28.3 and gain +6.5 | `04_rq3.py` | yes |
| RQ3 SWE-bench: 1,039/1,699 severe, 11.9 vs 37.4, diff -25.5 [-28.2, -22.8]; per-system median 68.1 and gain +14.2 | `04_rq3.py` | yes |
| RQ3 Terminal-Bench: 15/89 blocking, 290 runs, 10.2 vs 40.9, diff -30.6; per-system 21.7 and +4.4 | `04_rq3.py` | yes |
| Terminal-Bench awareness 89.3% (implicit) vs 70.1% (explicit); 311-run and 411-run versions | not included | no (see section 5) |
| Test-execution counts (12% and 3% project suite; 64% and 67% own script) | not included | no (see section 5) |
| Terminal-Bench run-label kappa (0.63, 0.74) | not included | no (see section 5) |
| Terminal-Bench gap types and FaaP taxonomy cross-tabulation | not included | no (see section 5) |

## 4. How to reproduce every number

```bash
cd replication_package
python3 -m pip install -r requirements.txt   # matplotlib only; skip if you only need the numbers
python3 scripts/verify.py                    # runs 01 to 04 and prints PASS/FAIL for each paper number
python3 scripts/05_figure4.py                # writes results/figure4.pdf and .png
```

Each script writes its table to `results/` when run on its own (for example, `python3 scripts/02_rq1.py`).
Results are deterministic: every bootstrap uses the fixed seed 20260925, and the scripts read only files in `data/`.
Scripts use relative paths and can be run from any folder.

## 5. Known gaps and open items

These items are not in this package. They are listed so readers know what is and is not reproduced.

1. **Terminal-Bench awareness and test-execution numbers.** The awareness comparison (89.3% vs 70.1%, kappa 0.80)
   and the test-execution counts (project suite 9.4% to 12.2% SWE-bench and 3.1% Nebius; own script 63.8% and 67.2%)
   come from scripts that are not in this package yet. The test-execution counts come from the FaaP
   analysis scripts (`FINDING_2_4` files), which were not found in the working folders.
2. **Terminal-Bench run-label kappa (0.63 and 0.74).** Neither value can be recomputed from the working files. The 0.63 is R2 against Cris on 92 runs before discussion. The working folder holds R2's labels only as a partial `.numbers` export, which has 29 disagreement rows. The 0.74 is R3's blind second reading of 60 runs. The R3 label column in the working file is empty. The agreement report's figure of 0.54 is on a 100-run subset (L001 to L100) and does not match the paper.
3. **Terminal-Bench gap types and FaaP shares.** The gap types now reproduce from `data/task_audits/terminal_bench_gap_types.csv` (22 tasks: 7, 5, 5, 4, 1 by primary kind; 15 blocking). The primary kinds come from a working draft, so the authors should confirm them. The FaaP shares 46.1% (shortlist) and 23.6% (spec_neglect) reproduce in `scripts/02_rq1.py`. The 76% figure and the FaaP intervals do not appear in the working folders.
4. **Terminal-Bench labels version.** The paper numbers come from the `labels-v5.1` version (git tag `labels-v5.1`, file `labels/labels_v5.csv`).
   The earlier `labels-v5` tag gives 29.3% explicit, not 30.1%.
5. **Figure 4.** The earlier figure script in the working folder used older Nebius numbers (32.5%, 30.0%, 37.5%) that do not match the final values.
   `05_figure4.py` plots the final RQ1 shares. Check that its layout matches the figure in the paper before publishing.
6. **Nebius run count in Table I.** The Nebius benchmark has 66,647 failed runs. These fall on 3,560 issues, the pool of issues with at least one failed run (see `protocols/ANALYSIS_PLANS.md`).
   The 360 labeled runs come from 360 audited issues. Table I should state 3,560 as the issue pool, not as a count of failed runs.
7. **Nebius R3 run labels for N081 to N120 (authors to confirm).** The sensitivity file is `labeling_sheet_N081-N120_cris_v2_alt.csv`. The working notes (`wp5_nebius/analysis/DEVIATIONS.md`, entry dated 2026-11-04) describe it as the third rater's v2 labels. It contains none of the test identifiers that appear in Cris's v1 notes, which has two. No other R3 file for these runs exists, so the file stays in place and the numbers are unchanged. The Nebius run-label kappa (0.73) and the R3 implicit share (13.1%) include these 40 runs. The authors should confirm that the file name, which contains `cris`, is correct.
8. **Rater R2 (no labels in package).** R2 is a graduate student in software engineering. No R2 run labels, Terminal-Bench labels included, were found in the working folders, so the package reports R1 and R3 only.

## 6. Provenance

- Derived data were built from the authors' working repository by `scripts/build_derived.py` (run once; raw inputs are not redistributed).
- Git tags in the working repository: `labels-v5.1` (Terminal-Bench labels used in the paper), `rq1-plan-frozen`,
  `rq3-addendum-frozen`, `nebius-plan-frozen`, and `rq2-rq3-addendum-frozen` (see `protocols/ANALYSIS_PLANS.md`).
- Final consensus audit: `task_audit_N001-N360_consensus.csv`, from the 2026-11-14 to 2026-11-15 round.
- Bootstrap and random seeds: 20260925 throughout.

## 7. Contact and citation

Author: Cris Huynh (first author, rater R1). Questions about the data or scripts: open an issue in the repository.
Please cite the paper when you reuse the data or scripts.
# beyond-pass-fail
