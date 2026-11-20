"""Figure 4: share of Explicit, Implicit and Other failures per benchmark, with 95% intervals.

Reads the numbers produced by 02_rq1.py (no hard-coded values). Writes results/figure4.pdf and .png.
Run:  python3 scripts/05_figure4.py     (needs matplotlib)
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from common import RESULTS  # noqa: E402
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("rq1", os.path.join(os.path.dirname(os.path.abspath(__file__)), "02_rq1.py"))
rq1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rq1)


def main():
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()):
        res = rq1.main(out_lines=[])
    datasets = ["Terminal-Bench", "Nebius", "SWE-bench"]
    keys = {"Terminal-Bench": "tb", "Nebius": "Nebius", "SWE-bench": "SWE-bench"}
    cats = [("explicit", "Explicit"), ("implicit", "Implicit"), ("other", "Other")]
    colors = {"explicit": "#2a78d6", "implicit": "#eb6834", "other": "#b8b5ad"}
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    width = 0.25
    for j, (cat, label) in enumerate(cats):
        xs = [i + (j - 1) * width for i in range(len(datasets))]
        vals = [res[f"{keys[d]}_{cat}"] for d in datasets]
        lo = [res[f"{keys[d]}_{cat}_ci"][0] for d in datasets]
        hi = [res[f"{keys[d]}_{cat}_ci"][1] for d in datasets]
        err = [[v - l for v, l in zip(vals, lo)], [h - v for v, h in zip(vals, hi)]]
        ax.bar(xs, vals, width, color=colors[cat], label=label, yerr=err, capsize=3, error_kw={"lw": 0.8})
        for x, v, h in zip(xs, vals, hi):
            ax.text(x, h + 1.2, f"{v:.1f}", ha="center", fontsize=7)  # label sits above the upper interval bound
    ax.set_xticks(range(len(datasets)))
    ax.set_xticklabels(datasets)
    ax.set_ylabel("Share of failed runs (%)")
    ax.set_ylim(0, 85)
    ax.legend(frameon=False, fontsize=8, ncol=3, loc="upper center")
    fig.tight_layout()
    os.makedirs(RESULTS, exist_ok=True)
    fig.savefig(os.path.join(RESULTS, "figure4.pdf"))
    fig.savefig(os.path.join(RESULTS, "figure4.png"), dpi=200)
    print("wrote results/figure4.pdf and results/figure4.png")


if __name__ == "__main__":
    main()
