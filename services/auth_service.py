from __future__ import annotations

import hashlib
import secrets
from db.connection import get_session
from db.schema import StaffAccount
from utils.time_utils import now_jst_dt


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000).hex()
    return f"pbkdf2_sha256${salt}${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        method, salt, digest = stored_hash.split("$", 2)
        if method != "pbkdf2_sha256":
            return False
        check = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000).hex()
        return secrets.compare_digest(check, digest)
    except Exception:
        return False


def authenticate(login_id: str, password: str):
    session = get_session()
    try:
        account = session.query(StaffAccount).filter(StaffAccount.login_id == login_id.strip().lower()).first()
        if not account or not account.is_active:
            return None
        if not verify_password(password, account.password_hash):
            return None
        account.last_login_at = now_jst_dt()
        session.commit()
        return {
            "id": account.id,
            "login_id": account.login_id,
            "display_name": account.display_name,
            "role": account.role,
            "must_change_password": account.must_change_password,
        }
    finally:
        session.close()


def change_password(account_id: int, new_password: str) -> None:
    if len(new_password) < 8 or not any(c.isdigit() for c in new_password) or not any(c.isalpha() for c in new_password):
        raise ValueError("パスワードは8文字以上で、英字と数字を含めてください。")
    session = get_session()
    try:
        account = session.query(StaffAccount).get(account_id)
        if not account:
            raise ValueError("アカウントが見つかりません。")
        account.password_hash = hash_password(new_password)
        account.must_change_password = False
        account.updated_at = now_jst_dt()
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
