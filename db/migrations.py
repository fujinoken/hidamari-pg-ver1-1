from __future__ import annotations

import os
import uuid
from sqlalchemy import create_engine, select, insert
from config.settings import DB_PATH, ADMIN_LOGIN_ID, ADMIN_PASSWORD, DEFAULT_FACILITY_ID
from db.schema import metadata, facilities, users, residents

def get_engine():
    return create_engine(f"sqlite:///{DB_PATH}", future=True)

def init_db():
    engine = get_engine()
    metadata.create_all(engine)

    with engine.begin() as conn:
        facility = conn.execute(
            select(facilities.c.id).where(facilities.c.id == DEFAULT_FACILITY_ID)
        ).first()
        if facility is None:
            conn.execute(insert(facilities).values(id=DEFAULT_FACILITY_ID, name="ひだまり"))

        admin = conn.execute(
            select(users.c.id).where(users.c.login_id == ADMIN_LOGIN_ID)
        ).first()
        if admin is None:
            conn.execute(insert(users).values(
                id="admin",
                facility_id=DEFAULT_FACILITY_ID,
                login_id=ADMIN_LOGIN_ID,
                password=ADMIN_PASSWORD,
                display_name="管理者",
                user_name="管理者",
                role="admin",
                is_active=True,
            ))

        # 初期利用者サンプル。不要なら画面から無効化・削除ではなく非表示運用推奨。
        sample = conn.execute(select(residents.c.id).where(residents.c.name == "さくら")).first()
        if sample is None:
            conn.execute(insert(residents).values(
                id="resident-sakura",
                facility_id=DEFAULT_FACILITY_ID,
                name="さくら",
                room="",
                is_active=True,
            ))
    return engine
