from sqlalchemy import text
import bcrypt

from db.connection import get_engine

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    )

def authenticate(login_id: str, password: str):
    engine = get_engine()

    with engine.begin() as conn:
        user = conn.execute(
            text("""
                SELECT *
                FROM users
                WHERE login_id=:login_id
                AND is_active=true
            """),
            {"login_id": login_id},
        ).mappings().fetchone()

    if not user:
        return None

    if not verify_password(password, user["password_hash"]):
        return None

    return dict(user)
