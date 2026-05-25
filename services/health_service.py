from __future__ import annotations

import pandas as pd
from sqlalchemy.dialects.postgresql import insert
from db.connection import get_session
from db.schema import HealthRecord, User


def upsert_health_record(data: dict) -> None:
    session = get_session()
    try:
        stmt = insert(HealthRecord).values(**data)
        update_cols = {c.name: getattr(stmt.excluded, c.name) for c in HealthRecord.__table__.columns if c.name not in ["id", "created_at"]}
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
        return [
            {
                "記録日": r.record_date,
                "利用者名": u.display_name,
                "体温": r.temperature,
                "血圧上": r.bp_high,
                "血圧下": r.bp_low,
                "脈拍": r.pulse,
                "SpO2": r.spo2,
                "体重": r.weight,
                "朝食": r.breakfast_rate,
                "昼食": r.lunch_rate,
                "夕食": r.dinner_rate,
                "気になる変化": r.change_note,
                "登録日時": r.created_at,
                "更新日時": r.updated_at,
                "入力者": r.input_by,
            }
            for r, u in rows
        ]
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
