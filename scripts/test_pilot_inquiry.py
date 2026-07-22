#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pilot_inquiry import build_naver_diagnosis_result_copy, build_pilot_inquiry_copies


def main() -> int:
    x = build_pilot_inquiry_copies(
        message="[발볼 늘림 안내]\n...",
        diagnosis_code="SF01-000099",
        recommendation_code="SF01",
        channel="coupang_sms",
        shoe_size=235,
    )
    assert x["inquiry_copy_short"] and "1단계" in x["inquiry_copy_short"]
    assert "SF01-000099" in x["inquiry_copy_short"]
    y = build_pilot_inquiry_copies(
        message="ok",
        diagnosis_code="SF00-000001",
        recommendation_code="SF00",
        channel="coupang_sms",
    )
    assert y["inquiry_copy_short"] is None
    z = build_naver_diagnosis_result_copy(
        diagnosis_code="SF02-000012",
        recommendation_code="SF02",
        shoe_size=240,
        recommended_fit_line="아주 편한핏",
        fit_recommendation_tip="편한핏 추천",
        stretch_recommendation_tip="기본핏 + 발볼 늘림 2단계",
    )
    assert "진단번호" in z and "240mm" in z and "아주 편한핏" in z
    print("OK test_pilot_inquiry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
