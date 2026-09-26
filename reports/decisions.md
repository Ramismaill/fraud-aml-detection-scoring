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