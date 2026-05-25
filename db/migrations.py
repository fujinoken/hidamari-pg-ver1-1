from __future__ import annotations

import bcrypt
from sqlalchemy import text

from config.settings import DEFAULT_FACILITY_ID, DEFAULT_FACILITY_NAME
from db.connection import get_engine
from db.schema import metadata


def table_exists(conn, table_name: str) -> bool:
    row = conn.execute(
        text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public'
            AND table_name=:table_name
        """),
        {"table_name": table_name},
    ).fetchone()
    return row is not None


def ensure_column(conn, table_name: str, column_name: str, column_def: str):
    if not table_exists(conn, table_name):
        return

    exists = conn.execute(
        text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema='public'
            AND table_name=:table_name
            AND column_name=:column_name
        """),
        {"table_name": table_name, "column_name": column_name},
    ).fetchone()

    if not exists:
        conn.execute(
            text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")
        )


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def create_tables(conn):
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS facilities (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            facility_id TEXT,
            login_id TEXT UNIQUE,
            user_name TEXT,
            display_name TEXT,
            role TEXT,
            password_hash TEXT,
            is_active BOOLEAN DEFAULT true
        )
    """))

    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS residents (
            id SERIAL PRIMARY KEY,
            facility_id TEXT,
            name TEXT NOT NULL
        )
    """))


def migrate_existing_tables(conn):
    ensure_column(conn, "users", "facility_id", "TEXT")
    ensure_column(conn, "users", "login_id", "TEXT")
    ensure_column(conn, "users", "user_name", "TEXT")
    ensure_column(conn, "users", "display_name", "TEXT")
    ensure_column(conn, "users", "role", "TEXT")
    ensure_column(conn, "users", "password_hash", "TEXT")
    ensure_column(conn, "users", "is_active", "BOOLEAN DEFAULT true")


def seed_default_facility(conn):
    exists = conn.execute(
        text("SELECT id FROM facilities WHERE id=:id"),
        {"id": DEFAULT_FACILITY_ID},
    ).fetchone()

    if exists:
        return

    conn.execute(
        text("""
            INSERT INTO facilities (id, name)
            VALUES (:id, :name)
        """),
        {
            "id": DEFAULT_FACILITY_ID,
            "name": DEFAULT_FACILITY_NAME,
        },
    )


def seed_default_users(conn):
    users = [
        {
            "id": "kanri",
            "login_id": "kanri",
            "display_name": "管理者",
            "role": "admin",
            "password": "rui",
        },
        {
            "id": "staff",
            "login_id": "staff",
            "display_name": "職員",
            "role": "staff",
            "password": "rui",
        },
    ]

    for user in users:
        exists = conn.execute(
            text("""
                SELECT id
                FROM users
                WHERE login_id=:login_id
            """),
            {"login_id": user["login_id"]},
        ).fetchone()

        if exists:
            continue

        conn.execute(
            text("""
                INSERT INTO users (
                    id,
                    facility_id,
                    login_id,
                    user_name,
                    display_name,
                    role,
                    password_hash,
                    is_active
                )
                VALUES (
                    :id,
                    :facility_id,
                    :login_id,
                    :user_name,
                    :display_name,
                    :role,
                    :password_hash,
                    true
                )
            """),
            {
                "id": user["id"],
                "facility_id": DEFAULT_FACILITY_ID,
                "login_id": user["login_id"],
                "user_name": user["login_id"],
                "display_name": user["display_name"],
                "role": user["role"],
                "password_hash": hash_password(user["password"]),
            },
        )


def init_db(seed: bool = True):
    engine = get_engine()

    with engine.begin() as conn:
        metadata.create_all(bind=conn)

        create_tables(conn)
        migrate_existing_tables(conn)

        if seed:
            seed_default_facility(conn)
            seed_default_users(conn)
