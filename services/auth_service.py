from sqlalchemy import select
from db.migrations import get_engine
from db.schema import users


def login(login_id: str, password: str):
    engine = get_engine()
    with engine.begin() as conn:
        row = conn.execute(
            select(users).where(users.c.login_id == login_id, users.c.password == password, users.c.is_active == True)
        ).mappings().first()
    return dict(row) if row else None
