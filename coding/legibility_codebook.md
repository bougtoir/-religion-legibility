# Legibility Feature Codebook (exploratory, deterministic)

Scope: DRH SCCSR v3 questions (question_name field) and Seshat Polaris Religion variables.
Coding is deterministic: each feature is a fixed regular-expression rule applied to the
question/variable text. Single-coder, rule-based implementation — labeled exploratory;
all rules and outputs are released for adjudication.

## Binary features

| feature | definition | rule (regex on question/variable name, case-insensitive) |
|---|---|---|
| `numeric_magnitude` | requires a count, magnitude, or quantitative estimate | `how many\|number of\|how much\|approximate\|percentage\|percent\|estimate the\|average` |
| `frequency_estimate` | requires a rate/frequency judgment | `how often\|frequency\|how frequently\|rate of` |
| `institutional_object` | refers to a named/bounded institution, office, text, or elite structure | `institution\|church\|temple\|priest\|clergy\|leader\|official\|government\|state\|court\|scripture\|text\|written\|doctrine\|orthodox\|monarch\|ruler` |
| `diffuse_phenomenon` | refers to non-institutional, dispersed, or folk practice/belief | `folk\|local\|household\|domestic\|family\|ancestor\|spirit\|magic\|divination\|taboo\|informal\|lay` |
| `person_level` | asks about individual persons/members rather than corporate actors | `members\|adherent\|individual\|participant\|believer\|person\|people` |
| `abstract_judgment` | requires an interpretive/normative judgment rather than observation | `moral\|norm\|belief\|believed\|ideolog\|sacred\|supernatural\|afterlife\|salvation\|ethical\|value` |
| `event_observable` | refers to a discrete, datable public event or ritual | `ritual\|ceremon\|sacrifice\|festival\|pilgrimage\|funeral\|initiation\|coronation\|rite` |

## Outcome

`unknown_share_q` = share of a question's answers that are explicit unknown answers
(DRH: "Field doesn't know"/"I don't know"/ES/FR/ZH variants). Analysis restricted to
questions with ≥50 answers.

## Model

Quasi-binomial logistic regression (statsmodels GLM, binomial family with
dispersion estimated), per question:
logit(p_q) = β0 + β·features_q, reported with effect estimates (odds ratios),
95% CIs, n questions, n answers, dispersion parameter.
