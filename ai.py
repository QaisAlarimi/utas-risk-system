"""AI suggestion layer. Suggests category/subtype + likelihood/severity/level; a human decides.
 - rules-v0: keyword scoring (works with no data).
 - ml: scikit-learn pipeline in models/ (created by train_model.py from VERIFIED reports only),
   used automatically when it exists."""
import os, re, joblib
import config
from keywords import KEYWORDS, IMMEDIATE_WORDS

import train_model
_ml = {}


def _load_ml():
    """Prefer a model trained on VERIFIED real reports; else the supervisor's synthetic-data model."""
    if "m" not in _ml:
        m = None
        for p in (train_model.PATH_VER, train_model.PATH_SYN):
            if os.path.exists(p):
                m = joblib.load(p)
                break
        _ml["m"] = m
    return _ml["m"]


def reload():
    _ml.clear()


def model_meta():
    m = _load_ml()
    return m["meta"] if m else None


def _is_latin(text):
    letters = [c for c in text if c.isalpha()]
    return bool(letters) and sum(c.isascii() for c in letters) / len(letters) > 0.6


def _rules(text):
    t = text.lower()
    best, hits = None, []
    for code, kws in KEYWORDS.items():
        matched = [k for k in kws if k.lower() in t]
        if matched:
            hits.append((sum(len(k) for k in matched), code, matched))
    hits.sort(reverse=True)
    if not hits:
        return None, 0.0, []
    top = hits[0]
    second = hits[1][0] if len(hits) > 1 else 0
    conf = min(0.9, 0.4 + 0.1 * len(top[2]) + (0.1 if top[0] > second * 1.3 else 0))
    return top[1], round(conf, 2), top[2]


def suggest(text, urgency="Normal", injury="Unknown", immediate="Unknown", people="Unknown", frequency="Unknown"):
    """Hybrid: ML model (English text) + keyword rules (English/Arabic). The human always decides."""
    m = _load_ml()
    ml_sub, ml_conf, alts = None, 0.0, []
    if m is not None and _is_latin(text):
        p = m["pipe"].predict_proba([text])[0]
        order = p.argsort()[::-1][:3]
        ml_sub, ml_conf = m["pipe"].classes_[order[0]], round(float(p[order[0]]), 2)
        alts = [(m["pipe"].classes_[i], float(p[i])) for i in order[1:]]
    r_sub, r_conf, r_why = _rules(text)
    why = []
    if ml_sub and r_sub == ml_sub:
        sub, conf, source = ml_sub, min(0.95, max(ml_conf, r_conf) + 0.1), "ml+rules"
        why = r_why
    elif ml_sub and (ml_conf >= 0.45 or not r_sub):
        sub, conf, source = ml_sub, ml_conf, "ml"
        why = ["model: " + ", ".join(f"{c} {p:.0%}" for c, p in [(ml_sub, ml_conf)] + alts)]
    elif r_sub:
        sub, conf, source, why = r_sub, r_conf, "rules-v0", r_why
    else:
        sub, conf, source = None, 0.0, "none"
    if source == "ml" and conf < 0.10:      # model is guessing: say so instead of showing a random type
        sub, conf, source, why = None, 0.0, "none", []
    cat = config.SUBTYPES[sub][0] if sub else None

    # likelihood / severity heuristics (placeholder until the specialist defines the rubric)
    t = text.lower()
    imm_hit = [w for w in IMMEDIATE_WORDS if w in t] or ([] if immediate != "Yes" else ["immediate hazard flagged"])
    L = 3
    if frequency in ("Daily", "Continuously") or people in ("21-50", "50+"):
        L = 4
    if frequency == "Rarely" and people in ("1", "2-5"):
        L = 2
    if urgency == "Immediate" or imm_hit:
        L = max(L, 4)
    S = {"EH": 4, "FH": 4, "CH": 4, "PH": 3, "ED": 2, "HK": 2}.get(cat, 2)
    if injury == "Yes":
        S = min(5, S + 1)
    if imm_hit and S < 4:
        S = 4
    level = config.level_from_score(L * S)
    reason = ", ".join(why) if why else "no clear keywords found - please classify manually"
    return {"category": cat, "subtype": sub, "likelihood": L, "severity": S, "level": level,
            "confidence": conf if sub else 0.0, "source": source, "reason": reason,
            "immediate": bool(imm_hit) or immediate == "Yes" or urgency == "Immediate"}
