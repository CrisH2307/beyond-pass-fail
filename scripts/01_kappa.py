"""Inter-rater agreement (before discussion).

R1 = first author, R3 = industry software engineer rater. Nebius and SWE-bench run labels and the Nebius task audit.
Kappa against OpenAI's severity ratings uses the 40-task SWE-bench calibration set (severe = 2 or 3).
Terminal-Bench run-label kappa (0.63 and 0.74 in the paper) is NOT computed here: the second Terminal-Bench
rating files are not in data/ (see data/README.md).
Run:  python3 scripts/01_kappa.py
"""
import os

from common import read, kappa, run_category, failure_kind, RESULTS


def main(out_lines=None):
    lines = []
    say = lambda s="": lines.append(s)
    res = {}
    say("## Agreement, run labels (R1 vs R3, before discussion)")
    for name, rel in (("Nebius", "run_labels/nebius_run_labels.csv"), ("SWE-bench", "run_labels/swebench_run_labels.csv")):
        rows = read(rel)
        a3 = {r["item_id"]: run_category(r["R1_label"], r["R1_note"]) for r in rows}
        b3 = {r["item_id"]: run_category(r["R3_label"], r["R3_note"]) for r in rows}
        k3, p3, n = kappa(a3, b3)
        a4 = {r["item_id"]: failure_kind(r["R1_label"], r["R1_note"]) for r in rows}
        b4 = {r["item_id"]: failure_kind(r["R3_label"], r["R3_note"]) for r in rows}
        k4, p4, _ = kappa(a4, b4)
        say(f"- {name} (n = {n}): 3 categories kappa {k3:.2f}, agreement {p3:.1f}%; 4 kinds kappa {k4:.2f}, agreement {p4:.1f}%")
        res[f"kappa_{name}_3"] = k3
        res[f"kappa_{name}_4"] = k4
    say("- Terminal-Bench run labels: not computed (see docstring).")
    say()

    say("## Agreement, Nebius task audit (R1 vs R3, before discussion)")
    r1 = {r["item_id"]: r for r in read("task_audits/nebius_task_audit_R1_N001-N360.csv")}
    r3 = {r["item_id"]: r for r in read("task_audits/nebius_task_audit_R3_N001-N360.csv")}
    imp1 = {i: r["hidden_requirement"].strip().lower() for i, r in r1.items()}
    imp3 = {i: r["hidden_requirement"].strip().lower() for i, r in r3.items()}
    k, p, n = kappa(imp1, imp3)
    say(f"- Implicit requirement (n = {n}): kappa {k:.2f}, agreement {p:.1f}%")
    res["kappa_audit_implicit"] = k
    blk1 = {i: (r["hidden_requirement"].strip().lower() == "yes" and r["blocking"].strip().lower() == "yes") for i, r in r1.items()}
    blk3 = {i: (r["hidden_requirement"].strip().lower() == "yes" and r["blocking"].strip().lower() == "yes") for i, r in r3.items()}
    k, p, n = kappa(blk1, blk3)
    say(f"- Blocking, yes vs not (n = {n}): kappa {k:.2f}, agreement {p:.1f}%")
    res["kappa_audit_blocking"] = k
    say()

    say("## SWE-bench calibration (40 tasks)")
    c1 = {r["item_id"]: r for r in read("task_audits/swebench_calibration_audit_R1.csv")}
    c3 = {r["item_id"]: r for r in read("task_audits/swebench_calibration_audit_R3.csv")}
    blk1 = {i: (r["hidden_requirement"].strip().lower() == "yes" and r["blocking"].strip().lower() == "yes") for i, r in c1.items()}
    blk3 = {i: (r["hidden_requirement"].strip().lower() == "yes" and r["blocking"].strip().lower() == "yes") for i, r in c3.items()}
    k, p, _ = kappa(blk1, blk3)
    say(f"- R1 vs R3 blocking: kappa {k:.2f}, agreement {p:.1f}%")
    oa = {r["item_id"]: float(r["false_negative"]) >= 2 for r in read("task_audits/swebench_calibration_openai_ratings.csv")}
    say(f"- OpenAI severe: {sum(oa.values())}/{len(oa)}")
    for name, blk in (("R1", blk1), ("R3", blk3)):
        k, p, _ = kappa(blk, oa)
        res[f"kappa_openai_{name}"] = k
        say(f"- {name} blocking vs OpenAI severe: kappa {k:.2f}, agreement {p:.1f}%")
    say()

    text = "\n".join(lines)
    if out_lines is None:
        os.makedirs(RESULTS, exist_ok=True)
        with open(os.path.join(RESULTS, "kappa.md"), "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(text)
    return res


if __name__ == "__main__":
    main()
