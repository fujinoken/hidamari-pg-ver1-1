from sqlalchemy import text
from db.migrations import get_engine

def login(login_id: str, password: str):
    engine = get_engine()
    with engine.begin() as conn:
        row = conn.execute(
            text("""
                SELECT id, login_id, display_name, role
                FROM staff_accounts
                WHERE login_id = :login_id
                  AND password = :password
                  AND COALESCE(is_active, TRUE) = TRUE
                LIMIT 1
            """),
            {"login_id": login_id, "password": password},
        ).mappings().first()
    return dict(row) if row else None
