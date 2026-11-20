"""RQ1: shares of failure sources with 95% Clopper-Pearson intervals.

Terminal-Bench: weighted estimate. The 311 shortlist runs are a census (weight 1). The 100 random
runs stand for the other 873 failed runs (weight 873/100). Interval: exact interval on the random
share, scaled to the 873 runs and added to the census count (same method as WP1 in the working folder).
Nebius and SWE-bench: plain shares of the labeled runs (R1 labels, primary).
Nebius task audit: consensus audit, implicit requirement and blocking groups.
Run:  python3 scripts/02_rq1.py
"""
from collections import Counter

from common import read, clopper_pearson, share_line, run_category, failure_kind, PKG, RESULTS, fmt
import os


def main(out_lines=None):
    lines = []
    say = lambda s="": lines.append(s)
    res = {}

    # ---------- Terminal-Bench (v5 labels, weighted)
    tb = read("run_labels/terminal_bench_run_labels.csv")
    census = [r for r in tb if r["stratum"] == "candidate"]
    rand = [r for r in tb if r["stratum"] == "random_other"]
    pop_other = 1184 - len(census)  # 873 unsampled failed runs
    assert len(census) == 311 and len(rand) == 100 and pop_other == 873

    def tb_cat(r):
        if r["label_v5"] == "ANCHORED":
            return "explicit"
        if r["label_v5"] == "NOT" and r["note_v5"].strip().lower() == "implicit":
            return "implicit"
        if r["label_v5"] == "NOT":
            return "other"
        return "unclear"

    say("## RQ1, Terminal-Bench (weighted; v5 labels)")
    say("| category | census count | random hits | estimate (runs) | share % | 95% CI % |")
    say("|---|---:|---:|---:|---:|---|")
    for cat, label in (("explicit", "Explicit (ANCHORED)"), ("implicit", "Implicit (NOT, note 'implicit')"),
                       ("other", "Other (NOT, not implicit)"), ("unclear", "Unclear")):
        c = sum(tb_cat(r) == cat for r in census)
        h = sum(tb_cat(r) == cat for r in rand)
        lo, hi = clopper_pearson(h, len(rand))
        est = c + pop_other * h / len(rand)
        share = 100 * est / 1184
        lo_s = 100 * (c + pop_other * lo) / 1184
        hi_s = 100 * (c + pop_other * hi) / 1184
        say(f"| {label} | {c} | {h} | {est:.1f} | {fmt(share)} | [{fmt(lo_s)}, {fmt(hi_s)}] |")
        res[f"tb_{cat}"] = share
        res[f"tb_{cat}_ci"] = (lo_s, hi_s)
    say()

    # ---------- Nebius and SWE-bench (R1 labels)
    for name, rel in (("Nebius", "run_labels/nebius_run_labels.csv"), ("SWE-bench", "run_labels/swebench_run_labels.csv")):
        rows = read(rel)
        cats = [run_category(r["R1_label"], r["R1_note"]) for r in rows]
        kinds = [failure_kind(r["R1_label"], r["R1_note"]) for r in rows]
        n = len(rows)
        say(f"## RQ1, {name} (R1 labels, n = {n})")
        say("| category | count | share % | 95% CI % |")
        say("|---|---:|---:|---|")
        for cat, label in (("explicit", "Explicit"), ("implicit", "Implicit"), ("other", "Other")):
            k = cats.count(cat)
            p, lo, hi = share_line(k, n)
            say(f"| {label} | {k} | {fmt(p)} | [{fmt(lo)}, {fmt(hi)}] |")
            res[f"{name}_{cat}"] = p
            res[f"{name}_{cat}_ci"] = (lo, hi)
        for kd, label in (("incorrect_fix", "- incorrect fix"), ("no_fix", "- no fix")):
            k = kinds.count(kd)
            p, lo, hi = share_line(k, n)
            say(f"| {label} | {k} | {fmt(p)} | [{fmt(lo)}, {fmt(hi)}] |")
            res[f"{name}_{kd}"] = p
        say()

    # ---------- Nebius task audit (consensus)
    audit = read("task_audits/nebius_task_audit_consensus_N001-N360.csv")
    n = len(audit)
    implicit = sum(r["hidden_requirement"].strip().lower() == "yes" for r in audit)
    blocking = sum(r["hidden_requirement"].strip().lower() == "yes" and r["blocking"].strip().lower() == "yes" for r in audit)
    p, lo, hi = share_line(implicit, n)
    say(f"## Nebius task audit (consensus, n = {n})")
    say(f"- Implicit requirement: {implicit} ({fmt(p)}%, CI [{fmt(lo)}, {fmt(hi)}])")
    p, lo, hi = share_line(blocking, n)
    say(f"- Blocking (implicit and blocking = yes): {blocking} ({fmt(p)}%, CI [{fmt(lo)}, {fmt(hi)}])")
    res["nb_audit_implicit"] = 100 * implicit / n
    res["nb_audit_blocking"] = 100 * blocking / n
    res["nb_audit_blocking_n"] = blocking
    res["nb_audit_implicit_n"] = implicit
    notes = [r["note"].lower() for r in audit if r["hidden_requirement"].strip().lower() == "yes"]
    say(f"- Notes among implicit items: contradicts {sum('contradicts' in x for x in notes)}, "
        f"unrelated {sum('unrelated' in x for x in notes)}")
    say()

    # ---------- Terminal-Bench FaaP shares (weighted ANCHORED total, census plus random draw)
    tb = read("run_labels/terminal_bench_run_labels.csv")
    anch = [r for r in tb if r["label_v5"].strip() == "ANCHORED"]
    est_total = sum(float(r["weight"]) for r in anch)
    shortlist = sum(float(r["weight"]) for r in anch if r["stratum"] == "candidate")
    spec = sum(float(r["weight"]) for r in anch if r["faap_trigger"] == "spec_neglect")
    res["faap_anchored_total"] = est_total
    res["faap_shortlist"] = 100 * shortlist / est_total
    res["faap_spec"] = 100 * spec / est_total
    say("## Terminal-Bench FaaP shares (ANCHORED, weighted)")
    say(f"- Estimated ANCHORED total: {est_total:.1f} runs")
    say(f"- In the shortlist (stratum candidate): {fmt(res['faap_shortlist'])}%")
    say(f"- FaaP trigger spec_neglect: {fmt(res['faap_spec'])}%")
    say("- Confidence intervals for these shares are not reproduced here.")
    say()

    # ---------- Terminal-Bench gap types (the 22 hidden-requirement tasks, by primary kind)
    gap = read("task_audits/terminal_bench_gap_types.csv")
    audit_tb = {r["task"]: r for r in read("task_audits/terminal_bench_task_audit.csv")}
    kinds = {}
    for r in gap:
        k = kinds.setdefault(r["kind_primary"], {"n": 0, "yes": 0})
        k["n"] += 1
        k["yes"] += audit_tb[r["task"]]["blocking"].strip().lower() == "yes"
    say(f"## Terminal-Bench gap types (hidden-requirement tasks, n = {len(gap)})")
    say("| primary kind | tasks | blocking = yes |")
    say("|---|---:|---:|")
    for kind in sorted(kinds):
        say(f"| {kind} | {kinds[kind]['n']} | {kinds[kind]['yes']} |")
    say()
    res["tb_gap_n"] = len(gap)
    res["tb_gap_kinds"] = sorted(v["n"] for v in kinds.values())
    res["tb_gap_blocking_yes"] = sum(v["yes"] for v in kinds.values())

    text = "\n".join(lines)
    if out_lines is None:
        os.makedirs(RESULTS, exist_ok=True)
        with open(os.path.join(RESULTS, "rq1.md"), "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(text)
    return res


if __name__ == "__main__":
    main()
