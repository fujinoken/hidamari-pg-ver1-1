from sqlalchemy import create_engine
from config.settings import DATABASE_URL

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(DATABASE_URL, future=True)
    return _engine
