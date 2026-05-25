
from __future__ import annotations
from datetime import datetime, date, timedelta
try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None

JST = ZoneInfo("Asia/Tokyo") if ZoneInfo else None

def now_jst_dt() -> datetime:
    if JST:
        return datetime.now(JST)
    return datetime.utcnow() + timedelta(hours=9)

def format_now_jst(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    return now_jst_dt().strftime(fmt)

def now_jst() -> str:
    return format_now_jst("%Y-%m-%d %H:%M:%S")

def today_jst() -> date:
    return now_jst_dt().date()

def to_date_str(value) -> str:
    if not value:
        return ""
    try:
        return value.strftime("%Y-%m-%d")
    except Exception:
        return str(value)[:10]
