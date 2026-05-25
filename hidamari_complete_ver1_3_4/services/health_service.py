from sqlalchemy import select, desc
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from db.connection import get_engine
from db.schema import health_records, excretion_records, users
from config.settings import DEFAULT_FACILITY_ID


def _dict_rows(rows):
    return [dict(r._mapping) for r in rows]


def upsert_health_record(data: dict):
    engine = get_engine()
    stmt = sqlite_insert(health_records).values(
        facility_id=data.get("facility_id", DEFAULT_FACILITY_ID),
        user_id=data["user_id"],
        record_date=str(data["record_date"]),
        temperature=data.get("temperature"),
        blood_pressure_high=data.get("blood_pressure_high"),
        blood_pressure_low=data.get("blood_pressure_low"),
        pulse=data.get("pulse"),
        spo2=data.get("spo2"),
        weight=data.get("weight"),
        meal_rate=data.get("meal_rate"),
        memo=data.get("memo"),
        created_by=data.get("created_by"),
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["facility_id", "user_id", "record_date"],
        set_={
            "temperature": stmt.excluded.temperature,
            "blood_pressure_high": stmt.excluded.blood_pressure_high,
            "blood_pressure_low": stmt.excluded.blood_pressure_low,
            "pulse": stmt.excluded.pulse,
            "spo2": stmt.excluded.spo2,
            "weight": stmt.excluded.weight,
            "meal_rate": stmt.excluded.meal_rate,
            "memo": stmt.excluded.memo,
        },
    )
    with engine.begin() as conn:
        conn.execute(stmt)


def list_health_records(limit: int = 200, facility_id: str = DEFAULT_FACILITY_ID):
    engine = get_engine()
    stmt = (
        select(health_records, users.c.display_name)
        .select_from(health_records.outerjoin(users, health_records.c.user_id == users.c.id))
        .where(health_records.c.facility_id == facility_id)
        .order_by(desc(health_records.c.record_date), users.c.display_name)
        .limit(limit)
    )
    with engine.connect() as conn:
        rows = conn.execute(stmt).fetchall()
    return _dict_rows(rows)


def upsert_excretion_record(data: dict):
    engine = get_engine()
    stmt = sqlite_insert(excretion_records).values(
        facility_id=data.get("facility_id", DEFAULT_FACILITY_ID),
        user_id=data["user_id"],
        record_date=str(data["record_date"]),
        urine_count=data.get("urine_count", 0),
        stool_count=data.get("stool_count", 0),
        stool_status=data.get("stool_status"),
        memo=data.get("memo"),
        created_by=data.get("created_by"),
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["facility_id", "user_id", "record_date"],
        set_={
            "urine_count": stmt.excluded.urine_count,
            "stool_count": stmt.excluded.stool_count,
            "stool_status": stmt.excluded.stool_status,
            "memo": stmt.excluded.memo,
        },
    )
    with engine.begin() as conn:
        conn.execute(stmt)


def list_excretion_records(limit: int = 200, facility_id: str = DEFAULT_FACILITY_ID):
    engine = get_engine()
    stmt = (
        select(excretion_records, users.c.display_name)
        .select_from(excretion_records.outerjoin(users, excretion_records.c.user_id == users.c.id))
        .where(excretion_records.c.facility_id == facility_id)
        .order_by(desc(excretion_records.c.record_date), users.c.display_name)
        .limit(limit)
    )
    with engine.connect() as conn:
        rows = conn.execute(stmt).fetchall()
    return _dict_rows(rows)
