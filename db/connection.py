
from __future__ import annotations
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from config.settings import require_database_url

_ENGINE: Engine | None = None

def get_engine() -> Engine:
    global _ENGINE
    if _ENGINE is None:
        url = require_database_url()
        _ENGINE = create_engine(
            url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            future=True,
        )
    return _ENGINE
