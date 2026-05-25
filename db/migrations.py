from __future__ import annotations

import bcrypt
from sqlalchemy import text

from config.settings import DEFAULT_FACILITY_ID, DEFAULT_FACILITY_NAME
from db.connection import get_engine
from db.schema import metadata


def table_exists(conn, table_name: str) -> bool:
    result = conn.execute(
        text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = :table_name
        """),
        {"table_name": table_name},
    ).fetchone()
    return result is not None


def ensure_column(conn, table_name: str, column_name: str, column_def: str) -> None:
    if not table_exists(conn, table_name):
        return

    exists = conn.execute(
        text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = :table_name
              AND column_name = :column_name
        """),
        {"table_name": table_name, "column_name": column_name},
    ).fetchone()

    if not exists:
        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}"))


def ensure_index(conn, index_name: str, sql: str) -> None:
    exists = conn.execute(
        text("""
            SELECT indexname
            FROM pg_indexes
            WHERE schemaname = 'public'
              AND indexname = :index_name
        """),
        {"index_name": index_name},
    ).fetchone()

    if not exists:
        conn.execute(text(sql))


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def seed_default_facility(conn) -> None:
    if not table_exists(conn, "facilities"):
        return

    exists = conn.execute(
        text("SELECT id FROM facilities WHERE id = :id"),
        {"id": DEFAULT_FACILITY_ID},
    ).fetchone()

    if not exists:
        conn.execute(
            text("""
                INSERT INTO facilities (id, name)
                VALUES (:id, :name, 'active')
            """),
            {"id": DEFAULT_FACILITY_ID, "name": DEFAULT_FACILITY_NAME},
        )


def seed_default_users(conn) -> None:
    if not table_exists(conn, "users"):
        return

    default_users = [
        ("kanri", "管理者", "admin"),
        ("staff", "職員", "staff"),
    ]

    for login_id, display_name, role in default_users:
        exists = conn.execute(
            text("SELECT id FROM users WHERE login_id = :login_id"),
            {"login_id": login_id},
        ).fetchone()

        if not exists:
            conn.execute(
                text("""
                    INSERT INTO users
                        (facility_id, login_id, display_name, role, password_hash,
                         must_change_password, is_active)
                    VALUES
                        (:facility_id, :login_id, :display_name, :role, :password_hash,
                         true, true)
                """),
                {
                    "facility_id": DEFAULT_FACILITY_ID,
                    "login_id": login_id,
                    "display_name": display_name,
                    "role": role,
                    "password_hash": hash_password("rui"),
                },
            )


def seed_default_residents(conn) -> None:
    if not table_exists(conn, "residents"):
        return

    default_names = [
        "さくら様",
        "谷様",
        "磯崎様",
        "川上様",
        "和波様",
        "桜井様",
        "國枝様",
        "中野様",
        "山口様",
    ]

    for name in default_names:
        exists = conn.execute(
            text("""
                SELECT id
                FROM residents
                WHERE facility_id = :facility_id
                  AND name = :name
            """),
            {"facility_id": DEFAULT_FACILITY_ID, "name": name},
        ).fetchone()

        if not exists:
            conn.execute(
                text("""
                    INSERT INTO residents (facility_id, name, is_visible)
                    VALUES (:facility_id, :name, true)
                """),
                {"facility_id": DEFAULT_FACILITY_ID, "name": name},
            )


def apply_existing_db_migrations(conn) -> None:
    # users
    ensure_column(conn, "users", "facility_id", "INTEGER DEFAULT 1")
    ensure_column(conn, "users", "is_active", "BOOLEAN DEFAULT true")
    ensure_column(conn, "users", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    ensure_column(conn, "users", "updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

    # residents
    ensure_column(conn, "residents", "facility_id", "INTEGER DEFAULT 1")
    ensure_column(conn, "residents", "is_visible", "BOOLEAN DEFAULT true")
    ensure_column(conn, "residents", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    ensure_column(conn, "residents", "updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

    # health_records
    ensure_column(conn, "health_records", "facility_id", "INTEGER DEFAULT 1")
    ensure_column(conn, "health_records", "updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

    # excretion_records
    ensure_column(conn, "excretion_records", "facility_id", "INTEGER DEFAULT 1")
    ensure_column(conn, "excretion_records", "updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

    # handover_records
    ensure_column(conn, "handover_records", "facility_id", "INTEGER DEFAULT 1")
    ensure_column(conn, "handover_records", "updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

    # audit_logs
    ensure_column(conn, "audit_logs", "facility_id", "INTEGER DEFAULT 1")

    # backup系
    ensure_column(conn, "backup_logs", "facility_id", "INTEGER DEFAULT 1")
    ensure_column(conn, "backup_history", "facility_id", "INTEGER DEFAULT 1")

    for table_name in [
        "users",
        "residents",
        "health_records",
        "excretion_records",
        "handover_records",
        "audit_logs",
        "backup_logs",
        "backup_history",
    ]:
        if table_exists(conn, table_name):
            conn.execute(
                text(f"""
                    UPDATE {table_name}
                    SET facility_id = :facility_id
                    WHERE facility_id IS NULL
                """),
                {"facility_id": DEFAULT_FACILITY_ID},
            )

    if table_exists(conn, "users"):
        ensure_index(conn, "idx_users_facility_id", "CREATE INDEX idx_users_facility_id ON users (facility_id)")

    if table_exists(conn, "residents"):
        ensure_index(conn, "idx_residents_facility_id", "CREATE INDEX idx_residents_facility_id ON residents (facility_id)")

    if table_exists(conn, "health_records"):
        ensure_index(conn, "idx_health_facility_date", "CREATE INDEX idx_health_facility_date ON health_records (facility_id, record_date)")

    if table_exists(conn, "excretion_records"):
        ensure_index(conn, "idx_excretion_facility_date", "CREATE INDEX idx_excretion_facility_date ON excretion_records (facility_id, record_date)")

    if table_exists(conn, "handover_records"):
        ensure_index(conn, "idx_handover_facility_date", "CREATE INDEX idx_handover_facility_date ON handover_records (facility_id, record_date)")


def init_db(seed: bool = True) -> None:
    engine = get_engine()

    with engine.begin() as conn:
        metadata.create_all(bind=conn)
        apply_existing_db_migrations(conn)

        if seed:
            seed_default_facility(conn)
            seed_default_users(conn)
            seed_default_residents(conn)
