from __future__ import annotations

from datetime import datetime, date, timedelta
try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None

JST = ZoneInfo("Asia/Tokyo") if ZoneInfo else None


def now_jst_dt() -> datetime:
    if JST:
        return datetime.now(JST)
    return datetime.utcnow() + timedelta(hours=9)


def now_jst() -> str:
    return now_jst_dt().strftime("%Y-%m-%d %H:%M:%S")


def today_jst() -> date:
    return now_jst_dt().date()


def fmt_dt(value) -> str:
    if not value:
        return ""
    try:
        return value.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(value)
