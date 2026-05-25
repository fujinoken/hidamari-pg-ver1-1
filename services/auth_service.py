from sqlalchemy import text
from db.connection import get_engine

def login(login_id: str, password: str):
    engine = get_engine()
    with engine.begin() as conn:
        row = conn.execute(text("""
            SELECT id, facility_id, login_id, staff_name, role
            FROM staff_accounts
            WHERE login_id = :login_id
              AND password = :password
              AND (is_active = TRUE OR is_active = 1)
            LIMIT 1
        """), {"login_id": login_id, "password": password}).mappings().first()
        return dict(row) if row else None
