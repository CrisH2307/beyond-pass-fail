# Analysis plans, freezes, and deviations

## Pre-specified analyses reproduced here

| Analysis | Plan | Script |
|---|---|---|
| RQ1 shares with 95% Clopper-Pearson intervals; Terminal-Bench weighted by 873/100 | `rq1-plan-frozen` | `scripts/02_rq1.py` |
| Blocking-task prevalence and the task audit | `rq3-addendum-frozen`, `nebius-plan-frozen` | `scripts/02_rq1.py` (Nebius audit), `scripts/04_rq3.py` |
| RQ2 patch metrics by failure kind (Table II) and ends-on-own | `rq2-rq3-addendum-frozen` | `scripts/03_rq2.py` |
| RQ3 resolve rates on blocking and other tasks, with task bootstrap | `rq2-rq3-addendum-frozen`, `nebius-plan-frozen` | `scripts/04_rq3.py` |

## Deviations from the frozen plans

These are changes made after the freezes.

1. **Sample size grew.** The labeled set grew from 971 to 1,091 failed runs. Terminal-Bench stays at 411 labeled runs (no new labels).
   The Nebius pilot of 120 issues (`nebius-plan-frozen`) became 360 labeled runs and 360 audited issues (N001 to N440 for runs, N001 to N360 for audits).
2. **Nebius frame.** The benchmark has 66,647 failed runs on 3,560 issues. The sample is one labeled run per issue for the labeled set. The paper's Table I should state this clearly.
   The pilot sample was dominated by one agent: 110 of the 120 pilot runs used `swe-agent-llama-70b`. In the final labeled set it is 344 of 360 runs (96%).
3. **Audit scope.** Nebius audits extended from the first 80 issues (N001 to N080) to all 360. Both raters audited all 360.
4. **Disagreements resolved after labels were saved.** The first 80 audits were discussed together with the 280 new ones.
   The consensus file is the primary audit. R1 and R3 remain as sensitivity rows. Of the 70 disagreements, 46 changed the R1 value, 17 changed the R3 value, and 7 changed both.
5. **SWE-bench audit replaced by a proxy.** The full SWE-bench audit (`directly matches` in the earlier draft) was replaced by OpenAI's `false_negative` ratings,
   with severe (2 or 3) as the blocking proxy. A 40-task calibration audit shows low agreement (kappa 0.15 for R1 and 0.38 for R3), so the SWE-bench RQ3 numbers
   describe OpenAI's broader criterion (tests may reject valid solutions), not our blocking label.
6. **Nebius RQ3 gain changed.** The median per-system gain on Nebius is +6.5 points (it was +14.8 in an earlier draft), because the larger audit includes more issues that some runs solve.
   The resolve-rate gap stays large: 0.6% on blocking issues against 17.1% on others.
7. **Table II "Other" column.** The working script for this column is marked approximate in its docstring. The rebuilt values in `scripts/03_rq2.py`
   match the paper's Table II. The no-fix line-count cell is computed here (29/27) but the paper shows a dash. The paper shows a dash, so keep the dash in the paper or state the computed value.
8. **Test-retest check (threat to validity, not a deviation).** Both raters relabeled 20 old SWE-bench runs without seeing their old labels.
   Same label: 70% (R1) and 65% (R3); kappa 0.14 and 0.24. The implicit label was the least stable. The paper reports this as a threat to validity.
   The test-retest sheets and hidden key are not in this package.
9. **Discussion timing (threat to validity).** Adjudication happened after all labels were saved, as noted in item 4.

## Open items for the authors

- The Nebius R3 run labels for N081 to N120 come from `cris_v2_alt`, which is not an independent R3 file. Confirm these labels or re-run the sensitivity analysis (`README.md`, section 5, item 7).
- The adjudication rule is summarized in `protocols/ANNOTATION_PROTOCOL.md`, section c. The verbatim rule sheet is not in the working files.
- Terminal-Bench audit: the 89-task audit file is the final audit used in the paper.
