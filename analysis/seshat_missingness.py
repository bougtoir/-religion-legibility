"""Seshat epistemic-state census (Polaris 2026 + Equinox 2020).

REVISED after denominator-semantics review:
- A row = one recorded (polity, variable) data point; absent polity-variable
  combinations are NOT identifiable as missing without applicability rules,
  which are not documented in the export. Coverage estimand is therefore
  reported descriptively only and never as "missingness".
- Epistemic states are harmonized across token conventions:
    unknown tokens: u, su, unknown, uncoded, suspected unknown
    inferred tokens: ip, ia (inferred present/absent)
    range tokens: p~a, a~p (bounded presence/absence uncertainty)
  Religion spells its tokens out; control collections use single-letter codes.
  Comparing only literal 'unknown' tokens conflates encoding conventions
  with epistemic state -- avoided here.
- No cross-collection inferential test: denominators (variable applicability,
  row-generation rules) differ structurally. Descriptive comparison only.

Outputs (data/processed/):
  polaris_epistemic_census.csv      per-collection state shares
  polaris_variable_epistemic.csv    per-variable census inside Religion
  polaris_coverage_descriptive.csv  rows vs naive polity x variable bound
  equinox_section_missingness.csv   Equinox canon per-section census
  equinox_variable_missingness.csv  Equinox religion-section variables
  seshat_summary.csv                headline numbers for the manuscript
"""
import os
import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..")
POL = os.path.join(ROOT, "data/raw/polaris/build_polaris_dataset/Polaris2026.xlsx")
EQX = os.path.join(ROOT, "data/raw/seshat/equinox/seshatdb-Equinox_Data-ed8f570/Equinox_on_GitHub_June9_2022.xlsx")
OUT = os.path.join(ROOT, "data/processed")
os.makedirs(OUT, exist_ok=True)

UNK = {"u", "su", "unknown", "uncoded", "suspected unknown"}
INF = {"ip", "ia"}
RNG = {"p~a", "a~p"}

def census(df):
    v = df["value_from"].astype(str).str.lower().str.strip()
    n = len(df)
    return {
        "rows": n,
        "polities": df["polity_id"].nunique() if "polity_id" in df else 0,
        "variables": df["variable_name"].nunique() if "variable_name" in df else 1,
        "n_unknown": int(v.isin(UNK).sum()),
        "pct_unknown": round(100 * v.isin(UNK).mean(), 1),
        "n_inferred": int(v.isin(INF).sum()),
        "pct_inferred": round(100 * v.isin(INF).mean(), 1),
        "n_range": int(v.isin(RNG).sum()),
        "pct_range": round(100 * v.isin(RNG).mean(), 1),
        "n_blank_value": int(v.isin({"nan", "none", ""}).sum() | df["value_from"].isna().sum()),
        "pct_uncertain_flag": round(100 * df["is_uncertain"].mean(), 1),
        "pct_disputed_flag": round(100 * df["is_disputed"].mean(), 1),
    }

sheets = ["General", "Social complexity", "Warfare", "Luxury goods", "Religion"]
rows = []
frames = {}
for sh in sheets:
    df = pd.read_excel(POL, sheet_name=sh)
    frames[sh] = df
    r = census(df)
    r["collection"] = sh
    rows.append(r)
cen = pd.DataFrame(rows)[["collection"] + [c for c in rows[0] if c != "collection"]]
cen.to_csv(os.path.join(OUT, "polaris_epistemic_census.csv"), index=False)

cov = []
for sh in sheets:
    df = frames[sh]
    nv, np_ = df.variable_name.nunique(), df.polity_id.nunique()
    cov.append({"collection": sh, "rows": len(df), "polities": np_,
                "variables": nv, "naive_universe": nv * np_,
                "share_of_naive_bound": round(len(df) / (nv * np_), 3)})
pd.DataFrame(cov).to_csv(os.path.join(OUT, "polaris_coverage_descriptive.csv"), index=False)

rel = frames["Religion"]
pv = rel.groupby("variable_name").apply(
    lambda g: pd.Series(census(g)), include_groups=False).reset_index()
pv = pv.sort_values("pct_unknown", ascending=False)
pv.to_csv(os.path.join(OUT, "polaris_variable_epistemic.csv"), index=False)

eq = pd.read_excel(EQX, sheet_name="Equinox2020_CanonDat")
cols = {c.lower().replace(".", "_"): c for c in eq.columns}
sec_col = cols.get("section") or cols.get("category")
val_col = cols.get("value_from") or cols.get("value")
var_col = cols.get("variable_name") or cols.get("variable")
assert sec_col and val_col and var_col, f"Equinox column detection failed: {list(eq.columns)}"

def eq_state(series):
    v = series.astype(str).str.lower().str.strip()
    return {"n_unknown": int(v.isin(UNK).sum()), "pct_unknown": round(100 * v.isin(UNK).mean(), 1),
            "n_inferred": int(v.isin(INF).sum()), "pct_inferred": round(100 * v.isin(INF).mean(), 1)}

es = eq.groupby(eq[sec_col]).apply(lambda g: pd.Series({"rows": len(g), **eq_state(g[val_col])}), include_groups=False).reset_index()
es.rename(columns={sec_col: "section"}, inplace=True)
es.to_csv(os.path.join(OUT, "equinox_section_missingness.csv"), index=False)

rel_sec = es.loc[es.section.astype(str).str.contains("relig", case=False), "section"].iloc[0]
ev = eq[eq[sec_col] == rel_sec].groupby(eq[var_col]).apply(
    lambda g: pd.Series({"rows": len(g), **eq_state(g[val_col])}), include_groups=False).reset_index()
ev.rename(columns={var_col: "variable"}, inplace=True)
ev.sort_values("pct_unknown", ascending=False).to_csv(
    os.path.join(OUT, "equinox_variable_missingness.csv"), index=False)

s = pd.DataFrame([
    {"metric": "polaris_religion_pct_unknown", "value": float(cen.loc[cen.collection == "Religion", "pct_unknown"].iloc[0])},
    {"metric": "polaris_warfare_pct_unknown", "value": float(cen.loc[cen.collection == "Warfare", "pct_unknown"].iloc[0])},
    {"metric": "polaris_socialcomplexity_pct_unknown", "value": float(cen.loc[cen.collection == "Social complexity", "pct_unknown"].iloc[0])},
    {"metric": "polaris_luxury_pct_unknown", "value": float(cen.loc[cen.collection == "Luxury goods", "pct_unknown"].iloc[0])},
    {"metric": "polaris_general_pct_unknown", "value": float(cen.loc[cen.collection == "General", "pct_unknown"].iloc[0])},
    {"metric": "polaris_religion_pct_inferred", "value": float(cen.loc[cen.collection == "Religion", "pct_inferred"].iloc[0])},
    {"metric": "polaris_warfare_pct_inferred", "value": float(cen.loc[cen.collection == "Warfare", "pct_inferred"].iloc[0])},
    {"metric": "polaris_socialcomplexity_pct_inferred", "value": float(cen.loc[cen.collection == "Social complexity", "pct_inferred"].iloc[0])},
    {"metric": "polaris_luxury_pct_inferred", "value": float(cen.loc[cen.collection == "Luxury goods", "pct_inferred"].iloc[0])},
    {"metric": "equinox_n_regions", "value": int(eq["NGA"].nunique())},
    {"metric": "equinox_total_values", "value": int(es.rows.sum())},
    {"metric": "equinox_n_polities", "value": int(eq["Polity"].nunique())},
])
s.to_csv(os.path.join(OUT, "seshat_summary.csv"), index=False)
print(cen.to_string(index=False))
print("\nReligion variables:")
print(pv[["variable_name", "rows", "pct_unknown", "pct_inferred"]].to_string(index=False))
