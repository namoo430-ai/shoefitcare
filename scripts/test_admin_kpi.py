"""Admin KPI · 기간 필터 · 작업실 큐 (로컬 SQLite)."""

from __future__ import annotations

import os
import sys
import tempfile
import uuid
from datetime import datetime, timedelta

os.environ.setdefault("SHOEFITCARE_DB", tempfile.mktemp(suffix=".db"))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pilot_storage as ps  # noqa: E402


def _mk_dx(sf: str, *, prec: int = 0) -> str:
    row = ps.create_diagnosis(
        {
            "q1": "길이는 맞는데 발볼이 조이는 편이에요",
            "q2": [],
            "q3": "가끔 신경 쓰여요",
            "q4": 235,
        },
        channel="naver",
        product_id="SR266",
    )
    dx_id = row["id"]
    ps.update_diagnosis(dx_id, {"order_no": "T-" + sf, "memo": "test"})
    with ps._conn() as c:
        c.execute(
            "UPDATE pilot_diagnoses SET recommendation_code=?, precision_completed=? WHERE id=?",
            (sf, prec, dx_id),
        )
        c.commit()
    return dx_id


def main() -> None:
    ps.init_pilot_tables()
    today = datetime.now().date()
    fd = (today - timedelta(days=30)).isoformat()
    td = today.isoformat()

    _mk_dx("SF01")
    _mk_dx("SF05", prec=1)

    c0 = ps.kpi_counts(from_date=fd, to_date=td)
    assert c0["total_diagnoses"] >= 2

    ws = ps.list_diagnoses(workshop_only=True, from_date=fd, to_date=td)
    codes = {r["recommendation_code"] for r in ws}
    assert "SF01" in codes
    assert "SF05" in codes

    nv = ps.naver_pilot_kpi(from_date=fd, to_date=td)
    assert nv["naver_diagnoses"] >= 2

    daily = ps.daily_diagnosis_counts(from_date=fd, to_date=td)
    assert isinstance(daily, list)

    print("test_admin_kpi: ok")


if __name__ == "__main__":
    main()
