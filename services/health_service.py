from sqlalchemy import text
from db.database import get_engine, fetch_columns, is_postgres
from config.settings import DEFAULT_FACILITY_ID
import uuid

def _fid(facility_id=None):
    return facility_id or DEFAULT_FACILITY_ID

def _active_sql(alias=""):
    col = f"{alias}.is_active" if alias else "is_active"
    return f"COALESCE(CAST({col} AS TEXT), 'true') IN ('true','TRUE','t','1')"

def _num(value):
    if value in ("", None):
        return None
    try:
        return float(value)
    except Exception:
        return None

def create_user(user_name, user_code="", facility_id=None):
    engine = get_engine()
    with engine.begin() as conn:
        cols = fetch_columns(conn, "users")
        id_type = (cols.get("id") or "").lower()
        active_value = True if is_postgres(conn.get_bind()) else 1

        # 同名＋同施設の重複登録を軽く防止
        existing = conn.execute(text("""
            SELECT CAST(id AS TEXT) FROM users
            WHERE COALESCE(facility_id, 'default')=:facility_id
              AND user_name=:user_name
            LIMIT 1
        """), {"facility_id": _fid(facility_id), "user_name": user_name}).scalar()
        if existing:
            return str(existing)

        if "int" in id_type:
            user_id = conn.execute(text("SELECT COALESCE(MAX(id) + 1, 1) FROM users")).scalar()
        else:
            user_id = str(uuid.uuid4())

        conn.execute(text("""
            INSERT INTO users (id, facility_id, user_code, user_name, is_active)
            VALUES (:id, :facility_id, :user_code, :user_name, :is_active)
        """), {
            "id": user_id,
            "facility_id": _fid(facility_id),
            "user_code": user_code,
            "user_name": user_name,
            "is_active": active_value,
        })
        return str(user_id)

def list_users(facility_id=None, active_only=True):
    sql = """
        SELECT CAST(id AS TEXT) AS id,
               COALESCE(user_code, '') AS user_code,
               COALESCE(user_name, '') AS user_name,
               is_active
        FROM users
        WHERE COALESCE(facility_id, 'default') = :facility_id
    """
    if active_only:
        sql += f" AND {_active_sql()}"
    sql += " ORDER BY user_name"

    with get_engine().connect() as conn:
        return [dict(r) for r in conn.execute(text(sql), {"facility_id": _fid(facility_id)}).mappings().all()]

def save_health_record(data, facility_id=None):
    payload = {
        "facility_id": _fid(facility_id),
        "user_id": str(data.get("user_id")),
        "record_date": str(data.get("record_date")),
        "temperature": _num(data.get("temperature")),
        "bp_high": _num(data.get("bp_high")),
        "bp_low": _num(data.get("bp_low")),
        "pulse": _num(data.get("pulse")),
        "spo2": _num(data.get("spo2")),
        "weight": _num(data.get("weight")),
        "meal_rate": _num(data.get("meal_rate")),
        "memo": data.get("memo") or "",
    }

    with get_engine().begin() as conn:
        conn.execute(text("""
            INSERT INTO health_records
            (facility_id, user_id, record_date, temperature, bp_high, bp_low, pulse, spo2, weight, meal_rate, memo)
            VALUES
            (:facility_id, :user_id, :record_date, :temperature, :bp_high, :bp_low, :pulse, :spo2, :weight, :meal_rate, :memo)
        """), payload)

def update_health_record(record_id, data, facility_id=None):
    payload = {
        "id": record_id,
        "facility_id": _fid(facility_id),
        "user_id": str(data.get("user_id")),
        "record_date": str(data.get("record_date")),
        "temperature": _num(data.get("temperature")),
        "bp_high": _num(data.get("bp_high")),
        "bp_low": _num(data.get("bp_low")),
        "pulse": _num(data.get("pulse")),
        "spo2": _num(data.get("spo2")),
        "weight": _num(data.get("weight")),
        "meal_rate": _num(data.get("meal_rate")),
        "memo": data.get("memo") or "",
    }

    with get_engine().begin() as conn:
        conn.execute(text("""
            UPDATE health_records
            SET user_id=:user_id,
                record_date=:record_date,
                temperature=:temperature,
                bp_high=:bp_high,
                bp_low=:bp_low,
                pulse=:pulse,
                spo2=:spo2,
                weight=:weight,
                meal_rate=:meal_rate,
                memo=:memo,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=:id AND COALESCE(facility_id, 'default')=:facility_id
        """), payload)

def delete_health_record(record_id, facility_id=None):
    with get_engine().begin() as conn:
        conn.execute(text("""
            DELETE FROM health_records
            WHERE id=:id AND COALESCE(facility_id, 'default')=:facility_id
        """), {"id": record_id, "facility_id": _fid(facility_id)})

def list_health_records(facility_id=None, user_id=None, start_date=None, end_date=None, keyword=None, limit=200):
    params = {"facility_id": _fid(facility_id), "limit": int(limit)}
    where = ["COALESCE(h.facility_id, 'default') = :facility_id"]

    if user_id:
        where.append("CAST(h.user_id AS TEXT) = :user_id")
        params["user_id"] = str(user_id)
    if start_date:
        where.append("CAST(h.record_date AS TEXT) >= :start_date")
        params["start_date"] = str(start_date)
    if end_date:
        where.append("CAST(h.record_date AS TEXT) <= :end_date")
        params["end_date"] = str(end_date)
    if keyword:
        where.append("(LOWER(COALESCE(u.user_name, '')) LIKE LOWER(:keyword) OR LOWER(COALESCE(h.memo, '')) LIKE LOWER(:keyword))")
        params["keyword"] = f"%{keyword}%"

    sql = f"""
        SELECT
            h.id,
            CAST(h.record_date AS TEXT) AS record_date,
            CAST(h.user_id AS TEXT) AS user_id,
            COALESCE(u.user_name, '') AS user_name,
            h.temperature,
            h.bp_high,
            h.bp_low,
            h.pulse,
            h.spo2,
            h.weight,
            h.meal_rate,
            h.memo
        FROM health_records h
        LEFT JOIN users u
          ON CAST(h.user_id AS TEXT) = CAST(u.id AS TEXT)
        WHERE {' AND '.join(where)}
        ORDER BY CAST(h.record_date AS TEXT) DESC, h.id DESC
        LIMIT :limit
    """
    with get_engine().connect() as conn:
        return [dict(r) for r in conn.execute(text(sql), params).mappings().all()]

def today_input_status(target_date, facility_id=None):
    users = list_users(facility_id)
    records = list_health_records(
        facility_id=facility_id,
        start_date=str(target_date),
        end_date=str(target_date),
        limit=1000
    )
    done_ids = {str(r["user_id"]) for r in records}
    return [
        {"利用者名": u["user_name"], "入力状況": "入力済み" if str(u["id"]) in done_ids else "未入力"}
        for u in users
    ]
