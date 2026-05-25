from sqlalchemy import text
from db.migrations import get_engine
from config.settings import DEFAULT_FACILITY_ID

def login(login_id: str, password: str):
    engine = get_engine()
    with engine.begin() as conn:
        row = conn.execute(
            text("""
                SELECT id, facility_id, login_id, role, display_name
                FROM staff_accounts
                WHERE login_id = :login_id
                  AND password = :password
                  AND COALESCE(is_active, true) = true
                LIMIT 1
            """),
            {"login_id": login_id, "password": password},
        ).mappings().first()

    return dict(row) if row else None

def ensure_session_defaults(st):
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "facility_id" not in st.session_state:
        st.session_state.facility_id = DEFAULT_FACILITY_ID
    if "role" not in st.session_state:
        st.session_state.role = "admin"
    if "display_name" not in st.session_state:
        st.session_state.display_name = "管理者"
