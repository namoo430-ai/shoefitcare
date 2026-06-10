"""
파일럿 진단·주문 추적 (SQLite)
"""

from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime
from typing import Any, Optional

from pilot_engine import (
    PILOT_RULE_VERSION,
    STRETCH_CODES,
    cohort_group,
    evaluate,
    pilot_input_from_dict,
    sf_engine_hint,
)

DB_PATH = os.environ.get("SHOEFITCARE_DB", "data/shoefitcare.db")


def _conn():
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_pilot_tables() -> None:
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS pilot_diagnoses (
                id TEXT PRIMARY KEY,
                diagnosis_code TEXT NOT NULL,
                created_at TEXT NOT NULL,
                channel TEXT,
                product_id TEXT,
                q1 TEXT, q2_json TEXT, q3 TEXT, q4 INTEGER, q5 TEXT,
                recommendation_code TEXT,
                complex_case INTEGER,
                precision_recommended INTEGER,
                precision_completed INTEGER DEFAULT 0,
                left_foot_length_mm REAL, right_foot_length_mm REAL,
                left_foot_width_mm REAL, right_foot_width_mm REAL,
                contact_masked TEXT,
                consent_at TEXT,
                order_no TEXT,
                return_status INTEGER,
                return_reason TEXT,
                actual_work_step INTEGER,
                memo TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS pilot_orders (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                order_no TEXT,
                product_id TEXT,
                has_diagnosis INTEGER DEFAULT 0,
                diagnosis_id TEXT,
                return_status INTEGER,
                return_reason TEXT,
                memo TEXT
            )
        """)
        c.execute(
            "CREATE INDEX IF NOT EXISTS idx_pilot_dx_code ON pilot_diagnoses(diagnosis_code)"
        )
        c.execute("""
            CREATE TABLE IF NOT EXISTS pilot_funnel_events (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                event TEXT NOT NULL,
                product_id TEXT,
                channel TEXT
            )
        """)
        c.execute(
            "CREATE INDEX IF NOT EXISTS idx_pilot_funnel_event ON pilot_funnel_events(event, created_at)"
        )
        c.execute("""
            CREATE TABLE IF NOT EXISTS pilot_photo_daily (
                log_date TEXT PRIMARY KEY,
                photo_count INTEGER NOT NULL DEFAULT 0,
                memo TEXT,
                updated_at TEXT NOT NULL
            )
        """)
        c.commit()
    _ensure_diagnosis_photo_columns()
    _ensure_diagnosis_loop_columns()
    _ensure_funnel_diagnosis_column()


def _ensure_diagnosis_loop_columns() -> None:
    with _conn() as c:
        cols = {row[1] for row in c.execute("PRAGMA table_info(pilot_diagnoses)")}
        if "pilot_rule_version" not in cols:
            c.execute("ALTER TABLE pilot_diagnoses ADD COLUMN pilot_rule_version TEXT")
        if "engine_hint_json" not in cols:
            c.execute("ALTER TABLE pilot_diagnoses ADD COLUMN engine_hint_json TEXT")
        if "precision_selected" not in cols:
            c.execute(
                "ALTER TABLE pilot_diagnoses ADD COLUMN precision_selected INTEGER DEFAULT 0"
            )
        c.commit()


def _ensure_funnel_diagnosis_column() -> None:
    with _conn() as c:
        cols = {row[1] for row in c.execute("PRAGMA table_info(pilot_funnel_events)")}
        if "diagnosis_id" not in cols:
            c.execute("ALTER TABLE pilot_funnel_events ADD COLUMN diagnosis_id TEXT")
        c.execute(
            "CREATE INDEX IF NOT EXISTS idx_pilot_funnel_dx "
            "ON pilot_funnel_events(diagnosis_id, event)"
        )
        c.commit()


def _ensure_diagnosis_photo_columns() -> None:
    with _conn() as c:
        cols = {row[1] for row in c.execute("PRAGMA table_info(pilot_diagnoses)")}
        if "photo_storage_key" not in cols:
            c.execute("ALTER TABLE pilot_diagnoses ADD COLUMN photo_storage_key TEXT")
        if "photo_uploaded_at" not in cols:
            c.execute("ALTER TABLE pilot_diagnoses ADD COLUMN photo_uploaded_at TEXT")
        c.commit()


PILOT_PHOTO_MAX_BYTES = 5 * 1024 * 1024
PILOT_PHOTO_DIR = os.path.join(os.path.dirname(DB_PATH) or ".", "pilot_photos")
PILOT_PHOTO_MIME = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def _next_serial(conn: sqlite3.Connection, prefix: str) -> int:
    row = conn.execute(
        "SELECT COUNT(*) FROM pilot_diagnoses WHERE recommendation_code = ?",
        (prefix,),
    ).fetchone()
    return int(row[0] or 0) + 1


def create_diagnosis(
    payload: dict[str, Any],
    *,
    channel: str = "web",
    product_id: str | None = None,
) -> dict[str, Any]:
    init_pilot_tables()
    inp = pilot_input_from_dict(payload)
    result = evaluate(inp)
    dx_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    prefix = result.recommendation_code
    serial = 0
    with _conn() as c:
        serial = _next_serial(c, prefix)
        diagnosis_code = f"{prefix}-{serial:06d}"
        hint = sf_engine_hint(result.recommendation_code)
        c.execute(
            """
            INSERT INTO pilot_diagnoses (
                id, diagnosis_code, created_at, channel, product_id,
                q1, q2_json, q3, q4, q5,
                recommendation_code, complex_case, precision_recommended,
                pilot_rule_version, engine_hint_json, precision_selected
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                dx_id,
                diagnosis_code,
                now,
                channel,
                product_id,
                inp.q1,
                json.dumps(inp.q2, ensure_ascii=False),
                inp.q3,
                inp.q4,
                inp.q5,
                result.recommendation_code,
                1 if result.complex_case else 0,
                1 if result.precision_recommended else 0,
                PILOT_RULE_VERSION,
                json.dumps(hint, ensure_ascii=False),
                0,
            ),
        )
        c.commit()
    inquiry_copy = f"{result.message}\n\n진단번호: {diagnosis_code}"
    return {
        "id": dx_id,
        "diagnosis_code": diagnosis_code,
        "recommendation_code": result.recommendation_code,
        "complex_case": result.complex_case,
        "precision_recommended": result.precision_recommended,
        "message": result.message,
        "inquiry_copy_text": inquiry_copy,
        "shoe_size": inp.q4,
        "pilot_rule_version": PILOT_RULE_VERSION,
        "engine_hint": hint,
    }


def complete_precision(
    diagnosis_id: str,
    *,
    left_length_cm: float,
    right_length_cm: float,
    left_width_cm: float,
    right_width_cm: float,
    contact: str,
    consent: bool,
) -> dict[str, Any]:
    if not consent:
        raise ValueError("연락처 안내 동의가 필요합니다.")
    init_pilot_tables()
    with _conn() as c:
        row = c.execute(
            "SELECT recommendation_code FROM pilot_diagnoses WHERE id = ?",
            (diagnosis_id,),
        ).fetchone()
        if not row:
            raise ValueError("진단을 찾을 수 없습니다.")
        prev = row[0]
        new_code = prev
        if prev == "SF04":
            new_code = "SF05"
        masked = _mask_contact(contact)
        c.execute(
            """
            UPDATE pilot_diagnoses SET
                precision_completed = 1,
                recommendation_code = ?,
                left_foot_length_mm = ?, right_foot_length_mm = ?,
                left_foot_width_mm = ?, right_foot_width_mm = ?,
                contact_masked = ?, consent_at = ?
            WHERE id = ?
            """,
            (
                new_code,
                left_length_cm * 10,
                right_length_cm * 10,
                left_width_cm * 10,
                right_width_cm * 10,
                masked,
                datetime.now().isoformat(),
                diagnosis_id,
            ),
        )
        c.commit()
    from pilot_engine import _message_for

    return {"recommendation_code": new_code, "message": _message_for(new_code)}


def _mask_contact(contact: str) -> str:
    t = (contact or "").strip()
    if len(t) < 4:
        return "****"
    return t[:3] + "****" + t[-2:]


def save_precision_photo(
    diagnosis_id: str,
    *,
    content: bytes,
    content_type: str,
) -> dict[str, Any]:
    if not diagnosis_id:
        raise ValueError("diagnosis_id가 필요합니다.")
    mime = (content_type or "").split(";")[0].strip().lower()
    if mime not in PILOT_PHOTO_MIME:
        raise ValueError("jpg, png, webp 이미지만 업로드할 수 있습니다.")
    if len(content) > PILOT_PHOTO_MAX_BYTES:
        raise ValueError("이미지는 5MB 이하여야 합니다.")
    if len(content) < 32:
        raise ValueError("이미지 파일이 비어 있습니다.")
    init_pilot_tables()
    with _conn() as c:
        row = c.execute(
            "SELECT precision_completed FROM pilot_diagnoses WHERE id = ?",
            (diagnosis_id,),
        ).fetchone()
        if not row:
            raise ValueError("진단을 찾을 수 없습니다.")
        if int(row[0] or 0) != 1:
            raise ValueError("정밀 진단 접수 후에만 사진을 올릴 수 있습니다.")
    ext = PILOT_PHOTO_MIME[mime]
    storage_key = f"{diagnosis_id}{ext}"
    os.makedirs(PILOT_PHOTO_DIR, exist_ok=True)
    path = os.path.join(PILOT_PHOTO_DIR, storage_key)
    with open(path, "wb") as f:
        f.write(content)
    now = datetime.now().isoformat()
    with _conn() as c:
        c.execute(
            """
            UPDATE pilot_diagnoses SET photo_storage_key = ?, photo_uploaded_at = ?
            WHERE id = ?
            """,
            (storage_key, now, diagnosis_id),
        )
        c.commit()
    return {"ok": True, "photo_uploaded_at": now}


def resolve_precision_photo_path(diagnosis_id: str) -> str | None:
    init_pilot_tables()
    with _conn() as c:
        row = c.execute(
            "SELECT photo_storage_key FROM pilot_diagnoses WHERE id = ?",
            (diagnosis_id,),
        ).fetchone()
        if not row or not row[0]:
            return None
        key = row[0]
    path = os.path.join(PILOT_PHOTO_DIR, key)
    if not os.path.isfile(path):
        return None
    return path


def update_diagnosis(
    diagnosis_id: str,
    fields: dict[str, Any],
) -> None:
    init_pilot_tables()
    allowed = {
        "order_no",
        "return_status",
        "return_reason",
        "actual_work_step",
        "memo",
    }
    sets = []
    vals = []
    for k, v in fields.items():
        if k not in allowed:
            continue
        sets.append(f"{k} = ?")
        vals.append(v)
    if not sets:
        return
    vals.append(diagnosis_id)
    with _conn() as c:
        c.execute(f"UPDATE pilot_diagnoses SET {', '.join(sets)} WHERE id = ?", vals)
        c.commit()


def register_order_no_diagnosis(
    order_no: str,
    *,
    product_id: str | None = None,
    return_status: int | None = None,
    return_reason: str = "",
) -> str:
    init_pilot_tables()
    oid = str(uuid.uuid4())
    with _conn() as c:
        c.execute(
            """
            INSERT INTO pilot_orders (id, created_at, order_no, product_id, has_diagnosis, return_status, return_reason)
            VALUES (?,?,?,?,0,?,?)
            """,
            (oid, datetime.now().isoformat(), order_no, product_id, return_status, return_reason),
        )
        c.commit()
    return oid


def list_diagnoses(
    *,
    q: str = "",
    code: str = "",
    limit: int = 200,
) -> list[dict[str, Any]]:
    init_pilot_tables()
    sql = "SELECT * FROM pilot_diagnoses WHERE 1=1"
    params: list[Any] = []
    if q:
        sql += " AND (diagnosis_code LIKE ? OR order_no LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%"])
    if code:
        sql += " AND recommendation_code = ?"
        params.append(code)
    sql += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    with _conn() as c:
        c.row_factory = sqlite3.Row
        rows = c.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


def return_rate_by_cohort() -> dict[str, Any]:
    """3그룹 반품율: 진단없음 / 진단만 / 진단+발볼늘림"""
    init_pilot_tables()
    groups = {
        "none": {"orders": 0, "returns": 0},
        "diagnosis_only": {"orders": 0, "returns": 0},
        "diagnosis_stretch": {"orders": 0, "returns": 0},
    }
    with _conn() as c:
        c.row_factory = sqlite3.Row
        for row in c.execute(
            "SELECT return_status FROM pilot_orders WHERE order_no IS NOT NULL AND has_diagnosis = 0"
        ):
            groups["none"]["orders"] += 1
            if int(row["return_status"] or 0) == 1:
                groups["none"]["returns"] += 1

        for row in c.execute(
            """
            SELECT recommendation_code, actual_work_step, return_status
            FROM pilot_diagnoses WHERE order_no IS NOT NULL AND order_no != ''
            """
        ):
            g = cohort_group(
                has_diagnosis=True,
                recommendation_code=row["recommendation_code"],
                actual_work_step=row["actual_work_step"],
            )
            groups[g]["orders"] += 1
            if int(row["return_status"] or 0) == 1:
                groups[g]["returns"] += 1

    out = {}
    for name, stat in groups.items():
        o, r = stat["orders"], stat["returns"]
        out[name] = {
            "orders": o,
            "returns": r,
            "return_rate_pct": round(100.0 * r / o, 2) if o else None,
        }
    return out


def kpi_counts() -> dict[str, int]:
    init_pilot_tables()
    with _conn() as c:
        total = c.execute("SELECT COUNT(*) FROM pilot_diagnoses").fetchone()[0]
        by_code = dict(
            c.execute(
                "SELECT recommendation_code, COUNT(*) FROM pilot_diagnoses GROUP BY recommendation_code"
            ).fetchall()
        )
        complex_n = c.execute(
            "SELECT COUNT(*) FROM pilot_diagnoses WHERE complex_case = 1"
        ).fetchone()[0]
        precision_n = c.execute(
            "SELECT COUNT(*) FROM pilot_diagnoses WHERE precision_completed = 1"
        ).fetchone()[0]
        orders_n = c.execute(
            "SELECT COUNT(*) FROM pilot_diagnoses WHERE order_no IS NOT NULL AND order_no != ''"
        ).fetchone()[0]
        returns_n = c.execute(
            "SELECT COUNT(*) FROM pilot_diagnoses WHERE return_status = 1"
        ).fetchone()[0]
    return {
        "total_diagnoses": int(total),
        "sf01": int(by_code.get("SF01", 0)),
        "sf02": int(by_code.get("SF02", 0)),
        "sf03": int(by_code.get("SF03", 0)),
        "sf04": int(by_code.get("SF04", 0)),
        "sf05": int(by_code.get("SF05", 0)),
        "sf00": int(by_code.get("SF00", 0)),
        "complex_case": int(complex_n),
        "precision_completed": int(precision_n),
        "orders_registered": int(orders_n),
        "returns_registered": int(returns_n),
    }


PILOT_FUNNEL_EVENTS = frozenset({
    "detail_view",
    "detail_cta_click",
    "pilot_result_view",
    "pilot_copy_inquiry",
    "precision_form_view",
    "precision_input_started",
    "precision_complete_view",
    "precision_photo_uploaded",
})


def _mark_precision_selected(diagnosis_id: str) -> None:
    dx = (diagnosis_id or "").strip()
    if not dx:
        return
    with _conn() as c:
        c.execute(
            "UPDATE pilot_diagnoses SET precision_selected = 1 WHERE id = ?",
            (dx,),
        )
        c.commit()


def record_funnel_event(
    event: str,
    *,
    product_id: str | None = None,
    channel: str = "html_detail",
    diagnosis_id: str | None = None,
) -> None:
    if event not in PILOT_FUNNEL_EVENTS:
        raise ValueError("invalid event")
    init_pilot_tables()
    pid = (product_id or "").strip()[:64] or None
    ch = (channel or "html_detail").strip()[:32] or "html_detail"
    dx = (diagnosis_id or "").strip()[:64] or None
    with _conn() as c:
        c.execute(
            """
            INSERT INTO pilot_funnel_events (
                id, created_at, event, product_id, channel, diagnosis_id
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (str(uuid.uuid4()), datetime.now().isoformat(), event, pid, ch, dx),
        )
        c.commit()
    if event == "precision_form_view" and dx:
        _mark_precision_selected(dx)


def funnel_kpi() -> dict[str, Any]:
    """상세·정밀 퍼널 + 사진 수신(수기) 집계."""
    init_pilot_tables()
    with _conn() as c:
        def _count(event: str) -> int:
            row = c.execute(
                "SELECT COUNT(*) FROM pilot_funnel_events WHERE event = ?",
                (event,),
            ).fetchone()
            return int(row[0] or 0)

        views = _count("detail_view")
        clicks = _count("detail_cta_click")
        diagnoses_detail = c.execute(
            "SELECT COUNT(*) FROM pilot_diagnoses WHERE channel = 'html_detail'"
        ).fetchone()[0]
        prec_form = _count("precision_form_view")
        prec_input = _count("precision_input_started")
        prec_complete_views = _count("precision_complete_view")
        precision_done = c.execute(
            "SELECT COUNT(*) FROM pilot_diagnoses WHERE precision_completed = 1"
        ).fetchone()[0]
        photo_app = c.execute(
            "SELECT COUNT(*) FROM pilot_diagnoses WHERE photo_storage_key IS NOT NULL AND photo_storage_key != ''"
        ).fetchone()[0]
        photo_total = c.execute(
            "SELECT COALESCE(SUM(photo_count), 0) FROM pilot_photo_daily"
        ).fetchone()[0]
        photo_rows = c.execute(
            """
            SELECT log_date, photo_count, memo, updated_at
            FROM pilot_photo_daily ORDER BY log_date DESC LIMIT 60
            """
        ).fetchall()

    v, cl, dx = int(views), int(clicks), int(diagnoses_detail)
    pf, pi, pcv, pd = int(prec_form), int(prec_input), int(prec_complete_views), int(precision_done)
    photos = int(photo_total)
    photo_app_n = int(photo_app)

    def pct(num: int, den: int) -> float | None:
        if den <= 0:
            return None
        return round(100.0 * num / den, 2)

    return {
        "detail_views": v,
        "detail_cta_clicks": cl,
        "diagnoses_html_detail": dx,
        "click_rate_pct": pct(cl, v),
        "wide_conversion_pct": pct(dx, v),
        "diagnosis_after_click_pct": pct(dx, cl),
        "precision_form_views": pf,
        "precision_input_started": pi,
        "precision_completed": pd,
        "precision_complete_views": pcv,
        "precision_submit_rate_pct": pct(pd, pf),
        "precision_input_to_submit_pct": pct(pd, pi),
        "precision_form_dropoff": max(pf - pd, 0) if pf else 0,
        "precision_photo_app_uploads": photo_app_n,
        "photo_app_after_precision_pct": pct(photo_app_n, pd),
        "photo_received_total": photos,
        "photo_after_precision_pct": pct(photos, pd),
        "photo_combined_after_precision_pct": pct(photo_app_n + photos, pd),
        "photo_daily": [
            {
                "log_date": r[0],
                "photo_count": int(r[1]),
                "memo": r[2] or "",
                "updated_at": r[3],
            }
            for r in photo_rows
        ],
    }


def upsert_photo_daily(log_date: str, photo_count: int, memo: str = "") -> None:
    init_pilot_tables()
    d = (log_date or "").strip()
    if len(d) != 10 or d[4] != "-" or d[7] != "-":
        raise ValueError("log_date는 YYYY-MM-DD 형식이어야 합니다.")
    n = int(photo_count)
    if n < 0:
        raise ValueError("photo_count는 0 이상이어야 합니다.")
    note = (memo or "").strip()[:200]
    now = datetime.now().isoformat()
    with _conn() as c:
        c.execute(
            """
            INSERT INTO pilot_photo_daily (log_date, photo_count, memo, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(log_date) DO UPDATE SET
                photo_count = excluded.photo_count,
                memo = excluded.memo,
                updated_at = excluded.updated_at
            """,
            (d, n, note, now),
        )
        c.commit()
