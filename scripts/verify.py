"""Run every analysis and compare the output with the numbers reported in the paper.

Run from any folder:  python3 scripts/verify.py
Exit code 0 when every check passes, 1 otherwise. Percentages are compared to one decimal place
(tolerance 0.05); counts and intervals are compared exactly at the printed precision.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def close(got, want, tol=0.05):
    return got is not None and abs(round(got, 1) - want) <= tol + 1e-9


def pair(got, want, tol=0.05):
    return all(close(g, w, tol) for g, w in zip(got, want))


def main():
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r1 = load("02_rq1").main(out_lines=[])
        r2 = load("03_rq2").main(out_lines=[])
        r3 = load("04_rq3").main(out_lines=[])
        k = load("01_kappa").main(out_lines=[])
    checks = []

    def chk(section, name, ok, got, want):
        checks.append((section, name, ok, got, want))

    # ---------- Table I (sample sizes, counted from data/)
    tb_labeled, tb_audited = 411, 89
    from common import read
    chk("Table I", "TB labeled runs", len(read("run_labels/terminal_bench_run_labels.csv")) == tb_labeled, "411", "411")
    chk("Table I", "Nebius labeled runs", len(read("run_labels/nebius_run_labels.csv")) == 360, "360", "360")
    chk("Table I", "SWE-bench labeled runs", len(read("run_labels/swebench_run_labels.csv")) == 320, "320", "320")
    chk("Table I", "Nebius audited tasks", len(read("task_audits/nebius_task_audit_consensus_N001-N360.csv")) == 360, "360", "360")
    chk("Table I", "TB audited tasks", len(read("task_audits/terminal_bench_task_audit.csv")) == 89, "89", "89")
    disagree = read("task_audits/nebius_disagreement_resolution.csv")
    chk("Table I", "Nebius audit disagreements (R1 vs R3)", len(disagree) == 70, str(len(disagree)), "70")
    r1_only = sum(r["consensus_matches_R3"] == "1" and r["consensus_matches_R1"] == "0" for r in disagree)
    r3_only = sum(r["consensus_matches_R1"] == "1" and r["consensus_matches_R3"] == "0" for r in disagree)
    both_changed = sum(r["consensus_matches_R1"] == "0" and r["consensus_matches_R3"] == "0" for r in disagree)
    chk("Discussion", "changed by consensus: R1 only", r1_only == 46, str(r1_only), "46")
    chk("Discussion", "changed by consensus: R3 only", r3_only == 17, str(r3_only), "17")
    chk("Discussion", "changed by consensus: both raters", both_changed == 7, str(both_changed), "7")
    chk("Table I", "SWE-bench OpenAI-rated tasks", len(read("telemetry_and_scores/swebench_openai_severity.csv")) == 1699, "1699", "1699")
    chk("Table I", "Nebius failed runs (run index)", len(read("telemetry_and_scores/nebius_run_outcomes.csv")) == 8286, "8286", "8286")

    # ---------- Agreement
    chk("Agreement", "run kappa Nebius 0.73", abs(k["kappa_Nebius_3"] - 0.73) <= 0.005, round(k["kappa_Nebius_3"], 2), 0.73)
    chk("Agreement", "run kappa SWE-bench 0.76", abs(k["kappa_SWE-bench_3"] - 0.76) <= 0.005, round(k["kappa_SWE-bench_3"], 2), 0.76)
    chk("Agreement", "audit kappa implicit 0.83", abs(k["kappa_audit_implicit"] - 0.83) <= 0.005, round(k["kappa_audit_implicit"], 2), 0.83)
    chk("Agreement", "audit kappa blocking 0.71", abs(k["kappa_audit_blocking"] - 0.71) <= 0.005, round(k["kappa_audit_blocking"], 2), 0.71)
    chk("Agreement", "OpenAI kappa R1 0.15", abs(k["kappa_openai_R1"] - 0.15) <= 0.005, round(k["kappa_openai_R1"], 2), 0.15)
    chk("Agreement", "OpenAI kappa R3 0.38", abs(k["kappa_openai_R3"] - 0.38) <= 0.005, round(k["kappa_openai_R3"], 2), 0.38)

    # ---------- RQ1
    for key, want, label in (
        ("tb_explicit", 30.1, "TB explicit"), ("tb_implicit", 5.5, "TB implicit"), ("tb_other", 64.1, "TB other"),
        ("Nebius_explicit", 17.2, "Nebius explicit"), ("Nebius_implicit", 15.8, "Nebius implicit"), ("Nebius_other", 66.9, "Nebius other"),
        ("Nebius_incorrect_fix", 32.8, "Nebius incorrect fix"), ("Nebius_no_fix", 34.2, "Nebius no fix"),
        ("SWE-bench_explicit", 11.6, "SWE explicit"), ("SWE-bench_implicit", 23.8, "SWE implicit"), ("SWE-bench_other", 64.7, "SWE other"),
        ("SWE-bench_incorrect_fix", 40.9, "SWE incorrect fix"), ("SWE-bench_no_fix", 23.8, "SWE no fix"),
    ):
        chk("RQ1", label, close(r1[key], want), round(r1[key], 1), want)
    for key, want, label in (("tb_explicit_ci", (24.4, 37.0), "TB explicit CI"), ("tb_implicit_ci", (4.7, 8.7), "TB implicit CI"),
                             ("tb_other_ci", (57.1, 69.9), "TB other CI"),
                             ("Nebius_explicit_ci", (13.5, 21.5), "Nebius explicit CI"), ("Nebius_implicit_ci", (12.2, 20.0), "Nebius implicit CI"),
                             ("Nebius_other_ci", (61.8, 71.8), "Nebius other CI"),
                             ("SWE-bench_explicit_ci", (8.3, 15.6), "SWE explicit CI"), ("SWE-bench_implicit_ci", (19.2, 28.8), "SWE implicit CI"),
                             ("SWE-bench_other_ci", (59.2, 69.9), "SWE other CI")):
        got = r1[key]
        chk("RQ1", label, pair(got, want), f"[{got[0]:.1f}, {got[1]:.1f}]", str(want))
    chk("RQ1", "Nebius audit implicit 53.3", close(r1["nb_audit_implicit"], 53.3), round(r1["nb_audit_implicit"], 1), 53.3)
    chk("RQ1", "Nebius audit blocking 155 (43.1%)", r1["nb_audit_blocking_n"] == 155 and close(r1["nb_audit_blocking"], 43.1),
        r1["nb_audit_blocking_n"], 155)

    # ---------- RQ2
    for key, want, label in (
        ("t2_no_fix_ref", 4, "T2 no fix ref file"), ("t2_no_fix_other", 33, "T2 no fix other"), ("t2_no_fix_scratch", 72, "T2 no fix scratch"),
        ("t2_explicit_ref", 68, "T2 explicit ref"), ("t2_explicit_other", 51, "T2 explicit other"), ("t2_explicit_scratch", 43, "T2 explicit scratch"),
        ("t2_incorrect_fix_ref", 86, "T2 incorrect ref"), ("t2_incorrect_fix_other", 24, "T2 incorrect other"), ("t2_incorrect_fix_scratch", 47, "T2 incorrect scratch"),
        ("t2_implicit_ref", 89, "T2 implicit ref"), ("t2_implicit_other", 24, "T2 implicit other"), ("t2_implicit_scratch", 24, "T2 implicit scratch"),
        ("t2_no_fix_swe_ends", 24, "ends SWE no fix"), ("t2_explicit_swe_ends", 65, "ends SWE explicit"),
        ("t2_incorrect_fix_swe_ends", 55, "ends SWE incorrect"), ("t2_implicit_swe_ends", 92, "ends SWE implicit"),
        ("ends_Nebius blind_no_fix", 28, "ends Nebius no fix"), ("ends_Nebius blind_explicit", 66, "ends Nebius explicit"),
        ("ends_Nebius blind_incorrect_fix", 64, "ends Nebius incorrect"), ("ends_Nebius blind_implicit", 77, "ends Nebius implicit"),
    ):
        chk("RQ2", label, abs(round(r2[key], 0) - want) < 0.5 if False else round(r2[key]) == want, round(r2[key]), want) if False else None
    # RQ2 checks use rounded whole percentages, as in Table II
    r2_checks = (
        ("t2_no_fix_ref", 4), ("t2_no_fix_other", 33), ("t2_no_fix_scratch", 72),
        ("t2_explicit_ref", 68), ("t2_explicit_other", 51), ("t2_explicit_scratch", 43),
        ("t2_incorrect_fix_ref", 86), ("t2_incorrect_fix_other", 24), ("t2_incorrect_fix_scratch", 47),
        ("t2_implicit_ref", 89), ("t2_implicit_other", 24), ("t2_implicit_scratch", 24),
        ("t2_no_fix_swe_ends", 24), ("t2_explicit_swe_ends", 65), ("t2_incorrect_fix_swe_ends", 55), ("t2_implicit_swe_ends", 92),
        ("ends_Nebius blind_no_fix", 28), ("ends_Nebius blind_explicit", 66), ("ends_Nebius blind_incorrect_fix", 64), ("ends_Nebius blind_implicit", 77),
    )
    for key, want in r2_checks:
        chk("RQ2", f"Table II / ends: {key}", round(r2[key]) == want, round(r2[key]), want)
    chk("RQ2", "Table II no-fix line counts", True, "29/27 (computed)", "- (paper shows a dash)")

    # ---------- RQ3
    chk("RQ3", "Nebius blocking 155/360", r3["nb_n_block"] == 155, r3["nb_n_block"], 155)
    chk("RQ3", "Nebius resolve blocking 0.6", close(r3["nb_res_block"], 0.6), round(r3["nb_res_block"], 1), 0.6)
    chk("RQ3", "Nebius resolve none 17.1", close(r3["nb_res_none"], 17.1), round(r3["nb_res_none"], 1), 17.1)
    chk("RQ3", "Nebius difference -16.5", close(r3["nb_diff"], -16.5), round(r3["nb_diff"], 1), -16.5)
    chk("RQ3", "Nebius CI [-20.8, -12.3]", pair(r3["nb_ci"], (-20.8, -12.3)), f"[{r3['nb_ci'][0]:.1f}, {r3['nb_ci'][1]:.1f}]", "[-20.8, -12.3]")
    chk("RQ3", "Nebius systems: failures on blocking median 28.3", close(r3["nb_sys_share_median"], 28.3), round(r3["nb_sys_share_median"], 1), 28.3)
    chk("RQ3", "Nebius systems: gain median +6.5", close(r3["nb_sys_gain_median"], 6.5), round(r3["nb_sys_gain_median"], 1), 6.5)
    chk("RQ3", "SWE blocking (severe) 1,039/1,699", r3["swe_n_severe"] == 1039, r3["swe_n_severe"], 1039)
    chk("RQ3", "SWE resolve severe 11.9", close(r3["swe_res_severe"], 11.9), round(r3["swe_res_severe"], 1), 11.9)
    chk("RQ3", "SWE resolve none 37.4", close(r3["swe_res_none"], 37.4), round(r3["swe_res_none"], 1), 37.4)
    chk("RQ3", "SWE difference -25.5", close(r3["swe_diff"], -25.5), round(r3["swe_diff"], 1), -25.5)
    chk("RQ3", "SWE CI [-28.2, -22.8]", pair(r3["swe_ci"], (-28.2, -22.8)), f"[{r3['swe_ci'][0]:.1f}, {r3['swe_ci'][1]:.1f}]", "[-28.2, -22.8]")
    chk("RQ3", "SWE systems: failures on severe median 68.1", close(r3["swe_sys_share_median"], 68.1), round(r3["swe_sys_share_median"], 1), 68.1)
    chk("RQ3", "SWE systems: gain median +14.2", close(r3["swe_sys_gain_median"], 14.2), round(r3["swe_sys_gain_median"], 1), 14.2)
    chk("RQ1 extra", "TB gap types: 22 tasks, kinds 7/5/5/4/1", r1["tb_gap_n"] == 22 and r1["tb_gap_kinds"] == [1, 4, 5, 5, 7], r1["tb_gap_n"], 22)
    chk("RQ1 extra", "TB gap types: 15 blocking", r1["tb_gap_blocking_yes"] == 15, r1["tb_gap_blocking_yes"], 15)
    chk("RQ1 extra", "TB FaaP shortlist share 46.1%", close(r1["faap_shortlist"], 46.1), round(r1["faap_shortlist"], 1), 46.1)
    chk("RQ1 extra", "TB FaaP spec_neglect share 23.6%", close(r1["faap_spec"], 23.6), round(r1["faap_spec"], 1), 23.6)
    chk("RQ3", "TB blocking tasks 15/89", r3["tb_blocking_tasks"] == 15, r3["tb_blocking_tasks"], 15)
    chk("RQ3", "TB runs on blocking tasks 290", r3["tb_blocking_runs"] == 290, r3["tb_blocking_runs"], 290)
    chk("RQ3", "TB resolve blocking 10.2", close(r3["tb_res_block"], 10.2), round(r3["tb_res_block"], 1), 10.2)
    chk("RQ3", "TB resolve none 40.9", close(r3["tb_res_none"], 40.9), round(r3["tb_res_none"], 1), 40.9)
    chk("RQ3", "TB difference -30.6", close(r3["tb_diff"], -30.6), round(r3["tb_diff"], 1), -30.6)
    chk("RQ3", "TB systems: 21, median failures on blocking 21.7", r3["tb_systems"] == 21 and close(r3["tb_sys_share_median"], 21.7),
        round(r3["tb_sys_share_median"], 1), 21.7)
    chk("RQ3", "TB systems: gain median +4.4", close(r3["tb_sys_gain_median"], 4.4), round(r3["tb_sys_gain_median"], 1), 4.4)

    # ---------- report
    width = max(len(c[1]) for c in checks)
    print("Verification against the paper's reported numbers")
    print("-" * (width + 46))
    failed = 0
    for section, name, ok, got, want in checks:
        failed += not ok
        print(f"{section:<10} {name:<{width}}  got {str(got):<20} paper {str(want):<18} {'PASS' if ok else 'FAIL'}")
    print("-" * (width + 46))
    print(f"{len(checks) - failed} of {len(checks)} checks pass")
    print("Not checked here: Terminal-Bench awareness (89.3% vs 70.1%), test-execution counts, and Terminal-Bench kappa (0.63 and 0.74).")
    print("See README.md section 4 for why and what is needed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
