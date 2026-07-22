"""파일럿 UI·결과 고정 문구 — config/pilot_copy.ko.json (레이아웃/Tailwind와 분리)."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
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
)

_CONFIG_PATH = Path(__file__).resolve().parent / "config" / "pilot_copy.ko.json"

PILOT_COPY_VERSION = "20260621-ko-v1"


def _engine_keys() -> dict[str, str]:
    """진단 엔진과 동일 문자열 — JSON의 engine_keys와 반드시 일치."""
    return {
        "q1_tight": Q1_TIGHT,
        "q1_slip": Q1_SLIP,
        "q1_instep": Q1_INSTEP,
        "q1_loose": Q1_LOOSE,
        "q1_none": Q1_NONE,
        "q2_hallux": Q2_HALLUX,
        "q2_ball": Q2_BALL,
        "q2_index": Q2_INDEX,
        "q2_instep": Q2_INSTEP,
        "q2_pinky": Q2_PINKY,
        "q2_none": Q2_NONE,
        "q3_slight": Q3_SLIGHT,
        "q3_mid": Q3_MID,
        "q3_severe": Q3_SEVERE,
        "q3_none": Q3_NONE,
    }


def _default_copy() -> dict[str, Any]:
    k = _engine_keys()
    return {
        "_meta": {
            "version": PILOT_COPY_VERSION,
            "file": "config/pilot_copy.ko.json",
            "edit_hint": "제목·버튼·안내 문구만 자유롭게 수정. engine_keys·steps[].opts 값은 pilot_engine.py와 동일해야 합니다.",
        },
        "engine_keys": k,
        "intro": {
            "title": "당신의 발은 어떤 모양일까요?",
            "tagline": "Every Fit is good",
            "start_button": "내 발 진단 시작하기 →",
        },
        "steps": [
            {
                "key": "q1",
                "title": "평소 어떤 불편함이 있으셨나요?",
                "nextBtn": "내 발 상태 확인하기 →",
                "single": True,
                "opts": [
                    k["q1_tight"],
                    k["q1_slip"],
                    k["q1_instep"],
                    k["q1_loose"],
                    k["q1_none"],
                ],
            },
            {
                "key": "q2",
                "title": "불편하신 부분이 어디 인가요?",
                "hint": "여러 곳을 선택해 주세요.",
                "nextBtn": "추천 계속 받기 →",
                "multi": True,
                "opts": [
                    k["q2_index"],
                    k["q2_instep"],
                    k["q2_pinky"],
                    k["q2_none"],
                ],
            },
            {
                "key": "q3",
                "title": "불편한 정도는 어느 쯤인가요?",
                "nextBtn": "거의 다 됐어요 →",
                "single": True,
                "opts": [
                    k["q3_slight"],
                    k["q3_mid"],
                    k["q3_severe"],
                    k["q3_none"],
                ],
            },
            {
                "key": "q4",
                "title": "보통 어떤 사이즈를 주문하시나요?",
                "nextBtn": "추천 결과 보기 →",
                "size": True,
            },
        ],
        "foot_compare": {
            "block_title": "👣 내 발유형 비교하기",
            "reference_title": "스탠다드 발(보통발)",
            "customer_title": "고객님 발형",
            "pain_note": "빨간 점: Q2에서 고르신 불편 부위(깜빡임·참고). 의료 진단이 아닙니다.",
            "reference_spec": [
                "발유형: 보통발",
                "발볼: 보통",
                "발등: 보통",
                "발길이: 정사이즈",
            ],
            "length_slip": "정사이즈 보다 작음",
            "length_sf04": "정사이즈 또는 약간 긴발",
        },
        "result": {
            "submit_loading": "발 편안 지도를 만들고 있어요…",
            "prec_optional_hint": "더 정확한 발볼 조절이 필요하시면 선택해 주세요.",
            "prec_optional_button": "더 정확한 발볼 조절 받기 (선택)",
            "stretch_prec_note": "복합증상으로 불편함이 많으신 경우 하단 탭 정밀 진단을 추천합니다.",
            "fit_block_title": "핏별 예상 편안함 (참고)",
            "narrative_block_title": "고객님 발 특성 (참고)",
            "tip_fit_title": "핏 추천 TIP",
            "tip_stretch_title": "발볼 늘림 추천 TIP",
            "tip_exchange_title": "무료 사이즈 혜택 안내",
            "tip_guide_section_title": "주문·혜택 안내",
            "tip_row_empty_summary": "자세히 보기",
            "tip_exchange_summary": "진단 복사 후 톡톡 → 1회 교환·2차 보정",
            "exchange_sheet_body": (
                "진단 결과 복사하기를 누른 후 네이버 톡톡 창에 붙여넣기 해주시면, "
                "1회 사이즈 교환 및 2차 사이즈 보정 서비스를 받으실 수 있어요."
            ),
            "exchange_match_hint": (
                "복사한 내용에 진단번호가 포함되어 있어요. "
                "톡톡에 붙여넣어 주시면 주문·진단을 연결해 드립니다."
            ),
            "narrative_q1_slip": [
                "발볼이 넓은 편이어서 발볼에 맞춰 발길이보다 사이즈를 크게 신는 패턴이에요.",
                "헐떡임 보정을 위해 한 사이즈 작게 주문해 주시고 발볼 늘림이나 좀 더 여유로운 핏으로 선택해 보세요.",
            ],
        },
        "common": {
            "next_default": "다음",
            "step_back": "이전 화면으로",
            "select_required": "선택해 주세요.",
            "q2_select_required": "항목을 선택해 주세요.",
        },
        "alerts": {
            "network_error": "네트워크 오류로 진단을 완료하지 못했습니다. 연결을 확인한 뒤 다시 시도해 주세요.",
            "result_error": "결과 화면을 표시하지 못했습니다. 새로고침 후 다시 시도해 주세요.",
            "prec_tab_blocked": "간편 진단 결과로 충분한 경우가 많아요. 통증이 여러 곳이거나 매우 심할 때 이용해 주세요.",
        },
    }


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(base)
    for key, val in override.items():
        if key == "_meta" and isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = {**out[key], **val}
        elif isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], val)
        else:
            out[key] = val
    return out


def load_pilot_copy() -> dict[str, Any]:
    base = _default_copy()
    if not _CONFIG_PATH.is_file():
        return base
    raw = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
    return _deep_merge(base, raw)


def validate_pilot_copy(copy: dict[str, Any] | None = None) -> None:
    """engine_keys가 pilot_engine 상수와 일치하는지 검사."""
    c = copy if copy is not None else load_pilot_copy()
    expected = _engine_keys()
    got = c.get("engine_keys") or {}
    for ek, ev in expected.items():
        if got.get(ek) != ev:
            raise ValueError(
                f"pilot_copy engine_keys.{ek} must match pilot_engine "
                f"(got {got.get(ek)!r}, want {ev!r}). Edit config or revert opts."
            )


def dump_pilot_copy_json() -> str:
    """pilot_ui HTML에 주입할 JSON (ensure_ascii=False → JS UTF-8)."""
    copy = load_pilot_copy()
    validate_pilot_copy(copy)
    return json.dumps(copy, ensure_ascii=False)


def foot_compare_reference_spec_lines() -> list[str]:
    fc = load_pilot_copy().get("foot_compare") or {}
    lines = fc.get("reference_spec")
    if isinstance(lines, list) and lines:
        return [str(x) for x in lines]
    return _default_copy()["foot_compare"]["reference_spec"]


def foot_compare_customer_length_label(q1: str, *, recommendation_code: str = "") -> str:
    from pilot_engine import normalize_q1

    q1n = normalize_q1(q1)
    fc = load_pilot_copy().get("foot_compare") or {}
    code = (recommendation_code or "").strip().upper()
    if code == "SF04":
        return str(fc.get("length_sf04") or "정사이즈 또는 약간 긴발")
    if q1n == Q1_SLIP:
        return str(fc.get("length_slip") or "정사이즈 보다 작음")
    return "정사이즈"


def narrative_q1_slip_lines() -> list[str]:
    res = load_pilot_copy().get("result") or {}
    lines = res.get("narrative_q1_slip")
    if isinstance(lines, list) and lines:
        return [str(x) for x in lines]
    return list(_default_copy()["result"]["narrative_q1_slip"])
