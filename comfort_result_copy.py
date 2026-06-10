"""
결과·착화 안내 문구 (50~60대 톤, 강요 표현 없음).

Lite / Full 공통. pain 키: hallux | wide_ball | high_instep | edema
"""

from __future__ import annotations

import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

_PROJECT_ROOT = Path(__file__).resolve().parent

# ── 진입 (Q_ENTRY) ───────────────────────────────────────
ENTRY_GREETING = "내 발에 맞는 편한 신발, 간단하게 찾아보세요."
ENTRY_BUTTON_LITE = "간단하게 추천받기"
ENTRY_BUTTON_FULL = "내 발에 맞게 자세히 진단하기"

LITE_CONTINUE_FULL = "내 발에 맞게 자세히 진단하기"

TRUST_LINE = "비슷한 불편을 느끼신 분들이 많이 선택하신 방법입니다."
CTA_LABEL = "이대로 편하게 신기"
CTA_BUY_DIAGNOSED = "진단 상품 바로가기"
CTA_BROWSE_OTHER = "다른 상품 보러가기"
CTA_COPY_INQUIRY = "문의용 양식+진단안내 복사"

COUPANG_INQUIRY_HINT = "위 안내를 복사해 쿠팡 판매자 문의에 붙여 넣어 주세요."

STRETCH_MM_PER_STEP = 2.5

COUPANG_STORE_FALLBACK_URL = "https://smartstore.naver.com/mizgirl"

PAIN_DIAGNOSIS: dict[str, str] = {
    "hallux": (
        "고객님은 엄지발가락 옆뼈가 눌리는 무지외반 유형입니다.\n\n"
        "👉 추천 옵션\n"
        "무지외반은 일반 핏으로는 압박이 쉽게 남습니다.\n"
        "발 상태에 따라 아래 기준으로 선택해 주세요.\n"
        "- 기본핏 선택 시 → 와이드 발볼 늘림 필수\n"
        "- 편한핏 / 와이드핏 제품 → 기본 착용 가능\n\n"
        "무지외반이 심한 경우\n"
        "- 아주편한핏 + 기본늘림\n"
        "- 편한핏 + 와이드늘림\n"
        "- 앞코늘림 (필수)\n\n"
        "튀어나온 뼈 부분은 발볼만 늘려서는 부족합니다.\n"
        "앞코까지 함께 확장해야 압박 없이 편하게 신으실 수 있습니다.\n"
        "이 조합이 아니면 같은 신발도 계속 아프게 느껴질 가능성이 높습니다."
    ),
    "wide_ball": (
        "고객님은 발볼이 넓어 양옆 압박이 있는 유형입니다.\n\n"
        "👉 추천 옵션\n"
        "- 기본핏 + 와이드늘림\n"
        "- 편한핏 + 기본늘림\n"
        "- 아주편한핏\n\n"
        "신발 형태는 유지하면서 발볼만 자연스럽게 여유를 만들어주는 조합입니다.\n"
        "가장 많은 고객분들이 선택하는 안정적인 방법입니다."
    ),
    "high_instep": (
        "고객님은 발등이 높아 위쪽 압박을 받는 유형입니다.\n\n"
        "👉 추천 옵션\n"
        "- 편한핏 또는 아주편한핏\n"
        "- 발등이 높은 경우 → 한 사이즈 크게 선택 추천\n\n"
        "이 경우 발볼보다 전체적인 여유가 더 중요합니다.\n"
        "발볼을 무리하게 늘리기보다 핏으로 해결하는 것이 가장 편합니다."
    ),
    "edema": (
        "고객님은 시간이 지날수록 발이 붓는 유형입니다.\n\n"
        "👉 추천 옵션\n"
        "- 편한핏 또는 아주편한핏\n"
        "- 발볼늘림 없음\n\n"
        "오후 붓는 상태까지 고려해 처음부터 여유 있는 핏을 선택하는 것이 중요합니다.\n"
        "딱 맞는 신발은 시간이 지나면 불편해질 가능성이 높습니다."
    ),
}

WEARING_GUIDANCE = (
    "이 신발은 발을 부드럽게 감싸주면서 편안하게 신으실 수 있는 여유 있는 착화감입니다.\n"
    "발볼이 넓거나 오래 걸으면 발이 쉽게 피로해지는 분들께 잘 맞습니다.\n\n"
    "✔ 발볼이 넓으신 분 → 발볼늘림 선택 추천\n"
    "✔ 무지외반이 있으신 분 → 앞코늘림 함께 추천\n"
    "✔ 발등이 높으신 분 → 한 사이즈 크게 선택 추천\n\n"
    "발에 맞게 조정된 신발은 걸을수록 편안함이 더 잘 느껴집니다.\n"
    "발 모양에 맞춰 조정되는 과정에서 자연스러운 형태 변화가 있을 수 있으며, "
    "편안한 착용을 위한 과정입니다.\n"
    "처음부터 발에 맞게 선택하시면 오래 신을수록 편안함을 더 느끼실 수 있습니다."
)


def pain_key_from_foot_issues(foot_issues: list[str] | None) -> str:
    issues = set(foot_issues or [])
    if "무지외반" in issues:
        return "hallux"
    if "발등 높음" in issues:
        return "high_instep"
    if "통통함" in issues:
        return "edema"
    if "넓음" in issues:
        return "wide_ball"
    return "wide_ball"


def pain_key_from_lite_q2(q2: str) -> str:
    return {"1": "hallux", "2": "wide_ball", "3": "high_instep", "4": "edema"}.get(q2, "wide_ball")


LITE_Q1_TEXT = "평소 어떤 신발을 신을 때 가장 불편하셨나요?"
LITE_Q2_TEXT = "발에서 가장 통증이나 불편함을 느끼는 부위는 어디인가요?"


def build_comfort_result_text(
    *,
    pain: str,
    include_wearing: bool = True,
    include_trust: bool = True,
    include_cta_hint: bool = False,
    lite_followup_note: Optional[str] = None,
) -> str:
    blocks = [PAIN_DIAGNOSIS.get(pain, PAIN_DIAGNOSIS["wide_ball"])]
    if include_wearing:
        blocks += ["", WEARING_GUIDANCE]
    if include_trust:
        blocks += ["", TRUST_LINE]
    if include_cta_hint:
        blocks += ["", CTA_LABEL]
    if lite_followup_note:
        blocks += ["", lite_followup_note]
    return "\n".join(blocks)


def lite_followup_note() -> str:
    return f"더 정확한 사이즈·상품 추천이 필요하시면 아래 「{LITE_CONTINUE_FULL}」을 눌러 주세요."


def diagnosis_code(session_id: str) -> str:
    compact = (session_id or "").replace("-", "").strip().upper()
    return f"SF-{compact[:8]}" if compact else "SF-UNKNOWN"


def format_stretch_for_inquiry(stretch_step: int, stretch_mm: float) -> str:
    if int(stretch_step or 0) > 0:
        return f"{int(stretch_step)}단계 ({float(stretch_mm or 0)}mm)"
    return "없음"


def lookup_product_meta(product_id: str | None) -> dict[str, str]:
    if not product_id:
        return {}
    path = _PROJECT_ROOT / "csv_templates" / "products.csv"
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if str(row.get("product_id", "")).strip() == str(product_id).strip():
                return {
                    "product_id": str(product_id).strip(),
                    "name": str(row.get("name", "")).strip(),
                    "product_url": str(row.get("product_url", "")).strip(),
                    "category": str(row.get("category", "")).strip(),
                }
    return {"product_id": str(product_id).strip(), "name": "", "product_url": "", "category": ""}


def build_inquiry_form_block(
    *,
    session_id: str,
    product_id: str | None,
    product_name: str | None,
    intake_mode: str,
    traffic_src: str,
    final_size: int | None = None,
    recommended_fit: str | None = None,
    stretch_step: int = 0,
    stretch_mm: float = 0,
) -> str:
    meta = lookup_product_meta(product_id)
    pid = product_id or meta.get("product_id") or "미지정"
    pname = (product_name or meta.get("name") or "").strip() or "상품명 미확인"
    mode_label = "간단진단" if intake_mode == "lite" else "정밀진단"
    lines = [
        "[슈핏케어 진단·주문 양식]",
        f"진단번호: {diagnosis_code(session_id)}",
        f"진단일시: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"상품코드: {pid}",
        f"상품명: {pname}",
        f"진단경로: {traffic_src or 'web'}-{mode_label}",
    ]
    if final_size is not None:
        lines.append(f"권장사이즈: {final_size}mm")
    if recommended_fit:
        lines.append(f"권장핏: {recommended_fit}")
    lines.append(f"발볼늘림: {format_stretch_for_inquiry(stretch_step, stretch_mm)}")
    return "\n".join(lines)


def build_coupang_inquiry_copy_text(
    *,
    session_id: str,
    diagnosis_body: str,
    product_id: str | None = None,
    product_name: str | None = None,
    intake_mode: str = "full",
    traffic_src: str = "web",
    final_size: int | None = None,
    recommended_fit: str | None = None,
    stretch_step: int = 0,
    stretch_mm: float = 0,
) -> str:
    form = build_inquiry_form_block(
        session_id=session_id,
        product_id=product_id,
        product_name=product_name,
        intake_mode=intake_mode,
        traffic_src=traffic_src,
        final_size=final_size,
        recommended_fit=recommended_fit,
        stretch_step=stretch_step,
        stretch_mm=stretch_mm,
    )
    body = (diagnosis_body or "").strip()
    return f"{form}\n---\n(진단 안내)\n{body}"


def is_coupang_flow(traffic_src: str | None, pinned_product_id: str | None) -> bool:
    if pinned_product_id:
        return True
    src = (traffic_src or "").strip().lower()
    return src.startswith("html") or src.startswith("coupang") or src == "pdp"


def lite_primary_stretch(pain: str) -> tuple[int, float]:
    """쿠팡 Lite 1차: 발볼 늘림 1·2단계만 안내 (엔진 전체 미실행)."""
    if pain == "hallux":
        step = 2
    elif pain == "wide_ball":
        step = 1
    else:
        step = 0
    mm = STRETCH_MM_PER_STEP * step if step else 0.0
    return step, mm


def format_coupang_stretch_message(stretch_step: int, stretch_mm: float) -> str:
    """쿠팡 채팅·문의 본문: 발볼 늘림 1·2단계 안내만."""
    step = int(stretch_step or 0)
    mm = float(stretch_mm or 0.0)
    if step <= 0:
        body = (
            "발볼 늘림 안내\n"
            "· 이번 진단 기준으로 발볼 늘림 1·2단계는 해당 없습니다.\n"
            "· 사이즈는 쿠팡 옵션에서 선택해 주세요."
        )
    elif step == 1:
        if mm <= 0:
            mm = STRETCH_MM_PER_STEP
        body = (
            "[발볼 늘림 안내]\n\n"
            f"이번 진단으로는 발볼 늘림 1단계(약 {mm:.1f}mm)가 잘 맞을 것 같아요.\n"
            "문의창에 「발볼 늘림 1단계」라고 남겨 주시면, 확인 후 맞춤으로 도와드릴게요.\n\n"
            "아래 안내문 전체를 복사해 문의 글에 붙여 넣어 주시면 "
            "발볼 늘림 접수가 한 번에 진행돼요."
        )
    else:
        if mm <= 0:
            mm = STRETCH_MM_PER_STEP * step
        body = (
            "[발볼 늘림 안내]\n\n"
            f"이번 진단으로는 발볼 늘림 2단계(약 {mm:.1f}mm)를 권장해 드려요.\n"
            "문의창에 「발볼 늘림 2단계」라고 남겨 주시면, 확인 후 맞춤으로 도와드릴게요.\n\n"
            "아래 안내문 전체를 복사해 문의 글에 붙여 넣어 주시면 "
            "발볼 늘림 접수가 한 번에 진행돼요."
        )
    return f"{body}\n\n{COUPANG_INQUIRY_HINT}"


def build_coupang_lite_result_display(pain: str, product_id: str | None) -> str:
    step, mm = lite_primary_stretch(pain)
    return format_coupang_stretch_message(step, mm)


def build_coupang_full_result_display(
    *,
    stretch_step: int,
    stretch_mm: float,
    product_name: str = "",
    recommended_fit: str = "",
    final_size: int = 0,
    recommendation_reason: str = "",
    summary_block: str = "",
    slip_hint: str = "",
    options_block: str = "",
    is_consult: bool = False,
    consult_reason: str = "",
) -> str:
    """쿠팡 정밀: 화면·문의 본문은 발볼 1·2단계만 (나머지 인자는 호환용 무시)."""
    if is_consult:
        return (
            "발볼 늘림 안내\n"
            "· 증상이 복합적이라 1·2단계는 문의 후 확정해 드릴게요.\n\n"
            f"{COUPANG_INQUIRY_HINT}"
        )
    return format_coupang_stretch_message(int(stretch_step or 0), float(stretch_mm or 0))


def coupang_stretch_notice(stretch_step: int) -> str:
    """쿠팡 전용 본문에는 이미 COUPANG_INQUIRY_HINT가 포함됨."""
    return ""


def checkout_payload_from_lite(
    prefill: dict[str, Any],
    *,
    session_id: str = "",
    inquiry_copy_text: str = "",
    traffic_src: str = "web",
    product_id: str | None = None,
) -> dict[str, Any]:
    pain = pain_key_from_lite_q2(str(prefill.get("lite_q2", "")))
    meta = lookup_product_meta(product_id)
    return {
        "pain": pain,
        "design_hint": prefill.get("design"),
        "option_interest": None,
        "foot_issues": prefill.get("foot_issues"),
        "product_id": product_id or meta.get("product_id"),
        "product_url": meta.get("product_url", ""),
        "traffic_src": traffic_src,
        "inquiry_copy_text": inquiry_copy_text,
        "cta_buy": CTA_BUY_DIAGNOSED,
        "cta_browse_other": CTA_BROWSE_OTHER,
        "cta_copy_inquiry": CTA_COPY_INQUIRY,
        "browse_url": os.environ.get("COUPANG_STORE_URL", COUPANG_STORE_FALLBACK_URL),
    }


def checkout_payload_from_diagnosis(
    inp: Any,
    res: Any,
    *,
    inquiry_copy_text: str = "",
    traffic_src: str = "web",
    product_id: str | None = None,
) -> dict[str, Any]:
    pain = pain_key_from_foot_issues(getattr(inp, "foot_issues", None))
    pid = product_id or getattr(res, "recommended_product_id", None)
    meta = lookup_product_meta(pid)
    return {
        "pain": pain,
        "final_size": getattr(res, "final_size", None),
        "recommended_fit": getattr(res, "recommended_fit", None),
        "stretch_step": getattr(res, "stretch_step", 0),
        "stretch_mm": getattr(res, "stretch_mm", 0),
        "recommended_product_id": pid,
        "recommended_product_name": getattr(res, "recommended_product_name", None) or meta.get("name"),
        "product_url": meta.get("product_url", ""),
        "traffic_src": traffic_src,
        "inquiry_copy_text": inquiry_copy_text,
        "cta_buy": CTA_BUY_DIAGNOSED,
        "cta_browse_other": CTA_BROWSE_OTHER,
        "cta_copy_inquiry": CTA_COPY_INQUIRY,
        "browse_url": os.environ.get("COUPANG_STORE_URL", COUPANG_STORE_FALLBACK_URL),
    }
