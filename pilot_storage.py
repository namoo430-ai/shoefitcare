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

from foot_profile import derive_foot_profile, foot_profile_to_dict
from foot_scores import compute_comfort_bars, compute_ux_scores
from pilot_fit_result import build_fit_result
from pilot_foot_compare import build_foot_compare_view
from pilot_links import naver_product_ops
from pilot_store_links import naver_store_links
from pilot_inquiry import build_naver_diagnosis_result_copy, build_pilot_inquiry_copies
from pilot_engine import (
    PILOT_RULE_VERSION,
    STRETCH_CODES,
    cohort_group,
    evaluate,
    pilot_input_from_dict,
    sf_engine_hint,
)

DB_PATH = os.environ.get("SHOEFITCARE_DB", "data/shoefitcare.db")

STRETCH_WORKSHOP_CODES = frozenset({"SF01", "SF02", "SF03", "SF05"})


def _day_start(d: str | None) -> str | None:
    if not d:
        return None
    s = d.strip()[:10]
    if len(s) != 10:
        return None
    return f"{s}T00:00:00"


def _day_end(d: str | None) -> str | None:
    if not d:
        return None
    s = d.strip()[:10]
    if len(s) != 10:
        return None
    return f"{s}T23:59:59.999999"


def _created_between_sql(
    from_date: str | None,
    to_date: str | None,
    *,
    col: str = "created_at",
) -> tuple[str, list[Any]]:
    parts: list[str] = []
    params: list[Any] = []
    start = _day_start(from_date)
    end = _day_end(to_date)
    if start:
        parts.append(f"{col} >= ?")
        params.append(start)
    if end:
        parts.append(f"{col} <= ?")
        params.append(end)
    if not parts:
        return "", []
    return " AND " + " AND ".join(parts), params


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
        c.execute("""
            CREATE TABLE IF NOT EXISTS pilot_ops_counters (
                counter_key TEXT PRIMARY KEY,
                counter_value INTEGER NOT NULL DEFAULT 0,
                memo TEXT,
                updated_at TEXT NOT NULL
            )
        """)
        c.commit()
    _ensure_diagnosis_photo_columns()
    _ensure_diagnosis_loop_columns()
    _ensure_funnel_diagnosis_column()
    _ensure_foot_profile_columns()


def _ensure_foot_profile_columns() -> None:
    with _conn() as c:
        cols = {row[1] for row in c.execute("PRAGMA table_info(pilot_diagnoses)")}
        if "r_code" not in cols:
            c.execute("ALTER TABLE pilot_diagnoses ADD COLUMN r_code TEXT")
        if "p_code" not in cols:
            c.execute("ALTER TABLE pilot_diagnoses ADD COLUMN p_code TEXT")
        if "s_code" not in cols:
            c.execute("ALTER TABLE pilot_diagnoses ADD COLUMN s_code TEXT")
        if "foot_profile_json" not in cols:
            c.execute("ALTER TABLE pilot_diagnoses ADD COLUMN foot_profile_json TEXT")
        c.execute(
            "CREATE INDEX IF NOT EXISTS idx_pilot_dx_rps "
            "ON pilot_diagnoses(r_code, p_code, s_code)"
        )
        c.commit()


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
    profile = derive_foot_profile(inp.q1, inp.q2, inp.q3)
    ux = compute_ux_scores(
        recommendation_code=result.recommendation_code,
        r_code=profile.r_code,
        p_code=profile.p_code,
        s_code=profile.s_code,
        complex_case=result.complex_case,
        precision_recommended=result.precision_recommended,
    )
    comfort_bars = compute_comfort_bars(
        recommendation_code=result.recommendation_code,
        r_code=profile.r_code,
        p_code=profile.p_code,
        s_code=profile.s_code,
        complex_case=result.complex_case,
        precision_recommended=result.precision_recommended,
    )
    if comfort_bars:
        ux = {**ux, "comfort_bars": comfort_bars}
    profile_dict = foot_profile_to_dict(profile)
    profile_dict.update(ux)
    profile_json = json.dumps(profile_dict, ensure_ascii=False)
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
                pilot_rule_version, engine_hint_json, precision_selected,
                r_code, p_code, s_code, foot_profile_json
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
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
                profile.r_code,
                profile.p_code,
                profile.s_code,
                profile_json,
            ),
        )
        c.commit()
    inquiry = build_pilot_inquiry_copies(
        message=result.message,
        diagnosis_code=diagnosis_code,
        recommendation_code=result.recommendation_code,
        channel=channel,
        shoe_size=inp.q4,
    )
    pid = (product_id or "").strip().upper() or None
    ops = naver_product_ops(pid)
    fit_result = build_fit_result(
        recommendation_code=result.recommendation_code,
        r_code=profile.r_code,
        p_code=profile.p_code,
        s_code=profile.s_code,
        complex_case=result.complex_case,
        shoe_size=inp.q4,
        stretch_on_option=bool(ops.get("stretch_on_option")),
        stretch_option_label=str(ops.get("stretch_option_label") or "발볼 늘림"),
        exchange_event_active=bool(ops.get("exchange_event_active", True)),
        q1=inp.q1,
    )
    foot_compare = build_foot_compare_view(
        r_code=profile.r_code,
        p_code=profile.p_code,
        s_code=profile.s_code,
        q1=inp.q1,
        q2=inp.q2,
        recommendation_code=result.recommendation_code,
    )
    store_links = naver_store_links() if (channel or "").lower().startswith("naver") else None
    return {
        "id": dx_id,
        "diagnosis_code": diagnosis_code,
        "recommendation_code": result.recommendation_code,
        "complex_case": result.complex_case,
        "precision_recommended": result.precision_recommended,
        "message": result.message,
        "inquiry_copy_text": inquiry["inquiry_copy_text"],
        "inquiry_copy_short": inquiry["inquiry_copy_short"],
        "inquiry_copy_naver_exchange": inquiry.get("inquiry_copy_naver_exchange"),
        "channel": channel,
        "shoe_size": inp.q4,
        "pilot_rule_version": PILOT_RULE_VERSION,
        "engine_hint": hint,
        "foot_profile": profile_dict,
        "ux_scores": ux,
        "fit_result": fit_result,
        "foot_compare": foot_compare,
        "product_ops": ops,
        "store_links": store_links,
        "q1": inp.q1,
        "q2": list(inp.q2 or []),
        "naver_diagnosis_copy": (
            build_naver_diagnosis_result_copy(
                diagnosis_code=diagnosis_code,
                recommendation_code=result.recommendation_code,
                shoe_size=inp.q4,
                recommended_fit_line=fit_result.get("recommended_fit_line"),
                fit_recommendation_tip=fit_result.get("fit_recommendation_tip"),
                stretch_recommendation_tip=fit_result.get("stretch_recommendation_tip"),
            )
            if (channel or "").lower().startswith("naver")
            else None
        ),
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
    r_code: str = "",
    p_code: str = "",
    from_date: str | None = None,
    to_date: str | None = None,
    workshop_only: bool = False,
    pending_work_only: bool = False,
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
    if r_code:
        sql += " AND r_code = ?"
        params.append(r_code.strip().upper())
    if p_code:
        sql += " AND p_code = ?"
        params.append(p_code.strip().upper())
    between, bp = _created_between_sql(from_date, to_date)
    sql += between
    params.extend(bp)
    if workshop_only:
        codes = ",".join(f"'{c}'" for c in sorted(STRETCH_WORKSHOP_CODES))
        sql += (
            f" AND (recommendation_code IN ({codes}) OR precision_completed = 1)"
        )
    if pending_work_only:
        sql += " AND actual_work_step IS NULL"
    sql += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    with _conn() as c:
        c.row_factory = sqlite3.Row
        rows = c.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


def get_diagnosis_by_code(diagnosis_code: str) -> dict[str, Any] | None:
    """진단번호 정확 일치 (대소문자 무시)."""
    init_pilot_tables()
    code = (diagnosis_code or "").strip()
    if not code:
        return None
    with _conn() as c:
        c.row_factory = sqlite3.Row
        row = c.execute(
            "SELECT * FROM pilot_diagnoses WHERE diagnosis_code = ? COLLATE NOCASE",
            (code,),
        ).fetchone()
    if not row:
        return None
    d = dict(row)
    d.pop("contact_masked", None)
    fp = d.get("foot_profile_json")
    if fp:
        try:
            d["foot_profile"] = json.loads(fp)
        except json.JSONDecodeError:
            d["foot_profile"] = None
    q2_raw = d.get("q2_json")
    if q2_raw:
        try:
            d["q2"] = json.loads(q2_raw)
        except json.JSONDecodeError:
            d["q2"] = []
    return d


def return_rate_by_cohort(
    *,
    from_date: str | None = None,
    to_date: str | None = None,
) -> dict[str, Any]:
    """3그룹 반품율: 진단없음 / 진단만 / 진단+발볼늘림"""
    init_pilot_tables()
    groups = {
        "none": {"orders": 0, "returns": 0},
        "diagnosis_only": {"orders": 0, "returns": 0},
        "diagnosis_stretch": {"orders": 0, "returns": 0},
    }
    order_between, order_params = _created_between_sql(from_date, to_date)
    dx_between, dx_params = _created_between_sql(from_date, to_date)
    with _conn() as c:
        c.row_factory = sqlite3.Row
        for row in c.execute(
            "SELECT return_status FROM pilot_orders WHERE order_no IS NOT NULL AND has_diagnosis = 0"
            + order_between,
            order_params,
        ):
            groups["none"]["orders"] += 1
            if int(row["return_status"] or 0) == 1:
                groups["none"]["returns"] += 1

        for row in c.execute(
            """
            SELECT recommendation_code, actual_work_step, return_status
            FROM pilot_diagnoses WHERE order_no IS NOT NULL AND order_no != ''
            """
            + dx_between,
            dx_params,
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


RETURN_PRIOR_MIN_ORDERS = 3


def _return_rate_from_rows(rows: list[tuple]) -> tuple[int, int, float | None]:
    orders = len(rows)
    if orders == 0:
        return 0, 0, None
    ret = sum(int(r[0] or 0) for r in rows)
    return orders, ret, round(100.0 * ret / orders, 2)


def return_prior_lookup(
    r_code: str,
    p_code: str,
    s_code: str,
    *,
    product_id: str | None = None,
) -> dict[str, Any]:
    """주문 연결된 진단 코호트로 반품율 추정 (Admin·내부 참고)."""
    init_pilot_tables()
    r, p, s = (r_code or "").upper(), (p_code or "").upper(), (s_code or "").upper()
    pid = (product_id or "").strip() or None
    tiers: list[tuple[str, str, tuple, list]] = []
    if pid:
        tiers.append(
            (
                "rps_product",
                f"R/P/S + SKU ({pid})",
                "r_code=? AND p_code=? AND s_code=? AND product_id=?",
                [r, p, s, pid],
            )
        )
    tiers.extend(
        [
            ("rps", "R/P/S 동일", "r_code=? AND p_code=? AND s_code=?", [r, p, s]),
            ("rp", "R+P 동일", "r_code=? AND p_code=?", [r, p]),
            ("r_only", "R 동일", "r_code=?", [r]),
        ]
    )
    with _conn() as c:
        for tier_id, label, where, args in tiers:
            sql = (
                f"SELECT return_status FROM pilot_diagnoses WHERE order_no IS NOT NULL "
                f"AND order_no != '' AND {where}"
            )
            rows = c.execute(sql, args).fetchall()
            n, ret_n, pct = _return_rate_from_rows(rows)
            if n >= RETURN_PRIOR_MIN_ORDERS:
                return {
                    "tier": tier_id,
                    "tier_label": label,
                    "orders": n,
                    "returns": ret_n,
                    "return_rate_pct": pct,
                    "sufficient": True,
                }
    return {
        "tier": "insufficient",
        "tier_label": "표본 부족",
        "orders": 0,
        "returns": 0,
        "return_rate_pct": None,
        "sufficient": False,
        "min_orders": RETURN_PRIOR_MIN_ORDERS,
    }


def foot_profile_kpi(
    *,
    from_date: str | None = None,
    to_date: str | None = None,
) -> dict[str, Any]:
    init_pilot_tables()
    between, bp = _created_between_sql(from_date, to_date)
    with _conn() as c:
        by_r = dict(c.execute(
            "SELECT r_code, COUNT(*) FROM pilot_diagnoses WHERE r_code IS NOT NULL"
            + between
            + " GROUP BY r_code",
            bp,
        ).fetchall())
        by_p = dict(c.execute(
            "SELECT p_code, COUNT(*) FROM pilot_diagnoses WHERE p_code IS NOT NULL"
            + between
            + " GROUP BY p_code",
            bp,
        ).fetchall())
        by_s = dict(c.execute(
            "SELECT s_code, COUNT(*) FROM pilot_diagnoses WHERE s_code IS NOT NULL"
            + between
            + " GROUP BY s_code",
            bp,
        ).fetchall())
        missing = c.execute(
            "SELECT COUNT(*) FROM pilot_diagnoses WHERE r_code IS NULL OR r_code = ''"
            + between,
            bp,
        ).fetchone()[0]
        prior_sql = (
            """
            SELECT r_code, p_code, s_code,
                   COUNT(*) AS orders,
                   SUM(CASE WHEN return_status = 1 THEN 1 ELSE 0 END) AS returns
            FROM pilot_diagnoses
            WHERE order_no IS NOT NULL AND order_no != ''
              AND r_code IS NOT NULL
            """
            + between
            + """
            GROUP BY r_code, p_code, s_code
            HAVING COUNT(*) >= 1
            ORDER BY orders DESC
            LIMIT 25
            """
        )
        prior_rows = c.execute(prior_sql, bp).fetchall()
    priors = []
    for row in prior_rows:
        r, p, s, o, ret = row[0], row[1], row[2], int(row[3]), int(row[4] or 0)
        priors.append({
            "r_code": r,
            "p_code": p,
            "s_code": s,
            "orders": o,
            "returns": ret,
            "return_rate_pct": round(100.0 * ret / o, 2) if o else None,
            "sufficient": o >= RETURN_PRIOR_MIN_ORDERS,
        })
    return {
        "by_r": {k: int(v) for k, v in by_r.items()},
        "by_p": {k: int(v) for k, v in by_p.items()},
        "by_s": {k: int(v) for k, v in by_s.items()},
        "missing_profile_count": int(missing or 0),
        "return_priors": priors,
        "prior_min_orders": RETURN_PRIOR_MIN_ORDERS,
    }


def backfill_foot_profiles(*, dry_run: bool = True) -> dict[str, int]:
    """r_code 비어 있는 행에 Q1~Q3로 R/P/S 재계산."""
    init_pilot_tables()
    updated = 0
    skipped = 0
    with _conn() as c:
        c.row_factory = sqlite3.Row
        rows = c.execute(
            """
            SELECT id, q1, q2_json, q3, recommendation_code, complex_case,
                   precision_recommended, precision_completed
            FROM pilot_diagnoses
            WHERE r_code IS NULL OR r_code = ''
            """
        ).fetchall()
        for row in rows:
            q2_raw = row["q2_json"]
            try:
                q2 = json.loads(q2_raw) if q2_raw else []
            except json.JSONDecodeError:
                q2 = []
            if not isinstance(q2, list):
                q2 = []
            profile = derive_foot_profile(row["q1"] or "", q2, row["q3"] or "")
            ux = compute_ux_scores(
                recommendation_code=row["recommendation_code"] or "SF00",
                r_code=profile.r_code,
                p_code=profile.p_code,
                s_code=profile.s_code,
                complex_case=bool(row["complex_case"]),
                precision_recommended=bool(row["precision_recommended"]),
                precision_completed=bool(row["precision_completed"]),
            )
            pd = foot_profile_to_dict(profile)
            pd.update(ux)
            if dry_run:
                updated += 1
                continue
            c.execute(
                """
                UPDATE pilot_diagnoses
                SET r_code=?, p_code=?, s_code=?, foot_profile_json=?
                WHERE id=?
                """,
                (profile.r_code, profile.p_code, profile.s_code, json.dumps(pd, ensure_ascii=False), row["id"]),
            )
            updated += 1
        if not dry_run:
            c.commit()
    return {"would_update" if dry_run else "updated": updated, "skipped": skipped}


COUPANG_OPS_KEYS = ("coupang_wing_orders", "coupang_sms_sent", "coupang_inquiry_inbound")
NAVER_OPS_KEYS = ("naver_store_orders", "naver_sms_sent", "naver_talktalk_inbound")
OPS_COUNTER_KEYS = COUPANG_OPS_KEYS + NAVER_OPS_KEYS


def get_ops_counters() -> dict[str, Any]:
    init_pilot_tables()
    out: dict[str, Any] = {}
    with _conn() as c:
        for row in c.execute(
            "SELECT counter_key, counter_value, memo, updated_at FROM pilot_ops_counters"
        ):
            out[row[0]] = {
                "value": int(row[1] or 0),
                "memo": row[2] or "",
                "updated_at": row[3],
            }
    for k in OPS_COUNTER_KEYS:
        out.setdefault(k, {"value": 0, "memo": "", "updated_at": None})
    return out


def upsert_ops_counter(key: str, value: int, memo: str = "") -> None:
    init_pilot_tables()
    k = (key or "").strip()
    if k not in OPS_COUNTER_KEYS:
        raise ValueError("invalid counter key")
    n = int(value)
    if n < 0:
        raise ValueError("counter must be >= 0")
    now = datetime.now().isoformat()
    with _conn() as c:
        c.execute(
            """
            INSERT INTO pilot_ops_counters (counter_key, counter_value, memo, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(counter_key) DO UPDATE SET
                counter_value=excluded.counter_value,
                memo=excluded.memo,
                updated_at=excluded.updated_at
            """,
            (k, n, (memo or "").strip()[:500], now),
        )
        c.commit()


def _funnel_count(
    event: str,
    *,
    channel: str | None = None,
    channel_like: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
) -> int:
    init_pilot_tables()
    sql = "SELECT COUNT(*) FROM pilot_funnel_events WHERE event = ?"
    params: list[Any] = [event]
    if channel:
        sql += " AND channel = ?"
        params.append(channel)
    elif channel_like:
        sql += " AND channel LIKE ?"
        params.append(channel_like)
    between, bp = _created_between_sql(from_date, to_date)
    sql += between
    params.extend(bp)
    with _conn() as c:
        row = c.execute(sql, params).fetchone()
        return int(row[0] or 0)


def list_funnel_events_for_diagnosis(
    diagnosis_id: str,
    *,
    limit: int = 40,
) -> list[dict[str, Any]]:
    init_pilot_tables()
    dx = (diagnosis_id or "").strip()
    if not dx:
        return []
    with _conn() as c:
        c.row_factory = sqlite3.Row
        rows = c.execute(
            """
            SELECT created_at, event, channel, product_id
            FROM pilot_funnel_events
            WHERE diagnosis_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (dx, int(limit)),
        ).fetchall()
    return [dict(r) for r in rows]


def daily_diagnosis_counts(
    *,
    from_date: str | None = None,
    to_date: str | None = None,
    channel_like: str | None = None,
) -> list[dict[str, Any]]:
    init_pilot_tables()
    sql = (
        "SELECT substr(created_at, 1, 10) AS day, COUNT(*) AS n "
        "FROM pilot_diagnoses WHERE 1=1"
    )
    params: list[Any] = []
    if channel_like:
        sql += " AND channel LIKE ?"
        params.append(channel_like)
    between, bp = _created_between_sql(from_date, to_date)
    sql += between
    params.extend(bp)
    sql += " GROUP BY day ORDER BY day"
    with _conn() as c:
        rows = c.execute(sql, params).fetchall()
    return [{"day": r[0], "count": int(r[1])} for r in rows if r[0]]


def coupang_pilot_kpi(
    *,
    from_date: str | None = None,
    to_date: str | None = None,
) -> dict[str, Any]:
    """쿠팡 문자·링크 퍼널 (Wing 수기 카운터 + 자동 진단·랜딩)."""
    init_pilot_tables()
    ops = get_ops_counters()
    wing = ops["coupang_wing_orders"]["value"]
    sms = ops["coupang_sms_sent"]["value"]
    inq = ops["coupang_inquiry_inbound"]["value"]
    with _conn() as c:
        ch_sql = (
            "SELECT channel, COUNT(*) FROM pilot_diagnoses "
            "WHERE channel LIKE 'coupang%'"
        )
        ch_params: list[Any] = []
        between, bp = _created_between_sql(from_date, to_date)
        ch_sql += between + " GROUP BY channel"
        ch_params.extend(bp)
        by_ch = dict(c.execute(ch_sql, ch_params).fetchall())
    dx_sms = int(by_ch.get("coupang_sms", 0))
    land_sms = _funnel_count(
        "pilot_landing", channel="coupang_sms", from_date=from_date, to_date=to_date
    )
    result_sms = _funnel_count(
        "pilot_result_view", channel="coupang_sms", from_date=from_date, to_date=to_date
    )

    def pct(num: int, den: int) -> float | None:
        if den <= 0:
            return None
        return round(100.0 * num / den, 2)

    return {
        "ops": ops,
        "diagnoses_by_channel": {k: int(v) for k, v in by_ch.items()},
        "coupang_sms_diagnoses": dx_sms,
        "coupang_sms_landings": land_sms,
        "coupang_sms_result_views": result_sms,
        "rate_sms_to_landing_pct": pct(land_sms, sms),
        "rate_landing_to_diagnosis_pct": pct(dx_sms, land_sms) if land_sms else pct(dx_sms, sms),
        "rate_wing_to_diagnosis_pct": pct(dx_sms, wing),
        "rate_inquiry_to_diagnosis_pct": pct(dx_sms, inq),
        "note": (
            "Wing 주문·SMS 발송·문의 유입은 Admin 수기 입력. "
            "링크 클릭(랜딩)·진단 완료는 자동. SMS 전량 발송 시 참여율 낮은 것이 흔함 → 문의 선행 권장."
        ),
        "from_date": from_date,
        "to_date": to_date,
    }


def naver_pilot_kpi(
    *,
    from_date: str | None = None,
    to_date: str | None = None,
) -> dict[str, Any]:
    """네이버 스마트스토어·SMS 퍼널 (수기 카운터 + 자동 진단·톡톡 이벤트)."""
    init_pilot_tables()
    ops = get_ops_counters()
    store = ops["naver_store_orders"]["value"]
    sms = ops["naver_sms_sent"]["value"]
    talk_in = ops["naver_talktalk_inbound"]["value"]
    with _conn() as c:
        ch_sql = (
            "SELECT channel, COUNT(*) FROM pilot_diagnoses WHERE channel LIKE 'naver%'"
        )
        ch_params: list[Any] = []
        between, bp = _created_between_sql(from_date, to_date)
        ch_sql += between + " GROUP BY channel"
        ch_params.extend(bp)
        by_ch = dict(c.execute(ch_sql, ch_params).fetchall())
    dx_total = sum(int(v) for v in by_ch.values())
    land = _funnel_count(
        "pilot_landing", channel_like="naver%", from_date=from_date, to_date=to_date
    )
    result_views = _funnel_count(
        "pilot_result_view", channel_like="naver%", from_date=from_date, to_date=to_date
    )
    copy_ex = _funnel_count(
        "pilot_copy_naver_exchange",
        channel_like="naver%",
        from_date=from_date,
        to_date=to_date,
    )
    talk_guide = _funnel_count(
        "talk_guide_open", channel_like="naver%", from_date=from_date, to_date=to_date
    )
    talk_open = _funnel_count(
        "talktalk_open", channel_like="naver%", from_date=from_date, to_date=to_date
    )
    fit_open = _funnel_count(
        "fit_category_open", channel_like="naver%", from_date=from_date, to_date=to_date
    )
    prec_form = _funnel_count(
        "precision_form_view", channel_like="naver%", from_date=from_date, to_date=to_date
    )
    prec_done = _funnel_count(
        "precision_complete_view", channel_like="naver%", from_date=from_date, to_date=to_date
    )

    def pct(num: int, den: int) -> float | None:
        if den <= 0:
            return None
        return round(100.0 * num / den, 2)

    return {
        "ops": {k: ops[k] for k in NAVER_OPS_KEYS},
        "diagnoses_by_channel": {k: int(v) for k, v in by_ch.items()},
        "naver_diagnoses": dx_total,
        "naver_landings": land,
        "naver_result_views": result_views,
        "naver_exchange_copies": copy_ex,
        "talk_guide_open": talk_guide,
        "talktalk_open": talk_open,
        "fit_category_open": fit_open,
        "precision_form_views": prec_form,
        "precision_complete_views": prec_done,
        "rate_sms_to_landing_pct": pct(land, sms),
        "rate_landing_to_diagnosis_pct": pct(dx_total, land) if land else pct(dx_total, sms),
        "rate_store_to_diagnosis_pct": pct(dx_total, store),
        "rate_talk_to_diagnosis_pct": pct(dx_total, talk_in),
        "rate_result_to_copy_pct": pct(copy_ex, result_views),
        "note": (
            "스토어 주문·SMS·톡톡 문의는 Admin 수기. "
            "교환 복사·톡톡 열기·정밀 퍼널은 기간 내 자동 집계."
        ),
        "from_date": from_date,
        "to_date": to_date,
    }


def pilot_storage_meta() -> dict[str, Any]:
    """Admin: DB 용량·기간·Render 에피머럴 경고."""
    init_pilot_tables()
    with _conn() as c:
        n = int(c.execute("SELECT COUNT(*) FROM pilot_diagnoses").fetchone()[0] or 0)
        oldest = c.execute("SELECT MIN(created_at) FROM pilot_diagnoses").fetchone()[0]
        newest = c.execute("SELECT MAX(created_at) FROM pilot_diagnoses").fetchone()[0]
    db_exists = os.path.isfile(DB_PATH)
    size = os.path.getsize(DB_PATH) if db_exists else 0
    return {
        "diagnosis_count": n,
        "oldest_diagnosis_at": oldest,
        "newest_diagnosis_at": newest,
        "db_file_bytes": int(size),
        "db_path_hint": os.path.basename(DB_PATH) or "shoefitcare.db",
        "ephemeral_warning": (
            "Render 무료·재배포·인스턴스 교체 시 SQLite가 비워져 오전 집계(SF01 등)가 0으로 보일 수 있습니다. "
            "Persistent Disk 또는 외부 DB 없이는 서버에만 임시 저장됩니다."
        ),
    }


def kpi_counts(
    *,
    from_date: str | None = None,
    to_date: str | None = None,
) -> dict[str, int]:
    init_pilot_tables()
    between, bp = _created_between_sql(from_date, to_date)
    with _conn() as c:
        total = c.execute(
            "SELECT COUNT(*) FROM pilot_diagnoses WHERE 1=1" + between,
            bp,
        ).fetchone()[0]
        by_code_rows = c.execute(
            "SELECT recommendation_code, COUNT(*) FROM pilot_diagnoses WHERE 1=1"
            + between
            + " GROUP BY recommendation_code",
            bp,
        ).fetchall()
        by_code = dict(by_code_rows)
        complex_n = c.execute(
            "SELECT COUNT(*) FROM pilot_diagnoses WHERE complex_case = 1" + between,
            bp,
        ).fetchone()[0]
        precision_n = c.execute(
            "SELECT COUNT(*) FROM pilot_diagnoses WHERE precision_completed = 1" + between,
            bp,
        ).fetchone()[0]
        orders_n = c.execute(
            "SELECT COUNT(*) FROM pilot_diagnoses WHERE order_no IS NOT NULL AND order_no != ''"
            + between,
            bp,
        ).fetchone()[0]
        returns_n = c.execute(
            "SELECT COUNT(*) FROM pilot_diagnoses WHERE return_status = 1" + between,
            bp,
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
    "pilot_landing",
    "pilot_copy_inquiry",
    "pilot_copy_inquiry_short",
    "pilot_copy_naver_exchange",
    "pilot_result_view",
    "talk_guide_open",
    "talktalk_open",
    "fit_category_open",
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


def funnel_kpi(
    *,
    from_date: str | None = None,
    to_date: str | None = None,
) -> dict[str, Any]:
    """상세·정밀 퍼널 + 사진 수신(수기) 집계."""
    init_pilot_tables()
    between_dx, dx_params = _created_between_sql(from_date, to_date)

    def _count(event: str) -> int:
        return _funnel_count(event, from_date=from_date, to_date=to_date)

    with _conn() as c:
        diagnoses_detail = c.execute(
            "SELECT COUNT(*) FROM pilot_diagnoses WHERE channel = 'html_detail'"
            + between_dx,
            dx_params,
        ).fetchone()[0]
        precision_done = c.execute(
            "SELECT COUNT(*) FROM pilot_diagnoses WHERE precision_completed = 1"
            + between_dx,
            dx_params,
        ).fetchone()[0]
        photo_app = c.execute(
            "SELECT COUNT(*) FROM pilot_diagnoses WHERE photo_storage_key IS NOT NULL "
            "AND photo_storage_key != ''"
            + between_dx,
            dx_params,
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

    views = _count("detail_view")
    clicks = _count("detail_cta_click")
    dx = int(diagnoses_detail)
    pf, pi, pcv, pd = (
        _count("precision_form_view"),
        _count("precision_input_started"),
        _count("precision_complete_view"),
        int(precision_done),
    )
    photos = int(photo_total)
    photo_app_n = int(photo_app)

    def pct(num: int, den: int) -> float | None:
        if den <= 0:
            return None
        return round(100.0 * num / den, 2)

    return {
        "detail_views": views,
        "detail_cta_clicks": clicks,
        "diagnoses_html_detail": dx,
        "click_rate_pct": pct(clicks, views),
        "wide_conversion_pct": pct(dx, views),
        "diagnosis_after_click_pct": pct(dx, clicks),
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
