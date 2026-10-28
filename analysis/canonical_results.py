"""Canonical numerical-results registry for the manuscript package.

Single source of truth for every analysis-derived number used in the
manuscript, abstract, figure/table captions, cover letter, and QC docs.
Reads data/processed/*.csv (pipeline outputs) and coding/affordance_audit.csv;
writes data/processed/canonical_results.json.

Also renders the manuscript and cover letter from templates:
  manuscript/templates/manuscript_template.md   -> manuscript/manuscript.md
  manuscript/templates/cover_letter_template.md -> manuscript/cover_letter.md
Tokens are written {{key}} and resolve to the registry's display string.

Display formatting policy (applied here only):
  pcts    -> one decimal, no trailing .0  ("19.3", "34")
  ints    -> thousands comma ("1,667")
  ors     -> two decimals trimmed ("11.7", "2.0", "0.88")
  ranges  -> "lo-hi" with en dash ("9.4-14.3" uses figure dash '–')
"""
import csv
import json
import os
import re
import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), "..")
PROC = os.path.join(ROOT, "data", "processed")
COD = os.path.join(ROOT, "coding")
TPL = os.path.join(ROOT, "manuscript", "templates")
OUT_JSON = os.path.join(PROC, "canonical_results.json")

def pct(x, dp=1):
    return f"{x:.{dp}f}"

def pctr(x):
    return str(int(round(x)))

def nint(x):
    return f"{int(x):,}"

def orr(x):
    return f"{x:.1f}".rstrip("0").rstrip(".") if x >= 10 else f"{x:.2f}".rstrip("0").rstrip(".")

R = {}
def reg(key, value, display, source):
    R[key] = {"value": value, "display": display, "source": source}

cen = pd.read_csv(os.path.join(PROC, "polaris_epistemic_census.csv")).set_index("collection")
src = "data/processed/polaris_epistemic_census.csv <- analysis/seshat_missingness.py"
for coll, key in [("Religion", "religion"), ("Warfare", "warfare"),
                  ("Social complexity", "soccomp"), ("Luxury goods", "luxury"),
                  ("General", "general")]:
    reg(f"polaris_{key}_pct_unknown", float(cen.loc[coll, "pct_unknown"]),
        pct(cen.loc[coll, "pct_unknown"]), src)
    reg(f"polaris_{key}_pct_inferred", float(cen.loc[coll, "pct_inferred"]),
        pct(cen.loc[coll, "pct_inferred"]), src)

controls = ["Warfare", "Social complexity", "Luxury goods", "General"]
ctrl_unk = [float(cen.loc[c, "pct_unknown"]) for c in ["Social complexity", "Luxury goods", "General"]]
reg("polaris_controls_unknown_range", [min(ctrl_unk), max(ctrl_unk)],
    f"{pctr(min(ctrl_unk))}–{pctr(max(ctrl_unk))}", src)
ctrl_inf = [float(cen.loc[c, "pct_inferred"]) for c in controls]
ctrl_inf_nz = [v for v in ctrl_inf if v > 0]
reg("polaris_controls_inferred_range", [min(ctrl_inf_nz), max(ctrl_inf_nz)],
    f"{pctr(min(ctrl_inf_nz))}–{pctr(max(ctrl_inf_nz))}", src)
reg("polaris_controls_inferred_nonzero_n", len(ctrl_inf_nz), str(len(ctrl_inf_nz)), src)
reg("polaris_controls_n", len(controls), str(len(controls)), src)

es = pd.read_csv(os.path.join(PROC, "equinox_section_missingness.csv"))
src = "data/processed/equinox_section_missingness.csv <- analysis/seshat_missingness.py"
eq_map = {"Religion and Normative Ideology": "religion", "Warfare variables": "warfare",
          "Social Complexity variables": "soccomp"}
for sec, key in eq_map.items():
    row = es[es.section == sec].iloc[0]
    reg(f"equinox_{key}_pct_unknown", float(row.pct_unknown), pct(row.pct_unknown), src)
reg("equinox_total_values", int(es.rows.sum()), nint(es.rows.sum()), src)

ssumm = pd.read_csv(os.path.join(PROC, "seshat_summary.csv")).set_index("metric")["value"]
reg("equinox_n_regions", int(ssumm["equinox_n_regions"]),
    str(int(ssumm["equinox_n_regions"])),
    "seshat_summary.csv: equinox_n_regions (Equinox canon NGA column)")

pv = pd.read_csv(os.path.join(PROC, "polaris_variable_epistemic.csv")).set_index("variable_name")
src = "data/processed/polaris_variable_epistemic.csv <- analysis/seshat_missingness.py"
reg("polaris_var_fragmentation_pct", float(pv.loc["religious_fragmentation", "pct_unknown"]),
    pctr(pv.loc["religious_fragmentation", "pct_unknown"]), src)
mor = pv.loc[[i for i in pv.index if i.startswith("moralizing_")], "pct_unknown"]
reg("polaris_var_moralizing_range", [float(mor.min()), float(mor.max())],
    f"{pctr(mor.min())}–{pctr(mor.max())}", src)
reg("polaris_var_human_sacrifice_pct", float(pv.loc["human_sacrifice", "pct_unknown"]),
    pctr(pv.loc["human_sacrifice", "pct_unknown"]), src)

ev = pd.read_csv(os.path.join(PROC, "equinox_variable_missingness.csv")).set_index("variable")
src = "data/processed/equinox_variable_missingness.csv <- analysis/seshat_missingness.py"
for var, key in [("production of public goods", "pubgoods"),
                 ("Ideology reinforces prosociality", "ideo_prosoc"),
                 ("Rulers are gods", "rulers_gods")]:
    reg(f"equinox_var_{key}_pct", float(ev.loc[var, "pct_unknown"]),
        pctr(ev.loc[var, "pct_unknown"]), src)
auth = ev.loc["RA"]
reg("equinox_var_religious_authority_pct", float(auth.pct_unknown),
    f"under {pctr(auth.pct_unknown)}", src)

summ = pd.read_csv(os.path.join(PROC, "drh_summary.csv")).set_index("metric")["value"]
src = "data/processed/drh_summary.csv <- analysis/drh_missingness.py"
reg("drh_total_answers", int(summ["total_answers"]), nint(summ["total_answers"]), src)
reg("drh_n_entries", int(summ["n_entries"]), nint(summ["n_entries"]), src)
reg("drh_n_questions", int(summ["n_questions"]), nint(summ["n_questions"]), src)
reg("drh_unknown_share_all_pct", float(100 * summ["unknown_share_all"]),
    pct(100 * summ["unknown_share_all"]), src)

mod = pd.read_csv(os.path.join(PROC, "legibility_model_drh.csv")).set_index("feature")
boot = pd.read_csv(os.path.join(PROC, "legibility_model_drh_bootstrap.csv")).set_index("feature")
src = ("data/processed/legibility_model_drh{,_bootstrap}.csv "
       "<- analysis/legibility_model.py")
reg("model_n_questions", int(mod.n_questions.iloc[0]), nint(mod.n_questions.iloc[0]), src)
reg("model_n_answers", int(mod.n_answers.iloc[0]), nint(mod.n_answers.iloc[0]), src)
reg("model_n_clusters", int(boot.n_clusters.iloc[0]), str(boot.n_clusters.iloc[0]), src)
reg("model_n_boot", int(boot.n_boot.iloc[0]), nint(boot.n_boot.iloc[0]), src)
for f in ["numeric_magnitude", "diffuse_phenomenon", "institutional_object",
          "event_observable", "person_level", "abstract_judgment",
          "frequency_estimate"]:
    r = mod.loc[f]
    b = boot.loc[f]
    reg(f"model_{f}_or", float(r.odds_ratio), orr(r.odds_ratio), src)
    reg(f"model_{f}_qb_ci", [float(r.or_lo), float(r.or_hi)],
        f"{orr(r.or_lo)}–{orr(r.or_hi)}", src)
    reg(f"model_{f}_boot_ci", [float(b.boot_or_lo), float(b.boot_or_hi)],
        f"{orr(b.boot_or_lo)}–{orr(b.boot_or_hi)}", src)
    reg(f"model_{f}_wild_p", float(b.wild_boot_p), f"{b.wild_boot_p:.3f}", src)

q = pd.read_csv(os.path.join(PROC, "drh_legibility_codes.csv"))
q = q[q.n_answers >= 50]
a = q.loc[q.numeric_magnitude == 1, "unknown_share"].mean()
b = q.loc[q.numeric_magnitude == 0, "unknown_share"].mean()
reg("drh_numeric_vs_rest_ratio", float(a / b), f"{a / b:.1f}",
    "data/processed/drh_legibility_codes.csv (questions >=50 answers)")

audit = list(csv.DictReader(open(os.path.join(COD, "affordance_audit.csv"))))
n_ds = len({r["dataset"] for r in audit})
n_dom = len({r["domain"] for r in audit})
reg("audit_n_infrastructures", n_ds, str(n_ds), "coding/affordance_audit.csv")
reg("audit_n_domains", n_dom, str(n_dom), "coding/affordance_audit.csv")
lm_src = open(os.path.join(ROOT, "analysis", "legibility_model.py")).read()
rules_block = re.search(r"RULES = \{(.*?)\n\}", lm_src, re.S).group(1)
n_rules = len(re.findall(r'"[a-z_]+":', rules_block))
reg("legibility_n_features", n_rules, str(n_rules),
    "analysis/legibility_model.py RULES dict")

t3 = list(csv.DictReader(open(os.path.join(ROOT, "tables", "table3_hypotheses.csv"))))
statuses = [r["Status"].lower() for r in t3]
n_tested = sum(1 for s in statuses if s.startswith("tested"))
n_partial = sum(1 for s in statuses if s.startswith("partially"))
n_theory = len(statuses) - n_tested - n_partial
reg("n_hypotheses", len(statuses), str(len(statuses)), "tables/table3_hypotheses.csv")
reg("n_hypotheses_tested", n_tested, str(n_tested), "tables/table3_hypotheses.csv")
reg("n_hypotheses_partial", n_partial, str(n_partial), "tables/table3_hypotheses.csv")
reg("n_hypotheses_theory", n_theory, str(n_theory), "tables/table3_hypotheses.csv")

WORDS = {0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
         6: "six", 7: "seven", 8: "eight", 9: "nine", 18: "eighteen"}
for k in ["audit_n_infrastructures", "audit_n_domains", "legibility_n_features",
          "n_hypotheses", "polaris_controls_inferred_nonzero_n",
          "polaris_controls_n"]:
    R[k + "_word"] = dict(R[k])
    R[k + "_word"]["display"] = WORDS[R[k]["value"]]
for k, word in [("n_hypotheses_tested", "one"), ("n_hypotheses_partial", "one"),
                ("n_hypotheses_theory", "four")]:
    assert R[k]["display"] == str({"one": 1, "four": 4}[word]), (k, R[k])
    R[k + "_word"] = dict(R[k])
    R[k + "_word"]["display"] = word

json.dump({"generated_by": "analysis/canonical_results.py",
           "policy": "pcts one-decimal trimmed; ints comma-grouped; "
                     "ORs 1-2 decimals; ranges en-dash",
           "results": R}, open(OUT_JSON, "w"), indent=2, sort_keys=True)
print("wrote", OUT_JSON, "with", len(R), "keys")

def render(text):
    def sub(m):
        k = m.group(1)
        if k not in R:
            raise KeyError("unresolved token {{" + k + "}}")
        return str(R[k]["display"])
    return re.sub(r"\{\{([a-z0-9_]+)\}\}", sub, text)

for tpl, out in [("manuscript_template.md", "manuscript.md"),
                 ("cover_letter_template.md", "cover_letter.md")]:
    src_p = os.path.join(TPL, tpl)
    if not os.path.exists(src_p):
        continue
    rendered = render(open(src_p).read())
    out_p = os.path.join(ROOT, "manuscript", out)
    open(out_p, "w").write(rendered)
    print("rendered", out_p)
