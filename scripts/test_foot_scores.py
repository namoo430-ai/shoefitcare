#!/usr/bin/env python3
"""foot_scores 규칙 스모크."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from foot_scores import compute_comfort_bars, compute_ux_scores


def main() -> int:
    ux = compute_ux_scores(
        recommendation_code="SF00",
        r_code="R1",
        p_code="P0",
        s_code="S0",
        complex_case=False,
        precision_recommended=False,
    )
    assert ux["fit_match_score"] >= 85

    ux2 = compute_ux_scores(
        recommendation_code="SF02",
        r_code="R5",
        p_code="P5",
        s_code="S3",
        complex_case=True,
        precision_recommended=True,
    )
    assert ux2["result_trust_pct"] < 65

    bars = compute_comfort_bars(
        recommendation_code="SF01",
        r_code="R1",
        p_code="P2",
        s_code="S2",
        complex_case=True,
        precision_recommended=False,
    )
    assert bars is not None
    assert bars["with_guidance"]["level"] >= bars["order_as_is"]["level"]

    none_bars = compute_comfort_bars(
        recommendation_code="SF00",
        r_code="R1",
        p_code="P0",
        s_code="S0",
        complex_case=False,
        precision_recommended=False,
    )
    assert none_bars is None

    from pilot_storage import backfill_foot_profiles, init_pilot_tables

    init_pilot_tables()
    backfill_foot_profiles(dry_run=True)

    print("OK test_foot_scores")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
