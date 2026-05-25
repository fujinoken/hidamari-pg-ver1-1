from sqlalchemy import create_engine, select, insert
from config.settings import DB_PATH, DEFAULT_ADMIN_ID, DEFAULT_ADMIN_PASSWORD
from db.schema import metadata, users, residents


def get_engine():
    return create_engine(f"sqlite:///{DB_PATH}", future=True)


def init_db():
    engine = get_engine()
    metadata.create_all(engine)
    with engine.begin() as conn:
        admin = conn.execute(select(users).where(users.c.login_id == DEFAULT_ADMIN_ID)).first()
        if admin is None:
            conn.execute(insert(users).values(
                id="admin", login_id=DEFAULT_ADMIN_ID, password=DEFAULT_ADMIN_PASSWORD,
                name="管理者", role="admin", is_active=True
            ))
        # 初期利用者。不要なら画面上では後で拡張できます。
        for rid, name in [("sakura", "さくら"), ("taro", "たろう")]:
            exists = conn.execute(select(residents).where(residents.c.id == rid)).first()
            if exists is None:
                conn.execute(insert(residents).values(id=rid, name=name, room="", is_active=True))
    return engine
