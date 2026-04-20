"""
슈핏케어 세션 상태 관리 (core/session.py)
==========================================
역할:
  - 챗봇 대화 흐름의 상태를 관리 (현재 CLI, 추후 Kakao/Slack/Web 전환 가능)
  - 어느 채널에서 실행해도 동일한 상태 기계(State Machine) 동작
  - 중단된 대화 재개 지원

상태 흐름:
  Q_ENTRY → (1) 상품 선행: Q_DESIGN → Q_FOOT → Q_FOOT_DETAIL(선택) → Q_SIZE …
         → (2) 기존: Q_MEAS → Q_MEAS_INPUT(선택) → Q_FOOT → Q_FOOT_DETAIL(선택) → Q_DESIGN
        → Q_SIZE → Q_SIZE_FIT → Q_FIT_EXP
        → (꽉낌=3) Q_TIGHT_CONFIRM_SIZE → Q_TIGHT_REVISE_SIZE(선택) → Q_TIGHT_HEEL_ON_UP
        → DIAGNOSING → RESULT → DONE
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import uuid
import json


# ──────────────────────────────────────────────
# 1. 상태 정의
# ──────────────────────────────────────────────
class SessionState(str, Enum):
    START         = "START"
    Q_ENTRY       = "Q_ENTRY"         # 진입: 상품 선행 vs 실측 우선
    Q_MEAS        = "Q_MEAS"          # Q0: 발길이·발볼 실측 가능 여부 (1차 분기)
    Q_MEAS_INPUT  = "Q_MEAS_INPUT"    # Q0-1: 실측값 (가능한 경우)
    Q_FOOT        = "Q_FOOT"          # Q2: 발 형태
    Q_FOOT_DETAIL = "Q_FOOT_DETAIL"   # Q2-1: 세부 증상 (조건부)
    Q_DESIGN      = "Q_DESIGN"        # Q4: 디자인
    Q_SIZE        = "Q_SIZE"          # Q5: 사이즈
    Q_SIZE_FIT    = "Q_SIZE_FIT"      # Q5-0: 최근 구매 제품의 핏 라인
    Q_FIT_EXP     = "Q_FIT_EXP"      # Q5-1: 착화 경험
    Q_TIGHT_CONFIRM_SIZE = "Q_TIGHT_CONFIRM_SIZE"   # 꽉낌: 기준 사이즈 확인
    Q_TIGHT_REVISE_SIZE  = "Q_TIGHT_REVISE_SIZE"    # 꽉낌: 사이즈 재입력
    Q_TIGHT_HEEL_ON_UP   = "Q_TIGHT_HEEL_ON_UP"     # 꽉낌: 한 치수 업 시 헐떡임(복합 보정)
    DIAGNOSING    = "DIAGNOSING"      # 분석 중
    RESULT        = "RESULT"          # 결과 출력
    AWAIT_CONSULT = "AWAIT_CONSULT"   # 상담 대기
    DONE          = "DONE"            # 완료


# ──────────────────────────────────────────────
# 2. 세션 데이터 클래스
# ──────────────────────────────────────────────
@dataclass
class ChatSession:
    """
    단일 고객 대화 세션.
    직렬화(JSON) 가능 → Redis / DB / 파일 어디에나 저장 가능
    """
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    state: SessionState = SessionState.START
    channel: str = "cli"              # "cli" | "kakao" | "web" | "slack"
    customer_id: Optional[str] = None # 로그인 사용자면 연결
    shop_id: str = "default_shop"
    policy_version: str = "v1"

    # 수집된 답변 (None = 아직 미입력)
    preferred_style:  Optional[str]       = None
    foot_issues:      Optional[list[str]] = None
    hallux_severity:  str = "0"
    wide_severity:    str = "0"
    instep_severity:  str = "0"
    toe_detail:       str = "0"
    design:           Optional[str]       = None
    original_size:    Optional[int]       = None
    fit_experience:   Optional[str]       = None
    # 꽉낌 후속: 한 치수 업 시 헐떡임 (복합점수 보정). None=모름/스킵
    heel_slip_when_one_size_up: Optional[bool] = None

    # 진입: True = 디자인(Q4) 먼저 → 발(Q2) → 사이즈(Q5)…
    product_first: bool = False

    # 1차 분기: 실측 가능 시 수치 (없으면 경험 경로)
    measurement_available: Optional[bool] = None
    foot_length_mm:        Optional[int]   = None
    foot_ball_width_mm:    Optional[float] = None
    instep_circumference_mm: Optional[float] = None

    # 대화 히스토리 (LLM 컨텍스트용)
    conversation_history: list[dict] = field(default_factory=list)

    # 진단 결과 (RESULT 상태에서 채워짐)
    diagnosis_result: Optional[dict] = None

    # 타임스탬프
    created_at:  str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at:  str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None

    # 디버그/어드민용
    error_count: int = 0
    last_error:  str = ""

    def touch(self):
        self.updated_at = datetime.now().isoformat()

    def is_complete(self) -> bool:
        return self.state in (SessionState.DONE, SessionState.AWAIT_CONSULT)

    def add_message(self, role: str, content: str) -> None:
        """LLM에 넘길 대화 히스토리 추가"""
        self.conversation_history.append({
            "role": role,        # "user" | "assistant"
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })
        self.touch()

    def to_json(self) -> str:
        d = {
            "session_id": self.session_id,
            "state": self.state.value,
            "channel": self.channel,
            "customer_id": self.customer_id,
            "shop_id": self.shop_id,
            "policy_version": self.policy_version,
            "preferred_style": self.preferred_style,
            "foot_issues": self.foot_issues,
            "hallux_severity": self.hallux_severity,
            "wide_severity": self.wide_severity,
            "instep_severity": self.instep_severity,
            "toe_detail": self.toe_detail,
            "design": self.design,
            "original_size": self.original_size,
            "fit_experience": self.fit_experience,
            "heel_slip_when_one_size_up": self.heel_slip_when_one_size_up,
            "measurement_available": self.measurement_available,
            "foot_length_mm": self.foot_length_mm,
            "foot_ball_width_mm": self.foot_ball_width_mm,
            "instep_circumference_mm": self.instep_circumference_mm,
            "product_first": self.product_first,
            "conversation_history": self.conversation_history,
            "diagnosis_result": self.diagnosis_result,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "error_count": self.error_count,
        }
        return json.dumps(d, ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, raw: str) -> "ChatSession":
        d = json.loads(raw)
        sess = cls()
        sess.session_id  = d["session_id"]
        sess.state       = SessionState(d["state"])
        sess.channel     = d.get("channel", "cli")
        sess.customer_id = d.get("customer_id")
        sess.shop_id     = d.get("shop_id", "default_shop")
        sess.policy_version = d.get("policy_version", "v1")
        sess.preferred_style  = d.get("preferred_style")
        sess.foot_issues      = d.get("foot_issues")
        sess.hallux_severity  = d.get("hallux_severity", "0")
        sess.wide_severity    = d.get("wide_severity", "0")
        sess.instep_severity  = d.get("instep_severity", "0")
        sess.toe_detail       = d.get("toe_detail", "0")
        sess.design           = d.get("design")
        sess.original_size    = d.get("original_size")
        sess.fit_experience   = d.get("fit_experience")
        _h = d.get("heel_slip_when_one_size_up")
        sess.heel_slip_when_one_size_up = None if _h is None else bool(_h)
        sess.measurement_available = d.get("measurement_available")
        sess.foot_length_mm   = d.get("foot_length_mm")
        sess.foot_ball_width_mm = d.get("foot_ball_width_mm")
        sess.instep_circumference_mm = d.get("instep_circumference_mm")
        sess.product_first = d.get("product_first", False)
        sess.conversation_history = d.get("conversation_history", [])
        sess.diagnosis_result     = d.get("diagnosis_result")
        sess.created_at      = d.get("created_at", sess.created_at)
        sess.updated_at      = d.get("updated_at", sess.updated_at)
        sess.completed_at    = d.get("completed_at")
        sess.error_count     = d.get("error_count", 0)
        return sess


# ──────────────────────────────────────────────
# 3. 세션 저장소 (인터페이스)
# ──────────────────────────────────────────────
class SessionStore:
    """
    세션 저장소 추상 인터페이스.
    현재: 파일 기반 (data/sessions/)
    전환 가능: Redis, DynamoDB, PostgreSQL 등 — save/load만 교체하면 됨
    """

    def __init__(self, store_dir: str = "data/sessions"):
        import os
        self._dir = store_dir
        os.makedirs(store_dir, exist_ok=True)

    def save(self, session: ChatSession) -> None:
        path = os.path.join(self._dir, f"{session.session_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write(session.to_json())

    def load(self, session_id: str) -> Optional[ChatSession]:
        import os
        path = os.path.join(self._dir, f"{session_id}.json")
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return ChatSession.from_json(f.read())

    def delete(self, session_id: str) -> None:
        import os
        path = os.path.join(self._dir, f"{session_id}.json")
        if os.path.exists(path):
            os.remove(path)


import os  # SessionStore 내부에서 사용하므로 모듈 레벨에도 필요


# ──────────────────────────────────────────────
# 4. 대화 흐름 컨트롤러
# ──────────────────────────────────────────────
class ConversationController:
    """
    채널 독립적인 대화 흐름 제어.

    사용법 (CLI):
        ctrl = ConversationController()
        session = ctrl.new_session(channel="cli")
        while not session.is_complete():
            prompt = ctrl.get_next_prompt(session)
            print(prompt["text"])
            user_input = input("입력: ")
            ctrl.process_input(session, user_input)
        print(ctrl.get_result_output(session))

    사용법 (카카오/웹 API):
        session = store.load(session_id) or ctrl.new_session(channel="kakao")
        response = ctrl.handle_message(session, user_text)
        store.save(session)
        return response  # JSON으로 클라이언트에 전달
    """

    ISSUE_MAP  = {"1": "좁음", "2": "보통", "3": "넓음", "4": "무지외반",
                  "5": "발등 높음", "6": "통통함", "7": "앞코"}
    DESIGN_MAP = {"1": "구두", "2": "로퍼", "3": "단화", "4": "운동화"}
    EXP_MAP    = {"1": "잘 맞음", "2": "볼 때문에 크게 사서 헐떡임", "3": "볼이 꽉 껴서 불편함"}
    FIT_LINE_MAP = {"1": "기본핏", "2": "편한핏", "3": "아주 편한핏"}

    def __init__(self, store: Optional[SessionStore] = None):
        self._store = store or SessionStore()

    def new_session(self, channel: str = "cli", customer_id: Optional[str] = None) -> ChatSession:
        sess = ChatSession(channel=channel, customer_id=customer_id)
        sess.state = SessionState.Q_ENTRY
        self._store.save(sess)
        return sess

    def handle_message(self, session: ChatSession, user_text: str) -> dict:
        """
        메시지 수신 → 상태 전이 → 다음 응답 반환
        반환 형태: {"text": str, "quick_replies": list, "state": str, "done": bool}
        """
        session.add_message("user", user_text)

        try:
            result = self._process(session, user_text.strip())
        except Exception as e:
            session.error_count += 1
            session.last_error = str(e)
            result = {
                "text": f"입력을 다시 확인해 주세요. ({e})",
                "quick_replies": [],
                "state": session.state.value,
                "done": False,
            }

        session.add_message("assistant", result["text"])
        self._store.save(session)
        return result

    def _process(self, session: ChatSession, text: str) -> dict:
        state = session.state

        # ── 진입: 상품 선행 vs 기존(실측 우선) ───
        if state == SessionState.Q_ENTRY:
            if text == "1":
                session.product_first = True
                session.state = SessionState.Q_DESIGN
                return self._design_prompt(product_first=True)
            if text == "2":
                session.product_first = False
                session.state = SessionState.Q_MEAS
                return {
                    "text": (
                        "Q0. 지금 발길이·발볼을 직접 재실 수 있나요?\n"
                        "1.예, 재볼 수 있어요  2.아니요, 평소 신던 경험만 알려드릴게요"
                    ),
                    "quick_replies": ["1", "2"],
                    "state": session.state.value,
                    "done": False,
                }
            raise ValueError("1 또는 2를 선택해 주세요.")

        # ── Q0: 실측 가능 여부 (1차 분기) ────────
        if state == SessionState.Q_MEAS:
            if text == "1":
                session.measurement_available = True
                session.state = SessionState.Q_MEAS_INPUT
                return {
                    "text": (
                        "발길이(mm), 발볼, 발등둘레 수치를 알려주세요.\n"
                        "발볼은 너비(mm, 예: 92) 또는 둘레(mm, 예: 228) 모두 입력 가능합니다.\n"
                        "발등둘레는 mm로 입력해 주세요. 모르면 생략 가능합니다.\n"
                        "예: 235, 92, 230  또는  235, 228, 230  또는  235"
                    ),
                    "quick_replies": [],
                    "state": session.state.value,
                    "done": False,
                }
            if text == "2":
                session.measurement_available = False
                session.foot_length_mm = None
                session.foot_ball_width_mm = None
                session.state = SessionState.Q_FOOT
                return {
                    "text": (
                        "Q2. 발의 형태나 불편한 곳을 선택해 주세요. (복수 선택 가능, 예: 3,4)\n"
                        "1.좁음  2.보통  3.넓음  4.무지외반  5.발등 높음  6.통통함  7.앞코"
                    ),
                    "quick_replies": ["1", "2", "3", "4", "5", "6", "7"],
                    "state": session.state.value,
                    "done": False,
                }
            raise ValueError("1 또는 2를 선택해 주세요.")

        # ── Q0-1: 실측 수치 ─────────────────────
        if state == SessionState.Q_MEAS_INPUT:
            raw = [x.strip() for x in text.replace("，", ",").split(",") if x.strip()]
            try:
                fl = int(raw[0])
                assert 200 <= fl <= 280
            except Exception:
                raise ValueError("발길이(mm)를 먼저 숫자로 입력해 주세요. (예: 235 또는 235, 228)")
            session.foot_length_mm = fl
            if len(raw) >= 2:
                try:
                    fb = float(raw[1])
                    session.foot_ball_width_mm = fb if fb > 0 else None
                except ValueError:
                    session.foot_ball_width_mm = None
            else:
                session.foot_ball_width_mm = None

            if len(raw) >= 3:
                try:
                    ins = float(raw[2])
                    session.instep_circumference_mm = ins if ins > 0 else None
                except ValueError:
                    session.instep_circumference_mm = None
            else:
                session.instep_circumference_mm = None
            session.state = SessionState.Q_FOOT
            return {
                "text": (
                    "Q2. 발의 형태나 불편한 곳을 선택해 주세요. (복수 선택 가능, 예: 3,4)\n"
                    "1.좁음  2.보통  3.넓음  4.무지외반  5.발등 높음  6.통통함  7.앞코"
                ),
                "quick_replies": ["1", "2", "3", "4", "5", "6", "7"],
                "state": session.state.value,
                "done": False,
            }

        # ── Q2: 발 형태 ─────────────────────────
        if state == SessionState.Q_FOOT:
            selected = [i.strip() for i in text.split(",") if i.strip()]
            issues = [self.ISSUE_MAP[k] for k in selected if k in self.ISSUE_MAP]
            if not issues:
                raise ValueError("목록에서 번호를 선택해 주세요.")
            session.foot_issues = issues

            # 세부 질문이 필요한 증상이 있으면 → Q_FOOT_DETAIL
            needs_detail = any(k in selected for k in ("3", "4", "5", "7"))
            if needs_detail:
                session.state = SessionState.Q_FOOT_DETAIL
                return self._foot_detail_prompt(session, selected)
            if session.product_first:
                session.state = SessionState.Q_SIZE
                return self._q_size_prompt(session)
            session.state = SessionState.Q_DESIGN
            return self._design_prompt()

        # ── Q2-1: 세부 증상 ─────────────────────
        if state == SessionState.Q_FOOT_DETAIL:
            return self._process_foot_detail(session, text)

        # ── Q4: 디자인 ──────────────────────────
        if state == SessionState.Q_DESIGN:
            val = self.DESIGN_MAP.get(text)
            if not val:
                raise ValueError("1·2·3·4 중 선택해 주세요.")
            session.design = val
            if session.product_first:
                session.state = SessionState.Q_FOOT
                return {
                    "text": (
                        f"선택하신 스타일({val}) 기준으로 발 정보를 물어볼게요.\n"
                        "Q2. 발의 형태나 불편한 곳을 선택해 주세요. (복수 선택 가능, 예: 3,4)\n"
                        "1.좁음  2.보통  3.넓음  4.무지외반  5.발등 높음  6.통통함  7.앞코"
                    ),
                    "quick_replies": ["1", "2", "3", "4", "5", "6", "7"],
                    "state": session.state.value,
                    "done": False,
                }
            session.state = SessionState.Q_SIZE
            return self._q_size_prompt(session)

        # ── Q5: 사이즈 ──────────────────────────
        if state == SessionState.Q_SIZE:
            try:
                size = int(text)
                assert 200 <= size <= 280
            except Exception:
                raise ValueError("올바른 사이즈(예: 235)를 입력해 주세요.")
            session.original_size = size
            session.state = SessionState.Q_SIZE_FIT
            return {
                "text": (
                    "Q5-0. 최근 산 해당 디자인 신발은 어떤 핏 라인이었나요?\n"
                    "1.기본핏  2.편한핏  3.아주 편한핏  (모르면 2)"
                ),
                "quick_replies": ["1", "2", "3"],
                "state": session.state.value,
                "done": False,
            }

        # ── Q5-0: 최근 제품 핏 ───────────────────
        if state == SessionState.Q_SIZE_FIT:
            val = self.FIT_LINE_MAP.get(text)
            if not val:
                raise ValueError("1·2·3 중 선택해 주세요.")
            # Q5 기준(0점) 신발의 핏 라인 저장
            session.preferred_style = val
            session.state = SessionState.Q_FIT_EXP
            return {
                "text": "Q5-1. 그 사이즈를 신었을 때 느낌은 어땠나요?\n1.잘 맞음  2.볼 때문에 크게 사서 헐떡임  3.볼이 꽉 껴서 불편함",
                "quick_replies": ["1", "2", "3"],
                "state": session.state.value,
                "done": False,
            }

        # ── Q5-1: 착화 경험 ─────────────────────
        if state == SessionState.Q_FIT_EXP:
            val = self.EXP_MAP.get(text)
            if not val:
                raise ValueError("1·2·3 중 선택해 주세요.")
            session.fit_experience = val
            session.heel_slip_when_one_size_up = None
            if text == "3":
                session.state = SessionState.Q_TIGHT_CONFIRM_SIZE
                return self._prompt_tight_confirm_size(session)
            session.state = SessionState.DIAGNOSING
            try:
                return self._run_diagnosis(session)
            except Exception:
                session.state = SessionState.Q_FIT_EXP
                raise

        # ── 꽉낌: 기준 사이즈 확인 (복합 보정 전) ─
        if state == SessionState.Q_TIGHT_CONFIRM_SIZE:
            if text == "1":
                session.state = SessionState.Q_TIGHT_HEEL_ON_UP
                return self._prompt_tight_heel_on_upsize(session)
            if text == "2":
                session.state = SessionState.Q_TIGHT_REVISE_SIZE
                return {
                    "text": (
                        "지금 그 신발의 올바른 사이즈(mm, 예: 235)를 숫자로 입력해 주세요.\n"
                        "(앞서 Q5에서 잘못 적으신 경우)"
                    ),
                    "quick_replies": [],
                    "state": session.state.value,
                    "done": False,
                }
            raise ValueError("1 또는 2를 선택해 주세요.")

        if state == SessionState.Q_TIGHT_REVISE_SIZE:
            try:
                size = int(text)
                assert 200 <= size <= 280
            except Exception:
                raise ValueError("올바른 사이즈(예: 235)를 입력해 주세요.")
            session.original_size = size
            session.state = SessionState.Q_TIGHT_HEEL_ON_UP
            return self._prompt_tight_heel_on_upsize(session)

        # ── 꽉낌: 한 치수 업 시 헐떡임 (복합 보정) ─
        if state == SessionState.Q_TIGHT_HEEL_ON_UP:
            if text == "1":
                session.heel_slip_when_one_size_up = True
            elif text == "2":
                session.heel_slip_when_one_size_up = False
            elif text == "3":
                session.heel_slip_when_one_size_up = None
            else:
                raise ValueError("1·2·3 중 선택해 주세요.")
            session.state = SessionState.DIAGNOSING
            try:
                return self._run_diagnosis(session)
            except Exception:
                session.state = SessionState.Q_TIGHT_HEEL_ON_UP
                raise

        if state == SessionState.DIAGNOSING:
            session.state = SessionState.Q_FIT_EXP
            raise ValueError(
                "직전 진단에서 오류가 발생했습니다. 마지막 질문에 답한 뒤 다시 시도해 주세요."
            )

        # ── 완료 상태 ────────────────────────────
        if session.is_complete():
            return {
                "text": "진단이 완료되었습니다. 추가 문의사항이 있으시면 알려주세요.",
                "quick_replies": [],
                "state": session.state.value,
                "done": True,
            }

        raise ValueError(f"알 수 없는 상태: {state}")

    # ── 헬퍼 ────────────────────────────────────

    def _foot_detail_prompt(self, session: ChatSession, selected: list) -> dict:
        """세부 증상 질문 (여러 개를 하나의 안내 텍스트로 묶음)"""
        lines = []
        if "3" in selected:
            lines.append("[넓음] 정도: 1.약간  2.많이")
        if "4" in selected:
            lines.append("[무지외반] 정도: 1.약간  2.중간  3.심함")
        if "5" in selected:
            lines.append("[발등 높이] 정도: 1.약간  2.중간  3.심함")
        if "7" in selected:
            lines.append("[앞코] 불편함: 1.발끝 닿음  2.너비 좁음  3.새끼발가락 통증")

        # 어떤 세부 질문을 기다리는지 세션에 기록
        session._pending_details = selected  # 임시 플래그
        detail_count = len(lines)
        if detail_count <= 1:
            guide = "숫자 1개만 입력해 주세요. (예: 3)"
        else:
            guide = "숫자를 순서대로 쉼표로 입력해 주세요. (예: 2,1,2)"

        return {
            "text": "조금 더 알려주세요!\n" + "\n".join(lines) + f"\n\n{guide}",
            "quick_replies": [],
            "state": session.state.value,
            "done": False,
        }

    def _process_foot_detail(self, session: ChatSession, text: str) -> dict:
        vals = [v.strip() for v in text.split(",")]
        pending = getattr(session, "_pending_details", [])
        idx = 0
        if "3" in pending:
            session.wide_severity = vals[idx] if idx < len(vals) else "1"
            idx += 1
        if "4" in pending:
            session.hallux_severity = vals[idx] if idx < len(vals) else "1"
            idx += 1
        if "5" in pending:
            session.instep_severity = vals[idx] if idx < len(vals) else "1"
            idx += 1
        if "7" in pending:
            session.toe_detail = vals[idx] if idx < len(vals) else "1"

        if session.product_first:
            session.state = SessionState.Q_SIZE
            return self._q_size_prompt(session)
        session.state = SessionState.Q_DESIGN
        return self._design_prompt()

    def _q_size_prompt(self, session: ChatSession) -> dict:
        val = session.design or "구두"
        return {
            "text": f"Q5. 평소 자주 신으시는 {val} 사이즈를 입력해 주세요. (225~255mm)",
            "quick_replies": ["225", "230", "235", "240", "245", "250", "255"],
            "state": session.state.value,
            "done": False,
        }

    def _design_prompt(self, product_first: bool = False) -> dict:
        lead = ""
        if product_first:
            lead = "먼저 보고 계신 상품 스타일에 맞춰 골라주세요.\n\n"
        return {
            "text": lead + "Q4. 어떤 디자인을 원하시나요?\n1.구두  2.로퍼  3.단화  4.운동화",
            "quick_replies": ["1", "2", "3", "4"],
            "state": SessionState.Q_DESIGN.value,
            "done": False,
        }

    def _prompt_tight_confirm_size(self, session: ChatSession) -> dict:
        mm = session.original_size or 0
        return {
            "text": (
                "복합점수(발 증상+핏 익숙도)를 맞추기 위해 두 가지만 더 물어볼게요.\n\n"
                f"Q5-2. 지금 말씀하신 신발, 방금 입력하신 기준 사이즈가 {mm}mm가 맞나요?\n"
                "1.네  2.아니요 (다시 입력할게요)"
            ),
            "quick_replies": ["1", "2"],
            "state": session.state.value,
            "done": False,
        }

    def _prompt_tight_heel_on_upsize(self, session: ChatSession) -> dict:
        return {
            "text": (
                "Q5-3. 비슷한 핏에서 한 치수 크게 신어 본 적이 있을 때, "
                "뒷꿈치가 헐떡였나요?\n"
                "1.네  2.아니요  3.해 본 적 없어요/잘 모르겠어요\n"
                "(복합점수 가중·보수에 반영됩니다)"
            ),
            "quick_replies": ["1", "2", "3"],
            "state": session.state.value,
            "done": False,
        }

    def _run_diagnosis(self, session: ChatSession) -> dict:
        """진단 실행 + 결과 저장 + 출력 생성"""
        from core.engine import CustomerInput, DiagnosisEngine
        from core.storage import (
            init_db, save_customer_input, save_diagnosis_result,
            export_rag_document
        )
        from dataclasses import asdict

        inp = CustomerInput(
            session_id      = session.session_id,
            preferred_style = session.preferred_style or "편한핏",
            foot_issues     = session.foot_issues or [],
            hallux_severity = session.hallux_severity,
            wide_severity   = session.wide_severity,
            instep_severity = session.instep_severity,
            toe_detail      = session.toe_detail,
            design          = session.design or "구두",
            original_size   = session.original_size or 235,
            fit_experience  = session.fit_experience or "잘 맞음",
            shop_id         = session.shop_id,
            policy_version  = session.policy_version,
            measurement_available = bool(session.measurement_available),
            foot_length_mm        = session.foot_length_mm,
            foot_ball_width_mm    = session.foot_ball_width_mm,
            instep_circumference_mm = session.instep_circumference_mm,
            heel_slip_when_one_size_up = session.heel_slip_when_one_size_up,
        )

        res = DiagnosisEngine().run(inp)

        # 저장
        init_db()
        save_customer_input(inp)
        save_diagnosis_result(res)
        export_rag_document(inp, res)

        session.diagnosis_result = asdict(res)
        session.state = SessionState.AWAIT_CONSULT if res.is_consult else SessionState.RESULT
        session.completed_at = datetime.now().isoformat()

        # 출력 생성
        output_text = self._format_result(inp, res)
        return {
            "text": output_text,
            "quick_replies": [],
            "state": session.state.value,
            "done": True,
            "diagnosis": asdict(res),  # API 응답에 구조화 데이터도 포함
        }

    def _format_result(self, inp, res) -> str:
        from core.engine import DiagnosisResult
        path_ko = "실측 경로" if res.recommendation_path == "measured" else "경험 기반 경로"
        q2_score, q5_fit_score = self._score_breakdown(inp)
        applied_score = max(0, res.composite_score - q5_fit_score)
        base_comp = q2_score + q5_fit_score
        comp_adj = res.composite_score - base_comp
        comp_line = (
            f"📌 복합점수    : {res.composite_score} (Q2 {q2_score} + Q5핏 {q5_fit_score}"
            + (f", 꽉낌 추정 보정 {comp_adj:+d}" if comp_adj != 0 else "")
            + ")"
        )
        rec_type = self._recommendation_type(res)
        lines = [
            "🌸" * 20,
            f"  [ {res.design} 전문가 맞춤 진단 결과 ]",
            "",
            f"📌 입력 경로   : {path_ko} (신뢰도 {res.confidence_score:.0%})",
            f"📌 추천 유형   : {rec_type}",
            comp_line,
            f"📌 적용점수    : {applied_score} (복합 {res.composite_score} − Q5핏 {q5_fit_score})",
            f"✅ 추천 제품   : {res.recommended_product_name} ({res.recommended_fit})",
            f"   추천 이유   : {res.recommendation_reason}",
            f"✅ 추천 사이즈 : {res.final_size}mm"
            + self._size_adjust_suffix(inp, res),
        ]

        if res.is_consult:
            lines += [
                "",
                "📞 상담 안내",
                f"   {res.consult_reason}",
                "   → 사장님이 곧 직접 전화드릴게요!",
            ]
        elif res.ready_made_option or res.stretch_option:
            lines += [
                "",
                "🧭 추천 방식 선택",
            ]
            if res.ready_made_option:
                lines.append(f"   - {res.ready_made_option}")
            if res.stretch_option:
                lines.append(f"   - {res.stretch_option}")
            lines.append("   → 고객 선택 후 최종 제작 지시를 확정합니다.")
        elif res.stretch_step > 0:
            lines += [
                "",
                f"🔧 발볼늘림 보완 : {res.stretch_step}단계({res.stretch_mm}mm)",
                f"   {res.stretch_reason}",
            ]
            if res.additional_works:
                lines.append(f"   추가 가공  : {', '.join(res.additional_works)}")
        else:
            lines += [
                "",
                "✨ 기성화만으로 충분히 편안하게 신으실 수 있습니다.",
            ]
            if res.additional_works:
                lines.append(f"   소폭 가공  : {', '.join(res.additional_works)}")

        lines += ["", "🌸" * 20]

        # 관리자용 지시서
        lines += [
            "",
            "🛠️  [관리자용 제작 지시서]",
            f"- 세션 ID  : {res.session_id}",
            f"- 디자인   : {res.design}",
            f"- 추천 유형  : {rec_type}",
            f"- 제품     : {res.recommended_product_id} / {res.recommended_product_name}",
            f"- 목표 사이즈: {res.final_size}mm",
            f"- 복합 점수  : {res.composite_score} = Q2({q2_score}) + Q5핏({q5_fit_score})"
            + (f" + 꽉낌보정({comp_adj:+d})" if comp_adj != 0 else ""),
            f"- 적용 점수  : {applied_score} (복합 {res.composite_score} − Q5핏 {q5_fit_score})",
            f"- 가공 단계  : {res.stretch_step}단계 ({res.stretch_mm}mm) — {res.stretch_reason}",
        ]
        if res.additional_works:
            lines.append(f"- 추가 가공  : {', '.join(res.additional_works)}")
        if res.is_consult:
            lines.append(f"- ⚠️  상담 필요: {res.consult_reason}")

        return "\n".join(lines)

    def _size_adjust_suffix(self, inp, res) -> str:
        """size_adjusted 원인별로 표시 (헐떡임만이 아님)."""
        if not res.size_adjusted:
            return ""
        fe = inp.fit_experience or ""
        issues = set(inp.foot_issues or [])
        if "헐떡임" in fe:
            return " (헐떡임 보정 -5mm)"
        if "꽉" in fe and res.final_size > res.original_size:
            return " (꽉낌 보정 +5mm)"
        if "발등 높음" in issues and res.final_size > res.original_size:
            return " (발등 보정 +5mm)"
        delta = res.final_size - res.original_size
        if delta != 0:
            sign = "+" if delta > 0 else ""
            return f" (사이즈 보정 {sign}{delta}mm)"
        return ""

    def _score_breakdown(self, inp) -> tuple[int, int]:
        issues = set(inp.foot_issues or [])
        q2 = 0
        if "넓음" in issues:
            wide = self._safe_int(getattr(inp, "wide_severity", "1"), default=1)
            q2 += 2 if wide >= 2 else 1
        if "무지외반" in issues:
            hallux = self._safe_int(getattr(inp, "hallux_severity", "1"), default=1)
            q2 += max(1, min(hallux, 3))
        if "통통함" in issues:
            q2 += 1
        q2 = max(0, min(q2, 6))
        fit_map = {"기본핏": 0, "편한핏": 1, "아주 편한핏": 2}
        q5 = fit_map.get(getattr(inp, "preferred_style", "편한핏"), 1)
        return q2, q5

    def _recommendation_type(self, res) -> str:
        if res.is_consult:
            return "상담형"
        if res.stretch_step > 0 or (res.additional_works and not res.size_adjusted):
            return "늘림형"
        return "기성화기본"

    def _safe_int(self, val: str, default: int = 0) -> int:
        try:
            return int(val)
        except Exception:
            return default

    def get_initial_prompt(self) -> dict:
        return {
            "text": (
                "✨ 안녕하세요! 슈핏케어입니다.\n"
                "발에 꼭 맞는 신발을 찾아드릴게요.\n\n"
                "Q진입. 어떻게 도와드릴까요?\n"
                "1.보고 있는 상품·스타일이 있어요 (상품 선행 빠른 진단)\n"
                "2.아직 고르는 중이에요 (실측·발 정보 먼저)"
            ),
            "quick_replies": ["1", "2"],
            "state": SessionState.Q_ENTRY.value,
            "done": False,
        }
