from __future__ import annotations

from db.connection import get_session
from db.schema import User
from utils.text_utils import stable_user_code


def list_users(include_hidden: bool = False):
    session = get_session()
    try:
        q = session.query(User)
        if not include_hidden:
            q = q.filter(User.is_visible == True)  # noqa: E712
        return q.order_by(User.id.asc()).all()
    finally:
        session.close()


def list_user_options():
    return [(u.id, u.display_name) for u in list_users()]


def create_user(display_name: str, basic_info: str = "", living_status: str = "", notes: str = "") -> User:
    session = get_session()
    try:
        user = User(
            user_code=stable_user_code(display_name),
            display_name=display_name.strip(),
            basic_info=basic_info,
            living_status=living_status,
            notes=notes,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def update_user(user_id: int, **kwargs) -> None:
    session = get_session()
    try:
        user = session.query(User).get(user_id)
        if not user:
            raise ValueError("利用者が見つかりません。")
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
