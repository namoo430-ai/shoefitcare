#!/usr/bin/env python3
"""Foot profile R/P/S 매핑 테스트."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from foot_profile import derive_foot_profile
from pilot_engine import (
    Q1_INSTEP,
    Q1_LOOSE,
    Q1_NONE,
    Q1_SLIP,
    Q1_TIGHT,
    Q2_BALL,
    Q2_HALLUX,
    Q2_INSTEP,
    Q2_NONE,
    Q2_PINKY,
    Q3_MID,
    Q3_NONE,
    Q3_SEVERE,
    Q3_SLIGHT,
)


def _assert_rps(q1, q2, q3, r, p, s):
    fp = derive_foot_profile(q1, q2, q3)
    assert fp.r_code == r, f"R: want {r} got {fp.r_code} for q1={q1!r} q2={q2}"
    assert fp.p_code == p, f"P: want {p} got {fp.p_code}"
    assert fp.s_code == s, f"S: want {s} got {fp.s_code}"


def main() -> int:
    _assert_rps(Q1_NONE, [Q2_NONE], Q3_NONE, "R1", "P0", "S0")
    _assert_rps(Q1_TIGHT, [Q2_BALL], Q3_SLIGHT, "R2", "P2", "S1")
    _assert_rps(Q1_SLIP, [Q2_BALL], Q3_SEVERE, "R2", "P2", "S3")
    _assert_rps(Q1_SLIP, [Q2_INSTEP], Q3_MID, "R5", "P3", "S2")
    _assert_rps(Q1_LOOSE, [Q2_BALL], Q3_SLIGHT, "R3", "P2", "S1")
    _assert_rps(Q1_INSTEP, [Q2_INSTEP], Q3_MID, "R4", "P3", "S2")
    _assert_rps(Q1_INSTEP, [Q2_BALL], Q3_SEVERE, "R5", "P2", "S3")
    _assert_rps(
        Q1_TIGHT,
        [Q2_HALLUX, Q2_BALL],
        Q3_SEVERE,
        "R2",
        "P5",
        "S3",
    )
    _assert_rps(Q1_TIGHT, [Q2_PINKY], Q3_NONE, "R1", "P4", "S0")

    from fastapi.testclient import TestClient

    from api import app

    c = TestClient(app)
    r = c.post(
        "/pilot/diagnose",
        json={
            "q1": Q1_TIGHT,
            "q2": [Q2_BALL],
            "q3": Q3_SLIGHT,
            "q4": 235,
            "channel": "test_rps",
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    fp = body.get("foot_profile") or {}
    assert fp.get("r_code") == "R2" and fp.get("p_code") == "P2" and fp.get("s_code") == "S1"
    assert "fit_match_score" in (body.get("ux_scores") or fp)
    bars = (body.get("ux_scores") or {}).get("comfort_bars")
    assert bars and bars.get("with_guidance", {}).get("level") >= 1

    r2 = c.post(
        "/pilot/diagnose",
        json={
            "q1": Q1_TIGHT,
            "q2": [Q2_BALL],
            "q3": Q3_SEVERE,
            "q4": 240,
            "channel": "naver_test",
        },
    )
    assert r2.status_code == 200
    assert r2.json().get("recommendation_code") == "SF02"
    assert r2.json().get("inquiry_copy_naver_exchange")

    print("OK test_foot_profile")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
