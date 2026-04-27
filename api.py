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
    from fastapi.responses import HTMLResponse
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
            "네, 발볼 늘림 가능합니다.\n"
            "주문하실 때 본품 옵션 '발볼 늘림'과 추가상품 '발볼 늘림 1단계/2단계'를 함께 선택해 주세요.\n"
            "원하시면 바로 맞춤진단 도와드릴게요. 평소 사이즈(mm)와 불편 부위만 알려주시면 됩니다."
        ),
        "B": (
            "네, 발볼 늘림 가능해요.\n"
            "주문 시 본품 '발볼 늘림'과 추가상품 '1단계/2단계'를 같이 선택해 주세요.\n"
            "맞춤 추천을 원하시면 사이즈(mm)와 불편 부위(발볼/앞코/무지외반)를 알려주세요."
        ),
    }
    _NAVER_AUTO_REPLY_FALLBACK = _NAVER_AUTO_REPLY_TEMPLATES.get(
        _NAVER_AUTO_REPLY_VARIANT, _NAVER_AUTO_REPLY_TEMPLATES["A"]
    )
    _NAVER_SEND_API_ENABLED = os.environ.get("NAVER_SEND_API_ENABLED", "false").strip().lower() in ("1", "true", "yes", "on")
    _NAVER_SEND_API_URL = os.environ.get("NAVER_SEND_API_URL", "").strip()
    _NAVER_SEND_API_AUTH = os.environ.get("NAVER_SEND_API_AUTH", "").strip()
    _NAVER_SEND_API_TIMEOUT_SEC = float(os.environ.get("NAVER_SEND_API_TIMEOUT_SEC", "5"))

    _DEMO_HTML = """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>슈핏케어 추천엔진 데모</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; background: #f7f8fb; color: #222; }
    .wrap { max-width: 720px; margin: 24px auto; background: #fff; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.06); overflow: hidden; }
    .head { padding: 16px 20px; background: #1f3a8a; color: #fff; }
    .head h1 { margin: 0; font-size: 18px; }
    .head p { margin: 6px 0 0; font-size: 13px; opacity: .95; }
    .status-badge { margin-top: 8px; display: inline-block; font-size: 12px; padding: 3px 8px; border-radius: 999px; background: #334155; color: #fff; }
    .status-badge.ok { background: #16a34a; }
    .status-badge.err { background: #b91c1c; }
    body.foot-mode .chat .quick { display: none !important; }
    .chat { height: 520px; overflow: auto; padding: 16px; background: #f7f8fb; }
    .msg { max-width: 86%; margin: 10px 0; padding: 10px 12px; border-radius: 12px; white-space: pre-wrap; line-height: 1.5; }
    .bot { background: #fff; border: 1px solid #e5e7eb; }
    .me { margin-left: auto; background: #dbeafe; border: 1px solid #bfdbfe; }
    .meta { font-size: 12px; color: #6b7280; margin-top: 4px; }
    .quick { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
    .quick button { border: 1px solid #d1d5db; background: #fff; border-radius: 999px; padding: 6px 10px; font-size: 13px; cursor: pointer; }
    .quick button:hover { background: #eef2ff; }
    .panel { padding: 10px 12px; border-top: 1px solid #e5e7eb; background: #fff; }
    .panel.hidden { display: none; }
    .panel.disabled { opacity: 0.5; }
    .panel.disabled .chips button,
    .panel.disabled .actions button { cursor: not-allowed; }
    .panel .label { font-size: 12px; color: #475569; margin-bottom: 8px; }
    .chips { display: flex; flex-wrap: wrap; gap: 8px; }
    .chips button { border: 1px solid #cbd5e1; background: #f8fafc; border-radius: 999px; padding: 7px 12px; font-size: 13px; cursor: pointer; }
    .chips button:hover { background: #e2e8f0; }
    .chips button.active { background: #dbeafe; border-color: #93c5fd; color: #1e3a8a; font-weight: 600; }
    .chips-detail { margin-top: 8px; display: none; }
    .selection-preview { margin-top: 8px; font-size: 12px; color: #334155; }
    .actions { display: flex; gap: 8px; margin-top: 10px; }
    .actions button { border: 0; border-radius: 8px; padding: 8px 12px; cursor: pointer; }
    #complete-selection { background: #1d4ed8; color: #fff; }
    #clear-selection { background: #64748b; color: #fff; }
    .input { display: flex; gap: 8px; padding: 12px; border-top: 1px solid #e5e7eb; background: #fff; }
    .input input { flex: 1; border: 1px solid #d1d5db; border-radius: 8px; padding: 10px; font-size: 14px; }
    .input button { border: 0; background: #1f3a8a; color: #fff; border-radius: 8px; padding: 10px 14px; cursor: pointer; }
    .row { display: flex; gap: 8px; align-items: center; padding: 8px 12px; border-top: 1px dashed #e5e7eb; font-size: 12px; color: #6b7280; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="head">
      <h1>슈핏케어 추천엔진 데모</h1>
      <p>/chat API를 사용해 추천 흐름을 바로 시연합니다.</p>
      <span id="ui-status" class="status-badge">UI 초기화 중</span>
    </div>
    <div class="row">session_id: <span id="sid">없음</span></div>
    <div id="chat" class="chat"></div>
    <div id="quick-start-panel" class="panel">
      <div class="label">빠른 시작</div>
      <div class="chips">
        <button type="button" data-role="quick-start" data-msg="1">상품 먼저 추천받기 (1)</button>
        <button type="button" data-role="quick-start" data-msg="2">발 정보 입력 후 추천받기 (2)</button>
      </div>
    </div>
    <div id="symptom-panel" class="panel disabled">
      <div class="label">증상 선택 (복수 선택)</div>
      <div id="symptom-chips" class="chips">
        <button type="button" data-symptom="narrow">좁음</button>
        <button type="button" data-symptom="normal">보통</button>
        <button type="button" data-symptom="wide">넓음</button>
        <button type="button" data-symptom="hallux">무지외반</button>
        <button type="button" data-symptom="instep">발등 높음</button>
        <button type="button" data-symptom="chubby">통통함</button>
        <button type="button" data-symptom="toe">앞코</button>
      </div>
      <div id="detail-wide" class="chips chips-detail">
        <button type="button" data-detail-for="wide" data-value="1">넓음 1. 약간</button>
        <button type="button" data-detail-for="wide" data-value="2">넓음 2. 많이</button>
      </div>
      <div id="detail-hallux" class="chips chips-detail">
        <button type="button" data-detail-for="hallux" data-value="1">무지외반 1. 약간</button>
        <button type="button" data-detail-for="hallux" data-value="2">무지외반 2. 중간</button>
        <button type="button" data-detail-for="hallux" data-value="3">무지외반 3. 심함</button>
      </div>
      <div id="detail-instep" class="chips chips-detail">
        <button type="button" data-detail-for="instep" data-value="1">발등 높음 1. 약간</button>
        <button type="button" data-detail-for="instep" data-value="2">발등 높음 2. 중간</button>
        <button type="button" data-detail-for="instep" data-value="3">발등 높음 3. 심함</button>
      </div>
      <div id="detail-toe" class="chips chips-detail">
        <button type="button" data-detail-for="toe" data-value="1">앞코 1. 발끝 닿음</button>
        <button type="button" data-detail-for="toe" data-value="2">앞코 2. 너비 좁음</button>
        <button type="button" data-detail-for="toe" data-value="3">앞코 3. 새끼발가락 통증</button>
      </div>
      <div id="selection-preview" class="selection-preview">선택된 항목: 없음</div>
      <div class="actions">
        <button type="button" id="complete-selection">선택 완료 (단일 전송)</button>
        <button type="button" id="clear-selection">전체 초기화</button>
      </div>
    </div>
    <div class="input">
      <input id="msg" placeholder="메시지를 입력하세요 (예: 1, 구두, 넓음)" />
      <button id="send">보내기</button>
      <button id="reset" style="background:#475569;">새 세션</button>
    </div>
  </div>
  <script>
    const chat = document.getElementById("chat");
    const msg = document.getElementById("msg");
    const sidEl = document.getElementById("sid");
    const uiStatus = document.getElementById("ui-status");
    const quickStartPanel = document.getElementById("quick-start-panel");
    const symptomPanel = document.getElementById("symptom-panel");
    const symptomChips = document.getElementById("symptom-chips");
    const selectionPreview = document.getElementById("selection-preview");
    const completeSelectionBtn = document.getElementById("complete-selection");
    const clearSelectionBtn = document.getElementById("clear-selection");
    let sessionId = null;
    let symptomPanelEnabled = false;
    let bootPromise = null;
    const basePayload = { channel: "web", customer_id: "demo_user", shop_id: "default_shop", policy_version: "v1" };
    const symptomOrder = ["narrow", "normal", "wide", "hallux", "instep", "chubby", "toe"];
    const detailOrder = ["wide", "hallux", "instep", "toe"];
    const symptomMap = {
      narrow: "좁음",
      normal: "보통",
      wide: "넓음",
      hallux: "무지외반",
      instep: "발등 높음",
      chubby: "통통함",
      toe: "앞코"
    };
    const selectedSymptoms = new Set();
    const selectedDetails = {};

    function add(text, who, extra) {
      const div = document.createElement("div");
      div.className = "msg " + who;
      div.textContent = text || "";
      chat.appendChild(div);
      if (extra) {
        const meta = document.createElement("div");
        meta.className = "meta";
        meta.textContent = extra;
        chat.appendChild(meta);
      }
      chat.scrollTop = chat.scrollHeight;
    }

    function setUiStatus(status, label) {
      uiStatus.classList.remove("ok", "err");
      if (status === "ok") uiStatus.classList.add("ok");
      if (status === "err") uiStatus.classList.add("err");
      uiStatus.textContent = label;
    }

    function updateInputPlaceholder(state) {
      const map = {
        Q_ENTRY: "메시지를 입력하세요 (예: 1 또는 2)",
        Q_MEAS: "메시지를 입력하세요 (예: 네 / 아니요)",
        Q_MEAS_INPUT: "발볼 너비를 입력하세요 (예: 92)",
        Q_MEAS_LENGTH: "발길이를 입력하세요 (예: 235)",
        Q_DESIGN: "스타일을 선택하거나 입력하세요 (예: 구두)",
        Q_FOOT: "증상은 아래 패널에서 선택해 주세요",
        Q_FOOT_DETAIL: "세부 단계는 아래 버튼으로 선택해 주세요",
        Q_SIZE: "사이즈를 입력하세요 (예: 235)",
        Q_SIZE_FIT: "핏 라인을 선택하거나 입력하세요 (예: 편한핏)",
        Q_FIT_EXP: "착화 경험을 선택하거나 입력하세요",
      };
      msg.placeholder = map[state] || "메시지를 입력하세요";
    }

    function updateGuidedPanels(state) {
      const showQuickStart = state === "Q_ENTRY" || state === "START";
      quickStartPanel.classList.toggle("hidden", !showQuickStart);
      const showSymptom = state === "Q_FOOT" || state === "Q_FOOT_DETAIL";
      symptomPanel.classList.toggle("hidden", !showSymptom);
      setSymptomPanelEnabled(showSymptom);
    }

    async function sendMessage(text) {
      const t = (text || "").trim();
      if (!t) return;
      if (bootPromise) await bootPromise;
      add(t, "me");
      await callChat(t);
    }

    async function callChat(userText) {
      const payload = { ...basePayload, session_id: sessionId, message: userText };
      let data;
      try {
        const res = await fetch("/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
        data = await res.json();
      } catch (e) {
        setUiStatus("err", "UI 오류: API 호출 실패");
        throw e;
      }
      sessionId = data.session_id || sessionId;
      sidEl.textContent = sessionId || "없음";
      updateInputPlaceholder(data.state);
      updateGuidedPanels(data.state);
      if (["Q_FOOT", "Q_FOOT_DETAIL"].includes(data.state)) {
        chat.querySelectorAll(".quick").forEach((el) => el.remove());
      }
      add(data.text || "(응답 없음)", "bot");
      const useInlineQuickReplies = !["Q_FOOT", "Q_FOOT_DETAIL"].includes(data.state);
      if (useInlineQuickReplies && Array.isArray(data.quick_replies) && data.quick_replies.length) {
        const q = document.createElement("div");
        q.className = "quick";
        data.quick_replies.forEach((x) => {
          const b = document.createElement("button");
          b.textContent = x;
          b.onclick = () => {
            add(x, "me");
            callChat(x);
          };
          q.appendChild(b);
        });
        chat.appendChild(q);
        chat.scrollTop = chat.scrollHeight;
      }
      return data;
    }

    function setSymptomPanelEnabled(enabled) {
      symptomPanelEnabled = Boolean(enabled);
      document.body.classList.toggle("foot-mode", symptomPanelEnabled);
      symptomPanel.classList.toggle("disabled", !symptomPanelEnabled);
      symptomChips.querySelectorAll("button").forEach((b) => { b.disabled = !symptomPanelEnabled; });
      document.querySelectorAll(".chips-detail button").forEach((b) => { b.disabled = !symptomPanelEnabled; });
      completeSelectionBtn.disabled = !symptomPanelEnabled;
      clearSelectionBtn.disabled = !symptomPanelEnabled;
      if (symptomPanelEnabled) {
        chat.querySelectorAll(".quick").forEach((el) => el.remove());
      }
    }

    function updateSelectionPreview() {
      if (!selectedSymptoms.size) {
        selectionPreview.textContent = "선택된 항목: 없음";
        return;
      }
      const labels = symptomOrder
        .filter((key) => selectedSymptoms.has(key))
        .map((key) => {
          const detail = selectedDetails[key];
          return detail ? `${symptomMap[key]}(${detail})` : symptomMap[key];
        });
      selectionPreview.textContent = "선택된 항목: " + labels.join(", ");
    }

    function clearSelectionUI() {
      selectedSymptoms.clear();
      Object.keys(selectedDetails).forEach((k) => delete selectedDetails[k]);
      document.querySelectorAll("#symptom-chips button").forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".chips-detail").forEach((panel) => {
        panel.style.display = "none";
        panel.querySelectorAll("button").forEach((b) => b.classList.remove("active"));
      });
      updateSelectionPreview();
    }

    function composeBaseMessage() {
      return symptomOrder.filter((key) => selectedSymptoms.has(key)).map((key) => symptomMap[key]).join(", ");
    }

    function composeDetailMessage() {
      const vals = [];
      detailOrder.forEach((key) => {
        if (selectedSymptoms.has(key)) vals.push(selectedDetails[key] || "1");
      });
      return vals.join(",");
    }

    document.querySelectorAll('[data-role="quick-start"]').forEach((b) => {
      b.onclick = async () => { await sendMessage(b.dataset.msg || ""); };
    });
    symptomChips.querySelectorAll("button").forEach((b) => {
      b.onclick = () => {
        if (!symptomPanelEnabled) return;
        const key = b.dataset.symptom;
        if (!key) return;
        if (selectedSymptoms.has(key)) {
          selectedSymptoms.delete(key);
          delete selectedDetails[key];
          b.classList.remove("active");
          const detailPanel = document.getElementById(`detail-${key}`);
          if (detailPanel) {
            detailPanel.style.display = "none";
            detailPanel.querySelectorAll("button").forEach((x) => x.classList.remove("active"));
          }
        } else {
          selectedSymptoms.add(key);
          b.classList.add("active");
          const detailPanel = document.getElementById(`detail-${key}`);
          if (detailPanel) detailPanel.style.display = "flex";
        }
        updateSelectionPreview();
      };
    });
    document.querySelectorAll(".chips-detail button").forEach((b) => {
      b.onclick = () => {
        if (!symptomPanelEnabled) return;
        const symptom = b.dataset.detailFor;
        const value = b.dataset.value;
        if (!symptom || !value) return;
        selectedDetails[symptom] = value;
        const group = document.querySelectorAll(`.chips-detail button[data-detail-for="${symptom}"]`);
        group.forEach((x) => x.classList.remove("active"));
        b.classList.add("active");
        updateSelectionPreview();
      };
    });
    document.getElementById("complete-selection").onclick = async () => {
      if (!symptomPanelEnabled) return;
      const baseMessage = composeBaseMessage();
      if (!baseMessage) return;
      add(baseMessage, "me");
      const response = await callChat(baseMessage);
      if (response && response.state === "Q_FOOT_DETAIL") {
        const detailMessage = composeDetailMessage();
        if (detailMessage) {
          add(detailMessage, "me");
          await callChat(detailMessage);
        }
      }
    };
    document.getElementById("clear-selection").onclick = () => {
      if (!symptomPanelEnabled) return;
      clearSelectionUI();
    };
    document.getElementById("send").onclick = () => {
      const run = async () => {
      const t = msg.value.trim();
      msg.value = "";
      await sendMessage(t);
      };
      run();
    };
    document.getElementById("reset").onclick = async () => {
      sessionId = null;
      sidEl.textContent = "없음";
      chat.innerHTML = "";
      clearSelectionUI();
      bootPromise = callChat("시작");
      await bootPromise;
      bootPromise = null;
    };
    msg.addEventListener("keydown", (e) => { if (e.key === "Enter") document.getElementById("send").click(); });
    clearSelectionUI();
    updateGuidedPanels("Q_ENTRY");
    updateInputPlaceholder("Q_ENTRY");
    setUiStatus("ok", "UI 로드 완료");
    bootPromise = callChat("시작");
    bootPromise.finally(() => { bootPromise = null; });
  </script>
</body>
</html>"""

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
                "quick_replies": ["1·2단계 추천", "무지외반 상담", "발볼 상담"],
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
            "1·2단계 추천",
            "1,2단계 추천 받기",
            "1/2단계 추천",
            "1단계/2단계 추천",
            "추천받기",
            "무지외반 상담",
            "발볼 상담",
            "발볼·무지외반 상담",
            "발볼 무지외반 상담",
        )
        compact_keywords = (
            "ai12추천",
            "12단계추천",
            "12단계추천받기",
            "추천받기",
            "무지외반상담",
            "발볼상담",
            "발볼무지외반상담",
        )
        return any(k in text for k in keywords) or any(k in compact for k in compact_keywords)

    def _prepare_naver_ai_entry(session, message: str) -> str:
        """
        톡톡 추천 버튼 클릭을 AI 진단 시작 입력으로 정규화.
        - 상태와 무관하게 진단 시작점(Q_ENTRY)으로 되돌린다.
        - 항상 '1'(상품 선행)로 바로 진입시킨다.
        """
        session.state = SessionState.Q_ENTRY
        session.completed_at = None
        return "1"

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
                raw = str(item).strip()
                code = "1" if (("추천" in raw and "단계" in raw) or ("상담" in raw)) else raw[:1000]
                title = raw[:18] if len(raw) > 18 else raw
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

    @app.get("/demo", response_class=HTMLResponse)
    def demo_page():
        """추천엔진 시연용 간단 프론트."""
        return HTMLResponse(content=_DEMO_HTML)

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
        # 푸시가 성공하면 웹훅 동기 응답(send)을 생략해 중복 발화를 방지한다.
        pushed = _send_naver_push(inbound, result, session)
        if pushed:
            return {"ok": True, "session_id": session.session_id}

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
