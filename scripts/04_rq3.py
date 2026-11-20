"""RQ3: resolve rates on blocking tasks versus other tasks, and per-system gains.

Nebius (primary: consensus audit; sensitivity: R1 and R3 audits before discussion).
  Unit: one audited issue. Rate per issue = share of its runs that resolve. Group rate = mean of issue rates.
  Gap = blocking minus none. 95% CI from 10,000 bootstrap redraws of issues (seed 20260925).
  Per system: failures on blocking tasks (share of each system's failures) and the gain in success
  rate without blocking tasks (pooled over runs).
SWE-bench (OpenAI 'false_negative' ensemble = maximum, severe = 2 or 3 as a proxy for blocking;
  24 submissions; mean of per-task rates; task bootstrap, 10,000 redraws, seed 20260925).
Terminal-Bench (description only, from the audit file; no bootstrap, as in the paper).
Run:  python3 scripts/04_rq3.py
"""
import os
import random
import statistics
from collections import defaultdict

from common import read, SEED, RESULTS

N_REDRAW = 10000


def group_of(row):
    h = row["hidden_requirement"].strip().lower()
    b = row["blocking"].strip().lower()
    if h == "no":
        return "none"
    return "blocking" if h == "yes" and b == "yes" else "other_hidden"


def nebius_units(audit_rel):
    audit = read(audit_rel)  # row order matters for the bootstrap draws; keep the file order
    return {r["item_id"]: group_of(r) for r in audit}


def nebius_runs():
    runs = defaultdict(list)
    for r in read("telemetry_and_scores/nebius_run_outcomes.csv"):
        runs[r["audit_item_id"]].append((r["model_name"], int(r["resolved"])))
    return runs


def rate(vals):
    return 100 * sum(vals) / len(vals)


def nebius_compare(groups, runs):
    """Blocking minus none, plus per-system numbers. Bootstrap order follows the audit file order."""
    rate_i = {i: rate([t for _, t in runs[i]]) for i in groups}
    gb = [i for i in groups if groups[i] == "blocking"]
    gn = [i for i in groups if groups[i] == "none"]
    mb = statistics.mean(rate_i[i] for i in gb)
    mn = statistics.mean(rate_i[i] for i in gn)
    rng = random.Random(SEED)
    d = []
    for _ in range(N_REDRAW):
        sb = [rate_i[rng.choice(gb)] for _ in gb]
        sn = [rate_i[rng.choice(gn)] for _ in gn]
        d.append(statistics.mean(sb) - statistics.mean(sn))
    d.sort()
    per = []
    for m in sorted({mm for i in groups for mm, _ in runs[i]}):
        v = [(groups[i], t) for i in groups for mm, t in runs[i] if mm == m]
        fails = [g for g, t in v if t == 0]
        nob = [t for g, t in v if g != "blocking"]
        share = 100 * sum(g == "blocking" for g in fails) / len(fails)
        gain = 100 * sum(nob) / len(nob) - 100 * sum(t for _, t in v) / len(v)
        per.append((share, gain))
    return {
        "n_blocking": len(gb), "n_total": len(groups), "n_none": len(gn),
        "res_blocking": mb, "res_none": mn, "diff": mb - mn, "ci": (d[249], d[9749]),
        "sys_share_median": statistics.median(s for s, _ in per),
        "sys_share_range": (min(s for s, _ in per), max(s for s, _ in per)),
        "sys_gain_median": statistics.median(g for _, g in per),
        "sys_gain_range": (min(g for _, g in per), max(g for _, g in per)),
        "systems": len(per),
    }


def swe_compare():
    sev = {}
    for r in read("telemetry_and_scores/swebench_openai_severity.csv"):
        sev[r["instance_id"]] = float(r["ensemble_false_negative"])
    grp = {i: ("severe" if v >= 2 else ("none" if v == 0 else "mild")) for i, v in sev.items()}
    subs = defaultdict(dict)
    for r in read("telemetry_and_scores/swebench_resolved_by_submission.csv"):
        subs[r["submission"]][r["instance_id"]] = int(r["resolved"])
    names = sorted(subs)
    assert len(names) == 24
    ids = sorted(grp)
    rate_i = {i: rate([subs[s][i] for s in names]) for i in ids}  # mean of per-task rates below
    gs = [i for i in ids if grp[i] == "severe"]
    gn = [i for i in ids if grp[i] == "none"]
    mb = statistics.mean(rate_i[i] for i in gs)
    mn = statistics.mean(rate_i[i] for i in gn)
    rng = random.Random(SEED)
    d = []
    for _ in range(N_REDRAW):
        sb = [rate_i[rng.choice(gs)] for _ in gs]
        sn = [rate_i[rng.choice(gn)] for _ in gn]
        d.append(statistics.mean(sb) - statistics.mean(sn))
    d.sort()
    per = []
    for s in names:
        fails = [i for i in ids if subs[s][i] == 0]
        share = 100 * sum(grp[i] == "severe" for i in fails) / len(fails)
        nob = [subs[s][i] for i in ids if grp[i] != "severe"]
        gain = 100 * sum(nob) / len(nob) - 100 * sum(subs[s][i] for i in ids) / len(ids)
        per.append((share, gain))
    return {
        "n_severe": len(gs), "n_total": len(ids), "n_none": len(gn),
        "res_severe": mb, "res_none": mn, "diff": mb - mn, "ci": (d[249], d[9749]),
        "sys_share_median": statistics.median(s for s, _ in per),
        "sys_share_range": (min(s for s, _ in per), max(s for s, _ in per)),
        "sys_gain_median": statistics.median(g for _, g in per),
        "sys_gain_range": (min(g for _, g in per), max(g for _, g in per)),
        "systems": len(per),
    }


def main(out_lines=None):
    lines = []
    say = lambda s="": lines.append(s)
    res = {}
    runs = nebius_runs()

    say("## RQ3, Nebius (per-issue resolve rate, mean over issues, 95% bootstrap CI)")
    for label, rel in (("Consensus audit (primary)", "task_audits/nebius_task_audit_consensus_N001-N360.csv"),
                       ("R1 audit before discussion", "task_audits/nebius_task_audit_R1_N001-N360.csv"),
                       ("R3 audit before discussion", "task_audits/nebius_task_audit_R3_N001-N360.csv")):
        g = nebius_units(rel)
        r = nebius_compare(g, runs)
        say(f"- {label}: blocking {r['n_blocking']}/{r['n_total']} ({100*r['n_blocking']/r['n_total']:.1f}%); "
            f"resolve blocking {r['res_blocking']:.1f} vs none {r['res_none']:.1f} (n = {r['n_none']}); "
            f"diff {r['diff']:+.1f} [{r['ci'][0]:+.1f}, {r['ci'][1]:+.1f}]")
        say(f"    per system ({r['systems']}): failures on blocking median {r['sys_share_median']:.1f} "
            f"(range {r['sys_share_range'][0]:.1f}-{r['sys_share_range'][1]:.1f}); gain median {r['sys_gain_median']:+.1f} "
            f"(range {r['sys_gain_range'][0]:+.1f}, {r['sys_gain_range'][1]:+.1f})")
        if label.startswith("Consensus"):
            res["nb_res_block"] = r["res_blocking"]
            res["nb_res_none"] = r["res_none"]
            res["nb_diff"] = r["diff"]
            res["nb_ci"] = r["ci"]
            res["nb_n_block"] = r["n_blocking"]
            res["nb_sys_share_median"] = r["sys_share_median"]
            res["nb_sys_share_range"] = r["sys_share_range"]
            res["nb_sys_gain_median"] = r["sys_gain_median"]
            res["nb_sys_gain_range"] = r["sys_gain_range"]
    say()

    say("## RQ3, SWE-bench (OpenAI severity as blocking proxy, 24 submissions)")
    r = swe_compare()
    say(f"- Severe tasks {r['n_severe']}/{r['n_total']}; resolve severe {r['res_severe']:.1f} vs none {r['res_none']:.1f} "
        f"(n = {r['n_none']}); diff {r['diff']:+.1f} [{r['ci'][0]:+.1f}, {r['ci'][1]:+.1f}]")
    say(f"    per system ({r['systems']}): failures on severe median {r['sys_share_median']:.1f} "
        f"(range {r['sys_share_range'][0]:.1f}-{r['sys_share_range'][1]:.1f}); gain median {r['sys_gain_median']:+.1f} "
        f"(range {r['sys_gain_range'][0]:+.1f}, {r['sys_gain_range'][1]:+.1f})")
    res.update(swe_res_severe=r["res_severe"], swe_res_none=r["res_none"], swe_diff=r["diff"], swe_ci=r["ci"],
               swe_n_severe=r["n_severe"], swe_sys_share_median=r["sys_share_median"],
               swe_sys_share_range=r["sys_share_range"], swe_sys_gain_median=r["sys_gain_median"],
               swe_sys_gain_range=r["sys_gain_range"])
    say()

    say("## RQ3, Terminal-Bench (description only; no bootstrap, as in the paper)")
    audit = {r["task"]: group_of(r) for r in read("task_audits/terminal_bench_task_audit.csv")}
    outcomes = read("telemetry_and_scores/terminal_bench_run_outcomes.csv")
    per_task = defaultdict(list)  # task -> pass indicators (1 = pass) over all runs of that task
    per_system = defaultdict(list)  # system -> (task group or None, pass indicator)
    for r in outcomes:
        passed = 1 - int(r["failed"])
        per_task[r["task"]].append(passed)
        per_system[r["system"]].append((audit.get(r["task"]), passed))
    blocking_tasks = [t for t, g in audit.items() if g == "blocking"]
    say(f"- Blocking tasks in the audit: {len(blocking_tasks)} of {len(audit)}")
    block_runs = sum(len(per_task[t]) for t in blocking_tasks)
    say(f"- Runs on blocking tasks: {block_runs}")
    group_rates = {}
    for g in ("blocking", "none"):
        rates = [rate(per_task[t]) for t, gg in audit.items() if gg == g and per_task[t]]
        group_rates[g] = statistics.mean(rates)
    diff = group_rates["blocking"] - group_rates["none"]
    say(f"- Resolve (pass) rate, mean of task rates: blocking {group_rates['blocking']:.1f} vs none {group_rates['none']:.1f}; "
        f"diff {diff:+.1f}")
    shares, gains = [], []
    for sysname, v in per_system.items():
        fails = [g for g, y in v if y == 0]
        nob = [y for g, y in v if g != "blocking"]
        allr = [y for _, y in v]
        if not fails or not nob:
            continue
        shares.append(100 * sum(g == "blocking" for g in fails) / len(fails))
        gains.append(100 * sum(nob) / len(nob) - 100 * sum(allr) / len(allr))
    say(f"- Per system ({len(shares)}): failures on blocking median {statistics.median(shares):.1f} "
        f"(range {min(shares):.1f}-{max(shares):.1f}); gain median {statistics.median(gains):+.1f} "
        f"(range {min(gains):+.1f}, {max(gains):+.1f})")
    res.update(tb_blocking_tasks=len(blocking_tasks), tb_blocking_runs=block_runs,
               tb_res_block=group_rates["blocking"], tb_res_none=group_rates["none"], tb_diff=diff,
               tb_sys_share_median=statistics.median(shares), tb_sys_gain_median=statistics.median(gains),
               tb_sys_gain_range=(min(gains), max(gains)), tb_sys_share_range=(min(shares), max(shares)),
               tb_systems=len(shares))
    say()

    text = "\n".join(lines)
    if out_lines is None:
        os.makedirs(RESULTS, exist_ok=True)
        with open(os.path.join(RESULTS, "rq3.md"), "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(text)
    return res


if __name__ == "__main__":
    main()
