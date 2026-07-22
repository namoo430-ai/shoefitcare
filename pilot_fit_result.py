"""결과 화면: 발 유형 설명 + 핏별 적합도 + 늘림 안내."""

from __future__ import annotations

from typing import Any

from foot_scores import compute_ux_scores, score_to_comfort_level
from pilot_copy import narrative_q1_slip_lines
from pilot_engine import Q1_LOOSE, Q1_SLIP, STRETCH_CODES, normalize_q1

FIT_LINES = ("기본핏", "편한핏", "아주 편한핏")
FIT_OFFSET = {"기본핏": 0, "편한핏": 1, "아주 편한핏": 2}
LEVEL_LABEL = {1: "낮음", 2: "낮음", 3: "중간", 4: "높음", 5: "높음"}


def engine_stretch_step(recommendation_code: str) -> int:
    code = (recommendation_code or "SF00").strip().upper()
    if code == "SF01":
        return 1
    if code == "SF02":
        return 2
    return 0


def effective_stretch_step(recommendation_code: str, fit_line: str) -> int:
    engine = engine_stretch_step(recommendation_code)
    off = FIT_OFFSET.get(fit_line, 0)
    return max(0, engine - off)


def precision_tab_eligible(
    *,
    recommendation_code: str,
    complex_case: bool,
    p_code: str,
    s_code: str,
) -> bool:
    """파일럿: 정밀 탭 최대 개방(전환율 관측). 필요 없는 고객은 자연 이탈 가정."""
    _ = (recommendation_code, complex_case, p_code, s_code)
    return True


def _is_sf04(code: str) -> bool:
    return (code or "").strip().upper() == "SF04"


def _show_sf04_loose_ui(code: str, q1: str) -> bool:
    """SF04 또는 Q1 여유(헐거움) — 동일 결과 카피."""
    if _is_sf04(code):
        return True
    return normalize_q1(q1) == Q1_LOOSE


def _is_loose_length_path(q1: str, code: str) -> bool:
    if _show_sf04_loose_ui(code, q1):
        return True
    return normalize_q1(q1) == Q1_LOOSE


def _sf04_loose_copy() -> tuple[str, str, list[str]]:
    """(핏 tip, 늘림 tip, 발 특징 narrative). SF04 = 헐거움·좁은발 전용."""
    fit_tip = (
        "칼발: 한 사이즈 크게 신어 헐거우면 → 기본핏(큰 사이즈 유지) + 앞깔창\n"
        "좁은발(길이 맞음): 한 사이즈 작게 하시거나, 기본핏(사이즈 유지) + 앞깔창"
    )
    stretch_tip = (
        "칼발: 기본핏 정사이즈 주문 + 발길이 늘림\n"
        "좁은발(길이 맞음): 발볼 늘림 해당 사항 없음"
    )
    narrative = [
        "길이 때문에 한 사이즈 크게 신으면 헐거움(칼발에 가깝게) 느껴지거나, "
        "발볼이 좁아 정사이즈에서도 여유 있는(좁은발) 패턴일 수 있어요.",
    ]
    return fit_tip, stretch_tip, narrative


def _use_basic_only_bars(code: str, q1: str) -> bool:
    c = (code or "").strip().upper()
    if c == "SF00":
        return True
    if c == "SF04":
        return True
    if normalize_q1(q1) == Q1_LOOSE:
        return True
    return False


def _foot_narrative_lines(
    r_code: str,
    p_code: str,
    s_code: str,
    *,
    q1: str = "",
    recommendation_code: str = "",
) -> list[str]:
    code = (recommendation_code or "").strip().upper()
    if normalize_q1(q1) == Q1_SLIP and not _show_sf04_loose_ui(code, q1):
        return narrative_q1_slip_lines()
    if code == "SF05":
        return [
            "발볼이 넓고 발등이 높은 편으로 느껴지는 패턴이에요.",
            "평소 여러 부위 압박이 있으셨어요.",
            "불편함이 자주 느껴지는 편이에요.",
            "스탠다드 발볼보다 발볼이 여유 있는 신발을 추천합니다.",
        ]
    if _show_sf04_loose_ui(code, q1):
        return _sf04_loose_copy()[2]
    if _is_loose_length_path(q1, code) or (
        code == "SF00" and (r_code or "").upper() == "R3"
    ):
        return [
            "발길이 때문에 한 사이즈 크게 신어 신발이 헐거워 느껴질 수 있는 패턴이에요 (참고)."
        ]

    r = (r_code or "R1").upper()
    p = (p_code or "P0").upper()
    s = (s_code or "S0").upper()
    lines: list[str] = []
    if r in ("R2", "R5"):
        lines.append("발볼이 넓은 편으로 느껴지는 패턴이에요.")
    elif r == "R3":
        lines.append("발볼이 좁은 편으로 느껴지는 패턴이에요.")
    if r in ("R4", "R5"):
        lines.append("발등이 높은 편으로 느껴지는 패턴이에요.")
    pain_bits: list[str] = []
    if p == "P1":
        pain_bits.append("엄지 옆")
    elif p == "P2":
        pain_bits.append("발볼")
    elif p == "P3":
        pain_bits.append("발등")
    elif p == "P4":
        pain_bits.append("새끼발가락 쪽")
    elif p == "P5":
        pain_bits.append("여러 부위")
    if pain_bits:
        lines.append(f"평소 {', '.join(pain_bits)} 압박이 있으셨어요.")
    if s == "S3":
        lines.append("불편함이 꽤 심한 편이에요.")
    elif s == "S2":
        lines.append("불편함이 자주 느껴지는 편이에요.")
    if not lines:
        lines.append("스탠다드 발볼에 비교적 가까운 편안한 패턴이에요.")
    elif r != "R3":
        lines.append("스탠다드 발볼보다 여유가 필요할 수 있어요.")
    return lines


def _preset_fit_comfort(code: str, q1: str, fit_line: str) -> tuple[int, str] | None:
    """고정 막대·라벨 (SF01~03, SF05, SF00/SF04 여유 등)."""
    c = (code or "").strip().upper()
    if c == "SF01":
        presets = {
            "기본핏": (2, "낮음"),
            "편한핏": (5, "높음"),
            "아주 편한핏": (4, "높음"),
        }
        return presets.get(fit_line)
    if c == "SF02":
        presets = {
            "기본핏": (1, "낮음"),
            "편한핏": (4, "높음"),
            "아주 편한핏": (5, "높음"),
        }
        return presets.get(fit_line)
    if c == "SF05":
        presets = {
            "기본핏": (1, "낮음"),
            "편한핏": (4, "높음"),
            "아주 편한핏": (5, "높음"),
        }
        return presets.get(fit_line)
    if c == "SF03":
        presets = {
            "기본핏": (1, "낮음"),
            "편한핏": (3, "중간"),
            "아주 편한핏": (5, "높음"),
        }
        return presets.get(fit_line)
    if _use_basic_only_bars(c, q1):
        if fit_line == "기본핏":
            return (5, "높음")
        return (1, "낮음")
    return None


def _default_recommended_fit_line(code: str) -> str | None:
    c = (code or "").strip().upper()
    if c == "SF01":
        return "편한핏"
    if c == "SF02":
        return "아주 편한핏"
    if c == "SF03":
        return "아주 편한핏"
    if c == "SF05":
        return "편한핏"
    return None


def _fit_tip_comfort_or_very() -> str:
    return "편한 핏이나 아주 편한 핏 제품을 추천드려요."


def _stretch_tip_sf02_lines() -> str:
    return "기본핏 + 발볼 늘림 2단계\n편한핏 + 발볼 늘림 1단계"


def _recommendation_tips(
    code: str,
    *,
    q1: str,
    rec_fit: str,
    shoe_size: int,
    stretch_on_option: bool,
    stretch_option_label: str,
    engine: int,
) -> tuple[str, str]:
    """(핏 추천 tip, 발볼 늘림 추천 tip)."""
    c = (code or "").strip().upper()
    sz = int(shoe_size or 235)
    opt = (stretch_option_label or "발볼 늘림").strip()
    if c == "SF03":
        return (
            "기본핏 제품을 선택하실 경우 한 사이즈 크게 주문하시는 것을 추천드려요.",
            "아주 편한핏 + 발볼 늘림 1단계\n편한핏 + 발볼 늘림 2단계",
        )
    if c == "SF04" or normalize_q1(q1) == Q1_LOOSE:
        fit_tip, stretch_tip, _ = _sf04_loose_copy()
        return fit_tip, stretch_tip
    if _use_basic_only_bars(c, q1) or c == "SF00":
        # SF00 = 늘림 불필요. 앞깔창·헐떡임 안내는 SF04(헐거움) 전용.
        fit_tip = "기본핏 · 평소 사이즈로 주문하시면 됩니다. 발볼 늘림은 필요 없어요."
        return fit_tip, "기본핏 + 발볼 늘림 없음"
    if c in STRETCH_CODES:
        st_rec = effective_stretch_step(c, rec_fit)
        if c == "SF01":
            fit_tip = "편한핏으로 주문하시는 것을 추천드려요."
            stretch_tip = "기본핏 + 발볼 늘림 1단계"
            return fit_tip, stretch_tip
        if c == "SF02":
            return _fit_tip_comfort_or_very(), _stretch_tip_sf02_lines()
        if st_rec == 0:
            fit_tip = f"{rec_fit}으로 주문하시면 추가 발볼 늘림 없이도 편하실 수 있어요."
        elif stretch_on_option:
            fit_tip = f"{rec_fit} + 주문 옵션 「{opt} {st_rec}단계」 · 사이즈 {sz}mm"
        else:
            fit_tip = (
                f"{rec_fit} · 사이즈 {sz}mm로 주문하신 뒤, "
                f"톡톡으로 늘림 {st_rec}단계 접수를 요청해 주세요."
            )
        st_basic = effective_stretch_step(c, "기본핏")
        if st_basic == 0:
            stretch_tip = "기본핏 + 발볼 늘림 없음"
        elif stretch_on_option:
            stretch_tip = f"기본핏 + 옵션 「{opt} {st_basic}단계」"
        else:
            stretch_tip = f"기본핏 + 발볼 늘림 {st_basic}단계"
        return fit_tip, stretch_tip
    if c == "SF05":
        return _fit_tip_comfort_or_very(), _stretch_tip_sf02_lines()
    return (
        f"{rec_fit} 옵션을 참고해 주세요 · 사이즈 {sz}mm",
        "발볼 늘림 필요 여부는 톡톡 문의로 확인해 주세요.",
    )


def _comfort_level_for_fit(
    *,
    recommendation_code: str,
    r_code: str,
    p_code: str,
    s_code: str,
    complex_case: bool,
    fit_line: str,
) -> int:
    base = compute_ux_scores(
        recommendation_code=recommendation_code,
        r_code=r_code,
        p_code=p_code,
        s_code=s_code,
        complex_case=complex_case,
        precision_recommended=False,
    )
    bonus = FIT_OFFSET.get(fit_line, 0) * 9
    score = min(95, base["fit_match_score"] + bonus)
    return score_to_comfort_level(score)


def _order_tip(
    code: str,
    rec_fit: str,
    engine: int,
    shoe_size: int,
    *,
    stretch_on_option: bool,
    stretch_option_label: str,
    q1: str = "",
) -> str:
    sz = int(shoe_size or 235)
    opt = (stretch_option_label or "발볼 늘림").strip()
    if code == "SF03":
        return f"한 사이즈 크게({sz + 5}mm 검토) + {rec_fit} 조합을 참고해 보세요."
    if code == "SF04" or normalize_q1(q1) == Q1_LOOSE:
        fit_tip, _, _ = _sf04_loose_copy()
        return fit_tip.split("\n")[0]
    if code == "SF00":
        return "기본핏 · 평소 사이즈로 주문하시면 됩니다. 발볼 늘림은 필요 없어요."
    if code in STRETCH_CODES:
        st = effective_stretch_step(code, rec_fit)
        if stretch_on_option and st > 0:
            return f"★ {rec_fit} + 주문 옵션 「{opt} {st}단계」 · 사이즈 {sz}mm"
        if st == 0:
            return f"★ {rec_fit}으로 주문하시면 추가 발볼 늘림 없이도 편하실 수 있어요."
        return f"★ {rec_fit} · 사이즈 {sz}mm → 주문 후 톡톡으로 늘림 {st}단계 접수"
    return f"★ {rec_fit} 옵션을 참고해 주세요 · 사이즈 {sz}mm"


def _alt_tip(code: str, rec_fit: str, engine: int, *, stretch_on_option: bool) -> str:
    if code not in STRETCH_CODES or engine == 0:
        return ""
    if stretch_on_option:
        if rec_fit != "기본핏" and engine >= 2:
            return "또는 기본핏 + 옵션에서 늘림 2단계를 선택하실 수 있어요."
        return ""
    if rec_fit == "아주 편한핏":
        if engine >= 2:
            return "또는 기본핏 + 발볼 늘림 2단계를 톡톡으로 요청하실 수 있어요."
        return "또는 기본핏 + 발볼 늘림 1단계를 톡톡으로 요청하실 수 있어요."
    if rec_fit == "편한핏" and engine >= 2:
        return "또는 아주 편한핏으로 주문하시거나, 기본핏 + 늘림 2단계를 검토해 보세요."
    return ""


def talk_sheet_hints(
    *,
    stretch_on_option: bool,
    stretch_option_label: str,
    recommendation_code: str,
    recommended_fit_line: str,
) -> list[str]:
    code = (recommendation_code or "").strip().upper()
    opt = (stretch_option_label or "발볼 늘림").strip()
    st = effective_stretch_step(code, recommended_fit_line)
    hints = [
        "① 아래 [한 줄 복사]를 눌러 주세요.",
        "② [톡톡 열기] 시 네이버 로그인 화면이 나올 수 있어요. 로그인 후 붙여넣어 보내 주세요.",
        "③ 네이버 쇼핑 앱에서 하시면 더 편할 수 있어요.",
    ]
    if code in STRETCH_CODES and st > 0:
        if stretch_on_option:
            hints.insert(
                1,
                f"주문 시 {recommended_fit_line} + 「{opt} {st}단계」 옵션을 선택해 주세요.",
            )
        else:
            hints.insert(
                1,
                f"먼저 {recommended_fit_line}으로 주문하신 뒤, 늘림 {st}단계 접수 문구를 보내 주세요.",
            )
    return hints


def build_fit_result(
    *,
    recommendation_code: str,
    r_code: str,
    p_code: str,
    s_code: str,
    complex_case: bool,
    shoe_size: int,
    stretch_on_option: bool = False,
    stretch_option_label: str = "발볼 늘림",
    exchange_event_active: bool = True,
    q1: str = "",
) -> dict[str, Any]:
    code = (recommendation_code or "SF00").strip().upper()
    lines_out: list[dict[str, Any]] = []
    for fit in FIT_LINES:
        preset = _preset_fit_comfort(code, q1, fit)
        if preset is not None:
            lv, label = preset
            stretch = effective_stretch_step(code, fit) if code in STRETCH_CODES else 0
        else:
            lv = _comfort_level_for_fit(
                recommendation_code=code,
                r_code=r_code,
                p_code=p_code,
                s_code=s_code,
                complex_case=complex_case,
                fit_line=fit,
            )
            label = LEVEL_LABEL.get(lv, "중간")
            stretch = effective_stretch_step(code, fit)
        lines_out.append(
            {
                "fit_line": fit,
                "comfort_level": lv,
                "comfort_label": label,
                "effective_stretch_step": stretch,
            }
        )
    if _use_basic_only_bars(code, q1):
        rec_fit = "기본핏"
    else:
        forced = _default_recommended_fit_line(code)
        if forced:
            rec_fit = forced
        else:
            recommended = max(
                lines_out, key=lambda x: (x["comfort_level"], FIT_OFFSET.get(x["fit_line"], 0))
            )
            rec_fit = recommended["fit_line"]
    engine = engine_stretch_step(code)
    fit_tip, stretch_tip = _recommendation_tips(
        code,
        q1=q1,
        rec_fit=rec_fit,
        shoe_size=shoe_size,
        stretch_on_option=stretch_on_option,
        stretch_option_label=stretch_option_label,
        engine=engine,
    )
    return {
        "narrative_lines": _foot_narrative_lines(
            r_code, p_code, s_code, q1=q1, recommendation_code=code
        ),
        "fit_lines": lines_out,
        "recommended_fit_line": rec_fit,
        "engine_stretch_step": engine,
        "stretch_on_option": stretch_on_option,
        "order_tip": _order_tip(
            code,
            rec_fit,
            engine,
            shoe_size,
            stretch_on_option=stretch_on_option,
            stretch_option_label=stretch_option_label,
            q1=q1,
        ),
        "alt_tip": _alt_tip(code, rec_fit, engine, stretch_on_option=stretch_on_option),
        "fit_recommendation_tip": fit_tip,
        "stretch_recommendation_tip": stretch_tip,
        "talk_sheet_hints": talk_sheet_hints(
            stretch_on_option=stretch_on_option,
            stretch_option_label=stretch_option_label,
            recommendation_code=code,
            recommended_fit_line=rec_fit,
        ),
        "exchange_event_active": exchange_event_active,
        "precision_tab_eligible": precision_tab_eligible(
            recommendation_code=code,
            complex_case=complex_case,
            p_code=p_code,
            s_code=s_code,
        ),
    }
