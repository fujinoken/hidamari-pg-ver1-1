from sqlalchemy import text
from db.migrations import get_engine


def authenticate(login_id: str, password: str):
    with get_engine().begin() as conn:
        row = conn.execute(
            text("SELECT id, facility_id, login_id, name, role FROM users WHERE login_id=:login_id AND password=:password LIMIT 1"),
            {"login_id": login_id, "password": password},
        ).mappings().first()
    return dict(row) if row else None
