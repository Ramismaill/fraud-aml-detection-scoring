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