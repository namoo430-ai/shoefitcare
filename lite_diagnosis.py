"""
3초 발볼 진단 (Lite) — 2문항 intake, Full 엔진과 분리.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Optional

import comfort_result_copy as comfort


@dataclass
class LiteResult:
    design_hint: str
    symptom_key: str
    summary_text: str
    prefill: dict[str, Any] = field(default_factory=dict)
    checkout_payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


Q1_OPTIONS = {
    "1": ("운동화/스니커즈", "운동화"),
    "2": ("구두/로퍼", "로퍼"),
    "3": ("플랫슈즈/샌들", "단화"),
}

Q2_OPTIONS = {
    "1": ("엄지발가락 옆뼈 (무지외반증)", "무지외반"),
    "2": ("발볼 양옆이 꽉 끼고 답답함", "넓음"),
    "3": ("발등이 높아서 위가 눌림", "발등 높음"),
    "4": ("오후만 되면 발이 심하게 부음", "통통함"),
}


def _compact(text: str) -> str:
    return (text or "").strip().replace(" ", "").lower()


def parse_q1(text: str) -> str:
    t = _compact(text)
    aliases = {
        "1": ("1", "운동화", "스니커즈"),
        "2": ("2", "구두", "로퍼"),
        "3": ("3", "플랫", "샌들", "플랫슈즈"),
    }
    for key, words in aliases.items():
        if t in {_compact(w) for w in words}:
            return key
    for key, (label, _) in Q1_OPTIONS.items():
        if _compact(label) in t:
            return key
    raise ValueError("운동화/스니커즈, 구두/로퍼, 플랫슈즈/샌들 중에서 선택해 주세요.")


def parse_q2(text: str) -> str:
    t = _compact(text)
    aliases = {
        "1": ("1", "무지외반", "엄지", "옆뼈"),
        "2": ("2", "발볼", "꽉", "답답"),
        "3": ("3", "발등", "눌림"),
        "4": ("4", "오후", "부음", "붓"),
    }
    for key, words in aliases.items():
        for w in words:
            if _compact(w) in t or t == _compact(w):
                return key
    raise ValueError("불편 부위를 선택해 주세요.")


def build_result(answers: dict[str, str]) -> LiteResult:
    q1 = answers.get("q1", "")
    q2 = answers.get("q2", "")
    _, design = Q1_OPTIONS.get(q1, ("", "로퍼"))
    _, issue = Q2_OPTIONS.get(q2, ("", "넓음"))
    pain = comfort.pain_key_from_lite_q2(q2)

    prefill: dict[str, Any] = {
        "design": design,
        "foot_issues": [issue],
        "lite_q1": q1,
        "lite_q2": q2,
    }
    if q2 == "1":
        prefill["hallux_severity"] = "2"
    if q2 == "3":
        prefill["instep_severity"] = "2"
    if q2 == "2":
        prefill["wide_severity"] = "2"

    # Lite: pain 진단만 본문에, 착화 안내·신뢰 문구는 하단 CTA와 중복 방지
    summary = comfort.build_comfort_result_text(
        pain=pain,
        include_wearing=False,
        include_trust=False,
        lite_followup_note=comfort.lite_followup_note(),
    )

    checkout = comfort.checkout_payload_from_lite(prefill)

    return LiteResult(
        design_hint=design,
        symptom_key=issue,
        summary_text=summary,
        prefill=prefill,
        checkout_payload=checkout,
    )


def apply_prefill_to_session(session: Any) -> None:
    answers = getattr(session, "lite_answers", None) or {}
    if not answers:
        return
    res = build_result(answers)
    pf = res.prefill
    session.design = pf.get("design") or session.design
    session.foot_issues = list(pf.get("foot_issues") or [])
    if pf.get("hallux_severity"):
        session.hallux_severity = str(pf["hallux_severity"])
    if pf.get("instep_severity"):
        session.instep_severity = str(pf["instep_severity"])
    if pf.get("wide_severity"):
        session.wide_severity = str(pf["wide_severity"])
    session.product_first = True


def prompt_q1() -> dict[str, Any]:
    return {
        "text": comfort.LITE_Q1_TEXT,
        "quick_replies": [label for label, _ in Q1_OPTIONS.values()],
    }


def prompt_q2() -> dict[str, Any]:
    return {
        "text": comfort.LITE_Q2_TEXT,
        "quick_replies": [
            "무지외반 (엄지 옆)",
            "발볼 꽉·답답",
            "발등 눌림",
            "오후 발 부음",
        ],
    }


def prompt_lite_done(result: LiteResult) -> dict[str, Any]:
    return {
        "text": result.summary_text,
        "quick_replies": [comfort.LITE_CONTINUE_FULL, "처음으로"],
        "lite": result.to_dict(),
        "checkout_payload": result.checkout_payload,
        "show_cta": True,
    }
