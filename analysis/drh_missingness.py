"""DRH (SCCSR v3) structured-missingness analysis.

The DRH lets experts answer "Field doesn't know" or "I don't know" per question —
an explicit, designed-in epistemic state that most datasets lack. That makes DRH a
partial falsification check for H6 (structured missingness): the platform admits
uncertainty, but *which* questions accumulate unknowns still traces legibility.

Outputs (data/processed/):
  - drh_unknown_by_question.csv   per-question unknown-answer share
  - drh_unknown_by_poll.csv       per-poll unknown-answer share
  - drh_answer_value_counts.csv   answer_value distribution
  - drh_summary.csv               headline stats
"""
import os
import pandas as pd

RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "drh", "drh_tables")
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
os.makedirs(OUT, exist_ok=True)

UNKNOWN_ANSWERS = {
    "field doesn't know",
    "i don't know",
    "el campo lo desconoce",
    "je ne sais pas",
    "我不知道",
}

def main():
    df = pd.read_csv(
        os.path.join(RAW, "answerset.csv"),
        usecols=["question_id", "question_name", "answer", "answer_value",
                 "entry_id", "poll_name", "branching_question"],
        low_memory=False,
    )
    ans = df["answer"].astype(str).str.strip().str.lower()
    df["unk"] = ans.isin(UNKNOWN_ANSWERS)

    by_q = (
        df.groupby(["question_id", "question_name", "poll_name"])
        .agg(n=("unk", "size"), unknown=("unk", "sum"), unknown_share=("unk", "mean"),
             entries=("entry_id", "nunique"))
        .reset_index()
        .sort_values("unknown_share", ascending=False)
    )
    by_q.to_csv(os.path.join(OUT, "drh_unknown_by_question.csv"), index=False)

    by_poll = (
        df.groupby("poll_name")
        .agg(n=("unk", "size"), unknown=("unk", "sum"), unknown_share=("unk", "mean"),
             questions=("question_id", "nunique"), entries=("entry_id", "nunique"))
        .reset_index()
        .sort_values("unknown_share", ascending=False)
    )
    by_poll.to_csv(os.path.join(OUT, "drh_unknown_by_poll.csv"), index=False)

    df["answer_value"].astype(str).value_counts().to_frame("count").to_csv(
        os.path.join(OUT, "drh_answer_value_counts.csv"))

    binmask = df["answer_value"].astype(str).isin(["0", "1"])
    summ = pd.DataFrame([
        {"metric": "total_answers", "value": len(df)},
        {"metric": "total_unknown", "value": int(df["unk"].sum())},
        {"metric": "unknown_share_all", "value": df["unk"].mean()},
        {"metric": "unknown_share_binary_questions", "value": df.loc[binmask, "unk"].mean()},
        {"metric": "n_questions", "value": df["question_id"].nunique()},
        {"metric": "n_entries", "value": df["entry_id"].nunique()},
        {"metric": "questions_gt30pct_unknown", "value": int((by_q["unknown_share"] > 0.3).sum())},
        {"metric": "questions_lt2pct_unknown", "value": int((by_q["unknown_share"] < 0.02).sum())},
    ])
    summ.to_csv(os.path.join(OUT, "drh_summary.csv"), index=False)
    print(summ.to_string(index=False))
    print()
    print(by_poll.to_string(index=False))
    print()
    print(by_q.head(40).to_string(index=False))

if __name__ == "__main__":
    main()
