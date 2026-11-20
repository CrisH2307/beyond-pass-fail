## Table II, SWE-bench patch metrics (n = 320, R1 kinds)
| Failure (n) | Ref. file | Other | Scratch | Lines agent/ref | Ends on own |
|---|---:|---:|---:|---:|---:|
| No fix (76) | 4% | 33% | 72% | 29/27 | 24% |
| Explicit (37) | 68% | 51% | 43% | 22/14 | 65% |
| Incorrect fix (131) | 86% | 24% | 47% | 25/14 | 55% |
| Implicit (76) | 89% | 24% | 24% | 12/11 | 92% |
Note: the paper shows '-' for the No fix line-count cell; this script computes it (see protocols/ANALYSIS_PLANS.md, deviation 7).

## Ends on its own, by R1 kind
| Source | No fix | Explicit | Incorrect fix | Implicit |
|---|---:|---:|---:|---:|
| SWE-bench | 24% (n=76) | 65% (n=37) | 55% (n=131) | 92% (n=76) |
| Nebius blind | 28% (n=123) | 66% (n=62) | 64% (n=118) | 77% (n=57) |

