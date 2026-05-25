from __future__ import annotations

import bcrypt
from sqlalchemy import text

from config.settings import DEFAULT_FACILITY_ID, DEFAULT_FACILITY_NAME
from db.connection import get_engine
from db.schema import metadata


def table_exists(conn, table_name: str) -> bool:
    row = conn.execute(
        text(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = :table_name
            """
        ),
        {"table_name": table_name},
    ).fetchone()
    return row is not None


def column_exists(conn, table_name: str, column_name: str) -> bool:
    if not table_exists(conn, table_name):
        return False

    row = conn.execute(
        text(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = :table_name
              AND column_name = :column_name
            """
        ),
        {"table_name": table_name, "column_name": column_name},
    ).fetchone()
    return row is not None


def column_data_type(conn, table_name: str, column_name: str) -> str:
    if not column_exists(conn, table_name, column_name):
        return ""

    row = conn.execute(
        text(
            """
            SELECT data_type
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = :table_name
              AND column_name = :column_name
            """
        ),
        {"table_name": table_name, "column_name": column_name},
    ).fetchone()
    return str(row[0]) if row else ""


def ensure_column(conn, table_name: str, column_name: str, column_def: str) -> None:
    if not table_exists(conn, table_name):
        return

    if not column_exists(conn, table_name, column_name):
        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}"))


def ensure_index(conn, index_name: str, sql: str) -> None:
    row = conn.execute(
        text(
            """
            SELECT indexname
            FROM pg_indexes
            WHERE schemaname = 'public'
              AND indexname = :index_name
            """
        ),
        {"index_name": index_name},
    ).fetchone()

    if row is None:
        conn.execute(text(sql))


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_fallback_tables(conn) -> None:
    """
    schema.py と同じ方針で最低限テーブルを作る。
    DB定義統一方針:
    - facility_id = TEXT
    - users.id = TEXT
    - login_id = TEXT
    - user_name は互換用の任意列
    """
    conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS facilities (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )

    conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                facility_id TEXT DEFAULT 'facility_default',
                login_id TEXT UNIQUE,
                user_name TEXT,
                display_name TEXT,
                role TEXT DEFAULT 'staff',
                password_hash TEXT,
                must_change_password BOOLEAN DEFAULT true,
                is_active BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )

    conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS residents (
                id SERIAL PRIMARY KEY,
                facility_id TEXT DEFAULT 'facility_default',
                name TEXT NOT NULL,
                is_visible BOOLEAN DEFAULT true,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )

    conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS health_records (
                id SERIAL PRIMARY KEY,
                facility_id TEXT DEFAULT 'facility_default',
                resident_id INTEGER,
                resident_name TEXT,
                record_date DATE,
                temperature NUMERIC,
                bp_high INTEGER,
                bp_low INTEGER,
                pulse INTEGER,
                spo2 INTEGER,
                weight NUMERIC,
                water_ml INTEGER,
                breakfast INTEGER,
                lunch INTEGER,
                dinner INTEGER,
                family_note TEXT,
                change_note TEXT,
                input_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )

    conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS excretion_records (
                id SERIAL PRIMARY KEY,
                facility_id TEXT DEFAULT 'facility_default',
                resident_id INTEGER,
                resident_name TEXT,
                record_date DATE,
                time_slot TEXT,
                urine_amount TEXT,
                urine_status TEXT,
                stool_amount TEXT,
                stool_status TEXT,
                memo TEXT,
                input_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )

    conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS handover_records (
                id SERIAL PRIMARY KEY,
                facility_id TEXT DEFAULT 'facility_default',
                record_date DATE,
                shift TEXT,
                writer TEXT,
                fact TEXT,
                notice TEXT,
                next_watch TEXT,
                priority TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )

    conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS audit_logs (
                id SERIAL PRIMARY KEY,
                facility_id TEXT DEFAULT 'facility_default',
                login_id TEXT,
                role TEXT,
                action TEXT,
                table_name TEXT,
                target_id TEXT,
                summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )

    conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS backup_logs (
                id SERIAL PRIMARY KEY,
                facility_id TEXT DEFAULT 'facility_default',
                backup_type TEXT,
                file_name TEXT,
                memo TEXT,
                created_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )


def apply_existing_db_migrations(conn) -> None:
    """
    既存DBが途中状態でも落ちにくい補修。
    ただし本番前はNeon DBをリセットし、schema.pyから作り直す運用を推奨。
    """
    ensure_column(conn, "facilities", "name", "TEXT")
    ensure_column(conn, "facilities", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    ensure_column(conn, "facilities", "updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

    ensure_column(conn, "users", "facility_id", "TEXT DEFAULT 'facility_default'")
    ensure_column(conn, "users", "login_id", "TEXT")
    ensure_column(conn, "users", "user_name", "TEXT")
    ensure_column(conn, "users", "display_name", "TEXT")
    ensure_column(conn, "users", "role", "TEXT DEFAULT 'staff'")
    ensure_column(conn, "users", "password_hash", "TEXT")
    ensure_column(conn, "users", "must_change_password", "BOOLEAN DEFAULT true")
    ensure_column(conn, "users", "is_active", "BOOLEAN DEFAULT true")
    ensure_column(conn, "users", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    ensure_column(conn, "users", "updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

    ensure_column(conn, "residents", "facility_id", "TEXT DEFAULT 'facility_default'")
    ensure_column(conn, "residents", "name", "TEXT")
    ensure_column(conn, "residents", "is_visible", "BOOLEAN DEFAULT true")
    ensure_column(conn, "residents", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    ensure_column(conn, "residents", "updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

    ensure_column(conn, "health_records", "facility_id", "TEXT DEFAULT 'facility_default'")
    ensure_column(conn, "health_records", "resident_id", "INTEGER")
    ensure_column(conn, "health_records", "resident_name", "TEXT")
    ensure_column(conn, "health_records", "record_date", "DATE")
    ensure_column(conn, "health_records", "temperature", "NUMERIC")
    ensure_column(conn, "health_records", "bp_high", "INTEGER")
    ensure_column(conn, "health_records", "bp_low", "INTEGER")
    ensure_column(conn, "health_records", "pulse", "INTEGER")
    ensure_column(conn, "health_records", "spo2", "INTEGER")
    ensure_column(conn, "health_records", "weight", "NUMERIC")
    ensure_column(conn, "health_records", "water_ml", "INTEGER")
    ensure_column(conn, "health_records", "breakfast", "INTEGER")
    ensure_column(conn, "health_records", "lunch", "INTEGER")
    ensure_column(conn, "health_records", "dinner", "INTEGER")
    ensure_column(conn, "health_records", "family_note", "TEXT")
    ensure_column(conn, "health_records", "change_note", "TEXT")
    ensure_column(conn, "health_records", "input_by", "TEXT")
    ensure_column(conn, "health_records", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    ensure_column(conn, "health_records", "updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

    ensure_column(conn, "excretion_records", "facility_id", "TEXT DEFAULT 'facility_default'")
    ensure_column(conn, "excretion_records", "resident_id", "INTEGER")
    ensure_column(conn, "excretion_records", "resident_name", "TEXT")
    ensure_column(conn, "excretion_records", "record_date", "DATE")
    ensure_column(conn, "excretion_records", "time_slot", "TEXT")
    ensure_column(conn, "excretion_records", "urine_amount", "TEXT")
    ensure_column(conn, "excretion_records", "urine_status", "TEXT")
    ensure_column(conn, "excretion_records", "stool_amount", "TEXT")
    ensure_column(conn, "excretion_records", "stool_status", "TEXT")
    ensure_column(conn, "excretion_records", "memo", "TEXT")
    ensure_column(conn, "excretion_records", "input_by", "TEXT")
    ensure_column(conn, "excretion_records", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    ensure_column(conn, "excretion_records", "updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

    ensure_column(conn, "handover_records", "facility_id", "TEXT DEFAULT 'facility_default'")
    ensure_column(conn, "handover_records", "record_date", "DATE")
    ensure_column(conn, "handover_records", "shift", "TEXT")
    ensure_column(conn, "handover_records", "writer", "TEXT")
    ensure_column(conn, "handover_records", "fact", "TEXT")
    ensure_column(conn, "handover_records", "notice", "TEXT")
    ensure_column(conn, "handover_records", "next_watch", "TEXT")
    ensure_column(conn, "handover_records", "priority", "TEXT")
    ensure_column(conn, "handover_records", "status", "TEXT")
    ensure_column(conn, "handover_records", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    ensure_column(conn, "handover_records", "updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

    ensure_column(conn, "audit_logs", "facility_id", "TEXT DEFAULT 'facility_default'")
    ensure_column(conn, "audit_logs", "login_id", "TEXT")
    ensure_column(conn, "audit_logs", "role", "TEXT")
    ensure_column(conn, "audit_logs", "action", "TEXT")
    ensure_column(conn, "audit_logs", "table_name", "TEXT")
    ensure_column(conn, "audit_logs", "target_id", "TEXT")
    ensure_column(conn, "audit_logs", "summary", "TEXT")
    ensure_column(conn, "audit_logs", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

    ensure_column(conn, "backup_logs", "facility_id", "TEXT DEFAULT 'facility_default'")
    ensure_column(conn, "backup_logs", "backup_type", "TEXT")
    ensure_column(conn, "backup_logs", "file_name", "TEXT")
    ensure_column(conn, "backup_logs", "memo", "TEXT")
    ensure_column(conn, "backup_logs", "created_by", "TEXT")
    ensure_column(conn, "backup_logs", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

    for table_name in [
        "users",
        "residents",
        "health_records",
        "excretion_records",
        "handover_records",
        "audit_logs",
        "backup_logs",
    ]:
        if table_exists(conn, table_name) and column_exists(conn, table_name, "facility_id"):
            conn.execute(
                text(
                    f"""
                    UPDATE {table_name}
                    SET facility_id = :facility_id
                    WHERE facility_id IS NULL
                    """
                ),
                {"facility_id": str(DEFAULT_FACILITY_ID)},
            )

    # 互換列 user_name がある場合は login_id で補完
    if table_exists(conn, "users"):
        if column_exists(conn, "users", "user_name") and column_exists(conn, "users", "login_id"):
            conn.execute(
                text(
                    """
                    UPDATE users
                    SET user_name = login_id
                    WHERE user_name IS NULL
                    """
                )
            )

        ensure_index(conn, "idx_users_facility_id", "CREATE INDEX idx_users_facility_id ON users (facility_id)")
        ensure_index(conn, "idx_users_login_id", "CREATE INDEX idx_users_login_id ON users (login_id)")

    if table_exists(conn, "residents"):
        ensure_index(conn, "idx_residents_facility_id", "CREATE INDEX idx_residents_facility_id ON residents (facility_id)")
        ensure_index(conn, "idx_residents_name", "CREATE INDEX idx_residents_name ON residents (name)")

    if table_exists(conn, "health_records"):
        ensure_index(conn, "idx_health_facility_date", "CREATE INDEX idx_health_facility_date ON health_records (facility_id, record_date)")
        ensure_index(conn, "idx_health_resident_date", "CREATE INDEX idx_health_resident_date ON health_records (resident_id, record_date)")

    if table_exists(conn, "excretion_records"):
        ensure_index(conn, "idx_excretion_facility_date", "CREATE INDEX idx_excretion_facility_date ON excretion_records (facility_id, record_date)")
        ensure_index(conn, "idx_excretion_resident_date", "CREATE INDEX idx_excretion_resident_date ON excretion_records (resident_id, record_date)")

    if table_exists(conn, "handover_records"):
        ensure_index(conn, "idx_handover_facility_date", "CREATE INDEX idx_handover_facility_date ON handover_records (facility_id, record_date)")


def seed_default_facility(conn) -> None:
    if not table_exists(conn, "facilities"):
        return

    exists = conn.execute(
        text("SELECT id FROM facilities WHERE id = :id"),
        {"id": str(DEFAULT_FACILITY_ID)},
    ).fetchone()

    if exists:
        return

    conn.execute(
        text(
            """
            INSERT INTO facilities (id, name)
            VALUES (:id, :name)
            """
        ),
        {
            "id": str(DEFAULT_FACILITY_ID),
            "name": DEFAULT_FACILITY_NAME,
        },
    )


def seed_default_users(conn) -> None:
    if not table_exists(conn, "users"):
        return

    default_users = [
        {
            "id": "kanri",
            "login_id": "kanri",
            "user_name": "kanri",
            "display_name": "管理者",
            "role": "admin",
            "password": "rui",
        },
        {
            "id": "staff",
            "login_id": "staff",
            "user_name": "staff",
            "display_name": "職員",
            "role": "staff",
            "password": "rui",
        },
    ]

    for user in default_users:
        exists = conn.execute(
            text("SELECT id FROM users WHERE login_id = :login_id"),
            {"login_id": user["login_id"]},
        ).fetchone()

        if exists:
            continue

        conn.execute(
            text(
                """
                INSERT INTO users
                    (id, facility_id, login_id, user_name, display_name, role, password_hash,
                     must_change_password, is_active)
                VALUES
                    (:id, :facility_id, :login_id, :user_name, :display_name, :role, :password_hash,
                     true, true)
                """
            ),
            {
                "id": user["id"],
                "facility_id": str(DEFAULT_FACILITY_ID),
                "login_id": user["login_id"],
                "user_name": user["user_name"],
                "display_name": user["display_name"],
                "role": user["role"],
                "password_hash": hash_password(user["password"]),
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
            text(
                """
                SELECT id
                FROM residents
                WHERE facility_id = :facility_id
                  AND name = :name
                """
            ),
            {
                "facility_id": str(DEFAULT_FACILITY_ID),
                "name": name,
            },
        ).fetchone()

        if exists:
            continue

        conn.execute(
            text(
                """
                INSERT INTO residents (facility_id, name, is_visible)
                VALUES (:facility_id, :name, true)
                """
            ),
            {
                "facility_id": str(DEFAULT_FACILITY_ID),
                "name": name,
            },
        )


def init_db(seed: bool = True) -> None:
    engine = get_engine()

    with engine.begin() as conn:
        # schema.pyで定義された統一DB構造を作成
        metadata.create_all(bind=conn)

        # 万一schema.pyで作られない場合の保険
        create_fallback_tables(conn)

        # 既存DBが残っている場合の補修
        apply_existing_db_migrations(conn)

        if seed:
            seed_default_facility(conn)
            seed_default_users(conn)
            seed_default_residents(conn)
