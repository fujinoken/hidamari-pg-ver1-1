from __future__ import annotations

import re
import hashlib
import pandas as pd


def clean_text(value, default: str = "") -> str:
    try:
        if pd.isna(value):
            return default
    except Exception:
        pass
    text = str(value).strip()
    if text.lower() in ["nan", "none", "nat"]:
        return default
    return text


def normalize_user_name_for_match(name: str) -> str:
    text = clean_text(name)
    text = re.sub(r"\s+", "", text)
    text = text.replace("　", "")
    text = text.replace("様", "").replace("さん", "").replace("殿", "")
    return text.lower()


def stable_user_code(name: str) -> str:
    base = normalize_user_name_for_match(name) or clean_text(name)
    return "usr_" + hashlib.sha1(base.encode("utf-8")).hexdigest()[:12]


def safe_float(value, default=None):
    try:
        if value in [None, ""]:
            return default
        return float(value)
    except Exception:
        return default


def safe_int(value, default=0):
    try:
        if value in [None, ""]:
            return default
        return int(float(value))
    except Exception:
        return default
