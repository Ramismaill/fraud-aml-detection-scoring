# M1 Pilot — Decision Log



Reviewed with DeepSeek (external reviewer). Project rules (handoff §4, §6, §7)

take priority over any reviewer. Thresholds below are PRE-REGISTERED and will

NOT be edited after pilot results are seen (day 7).



## DECISION #1 — Pilot scope (2026-09-25)

- Chosen: 8-notebook feasibility pilot; stop at INITIAL RESULTS; per-dataset

&#x20; evaluation, no unified analyst queue; K-Means/Apriori/SHAP as smoke tests only.

- Alternatives: full 3-week MVP; BAF-only pilot.

- Why: fair comparison with the EPIAS pilot (stopped at the same level);

&#x20; AMLworld leakage-free features are the key feasibility question.

- Risk: day 4 (AML rolling features) is the heaviest step.

- Mitigation (DeepSeek, accepted): hard checkpoint end of day 3 — both audits

&#x20; green (Parquet written, row counts match source, label rates in range) or

&#x20; stop and ship a 4-notebook report. Day 6 time-boxed: 3 blocks x 30 min.

- DeepSeek view: drop K-Means/Apriori → REJECTED (Muhammet's instruction §6;

&#x20; instructor wants all techniques; TreeExplainer on \~2k rows is standard).



## DECISION #2 — PASS / CONDITIONAL / FAIL criteria (pre-registered)

- BAF PASS: Recall@5%FPR >= 0.40 (pre-registered guess, no citation);

&#x20; PR-AUC > 5x prevalence; leakage checks pass.

- AML PASS: at least one of PR-AUC >= 0.01 | minority-F1 >= 0.10 |

&#x20; Recall@5%FPR >= 0.20, AND lower bound of 95% bootstrap CI (200 resamples)

&#x20; of PR-AUC > prevalence.

- Lift@1%: reported as supporting evidence, not gating.

- General: both baselines run end-to-end; AML features <= 1 working day;

&#x20; peak RAM < 12 GB.

- CONDITIONAL: everything runs but one dataset needed subsampling or > 1 day,

&#x20; or one metric below threshold with an understood reason.

- FAIL: leakage-free AML features cannot be built on this hardware, or no

&#x20; signal above prevalence.

- Note: no published PR-AUC figures for AMLworld HI-Small with simple

&#x20; features; the AML thresholds are informed guesses, stated as such.



## DECISION #3 — Cold-start policy for AML rolling features

- Chosen: no rows dropped. "No history at time t" is knowable at t → not

&#x20; leakage. Add `account_age_hours` (time since first appearance).

- Alternatives: drop warm-up rows (impossible: 10-day dataset, 7d window);

&#x20; expanding window (changes feature meaning over time).

- Limitation: 7d windows are fully warm only from day 7; reported in drift-by-day.



## DECISION #4 — Derived features under cold-start (DeepSeek, accepted)

- Count-like features (n_tx, n_unique_peers, n_currencies): 0 when no history.

- Aggregates (mean/std/max amount): NULL when no history (LightGBM handles NaN).

- Ratios (pass-through, amt/mean): NULL when denominator is 0.

- No companion has_history flag (redundant with count == 0).

- Check: fraction of NULL aggregates per day must decrease over the train

&#x20; period (computed in 05, reported in 08).

- Open: IF/COPOD do not accept NaN → imputation rule decided in 06.



## Metrics (both datasets)

PR-AUC, Recall@5%FPR, Precision@100, Lift@1% (supporting); AML also

minority-class F1 (comparable to the AMLworld paper); BAF also FPR ratio by

customer_age >= 50 (predictive equality).



## Why the two datasets are never joined

BAF and AMLworld share no customers, banks or time axis, and their labels

mean different things (fraudulent application vs laundering transfer).

Cross-dataset transfer is out of scope for this pilot.

## DECISION #2a — Prevalence reference for thresholds (2026-09-26, clarification)
- Audit found label-distribution shift: train 0.998%, valid 1.183%, test 1.404%.
- All "x prevalence" thresholds are measured against the prevalence of the set
  being evaluated (BAF test: 0.01404 -> PR-AUC threshold 5x = 0.070), not the
  global 1.10% (0.055). Stricter reading of an ambiguous definition; multiplier unchanged.
- These thresholds are project-specific acceptance criteria, not general
  benchmarks for fraud detection.

## Day-3 checkpoint wording (amended 2026-09-26)
- BAF: label rate within 0.85-1.5% per split (handoff range).
- AML: overall label rate close to the paper's HI-Small ratio (1/981 = 0.102%);
  per-day rates reported descriptively.
- Prevalence non-stationarity across splits is a finding, not a failure.

## DECISION #5 — Representation of intended_balcon_amount (procedure pre-registered 2026-09-26)
- Evidence (02_audit_baf Cell 4): 74% negative; 99% of negatives in [-1.87, -0.18]
  around -1.01; fraud ~1.2-1.4% across negative bins vs ~0.5-0.6% across
  non-negative bins (discontinuity at zero, no gradient in magnitude).
  This is an association, not proof that negatives mean "missing".
- Resolution order:
  1. Official feature description (Feedzai datasheet) if it defines negatives.
  2. Otherwise, experiment in 04 on the validation month (5), same LightGBM
     settings and SEED: A = raw value; B = raw value + flag (v < 0);
     C = flag + value set to NaN when v < 0.
     Winner = highest validation PR-AUC; if |delta| < 5% of the best value,
     choose the simplest (A).
- Pre-registered prediction: A ~ B > C. If results contradict it, the sentinel
  hypothesis is revisited in the report.
- The test set is not used for this choice.

## Audit findings recorded as limitations
- velocity_* features are precomputed by the dataset generator; past-only cannot
  be verified from the file and is assumed from dataset design.
- velocity_6h contains 44 negative observations despite being count-like
  (9 train / 11 valid / 24 test, none fraud). Treated as a dataset-generation
  anomaly and retained without modification.
- Negative-valued columns: the five community-listed columns use -1 only;
  credit_risk_score and velocity_6h have many distinct negative values (real values).
  The data confirms the encoding pattern, not the semantics ("missing").
- Licence: Kaggle API reported "CC-BY-NC-SA-4.0" for the BAF dataset on
  2026-09-25 (handoff said CC BY-NC-ND). Non-commercial: this project is a
  research/feasibility artifact; any production use needs a separate licensing
  review. Data is never committed.

## DECISION #2b — AML PASS rule tightened (Muhammet, 2026-09-26, before any model result)
- AML PASS requires ALL of:
  1. Rolling features past-only; chronological 60/20/20 split (no random split).
  2. PR-AUC >= max(0.01, 5 x AML test prevalence)   [mandatory]
  3. At least one of: Recall@5%FPR >= 0.20 | minority-class F1 >= 0.10
  4. Lower bound of the 95% block-bootstrap CI of PR-AUC > AML test prevalence.
- Replaces the AML "one of three" rule in DECISION #2. BAF rule unchanged.
- If criteria 1-3 hold but criterion 4 fails, the verdict is CONDITIONAL, not FAIL
  (test sample too small to separate from chance: a feasibility finding).
- Bootstrap: resample time blocks, not rows (same-account, same-period transactions
  are dependent). Block size chosen so that the test set has 40-400 blocks: daily
  if the test period spans >= 40 days, otherwise hourly. Fixed from the audit
  (03_audit_aml) before modelling. 200 resamples.
- Thresholds: Recall@5%FPR is a ranking metric computed on test (as in the BAF paper).
  The F1 decision threshold and risk-band cut-offs are chosen on validation only
  and then applied unchanged to test.
- Reported, not gating: Precision@100, Precision@500, lift vs test prevalence.
- 06_anomaly: add flag velocity_6h_invalid_negative and check that the 44
  impossible values do not dominate IF/COPOD top-ranked anomalies.


## DECISION #6 — AML split, evaluation window and time features (2026-09-26, from audit, before any feature or model)
- Audit (03_audit_aml): 5,078,345 tx; 5,177 laundering (0.1019%, equal to the 1/981 ratio).
  Time range 2022-09-01 00:00 -> 2022-09-18 16:18 (17.68 days); normal traffic ends
  2022-09-10. Tail 2022-09-11 -> 09-18: 1,108 tx, 655 laundering (59.1%), 100% ACH;
  398 of 403 tail source accounts were active before the tail, 5 have no earlier history.
  Interpretation: consistent with the generator completing laundering patterns started
  earlier; the paper table in the handoff lists HI-Small as 10 days (not re-verified
  from the paper). Hypothesis, not proven.
- Split: chronological by transaction share. cut60 = 2022-09-06 13:36,
  cut80 = 2022-09-08 16:12 (rows with ts < cut go to the earlier split); these two
  timestamps define the split.
  train 3,046,861 (0.0754%) | valid 1,015,602 (0.1065%) | test 1,015,882 (0.1770%).
- Evaluation window: gating metrics are computed on test_core = test with
  ts < 2022-09-11: 1,014,774 tx, 1,143 laundering (0.1126%), 56 hourly blocks.
  Full-test metrics are reported for comparison with the paper but do not gate.
  The tail is kept in the data, not deleted.
- Finding: the higher full-test prevalence is attributable to the tail; within the
  normal-traffic window, prevalence (0.1126%) is close to validation (0.1065%).
- AML PASS (full rule from #2b, on test_core): PR-AUC >= max(0.01, 5 x 0.001126) = 0.01
  AND (Recall@5%FPR >= 0.20 OR minority-F1 >= 0.10) AND lower bound of the 95%
  hourly block-bootstrap CI of PR-AUC > 0.001126. If only the CI criterion fails,
  verdict is CONDITIONAL, not FAIL. The 5x rule gives 0.0056, so the 0.01 floor
  binds: effective bar is about 8.9x prevalence.
- Time features: hour_of_day allowed (tail laundering share is roughly flat across
  hours in the audit). No absolute-time features (date, day index, time since dataset
  start). No day_of_week in the pilot (train has one weekend; test_core ends on a
  Saturday). No cumulative counts since dataset start: rolling windows only (1h/24h/7d).
- Limitation: the 5 tail-only source accounts cannot be scored with any history.
- Alternatives rejected: gating on full test (affected by the tail); deleting the tail
  everywhere (loses comparability); calendar-day split (test would be mostly tail).
- Any change after this point is recorded as #6a, not by editing #6.
