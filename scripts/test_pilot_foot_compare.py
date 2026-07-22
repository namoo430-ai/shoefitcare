"""pilot_foot_compare 스모크 테스트."""

from __future__ import annotations

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

from pilot_engine import Q1_LOOSE, Q1_SLIP, Q1_TIGHT, Q2_BALL, Q2_HALLUX, Q2_INDEX, Q2_INSTEP, Q3_MID, Q3_SEVERE, Q3_SLIGHT
from pilot_foot_compare import (
    build_foot_compare_view,
    customer_foot_image_key,
    customer_foot_type_key,
)


def main() -> None:
    fc = build_foot_compare_view(r_code="R3", p_code="P2", s_code="S2", q1=Q1_LOOSE)
    assert fc["reference"]["type_key"] == "nomal"
    assert fc["customer"]["type_key"] == "slender"
    cust_specs = fc["customer"]["spec_lines"]
    assert cust_specs[0] == "발유형: 좁은발"
    assert cust_specs[1] == "발볼: 보통"
    assert cust_specs[3] == "발길이: 정사이즈"

    fc2 = build_foot_compare_view(r_code="R2", p_code="P1", s_code="S1", q1="", q2=[Q2_HALLUX])
    assert fc2["customer"]["type_key"] == "bunion"
    assert fc2["customer"]["image"] == "Bunion.jpg"
    assert fc2["customer"]["spec_lines"][0] == "발유형: 무지외반"
    assert fc2["customer"]["spec_lines"][1] == "발볼: 넓음"

    fc_hallux_r1_s3 = build_foot_compare_view(
        r_code="R1", p_code="P1", s_code="S3", q1=Q1_TIGHT, q2=[Q2_HALLUX]
    )
    assert fc_hallux_r1_s3["customer"]["image"] == "Bunion.jpg"
    assert fc_hallux_r1_s3["customer"]["spec_lines"][0] == "발유형: 무지외반"
    assert fc_hallux_r1_s3["customer"]["spec_lines"][1] == "발볼: 아주넓음"

    fc_hallux_slight = build_foot_compare_view(
        r_code="R1", p_code="P1", s_code="S1", q1="", q2=[Q2_HALLUX]
    )
    assert fc_hallux_slight["customer"]["spec_lines"][1] == "발볼: 넓음"

    fc_instep_s2 = build_foot_compare_view(
        r_code="R1", p_code="P3", s_code="S2", q1="", q2=[Q2_INSTEP]
    )
    assert fc_instep_s2["customer"]["spec_lines"][2] == "발등: 높은편"

    fc_instep_s3 = build_foot_compare_view(
        r_code="R4", p_code="P3", s_code="S3", q1="", q2=[Q2_INSTEP]
    )
    assert fc_instep_s3["customer"]["spec_lines"][2] == "발등: 매우 높음"

    fc3 = build_foot_compare_view(r_code="R2", p_code="P2", s_code="S1", q1=Q1_SLIP, q2=[Q2_BALL])
    assert fc3["customer"]["spec_lines"][1] == "발볼: 넓음"
    assert fc3["customer"]["spec_lines"][3] == "발길이: 정사이즈 보다 작음"

    assert fc["reference"]["spec_lines"][-1] == "발길이: 정사이즈"
    assert "hallux" in fc2["customer"]["pain_zones"]
    assert "index_toe" not in fc2["customer"]["pain_zones"]

    fc2_index = build_foot_compare_view(
        r_code="R2", p_code="P1", s_code="S1", q1="", q2=[Q2_INDEX]
    )
    assert "index_toe" in fc2_index["customer"]["pain_zones"]

    fc_sf01 = build_foot_compare_view(
        r_code="R2", p_code="P2", s_code="S2", q1=Q1_TIGHT, q2=[Q2_BALL]
    )
    assert fc_sf01["customer"]["spec_lines"][1] == "발볼: 넓음"

    fc4 = build_foot_compare_view(
        r_code="R2", p_code="P2", s_code="S3", q1=Q1_TIGHT, q2=[Q2_BALL]
    )
    assert fc4["customer"]["type_key"] == "wide"
    assert fc4["customer"]["image"] == "wide.jpg"
    assert fc4["customer"]["spec_lines"] == [
        "발유형: 넓은발",
        "발볼: 아주넓음",
        "발등: 보통",
        "발길이: 정사이즈",
    ]

    fc5 = build_foot_compare_view(
        r_code="R2",
        p_code="P2",
        s_code="S2",
        q1="",
        q2=[Q2_HALLUX, Q2_BALL],
    )
    assert fc5["customer"]["image"] == "wide.jpg"
    assert fc5["customer"]["spec_lines"][0] == "발유형: 넓은발 / 무지외반"
    assert fc5["customer"]["spec_lines"][1] == "발볼: 넓음"
    assert "hallux" in fc5["customer"]["pain_zones"]
    assert "ball" in fc5["customer"]["pain_zones"]

    fc_sf04 = build_foot_compare_view(
        r_code="R3", p_code="P0", s_code="S1", q1=Q1_LOOSE, recommendation_code="SF04"
    )
    assert fc_sf04["customer"]["spec_lines"][3] == "발길이: 정사이즈 또는 약간 긴발"

    fc_loose = build_foot_compare_view(r_code="R3", p_code="P0", s_code="S1", q1=Q1_LOOSE)
    assert fc_loose["customer"]["image"] == "narrow.jpg"

    assert customer_foot_type_key(r_code="R2", p_code="P0", q1="") == "wide"
    assert (
        customer_foot_image_key(r_code="R1", p_code="P1", q1="", q2=[])
        == "bunion"
    )
    assert len(fc["intro_sequence"]) == 4
    print("test_pilot_foot_compare: ok")


if __name__ == "__main__":
    main()
