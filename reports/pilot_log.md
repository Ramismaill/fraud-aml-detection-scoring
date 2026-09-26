\# M1 Pilot — Daily Log



| Day | Date | Notebook(s) | Status | Wall time | Peak RAM | Blocker | Next |

|---|---|---|---|---|---|---|---|

| 1 | 2026-09-25 | 00\_setup, 01\_download | done | download 66 s (725 MB); row counts verified | 0.27 GB | none | 02\_audit\_baf |

| 2 | 2026-09-26 | 02\_audit\_baf | done | read 2.4 s; parquet write 2.3 s; 69.5 MB | 1.00 GB | none | 03\_audit\_aml |



\## Day 2 notes

\- Negative-valued columns confirmed: five community-listed columns use -1 only; credit\_risk\_score and velocity\_6h have real negative values.

\- velocity\_\* features are precomputed by the dataset generator; past-only cannot be verified from the file and is assumed from dataset design. Documented as a limitation.

\- Label-distribution shift: prevalence rises from 0.998% (train) to 1.404% (test).

\- Missing-code signal is column-specific: 3 columns higher fraud when negative, 2 lower, 1 null. All 6 flags will be created in 04.

\- Temporal variation in missing-code prevalence assessed as a feature-distribution shift indicator; bank\_months\_count is lower in month 0 only.

