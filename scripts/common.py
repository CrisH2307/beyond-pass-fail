"""Shared helpers for the replication scripts. Standard library only.

All paths are relative to this file, so the package runs from any working directory.
"""
import csv
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
DATA = os.path.join(PKG, "data")
RESULTS = os.path.join(PKG, "results")
SEED = 20260925  # fixed seed for every bootstrap in the paper


def read(rel):
    """Read a CSV under data/ as a list of dicts (UTF-8, BOM tolerated)."""
    with open(os.path.join(DATA, rel), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clopper_pearson(k, n, alpha=0.05):
    """Exact two-sided binomial interval, returned as proportions in [0, 1]."""
    from math import comb

    def cdf(j, p):
        return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(j + 1))

    def solve(f):
        lo, hi = 0.0, 1.0
        for _ in range(100):
            mid = (lo + hi) / 2
            if f(mid):
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    low = 0.0 if k == 0 else solve(lambda p: 1 - cdf(k - 1, p) < alpha / 2)
    high = 1.0 if k == n else solve(lambda p: cdf(k, p) > alpha / 2)
    return low, high


def share_line(count, n):
    lo, hi = clopper_pearson(count, n)
    return 100 * count / n, 100 * lo, 100 * hi


def kappa(a, b):
    """Cohen's kappa and percent agreement for two dicts keyed by item id."""
    ids = sorted(set(a) & set(b))
    pairs = [(a[i], b[i]) for i in ids]
    n = len(pairs)
    po = sum(x == y for x, y in pairs) / n
    ca = Counter(x for x, _ in pairs)
    cb = Counter(y for _, y in pairs)
    pe = sum(ca[t] * cb[t] for t in set(ca) | set(cb)) / n ** 2
    return (po - pe) / (1 - pe), 100 * po, n


def run_category(label, note):
    """Four-way run category used for Nebius and SWE-bench (R1 and R3 labels)."""
    lab = (label or "").strip().upper()
    note = (note or "").lower()
    if lab == "ANCHORED":
        return "explicit"
    if lab == "NOT":
        return "implicit" if "implicit" in note else "other"
    return "unclear"


def failure_kind(label, note):
    """Splits 'other' into no fix and incorrect fix."""
    cat = run_category(label, note)
    if cat != "other":
        return cat
    n = (note or "").lower().strip()
    return "no_fix" if n.startswith(("no_fix", "no fix")) else "incorrect_fix"


def fmt(x):
    return f"{x:.1f}"
