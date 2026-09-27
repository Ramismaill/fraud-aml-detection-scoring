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


## DECISION #7 — Two separate analyst queues, one common framework (Muhammet, 2026-09-27)
- No single combined queue. Output = BAF Analyst Queue (account-opening fraud)
  + AML Analyst Queue (transaction monitoring): different operational processes.
- Common to both: risk ranking, risk bands, SHAP explanation cards, same evaluation logic.
- Different unit of analysis: BAF ranks account-opening applications; AML ranks
  transactions. Risk bands therefore carry different operational meaning in each
  queue; thresholds are set per dataset (base rates differ ~10x).
- No joint model: label semantics, feature space and time axis differ; cross-dataset
  transfer is out of scope.
- SHAP shows the model's attribution for a prediction, not the real-world cause;
  with correlated features, credit can shift between them, so top features are
  read as a group.
- Replaces the single-queue diagram in the handoff (section 6).
- Presentation flow (compress to 5-6 slides): volume -> manual review impossible ->
  risk ranking -> rare events -> accuracy misleading -> data changes over time ->
  chronological split -> leakage prevention -> success criteria fixed before results
  -> BAF and AML evaluated independently -> separate ranked queues -> risk bands +
  SHAP -> PASS / CONDITIONAL / FAIL.


## DECISION #8 — BAF baseline: features, model, procedure (2026-09-27, before any training)
- Order: (1) DECISION #5 A/B/C compared on validation (month 5); (2) the winner's model
  from that round is the final model, no retraining (deterministic, same seed);
  (3) test (months 6-7) evaluated once. Month 5 serves both early stopping and the
  A/B/C choice: one validation split, not independent confirmation.
- Features: all raw columns except fraud_bool and month (month = absolute time index):
  29 raw. 5 categorical columns (identified in 02_audit_baf) as native LightGBM
  category. Flags <col>_is_missing (v < 0) for the 5 columns coded with -1, in every
  variant. credit_risk_score and velocity_6h have real negatives: kept raw, no flag.
  intended_balcon_amount: A = raw (34 features); B = raw + flag (35);
  C = NaN when v < 0 + flag (35). No engineered features in the baseline.
- Model: lightgbm.train (native API), LightGBM 4.7.0, objective=binary,
  learning_rate=0.05, num_leaves=63, min_child_samples=100, feature_fraction=0.8,
  bagging_fraction=0.8, bagging_freq=1, up to 2000 rounds, early stopping 100 rounds
  on validation average_precision; best_iteration reported.
- Imbalance: no class weighting. BAF paper settings are not replicated or claimed.
- Reproducibility: seed=42, deterministic=True, force_col_wise=True, num_threads=8.
- Early-stopping metric = LightGBM average_precision; reported PR-AUC = sklearn
  average_precision_score (small differences possible, reported if > 1e-3).
- Reported on test: src.metrics.summary (PR-AUC, Recall@5%FPR, Precision@100/500,
  Lift@1%) and the FPR ratio customer_age >= 50 vs < 50 at the 5%-FPR threshold
  chosen on validation (group cut-off 50 from the handoff, section 5.1). Report only.


### DECISION #5 — outcome (2026-09-27)
- Validation PR-AUC: A 0.1852, B 0.1831, C 0.1878; all within the 5% margin -> A kept
  by the pre-registered simplicity rule.
- The recorded prediction (A ~ B > C) was not confirmed: C scored nominally highest.
  Null result: the representation of intended_balcon_amount has no measurable effect
  on the tree model at this sample size.


## DECISION #9 — AML baseline: past-only features and model (2026-09-27, before any AML feature code)
Unit = one transaction t (src, dst, ts). Split and test_core as in #6. Every row is
scored (self-loops and tail included); gating uses test_core only.
1. Past-only: every aggregate for t uses only transactions with ts < t.ts (strictly
   earlier minute); same-minute rows and t itself are excluded. History may cross
   split boundaries backwards only.
2. Amounts: u_c = USD value of one unit of currency c, u_USD = 1. From TRAIN-period
   cross-currency transfers, median(amt_received / amt_paid) per (pay_ccy, recv_ccy)
   pair = u_pay / u_recv; log u_c solved by least squares over all pairs (covers
   currencies without a direct USD pair). amt_usd = amt_paid * u_pay_ccy, used for all
   sums. Fixed train-only rates ignore any real exchange-rate drift over time
   (limitation). If a currency is not connected to USD: no conversion; use
   log(amt_paid) + pay_ccy instead, recorded as #9a.
3. Self-loops (src = dst): kept, scored, flagged is_self_loop; excluded from every
   account and pair aggregate.
4. Features (exactly 33, asserted in code):
   Sender src, windows 1h/24h/7d: out_cnt, out_sum_usd, in_cnt, in_sum_usd (12).
   Sender 24h: n_unique_dst_out, n_unique_src_in, pass_through_24h = out_sum/in_sum
   (NULL if in_sum = 0); mins_since_last_in (4).
   Receiver dst, windows 1h/24h/7d: in_cnt, in_sum_usd (6). Receiver 24h:
   n_unique_src_in, out_cnt_24h (2).
   Pair: pair_cnt_7d = earlier transfers src -> dst (directional) (1).
   Ages: src_age_hours, dst_age_hours = t.ts - MIN(ts) over rows with ts < t.ts where
   the account appears as src OR dst (2).
   Transaction: log_amount_usd, pay_format (cat), pay_ccy (cat), is_cross_ccy,
   hour_of_day (integer), is_self_loop (6).
   The 7d window is effectively expanding inside the 5.6-day train period.
5. Cold start: counts = 0; sums, ratios, mins_since_last_in, ages = NULL.
6. Forbidden: is_laundering in any feature; from_bank, to_bank, account IDs; ts, date,
   day index, day_of_week, time since dataset start; Patterns.txt; accounts.csv;
   whole-period graph measures (degree, PageRank, communities) - the most common AML
   leakage source, because they use future edges by construction.
7. Order: FX rates (train only) -> event table without self-loops -> windowed
   aggregates -> join back to transactions -> cold-start fill -> assert 33 features
   -> split by #6 timestamps.
8. Leakage checks: (a) 20 random rows recomputed in pandas from strictly earlier rows:
   values AND the number of rows used must equal DuckDB (counts); (b) label-permutation
   test; (c) rows at the first dataset minute have all counts = 0.
9. Model: LightGBM settings of #8, no class weighting; train split only; early
   stopping on validation average_precision. F1 threshold = F1 maximiser on
   VALIDATION, applied unchanged to test_core; no threshold is chosen on test.
10. Evaluation once. Gating on test_core per #2b/#6: PR-AUC >= 0.01 AND
    (Recall@5%FPR >= 0.20 OR F1 >= 0.10) AND hourly block-bootstrap 95% CI lower
    bound of PR-AUC > 0.001126 (= 1,143 / 1,014,774), 200 resamples. Full test reported.
11. Limitation: history depth grows over time; early train rows have shallower history
    than validation/test rows. A property of chronological data, not leakage.
12. Reproducibility: DuckDB and LightGBM versions written to results_aml_baseline.json.
    Time-box (#2): feature building > 1 working day -> CONDITIONAL.


## DECISION #9a — Amendments to #9 (2026-09-27, before any AML feature code)
- Naming (Muhammet): mins_since_last_in -> mins_since_last_inflow;
  src_age_hours / dst_age_hours -> src_observed_age_hours / dst_observed_age_hours
  (time since first OBSERVED transaction; real account opening dates are unknown).
- Naming (DeepSeek review): the duplicate name n_unique_src_in is resolved to
  src_n_senders_in_24h (Sender side) and dst_n_senders_in_24h (Receiver side).
  Feature count unchanged (33 base + 1 added below = 34).
- Added feature (Muhammet): amt_over_inflow_24h = amt_usd of t / src in_sum_usd over
  the past 24h (NULL if in_sum = 0). Uses only information known at t. Count: 34.
- Window definition: a W-window for t covers ts in [t.ts - W, t.ts) at minute resolution.
- FX stability (Muhammet): rates estimated on day 1 (2022-09-01) are compared with
  rates from the whole train period; if any currency differs by more than 1%, the
  #9 fallback (log(amt_paid) + pay_ccy, no cross-currency sums) is used.
- Edge-case leakage tests: first transaction of an account, same-minute transfers,
  a transfer exactly W before t, self-loop, high-activity account.
- Diagnostic (report only): ablation model without pay_format (ACH carries 4,483 of
  5,177 laundering). Large drop -> model relies mostly on a generator rule; reported
  as a limitation, does not change the PASS rule.
- Diagnostic (report only): 4-hour moving-block bootstrap CI next to the pre-registered
  1-hour CI; number of test_core hours with laundering and share of the busiest hour.
- Framing: Recall@5%FPR = benchmark comparison metric; Precision@K = operational metric.
- For 06: RobustScaler and any imputation are fit on train only.


## DECISION #9b — mins_since_last_inflow is all-time, not 24h-capped (2026-09-27, before Cell 4b)
- #9 point 4 lists mins_since_last_inflow under the Sender 24h block, but it carries
  no _24h suffix; semantics: minutes since the most recent prior inflow (dst = account),
  at any time before t.ts, not capped to 24h.
- Reason: capping removes information the tree can use directly (it can split on any
  threshold, e.g. <=60, <=1440); the AML-relevant recency window is learned, not imposed.
  pass_through_24h and amt_over_inflow_24h remain windowed (they are ratios against
  24h sums, not raw recency).
- NULL if the account has no prior inflow (cold start).
- Implementation: MAX(prev_ts) over rows where dst = account AND prev_ts <= t.ts - 1 minute
  (same-minute and self-loop inflows excluded, consistent with #9's same-minute rule).
- Distribution note: early-train rows are bounded by dataset start (not full history);
  this is the expanding-window limitation already noted in #9 point 11, not leakage.


## DECISION #9c — fan-out/fan-in 24h redefined as new-counterparty count, not true distinct (2026-09-27, after OOM on self-join)
- Original #9 point 4: n_unique_dst_out (fan-out), n_unique_src_in (fan-in) as
  COUNT(DISTINCT counterparty) over 24h.
- Problem: a self-join within the 24h window to compute COUNT(DISTINCT) cross-multiplies
  matched outflow rows by matched inflow rows per t (double LEFT JOIN), producing fan-out
  proportional to activity^2 for high-activity accounts; this exhausted 18.6GB DuckDB temp
  space (OutOfMemoryException) after ~17 minutes.
- A correlated-subquery alternative was cost-estimated at ~3 hours (5M rows x 2 subqueries
  x ~1ms each even with indexes), exceeding the #9 point 10 time-box.
- Decision: redefine n_unique_dst_out_24h -> new_counterparty_out_24h, and
  src_n_senders_in_24h -> new_counterparty_in_24h. Computed via LAG() per (src,dst) pair:
  a transaction counts as "new" if its (src,dst) pair had no prior transaction, or its
  prior transaction was more than 24h before t.ts. Feature = count of such "new" pairs
  for the account within [t.ts-24h, t.ts).
- This is not identical to true distinct-counterparty-count (it does not decrement when
  a previously-new pair ages out of the window in the same way; it counts newly-appearing
  pairs, not currently-distinct pairs in-window). It is a standard AML signal in its own
  right ("new counterparty rate") and is computable via a single windowed LAG, no self-join.
- Renamed feature names logged here supersede #9 point 4's n_unique_dst_out / n_unique_src_in.


## DECISION #9d — receiver naming, receiver new-counterparty, cold-start sums, FX estimator (2026-09-27, before Cell 4c)
1. Naming: receiver (dst-side) features carry a dst_ prefix; sender features keep the
   #9/#9a/#9c names. Receiver names: dst_in_cnt_1h/24h/7d, dst_in_sum_usd_1h/24h/7d,
   dst_out_cnt_24h, dst_new_counterparty_in_24h (8).
2. Receiver fan-in follows #9c: dst_n_senders_in_24h (#9a) -> dst_new_counterparty_in_24h
   = number of transfers into dst within [t.ts-24h, t.ts) whose (src,dst) pair had no
   earlier transfer, or whose previous transfer was more than 24h earlier. Same
   single-LAG pair table as Cell 4b-2 (tie-break by id).
3. Column mapping for Cell 4b-2 output, applied when features are assembled (4f):
   n_new_dst_24h -> new_counterparty_out_24h; n_new_senders_in_24h ->
   new_counterparty_in_24h. Definitions unchanged.
4. Cold start (#3/#4, #9 point 5): a windowed sum is NULL when the account has no
   earlier non-self-loop event in that direction at all (no history); it is 0 when
   history exists but the window is empty. The distinction applies to sums only;
   counts are 0 in both cases. Receiver sums: implemented in 4c by ASOF NULL
   propagation (no earlier row in cum_in -> NULL). Sender sums: Cell 4a writes 0, so
   4a and 4c are inconsistent until 4f. In 4f the "no history" flag for sender sums is
   recomputed with the same ASOF-no-match logic against cum_out / cum_in; it is NOT
   inferred from sender_features values (a 0 there cannot distinguish the two cases).
5. FX estimator: Cell 2 fitted least squares on log(amt_received/amt_paid) of every
   train cross-currency row, not on per-pair medians as #9 point 2 states. Rule fixed
   before the check: rates from per-pair medians are computed; if every currency
   differs by < 1% from the fitted rates (same threshold as the #9a day-1 check), the
   fitted rates are kept and the measured divergence is logged in pilot_log.md (this
   decision text is not edited afterwards). Otherwise stop and review before any
   further feature code. Switching estimators would require re-running Cells 2, 4a,
   4b-1, 4b-2 and all their checks.
6. Final naming at assembly (Cell 4f): sender features gain a src_ prefix; receiver
   features keep dst_. Applied via SELECT aliases in 4f together with the point-3
   mapping; Cells 4a/4b-1/4b-2 are not re-run.
7. dst_out_cnt_24h is the receiver's own outbound activity (dst acting as sender of
   other transfers), a deliberate mixed-perspective feature from #9 point 4.
8. Verification note: the Cell 4b-2 brute-force ordered "previous pair event" by ts
   only, while the LAG orders by (ts, id). The 5 sample rows did not hit a same-minute
   repeat of a pair, so it passed; the feature is correct, the check was weaker than
   the code. The 4c and 4f brute-force checks order by (ts, id), matching the reference.


## DECISION #9e — Sender-side cold-start NULL fix implemented at assembly (2026-09-27)
#9d point 4 promised that sender-side sums would be normalized from 0 (Cell 4a's 
COALESCE encoding) to NULL at assembly, when the account has no prior history at all 
in the relevant direction. The first 4f attempt joined sender_features as-is and did 
not implement this.
Detection: a cross-side diagnostic compared null fraction per day for the same 
semantic field (in_sum_usd_24h) on sender vs receiver side. Sender showed 0.0% NULL 
on every day; receiver declined from 56.1% (day 1) to <1% (day 6). The asymmetry 
exposed the missing fix -- neither side's own invariants would have caught this.
Fix (at assembly, Cell 4f): an ASOF-based mask over cum_out and cum_in, joined at 
t.upper_x with no lower bound. If no match, the account has no prior history at all 
in that direction, and the corresponding sum columns become NULL.
Affected features (8):
  out_sum_usd_{1h,24h,7d} (3)
  in_sum_usd_{1h,24h,7d} (3)
  pass_through_24h (1)
  amt_over_inflow_24h (1)
Counts (out_cnt_*, in_cnt_*) remain 0 in both cases; that is correct and unchanged.
The first aml_features.parquet (saved before this fix) is invalid for training and 
must be regenerated.
Not a policy change: implements #9d point 4 as registered. Documented separately 
because the assembled table changes and the corrected parquet must be the one used 
for training.


## DECISION #9f — New-counterparty definition, same-minute eligibility, self-loop age (2026-09-27, before AML training)
1. New-counterparty definition changed from #9c's "no prior OR gap > 24h" to
   "first occurrence ever" (standard AML definition, per Muhammet's review).
   Verified impact (Task 2): on the full non-self-loop pair-event set (4,487,133 rows),
   old definition flagged 1,613,573 (35.96%) as new; new definition flags 647,939
   (14.44%). Difference: 965,634 rows / 21.52 percentage points -- material.
   Implementation: ROW_NUMBER() OVER (PARTITION BY src, dst ORDER BY ts, id) = 1.
   Verified (Task 1b) on controlled test (A->X, A->Y, A->X): row 3 (second A->X)
   yields rn=2, is_first=False. Partition mechanics apply to ROW_NUMBER as expected.
   Feature names updated:
     n_new_dst_24h        -> n_first_seen_dst_24h
     n_new_senders_in_24h -> n_first_seen_senders_in_24h
     dst_new_counterparty_in_24h -> dst_first_seen_in_24h
     sender_new_counterparty_24h (table) -> sender_first_seen_24h
2. Same-minute eligibility: strict ts < t.ts. No same-minute row is history for
   another. The ROW_NUMBER=1 implementation marks exactly one row per (src, dst)
   partition as "first ever". id serves only as a deterministic tiebreak for which
   row carries the "first" label; it does not grant chronological visibility.
3. Self-loops in observed_age (Muhammet's request): self-loops remain excluded from
   all transaction/flow aggregates (#9 point 3, unchanged). They ARE counted toward
   first-seen timestamp for src_observed_age_hours / dst_observed_age_hours.
   Verified defect in current 4d (Task 3): account 01729_80066E7B0's first dataset
   appearance is a self-loop at 2022-09-01 00:02:00; its first non-self outbound is
   5 days later (2022-09-06 03:21:00). Cell 4d's stored src_observed_age_hours is
   NULL for all rows until the first non-self event, i.e. self-loops are excluded
   from first-seen. This must be corrected: 4d will be re-run with self-loop-
   inclusive first-seen. Name stays observed_age.
4. FX train-only confirmed: Cell 2's fx_train query filters ts < TRAIN_CUTOFF;
   the day-1-vs-full-train stability check also used train-period data only. No
   validation/test data entered FX rate estimation.
5. Rebuild plan (execution order): Cell 4b-2 (ROW_NUMBER, renamed table + columns),
   Cell 4d (self-loop-inclusive first-seen), Cell 4c (rebuild receiver_features
   against new cum_in_new), Cell 4f (assembly with sender NULL mask per #9e + new
   names). The previously saved aml_features.parquet is invalid and must be
   regenerated after rebuild.


### DECISION #9f — addendum (2026-09-27, after Muhammet's clarification)
Clarification captured explicitly:
- pair_seen_before_t (per transaction): strict past_ts < current_ts. Same-minute rows are
  never history for each other, regardless of id order. NOT currently exposed as a boolean
  feature in the 34-feature set.
- pair_first_seen_timestamp (per pair): MIN(ts), one event per (src, dst). Used for all
  aggregate n_first_seen_* features. Implementation: ROW_NUMBER=1 picks exactly one row
  per pair (tie broken by id, only for row selection); cumulative counts use
  upper_x = ts - 1 minute, so no transaction sees same-minute siblings.
Empirically verified: on a same-minute duplicate pair (n=2+), only one row carries
is_first_seen=TRUE; the aggregate n_first_seen_dst_24h for a later transaction matches
the brute-force MIN(ts)-per-pair count exactly. If a per-transaction boolean
"is_this_pair_new_to_me" is added in a future iteration, it must use strict ts < t and
would diverge from ROW_NUMBER=1 for same-minute duplicates -- this is documented here
so the two concepts do not get conflated.
