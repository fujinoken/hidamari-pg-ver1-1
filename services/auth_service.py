from sqlalchemy import text
from db.connection import engine


def login(login_id: str, password: str):
    """Login without boolean/integer comparisons. is_active is checked in Python."""
    with engine.begin() as conn:
        row = conn.execute(text("""
            SELECT id, facility_id, login_id, password, staff_name, role, is_active
            FROM staff_accounts
            WHERE login_id = :login_id AND password = :password
            LIMIT 1
        """), {"login_id": login_id, "password": password}).mappings().first()
    if not row:
        return None
    active = row.get("is_active")
    if str(active).lower() in {"false", "0", "none"}:
        return None
    return dict(row)
