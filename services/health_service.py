from __future__ import annotations

import datetime as dt
import pandas as pd
from sqlalchemy import select, insert, update, delete
from db.migrations import get_engine
from db.schema import health_records, excretion_records, residents, users

def list_residents(facility_id: str = "default"):
    engine = get_engine()
    with engine.begin() as conn:
        rows = conn.execute(
            select(residents).where(
                residents.c.facility_id == facility_id,
                residents.c.is_active == True,
            ).order_by(residents.c.name)
        ).mappings().all()
    return [dict(r) for r in rows]

def upsert_health_record(data: dict):
    engine = get_engine()
    with engine.begin() as conn:
        existing = conn.execute(
            select(health_records.c.id).where(
                health_records.c.facility_id == data["facility_id"],
                health_records.c.resident_id == data["resident_id"],
                health_records.c.record_date == data["record_date"],
            )
        ).first()
        if existing:
            conn.execute(update(health_records).where(health_records.c.id == existing[0]).values(**data))
            return existing[0]
        res = conn.execute(insert(health_records).values(**data))
        return res.inserted_primary_key[0]

def get_health_records(facility_id: str = "default", limit: int = 100):
    engine = get_engine()
    with engine.begin() as conn:
        rows = conn.execute(
            select(health_records, residents.c.name.label("resident_name"))
            .join(residents, residents.c.id == health_records.c.resident_id)
            .where(health_records.c.facility_id == facility_id)
            .order_by(health_records.c.record_date.desc(), residents.c.name)
            .limit(limit)
        ).mappings().all()
    return pd.DataFrame([dict(r) for r in rows])

def upsert_excretion_record(data: dict):
    engine = get_engine()
    with engine.begin() as conn:
        existing = conn.execute(
            select(excretion_records.c.id).where(
                excretion_records.c.facility_id == data["facility_id"],
                excretion_records.c.resident_id == data["resident_id"],
                excretion_records.c.record_date == data["record_date"],
            )
        ).first()
        if existing:
            conn.execute(update(excretion_records).where(excretion_records.c.id == existing[0]).values(**data))
            return existing[0]
        res = conn.execute(insert(excretion_records).values(**data))
        return res.inserted_primary_key[0]

def get_excretion_records(facility_id: str = "default", limit: int = 100):
    engine = get_engine()
    with engine.begin() as conn:
        rows = conn.execute(
            select(excretion_records, residents.c.name.label("resident_name"))
            .join(residents, residents.c.id == excretion_records.c.resident_id)
            .where(excretion_records.c.facility_id == facility_id)
            .order_by(excretion_records.c.record_date.desc(), residents.c.name)
            .limit(limit)
        ).mappings().all()
    return pd.DataFrame([dict(r) for r in rows])
