# Statistical Analysis Plan (as executed, post-revision)

## Design

Observational measurement audit + harmonized epistemic-state census + exploratory legibility model. No causal identification is claimed.

## Estimands and procedures

1. **Explicit-unknown share (Estimand 1)**: P(explicit unknown | row exists), per collection/sheet, after harmonizing token conventions across collections — UNK = {u, su, unknown, uncoded, suspected unknown}, INF = {ip, ia} inferred present/absent, RNG = {p~a, a~p} ranges. One row = one recorded (polity, variable) data point; absent rows are NOT missing data (applicability rules are undocumented, so the expected universe is not reconstructible).

2. **Coverage (descriptive only)**: rows relative to the naive polity×variable bound (`polaris_coverage_descriptive.csv`). Reported descriptively; NOT interpretable as missingness and never inferred on.

3. **No cross-collection inference**: polity-matched Wilcoxon tests were dropped — denominators (variable families, applicability, row generation) are structurally non-comparable. All cross-collection statements are descriptive.

4. **Within-instrument legibility gradient**: per-variable unknown share inside the Polaris religion collection and the Equinox religion section, where denominators are commensurable.

5. **Exploratory legibility model (H1)**: deterministic coding scheme (`coding/legibility_codebook.md`, fixed regex rules, 7 features) developed for the revised analysis and applied uniformly to all eligible questions — NOT outcome-blind or pre-registered. Quasi-binomial GLM on questions with ≥50 answers, with poll-level cluster bootstrap and wild-cluster bootstrap sensitivity.

6. **Affordance audit**: named/versioned instruments only; availability ∈ {direct, indirect, absent, NA} + unit-of-analysis column; NA = outside the instrument's unit.

## Decisions logged

- The earlier 18.6% vs 0–1.7% headline was abandoned after harmonizing token conventions.
- Seshat raw data are not republished; aggregate outputs only.
- H1 is tested; H6 partially tested; H2–H5 are theoretical propositions.
