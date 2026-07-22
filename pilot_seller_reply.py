"""판매자 맞춤 답변문 생성 (진단 + 상품 핏 라인)."""

from __future__ import annotations

from typing import Any

from pilot_engine import Q1_LOOSE, normalize_q1

VALID_FIT_LINES = frozenset({"기본핏", "편한핏", "아주 편한핏"})

STRETCH_CODES = frozenset({"SF01", "SF02"})


def normalize_fit_line(fit_line: str) -> str:
    s = (fit_line or "").strip()
    if s in ("아주편한핏", "아주 편한핏"):
        return "아주 편한핏"
    if s in ("편안핏", "편한핏"):
        return "편한핏"
    if s == "기본핏":
        return "기본핏"
    return s


def _stretch_step_from_sf(recommendation_code: str) -> int:
    code = (recommendation_code or "SF00").strip().upper()
    if code == "SF01":
        return 1
    if code == "SF02":
        return 2
    return 0


def build_seller_reply(
    dx: dict[str, Any],
    *,
    seller_fit_line: str,
    actual_work_step: int | None = None,
) -> dict[str, str]:
    """진단 행(dict) + 판매자 선택 핏 → 카톡/톡톡 붙여넣기용 문구."""
    fit = normalize_fit_line(seller_fit_line)
    if fit not in VALID_FIT_LINES:
        raise ValueError("seller_fit_line 은 기본핏, 편한핏, 아주 편한핏 중 하나여야 합니다.")

    code = (dx.get("recommendation_code") or "SF00").strip().upper()
    dx_code = (dx.get("diagnosis_code") or "").strip()
    q4 = int(dx.get("q4") or 235)
    product_id = (dx.get("product_id") or "").strip()
    r_code = (dx.get("r_code") or "").strip()
    p_code = (dx.get("p_code") or "").strip()
    s_code = (dx.get("s_code") or "").strip()

    step = actual_work_step
    if step is None:
        step = _stretch_step_from_sf(code)
    step = max(0, min(3, int(step)))

    stretch_line = ""
    if code in STRETCH_CODES and step in (1, 2):
        stretch_line = f"발볼 늘림 {step}단계 적용을 권장드립니다."
    elif code == "SF00":
        stretch_line = "발볼 늘림 없이 착용 가능한 안내로 확인되었습니다."
    elif code == "SF03":
        stretch_line = "전체 압박이 심한 경우 한 사이즈 크게 주문을 검토해 주세요."
    elif code == "SF04":
        if normalize_q1(str(dx.get("q1") or "")) == Q1_LOOSE:
            stretch_line = (
                "발길이 때문에 크게 신어 헐거우신 경우(참고): 톡톡으로 "
                "한 사이즈 크게 유지 + 앞깔창 보정 안내를 요청해 주세요."
            )
        else:
            stretch_line = "발 핏에 맞춰 사이즈·핏 옵션을 조정해 주세요."
    else:
        stretch_line = "안내 내용을 참고해 주세요."

    profile_note = f"발 프로필 참고: {r_code}/{p_code}/{s_code}" if r_code else ""

    short = (
        f"[맞춤 안내]\n"
        f"진단번호: {dx_code}\n"
        f"핏: {fit} · 사이즈: {q4}mm\n"
        f"{stretch_line}"
    ).strip()

    long_parts = [
        "[엄마신발 맞춤 안내]",
        f"진단번호: {dx_code}",
        "",
        f"▶ 스마트스토어에서 선택해 주세요",
        f"· 핏 옵션: {fit}",
        f"· 사이즈: {q4}mm",
        "",
        f"▶ 안내 요약",
        stretch_line,
    ]
    if code in STRETCH_CODES and step in (1, 2):
        long_parts.append(
            f"주문 후 발볼 늘림 {step}단계는 톡톡/문의로 접수해 주시면 확인 후 진행해 드립니다."
        )
    if product_id:
        long_parts.extend(["", f"(상품: {product_id})"])
    long_parts.extend(
        [
            "",
            "궁금하신 점은 톡톡으로 편하게 남겨 주세요.",
        ]
    )
    long_text = "\n".join(long_parts)

    exchange = ""
    if code in STRETCH_CODES:
        exchange = (
            f"[1회 무료 교환 인증]\n"
            f"진단번호: {dx_code}\n"
            f"핏: {fit} · {q4}mm · 발볼 늘림 {step}단계 안내 확인 · 교환 신청합니다."
        )

    seller_note = profile_note or ""

    return {
        "reply_short": short,
        "reply_long": long_text,
        "reply_exchange": exchange,
        "seller_note": seller_note,
        "suggested_work_step": str(step),
        "seller_fit_line": fit,
    }
