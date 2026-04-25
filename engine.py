"""
슈핏케어 진단 엔진 (core/engine.py)
=====================================
역할: 기성화 추천 우선 → 발볼늘림 보완 로직
     반품율 감소가 최우선 목표
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import json
from pathlib import Path


# ──────────────────────────────────────────────
# 1. 기성화 제품 카탈로그 (실제 운영시 DB에서 로드)
# ──────────────────────────────────────────────
PRODUCT_CATALOG = {
    "구두": [
        {"id": "dress_slim",  "name": "슬림핏 구두",    "fit": "기본핏",    "width_code": "D",  "toe": "pointed", "notes": "발볼 좁음, 무지외반 비추"},
        {"id": "dress_wide",  "name": "와이드핏 구두",   "fit": "편한핏",    "width_code": "EE", "toe": "round",   "notes": "넓은 발볼 대응"},
        {"id": "dress_extra", "name": "익스트라 구두",   "fit": "아주 편한핏","width_code": "EEE","toe": "round",   "notes": "무지외반·넓은볼 최적"},
    ],
    "로퍼": [
        {"id": "loafer_std",  "name": "스탠다드 로퍼",  "fit": "기본핏",    "width_code": "D",  "toe": "round",   "notes": "기본"},
        {"id": "loafer_wide", "name": "와이드 로퍼",    "fit": "편한핏",    "width_code": "EE", "toe": "round",   "notes": "넓은볼 적합"},
    ],
    "단화": [
        {"id": "flat_basic",  "name": "베이직 단화",    "fit": "기본핏",    "width_code": "D",  "toe": "round",   "notes": "기본"},
        {"id": "flat_wide",   "name": "와이드 단화",    "fit": "편한핏",    "width_code": "EE", "toe": "wide",    "notes": "넓은볼 편안"},
    ],
    "운동화": [
        {"id": "sneaker_std", "name": "스탠다드 운동화", "fit": "기본핏",    "width_code": "D",  "toe": "round",   "notes": "기본"},
        {"id": "sneaker_wide","name": "와이드 운동화",   "fit": "편한핏",    "width_code": "EE", "toe": "round",   "notes": "넓은볼·발등 높음"},
        {"id": "sneaker_xtra","name": "익스트라 운동화", "fit": "아주 편한핏","width_code": "EEE","toe": "round",   "notes": "무지외반·복합 증상"},
    ],
}

# 235mm 기준 내부 발볼(cm) 컷오프
# 요청 반영: 로퍼/단화 = 기본 8.0 / 편한 8.2 / 아주편한 8.5
BALL_WIDTH_GUIDE_CM = {
    "구두": {"기본핏": 8.0, "편한핏": 8.2, "아주 편한핏": 8.5},
    "로퍼": {"기본핏": 8.0, "편한핏": 8.2, "아주 편한핏": 8.5},
    "단화": {"기본핏": 8.0, "편한핏": 8.2, "아주 편한핏": 8.5},
    "운동화": {"기본핏": 8.2, "편한핏": 8.5, "아주 편한핏": 8.5},
}


def _load_rules_config() -> dict:
    """rules_v1.json 로드. 없거나 손상 시 기본값 사용."""
    rules_path = Path(__file__).with_name("rules_v1.json")
    if not rules_path.exists():
        return {}
    try:
        return json.loads(rules_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


RULES_CONFIG = _load_rules_config()
_DEFAULT_FIT_SCALE = {"기본핏": 0, "편한핏": 1, "아주 편한핏": 2}
FIT_SCALE = RULES_CONFIG.get("meta", {}).get("fit_scale", _DEFAULT_FIT_SCALE)
SIZE_STEP_MM = int(RULES_CONFIG.get("meta", {}).get("size_step_mm", 5))
COMPOSITE_CONSULT_SCORE = int(RULES_CONFIG.get("thresholds", {}).get("composite_consult_score", 4))
_stretch_raw = RULES_CONFIG.get("stretch_equivalence", {})
STRETCH_EQUIVALENCE = {
    int(k): int(v) for k, v in _stretch_raw.items()
} if _stretch_raw else {1: SIZE_STEP_MM, 2: SIZE_STEP_MM * 2, 3: SIZE_STEP_MM * 3}

# ──────────────────────────────────────────────
# 2. 데이터 클래스 정의
# ──────────────────────────────────────────────
@dataclass
class CustomerInput:
    """고객 입력 원본 (변경 없이 보존 → RAG 원문 데이터)"""
    session_id: str
    preferred_style: str        # "기본핏" | "편한핏" | "아주 편한핏"
    foot_issues: list[str]      # ["넓음", "무지외반", ...]
    wide_severity: str          # "0" | "1"(약간) | "2"(많이)
    hallux_severity: str        # "0" | "1" | "2" | "3"
    instep_severity: str        # "0" | "1" | "2" | "3"
    toe_detail: str             # "0" | "1" | "2" | "3"
    design: str                 # "구두" | "로퍼" | ...
    original_size: int          # mm
    fit_experience: str         # "잘 맞음" | "헐떡임" | "꽉 껴서"
    shop_id: str = "default_shop"
    policy_version: str = "v1"
    # 1차 분기: 발길이·발볼 실측 가능 여부
    measurement_available: bool = False
    foot_length_mm: Optional[int] = None
    foot_ball_width_mm: Optional[float] = None
    instep_circumference_mm: Optional[float] = None
    # 꽉낌(Q5-1) 후속: 한 치수 업 착화 시 뒤꿈치 헐떡임 여부 → 복합점수 보정
    # True=헐떡임 있었음(보수), False=없었음(볼 폭 이슈 가중), None=미응답·해당 없음
    heel_slip_when_one_size_up: Optional[bool] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class DiagnosisResult:
    """진단 결과 (분석 산출물)"""
    session_id: str
    # --- 기성화 추천 (1순위) ---
    recommended_product_id: str
    recommended_product_name: str
    recommended_fit: str
    recommendation_reason: str
    ready_made_option: str
    stretch_option: str
    ready_made_possible: bool   # 기성화만으로 해결 가능 여부
    # --- 사이즈 보정 ---
    original_size: int
    final_size: int
    size_adjusted: bool
    # --- 발볼늘림 (2순위, 보완) ---
    stretch_step: int           # 0~3
    stretch_mm: float
    stretch_reason: str
    additional_works: list[str]
    # --- 상담 여부 ---
    is_consult: bool
    consult_reason: str
    # --- 메타 ---
    design: str
    failure_experience: str
    composite_score: int
    measurement_available: bool
    recommendation_path: str    # "measured" | "experience"
    confidence_score: float     # 0.0 ~ 1.0
    shop_id: str = "default_shop"
    policy_version: str = "v1"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# ──────────────────────────────────────────────
# 3. 핵심 진단 엔진
# ──────────────────────────────────────────────
class DiagnosisEngine:
    """
    우선순위:
      1) 기성화 추천 (데이터 기반)
      2) 기성화로 해결 불가한 부분만 발볼늘림으로 보완
      3) 복합·심한 증상은 상담으로 전환
    """

    FIT_ORDER = [name for name, _ in sorted(FIT_SCALE.items(), key=lambda item: item[1])]
    STRETCH_TO_SIZE_UP_MM = STRETCH_EQUIVALENCE
    FIT_SCORE = {"기본핏": 0, "편한핏": 1, "아주 편한핏": 2}

    def run(self, inp: CustomerInput) -> DiagnosisResult:
        issues = set(inp.foot_issues)
        path = "measured" if inp.measurement_available else "experience"
        confidence = self._compute_confidence(inp)
        composite_score = self._composite_score(inp, issues)

        # Step 1. 사이즈 보정
        final_size, size_adjusted = self._adjust_size(inp, issues)

        # Step 2. 기성화 추천 (최우선)
        product, fit, reason, ready_made = self._recommend_product(inp, issues)
        ready_made_option = ""
        stretch_option = ""

        # 경험 경로 + 낮은 신뢰도는 보수 추천으로 리스크 완화
        if path == "experience" and confidence < 0.72 and inp.fit_experience != "잘 맞음":
            product, fit, reason, ready_made = self._apply_experience_conservative_fit(
                inp, product, fit, reason, ready_made, confidence
            )

        # Step 2-1. 실측 경로 + "꽉낌"은 길이/폭 원인을 분리해 고객이 선택하도록 옵션 제공
        # 단, 앞코 발끝 닿음(발길이 늘림 필요)과 복합이면 무조건 +5mm를 유지한다.
        choice_mode = False
        choice_note = ""
        is_toe_length_plus_tight = ("꽉" in inp.fit_experience) and (inp.toe_detail == "1")
        if path == "measured" and ("꽉" in inp.fit_experience) and (not is_toe_length_plus_tight):
            choice_mode = True
            choice_note = self._build_measured_tight_choice_note(inp, issues)
            reason = reason + choice_note
            # 선택 모드에서는 엔진이 일방적으로 사이즈/가공을 확정하지 않음 (분쟁/반품 방어)
            final_size, size_adjusted = inp.original_size, False
        elif is_toe_length_plus_tight:
            reason = reason + " [앞코 발끝 닿음+꽉낌 복합: 한 사이즈 업(+5mm) 고정]"

        # Step 2-2. 경험 경로 + 꽉낌 + (복합점수>=3 또는 발등 이슈): 한 사이즈 업 우선
        if path == "experience" and ("꽉" in inp.fit_experience):
            should_upsize = self._should_upsize_for_tight(inp, issues)
            option_product = self._find_by_fit(PRODUCT_CATALOG.get(inp.design, []), "아주 편한핏")
            if should_upsize and option_product:
                product = option_product
                fit = "아주 편한핏"
                reason = self._tight_upsize_reason(inp, issues)
            elif not should_upsize:
                reason = "볼 압박(꽉낌) 단독: 사이즈 업 없이 핏/가공 보정 우선"

        # Step 3. 상담 필요 여부 판단
        is_consult, consult_reason = self._check_consult(inp, issues, confidence, path)

        # Step 4. 발볼늘림 보완 결정
        if choice_mode and not is_consult:
            stretch_step, stretch_mm, stretch_reason = 0, 0.0, "고객 선택 후 적용(옵션 A/B 중 선택)"
        else:
            stretch_step, stretch_mm, stretch_reason = self._decide_stretch(
                inp, issues, ready_made, is_consult
            )

        # Step 5. 추가 가공
        additional = self._additional_works(inp, issues, stretch_step, size_adjusted)
        if choice_mode:
            additional.append("선택 옵션 안내: A(사이즈 +5mm + 앞깔창) 또는 B(정사이즈 + 발볼늘림 1단계)")

        return DiagnosisResult(
            session_id=inp.session_id,
            recommended_product_id=product["id"],
            recommended_product_name=product["name"],
            recommended_fit=fit,
            recommendation_reason=reason,
            ready_made_option=ready_made_option,
            stretch_option=stretch_option,
            ready_made_possible=ready_made,
            original_size=inp.original_size,
            final_size=final_size,
            size_adjusted=size_adjusted,
            stretch_step=stretch_step,
            stretch_mm=stretch_mm,
            stretch_reason=stretch_reason,
            additional_works=additional,
            is_consult=is_consult,
            consult_reason=consult_reason,
            design=inp.design,
            failure_experience=inp.fit_experience,
            composite_score=composite_score,
            measurement_available=inp.measurement_available,
            recommendation_path=path,
            confidence_score=confidence,
            shop_id=inp.shop_id,
            policy_version=inp.policy_version,
        )

    # ── 내부 메서드 ──────────────────────────

    def _compute_confidence(self, inp: CustomerInput) -> float:
        """실측 가능 여부/입력 완성도 기반 신뢰도 계산."""
        if inp.measurement_available:
            score = 0.88
            if inp.foot_length_mm is not None and inp.foot_ball_width_mm is not None:
                score += 0.07
            # 발볼 입력이 비정상 범위면 신뢰도 하향 (단위 혼동 가능성)
            ball_cm = self._normalize_ball_cm(inp.foot_ball_width_mm)
            if inp.foot_ball_width_mm is not None and ball_cm is None:
                score -= 0.18
            return min(score, 0.95)

        score = 0.58
        if inp.fit_experience == "잘 맞음":
            score += 0.10
        if "무지외반" in inp.foot_issues and inp.hallux_severity in ("2", "3"):
            score -= 0.08
        if "발등 높음" in inp.foot_issues and inp.instep_severity in ("2", "3"):
            score -= 0.06
        return max(0.35, min(score, 0.82))

    def _apply_experience_conservative_fit(
        self,
        inp: CustomerInput,
        product: dict,
        fit: str,
        reason: str,
        ready_made: bool,
        confidence: float,
    ) -> tuple[dict, str, str, bool]:
        catalog = PRODUCT_CATALOG.get(inp.design, [])
        if not catalog:
            return product, fit, reason, ready_made

        try:
            idx = self.FIT_ORDER.index(fit)
        except ValueError:
            idx = 1

        if idx >= len(self.FIT_ORDER) - 1:
            return product, fit, reason + " (경험기반·보수 유지)", ready_made

        new_fit = self.FIT_ORDER[idx + 1]
        alt = self._find_by_fit(catalog, new_fit)
        if not alt:
            return product, fit, reason, ready_made

        extra = f" [경험기반·신뢰도 {confidence:.2f}: {new_fit} 보수 보정]"
        return alt, new_fit, reason + extra, ready_made

    def _build_measured_tight_choice_note(self, inp: CustomerInput, issues: set) -> str:
        """
        실측 경로에서 '꽉낌' 발생 시:
        - 길이가 부족하면: 한 사이즈 업 + 앞깔창(안정화)
        - 길이가 충분하면: 정사이즈 유지 + 발볼늘림(폭 문제 해결)
        고객이 선택할 수 있도록 옵션을 텍스트로 제공.
        """
        foot_len = inp.foot_length_mm
        if foot_len is None:
            return " [실측값 불충분: 옵션 A(사이즈+5mm+앞깔창) vs 옵션 B(정사이즈+발볼늘림) 중 선택]"

        length_gap = inp.original_size - foot_len  # (+) 신발이 발보다 긴 정도
        a = f"A) {inp.original_size + 5}mm + 앞깔창 보정(길이 여유 확보 후 헐떡임 방지)"
        b = "B) " + f"{inp.original_size}mm 유지 + 발볼늘림 1단계(2.5mm)"
        # 폭 이슈가 명확하면 B가 실전 성공률이 높음
        width_bias = ("넓음" in issues) or ("무지외반" in issues)

        if length_gap <= 6:
            default = "A 권장(실측 대비 길이 여유가 적음)"
        elif length_gap >= 13:
            default = "B 권장(실측 대비 길이 여유가 충분, 폭 문제 가능성↑)"
        else:
            default = "A/B 모두 가능(고객님 선호 착화감으로 선택)"

        if width_bias and length_gap >= 10:
            default = "B 우선 권장(넓은볼/무지외반 + 길이 여유 → 폭 보정이 효율적)"

        return f" [꽉낌(실측): length_gap={length_gap}mm → {default} / {a} / {b}]"

    def _adjust_size(self, inp: CustomerInput, issues: set) -> tuple[int, bool]:
        # 1) 헐떡임(뒤꿈치 뜸)은 과대 사이즈 가능성이 높아 -5mm 보정 우선
        if "헐떡임" in inp.fit_experience:
            return inp.original_size - 5, True
        # 2) 발등은 예외: 점수와 별개로 한 사이즈 업 우선
        if "발등 높음" in issues:
            return inp.original_size + 5, True
        # 3) 꽉낌은 길이는 대체로 충족으로 보고 과한 업사이즈를 제한
        #    - Q5-3 응답을 직접 분기 트리거로 사용한다.
        if "꽉" in inp.fit_experience:
            if inp.heel_slip_when_one_size_up is False:
                return inp.original_size + 5, True
            if inp.heel_slip_when_one_size_up is True:
                return inp.original_size - 5, True
            # 정보가 불확실(해본 적 없음)할 때는 심한 무지외반만 안전측으로 업사이즈
            if inp.heel_slip_when_one_size_up is None and inp.hallux_severity == "3":
                return inp.original_size + 5, True
        return inp.original_size, False

    def _recommend_product(
        self, inp: CustomerInput, issues: set
    ) -> tuple[dict, str, str, bool]:
        catalog = PRODUCT_CATALOG.get(inp.design, [])
        if not catalog:
            return {"id": "unknown", "name": "미등록 디자인"}, "기본핏", "카탈로그 없음", False

        hallux = inp.hallux_severity
        instep = inp.instep_severity

        # 심한 복합증상 → 기성화 한계
        if "무지외반" in issues and hallux == "3":
            # EEE 폭 제품 우선 탐색
            product = self._find_by_width(catalog, "EEE") or catalog[-1]
            return (
                product,
                "아주 편한핏",
                "무지외반 심함: 가장 넓은 폭 기성화 선택, 발볼늘림 추가 필요",
                False,  # 기성화만으로 부족 → 가공 필요
            )

        if "넓음" in issues and "무지외반" in issues:
            product = self._find_by_width(catalog, "EE") or catalog[-1]
            return product, "편한핏", "넓은볼+무지외반: EE 폭 기성화로 1차 해결", True

        if "넓음" in issues:
            product = self._find_by_width(catalog, "EE") or catalog[-1]
            return product, "편한핏", "넓은 발볼: EE 폭 기성화 추천", True

        if "무지외반" in issues:
            product = self._find_by_width(catalog, "EE") or catalog[-1]
            return product, "편한핏", "무지외반: EE 폭 기성화 추천", True

        if "발등 높음" in issues and instep == "3":
            # 발등 심함은 기성화 한계
            product = self._find_by_width(catalog, "EE") or catalog[-1]
            return product, "편한핏", "발등 심함: 기성화 + 상담 필요", False

        # Q5-1 "잘 맞음"이면 고객이 선택한 Q5 앵커 핏을 우선 반영
        if inp.fit_experience == "잘 맞음":
            anchor_fit = inp.preferred_style if inp.preferred_style in self.FIT_ORDER else "편한핏"
            anchor_product = self._find_by_fit(catalog, anchor_fit)
            if anchor_product:
                return anchor_product, anchor_fit, "Q5 기준사이즈/핏 앵커 기반 고정 추천", True

        # 실측 발볼값이 있는 경우: 디자인별 내부 기준표 우선 적용
        measured_fit = self._fit_from_measured_ball_width(inp)
        if measured_fit:
            measured_product = self._find_by_fit(catalog, measured_fit)
            if measured_product:
                reason = f"실측 발볼 기준({inp.design} {measured_fit})으로 추천"
                return measured_product, measured_fit, reason, True
            # 아주 편한핏 상품이 없는 디자인은 편한핏으로 대체 + 보완 가공
            if measured_fit == "아주 편한핏":
                fallback = self._find_by_fit(catalog, "편한핏") or catalog[-1]
                return (
                    fallback,
                    "편한핏",
                    f"실측상 아주 편한핏 권장이나 상품 미보유: 편한핏 대체 + 발볼 보완 추천",
                    False,
                )

        # 기본 케이스: Q5 기준사이즈(앵커)에서 무리 없는 기본핏 우선
        product = self._find_by_fit(catalog, "기본핏") or catalog[0]
        return product, "기본핏", "기준사이즈(Q5) 앵커 기반 기본핏 추천", True

    def _find_by_width(self, catalog: list, width_code: str) -> Optional[dict]:
        for p in catalog:
            if p["width_code"] == width_code:
                return p
        return None

    def _find_by_fit(self, catalog: list, fit: str) -> Optional[dict]:
        for p in catalog:
            if p["fit"] == fit:
                return p
        return None

    def _fit_from_measured_ball_width(self, inp: CustomerInput) -> Optional[str]:
        """실측 발볼(입력값)과 디자인별 기준표로 핏 단계 산출."""
        if not inp.measurement_available or inp.foot_ball_width_mm is None:
            return None

        guide = BALL_WIDTH_GUIDE_CM.get(inp.design)
        if not guide:
            return None

        ball_cm = self._normalize_ball_cm(inp.foot_ball_width_mm)
        if ball_cm is None:
            # 단위 혼동/이상치면 실측 발볼 자동판정은 건너뛰고 다른 룰로 추천
            return None

        if ball_cm >= guide["아주 편한핏"]:
            return "아주 편한핏"
        if ball_cm >= guide["편한핏"]:
            return "편한핏"
        return "기본핏"

    def _normalize_ball_cm(self, raw: Optional[float]) -> Optional[float]:
        """
        발볼 입력값을 cm 너비로 정규화.
        허용 입력:
        - 9.2 같은 cm 너비
        - 92 같은 mm 너비
        - 228 같은 mm 둘레(자동 환산: /26)
        """
        if raw is None:
            return None
        if raw <= 0:
            return None

        if raw < 20:
            ball_cm = raw
        elif raw < 150:
            ball_cm = raw / 10.0
        else:
            # 둘레(mm) 추정값 -> 너비(cm) 근사
            ball_cm = raw / 26.0

        # 발볼 너비 합리 범위 벗어나면 무효 처리
        if not (7.0 <= ball_cm <= 11.5):
            return None
        return ball_cm

    def _check_consult(
        self,
        inp: CustomerInput,
        issues: set,
        confidence: float,
        path: str,
    ) -> tuple[bool, str]:
        # 운영 정책: 꽉낌은 Q5-3 응답 기반 사이즈 분기 우선.
        if "꽉" in inp.fit_experience and self._should_upsize_for_tight(inp, issues):
            return False, ""
        if "무지외반" in issues and inp.hallux_severity == "3":
            return True, "무지외반 심함: 돌출부 형태 직접 확인 필요"
        if "발등 높음" in issues and inp.instep_severity == "3":
            return True, "발등 심함: 발등 높이 직접 측정 필요"
        hallux_score = self._safe_int(inp.hallux_severity)
        combo_score = hallux_score + (1 if "넓음" in issues else 0)
        if ("무지외반" in issues and "넓음" in issues) and combo_score >= COMPOSITE_CONSULT_SCORE:
            return True, f"무지외반+넓은발볼 복합 점수({combo_score})로 상담 권장"
        if path == "experience" and confidence < 0.62:
            if "넓음" in issues and "무지외반" in issues:
                return True, "실측 없음·복합 증상: 전화 상담 후 주문 권장"
            if "발등 높음" in issues and inp.instep_severity in ("1", "2"):
                return True, "실측 없음·발등 이슈: 상담 후 맞춤 권장"
        return False, ""

    def _decide_stretch(
        self,
        inp: CustomerInput,
        issues: set,
        ready_made: bool,
        is_consult: bool,
    ) -> tuple[int, float, str]:
        """
        기성화로 해결 가능하면 가공 최소화.
        기성화 부족분만 가공으로 보완.
        """
        if is_consult:
            return 0, 0.0, "상담 후 결정"

        # 심한 무지외반 → 기성화 부족 → 3단계 가공
        if "무지외반" in issues and inp.hallux_severity == "3":
            return 3, 7.5, self._build_stretch_reason(inp, 3, 7.5, "기성화 EEE 폭으로도 부족한 돌출부 핀포인트 보정")

        # 헐떡임으로 사이즈 다운 → 줄어든 볼 공간 보완 (1단계)
        if "헐떡임" in inp.fit_experience and ("넓음" in issues or "무지외반" in issues):
            reason = "사이즈 다운 보상: 줄어든 볼 공간 1단계 보완"
            # -5mm 다운 후 1단계(2.5mm) 보정은 체감상 원래 신던 사이즈 폭(앵커)로 안내
            reason += f" (약 2.5mm 확장, 발볼 체감은 {inp.original_size}mm 사이즈 수준)"
            if inp.design == "구두":
                reason += " [구두 기준: 기본핏 8.0 -> 편한핏 8.2]"
            return 1, 2.5, reason

        # 꽉낌은 Q5-3 응답 기반으로 늘림 우선순위를 부여
        if "꽉" in inp.fit_experience:
            if inp.heel_slip_when_one_size_up is False:
                return 0, 0.0, "업사이즈(한 치수 업) 수용 가능: 과늘림 방지를 위해 추가 늘림 비활성화"
            if inp.heel_slip_when_one_size_up is True:
                if "앞코" in issues:
                    return 1, 2.5, self._build_stretch_reason(inp, 1, 2.5, "업사이즈 헐떡임 이력: 보수 사이즈 + 앞코/볼 압박 완화 보정")
                return 0, 0.0, "업사이즈 헐떡임 이력: 보수 사이즈 우선, 추가 늘림 최소화"
            # 해본 적 없음/모름: 심한 무지외반은 3단계 보정 유지
            if inp.heel_slip_when_one_size_up is None and inp.hallux_severity == "3":
                return 3, 7.5, self._build_stretch_reason(inp, 3, 7.5, "정보 불확실 + 무지외반 심함: 3단계 보정")

            applied = self._applied_score(inp, issues)
            if applied >= 3:
                return 0, 0.0, "꽉낌 + 적용점수 3이상: 한 사이즈 업(+5mm) 우선"
            if applied == 1:
                return 1, 2.5, self._build_stretch_reason(inp, 1, 2.5, "적용점수 1점: 1단계 늘림")
            if applied == 2:
                return 2, 5.0, self._build_stretch_reason(inp, 2, 5.0, "적용점수 2점: 2단계 늘림")

        # 넓은볼+무지외반(경/중)은 기성화와 별개로 2단계 보완 가능
        if "넓음" in issues and "무지외반" in issues and inp.hallux_severity in ("1", "2"):
            return 2, 5.0, self._build_stretch_reason(inp, 2, 5.0, "기성화 보완: 2단계 넓힘 추가")

        # 기성화만으로 해결 가능하면 가공 없음
        if ready_made:
            return 0, 0.0, "기성화로 충분히 해결 가능"

        return 0, 0.0, "가공 불필요"

    def _additional_works(
        self,
        inp: CustomerInput,
        issues: set,
        stretch_step: int,
        size_adjusted: bool,
    ) -> list[str]:
        works = []
        if "앞코" in issues:
            if inp.toe_detail == "1":
                works.append("발길이 늘림")
            elif inp.toe_detail == "3":
                # 꽉낌으로 +5mm 사이즈 업이 이미 적용된 경우 핀포인트 가공은 중복 제외
                if not ("꽉" in inp.fit_experience and size_adjusted):
                    works.append("핀포인트 앞코 늘림")
            else:
                # 요청 반영: 앞코 너비 늘림은 발볼늘림 적용 시에만 추가
                if stretch_step > 0:
                    works.append("앞코 너비 늘림")
        if "발등 높음" in issues and inp.instep_severity in ("1", "2"):
            works.append("발등 높이 늘림")
        if "무지외반" in issues and inp.hallux_severity == "3":
            works.append("핀포인트 무지외반 늘림")
        return works

    def _build_stretch_reason(self, inp: CustomerInput, step: int, stretch_mm: float, base: str) -> str:
        """발볼 늘림 단계와 체감 안내. 2단계는 폭 보정만 하므로 발볼 체감은 한 사이즈(+5mm)에 가깝게 서술."""
        size_up_mm = self.STRETCH_TO_SIZE_UP_MM.get(step, 0)
        if step == 2:
            # 실제 주문 사이즈는 유지하고 폭만 넓히므로, 체감은 '한 치수 업' 수준으로 안내 (두 치수 과장 방지)
            equivalent_size = inp.original_size + SIZE_STEP_MM
            note = (
                f" (약 {stretch_mm:.1f}mm 확장, 발볼 체감은 한 사이즈 업(+{SIZE_STEP_MM}mm, "
                f"{equivalent_size}mm급)에 가깝게 보정)"
            )
        else:
            equivalent_size = inp.original_size + size_up_mm
            note = f" (약 {stretch_mm:.1f}mm 확장, 발볼 체감은 {equivalent_size}mm 사이즈 수준)"
        # 구두 기준 명시: 1단계는 기본핏 8.0 -> 편한핏 8.2로 해석
        if inp.design == "구두" and step == 1:
            note += " [구두 기준: 기본핏 8.0 -> 편한핏 8.2]"
        return base + note

    def _safe_int(self, val: str, default: int = 0) -> int:
        try:
            return int(val)
        except Exception:
            return default

    def _composite_score(self, inp: CustomerInput, issues: set) -> int:
        """운영 점수: Q2 증상점수 + Q5 핏점수 (1~6 캡)."""
        return self._policy_total_score(inp, issues)

    def _policy_total_score(self, inp: CustomerInput, issues: set) -> int:
        q2 = self._q2_score(inp, issues)
        q5_fit = self._fit_score(inp)
        total = q2 + q5_fit
        return max(0, min(total, 6))

    def _applied_score(self, inp: CustomerInput, issues: set) -> int:
        """실행 점수: 복합점수에서 Q5 핏 익숙도를 차감해 보정 강도를 계산."""
        total = self._policy_total_score(inp, issues)
        return max(0, total - self._fit_score(inp))

    def _fit_score(self, inp: CustomerInput) -> int:
        return self.FIT_SCORE.get(inp.preferred_style, 1)

    def _q2_score(self, inp: CustomerInput, issues: set) -> int:
        score = 0
        if "넓음" in issues:
            wide = self._safe_int(inp.wide_severity, default=1)
            score += 2 if wide >= 2 else 1
        if "무지외반" in issues:
            score += max(1, min(self._safe_int(inp.hallux_severity, default=1), 3))
        if "통통함" in issues:
            score += 1
        # 발등/앞코는 예외처리: 점수 미부여
        return max(0, min(score, 6))

    def _should_upsize_for_tight(self, inp: CustomerInput, issues: set) -> bool:
        """
        꽉낌 시 사이즈 업 조건(Q5-3 직분기):
        - Q5-3 = 2(업해도 헐떡임 없음)
        - Q5-3 = 3(모름) + 무지외반 심함
        """
        if inp.heel_slip_when_one_size_up is False:
            return True
        if inp.heel_slip_when_one_size_up is None and inp.hallux_severity == "3":
            return True
        return False

    def _tight_upsize_reason(self, inp: CustomerInput, issues: set) -> str:
        """꽉낌 업사이즈 사유를 Q5-3 응답 중심으로 설명한다."""
        if inp.heel_slip_when_one_size_up is False:
            return "볼 압박(꽉낌) + 업사이즈 헐떡임 없음: 같은 핏라인 한 사이즈 업(+5mm) 추천"
        if inp.heel_slip_when_one_size_up is None and inp.hallux_severity == "3":
            return "볼 압박(꽉낌) + 정보 불확실 + 무지외반 심함: 한 사이즈 업(+5mm) 안전 권장"
        return "볼 압박(꽉낌): 업사이즈 여부는 보수적으로 판단"

    def _build_anchor_tight_options(self, inp: CustomerInput) -> tuple[str, str]:
        """
        Q5-0 앵커가 편한핏이고 꽉낌일 때 제안:
        - 기성화: 아주 편한핏 라인
        - 늘림: 편한핏 + 1단계 또는 기본핏 + 2단계
        """
        catalog = PRODUCT_CATALOG.get(inp.design, [])
        rm = self._find_by_fit(catalog, "아주 편한핏")
        cf = self._find_by_fit(catalog, "편한핏")
        bf = self._find_by_fit(catalog, "기본핏")

        if rm:
            ready = f"기성화 옵션: {rm['name']}(아주 편한핏) 권장"
        else:
            fallback = cf or bf or {"name": "해당 라인 미보유"}
            ready = f"기성화 옵션: 아주 편한핏 미보유 → {fallback['name']} 대체"

        stretch_items = []
        if cf:
            stretch_items.append(f"편한핏({cf['name']}) + 발볼늘림 1단계(2.5mm)")
        if bf:
            stretch_items.append(f"기본핏({bf['name']}) + 발볼늘림 2단계(5.0mm)")
        if not stretch_items:
            stretch_items.append("늘림 옵션: 라인 확인 필요(관리자 상담)")

        stretch = "늘림 옵션: " + " / ".join(stretch_items)
        return ready, stretch
