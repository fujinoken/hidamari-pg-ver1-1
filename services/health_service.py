from __future__ import annotations

import pandas as pd
from sqlalchemy.dialects.postgresql import insert
from db.connection import get_session
from db.schema import HealthRecord, User


def health_record_to_dict(record: HealthRecord, user_name: str = "") -> dict:
    return {
        "ID": record.id,
        "記録日": record.record_date,
        "利用者名": user_name,
        "体温": record.temperature,
        "血圧上": record.bp_high,
        "血圧下": record.bp_low,
        "脈拍": record.pulse,
        "SpO2": record.spo2,
        "体重": record.weight,
        "朝食": record.breakfast_rate,
        "昼食": record.lunch_rate,
        "夕食": record.dinner_rate,
        "水分ml": record.water_ml,
        "家族共有メモ": record.family_note,
        "気になる変化": record.change_note,
        "入力者": record.input_by,
        "登録日時": record.created_at,
        "更新日時": record.updated_at,
    }


def upsert_health_record(data: dict) -> None:
    session = get_session()
    try:
        stmt = insert(HealthRecord).values(**data)
        update_cols = {
            c.name: getattr(stmt.excluded, c.name)
            for c in HealthRecord.__table__.columns
            if c.name not in ["id", "created_at"]
        }
        stmt = stmt.on_conflict_do_update(
            constraint="uq_health_record_date_user",
            set_=update_cols,
        )
        session.execute(stmt)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def list_health_records(limit: int = 300):
    session = get_session()
    try:
        rows = (
            session.query(HealthRecord, User)
            .join(User, HealthRecord.user_id == User.id)
            .order_by(HealthRecord.record_date.desc(), User.display_name.asc())
            .limit(limit)
            .all()
        )
        return [health_record_to_dict(r, u.display_name) for r, u in rows]
    finally:
        session.close()


def search_health_records(user_id: int | None = None, date_from=None, date_to=None, keyword: str = "", limit: int = 500):
    session = get_session()
    try:
        q = session.query(HealthRecord, User).join(User, HealthRecord.user_id == User.id)
        if user_id:
            q = q.filter(HealthRecord.user_id == user_id)
        if date_from:
            q = q.filter(HealthRecord.record_date >= date_from)
        if date_to:
            q = q.filter(HealthRecord.record_date <= date_to)
        if keyword:
            like = f"%{keyword}%"
            q = q.filter((HealthRecord.family_note.ilike(like)) | (HealthRecord.change_note.ilike(like)) | (HealthRecord.input_by.ilike(like)))
        rows = q.order_by(HealthRecord.record_date.desc(), User.display_name.asc()).limit(limit).all()
        return [health_record_to_dict(r, u.display_name) for r, u in rows]
    finally:
        session.close()


def get_health_record(record_id: int) -> dict | None:
    session = get_session()
    try:
        row = (
            session.query(HealthRecord, User)
            .join(User, HealthRecord.user_id == User.id)
            .filter(HealthRecord.id == record_id)
            .first()
        )
        if not row:
            return None
        r, u = row
        return health_record_to_dict(r, u.display_name)
    finally:
        session.close()


def update_health_record(record_id: int, data: dict) -> None:
    session = get_session()
    try:
        record = session.query(HealthRecord).filter(HealthRecord.id == record_id).first()
        if not record:
            raise ValueError("対象の健康記録が見つかりません。")
        for key, value in data.items():
            if hasattr(record, key):
                setattr(record, key, value)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def delete_health_record(record_id: int) -> None:
    session = get_session()
    try:
        record = session.query(HealthRecord).filter(HealthRecord.id == record_id).first()
        if not record:
            raise ValueError("対象の健康記録が見つかりません。")
        session.delete(record)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def latest_weight_by_user(user_id: int):
    session = get_session()
    try:
        return (
            session.query(HealthRecord)
            .filter(HealthRecord.user_id == user_id, HealthRecord.weight.isnot(None))
            .order_by(HealthRecord.record_date.desc())
            .first()
        )
    finally:
        session.close()


def weight_unmeasured_over(days: int = 14):
    session = get_session()
    try:
        users = session.query(User).filter(User.is_visible == True).all()  # noqa: E712
        rows = []
        today = pd.Timestamp.today().date()
        for u in users:
            latest = (
                session.query(HealthRecord)
                .filter(HealthRecord.user_id == u.id, HealthRecord.weight.isnot(None))
                .order_by(HealthRecord.record_date.desc())
                .first()
            )
            if not latest:
                rows.append({"利用者名": u.display_name, "最新体重": "未測定", "最終測定日": "", "経過日数": "未測定"})
            else:
                elapsed = (today - latest.record_date).days
                if elapsed >= days:
                    rows.append({"利用者名": u.display_name, "最新体重": latest.weight, "最終測定日": latest.record_date, "経過日数": elapsed})
        return rows
    finally:
        session.close()
