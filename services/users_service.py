
from __future__ import annotations
import uuid
import pandas as pd
from sqlalchemy import select, insert, update
from db.connection import get_engine
from db.schema import users
from config.settings import DEFAULT_FACILITY_ID
from utils.time_utils import now_jst_dt

def list_users(active_only=True) -> pd.DataFrame:
    with get_engine().begin() as conn:
        stmt = select(users).where(users.c.facility_id == DEFAULT_FACILITY_ID).order_by(users.c.user_name)
        if active_only:
            stmt = stmt.where(users.c.display_flag == True)
        rows = conn.execute(stmt).mappings().all()
    return pd.DataFrame([dict(r) for r in rows])

def user_options() -> list[dict]:
    df = list_users(active_only=True)
    if df.empty:
        return []
    return df.to_dict("records")

def add_user(user_name: str, memo: str = ""):
    with get_engine().begin() as conn:
        conn.execute(insert(users).values(
            id=str(uuid.uuid4()),
            facility_id=DEFAULT_FACILITY_ID,
            user_name=user_name,
            display_flag=True,
            memo=memo,
        ))

def update_user(user_id: str, user_name: str, display_flag: bool, memo: str = ""):
    with get_engine().begin() as conn:
        conn.execute(update(users).where(users.c.id == user_id).values(
            user_name=user_name,
            display_flag=display_flag,
            memo=memo,
            updated_at=now_jst_dt(),
        ))
