# Analysis Decisions (major revision)

## Seshat denominator semantics — resolution

- **Row semantics**: one row = one recorded (polity, variable) data point in the Polaris export. No row ⇒ the combination is not identifiable as missing; the export does not document variable-applicability or row-generation rules. The naive polity×variable bound is reported descriptively only (`polaris_coverage_descriptive.csv`) and is never called missingness.
- **Estimands split**: Estimand 1 = P(explicit unknown | row exists), computed after harmonizing token conventions across collections (u/su/unknown/uncoded vs spelled-out tokens; ip/ia reported separately). Estimand 2 (coverage vs a justified expected universe) is **abandoned** — the expected universe cannot be validly reconstructed.
- **Cross-collection inference**: Wilcoxon polity-matched tests were **dropped** — denominators are structurally non-comparable (different variable families, applicability, and row-generation). Comparisons are descriptive only.
- **Discovery that changed the headline**: control collections encode epistemic states in single-letter codes; the original "18.6% vs 0–1.7%" compared only literal `unknown` tokens and was a token-convention artifact. Harmonized: Religion 19.3% unknown (Warfare 20.1%, SC 11.2%, Luxury 10.7%, General 3.1%) and 0% inferred vs 18–23% inferred in controls.

## Claims retained / weakened / abandoned

- **Retained**: within-instrument legibility gradients (Polaris religion variables 11–34%; Equinox religion section <1%–54%); DRH question-level unknown gradient, now formalized (quasi-binomial model, ORs + 95% CI); architecture-dependence conclusion.
- **Weakened**: "religion variables are more missing than controls" → "collections encode epistemic states differently; religion marks uncertainty explicitly while controls infer values."
- **Abandoned**: the 18.6% vs 0–1.7% headline; all p-values across collections; "concentration in abstract attributes" as an informal claim (now replaced by the exploratory rule-coding model result).

## Legibility coding

- Exploratory deterministic codebook (coding/legibility_codebook.md), 7 binary features, fixed regex rules, applied uniformly to all eligible questions. Developed for the revised analysis AFTER outcomes had been inspected in an earlier iteration — the "frozen/prespecified" wording was removed as inaccurate. Single-coder → exploratory; all codes released.
- Model: quasi-binomial GLM (dispersion ≈ 15.3) on questions with ≥50 answers (n=1,667). Dependence-robust check: poll-level cluster bootstrap (6 clusters, 999 reps) + wild-cluster p — point estimates unchanged, CIs widen; only numeric_magnitude (OR 11.7, boot CI 9.4–14.3, wild p=0.018) and diffuse_phenomenon (OR 2.0, 1.4–2.6, p=0.019) remain robust.

## Affordance audit

- Recoded to availability (direct/indirect/absent/NA) + unit column; NA used for unit-incompatible cells; sampling geography ≠ territorial embeddedness; named versioned instruments only. Single coder; rubric + cell evidence released.

## Hypothesis status

- H1 tested (DRH model + within-instrument gradients); H6 partially tested; H2–H5 theoretical propositions.
