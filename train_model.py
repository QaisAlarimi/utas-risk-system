"""Train the subtype/category suggestion model.

Two sources (never mixed silently):
  * synthetic : the supervisor's Campus_Risk_Dataset_1000_Synthetic_Reports.xlsx  (AI-generated sample
                data - for pipeline development / preliminary NLP experiments only, NOT ground truth)
  * verified  : real reports verified by an admin inside the app (needs >=100 rows)
Usage:  python train_model.py            -> trains the synthetic-data model into models/
Evaluation follows README_ML: group split (identical texts never cross train/test), macro-F1,
per-class recall.  NOTE: the synthetic data is template-like, so scores near 100% only prove the
pipeline works, not real-world accuracy."""
import os, datetime as dt
import joblib, numpy as np, pandas as pd
from sklearn.pipeline import Pipeline, make_union
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import f1_score, accuracy_score, recall_score
import config

SYN_XLSX = os.path.join(config.BASE, "data", "Campus_Risk_Dataset_1000_Synthetic_Reports.xlsx")
PATH_SYN = os.path.join(config.MODEL_DIR, "category_model_synthetic.joblib")
PATH_VER = os.path.join(config.MODEL_DIR, "category_model_verified.joblib")
MIN_ROWS = 100
MIN_PER_CLASS = 5


def _pipe():
    vec = make_union(TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True),
                     TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True))
    return Pipeline([("vec", vec), ("clf", LogisticRegression(max_iter=3000, C=10))])


def _fit_eval(texts, labels, data_kind, out_path):
    texts, labels = pd.Series(texts).reset_index(drop=True), pd.Series(labels).reset_index(drop=True)
    groups = texts.str.lower().str.strip()
    tr, te = next(GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=7).split(texts, groups=groups))
    p = _pipe().fit(texts[tr], labels[tr])
    pred = p.predict(texts[te])
    f1 = f1_score(labels[te], pred, average="macro")
    cat_acc = float((pd.Series(pred).str[:2].values == labels[te].str[:2].values).mean())
    rec = recall_score(labels[te], pred, average=None, labels=sorted(set(labels)), zero_division=0)
    p = _pipe().fit(texts, labels)                     # final model on all rows
    os.makedirs(config.MODEL_DIR, exist_ok=True)
    meta = {"data": data_kind, "rows": int(len(texts)), "classes": int(labels.nunique()), "macro_f1_holdout": float(f1),
            "category_acc_holdout": cat_acc, "min_class_recall": float(np.min(rec)), "model": "TF-IDF(word+char) + LogisticRegression",
            "split": "group split by identical text (no duplicate crossing)", "trained_at": dt.datetime.now().isoformat(timespec="seconds")}
    joblib.dump({"pipe": p, "meta": meta}, out_path)
    return meta


def train_synthetic():
    df = pd.read_excel(SYN_XLSX, sheet_name="Risk_Reports_Dataset")
    return _fit_eval(df.risk_description, df.risk_subtype_code, "synthetic", PATH_SYN)


def train_verified(df: pd.DataFrame):
    df = df.dropna(subset=["risk_description", "risk_subtype_verified"])
    df = df[~df.get("is_demo", False)] if "is_demo" in df else df
    vc = df.risk_subtype_verified.value_counts()
    d = df[df.risk_subtype_verified.isin(vc[vc >= MIN_PER_CLASS].index)]
    if len(d) < MIN_ROWS or d.risk_subtype_verified.nunique() < 2:
        return None, f"{len(df)} verified real rows, {d.risk_subtype_verified.nunique()} usable subtypes"
    return _fit_eval(d.risk_description, d.risk_subtype_verified, "verified", PATH_VER), ""


if __name__ == "__main__":
    print(train_synthetic())
