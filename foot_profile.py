"""
Foot Comport Matrix (P0): Q1~Q3 → R / P / S 프로파일.

Reference Foot (R), Pain Pattern (P), Pain Severity (S).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pilot_engine import (
    Q1_INSTEP,
    Q1_LOOSE,
    Q1_NONE,
    Q1_SLIP,
    Q1_TIGHT,
    Q2_BALL,
    Q2_HALLUX,
    Q2_INDEX,
    Q2_INSTEP,
    Q2_NONE,
    Q2_PINKY,
    Q3_MID,
    Q3_NONE,
    Q3_SEVERE,
    Q3_SLIGHT,
    normalize_q1,
    normalize_q3,
)

FOOT_PROFILE_VERSION = "20260620-r-tight-ball-r2"

R_LABELS = {
    "R1": "Standard Foot",
    "R2": "Wide Foot",
    "R3": "Narrow Foot",
    "R4": "High Instep Foot",
    "R5": "Wide + High Instep Foot",
}
P_LABELS = {
    "P0": "통증 없음",
    "P1": "엄지(무지외반)",
    "P2": "발볼",
    "P3": "발등",
    "P4": "새끼발가락",
    "P5": "복합통증",
}
S_LABELS = {
    "S0": "불편 거의 없음",
    "S1": "가끔 신경 쓰임",
    "S2": "자주 불편함",
    "S3": "매우 불편함",
}


@dataclass(frozen=True)
class FootProfile:
    r_code: str
    p_code: str
    s_code: str
    version: str = FOOT_PROFILE_VERSION

    @property
    def r_label(self) -> str:
        return R_LABELS.get(self.r_code, self.r_code)

    @property
    def p_label(self) -> str:
        return P_LABELS.get(self.p_code, self.p_code)

    @property
    def s_label(self) -> str:
        return S_LABELS.get(self.s_code, self.s_code)


def _active_q2(q2: list[str]) -> list[str]:
    raw = list(q2 or [])
    if Q2_NONE in raw and len(raw) == 1:
        return []
    return [x for x in raw if x != Q2_NONE]


def derive_s_code(q3: str) -> str:
    q3n = normalize_q3(q3)
    if q3n == Q3_NONE:
        return "S0"
    if q3n == Q3_SLIGHT:
        return "S1"
    if q3n == Q3_MID:
        return "S2"
    if q3n == Q3_SEVERE:
        return "S3"
    return "S0"


def derive_p_code(q1: str, q2: list[str]) -> str:
    q1n = normalize_q1(q1)
    if q1n == Q1_NONE:
        return "P0"
    active = _active_q2(q2)
    if not active:
        return "P0"
    if len(active) >= 2:
        return "P5"
    if Q2_INDEX in active:
        return "P1"
    if Q2_HALLUX in active:
        return "P1"
    if Q2_BALL in active:
        return "P2"
    if Q2_INSTEP in active:
        return "P3"
    if Q2_PINKY in active:
        return "P4"
    return "P0"


def derive_r_code(q1: str, q2: list[str]) -> str:
    q1n = normalize_q1(q1)
    active = _active_q2(q2)

    if q1n == Q1_NONE:
        return "R1"
    if q1n == Q1_LOOSE:
        return "R3"
    if q1n == Q1_SLIP:
        # Wide(R2); + Q2 발등 → R5 (팀 확정, FOOT_PROFILE_RPS_MAPPING.md)
        if Q2_INSTEP in active:
            return "R5"
        return "R2"
    if q1n == Q1_INSTEP:
        if Q2_BALL in active or len(active) >= 2:
            return "R5"
        return "R4"
    if q1n == Q1_TIGHT:
        if Q2_BALL in active:
            return "R2"
        return "R1"
    return "R1"


def derive_foot_profile(q1: str, q2: list[str], q3: str) -> FootProfile:
    """Q1~Q3 (정규화 전 문자열 가능) → R/P/S."""
    q1n = normalize_q1(q1)
    q2n = list(q2 or [])
    if Q2_NONE in q2n and len(q2n) == 1:
        q2n = [Q2_NONE]
    return FootProfile(
        r_code=derive_r_code(q1n, q2n),
        p_code=derive_p_code(q1n, q2n),
        s_code=derive_s_code(q3),
    )


def foot_profile_to_dict(profile: FootProfile) -> dict[str, Any]:
    return {
        "version": profile.version,
        "r_code": profile.r_code,
        "p_code": profile.p_code,
        "s_code": profile.s_code,
        "r_label": profile.r_label,
        "p_label": profile.p_label,
        "s_label": profile.s_label,
    }
