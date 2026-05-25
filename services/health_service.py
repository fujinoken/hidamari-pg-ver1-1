from datetime import date
import pandas as pd
from sqlalchemy import select, insert, desc
from db.migrations import get_engine, init_db
from db.schema import health_records, excretion_records, handover_records, residents


def _engine_ready():
    return init_db()


def list_residents():
    engine = _engine_ready()
    with engine.begin() as conn:
        rows = conn.execute(select(residents).where(residents.c.is_active == True)).mappings().all()
    return [dict(r) for r in rows]


def add_health_record(data: dict):
    engine = _engine_ready()
    with engine.begin() as conn:
        conn.execute(insert(health_records).values(**data))


def add_excretion_record(data: dict):
    engine = _engine_ready()
    with engine.begin() as conn:
        conn.execute(insert(excretion_records).values(**data))


def add_handover_record(data: dict):
    engine = _engine_ready()
    with engine.begin() as conn:
        conn.execute(insert(handover_records).values(**data))


def list_health_records(limit: int = 30):
    engine = _engine_ready()
    stmt = select(health_records).order_by(desc(health_records.c.record_date), desc(health_records.c.id)).limit(limit)
    return pd.read_sql(stmt, engine)


def list_excretion_records(limit: int = 30):
    engine = _engine_ready()
    stmt = select(excretion_records).order_by(desc(excretion_records.c.record_date), desc(excretion_records.c.id)).limit(limit)
    return pd.read_sql(stmt, engine)


def list_handover_records(limit: int = 30):
    engine = _engine_ready()
    stmt = select(handover_records).order_by(desc(handover_records.c.record_date), desc(handover_records.c.id)).limit(limit)
    return pd.read_sql(stmt, engine)
