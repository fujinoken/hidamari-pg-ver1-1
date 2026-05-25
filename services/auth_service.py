import uuid
from sqlalchemy import select
from db.connection import get_engine
from db.schema import users
from config.settings import DEFAULT_FACILITY_ID


def _row_to_dict(row):
    return dict(row._mapping) if row else None


def login(login_id: str, password: str):
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            select(users).where(users.c.login_id == login_id, users.c.password == password, users.c.is_active == 1)
        ).first()
    return _row_to_dict(row)


def list_users(facility_id: str = DEFAULT_FACILITY_ID):
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            select(users.c.id, users.c.login_id, users.c.display_name, users.c.role, users.c.is_active)
            .where(users.c.facility_id == facility_id)
            .order_by(users.c.display_name)
        ).fetchall()
    return [dict(r._mapping) for r in rows]


def create_user(login_id: str, password: str, display_name: str, role: str = "staff", facility_id: str = DEFAULT_FACILITY_ID):
    engine = get_engine()
    try:
        with engine.begin() as conn:
            conn.execute(users.insert().values(
                id=str(uuid.uuid4()), facility_id=facility_id, login_id=login_id,
                password=password, display_name=display_name, user_name=display_name,
                role=role, is_active=1,
            ))
        return True, "登録しました"
    except Exception as e:
        return False, f"登録できませんでした: {e}"
