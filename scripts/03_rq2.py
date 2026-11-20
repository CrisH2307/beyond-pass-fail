"""RQ2: behaviour of the agent runs by failure kind (Table II) and 'ends on its own' rates.

Table II, SWE-bench (n = 320): per-run patch metrics (derived in data/telemetry_and_scores/) grouped by R1 failure kind.
  Ref. file: run edits a non-test file that the reference fix also edits.
  Other: run edits a non-test file the reference fix does not touch (root-level new files excluded).
  Scratch: run adds a new file at the repo root that the reference fix does not add.
  Lines: median changed lines, agent / reference, over runs with a reference-file edit.
'Ends on its own': exit status 'submitted' (SWE-bench and Nebius blind runs).
Not in this package: Terminal-Bench awareness (89.3% vs 70.1%) and test-execution counts (see README).
Run:  python3 scripts/03_rq2.py
"""
import os
import statistics
from collections import defaultdict

from common import read, RESULTS, failure_kind

KINDS = (("no_fix", "No fix"), ("explicit", "Explicit"), ("incorrect_fix", "Incorrect fix"), ("implicit", "Implicit"))


def main(out_lines=None):
    lines = []
    say = lambda s="": lines.append(s)
    res = {}

    sw_labels = {r["item_id"]: failure_kind(r["R1_label"], r["R1_note"]) for r in read("run_labels/swebench_run_labels.csv")}
    metrics = {r["item_id"]: r for r in read("telemetry_and_scores/swebench_run_patch_metrics.csv")}
    say("## Table II, SWE-bench patch metrics (n = 320, R1 kinds)")
    say("| Failure (n) | Ref. file | Other | Scratch | Lines agent/ref | Ends on own |")
    say("|---|---:|---:|---:|---:|---:|")
    for kind, label in KINDS:
        ids = [i for i, k in sw_labels.items() if k == kind]
        rows = [metrics[i] for i in ids]
        n = len(rows)
        ref = sum(int(r["ref_file_edit"]) for r in rows)
        oth = sum(int(r["other_file_edit"]) for r in rows)
        scr = sum(int(r["scratch_file_added"]) for r in rows)
        ends = sum(r["exit_status"] == "submitted" for r in rows)
        with_ref = [r for r in rows if r["ref_file_edit"] == "1"]
        lines_txt = (f"{statistics.median(int(r['agent_changed_lines']) for r in with_ref):g}/"
                     f"{statistics.median(int(r['ref_changed_lines']) for r in with_ref):g}") if with_ref else "-"
        say(f"| {label} ({n}) | {100*ref/n:.0f}% | {100*oth/n:.0f}% | {100*scr/n:.0f}% | {lines_txt} | {100*ends/n:.0f}% |")
        res[f"t2_{kind}_ref"] = 100 * ref / n
        res[f"t2_{kind}_other"] = 100 * oth / n
        res[f"t2_{kind}_scratch"] = 100 * scr / n
        res[f"t2_{kind}_swe_ends"] = 100 * ends / n
    say("Note: the paper shows '-' for the No fix line-count cell; this script computes it (see protocols/ANALYSIS_PLANS.md, deviation 7).")
    say()

    # ---------- Ends on its own, Nebius blind runs (R1 kinds)
    nb = read("run_labels/nebius_run_labels.csv")
    say("## Ends on its own, by R1 kind")
    say("| Source | No fix | Explicit | Incorrect fix | Implicit |")
    say("|---|---:|---:|---:|---:|")
    nb_cells = []
    for name, rows, kindfn in (("SWE-bench", list(metrics.values()), None), ("Nebius blind", nb, "nb")):
        cells = []
        for kind, _ in KINDS:
            if kindfn is None:
                ids = [i for i, k in sw_labels.items() if k == kind]
                n = len(ids)
                e = sum(metrics[i]["exit_status"] == "submitted" for i in ids)
            else:
                rs = [r for r in nb if failure_kind(r["R1_label"], r["R1_note"]) == kind]
                n = len(rs)
                e = sum(r["exit_status"] == "submitted" for r in rs)
            cells.append(f"{100*e/n:.0f}% (n={n})")
            res[f"ends_{name}_{kind}"] = 100 * e / n
        say(f"| {name} | " + " | ".join(cells) + " |")
    say()

    text = "\n".join(lines)
    if out_lines is None:
        os.makedirs(RESULTS, exist_ok=True)
        with open(os.path.join(RESULTS, "rq2.md"), "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(text)
    return res


if __name__ == "__main__":
    main()
