\# M1 Pilot — Decision Log



Reviewed with DeepSeek (external reviewer). Project rules (handoff §4, §6, §7)

take priority over any reviewer. Thresholds below are PRE-REGISTERED and will

NOT be edited after pilot results are seen (day 7).



\## DECISION #1 — Pilot scope (2026-09-25)

\- Chosen: 8-notebook feasibility pilot; stop at INITIAL RESULTS; per-dataset

&#x20; evaluation, no unified analyst queue; K-Means/Apriori/SHAP as smoke tests only.

\- Alternatives: full 3-week MVP; BAF-only pilot.

\- Why: fair comparison with the EPIAS pilot (stopped at the same level);

&#x20; AMLworld leakage-free features are the key feasibility question.

\- Risk: day 4 (AML rolling features) is the heaviest step.

\- Mitigation (DeepSeek, accepted): hard checkpoint end of day 3 — both audits

&#x20; green (Parquet written, row counts match source, label rates in range) or

&#x20; stop and ship a 4-notebook report. Day 6 time-boxed: 3 blocks x 30 min.

\- DeepSeek view: drop K-Means/Apriori → REJECTED (Muhammet's instruction §6;

&#x20; instructor wants all techniques; TreeExplainer on \~2k rows is standard).



\## DECISION #2 — PASS / CONDITIONAL / FAIL criteria (pre-registered)

\- BAF PASS: Recall@5%FPR >= 0.40 (pre-registered guess, no citation);

&#x20; PR-AUC > 5x prevalence; leakage checks pass.

\- AML PASS: at least one of PR-AUC >= 0.01 | minority-F1 >= 0.10 |

&#x20; Recall@5%FPR >= 0.20, AND lower bound of 95% bootstrap CI (200 resamples)

&#x20; of PR-AUC > prevalence.

\- Lift@1%: reported as supporting evidence, not gating.

\- General: both baselines run end-to-end; AML features <= 1 working day;

&#x20; peak RAM < 12 GB.

\- CONDITIONAL: everything runs but one dataset needed subsampling or > 1 day,

&#x20; or one metric below threshold with an understood reason.

\- FAIL: leakage-free AML features cannot be built on this hardware, or no

&#x20; signal above prevalence.

\- Note: no published PR-AUC figures for AMLworld HI-Small with simple

&#x20; features; the AML thresholds are informed guesses, stated as such.



\## DECISION #3 — Cold-start policy for AML rolling features

\- Chosen: no rows dropped. "No history at time t" is knowable at t → not

&#x20; leakage. Add `account\_age\_hours` (time since first appearance).

\- Alternatives: drop warm-up rows (impossible: 10-day dataset, 7d window);

&#x20; expanding window (changes feature meaning over time).

\- Limitation: 7d windows are fully warm only from day 7; reported in drift-by-day.



\## DECISION #4 — Derived features under cold-start (DeepSeek, accepted)

\- Count-like features (n\_tx, n\_unique\_peers, n\_currencies): 0 when no history.

\- Aggregates (mean/std/max amount): NULL when no history (LightGBM handles NaN).

\- Ratios (pass-through, amt/mean): NULL when denominator is 0.

\- No companion has\_history flag (redundant with count == 0).

\- Check: fraction of NULL aggregates per day must decrease over the train

&#x20; period (computed in 05, reported in 08).

\- Open: IF/COPOD do not accept NaN → imputation rule decided in 06.



\## Metrics (both datasets)

PR-AUC, Recall@5%FPR, Precision@100, Lift@1% (supporting); AML also

minority-class F1 (comparable to the AMLworld paper); BAF also FPR ratio by

customer\_age >= 50 (predictive equality).



\## Why the two datasets are never joined

BAF and AMLworld share no customers, banks or time axis, and their labels

mean different things (fraudulent application vs laundering transfer).

Cross-dataset transfer is out of scope for this pilot.

