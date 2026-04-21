"""
슈핏케어 FastAPI 어댑터.

실행:
    pip install fastapi uvicorn
    uvicorn api:app --reload
"""

# ──────────────────────────────────────────────
# FastAPI 어댑터 (설치 시 활성화)
# ──────────────────────────────────────────────
try:
    from fastapi import FastAPI
    from pydantic import BaseModel
    import sys, os
    import json
    import hashlib
    import urllib.request
    import urllib.error
    from datetime import datetime
    from collections import Counter
    from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

    from core.session import ConversationController, SessionStore, SessionState
    from core.storage import init_db
    from adapters.naver import NaverAdapter
    from adapters.kakao import KakaoAdapter

    app = FastAPI(title="슈핏케어 API")
    store = SessionStore()
    ctrl  = ConversationController(store=store)
    naver_adapter = NaverAdapter()
    kakao_adapter = KakaoAdapter()
    init_db()
    _EXECUTOR = ThreadPoolExecutor(max_workers=4)
    _TIMEOUT_SEC = 8.0
    _FALLBACK_TEXT = (
        "잠시 응답이 지연되고 있어요. 같은 내용을 한 번 더 보내주시면 바로 이어서 도와드릴게요."
    )
    _NAVER_AUTO_REPLY_VARIANT = os.environ.get("NAVER_AUTO_REPLY_VARIANT", "A").strip().upper()
    _NAVER_AUTO_REPLY_TEMPLATES = {
        "A": (
            "문의하신 상품은 발볼 늘림 가능합니다.\n"
            "주문 시 본품 옵션 '발볼 늘림' + 추가상품 '발볼 늘림 1단계/2단계'를 함께 선택해 주세요.\n"
            "원하시면 30초 진단으로 단계를 바로 추천드릴게요. 평소 사이즈(mm)와 불편 부위를 알려주세요."
        ),
        "B": (
            "발볼 늘림 가능해요.\n"
            "주문은 본품 '발볼 늘림'과 추가상품 '1단계/2단계'를 같이 선택해 주세요.\n"
            "바로 추천받으시려면 사이즈(mm)와 불편 부위(발볼/앞코/무지외반)만 알려주세요."
        ),
    }
    _NAVER_AUTO_REPLY_FALLBACK = _NAVER_AUTO_REPLY_TEMPLATES.get(
        _NAVER_AUTO_REPLY_VARIANT, _NAVER_AUTO_REPLY_TEMPLATES["A"]
    )
    _NAVER_SEND_API_ENABLED = os.environ.get("NAVER_SEND_API_ENABLED", "false").strip().lower() in ("1", "true", "yes", "on")
    _NAVER_SEND_API_URL = os.environ.get("NAVER_SEND_API_URL", "").strip()
    _NAVER_SEND_API_AUTH = os.environ.get("NAVER_SEND_API_AUTH", "").strip()
    _NAVER_SEND_API_TIMEOUT_SEC = float(os.environ.get("NAVER_SEND_API_TIMEOUT_SEC", "5"))

    def _audit_event(event: str, session_id: str, channel: str, shop_id: str, policy_version: str, message: str = ""):
        """운영 로그(JSONL): 민감 원문은 저장하지 않고 추적 가능한 메타만 기록."""
        log_dir = os.path.join("data", "logs")
        os.makedirs(log_dir, exist_ok=True)
        msg = message or ""
        msg_hash = hashlib.sha256(msg.encode("utf-8")).hexdigest()[:16] if msg else ""
        payload = {
            "ts": datetime.now().isoformat(),
            "event": event,
            "session_id": session_id,
            "channel": channel,
            "shop_id": shop_id,
            "policy_version": policy_version,
            "message_hash": msg_hash,
            "message_len": len(msg),
        }
        with open(os.path.join(log_dir, "chat_events.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def _safe_handle_message(session, message: str) -> dict:
        """챗봇 처리 보호 래퍼: timeout/예외 시 fallback 반환."""
        try:
            fut = _EXECUTOR.submit(ctrl.handle_message, session, message)
            return fut.result(timeout=_TIMEOUT_SEC)
        except FutureTimeout:
            _audit_event("timeout", session.session_id, session.channel, session.shop_id, session.policy_version, message)
            return {
                "text": _FALLBACK_TEXT,
                "quick_replies": [],
                "state": session.state.value,
                "done": False,
            }
        except Exception:
            _audit_event("exception", session.session_id, session.channel, session.shop_id, session.policy_version, message)
            return {
                "text": "일시적인 오류가 발생했어요. 같은 답변을 다시 입력해 주세요.",
                "quick_replies": [],
                "state": session.state.value,
                "done": False,
            }

    def _naver_auto_reply(message: str) -> dict | None:
        """
        톡톡 절차형 문의는 자동종결 템플릿으로 즉시 응답.
        개인 맞춤형 문의는 None 반환하여 기존 진단 플로우로 전달한다.
        """
        text = (message or "").strip().lower()
        if not text:
            return None

        process_keywords = ("신청", "방법", "어떻게", "옵션", "주문", "선택", "발볼 늘림")
        personalized_keywords = ("넓", "무지외반", "꽉", "헐떡", "통증", "괜찮")

        has_process = any(k in text for k in process_keywords)
        has_personalized = any(k in text for k in personalized_keywords)

        # 절차형 문의만 자동종결
        if has_process and not has_personalized:
            return {
                "text": _NAVER_AUTO_REPLY_FALLBACK,
                "quick_replies": ["1단계/2단계 추천받기", "주문 방법 다시 보기"],
                "state": "AUTO_CLOSED",
                "done": True,
            }
        return None

    def _is_naver_ai_entry(message: str) -> bool:
        text = (message or "").strip().lower()
        if not text:
            return False
        compact = (
            text.replace(" ", "")
            .replace("_", "")
            .replace("-", "")
            .replace("/", "")
            .replace(",", "")
            .replace("·", "")
        )
        keywords = (
            "ai_1_2추천",
            "ai_1_2 추천",
            "1·2단계 추천받기",
            "1,2단계 추천 받기",
            "1/2단계 추천",
            "1단계/2단계 추천",
            "추천받기",
            "무지외반 상담",
            "발볼·무지외반 상담",
            "발볼 무지외반 상담",
        )
        compact_keywords = (
            "ai12추천",
            "12단계추천",
            "12단계추천받기",
            "추천받기",
            "무지외반상담",
            "발볼무지외반상담",
        )
        return any(k in text for k in keywords) or any(k in compact for k in compact_keywords)

    def _prepare_naver_ai_entry(session, message: str) -> str:
        """
        톡톡 추천 버튼 클릭을 AI 진단 시작 입력으로 정규화.
        - 완료 상태면 재진단 가능하도록 Q_ENTRY로 되돌린다.
        - Q_ENTRY에서는 '1'(상품 선행)로 바로 진입시킨다.
        """
        if session.state in (SessionState.RESULT, SessionState.AWAIT_CONSULT, SessionState.DONE):
            session.state = SessionState.Q_ENTRY
            session.completed_at = None
        if session.state == SessionState.Q_ENTRY:
            return "1"
        return message

    def _load_chat_events(log_path: str) -> list[dict]:
        events: list[dict] = []
        if not os.path.exists(log_path):
            return events
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except Exception:
                    continue
        return events

    def _naver_push_payload(inbound, result: dict) -> dict:
        """네이버 보내기 API(chatbot-api README: POST …/chatbot/v1/event) 스펙에 맞춘 payload."""
        quick = result.get("quick_replies", []) or []
        text_content: dict = {"text": result.get("text", "")}
        if quick:
            button_list = []
            for item in quick:
                code = str(item)[:1000]
                title = code[:18] if len(code) > 18 else code
                button_list.append({"type": "TEXT", "data": {"title": title, "code": code}})
            text_content["quickReply"] = {"buttonList": button_list}
        return {
            "event": "send",
            "user": inbound.user_id,
            "textContent": text_content,
        }

    def _send_naver_push(inbound, result: dict, session) -> bool:
        """
        네이버 보내기 API로 챗봇 응답을 푸시한다.
        - env 미설정/호출 실패 시 False 반환(기존 반환 로직 유지)
        """
        if not _NAVER_SEND_API_ENABLED:
            return False
        if not _NAVER_SEND_API_URL:
            _audit_event("naver_send_api_skipped_no_url", session.session_id, session.channel, session.shop_id, session.policy_version)
            return False

        payload = _naver_push_payload(inbound, result)
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers = {"Content-Type": "application/json;charset=UTF-8"}
        if _NAVER_SEND_API_AUTH:
            headers["Authorization"] = _NAVER_SEND_API_AUTH

        req = urllib.request.Request(_NAVER_SEND_API_URL, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=_NAVER_SEND_API_TIMEOUT_SEC) as resp:
                code = getattr(resp, "status", 200)
                if 200 <= int(code) < 300:
                    _audit_event("naver_send_api_success", session.session_id, session.channel, session.shop_id, session.policy_version)
                    return True
                _audit_event("naver_send_api_non2xx", session.session_id, session.channel, session.shop_id, session.policy_version)
                return False
        except urllib.error.HTTPError:
            _audit_event("naver_send_api_http_error", session.session_id, session.channel, session.shop_id, session.policy_version)
            return False
        except Exception:
            _audit_event("naver_send_api_exception", session.session_id, session.channel, session.shop_id, session.policy_version)
            return False

    class MessageRequest(BaseModel):
        session_id: str | None = None
        message:    str
        channel:    str = "web"
        customer_id: str | None = None
        shop_id: str = "default_shop"
        policy_version: str = "v1"

    @app.post("/chat")
    def chat(req: MessageRequest):
        """
        단일 엔드포인트 — 채널 무관하게 동일하게 동작.
        카카오: POST /chat  {"session_id": "xxx", "message": "1"}
        웹챗:   POST /chat  {"session_id": null,  "message": "시작"}
        """
        # 세션 로드 or 신규 생성
        session = None
        if req.session_id:
            session = store.load(req.session_id)

        if session is None:
            session = ctrl.new_session(channel=req.channel, customer_id=req.customer_id)
            session.shop_id = req.shop_id
            session.policy_version = req.policy_version
            # 신규 세션 → 첫 안내 반환
            intro = ctrl.get_initial_prompt()
            store.save(session)
            _audit_event("chat_start", session.session_id, session.channel, session.shop_id, session.policy_version, req.message)
            return {"session_id": session.session_id, **intro}
        session.shop_id = req.shop_id
        session.policy_version = req.policy_version

        # 메시지 처리
        result = _safe_handle_message(session, req.message)
        _audit_event("chat_message", session.session_id, session.channel, session.shop_id, session.policy_version, req.message)
        return {"session_id": session.session_id, **result}

    @app.post("/webhook/naver")
    def naver_webhook(payload: dict):
        inbound = naver_adapter.parse_inbound(payload)
        session = store.load(inbound.session_key)

        if session is None:
            session = ctrl.new_session(channel="naver", customer_id=inbound.user_id)
            session.session_id = inbound.session_key
            session.shop_id = str(payload.get("shop_id") or "default_shop")
            session.policy_version = str(payload.get("policy_version") or "v1")
            store.save(session)
            if inbound.message:
                if _is_naver_ai_entry(inbound.message):
                    _audit_event("naver_ai_entry_click", session.session_id, session.channel, session.shop_id, session.policy_version, inbound.message)
                    normalized = _prepare_naver_ai_entry(session, inbound.message)
                    result = _safe_handle_message(session, normalized)
                else:
                    auto_result = _naver_auto_reply(inbound.message)
                    if auto_result:
                        session.add_message("user", inbound.message)
                        session.add_message("assistant", auto_result["text"])
                        _audit_event("naver_auto_closed", session.session_id, session.channel, session.shop_id, session.policy_version, inbound.message)
                        result = auto_result
                    else:
                        result = _safe_handle_message(session, inbound.message)
            else:
                result = ctrl.get_initial_prompt()
        else:
            session.shop_id = str(payload.get("shop_id") or session.shop_id)
            session.policy_version = str(payload.get("policy_version") or session.policy_version)
            if inbound.message:
                if _is_naver_ai_entry(inbound.message):
                    _audit_event("naver_ai_entry_click", session.session_id, session.channel, session.shop_id, session.policy_version, inbound.message)
                    normalized = _prepare_naver_ai_entry(session, inbound.message)
                    result = _safe_handle_message(session, normalized)
                else:
                    auto_result = _naver_auto_reply(inbound.message)
                    if auto_result:
                        session.add_message("user", inbound.message)
                        session.add_message("assistant", auto_result["text"])
                        _audit_event("naver_auto_closed", session.session_id, session.channel, session.shop_id, session.policy_version, inbound.message)
                        result = auto_result
                    else:
                        result = _safe_handle_message(session, inbound.message)
            else:
                result = ctrl.get_initial_prompt()

        store.save(session)
        _audit_event("naver_webhook", session.session_id, session.channel, session.shop_id, session.policy_version, inbound.message)

        # 옵션: 네이버 보내기 API로 응답 푸시 (시나리오 고정 응답을 대체/보완)
        _send_naver_push(inbound, result, session)

        response = naver_adapter.build_outbound(result)
        response["session_id"] = session.session_id
        return response

    @app.post("/webhook/kakao")
    def kakao_webhook(payload: dict):
        inbound = kakao_adapter.parse_inbound(payload)
        session = store.load(inbound.session_key)

        if session is None:
            session = ctrl.new_session(channel="kakao", customer_id=inbound.user_id)
            session.session_id = inbound.session_key
            session.shop_id = str(payload.get("shop_id") or "default_shop")
            session.policy_version = str(payload.get("policy_version") or "v1")
            store.save(session)
            if inbound.message:
                result = _safe_handle_message(session, inbound.message)
            else:
                result = ctrl.get_initial_prompt()
        else:
            session.shop_id = str(payload.get("shop_id") or session.shop_id)
            session.policy_version = str(payload.get("policy_version") or session.policy_version)
            if inbound.message:
                result = _safe_handle_message(session, inbound.message)
            else:
                result = ctrl.get_initial_prompt()

        store.save(session)
        _audit_event("kakao_webhook", session.session_id, session.channel, session.shop_id, session.policy_version, inbound.message)
        return kakao_adapter.build_outbound(result)

    @app.post("/feedback")
    def feedback(session_id: str, was_returned: bool, reason: str = ""):
        """반품 피드백 수신 — 주문 완료 후 별도 호출"""
        from core.storage import save_return_feedback, update_rag_return_status
        save_return_feedback(session_id, was_returned, reason)
        update_rag_return_status(session_id, was_returned, reason)
        return {"ok": True}

    @app.get("/report")
    def report(shop_id: str | None = None, policy_version: str | None = None):
        """반품율 리포트"""
        from core.storage import get_return_rate_report
        return get_return_rate_report(shop_id=shop_id, policy_version=policy_version)

    @app.get("/ops/naver-events-summary")
    def naver_events_summary(shop_id: str | None = None, policy_version: str | None = None, limit: int = 5000):
        """
        Day2 운영 점검용:
        - 자동종결/진단연결/예외 이벤트 개수
        - 최근 로그 기준 카운트 제공 (원문 미포함)
        """
        log_path = os.path.join("data", "logs", "chat_events.jsonl")
        rows = _load_chat_events(log_path)
        if limit > 0:
            rows = rows[-limit:]

        filtered = []
        for row in rows:
            if row.get("channel") != "naver":
                continue
            if shop_id and str(row.get("shop_id")) != str(shop_id):
                continue
            if policy_version and str(row.get("policy_version")) != str(policy_version):
                continue
            filtered.append(row)

        event_counter = Counter(row.get("event", "unknown") for row in filtered)
        return {
            "scope": {
                "shop_id": shop_id,
                "policy_version": policy_version,
                "limit": limit,
                "template_variant": _NAVER_AUTO_REPLY_VARIANT,
            },
            "total_events": len(filtered),
            "event_counts": dict(event_counter),
            "auto_close_rate": (
                round(event_counter.get("naver_auto_closed", 0) / len(filtered), 4)
                if filtered else 0.0
            ),
        }

except ImportError:
    # fastapi 미설치 시 스킵 (CLI 모드에서는 불필요)
    pass
