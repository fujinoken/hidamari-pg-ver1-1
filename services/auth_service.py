from __future__ import annotations

import bcrypt
from sqlalchemy import text

from config.settings import DEFAULT_FACILITY_ID
from db.connection import hidamari_db_connection


def verify_password(password: str, password_hash: str) -> bool:
    if not password_hash:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        return False


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def authenticate(login_id: str, password: str) -> dict | None:
    """
    ログイン認証。
    DB定義統一方針:
    - login_id を正式ログインIDとして使用
    - user_name は互換列。ログイン検索では login_id を優先し、必要に応じて user_name も許容。
    """
    login_id = (login_id or "").strip()
    if not login_id or not password:
        return None

    with hidamari_db_connection() as conn:
        row = conn.execute(
            text(
                """
                SELECT
                    id,
                    facility_id,
                    login_id,
                    user_name,
                    display_name,
                    role,
                    password_hash,
                    must_change_password,
                    is_active
                FROM users
                WHERE (login_id = :login_id OR user_name = :login_id)
                  AND COALESCE(is_active, true) = true
                LIMIT 1
                """
            ),
            {"login_id": login_id},
        ).mappings().fetchone()

    if not row:
        return None

    data = dict(row)
    if not verify_password(password, data.get("password_hash", "")):
        return None

    return {
        "id": data.get("id"),
        "facility_id": data.get("facility_id") or str(DEFAULT_FACILITY_ID),
        "login_id": data.get("login_id") or data.get("user_name"),
        "user_name": data.get("user_name"),
        "display_name": data.get("display_name") or data.get("login_id"),
        "role": data.get("role") or "staff",
        "must_change_password": bool(data.get("must_change_password")),
        "is_active": bool(data.get("is_active", True)),
    }


def change_password(user_id: str, new_password: str) -> None:
    if not user_id:
        raise ValueError("ユーザーIDが確認できません。")
    if not new_password or len(new_password) < 4:
        raise ValueError("パスワードは4文字以上で入力してください。")

    new_hash = hash_password(new_password)

    with hidamari_db_connection() as conn:
        conn.execute(
            text(
                """
                UPDATE users
                SET password_hash = :password_hash,
                    must_change_password = false,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :id
                """
            ),
            {"password_hash": new_hash, "id": str(user_id)},
        )


def is_admin_user(user: dict | None) -> bool:
    if not user:
        return False
    return user.get("role") == "admin"


def current_facility_id(user: dict | None) -> str:
    if user and user.get("facility_id"):
        return str(user["facility_id"])
    return str(DEFAULT_FACILITY_ID)
