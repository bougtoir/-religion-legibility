"""Build/validate manuscript tables.

- table4_audit_summary.csv is GENERATED from coding/affordance_audit.csv
  (never hand-edited).
- table1/table2/table3 are curated CSVs; {{key}} tokens inside them are
  resolved against data/processed/canonical_results.json (same registry as
  the manuscript), then schema-checked.
"""
import csv
import glob
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
COD = os.path.join(ROOT, "coding")
TAB = os.path.join(ROOT, "tables")
REG = json.load(open(os.path.join(ROOT, "data", "processed",
                                   "canonical_results.json")))["results"]

def render(text):
    def sub(m):
        k = m.group(1)
        if k not in REG:
            raise KeyError("unresolved token {{" + k + "}}")
        return str(REG[k]["display"])
    return re.sub(r"\{\{([a-z0-9_]+)\}\}", sub, text)

audit = list(csv.DictReader(open(os.path.join(COD, "affordance_audit.csv"))))
by_ds = {}
for r in audit:
    d = by_ds.setdefault(r["dataset"], {"absent": 0, "direct": 0, "indirect": 0})
    if r["availability"] in d:
        d[r["availability"]] += 1
rows = [["dataset", "absent", "direct", "indirect", "direct_or_indirect"]]
for ds in sorted(by_ds):
    d = by_ds[ds]
    rows.append([ds, d["absent"], d["direct"], d["indirect"],
                 d["direct"] + d["indirect"]])
with open(os.path.join(TAB, "table4_audit_summary.csv"), "w", newline="") as f:
    csv.writer(f).writerows(rows)
print("table4_audit_summary.csv regenerated:", len(rows) - 1, "datasets")

for name in ["table1_genealogy.csv", "table2_legibility.csv",
             "table3_hypotheses.csv"]:
    p = os.path.join(TAB, name)
    if not os.path.exists(p):
        sys.exit("missing " + name)
    raw = open(p).read()
    rendered = render(raw)
    if rendered != raw:
        open(p, "w").write(rendered)
        print(name, "tokens resolved")
    data = list(csv.reader(open(p)))
    assert len(data) > 1, name + " empty"
    print(name, len(data) - 1, "rows")
