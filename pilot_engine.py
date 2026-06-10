"""
슈핏케어 파일럿 룰 엔진 — Q1~Q4 → SF00~SF05 (Q5는 레거시 저장만)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

Q1_TIGHT = "길이는 맞는데 발볼이 조이는 편이에요"
Q1_SLIP = "발볼 때문에 큰 사이즈를 신으면 헐거워져요"
Q1_INSTEP = "발등이 눌리는 편이에요"
Q1_LOOSE = "대부분 신발이 여유 있는 편이에요"
Q1_NONE = "특별히 불편함이 없어요"

Q2_HALLUX = "엄지발가락 옆(무지외반)"
Q2_PINKY = "새끼 발가락쪽"
Q2_BALL = "발볼 부분"
Q2_INSTEP = "발등 부분"
Q2_NONE = "불편 사항 없음"

Q3_SLIGHT = "가끔 신경 쓰여요"
Q3_MID = "자주 불편해요"  # 로직상 Q3_SLIGHT와 동일 분기
Q3_SEVERE = "매우 불편해요"
Q3_NONE = "불편은 거의 없어요"


def normalize_q1(q1: str) -> str:
    q1 = (q1 or "").strip()
    legacy = {
        "발볼이 꽉 끼는 편이에요": Q1_TIGHT,
        "특별한 불편은 없어요": Q1_NONE,
    }
    return legacy.get(q1, q1)


def normalize_q3(q3: str) -> str:
    q3 = (q3 or "").strip()
    legacy = {
        "약간 불편함": Q3_SLIGHT,
        "보통 불편함": Q3_SLIGHT,
        "불편함이 있어요": Q3_SLIGHT,
        "많이 불편해요": Q3_SEVERE,
        "매우 불편함": Q3_SEVERE,
        "불편 사항 없음": Q3_NONE,
    }
    return legacy.get(q3, q3)

Q5_TIGHT = "대부분 신발이 발볼이 꽉 끼는 편"
Q5_OK = "대부분 잘 맞는 편"
Q5_LOOSE = "대부분 신발이 헐거운 편"

SHOE_SIZES = list(range(225, 256, 5))

STRETCH_CODES = frozenset({"SF01", "SF02"})

# 파일럿 룰·문구 배포 세대 (반품 코호트를 버전별로 자를 때 사용)
PILOT_RULE_VERSION = "20260605-sf00-fit-copy"


@dataclass
class PilotInput:
    q1: str
    q2: list[str]
    q3: str
    q4: int
    q5: str


@dataclass
class PilotResult:
    recommendation_code: str
    complex_case: bool
    precision_recommended: bool
    message: str
    instep_adjustment: bool = False


def _has(q2: list[str], key: str) -> bool:
    return key in (q2 or [])


def compute_complex_case(q2: list[str]) -> bool:
    if not q2 or (len(q2) == 1 and Q2_NONE in q2):
        return False
    if len(q2) >= 2:
        return True
    if _has(q2, Q2_HALLUX):
        return True
    return False


def precision_recommended(
    *,
    complex_case: bool,
    q3: str,
    code: str,
    q1: str = "",
) -> bool:
    if complex_case:
        return True
    if q3 == Q3_SEVERE:
        return True
    if code == "SF04":
        return True
    return False


def _q2_instep_selected(q2: list[str]) -> bool:
    return _has(q2, Q2_INSTEP)


def evaluate(inp: PilotInput) -> PilotResult:
    inp = PilotInput(
        normalize_q1(inp.q1),
        inp.q2,
        normalize_q3(inp.q3),
        inp.q4,
        inp.q5,
    )
    q2 = list(inp.q2 or [])
    if Q2_NONE in q2:
        q2 = [Q2_NONE]

    if inp.q1 == Q1_NONE:
        code = "SF00"
        msg = _message_for(code, q1=inp.q1, q4=inp.q4, q2=[Q2_NONE])
        return PilotResult(
            recommendation_code=code,
            complex_case=False,
            precision_recommended=False,
            message=msg,
        )

    if inp.q3 == Q3_NONE:
        code = "SF00"
        msg = _message_for(code, q1=inp.q1, q4=inp.q4, q2=q2)
        cx = compute_complex_case(q2)
        return PilotResult(
            recommendation_code=code,
            complex_case=cx,
            precision_recommended=precision_recommended(
                complex_case=cx, q3=inp.q3, code=code, q1=inp.q1
            ),
            message=msg,
        )

    code = "SF00"
    instep_adj = False

    if inp.q1 == Q1_TIGHT and inp.q3 == Q3_SEVERE:
        code = "SF03"
    elif (
        inp.q1 == Q1_INSTEP
        and _has(q2, Q2_HALLUX)
        and inp.q3 == Q3_SEVERE
    ):
        code = "SF03"
    elif (
        inp.q1 == Q1_INSTEP
        and _q2_instep_selected(q2)
        and inp.q3 == Q3_SEVERE
    ):
        code = "SF04"
    elif _has(q2, Q2_HALLUX) and inp.q3 == Q3_SEVERE:
        code = "SF02"
    elif inp.q1 == Q1_SLIP and inp.q3 == Q3_SEVERE and _has(q2, Q2_BALL):
        code = "SF02"
    elif inp.q1 == Q1_TIGHT and inp.q3 in (Q3_SLIGHT, Q3_MID):
        code = "SF01"
    elif (
        inp.q1 == Q1_INSTEP
        and _q2_instep_selected(q2)
        and inp.q3 in (Q3_SLIGHT, Q3_MID)
    ):
        code = "SF01"
    elif (
        inp.q1 == Q1_INSTEP
        and not _q2_instep_selected(q2)
        and inp.q3 == Q3_SEVERE
    ):
        code = "SF03"
    elif (
        inp.q1 == Q1_INSTEP
        and not _q2_instep_selected(q2)
        and inp.q3 in (Q3_SLIGHT, Q3_MID)
    ):
        code = "SF01"
    elif inp.q1 == Q1_SLIP:
        code = "SF01"
    elif inp.q1 == Q1_LOOSE or inp.q5 == Q5_LOOSE:
        code = "SF04"
    else:
        code = "SF00"

    cx = compute_complex_case(q2)
    return PilotResult(
        recommendation_code=code,
        complex_case=cx,
        precision_recommended=precision_recommended(
            complex_case=cx, q3=inp.q3, code=code, q1=inp.q1
        ),
        message=_message_for(code, q1=inp.q1, q4=inp.q4, q2=q2),
        instep_adjustment=instep_adj,
    )


def apply_precision_sf05(previous_code: str) -> Optional[str]:
    if previous_code == "SF04":
        return "SF05"
    return None


def _smaller_size_mm(q4: int) -> Optional[int]:
    if q4 in SHOE_SIZES:
        idx = SHOE_SIZES.index(q4)
        if idx > 0:
            return SHOE_SIZES[idx - 1]
    smaller = q4 - 5
    if smaller >= SHOE_SIZES[0]:
        return smaller
    return None


def _message_for(
    code: str,
    *,
    q1: str = "",
    q4: int = 235,
    q2: Optional[list[str]] = None,
) -> str:
    q2 = list(q2 or [])
    slip = q1 == Q1_SLIP and code in STRETCH_CODES
    instep_stretch = (
        q1 == Q1_INSTEP and code == "SF01" and _q2_instep_selected(q2)
    )
    instep_severe = q1 == Q1_INSTEP and code == "SF04"
    smaller = _smaller_size_mm(q4) if slip else None

    def _stretch_title() -> str:
        extra = " · 헐떡임 대응" if slip else ""
        return f"[발볼 늘림 안내{extra}]\n\n"

    sf01_line = (
        f"진단 결과, 평소 사이즈({q4}mm)보다 한 사이즈 작게({smaller}mm) 주문하시고 "
        "발볼 늘림 1단계가 적합합니다.\n"
        if slip and smaller is not None
        else (
            "진단 결과, 한 사이즈 작게 주문하시고 발볼 늘림 1단계가 적합합니다.\n"
            if slip
            else (
                "진단 결과, 전체적인 압박 완화를 위해 발볼 늘림 1단계가 적합합니다.\n"
                if instep_stretch
                else (
                    "발볼이 넓은 편이에요.\n"
                    "일반 사이즈에서 볼 부분이 조일 수 있어요.\n"
                    "발볼 늘림 1단계 또는 편한 핏 제품을 권장합니다.\n"
                )
            )
        )
    )
    sf02_line = (
        f"진단 결과, 평소 사이즈({q4}mm)보다 한 사이즈 작게({smaller}mm) 주문하시고 "
        "발볼 늘림 2단계가 적합합니다.\n"
        if slip and smaller is not None
        else (
            "진단 결과, 한 사이즈 작게 주문하시고 발볼 늘림 2단계가 적합합니다.\n"
            if slip
            else "진단 결과, 발볼 늘림 2단계가 적합합니다.\n"
        )
    )

    messages = {
        "SF00": (
            "발볼 핏 안내\n\n"
            "😊 현재는 발볼 늘림 없이도 편하게 착용 가능한 유형으로 확인되었어요.\n\n"
            "추천\n\n"
            "발볼 늘림 없이 주문\n"
            "평소 신는 정사이즈 선택\n\n"
            "📌 사이즈는 옵션에서 선택해 주세요."
        ),
        "SF01": _stretch_title() + sf01_line,
        "SF02": _stretch_title() + sf02_line,
        "SF03": (
            "전체적으로 압박이 심한 경우 한 사이즈를 크게 하시는 것을 추천드립니다.\n"
            "복합적인 통증이신 경우 정밀 진단을 받아 보세요."
        ),
        "SF04": (
            (
                "발등 압박이 매우 심하게 느껴지는 경우입니다.\n"
                "한 사이즈 크게 주문을 검토해 보시고, 정밀 진단을 받아 보세요."
            )
            if instep_severe
            else (
                "고객님은 발볼이 좁은 유형으로 추정됩니다.\n"
                "엄마신발은 일반 신발보다 발볼이 넓고 편안하게 제작된 제품입니다.\n"
                "평소 신발이 자주 헐거운 편이라면 한사이즈 작게 주문하는 것을 고려해 보세요.\n"
                "칼발 등으로 발길이 때문에 사이즈를 줄이기 어려우면 정밀 진단을 권장드립니다."
            )
        ),
        "SF05": (
            "정밀 진단 결과\n"
            "· 정사이즈 유지, 발길이 늘림 서비스 또는 앞깔창 보정을 권장드립니다.\n"
            "· 발볼은 좁은 편이나 발길이 영향으로 사이즈 다운이 어려운 칼발 유형입니다."
        ),
    }
    return messages.get(code, messages["SF00"])


def sf_engine_hint(recommendation_code: str) -> dict[str, Any]:
    """SF → full engine(Q5 등가·핏) 분석용 힌트. 고객 노출·처방 확정 아님."""
    code = (recommendation_code or "SF00").strip().upper()
    base: dict[str, Any] = {
        "sf_code": code,
        "policy_n": 0,
        "stretch_step": 0,
        "primary_axis": "none",
        "fit_axis_note": "기본핏/편한핏/아주편한핏은 engine.py 등가표와 연동 예정",
    }
    if code == "SF01":
        base.update(policy_n=1, stretch_step=1, primary_axis="stretch_or_fit")
    elif code == "SF02":
        base.update(policy_n=2, stretch_step=2, primary_axis="stretch_or_size")
    elif code == "SF03":
        base.update(policy_n=2, stretch_step=0, primary_axis="size_up")
    elif code == "SF04":
        base.update(policy_n=0, stretch_step=0, primary_axis="consult_or_size")
    elif code == "SF05":
        base.update(policy_n=0, stretch_step=0, primary_axis="length_instep_after_precision")
    return base


def cohort_group(
    *,
    has_diagnosis: bool,
    recommendation_code: str,
    actual_work_step: Optional[int],
) -> str:
    """반품 분석 3그룹: none | diagnosis_only | diagnosis_stretch"""
    if not has_diagnosis:
        return "none"
    step = int(actual_work_step or 0)
    if recommendation_code in STRETCH_CODES or step in (1, 2):
        return "diagnosis_stretch"
    return "diagnosis_only"


def pilot_input_from_dict(d: dict[str, Any]) -> PilotInput:
    q2 = d.get("q2") or d.get("q2_pain_areas") or []
    if isinstance(q2, str):
        q2 = [x.strip() for x in q2.split(",") if x.strip()]
    return PilotInput(
        q1=normalize_q1(str(d.get("q1") or d.get("q1_problem") or "")),
        q2=q2,
        q3=normalize_q3(str(d.get("q3") or d.get("q3_pain_level") or "")),
        q4=int(d.get("q4") or d.get("shoe_size") or 235),
        q5=str(d.get("q5") or "").strip(),
    )
