from sqlalchemy import create_engine, text
from config.settings import get_database_url, DEFAULT_ADMIN_ID, DEFAULT_ADMIN_PASSWORD, DEFAULT_FACILITY_ID
from db.schema import metadata
import uuid

def get_engine():
    return create_engine(get_database_url(), pool_pre_ping=True, future=True)

def _safe_execute(conn, sql: str):
    try:
        conn.execute(text(sql))
    except Exception:
        # 既存DB差異がある場合でもアプリを止めない
        pass

def _is_postgres(engine) -> bool:
    return engine.dialect.name.startswith("postgresql")

def _is_sqlite(engine) -> bool:
    return engine.dialect.name.startswith("sqlite")

def init_db():
    """
    DB定義を全体統一。
    Neon/PostgreSQLに古いDB構造が残っている場合も、
    不足列追加・TEXT型への寄せ直しを行う。
    """
    engine = get_engine()

    # 新規テーブル作成
    metadata.create_all(engine)

    with engine.begin() as conn:
        if _is_postgres(engine):
            # 旧DBの型不一致対策：id/user_id/login_id/facility_id は TEXT に寄せる
            # 失敗しても、後段のSELECTではCASTして読むので止めない
            alter_sqls = [
                "ALTER TABLE users ALTER COLUMN id TYPE TEXT USING id::text",
                "ALTER TABLE users ALTER COLUMN facility_id TYPE TEXT USING facility_id::text",
                "ALTER TABLE users ALTER COLUMN user_code TYPE TEXT USING user_code::text",
                "ALTER TABLE users ALTER COLUMN user_name TYPE TEXT USING user_name::text",
                "ALTER TABLE health_records ALTER COLUMN id TYPE TEXT USING id::text",
                "ALTER TABLE health_records ALTER COLUMN facility_id TYPE TEXT USING facility_id::text",
                "ALTER TABLE health_records ALTER COLUMN user_id TYPE TEXT USING user_id::text",
                "ALTER TABLE staff_accounts ALTER COLUMN id TYPE TEXT USING id::text",
                "ALTER TABLE staff_accounts ALTER COLUMN facility_id TYPE TEXT USING facility_id::text",
                "ALTER TABLE staff_accounts ALTER COLUMN login_id TYPE TEXT USING login_id::text",
            ]
            for sql in alter_sqls:
                _safe_execute(conn, sql)

            # 不足列の追加
            add_columns = [
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS facility_id TEXT DEFAULT 'default'",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS user_code TEXT DEFAULT ''",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS user_name TEXT DEFAULT ''",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE",
                "ALTER TABLE staff_accounts ADD COLUMN IF NOT EXISTS facility_id TEXT DEFAULT 'default'",
                "ALTER TABLE staff_accounts ADD COLUMN IF NOT EXISTS login_id TEXT DEFAULT 'admin'",
                "ALTER TABLE staff_accounts ADD COLUMN IF NOT EXISTS password TEXT DEFAULT 'admin'",
                "ALTER TABLE staff_accounts ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'admin'",
                "ALTER TABLE staff_accounts ADD COLUMN IF NOT EXISTS display_name TEXT DEFAULT '管理者'",
                "ALTER TABLE staff_accounts ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE",
                "ALTER TABLE health_records ADD COLUMN IF NOT EXISTS facility_id TEXT DEFAULT 'default'",
                "ALTER TABLE health_records ADD COLUMN IF NOT EXISTS record_date DATE",
                "ALTER TABLE health_records ADD COLUMN IF NOT EXISTS user_id TEXT",
                "ALTER TABLE health_records ADD COLUMN IF NOT EXISTS temperature DOUBLE PRECISION",
                "ALTER TABLE health_records ADD COLUMN IF NOT EXISTS bp_high DOUBLE PRECISION",
                "ALTER TABLE health_records ADD COLUMN IF NOT EXISTS bp_low DOUBLE PRECISION",
                "ALTER TABLE health_records ADD COLUMN IF NOT EXISTS pulse DOUBLE PRECISION",
                "ALTER TABLE health_records ADD COLUMN IF NOT EXISTS spo2 DOUBLE PRECISION",
                "ALTER TABLE health_records ADD COLUMN IF NOT EXISTS weight DOUBLE PRECISION",
                "ALTER TABLE health_records ADD COLUMN IF NOT EXISTS meal_rate DOUBLE PRECISION",
                "ALTER TABLE health_records ADD COLUMN IF NOT EXISTS memo TEXT",
            ]
            for sql in add_columns:
                _safe_execute(conn, sql)

        elif _is_sqlite(engine):
            # SQLiteはADD COLUMN IF NOT EXISTS不可。PRAGMA確認して不足列だけ追加。
            def sqlite_cols(table):
                rows = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
                return {r[1] for r in rows}
            for table, cols in {
                "users": [
                    ("facility_id", "TEXT DEFAULT 'default'"),
                    ("user_code", "TEXT DEFAULT ''"),
                    ("user_name", "TEXT DEFAULT ''"),
                    ("is_active", "BOOLEAN DEFAULT 1"),
                ],
                "health_records": [
                    ("facility_id", "TEXT DEFAULT 'default'"),
                    ("record_date", "DATE"),
                    ("user_id", "TEXT"),
                    ("temperature", "FLOAT"),
                    ("bp_high", "FLOAT"),
                    ("bp_low", "FLOAT"),
                    ("pulse", "FLOAT"),
                    ("spo2", "FLOAT"),
                    ("weight", "FLOAT"),
                    ("meal_rate", "FLOAT"),
                    ("memo", "TEXT"),
                ],
            }.items():
                existing = sqlite_cols(table)
                for name, typ in cols:
                    if name not in existing:
                        _safe_execute(conn, f"ALTER TABLE {table} ADD COLUMN {name} {typ}")

        # 管理者アカウント作成
        exists = conn.execute(
            text("SELECT COUNT(*) FROM staff_accounts WHERE login_id = :login_id"),
            {"login_id": DEFAULT_ADMIN_ID},
        ).scalar()
        if not exists:
            conn.execute(
                text("""
                    INSERT INTO staff_accounts
                    (id, facility_id, login_id, password, role, display_name, is_active)
                    VALUES
                    (:id, :facility_id, :login_id, :password, 'admin', '管理者', true)
                """),
                {
                    "id": str(uuid.uuid4()),
                    "facility_id": DEFAULT_FACILITY_ID,
                    "login_id": DEFAULT_ADMIN_ID,
                    "password": DEFAULT_ADMIN_PASSWORD,
                },
            )

    return engine
