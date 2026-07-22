"""P1/P2: R/P/S 기반 핏 적합도·결과 신뢰도 (규칙 기반, 튜닝 가능)."""

from __future__ import annotations

STRETCH_CODES = frozenset({"SF01", "SF02"})


def score_to_comfort_level(fit_match_score: int) -> int:
    s = int(fit_match_score)
    if s >= 86:
        return 5
    if s >= 76:
        return 4
    if s >= 66:
        return 3
    if s >= 56:
        return 2
    return 1


def compute_ux_scores(
    *,
    recommendation_code: str,
    r_code: str,
    p_code: str,
    s_code: str,
    complex_case: bool,
    precision_recommended: bool,
    precision_completed: bool = False,
) -> dict[str, int]:
    code = (recommendation_code or "SF00").strip().upper()
    match = 80
    if code == "SF00":
        match = 90
    elif code == "SF01":
        match = 78
    elif code == "SF02":
        match = 72
    elif code == "SF03":
        match = 65
    elif code in ("SF04", "SF05"):
        match = 58

    if s_code == "S0":
        match += 4
    elif s_code == "S1":
        match += 0
    elif s_code == "S2":
        match -= 4
    elif s_code == "S3":
        match -= 10

    if p_code == "P5":
        match -= 12
    elif p_code in ("P1", "P2", "P3", "P4"):
        match -= 2

    if r_code in ("R4", "R5"):
        match -= 3

    trust = match
    if complex_case:
        trust -= 10
    if p_code == "P5":
        trust -= 8
    if s_code == "S3":
        trust -= 6
    if precision_recommended and not precision_completed:
        trust -= 12
    if r_code in ("R4", "R5") and not precision_completed:
        trust -= 5
    if precision_completed:
        trust += 8

    fit_match_score = max(45, min(95, int(round(match))))
    result_trust_pct = max(45, min(95, int(round(trust))))
    return {
        "fit_match_score": fit_match_score,
        "result_trust_pct": result_trust_pct,
    }


def compute_comfort_bars(
    *,
    recommendation_code: str,
    r_code: str,
    p_code: str,
    s_code: str,
    complex_case: bool,
    precision_recommended: bool,
    precision_completed: bool = False,
) -> dict[str, object] | None:
    code = (recommendation_code or "").strip().upper()
    if code not in STRETCH_CODES:
        return None
    common = dict(
        r_code=r_code,
        p_code=p_code,
        s_code=s_code,
        complex_case=complex_case,
        precision_recommended=precision_recommended,
        precision_completed=precision_completed,
    )
    with_guidance = compute_ux_scores(recommendation_code=code, **common)
    as_is = compute_ux_scores(recommendation_code="SF03", **common)
    return {
        "order_as_is": {
            "level": score_to_comfort_level(as_is["fit_match_score"]),
            "label": "늘림 없이 평소 사이즈 (참고)",
        },
        "with_guidance": {
            "level": score_to_comfort_level(with_guidance["fit_match_score"]),
            "label": "안내드린 발볼 늘림 적용 후 (참고)",
        },
        "hint": "안내에 맞추면 편하게 신으실 가능성이 더 높은 경우가 많아요.",
    }
