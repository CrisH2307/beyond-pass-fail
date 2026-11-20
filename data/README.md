# Data dictionary

All files are UTF-8 CSV with a header row. Item IDs are the IDs used in the paper's working files.
No raw agent trajectories, full task texts, or gold patches are included. The files hold labels, audits, and derived
metrics. The audit files keep short verbatim quotes that the audit depends on (a test line or one issue sentence per item).

## Rater mapping (read this first)

| Code | Who | Role |
|---|---|---|
| `R1` | First author (Cris Huynh) | Primary run labeler and primary auditor. Run labels for the paper use R1 unless stated. |
| `R2` | Graduate student in software engineering | Not used in the numbers reported in the paper. No `R2` labels are in this package: no R2 Terminal-Bench or Nebius label files were found in the working folders. |
| `R3` | Industry software engineer rater | Independent labeler and auditor. Used for agreement and sensitivity analyses. |
| `consensus` | R1 and R3 after discussion | Primary audit for Nebius (360 issues). |

## Sample sizes

| Dataset | Labeled runs | Audited tasks / issues | Notes |
|---|---:|---:|---|
| Terminal-Bench | 411 (311 census + 100 random) | 89 | The 411 runs stand for 1,184 failed runs (weights below). |
| Nebius | 360 | 360 consensus audits (N001 to N360) | Labeled runs are issues N081 to N440. Audits cover N001 to N360. Join on `instance_id`. |
| SWE-bench | 320 | 1,699 tasks with OpenAI ratings; 40 calibration tasks | Pass/fail for 24 submissions in `telemetry_and_scores/`. |

The Nebius benchmark has 66,647 failed runs. These fall on 3,560 issues, the pool of issues with at least one failed run. The 360 labeled runs come from 360 audited issues.

Caveat: the R3 run labels for N081 to N120 have no separate rater file. See `README.md`, section 5, item 7.

## run_labels/terminal_bench_run_labels.csv (411 rows)

| Column | Meaning |
|---|---|
| `item_id` | Label ID (L001 to L411). |
| `run_id` | FaaP run ID: `<task>__<scaffold>__<model>`. |
| `task` | Terminal-Bench task name. |
| `stratum` | `candidate` (census of 311 shortlisted runs) or `random_other` (100 random runs from the other 873). |
| `weight` | 1 for census runs; 8.73 (= 873/100) for random runs. |
| `faap_trigger`, `faap_category` | FaaP's own labels. Used for the frame only; not used for the human labels. |
| `label_v4` | Earlier label round (`labels-v4`). Kept for comparison. |
| `label_v5` | Final label used in the paper (`labels-v5.1`): `ANCHORED` (explicit), `NOT` (not explicit), `UNCLEAR`. |
| `note_v5` | Free-text note. `implicit` means the missed expectation is not written in the task text. |

Category rule (Terminal-Bench): explicit = `ANCHORED`; implicit = `NOT` with note `implicit`; other = `NOT` without that note; unclear = `UNCLEAR`.

## run_labels/nebius_run_labels.csv (360 rows)

| Column | Meaning |
|---|---|
| `item_id` | Run label ID (N081 to N440). |
| `instance_id` | SWE-bench-style issue ID (repository and PR number). |
| `model_name` | Agent model. 344 of 360 runs (96%) use `swe-agent-llama-70b`, so the Nebius results describe mostly that agent. |
| `exit_status` | How the run ended (`submitted`, or an error or limit status). |
| `R1_label` | `ANCHORED` (explicit), `NOT` (not explicit), or `UNCLEAR`. |
| `R1_note` | Free text. `implicit` marks an implicit requirement. `no_fix` marks a run with no change to project code; otherwise `NOT` runs are incorrect fixes. |
| `R3_label`, `R3_note` | Same as R1, from rater R3. |

Category rules (Nebius and SWE-bench): explicit = `ANCHORED`; implicit = `NOT` with `implicit` in the note; other = `NOT` without `implicit`.
Other splits into no fix (note starts with `no_fix` or `no fix`) and incorrect fix (everything else).

## run_labels/swebench_run_labels.csv (320 rows)

Same columns and rules as the Nebius file, without `model_name`. `item_id` is S001 to S320.
`instance_id` is the SWE-bench instance and `exit_status` is the run's exit status.

## task_audits/nebius_task_audit_{R1,R3,consensus}_N001-N360.csv (360 rows each)

| Column | Meaning |
|---|---|
| `item_id` | Issue ID (N001 to N360). |
| `hidden_requirement` | `yes` if a hidden test checks something the issue text does not state and the repository does not show. `no` otherwise. |
| `blocking` | Only meaningful when `hidden_requirement` is `yes`: `yes` (a correct solution to the written issue still fails the tests), `no`, or `unclear`. Written as `no` when `hidden_requirement` is `no`. |
| `note` | `unrelated` (the only hidden requirement is a test the issue never mentions), `contradicts` (the issue's own suggested fix fails the test), `repo shows it`, or free text. |

Group rule: blocking = `hidden_requirement` yes AND `blocking` yes; other hidden = `hidden_requirement` yes but not blocking; none = `hidden_requirement` no.
The `consensus` file keeps the row order of the working file. The RQ3 bootstrap depends on this order.

## task_audits/nebius_disagreement_resolution.csv (70 rows)

Every issue where R1 and R3 disagreed on `hidden_requirement` or `blocking` before discussion.
Columns: the R1, R3, and consensus values, and whether the consensus matches R1 and R3.
Counts: consensus changed R1 only in 46 issues, R3 only in 17, and both in 7 (where the consensus matched neither).

## task_audits/terminal_bench_task_audit.csv (89 rows)

One row per Terminal-Bench task: `task`, `hidden_requirement`, `blocking`, and the audit notes. This is the final 89-task audit used in the paper: 22 tasks with a hidden requirement, 15 blocking, 6 not blocking, and 1 unclear. The `draft_blocking` and `verified_by` columns are working-file fields kept for traceability.

## task_audits/terminal_bench_gap_types.csv (22 rows)

One row per Terminal-Bench task with a hidden requirement (the 22 tasks with `hidden_requirement` = yes). Columns: `task`, `kind_primary` and `kind_secondary` (failure-gap kinds A to E), and `why` (a short reason). Kinds: A_unstated_name, B_unstated_format, C_hidden_reference, D_text_points_other_way, E_extra_criterion. Primary kinds: 7 C, 5 A, 5 D, 4 B, 1 E. The blocking split comes from `terminal_bench_task_audit.csv`. Status: the kinds were assigned in a working draft; the authors should confirm them before publication.

## task_audits/swebench_calibration_audit_{R1,R3}.csv (40 rows each)

Blind audit of 40 SWE-bench tasks, same columns as the Nebius audit. Used for the kappa against OpenAI ratings.

## task_audits/swebench_calibration_openai_ratings.csv (40 rows)

OpenAI's ratings for the same 40 tasks: `false_negative` (0 to 3). Severe = 2 or 3.

## telemetry_and_scores/nebius_run_outcomes.csv (8,286 rows)

One row per Nebius run on an audited issue. Columns: `audit_item_id` (N001 to N360), `instance_id`, `model_name`,
`resolved` (1 if the hidden tests pass), `exit_status`. Used for RQ3.

## telemetry_and_scores/swebench_run_patch_metrics.csv (320 rows)

Per SWE-bench run (derived from the agent's final patch and the reference fix):

| Column | Meaning |
|---|---|
| `ref_file_edit` | 1 if the run edits a non-test file that the reference fix also edits. |
| `other_file_edit` | 1 if the run edits a non-test file that the reference fix does not touch (root-level new files excluded). |
| `scratch_file_added` | 1 if the run adds a new file at the repository root that the reference fix does not add. |
| `agent_changed_lines` | Changed lines in the agent's patch (added and removed). |
| `ref_changed_lines` | Changed lines in the reference fix, non-test files only. |

## telemetry_and_scores/swebench_openai_severity.csv (1,699 rows)

`ensemble_false_negative`: OpenAI's ensemble value (maximum over annotators; severe = 2 or 3). `annotator_scores`: the individual scores, separated by `;`. Source: OpenAI's public SWE-bench annotation release.

## telemetry_and_scores/swebench_resolved_by_submission.csv (40,776 rows)

For each of the 24 SWE-bench test-split submissions and each of the 1,699 tasks: `resolved` (1 or 0). Source: the public `results.json` files in the SWE-bench experiments repository.

## telemetry_and_scores/terminal_bench_run_outcomes.csv (1,794 rows)

Terminal-Bench runs: `run_id`, `task`, `system` (`scaffold__model`), `failed` (1 = failed, 0 = passed). The 1,184 failed runs match the FaaP release.

## Licence

The data files are licensed under CC BY 4.0 (see `DATA_LICENSE.md`). The source benchmarks have their own licences. Do not redistribute their raw trajectories or full task texts from this package. The short audit quotes are kept for transparency.
