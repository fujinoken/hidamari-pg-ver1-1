import uuid
from sqlalchemy import select, func
from db.connection import get_engine
from db.schema import metadata, users
from config.settings import DEFAULT_FACILITY_ID, DEFAULT_ADMIN_LOGIN_ID, DEFAULT_ADMIN_PASSWORD


def init_db():
    engine = get_engine()
    metadata.create_all(engine)
    with engine.begin() as conn:
        count = conn.execute(select(func.count()).select_from(users).where(users.c.login_id == DEFAULT_ADMIN_LOGIN_ID)).scalar_one()
        if count == 0:
            conn.execute(users.insert().values(
                id=str(uuid.uuid4()),
                facility_id=DEFAULT_FACILITY_ID,
                login_id=DEFAULT_ADMIN_LOGIN_ID,
                password=DEFAULT_ADMIN_PASSWORD,
                display_name="管理者",
                user_name="管理者",
                role="admin",
                is_active=1,
            ))


def get_conn():
    # 互換用：SQLAlchemy接続を返します
    return get_engine().connect()


def reset_db_for_debug():
    engine = get_engine()
    metadata.drop_all(engine)
    init_db()
