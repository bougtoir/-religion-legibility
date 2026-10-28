"""Legibility coding + quasi-binomial model for DRH questions and Seshat religion variables.

Frozen rules in coding/legibility_codebook.md are applied deterministically.
Outputs:
  data/processed/drh_legibility_codes.csv     per-question features + unknown share
  data/processed/seshat_legibility_codes.csv  per-variable features + unknown share
  data/processed/legibility_model_drh.csv     GLM coefficients (OR, 95% CI, p)
"""
import os, re
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "data/processed")

RULES = {
    "numeric_magnitude": r"how many|number of|how much|approximate|percentage|percent|estimate the|average",
    "frequency_estimate": r"how often|frequency|how frequently|rate of",
    "institutional_object": r"institution|church|temple|priest|clergy|leader|official|government|state|court|scripture|text|written|doctrine|orthodox|monarch|ruler",
    "diffuse_phenomenon": r"folk|local|household|domestic|family|ancestor|spirit|magic|divination|taboo|informal|lay",
    "person_level": r"members|adherent|individual|participant|believer|person|people",
    "abstract_judgment": r"moral|norm|belief|believed|ideolog|sacred|supernatural|afterlife|salvation|ethical|value",
    "event_observable": r"ritual|ceremon|sacrifice|festival|pilgrimage|funeral|initiation|coronation|rite",
}
COMP = {k: re.compile(v, re.I) for k, v in RULES.items()}

def code(text):
    return {k: int(bool(rx.search(str(text)))) for k, rx in COMP.items()}

ans = pd.read_csv(os.path.join(ROOT, "data/raw/drh/drh_tables/answerset.csv"), low_memory=False)
UNK_ANS = {"field doesn't know", "i don't know", "el campo lo desconoce", "je ne sais pas", "我不知道"}
ans["is_unknown"] = ans["answer"].astype(str).str.strip().str.lower().isin(UNK_ANS)

q = ans.groupby(["question_id", "question_name", "poll_name"]).agg(
    n_answers=("is_unknown", "size"), n_unknown=("is_unknown", "sum")).reset_index()
q["unknown_share"] = q.n_unknown / q.n_answers
feats = q["question_name"].apply(code).apply(pd.Series)
q = pd.concat([q, feats], axis=1)
q_model = q[q.n_answers >= 50].copy()
q.to_csv(os.path.join(OUT, "drh_legibility_codes.csv"), index=False)

X = sm.add_constant(q_model[list(RULES)].astype(float))
y = np.column_stack([q_model.n_unknown, q_model.n_answers - q_model.n_unknown])
m = sm.GLM(y, X, family=sm.families.Binomial()).fit(scale="X2")
ci = m.conf_int()
res = pd.DataFrame({
    "feature": m.params.index,
    "beta": m.params.values,
    "odds_ratio": np.exp(m.params.values),
    "or_lo": np.exp(ci[0].values),
    "or_hi": np.exp(ci[1].values),
    "se": m.bse.values,
    "p": m.pvalues.values,
    "n_questions": len(q_model),
    "n_answers": int(q_model.n_answers.sum()),
    "dispersion": m.pearson_chi2 / m.df_resid,
})
res.to_csv(os.path.join(OUT, "legibility_model_drh.csv"), index=False)
print(res.to_string(index=False))
print("\nDRH mean unknown share by feature presence:")
for f_ in RULES:
    a = q_model[q_model[f_] == 1].unknown_share.mean()
    b = q_model[q_model[f_] == 0].unknown_share.mean()
    print(f"  {f_}: {a:.3f} (n={int((q_model[f_]==1).sum())}) vs {b:.3f} (n={int((q_model[f_]==0).sum())})")

rel = pd.read_excel(os.path.join(ROOT, "data/raw/polaris/build_polaris_dataset/Polaris2026.xlsx"), sheet_name="Religion")
UNK = {"u", "su", "unknown", "uncoded", "suspected unknown"}
rel["is_unknown"] = rel["value_from"].astype(str).str.lower().str.strip().isin(UNK)
sv = rel.groupby("variable_name").agg(n=("is_unknown", "size"), n_unknown=("is_unknown", "sum")).reset_index()
sv["unknown_share"] = sv.n_unknown / sv.n
svf = sv["variable_name"].str.replace("_", " ").apply(code).apply(pd.Series)
sv = pd.concat([sv, svf], axis=1)
sv.to_csv(os.path.join(OUT, "seshat_legibility_codes.csv"), index=False)
print("\nSeshat religion variables:")
print(sv[["variable_name", "n", "unknown_share"] + list(RULES)].to_string(index=False))

rng = np.random.default_rng(20261003)
clusters = q_model.poll_name.unique()
B = 999
FEAT = list(RULES)

def fit(sub):
    Xs = sm.add_constant(sub[FEAT].astype(float))
    ys = np.column_stack([sub.n_unknown, sub.n_answers - sub.n_unknown])
    return sm.GLM(ys, Xs, family=sm.families.Binomial()).fit(scale="X2").params.values

boot = []
for _ in range(B):
    draw = rng.choice(clusters, size=len(clusters), replace=True)
    sub = pd.concat([q_model[q_model.poll_name == c] for c in draw], ignore_index=True)
    try:
        boot.append(fit(sub))
    except Exception:
        continue
boot = np.asarray(boot)
beta_hat = m.params.values
lo = np.nanpercentile(boot, 2.5, axis=0)
hi = np.nanpercentile(boot, 97.5, axis=0)

pvals = {}
t_obs = m.params.values / m.bse.values
for k, f in enumerate(m.params.index):
    if f == "const":
        continue
    fi = list(m.params.index).index(f)
    Xr = X.copy()
    Xr[f] = 0.0
    mr = sm.GLM(y, Xr, family=sm.families.Binomial()).fit(scale="X2")
    resid = q_model.n_unknown / q_model.n_answers - mr.fittedvalues
    tstat = []
    for _ in range(B):
        w = {c: rng.choice([-1.0, 1.0]) for c in clusters}
        yw = mr.fittedvalues + np.array([w[c] for c in q_model.poll_name]) * resid
        ywc = np.clip(yw, 0, 1)
        y_b = np.column_stack([np.round(ywc * q_model.n_answers).astype(int),
                               q_model.n_answers - np.round(ywc * q_model.n_answers).astype(int)])
        try:
            mb = sm.GLM(y_b, X, family=sm.families.Binomial()).fit(scale="X2")
            tstat.append(mb.params.values[fi] / mb.bse.values[fi])
        except Exception:
            continue
    tstat = np.asarray(tstat)
    pvals[f] = float(np.mean(np.abs(tstat) >= abs(t_obs[fi])))

sens = pd.DataFrame({
    "feature": m.params.index,
    "beta": beta_hat,
    "odds_ratio": np.exp(beta_hat),
    "qb_or_lo": np.exp(ci[0].values),
    "qb_or_hi": np.exp(ci[1].values),
    "boot_beta_lo": lo,
    "boot_beta_hi": hi,
    "boot_or_lo": np.exp(lo),
    "boot_or_hi": np.exp(hi),
    "qb_p": m.pvalues.values,
    "wild_boot_p": [pvals.get(f, np.nan) for f in m.params.index],
    "n_clusters": len(clusters),
    "n_boot": len(boot),
})
sens.to_csv(os.path.join(OUT, "legibility_model_drh_bootstrap.csv"), index=False)
print("\nCluster-robust sensitivity (poll-level bootstrap, %d clusters, %d reps):" % (len(clusters), len(boot)))
print(sens.to_string(index=False))
