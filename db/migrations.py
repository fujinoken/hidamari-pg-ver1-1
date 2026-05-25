from __future__ import annotations

from db.connection import get_engine, get_session
from db.schema import Base, Facility, StaffAccount, User
from services.auth_service import hash_password
from utils.text_utils import stable_user_code

DEFAULT_USERS = [
    "さくら様", "谷様", "磯崎様", "川上様", "和波様", "桜井様", "國枝様", "中野様", "山口様"
]


def init_db(seed: bool = True) -> None:
    engine = get_engine()
    Base.metadata.create_all(engine)
    if seed:
        seed_initial_data()


def seed_initial_data() -> None:
    session = get_session()
    try:
        if session.query(Facility).count() == 0:
            session.add(Facility(name="ひだまり", memo="初期施設"))

        if session.query(StaffAccount).count() == 0:
            session.add_all([
                StaffAccount(
                    login_id="kanri",
                    display_name="管理者",
                    password_hash=hash_password("rui"),
                    role="admin",
                    must_change_password=True,
                ),
                StaffAccount(
                    login_id="staff",
                    display_name="職員",
                    password_hash=hash_password("rui"),
                    role="staff",
                    must_change_password=True,
                ),
            ])

        if session.query(User).count() == 0:
            for name in DEFAULT_USERS:
                session.add(User(user_code=stable_user_code(name), display_name=name, is_visible=True))

        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
