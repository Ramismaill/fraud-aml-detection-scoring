Day 2 notes:

\- Negative-valued columns confirmed: five community-listed columns use -1 only; credit\_risk\_score and velocity\_6h have real negative values.

\- velocity\_\* features are precomputed by the dataset generator; past-only cannot be verified from the file and is assumed from dataset design. Documented as a limitation.

\- Label-distribution shift: prevalence rises from 0.998% (train) to 1.404% (test).

\- Missing-code signal is column-specific: 3 columns higher fraud when negative, 2 lower, 1 null. All 6 flags will be created in 04.

\- Temporal variation in missing-code prevalence assessed as a feature-distribution shift indicator; bank\_months\_count is lower in month 0 only.

