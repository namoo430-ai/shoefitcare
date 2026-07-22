"""결과 화면 · 기준 발 vs 고객 발형 비교 (R/P/S + Q1)."""

from __future__ import annotations

from typing import Any

from pilot_copy import foot_compare_reference_spec_lines
from pilot_engine import Q1_LOOSE, Q1_SLIP, Q1_TIGHT, Q2_BALL, Q2_HALLUX, Q2_INDEX, Q2_INSTEP, Q2_NONE, Q2_PINKY, normalize_q1
from pilot_copy import foot_compare_customer_length_label, narrative_q1_slip_lines

FOOT_TYPE_FILES: dict[str, str] = {
    "nomal": "nomal.jpg",
    "wide": "wide.jpg",
    "narrow": "narrow.jpg",
    "bunion": "Bunion.jpg",
    "slender": "narrow.jpg",
}

FOOT_TYPE_LABEL: dict[str, str] = {
    "nomal": "보통발",
    "wide": "넓은발",
    "narrow": "좁은발",
    "bunion": "무지외반",
    "slender": "칼발",
}

FOOT_COMPARE_SPEC_VERSION = "20260622-instep-q3-label"


def _active_q2_list(q2: list[str] | None) -> list[str]:
    active = [x.strip() for x in (q2 or []) if x and x.strip()]
    if not active or (len(active) == 1 and active[0] == Q2_NONE):
        return []
    return [x for x in active if x != Q2_NONE]


def _ball_label(
    r_code: str,
    s_code: str = "S0",
    *,
    p_code: str = "P0",
    q2: list[str] | None = None,
) -> str:
    r = (r_code or "R1").upper()
    s = (s_code or "S0").upper()
    p = (p_code or "P0").upper()
    active = _active_q2_list(q2)
    has_hallux = p == "P1" or Q2_HALLUX in active
    has_ball_q2 = Q2_BALL in active

    if r in ("R2", "R5") or has_ball_q2:
        if s == "S3":
            return "아주넓음"
        return "넓음"

    if has_hallux and not has_ball_q2:
        if s == "S3":
            return "아주넓음"
        if s in ("S1", "S2"):
            return "넓음"
        return "보통"

    return "보통"


def _instep_label(
    r_code: str,
    s_code: str = "S0",
    *,
    p_code: str = "P0",
    q2: list[str] | None = None,
) -> str:
    r = (r_code or "R1").upper()
    s = (s_code or "S0").upper()
    p = (p_code or "P0").upper()
    active = _active_q2_list(q2)
    has_instep = p == "P3" or Q2_INSTEP in active

    if has_instep:
        if s == "S3":
            return "매우 높음"
        if s in ("S1", "S2"):
            return "높은편"
        return "보통"

    if r in ("R4", "R5"):
        return "높음"
    return "보통"


def _length_label(q1: str, *, recommendation_code: str = "") -> str:
    return foot_compare_customer_length_label(q1, recommendation_code=recommendation_code)


def _foot_type_spec_value(
    *,
    type_key: str,
    r_code: str,
    p_code: str,
    q2: list[str] | None,
) -> str:
    """발유형: 복합 시 넓은발 / 무지외반 등 슬래시로 병기."""
    r = (r_code or "R1").upper()
    p = (p_code or "P0").upper()
    active = _active_q2_list(q2)
    has_hallux = p == "P1" or Q2_HALLUX in active
    has_ball_q2 = Q2_BALL in active
    if has_hallux and not has_ball_q2:
        return "무지외반"
    is_wide = r in ("R2", "R5") or type_key == "wide"
    parts: list[str] = []
    if is_wide:
        parts.append("넓은발")
    if has_hallux:
        parts.append("무지외반")
    if parts:
        return " / ".join(parts)
    labels = {
        "nomal": "보통발",
        "wide": "넓은발",
        "narrow": "좁은발",
        "bunion": "무지외반",
        "slender": "좁은발",
    }
    return labels.get(type_key, "보통발")


INTRO_SEQUENCE: list[dict[str, str]] = [
    {"key": "nomal", "label": "보통발"},
    {"key": "wide", "label": "넓은발"},
    {"key": "narrow", "label": "좁은발"},
    {"key": "bunion", "label": "무지외반"},
]


def _foot_type_spec_label(*, type_key: str, p_code: str) -> str:
    """결과 스펙 4줄 — 발유형 (무지외반/보통발/넓은발/좁은발)."""
    if (p_code or "").upper() == "P1":
        return "무지외반"
    labels = {
        "nomal": "보통발",
        "wide": "넓은발",
        "narrow": "좁은발",
        "bunion": "무지외반",
        "slender": "좁은발",
    }
    return labels.get(type_key, "보통발")


def customer_foot_type_key(
    *,
    r_code: str,
    p_code: str,
    q1: str,
) -> str:
    p = (p_code or "P0").upper()
    if p == "P1":
        return "bunion"
    q1n = normalize_q1(q1)
    if q1n == Q1_LOOSE:
        return "slender"
    r = (r_code or "R1").upper()
    if r in ("R2", "R5"):
        return "wide"
    if r == "R3":
        return "narrow"
    return "nomal"


def customer_foot_image_key(
    *,
    r_code: str,
    p_code: str,
    q1: str,
    q2: list[str] | None = None,
) -> str:
    """복합 통증: wide(발볼) 또는 bunion(무지외반) PNG + Q2 도트."""
    active = _active_q2_list(q2)
    p = (p_code or "P0").upper()
    has_hallux = p == "P1" or Q2_HALLUX in active
    has_ball = Q2_BALL in active
    r = (r_code or "R1").upper()
    is_wide_r = r in ("R2", "R5")
    if has_ball:
        return "wide"
    if has_hallux:
        return "bunion"
    if is_wide_r:
        return "wide"
    return customer_foot_type_key(r_code=r_code, p_code=p_code, q1=q1)


def pain_zones_from_q2(q2: list[str]) -> list[str]:
    active = [x.strip() for x in (q2 or []) if x and x.strip()]
    if not active or (len(active) == 1 and active[0] == Q2_NONE):
        return []
    zones: list[str] = []
    if Q2_HALLUX in active:
        zones.append("hallux")
    if Q2_INDEX in active:
        zones.append("index_toe")
    if Q2_BALL in active:
        zones.append("ball")
    if Q2_INSTEP in active:
        zones.append("instep")
    if Q2_PINKY in active:
        zones.append("pinky")
    return zones


def pain_zones_for_profile(p_code: str) -> list[str]:
    p = (p_code or "P0").upper()
    mapping = {
        "P1": ["hallux"],
        "P2": ["ball"],
        "P3": ["instep"],
        "P4": ["pinky"],
        "P5": ["hallux", "ball", "instep", "pinky"],
    }
    return list(mapping.get(p, []))


def pain_opacity_for_severity(s_code: str) -> float:
    s = (s_code or "S0").upper()
    if s == "S3":
        return 0.72
    if s == "S2":
        return 0.55
    if s == "S1":
        return 0.38
    return 0.0


def _spec_lines(
    *,
    type_key: str,
    r_code: str,
    p_code: str,
    s_code: str,
    q1: str,
    q2: list[str] | None,
    reference: bool,
    recommendation_code: str = "",
) -> list[str]:
    if reference:
        return list(foot_compare_reference_spec_lines())
    type_label = _foot_type_spec_value(
        type_key=type_key, r_code=r_code, p_code=p_code, q2=q2
    )
    return [
        f"발유형: {type_label}",
        f"발볼: {_ball_label(r_code, s_code, p_code=p_code, q2=q2)}",
        f"발등: {_instep_label(r_code, s_code, p_code=p_code, q2=q2)}",
        f"발길이: {_length_label(q1, recommendation_code=recommendation_code)}",
    ]


def build_foot_compare_view(
    *,
    r_code: str,
    p_code: str,
    s_code: str,
    q1: str = "",
    q2: list[str] | None = None,
    recommendation_code: str = "",
) -> dict[str, Any]:
    ref_key = "nomal"
    q2list = list(q2 or [])
    cust_key = customer_foot_type_key(r_code=r_code, p_code=p_code, q1=q1)
    img_key = customer_foot_image_key(
        r_code=r_code, p_code=p_code, q1=q1, q2=q2list
    )
    zones = pain_zones_from_q2(q2list)
    if not zones:
        zones = pain_zones_for_profile(p_code)
    opacity = pain_opacity_for_severity(s_code) if zones else 0.0
    cust_image = FOOT_TYPE_FILES.get(img_key, FOOT_TYPE_FILES["nomal"])
    return {
        "reference": {
            "type_key": ref_key,
            "label": FOOT_TYPE_LABEL[ref_key],
            "image": FOOT_TYPE_FILES[ref_key],
            "spec_lines": _spec_lines(
                type_key=ref_key, r_code="R1", p_code="P0", s_code="S0", q1="", q2=None, reference=True
            ),
        },
        "customer": {
            "type_key": img_key,
            "label": FOOT_TYPE_LABEL.get(img_key, cust_key),
            "image": cust_image,
            "spec_lines": _spec_lines(
                type_key=cust_key,
                r_code=r_code,
                p_code=p_code,
                s_code=s_code,
                q1=q1,
                q2=q2list,
                reference=False,
                recommendation_code=recommendation_code,
            ),
            "pain_zones": zones,
            "pain_opacity": opacity,
        },
        "intro_sequence": INTRO_SEQUENCE,
        "image_base_path": "/product-images",
        "q2": list(q2 or []),
        "spec_version": FOOT_COMPARE_SPEC_VERSION,
    }
