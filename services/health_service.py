from __future__ import annotations

import uuid
import datetime as dt
import pandas as pd
from sqlalchemy import text
from db.migrations import get_engine
from config.settings import DEFAULT_FACILITY_ID

def _date_value(d):
    if isinstance(d, dt.datetime):
        return d.date()
    if isinstance(d, dt.date):
        return d
    return dt.date.fromisoformat(str(d))

def _str_or_none(v):
    if v is None:
        return None
    v = str(v).strip()
    return v if v else None

def create_user(user_name: str, user_code: str = "", facility_id: str = DEFAULT_FACILITY_ID):
    user_name = user_name.strip()
    if not user_name:
        raise ValueError("利用者名を入力してください。")
    engine = get_engine()
    uid = str(uuid.uuid4())
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO users (id, facility_id, user_code, user_name, is_active)
                VALUES (:id, :facility_id, :user_code, :user_name, true)
            """),
            {
                "id": uid,
                "facility_id": facility_id,
                "user_code": user_code.strip(),
                "user_name": user_name,
            },
        )
    return uid

def list_users(facility_id: str = DEFAULT_FACILITY_ID, active_only: bool = True):
    engine = get_engine()
    where_active = "AND COALESCE(is_active, true) = true" if active_only else ""
    with engine.begin() as conn:
        rows = conn.execute(
            text(f"""
                SELECT CAST(id AS TEXT) AS id,
                       COALESCE(CAST(user_code AS TEXT), '') AS user_code,
                       COALESCE(CAST(user_name AS TEXT), '') AS user_name,
                       COALESCE(is_active, true) AS is_active
                FROM users
                WHERE COALESCE(CAST(facility_id AS TEXT), 'default') = :facility_id
                {where_active}
                ORDER BY user_name
            """),
            {"facility_id": facility_id},
        ).mappings().all()
    return [dict(r) for r in rows]

def get_user_options(facility_id: str = DEFAULT_FACILITY_ID):
    users = list_users(facility_id)
    return {f"{u['user_name']}（{u['user_code']}）" if u.get("user_code") else u["user_name"]: u["id"] for u in users}

def save_health_record(
    record_date,
    user_id: str,
    temperature=None,
    bp_high=None,
    bp_low=None,
    pulse=None,
    spo2=None,
    weight=None,
    meal_rate=None,
    memo="",
    facility_id: str = DEFAULT_FACILITY_ID,
):
    if not user_id:
        raise ValueError("利用者を選択してください。")
    engine = get_engine()
    record_id = str(uuid.uuid4())
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO health_records
                (id, facility_id, record_date, user_id, temperature, bp_high, bp_low,
                 pulse, spo2, weight, meal_rate, memo)
                VALUES
                (:id, :facility_id, :record_date, :user_id, :temperature, :bp_high, :bp_low,
                 :pulse, :spo2, :weight, :meal_rate, :memo)
            """),
            {
                "id": record_id,
                "facility_id": facility_id,
                "record_date": _date_value(record_date),
                "user_id": str(user_id),
                "temperature": temperature,
                "bp_high": bp_high,
                "bp_low": bp_low,
                "pulse": pulse,
                "spo2": spo2,
                "weight": weight,
                "meal_rate": meal_rate,
                "memo": memo,
            },
        )
    return record_id

def update_health_record(record_id: str, **kwargs):
    allowed = ["record_date", "user_id", "temperature", "bp_high", "bp_low", "pulse", "spo2", "weight", "meal_rate", "memo"]
    values = {k: kwargs[k] for k in allowed if k in kwargs}
    if "record_date" in values:
        values["record_date"] = _date_value(values["record_date"])
    if "user_id" in values and values["user_id"] is not None:
        values["user_id"] = str(values["user_id"])
    if not values:
        return
    values["id"] = str(record_id)
    set_clause = ", ".join([f"{k} = :{k}" for k in values.keys() if k != "id"])
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text(f"UPDATE health_records SET {set_clause} WHERE CAST(id AS TEXT) = :id"), values)

def delete_health_record(record_id: str):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM health_records WHERE CAST(id AS TEXT) = :id"),
            {"id": str(record_id)},
        )

def list_health_records(
    facility_id: str = DEFAULT_FACILITY_ID,
    start_date=None,
    end_date=None,
    user_id: str | None = None,
    limit: int = 300,
):
    engine = get_engine()
    params = {"facility_id": facility_id, "limit": int(limit)}
    where = ["COALESCE(CAST(h.facility_id AS TEXT), 'default') = :facility_id"]

    if start_date:
        where.append("h.record_date >= :start_date")
        params["start_date"] = _date_value(start_date)
    if end_date:
        where.append("h.record_date <= :end_date")
        params["end_date"] = _date_value(end_date)
    if user_id:
        where.append("CAST(h.user_id AS TEXT) = :user_id")
        params["user_id"] = str(user_id)

    sql = f"""
        SELECT
            CAST(h.id AS TEXT) AS id,
            h.record_date,
            CAST(h.user_id AS TEXT) AS user_id,
            COALESCE(CAST(u.user_name AS TEXT), CAST(h.user_id AS TEXT)) AS user_name,
            h.temperature, h.bp_high, h.bp_low, h.pulse, h.spo2,
            h.weight, h.meal_rate, h.memo
        FROM health_records h
        LEFT JOIN users u
          ON CAST(h.user_id AS TEXT) = CAST(u.id AS TEXT)
        WHERE {" AND ".join(where)}
        ORDER BY h.record_date DESC, user_name ASC
        LIMIT :limit
    """
    with engine.begin() as conn:
        rows = conn.execute(text(sql), params).mappings().all()
    return pd.DataFrame([dict(r) for r in rows])

def today_input_status(facility_id: str = DEFAULT_FACILITY_ID, target_date=None):
    target_date = _date_value(target_date or dt.date.today())
    engine = get_engine()
    with engine.begin() as conn:
        rows = conn.execute(
            text("""
                SELECT
                    CAST(u.id AS TEXT) AS user_id,
                    COALESCE(CAST(u.user_name AS TEXT), '') AS user_name,
                    CASE WHEN COUNT(h.id) > 0 THEN 1 ELSE 0 END AS done
                FROM users u
                LEFT JOIN health_records h
                  ON CAST(h.user_id AS TEXT) = CAST(u.id AS TEXT)
                 AND h.record_date = :target_date
                WHERE COALESCE(CAST(u.facility_id AS TEXT), 'default') = :facility_id
                  AND COALESCE(u.is_active, true) = true
                GROUP BY CAST(u.id AS TEXT), COALESCE(CAST(u.user_name AS TEXT), '')
                ORDER BY user_name
            """),
            {"facility_id": facility_id, "target_date": target_date},
        ).mappings().all()
    df = pd.DataFrame([dict(r) for r in rows])
    if not df.empty:
        df["入力状況"] = df["done"].apply(lambda x: "入力済み" if int(x) == 1 else "未入力")
    return df
