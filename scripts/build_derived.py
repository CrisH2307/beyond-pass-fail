#!/usr/bin/env python3
"""Build the derived files in data/ from the authors' working folders.

Run once by the authors. The package scripts (02 to 05) read only data/, so this file is needed
only to rebuild data/ from the raw inputs, which are not redistributed (see data/README.md).

    python3 scripts/build_derived.py --repo <path to AgentVerify_Code_Repo> --out data

Raw inputs read (relative to --repo):
  .worktrees/prep-v5/labels/labels_v5.csv                        Terminal-Bench v5 labels (label, v4_label)
  labels/key.csv                                                 Terminal-Bench sampling key (candidate / random)
  .worktrees/prep-v5/exploratory/wp5_nebius/...                  Nebius labels, audits, sample, run index
  .worktrees/prep-v5/exploratory/continue_work/...               Nebius and SWE-bench v2 labels, consensus audit
  .worktrees/prep-v5/exploratory/wp6_swebench/...                SWE-bench sample, agent patches, gold patches
  .worktrees/prep-v5/exploratory/addendum_rq2_rq3/...            SWE-bench resolved lists and OpenAI annotations
Needs pyarrow (SWE-bench gold patches are Parquet). Standard library otherwise.
"""
import argparse
import csv
import glob
import gzip
import io
import json
import os
import re
import statistics
import zipfile
from collections import defaultdict

import pyarrow.parquet as pq

ap = argparse.ArgumentParser()
ap.add_argument("--repo", required=True)
ap.add_argument("--out", required=True)
args = ap.parse_args()
REPO = os.path.abspath(args.repo)
OUT = os.path.abspath(args.out)
EX = os.path.join(REPO, ".worktrees", "prep-v5", "exploratory")
NB = os.path.join(EX, "wp5_nebius")
NBJ = os.path.join(NB, "annotation_jobs")
SW = os.path.join(EX, "wp6_swebench")
SWJ = os.path.join(SW, "annotation_jobs")
CW = os.path.join(EX, "continue_work")
ADD = os.path.join(EX, "addendum_rq2_rq3")
CLI = os.path.join(REPO, "cli_trajectory_analysis", "data", "v2_annotations")
for sub in ("run_labels", "task_audits", "telemetry_and_scores"):
    os.makedirs(os.path.join(OUT, sub), exist_ok=True)


def rcsv(path, enc="utf-8-sig"):
    with open(path, encoding=enc, newline="") as f:
        return list(csv.DictReader(f))


def wcsv(path, fields, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def labels_csv(path):
    return {r["item_id"].strip(): (r["label"].strip().upper(), r.get("note") or "") for r in rcsv(path)}


def labels_json(path):
    return {r["item_id"].strip(): (r["label"].strip().upper(), r.get("note") or "") for r in json.load(open(path))}


def audit_csv(path):
    out = {}
    for r in rcsv(path):
        h = (r["hidden_requirement"] or "").strip().lower()
        b = (r["blocking"] or "").strip().lower()
        out[r["item_id"].strip()] = (h, b if h == "yes" else "no", r.get("note") or "")
    return out


def audit_json(path):
    out = {}
    for r in json.load(open(path)):
        h = (r["hidden_requirement"] or "").strip().lower()
        b = (r["blocking"] or "").strip().lower()
        out[r["item_id"].strip()] = (h, b if h == "yes" else "no", r.get("note") or "")
    return out


# ------------------------------------------------------------------ Terminal-Bench
key = rcsv(os.path.join(REPO, "labels", "key.csv"))
v5 = {r["item_id"].strip(): r for r in rcsv(os.path.join(REPO, ".worktrees", "prep-v5", "labels", "labels_v5.csv"))}
rows = []
for k in key:
    r = v5[k["item_id"].strip()]
    rows.append({
        "item_id": k["item_id"], "run_id": k["run_id"], "task": r["task"],
        "stratum": k["source"], "weight": 1 if k["source"] == "candidate" else round(873 / 100, 2),
        "faap_trigger": k["faap_trigger"], "faap_category": k["faap_category"],
        "label_v4": r["v4_label"], "label_v5": r["label"], "note_v5": r.get("note") or "",
    })
wcsv(os.path.join(OUT, "run_labels", "terminal_bench_run_labels.csv"),
     ["item_id", "run_id", "task", "stratum", "weight", "faap_trigger", "faap_category", "label_v4", "label_v5", "note_v5"], rows)
print("TB run labels", len(rows))

tb_audit = os.path.join(EX, "inputs", "task_audit.csv")
if os.path.exists(tb_audit):
    with open(tb_audit, "rb") as src, open(os.path.join(OUT, "task_audits", "terminal_bench_task_audit.csv"), "wb") as dst:
        dst.write(src.read())

# ------------------------------------------------------------------ Nebius run labels (N081-N440)
nb_r1, nb_r3 = {}, {}
nb_r1.update(labels_csv(os.path.join(NB, "labeling_sheet_N081-N120_cris_v1_strict.csv")))
nb_r3.update(labels_csv(os.path.join(NB, "labeling_sheet_N081-N120_cris_v2_alt.csv")))  # see data/README.md, open issue
for b in ("N121-N200", "N201-N280", "N281-N320"):
    nb_r1.update(labels_csv(os.path.join(NBJ, f"labeling_sheet_{b}_cris.csv")))
    nb_r3.update(labels_csv(os.path.join(NBJ, f"labeling_sheet_{b}_R3.csv")))
for b in ("N321-N360", "N361-N400", "N401-N440"):
    nb_r1.update(labels_json(os.path.join(CW, "cris", f"runs_{b}_v2.json")))
    nb_r3.update(labels_json(os.path.join(CW, "R3", f"runs_{b}_v2.json")))
nb_r1 = {k: v for k, v in nb_r1.items() if 81 <= int(k[1:]) <= 440}
nb_r3 = {k: v for k, v in nb_r3.items() if 81 <= int(k[1:]) <= 440}
assert len(nb_r1) == len(nb_r3) == 360, (len(nb_r1), len(nb_r3))

samp = {}
for f in (os.path.join(NB, "sample.csv"), os.path.join(NB, "ext_N121-N320", "sample.csv"), os.path.join(NB, "ext_N321-N440", "sample.csv")):
    for r in rcsv(f):
        samp[r["item_id"]] = r
rows = []
for it in sorted(nb_r1, key=lambda x: int(x[1:])):
    s = samp[it]
    rows.append({"item_id": it, "instance_id": s["instance_id"], "model_name": s["model_name"], "exit_status": s["exit_status"],
                 "R1_label": nb_r1[it][0], "R1_note": nb_r1[it][1], "R3_label": nb_r3[it][0], "R3_note": nb_r3[it][1]})
wcsv(os.path.join(OUT, "run_labels", "nebius_run_labels.csv"),
     ["item_id", "instance_id", "model_name", "exit_status", "R1_label", "R1_note", "R3_label", "R3_note"], rows)
print("Nebius run labels", len(rows))

# ------------------------------------------------------------------ SWE-bench run labels (S001-S320)
sw_r1, sw_r3 = {}, {}
for b in ("S001-S040", "S041-S120", "S121-S180", "S181-S240"):
    sw_r1.update(labels_csv(os.path.join(SWJ, f"labeling_sheet_{b}_cris.csv")))
    sw_r3.update(labels_csv(os.path.join(SWJ, f"labeling_sheet_{b}_R3.csv")))
for b in ("S241-S280", "S281-S320"):
    sw_r1.update(labels_json(os.path.join(CW, "cris", f"runs_{b}_v2.json")))
    sw_r3.update(labels_json(os.path.join(CW, "R3", f"runs_{b}_v2.json")))
assert len(sw_r1) == len(sw_r3) == 320
sw_meta = {}
for f in (os.path.join(SW, "raw", "sampled_runs.jsonl.gz"), os.path.join(SW, "ext_S241-S320", "raw", "sampled_runs.jsonl.gz")):
    for line in gzip.open(f, "rt"):
        r = json.loads(line)
        sw_meta[r["item_id"]] = r
rows = []
for it in sorted(sw_r1, key=lambda x: int(x[1:])):
    m = sw_meta[it]
    rows.append({"item_id": it, "instance_id": m["instance_id"], "exit_status": m["exit_status"],
                 "R1_label": sw_r1[it][0], "R1_note": sw_r1[it][1], "R3_label": sw_r3[it][0], "R3_note": sw_r3[it][1]})
wcsv(os.path.join(OUT, "run_labels", "swebench_run_labels.csv"),
     ["item_id", "instance_id", "exit_status", "R1_label", "R1_note", "R3_label", "R3_note"], rows)
print("SWE run labels", len(rows))

# ------------------------------------------------------------------ Nebius task audits (N001-N360)
a_r1 = audit_csv(os.path.join(NB, "task_audit_N001-N080_cris_v1_merged.csv"))
a_r3 = audit_csv(os.path.join(NB, "task_audit_N001-N080_rater3_merged.csv"))
for b in ("N081-N120", "N121-N160", "N161-N200", "N201-N240", "N241-N280", "N281-N320", "N321-N360"):
    a_r1.update(audit_json(os.path.join(CW, "cris", f"audit_{b}.json")))
    a_r3.update(audit_json(os.path.join(CW, "R3", f"audit_{b}.json")))
assert len(a_r1) == len(a_r3) == 360
cons = audit_csv(os.path.join(CW, "discussion", "task_audit_N001-N360_consensus.csv"))
assert set(cons) == set(a_r1) == set(a_r3)
# Row order is kept as in the working files: the RQ3 bootstrap draws depend on it.
for name, a in (("R1", a_r1), ("R3", a_r3), ("consensus", cons)):
    rows = [{"item_id": k, "hidden_requirement": v[0], "blocking": v[1], "note": v[2]} for k, v in a.items()]
    wcsv(os.path.join(OUT, "task_audits", f"nebius_task_audit_{name}_N001-N360.csv"),
         ["item_id", "hidden_requirement", "blocking", "note"], rows)
# Audit disagreements before discussion (R1 and R3 differ) and what the consensus chose.
rows = []
for i in a_r1:
    if a_r1[i][:2] != a_r3[i][:2]:
        c = cons[i]
        rows.append({"item_id": i,
                     "R1_hidden": a_r1[i][0], "R1_blocking": a_r1[i][1],
                     "R3_hidden": a_r3[i][0], "R3_blocking": a_r3[i][1],
                     "consensus_hidden": c[0], "consensus_blocking": c[1],
                     "consensus_matches_R1": int(c[:2] == a_r1[i][:2]),
                     "consensus_matches_R3": int(c[:2] == a_r3[i][:2]),
                     "consensus_note": c[2]})
wcsv(os.path.join(OUT, "task_audits", "nebius_disagreement_resolution.csv"), list(rows[0].keys()), rows)
print("audit disagreements", len(rows))

# ------------------------------------------------------------------ Nebius run outcomes (for RQ3)
want = {samp[i]["instance_id"]: i for i in a_r1}
rows = []
for r in csv.DictReader(gzip.open(os.path.join(NB, "runs_index.csv.gz"), "rt")):
    if r["instance_id"] in want:
        rows.append({"audit_item_id": want[r["instance_id"]], "instance_id": r["instance_id"], "model_name": r["model_name"],
                     "resolved": 1 if r["target"] == "True" else 0, "exit_status": r["exit_status"]})
wcsv(os.path.join(OUT, "telemetry_and_scores", "nebius_run_outcomes.csv"),
     ["audit_item_id", "instance_id", "model_name", "resolved", "exit_status"], rows)
print("Nebius run outcomes", len(rows))

# ------------------------------------------------------------------ SWE-bench calibration (40 tasks)
c_r1 = audit_json(os.path.join(CW, "cris", "audit_calib.json"))
c_r3 = audit_json(os.path.join(CW, "R3", "audit_calib.json"))
for name, c in (("R1", c_r1), ("R3", c_r3)):
    rows = [{"item_id": k, "hidden_requirement": v[0], "blocking": v[1], "note": v[2]} for k, v in c.items()]
    wcsv(os.path.join(OUT, "task_audits", f"swebench_calibration_audit_{name}.csv"), ["item_id", "hidden_requirement", "blocking", "note"], rows)
oa = rcsv(os.path.join(SW, "calib_audit", "hidden_openai_ratings_DO_NOT_OPEN.csv"))
wcsv(os.path.join(OUT, "task_audits", "swebench_calibration_openai_ratings.csv"),
     ["item_id", "instance_id", "false_negative", "false_negative_notes"],
     [{"item_id": r["item_id"], "instance_id": r["instance_id"], "false_negative": r["false_negative"],
       "false_negative_notes": r["false_negative_notes"]} for r in oa])

# ------------------------------------------------------------------ SWE-bench RQ3 inputs (OpenAI ratings + resolved lists)
SUBS = ['20231010_rag_claude2', '20231010_rag_gpt35', '20231010_rag_swellama13b', '20231010_rag_swellama7b', '20240402_rag_claude3opus',
        '20240402_rag_gpt4', '20240402_sweagent_claude3opus', '20240402_sweagent_gpt4', '20240509_amazon-q-developer-agent-20240430-dev',
        '20240615_appmap-navie_gpt4o', '20240617_factory_code_droid', '20240620_sweagent_claude3.5sonnet', '20240628_autocoderover-v20240620',
        '20240721_amazon-q-developer-agent-20240719-dev', '20240728_sweagent_gpt4o', '20240820_honeycomb',
        '20241103_OpenHands-CodeAct-2.1-sonnet-20241022', '20241121_autocoderover-v2.0-claude-3-5-sonnet-20241022',
        '20250131_amazon-q-developer-agent-20241202-dev', '20250227_sweagent-claude-3-7-20250219', '20250522_amazon-q-developer-agent-20250405-dev',
        '20250605_atlassian-rovo-dev', '20251027_salesforce_SAGE', '20251219_sonar-foundation-agent_claude-opus-4-5']
assert len(SUBS) == 24
zf = zipfile.ZipFile(os.path.join(SW, "raw", "swe-bench-annotation-results.zip"))
ens = {r["instance_id"]: float(r["false_negative"]) for r in csv.DictReader(io.TextIOWrapper(zf.open("ensembled_annotations_public.csv"), encoding="utf-8"))}
three = defaultdict(list)
for r in csv.DictReader(io.TextIOWrapper(zf.open("samples_with_3_annotations_public.csv"), encoding="utf-8")):
    if r["false_negative"].strip() != "":
        three[r["instance_id"]].append(float(r["false_negative"]))
rows = []
for iid in sorted(ens):
    rows.append({"instance_id": iid, "ensemble_false_negative": ens[iid],
                 "annotator_scores": ";".join(str(x) for x in three.get(iid, []))})
wcsv(os.path.join(OUT, "telemetry_and_scores", "swebench_openai_severity.csv"),
     ["instance_id", "ensemble_false_negative", "annotator_scores"], rows)
print("OpenAI severity tasks", len(rows))
rows = []
for s in SUBS:
    res = set(json.load(open(os.path.join(ADD, "..", "wp6_swebench", "raw", "results", f"{s}.json"))).get("resolved", []))
    for iid in sorted(ens):
        rows.append({"submission": s, "instance_id": iid, "resolved": 1 if iid in res else 0})
wcsv(os.path.join(OUT, "telemetry_and_scores", "swebench_resolved_by_submission.csv"), ["submission", "instance_id", "resolved"], rows)
print("SWE resolved rows", len(rows))

# ------------------------------------------------------------------ SWE-bench patch telemetry (Table II)
gold = {}
for f in glob.glob(os.path.join(SW, "*.parquet")):
    for r in pq.read_table(f, columns=["instance_id", "patch"]).to_pylist():
        gold[r["instance_id"]] = r["patch"]


def files(diff):
    out = {}
    for blk in re.split(r"(?m)^diff --git ", diff or "")[1:]:
        m = re.match(r"a/(\S+) b/(\S+)", blk)
        if not m:
            continue
        path = m.group(2)
        new = "new file mode" in blk or "\n--- /dev/null" in blk
        ch = sum(1 for l in blk.splitlines() if (l.startswith("+") or l.startswith("-")) and not l.startswith(("+++", "---")))
        out[path] = (new, ch)
    return out


is_test = lambda p: bool(re.search(r"(^|/)(tests?|testing)(/|$)|(^|/)test_[^/]*$|_tests?\.py$|conftest\.py$", p))
rows = []
for it in sorted(sw_r1, key=lambda x: int(x[1:])):
    m = sw_meta[it]
    a = files(m["agent_final_patch"])
    g = files(gold[m["instance_id"]])
    gsrc = {p for p in g if not is_test(p)}
    ref = any(p in gsrc for p in a)
    other = any(p not in g and not (n and "/" not in p) and not is_test(p) for p, (n, _) in a.items())
    scratch = any(n and "/" not in p and p not in g for p, (n, _) in a.items())
    rows.append({"item_id": it, "instance_id": m["instance_id"], "exit_status": m["exit_status"],
                 "ref_file_edit": int(ref), "other_file_edit": int(other), "scratch_file_added": int(scratch),
                 "agent_changed_lines": sum(ch for _, (_, ch) in a.items()),
                 "ref_changed_lines": sum(ch for p, (_, ch) in g.items() if not is_test(p))})
wcsv(os.path.join(OUT, "telemetry_and_scores", "swebench_run_patch_metrics.csv"),
     ["item_id", "instance_id", "exit_status", "ref_file_edit", "other_file_edit", "scratch_file_added", "agent_changed_lines", "ref_changed_lines"], rows)
print("SWE patch metrics", len(rows))

# ------------------------------------------------------------------ Terminal-Bench run outcomes (for RQ3)
failed = {r["run_id"] for r in rcsv(os.path.join(REPO, "data", "processed", "failed_runs.csv"))}
all_runs = {os.path.basename(f)[:-5] for f in glob.glob(os.path.join(CLI, "*.json"))} | failed
rows = []
for rid in sorted(all_runs):
    task, scaffold_model = rid.split("__", 1)
    rows.append({"run_id": rid, "task": task, "system": scaffold_model, "failed": 1 if rid in failed else 0})
wcsv(os.path.join(OUT, "telemetry_and_scores", "terminal_bench_run_outcomes.csv"), ["run_id", "task", "system", "failed"], rows)
print("TB run outcomes", len(rows), "failed", sum(r["failed"] for r in rows))
print("done")
