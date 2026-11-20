# Annotation protocol

The study uses two lanes. The run lane labels what went wrong in each failed run. The task lane audits whether
the benchmark task itself states what the hidden tests check. The run lane is blind to the test code. The task lane is blind to run outcomes.

Labels are written as they appear in the data files. The category names in the paper map as follows:
Explicit = `ANCHORED`; Implicit = `NOT` with the note `implicit`; Other = `NOT` without that note, split into
No fix and Incorrect fix; Unclear = `UNCLEAR`.

## (a) Run lane: blind labeling

### Terminal-Bench (FaaP runs)

Each row shows the task requirement, FaaP's one-sentence failure summary, FaaP's explanation of the decisive mistake,
and FaaP's quote from the run. Labelers do not see FaaP's labels or timing data.

**The one question.** At the decisive mistake, did the agent stop working toward something the task text explicitly asked for?

Answer it in three checks, in order:

1. **Point to the requirement.** Find a sentence in the requirement text that the agent's work did not satisfy.
   If there is none, the label is `NOT`.
2. **Was the agent aiming at it?** At the decisive mistake, was the agent still working toward that sentence as written?
   - No (it ignored, forgot, misread, replaced, narrowed, or gave up on it): `ANCHORED`.
   - Yes, but it failed for another reason (environment, missing know-how, a bug in its code): `NOT`.
   - Unsure: use the tie-breaker. Imagine the agent's own plan had worked perfectly. If the requirement would then be
     unmet, the label is `ANCHORED`. If it would be met, the label is `NOT`.
3. **Not enough information** to answer check 1 or 2: `UNCLEAR`, with the reason in `note`.

Rules that apply throughout:

- Judge the **decisive mistake**, not what happened after it.
- Judge **what the agent did to the requirement**, not why it did it.
- **Only the task text counts.** A hint such as "X is installed" is not a requirement. If the missed expectation appears
  only in a README, a data file, or the hidden test, the label is `NOT` with the note `implicit`.
- Record the words from the task in `requirement_quote` and the words showing the agent's action in `evidence_quote`
  (both required for `ANCHORED`).

Worked example (`ANCHORED`): the task says "use the Qwen2.5-1.5B-Instruct tokenizer", and the agent used a different
Qwen tokenizer. Nothing errors, and the result is just wrong.

### Nebius and SWE-bench (agent patches)

These runs end with a patch, so the decision is made on the patch.

**The decision test.** If the agent's patch did exactly what the issue text asks, would it be correct?

- No: the agent missed something written in the issue. Label `ANCHORED` and quote the issue sentence.
- Yes, but the hidden test still fails because it expects something the issue never names: label `NOT` with the note `implicit`.

**Patch outcomes** (these set the "Other" split):

1. Final patch makes no change to project code (empty, or only a reproduction script, downloaded files, or build files): `NOT`, **No fix**.
2. Patch that does not apply: `NOT`, **Incorrect fix**.
3. Patch aimed at the written requirement but wrong or crashing: `NOT`, **Incorrect fix**.
4. Patch that changes something other than what the issue names: `ANCHORED`, quote the name in the issue.
5. Only the hidden test expects a specific internal target (a function, class, signature, or file location): `NOT` with the note `implicit`.

**Edge cases:**

- *Symptom-only issue* ("X crashes when Y is empty"). If the crash is not fixed: `ANCHORED`, quoting the symptom sentence.
  If the crash is fixed but the test calls an unstated internal function: `NOT` with `implicit`.
- *Names inside tracebacks or code snippets* count as written. If the patch ignores them: `ANCHORED`, quoting the line.
- *Issue suggests a fix that fails the test.* If the agent followed the issue's own suggested fix and the test still rejects it:
  `NOT` with `implicit` and the note `contradicts`. Report these separately.
- *Test checks behaviour the issue never mentions.* `NOT` with `implicit` and the note `unrelated`. Report these separately.
- *The repository already shows the expected name.* The run label still follows the issue text only. Record "repo shows it" in the task audit.

**Blinding.** Labelers work from the sheet that has the issue text, the final patch, the last three agent messages, and the exit status.
They do not see the tests, the OpenAI ratings, or the other rater's labels.

## (b) Task lane: blind audit

The audit asks two questions about each task. Labelers open the task packet (issue text, repository at the base commit, and test code).
They do not open run outputs or the other rater's audit.

1. **hidden_requirement** (`yes` / `no`): Does a hidden test check something that the issue text does not state and the repository does not show?
2. **blocking** (only if hidden_requirement is `yes`; `yes`, `no`, or `unclear`): Would a correct solution to the written issue still fail the tests?
   Answer `yes` only if you can name the test line and the mistake it causes.

Notes (optional, one word where possible): `unrelated`, `contradicts`, `repo shows it`.

For each audited item, record:

- `test_quote`: the test line, copied verbatim.
- `instruction_quote`: the closest words from the issue or task text (empty if the text says nothing).
- `reason`: one sentence.

Pace: about 6 to 10 minutes per issue. When unsure, mark `unclear` and move on. Do not chase certainty.

Limitation to report: the released audit files store the test line verbatim but do not store the test file path and line number in separate columns.
Add them to `test_quote` when you reproduce the audit.

## (c) Adjudication of disagreements

**What was done.** Two raters audited each of the 360 Nebius issues independently. They compared the audits and resolved 70 disagreements
through discussion. The 70 items are the ones where R1 and R3 disagreed on `hidden_requirement` or `blocking` before discussion.
The consensus was recorded as a third file. The discussion took place after all run labels had been saved. The first 80 audits were discussed
together with the later 280.

**Outcome.** Of the 70 disagreements, the consensus matched R1 but not R3 in 17 cases, matched R3 but not R1 in 46 cases,
and matched neither in 7. The per-item values are in `data/task_audits/nebius_disagreement_resolution.csv`.

**Adjudication rule.** R1 and R3 met to review all 70 audit disagreements. For each item, they inspected the exact failing hidden-test file and line number, alongside the task description and repository context. They then agreed on whether a valid solution that meets every stated requirement would still fail that assertion.

This is the authors' summary of the rule. The verbatim rule sheet is not in the working files.

## Agreement reporting

- Run labels: Cohen's kappa and percent agreement, before discussion. Nebius kappa 0.73 (3 categories) and SWE-bench 0.76.
- Task audits: kappa before discussion. Implicit requirement 0.83 and blocking 0.71 on Nebius.
- SWE-bench calibration: kappa of each rater's blocking label against OpenAI's severe ratings: 0.15 (R1) and 0.38 (R3).
- Terminal-Bench run labels: the second-rater kappa (0.63 and 0.74 in the paper) is not reproduced in this package (see the top-level README, section 5).
