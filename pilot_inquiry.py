"""쿠팡·네이버 판매자 문의용 복사 문구 (파일럿)."""

from __future__ import annotations


def stretch_step_label(recommendation_code: str) -> str | None:
    code = (recommendation_code or "").strip().upper()
    if code == "SF01":
        return "1단계"
    if code == "SF02":
        return "2단계"
    return None


def is_marketplace_channel(channel: str) -> bool:
    ch = (channel or "").strip().lower()
    return ch.startswith("coupang") or ch.startswith("naver")


def is_naver_channel(channel: str) -> bool:
    return (channel or "").strip().lower().startswith("naver")


def build_naver_diagnosis_result_copy(
    *,
    diagnosis_code: str,
    recommendation_code: str,
    shoe_size: int | None,
    recommended_fit_line: str | None = None,
    fit_recommendation_tip: str | None = None,
    stretch_recommendation_tip: str | None = None,
) -> str:
    """네이버 톡톡 붙여넣기용 간편 진단 결과 (교환·보정 이벤트)."""
    lines = [
        "[Every Fit · 발 편안 지도 · 진단 결과]",
        f"진단번호: {diagnosis_code}",
        f"안내 코드: {(recommendation_code or '').strip().upper()}",
    ]
    if shoe_size:
        lines.append(f"주문 사이즈: {int(shoe_size)}mm")
    if recommended_fit_line:
        lines.append(f"추천 핏: {recommended_fit_line}")
    if fit_recommendation_tip:
        tip = fit_recommendation_tip.replace("\n", " / ")
        lines.append(f"핏 추천 TIP: {tip}")
    if stretch_recommendation_tip:
        st = stretch_recommendation_tip.replace("\n", " / ")
        lines.append(f"발볼 늘림 TIP: {st}")
    lines.append("")
    lines.append("위 진단 결과 확인 후 사이즈 교환·핏 보정 상담 부탁드립니다.")
    return "\n".join(lines)


def build_pilot_inquiry_copies(
    *,
    message: str,
    diagnosis_code: str,
    recommendation_code: str,
    channel: str,
    shoe_size: int | None = None,
) -> dict[str, str | None]:
    long_text = f"{message}\n\n진단번호: {diagnosis_code}"
    step = stretch_step_label(recommendation_code)
    short: str | None = None
    naver_exchange: str | None = None
    if step and is_marketplace_channel(channel):
        size_line = f"주문 사이즈: {shoe_size}mm\n" if shoe_size else ""
        platform = "쿠팡" if (channel or "").lower().startswith("coupang") else "스마트스토어"
        short = (
            f"[{platform} 발볼 늘림 요청]\n"
            f"진단번호: {diagnosis_code}\n"
            f"{size_line}"
            f"발볼 늘림 {step} 요청드립니다."
        ).replace("\n\n", "\n")
        if is_naver_channel(channel):
            naver_exchange = (
                f"[1회 무료 교환 인증]\n"
                f"진단번호: {diagnosis_code}\n"
                f"{size_line}"
                f"발볼 안내(늘림 {step}) 확인했습니다. 교환 신청합니다."
            ).replace("\n\n", "\n")
    elif is_marketplace_channel(channel) and (recommendation_code or "").strip().upper() in (
        "SF03",
        "SF04",
        "SF05",
    ):
        platform = "쿠팡" if (channel or "").lower().startswith("coupang") else "스마트스토어"
        size_line = f"주문 사이즈: {shoe_size}mm\n" if shoe_size else ""
        short = (
            f"[{platform} 핏 안내 문의]\n"
            f"진단번호: {diagnosis_code}\n"
            f"{size_line}"
            f"간편 안내 확인 후 맞춤 상담 부탁드립니다."
        ).replace("\n\n", "\n")
    return {
        "inquiry_copy_text": long_text,
        "inquiry_copy_short": short,
        "inquiry_copy_naver_exchange": naver_exchange,
    }
