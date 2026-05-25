
from __future__ import annotations
import bcrypt
from sqlalchemy import select, update
from db.connection import get_engine
from db.schema import staff_accounts
from config.settings import DEFAULT_FACILITY_ID
from utils.time_utils import now_jst_dt

def authenticate(login_id: str, password: str) -> dict | None:
    login_id = (login_id or "").strip()
    password = password or ""
    if not login_id or not password:
        return None
    with get_engine().begin() as conn:
        row = conn.execute(
            select(staff_accounts).where(
                staff_accounts.c.facility_id == DEFAULT_FACILITY_ID,
                staff_accounts.c.login_id == login_id,
                staff_accounts.c.active == True,
            )
        ).mappings().first()
        if not row:
            return None
        ok = bcrypt.checkpw(password.encode("utf-8"), row["password_hash"].encode("utf-8"))
        if not ok:
            return None
        return dict(row)

def change_password(staff_id: str, new_password: str):
    if not new_password or len(new_password) < 4:
        raise ValueError("パスワードは4文字以上にしてください。")
    hashed = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    with get_engine().begin() as conn:
        conn.execute(
            update(staff_accounts)
            .where(staff_accounts.c.id == staff_id)
            .values(password_hash=hashed, must_change_password=False, updated_at=now_jst_dt())
        )

def is_admin(user: dict) -> bool:
    return (user or {}).get("role") == "admin"

def require_admin(user: dict):
    if not is_admin(user):
        raise PermissionError("管理者のみ操作できます。")
