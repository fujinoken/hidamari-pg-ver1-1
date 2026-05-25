from __future__ import annotations
from sqlalchemy import select
from db.migrations import get_engine
from db.schema import staff_accounts

def login(login_id: str, password: str):
    engine = get_engine()
    with engine.begin() as conn:
        row = conn.execute(
            select(staff_accounts).where(
                staff_accounts.c.login_id == login_id,
                staff_accounts.c.password == password,
                staff_accounts.c.is_active == True,
            )
        ).mappings().first()
    return dict(row) if row else None
