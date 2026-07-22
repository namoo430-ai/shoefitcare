"""pilot_fit_result 스모크 테스트."""

from __future__ import annotations

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

from pilot_fit_result import build_fit_result, effective_stretch_step, talk_sheet_hints


def main() -> None:
    fr = build_fit_result(
        recommendation_code="SF02",
        r_code="R2",
        p_code="P1",
        s_code="S2",
        complex_case=False,
        shoe_size=235,
        stretch_on_option=False,
    )
    assert fr["recommended_fit_line"] == "아주 편한핏"
    assert fr["fit_lines"][0]["comfort_level"] == 1
    assert fr["fit_lines"][1]["comfort_level"] == 4
    assert fr["fit_lines"][2]["comfort_level"] == 5
    assert effective_stretch_step("SF02", "기본핏") == 2
    assert effective_stretch_step("SF02", "편한핏") == 1
    assert len(fr["fit_lines"]) == 3
    assert fr["precision_tab_eligible"] is True

    fr2 = build_fit_result(
        recommendation_code="SF02",
        r_code="R2",
        p_code="P5",
        s_code="S3",
        complex_case=True,
        shoe_size=240,
        stretch_on_option=True,
        stretch_option_label="발볼늘림",
    )
    assert fr2["precision_tab_eligible"] is True
    assert fr2["stretch_on_option"] is True
    assert "편한" in fr2["fit_recommendation_tip"] and "아주" in fr2["fit_recommendation_tip"]
    assert "2단계" in fr2["stretch_recommendation_tip"]
    assert "1단계" in fr2["stretch_recommendation_tip"]
    hints_opt = talk_sheet_hints(
        stretch_on_option=True,
        stretch_option_label="발볼늘림",
        recommendation_code="SF02",
        recommended_fit_line="기본핏",
    )
    assert any("옵션" in h for h in hints_opt)
    assert fr2["exchange_event_active"] is True

    fr_sf01 = build_fit_result(
        recommendation_code="SF01",
        r_code="R2",
        p_code="P2",
        s_code="S2",
        complex_case=False,
        shoe_size=235,
    )
    assert fr_sf01["recommended_fit_line"] == "편한핏"
    assert fr_sf01["fit_lines"][0]["comfort_level"] == 2
    assert fr_sf01["fit_lines"][1]["comfort_level"] == 5
    assert fr_sf01["fit_lines"][2]["comfort_level"] == 4
    assert "편한핏" in fr_sf01["fit_recommendation_tip"]
    assert fr_sf01["stretch_recommendation_tip"] == "기본핏 + 발볼 늘림 1단계"
    assert fr_sf01["precision_tab_eligible"] is True

    fr_sf05 = build_fit_result(
        recommendation_code="SF05",
        r_code="R5",
        p_code="P5",
        s_code="S2",
        complex_case=True,
        shoe_size=235,
    )
    assert fr_sf05["recommended_fit_line"] == "편한핏"
    assert fr_sf05["fit_lines"][1]["comfort_level"] == 4
    assert fr_sf05["fit_lines"][2]["comfort_level"] == 5
    assert "여유 있는 신발" in " ".join(fr_sf05["narrative_lines"])
    assert "편한" in fr_sf05["fit_recommendation_tip"]
    assert "2단계" in fr_sf05["stretch_recommendation_tip"]

    fr_sf03 = build_fit_result(
        recommendation_code="SF03",
        r_code="R2",
        p_code="P2",
        s_code="S2",
        complex_case=False,
        shoe_size=235,
    )
    assert fr_sf03["recommended_fit_line"] == "아주 편한핏"
    assert fr_sf03["fit_lines"][0]["comfort_level"] == 1
    assert fr_sf03["fit_lines"][1]["comfort_level"] == 3
    assert fr_sf03["fit_lines"][2]["comfort_level"] == 5
    assert "한 사이즈 크게" in fr_sf03["fit_recommendation_tip"]
    assert "아주 편한핏 + 발볼 늘림 1단계" in fr_sf03["stretch_recommendation_tip"]
    assert "편한핏 + 발볼 늘림 2단계" in fr_sf03["stretch_recommendation_tip"]

    from pilot_engine import Q1_LOOSE, Q1_SLIP

    fr_slip = build_fit_result(
        recommendation_code="SF01",
        r_code="R2",
        p_code="P2",
        s_code="S2",
        complex_case=False,
        shoe_size=235,
        q1=Q1_SLIP,
    )
    assert "발볼에 맞춰" in fr_slip["narrative_lines"][0]
    assert "한 사이즈 작게" in fr_slip["narrative_lines"][1]

    fr_loose = build_fit_result(
        recommendation_code="SF04",
        r_code="R3",
        p_code="P0",
        s_code="S1",
        complex_case=False,
        shoe_size=235,
        q1=Q1_LOOSE,
    )
    assert fr_loose["recommended_fit_line"] == "기본핏"
    assert fr_loose["fit_lines"][0]["comfort_level"] == 5
    assert fr_loose["fit_lines"][1]["comfort_level"] == 1
    assert "칼발" in fr_loose["fit_recommendation_tip"]
    assert "좁은발" in fr_loose["fit_recommendation_tip"]
    assert "큰 사이즈 유지" in fr_loose["fit_recommendation_tip"]
    assert "한 사이즈 작게" in fr_loose["fit_recommendation_tip"]
    assert "발길이 늘림" in fr_loose["stretch_recommendation_tip"]
    assert "해당 사항 없음" in fr_loose["stretch_recommendation_tip"]
    assert fr_loose["precision_tab_eligible"] is True

    fr_sf00 = build_fit_result(
        recommendation_code="SF00",
        r_code="R1",
        p_code="P0",
        s_code="S0",
        complex_case=False,
        shoe_size=235,
    )
    assert fr_sf00["precision_tab_eligible"] is True
    assert "헐거" in " ".join(fr_loose["narrative_lines"])

    print("test_pilot_fit_result: ok")


if __name__ == "__main__":
    main()
