from sqlalchemy import text
from db.database import get_engine

def login(login_id: str, password: str):
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT CAST(id AS TEXT) AS id,
                   COALESCE(facility_id, 'default') AS facility_id,
                   login_id,
                   COALESCE(staff_name, login_id) AS staff_name,
                   COALESCE(role, 'staff') AS role
            FROM staff_accounts
            WHERE login_id = :login_id
              AND password = :password
              AND COALESCE(CAST(is_active AS TEXT), 'true') IN ('true','TRUE','t','1')
            LIMIT 1
        """), {"login_id": login_id, "password": password}).mappings().first()
    return dict(row) if row else None

def logout(st):
    for key in ["logged_in", "account", "facility_id", "staff_name", "role"]:
        if key in st.session_state:
            del st.session_state[key]
