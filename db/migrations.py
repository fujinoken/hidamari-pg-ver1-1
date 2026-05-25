
from __future__ import annotations
import uuid
import bcrypt
from sqlalchemy import select, insert, text
from db.connection import get_engine
from db.schema import metadata, facilities, staff_accounts, users
from config.settings import DEFAULT_FACILITY_ID, DEFAULT_FACILITY_NAME
from utils.time_utils import now_jst

DEFAULT_USERS = ["さくら様", "谷様", "磯崎様", "川上様", "和波様", "桜井様", "國枝様", "中野様", "山口様"]

def _hash_pw(pw: str) -> str:
    return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def init_db(seed: bool = True):
    engine = get_engine()
    metadata.create_all(engine)
    with engine.begin() as conn:
        # 互換用：古いDBに列がない場合だけ追加
        for sql in [
            "ALTER TABLE health_records ADD COLUMN IF NOT EXISTS updated_by VARCHAR(64) DEFAULT ''",
            "ALTER TABLE excretion_records ADD COLUMN IF NOT EXISTS updated_by VARCHAR(64) DEFAULT ''",
            "ALTER TABLE handover_logs ADD COLUMN IF NOT EXISTS updated_by VARCHAR(64) DEFAULT ''",
        ]:
            try:
                conn.execute(text(sql))
            except Exception:
                pass

    if not seed:
        return

    with engine.begin() as conn:
        exists = conn.execute(select(facilities.c.id).where(facilities.c.id == DEFAULT_FACILITY_ID)).first()
        if not exists:
            conn.execute(insert(facilities).values(id=DEFAULT_FACILITY_ID, name=DEFAULT_FACILITY_NAME))

        staff_count = conn.execute(select(staff_accounts.c.id).limit(1)).first()
        if not staff_count:
            conn.execute(insert(staff_accounts), [
                {
                    "id": str(uuid.uuid4()),
                    "facility_id": DEFAULT_FACILITY_ID,
                    "login_id": "kanri",
                    "display_name": "管理者",
                    "password_hash": _hash_pw("rui"),
                    "role": "admin",
                    "active": True,
                    "must_change_password": True,
                },
                {
                    "id": str(uuid.uuid4()),
                    "facility_id": DEFAULT_FACILITY_ID,
                    "login_id": "staff",
                    "display_name": "職員",
                    "password_hash": _hash_pw("rui"),
                    "role": "staff",
                    "active": True,
                    "must_change_password": True,
                },
            ])

        user_count = conn.execute(select(users.c.id).where(users.c.facility_id == DEFAULT_FACILITY_ID).limit(1)).first()
        if not user_count:
            conn.execute(insert(users), [
                {
                    "id": str(uuid.uuid4()),
                    "facility_id": DEFAULT_FACILITY_ID,
                    "user_name": name,
                    "display_flag": True,
                    "memo": "",
                }
                for name in DEFAULT_USERS
            ])
