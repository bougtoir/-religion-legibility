"""Generate all manuscript figures (PNG, 300 dpi, black text on white)."""
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Ellipse, Rectangle

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, "..")
PROC = os.path.join(ROOT, "data", "processed")
COD = os.path.join(ROOT, "coding")
FIG = os.path.join(ROOT, "figures")
os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.edgecolor": "black",
    "text.color": "black",
    "axes.labelcolor": "black",
    "xtick.color": "black",
    "ytick.color": "black",
})

def fig2_pipeline():
    fig, ax = plt.subplots(figsize=(8.5, 5.6))
    ax.set_xlim(0, 10); ax.set_ylim(0, 10.6); ax.axis("off")
    stages = [
        ("$R_i$", "Pre-classificatory\nreligious structure", "authority, norms,\npractice, identity,\nplace, tradition"),
        ("$C_{ij}$", "Classification", "category availability,\ncognitive burden,\nstigma, forced choice"),
        ("$D_{ij}$", "Documentation /\nmaterial trace", "textual, institutional,\ndocumentary footprint"),
        ("$I_{ij}$", "Inclusion", "sampling frame,\ndatabase architecture"),
        ("$K_{ij}$", "Codability", "codebook resolution,\nexpert knowledge,\ndesigned unknown state"),
        ("$Y_{ij}$", "Observed\nreligious datum", "census cell, survey\nresponse, database row"),
    ]
    w, h, ytop, ybot = 2.6, 2.5, 7.0, 1.9
    xs = [0.6, 3.7, 6.8]
    positions = [(xs[0], ytop), (xs[1], ytop), (xs[2], ytop),
                 (xs[2], ybot), (xs[1], ybot), (xs[0], ybot)]
    for (sym, title, sub), (x, y) in zip(stages, positions):
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                             fc="#f2f2f2", ec="black", lw=1.2)
        ax.add_patch(box)
        ax.text(x + w / 2, y + h - 0.38, sym, ha="center", fontsize=13, fontweight="bold")
        ax.text(x + w / 2, y + h - 1.15, title, ha="center", fontsize=9, fontweight="bold")
        ax.text(x + w / 2, y + 0.58, sub, ha="center", fontsize=7.6, color="#333333")
    arrowprops = dict(arrowstyle="-|>", lw=1.4, color="black")
    links = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)]
    for a, b in links:
        (xa, ya), (xb, yb) = positions[a], positions[b]
        if ya == yb:
            ax.add_patch(FancyArrowPatch((xa + w, ya + h / 2), (xb, yb + h / 2), **arrowprops))
        else:
            ax.add_patch(FancyArrowPatch((xa + w / 2, ya), (xb + w / 2, yb + h), **arrowprops))
    ax.add_patch(FancyArrowPatch((1.9, 1.9), (1.9, 0.85), **arrowprops))
    ax.annotate("comparative inference", xy=(1.9, 0.62), ha="center", fontsize=9, fontstyle="italic")
    ax.text(5.0, 10.15, "A religiously relevant phenomenon becomes data through staged selection",
            ha="center", fontsize=11, fontweight="bold")
    ax.text(5.3, 0.35, r"$P(\mathrm{observed\ as\ religious\ datum}\,|\,R_i)$ varies with the legibility of $R_i$",
            ha="center", fontsize=9, fontstyle="italic")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig2_pipeline.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)

def fig1_projection():
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(8.5, 3.6), gridspec_kw={"width_ratios": [1.5, 1]})
    axL.set_xlim(0, 10); axL.set_ylim(0, 10); axL.axis("off")
    dims = [
        ("A: recognized\nauthority", (3.4, 6.6)),
        ("N: normative\ncommitments", (6.6, 6.6)),
        ("P: practices\nand rituals", (2.6, 3.8)),
        ("I: identities /\nself-description", (7.4, 3.8)),
        ("L: institutions,\ncommunity, place", (5.0, 5.0)),
    ]
    for label, (x, y) in dims:
        axL.add_patch(Ellipse((x, y), 4.4, 3.1, fc="none", ec="black", lw=1.1))
        axL.text(x, y, label, ha="center", va="center", fontsize=8)
    axL.text(5.0, 9.4, r"$R_i=(A_i,N_i,P_i,I_i,L_i)$: overlapping, high-dimensional",
             ha="center", fontsize=9.5, fontweight="bold")
    axL.text(5.0, 0.5, "same person may hold multiple, partially overlapping positions",
             ha="center", fontsize=8, fontstyle="italic")

    axR.set_xlim(0, 10); axR.set_ylim(0, 10); axR.axis("off")
    box = FancyBboxPatch((2.0, 4.0), 6.0, 2.2, boxstyle="round,pad=0.06",
                         fc="#f2f2f2", ec="black", lw=1.4)
    axR.add_patch(box)
    axR.text(5.0, 5.1, r"$C_i=\Pi(R_i)$" + "\nsingle affiliation category",
             ha="center", fontsize=9.5, fontweight="bold")
    axR.text(5.0, 8.6, "one bounded, nameable category per person", ha="center", fontsize=8.5)
    for (lbl, yy) in [("same affiliation ≠ same authority", 2.9),
                      ("different affiliation ≠ disjoint authority", 2.1),
                      ("no affiliation ≠ no religiously", 1.3),
                      ("consequential norms", 0.8)]:
        axR.text(5.0, yy, lbl, ha="center", fontsize=8, fontstyle="italic")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig1_projection.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)

def fig3_heatmap():
    cod = pd.read_csv(os.path.join(COD, "affordance_audit.csv"))
    order_datasets = ["Census (confessional model, E&W 2021)",
                      "WVS Wave 7 (2017-2022) religion block",
                      "ISSP Religion IV module (2018)",
                      "Pew Religious Landscape Study 2023-24",
                      "Seshat Polaris 2026 (Equinox 2020 checked)",
                      "DRH SCCSR v3 (Zenodo 2026-01-20)",
                      "Pulotu v1.3.1 (D-PLACE release)",
                      "Ethnographic Atlas (D-PLACE EA v2016)",
                      "SCCS (D-PLACE SCCS v2015)"]
    dom_order = ["affiliation_membership", "exclusivity_multiple", "doctrine",
                 "scripture_canon", "clergy_hierarchy", "centralized_institution",
                 "territorial_polity", "public_ritual", "household_ritual",
                 "ancestor_practice", "sacred_place", "seasonal_local",
                 "diffuse_agents", "practice_without_identity", "normative_obligation",
                 "authority_source", "intergenerational", "uncertainty_missingness"]
    pretty_dom = ["Affiliation / membership", "Exclusivity / multiple belonging",
                  "Doctrine", "Scripture / canon", "Clergy / hierarchy",
                  "Centralized institution", "Territorial / polity anchoring",
                  "Public ritual", "Household ritual", "Ancestor practice",
                  "Sacred place / landscape", "Seasonal / local practice",
                  "Diffuse supernatural agents", "Practice without identity",
                  "Normative obligation", "Authority source",
                  "Intergenerational transmission", "Uncertainty / missingness design"]
    pretty_ds = ["Census (E&W 2021)", "WVS W7", "ISSP Religion IV", "Pew RLS 2023-24",
                 "Seshat Polaris", "DRH SCCSR v3", "Pulotu", "Ethnographic Atlas", "SCCS"]
    cat = {"absent": 0, "indirect": 1, "direct": 2, "NA": np.nan}
    cod["code"] = cod["availability"].map(cat)
    M = cod.pivot_table(index="dataset", columns="domain", values="code", aggfunc="first").loc[order_datasets, dom_order]
    fig, ax = plt.subplots(figsize=(9.5, 3.9))
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("aff", ["#f0f0f0", "#bdbdbd", "#252525"])
    cmap.set_bad(color="#ffffff")
    im = ax.imshow(M.values, cmap=cmap, vmin=0, vmax=2, aspect="auto")
    ax.set_xticks(range(len(dom_order)))
    ax.set_xticklabels(pretty_dom, rotation=55, ha="right", fontsize=7.5)
    ax.set_yticks(range(len(order_datasets)))
    ax.set_yticklabels(pretty_ds, fontsize=8.5)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M.values[i, j]
            if np.isnan(v):
                ax.add_patch(Rectangle((j - .5, i - .5), 1, 1, fill=False,
                                       hatch="///", edgecolor="#888888", lw=0))
                ax.text(j, i, "NA", ha="center", va="center", fontsize=5.5, color="#888888")
            else:
                lbl = {0.0: "abs", 1.0: "ind", 2.0: "dir"}[v]
                ax.text(j, i, lbl, ha="center", va="center", fontsize=6,
                        color="white" if v == 2 else "black")
    cbar = fig.colorbar(im, ax=ax, ticks=[0, 1, 2], shrink=0.7)
    cbar.ax.set_yticklabels(["absent", "indirect", "direct"], fontsize=7.5)
    ax.set_title("Measurement affordance by instrument and domain\n(NA = outside the instrument's unit of analysis)", fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig3_affordance_heatmap.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)

def fig4_missingness():
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(9.5, 4.2))
    cen = pd.read_csv(os.path.join(PROC, "polaris_epistemic_census.csv"))
    order = ["Religion", "Warfare", "Social complexity", "Luxury goods", "General"]
    cen = cen.set_index("collection").loc[order].reset_index()
    x = np.arange(len(cen))
    axA.bar(x - 0.2, cen["pct_unknown"], width=0.4, color="#252525",
            edgecolor="black", label="explicit unknown (u/su/unknown/uncoded)")
    axA.bar(x + 0.2, cen["pct_inferred"], width=0.4, color="#bdbdbd",
            edgecolor="black", label="inferred present/absent (ip/ia)")
    axA.set_xticks(x)
    axA.set_xticklabels(cen["collection"], rotation=30, ha="right", fontsize=8)
    axA.set_ylabel("Share of recorded values (%)")
    axA.set_title("A. Polaris 2026: epistemic-state census by collection", fontsize=9.5)
    axA.set_ylim(0, 26)
    axA.legend(fontsize=6.8, loc="upper left")
    for i, (u, f_) in enumerate(zip(cen["pct_unknown"], cen["pct_inferred"])):
        axA.text(i - 0.2, u + 0.5, f"{u:.1f}", ha="center", fontsize=6.8)
        axA.text(i + 0.2, f_ + 0.5, f"{f_:.1f}", ha="center", fontsize=6.8)

    pv = pd.read_csv(os.path.join(PROC, "polaris_variable_epistemic.csv"))
    pv = pv.sort_values("pct_unknown")
    labels = [v.replace("moralizing_", "mor_").replace("_", " ") for v in pv["variable_name"]]
    axB.barh(range(len(pv)), pv["pct_unknown"], color="#9e9e9e", edgecolor="black")
    axB.set_yticks(range(len(pv)))
    axB.set_yticklabels(labels, fontsize=6.2)
    axB.set_xlabel("Explicit-unknown share of recorded values (%)")
    axB.set_title("B. Within the religion collection, by variable", fontsize=9.5)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig4_missingness_controls.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)

def fig5_drh_gradient():
    q = pd.read_csv(os.path.join(PROC, "drh_legibility_codes.csv"))
    q = q[q["n_answers"] >= 50].copy()
    mod = pd.read_csv(os.path.join(PROC, "legibility_model_drh.csv"))
    fig, (axA, axB) = plt.subplots(1, 2, figsize=(9.5, 4.3), gridspec_kw={"width_ratios": [1.15, 1]})
    feats = ["numeric_magnitude", "diffuse_phenomenon", "person_level",
             "abstract_judgment", "frequency_estimate",
             "institutional_object", "event_observable"]
    data = [100 * q.loc[q[f_] == 1, "unknown_share"] for f_ in feats]
    axA.boxplot(data, vert=True, widths=0.55, patch_artist=True,
                medianprops={"color": "black"}, showfliers=False,
                boxprops={"facecolor": "#d9d9d9"})
    for i, d in enumerate(data):
        jit = np.random.default_rng(i).uniform(-0.18, 0.18, len(d))
        axA.scatter(i + 1 + jit, d, s=2.5, color="#555555", alpha=0.35)
    axA.set_xticklabels([g.replace("_", " ") for g in feats], fontsize=6.5, rotation=25, ha="right")
    axA.set_ylabel("Unknown-answer share per question (%)")
    axA.set_title("A. Distribution by coded legibility class (questions with feature = 1)", fontsize=9)

    m2 = mod[mod.feature != "const"].iloc[::-1]
    try:
        boot = pd.read_csv(os.path.join(PROC, "legibility_model_drh_bootstrap.csv"))
        b2 = boot[boot.feature != "const"].iloc[::-1]
        axB.errorbar(b2["odds_ratio"], np.arange(len(b2)) + 0.18,
                     xerr=[b2["odds_ratio"] - b2["boot_or_lo"],
                           b2["boot_or_hi"] - b2["odds_ratio"]],
                     fmt="none", ecolor="#bbbbbb", elinewidth=3, capsize=0,
                     label="cluster bootstrap 95% CI")
    except Exception:
        pass
    axB.errorbar(m2["odds_ratio"], range(len(m2)),
                 xerr=[m2["odds_ratio"] - m2["or_lo"], m2["or_hi"] - m2["odds_ratio"]],
                 fmt="o", color="black", ecolor="#555555", capsize=3, markersize=5,
                 label="quasi-binomial 95% CI")
    axB.axvline(1, color="black", lw=0.8, ls="--")
    axB.set_yticks(range(len(m2)))
    axB.set_yticklabels(m2["feature"].str.replace("_", " "), fontsize=8)
    axB.set_xscale("log")
    axB.set_xlim(0.4, 40)
    axB.legend(fontsize=6.5, loc="lower right")
    axB.set_xlabel("Odds ratio for unknown answer (log scale, 95% CI)")
    import json
    reg = json.load(open(os.path.join(PROC, "canonical_results.json")))["results"]
    axB.set_title("B. Quasi-binomial model (n=%s questions)" % reg["model_n_questions"]["display"], fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig5_drh_gradient.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)

if __name__ == "__main__":
    fig2_pipeline()
    fig1_projection()
    fig3_heatmap()
    fig4_missingness()
    fig5_drh_gradient()
    print("figures written:", sorted(os.listdir(FIG)))
