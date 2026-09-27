# M1 Pilot — Daily Log


| Day | Date | Notebook(s) | Status | Wall time | Peak RAM | Blocker | Next |
|---|---|---|---|---|---|---|---|
| 1 | 2026-09-25 | 00_setup, 01_download | done | download 66 s (725 MB); row counts verified | 0.27 GB | none | 02_audit_baf |
| 2 | 2026-09-26 | 02_audit_baf | done | read 2.4 s; parquet write 2.3 s; 69.5 MB | 1.00 GB | none | 03_audit_aml |
| 3 | 2026-09-27 | 03_audit_aml | done | load 12 s; parquet 7 s; 165 MB | 2.37 GB | none | 04_baf_baseline |



## Day 2 notes

- Negative-valued columns confirmed: five community-listed columns use -1 only; credit_risk_score and velocity_6h have real negative values.

- velocity_* features are precomputed by the dataset generator; past-only cannot be verified from the file and is assumed from dataset design. Documented as a limitation.

- Label-distribution shift: prevalence rises from 0.998% (train) to 1.404% (test).

- Missing-code signal is column-specific: 3 columns higher fraud when negative, 2 lower, 1 null. All 6 flags will be created in 04.

- Temporal variation in missing-code prevalence assessed as a feature-distribution shift indicator; bank_months_count is lower in month 0 only.


## Day 3 notes (in progress)
- AML audit: normal traffic ends 2022-09-10; the 2022-09-11 to 09-18 tail (1,108 tx, 59% laundering) sits entirely in test.
- test_core prevalence (0.1126%) is close to valid (0.1065%): the apparent train->test rise on AML is attributable to the tail.

- AML: 591,212 self-loops (11 laundering), kept as transactions; to be excluded from counterparty features in 05 (decision to register there).
- AML: 72,170 cross-currency transfers, 0 laundering: the cross-currency red flag from the handoff does not hold in HI-Small.
- AML: ACH carries 4,483 of 5,177 laundering (0.75% vs 0.10% overall); 9 exact duplicate rows kept and documented.
- DAY-3 CHECKPOINT: GREEN. Both audits complete; Parquet round-trips verified; label rates in range (BAF 0.998/1.183/1.404% per split; AML 0.1019%).
