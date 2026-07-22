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
    from fastapi import FastAPI, HTTPException, Header, File, UploadFile, Form
    from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel
    import sys, os
    import json
    import hashlib
    import urllib.request
    import urllib.error
    from datetime import datetime
    from collections import Counter
    from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
    _ROOT = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, _ROOT)

    from core.session import ConversationController, SessionStore, SessionState
    from core.storage import init_db
    from adapters.naver import NaverAdapter
    from adapters.kakao import KakaoAdapter

    app = FastAPI(title="슈핏케어 API")
    _IMAGES_DIR = os.path.join(_ROOT, "images")
    if os.path.isdir(_IMAGES_DIR):
        app.mount("/product-images", StaticFiles(directory=_IMAGES_DIR), name="product-images")
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
    # 데모 UI/세션 변경 확인용 — 화면에 표시됨. 값이 안 바뀌면 서버 재시작 필요.
    DEMO_UI_BUILD = "20260529-pilot-legacy-demo"
    from pilot_storage import (
        init_pilot_tables,
        create_diagnosis,
        complete_precision,
        update_diagnosis,
        register_order_no_diagnosis,
        list_diagnoses,
        get_diagnosis_by_code,
        kpi_counts,
        return_rate_by_cohort,
        record_funnel_event,
        funnel_kpi,
        foot_profile_kpi,
        return_prior_lookup,
        backfill_foot_profiles,
        coupang_pilot_kpi,
        naver_pilot_kpi,
        daily_diagnosis_counts,
        list_funnel_events_for_diagnosis,
        get_ops_counters,
        upsert_ops_counter,
        pilot_storage_meta,
        upsert_photo_daily,
        save_precision_photo,
        resolve_precision_photo_path,
    )
    from pilot_ui import PILOT_HTML, ADMIN_HTML, SELLER_QUICK_HTML, PILOT_BUILD, PILOT_COPY_JSON
    from pilot_engine import PILOT_RULE_VERSION, sf_engine_hint
    from pilot_foot_compare import build_foot_compare_view
    from pilot_seller_reply import build_seller_reply

    init_pilot_tables()
    _ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "").strip()

    def _require_admin(x_admin_token: str | None = None) -> None:
        if not _ADMIN_TOKEN:
            raise HTTPException(status_code=503, detail="ADMIN_TOKEN not configured")
        if (x_admin_token or "").strip() != _ADMIN_TOKEN:
            raise HTTPException(status_code=401, detail="unauthorized")

    def _admin_token_from_query(token: str | None = None) -> str | None:
        return (token or "").strip() or None

    def _resolve_admin_token(
        x_admin_token: str | None = None,
        token: str | None = None,
    ) -> str | None:
        return (x_admin_token or "").strip() or _admin_token_from_query(token)

    def _admin_date_params(
        from_date: str | None = None,
        to_date: str | None = None,
    ) -> dict[str, str | None]:
        fd = (from_date or "").strip()[:10] or None
        td = (to_date or "").strip()[:10] or None
        return {"from_date": fd, "to_date": td}

    def _admin_diagnosis_detail_payload(row: dict) -> dict:
        q2 = row.get("q2") or []
        if not q2 and row.get("q2_json"):
            try:
                q2 = json.loads(row["q2_json"])
            except json.JSONDecodeError:
                q2 = []
        hint_raw = row.get("engine_hint_json")
        engine_hint: dict = {}
        if hint_raw:
            try:
                engine_hint = json.loads(hint_raw)
            except json.JSONDecodeError:
                engine_hint = {}
        foot_compare = build_foot_compare_view(
            r_code=row.get("r_code") or "R1",
            p_code=row.get("p_code") or "P0",
            s_code=row.get("s_code") or "S0",
            q1=row.get("q1") or "",
            q2=q2,
            recommendation_code=row.get("recommendation_code") or "",
        )
        code = (row.get("recommendation_code") or "SF00").strip().upper()
        stretch_hint = sf_engine_hint(code)
        try:
            seller_preview = build_seller_reply(row, seller_fit_line="기본핏")
        except ValueError:
            seller_preview = {}
        events = list_funnel_events_for_diagnosis(str(row.get("id") or ""))
        safe = {k: row.get(k) for k in row if k != "contact_masked"}
        safe["q2"] = q2
        safe["foot_profile"] = row.get("foot_profile")
        return {
            "diagnosis": safe,
            "foot_compare": foot_compare,
            "engine_hint": engine_hint,
            "stretch_hint": stretch_hint,
            "seller_preview": seller_preview,
            "funnel_timeline": events,
        }

    _DEMO_HTML = """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>슈핏케어 추천엔진 데모</title>
  <style>
    :root { --pink: #c97b84; --pink-soft: #f3e4e6; --bg: #f2f2f7; --card: #ffffff; --text: #1c1c1e; --muted: #8e8e93; }
    * { box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", sans-serif; margin: 0; background: var(--bg); color: var(--text); -webkit-font-smoothing: antialiased; }
    .phone { max-width: 430px; margin: 0 auto; min-height: 100dvh; display: flex; flex-direction: column; background: var(--bg); }
    .head { padding: 14px 16px 10px; background: var(--card); border-bottom: 1px solid rgba(0,0,0,.06); }
    .head h1 { margin: 0; font-size: 17px; font-weight: 600; }
    .head p { margin: 4px 0 0; font-size: 14px; color: var(--muted); line-height: 1.45; }
    .status-badge { display: none; }
    body.foot-mode .chat .quick { display: none !important; }
    .chat { flex: 1; overflow: auto; padding: 12px 14px 100px; }
    .msg { max-width: 88%; margin: 6px 0; padding: 12px 14px; border-radius: 18px; white-space: pre-wrap; line-height: 1.55; font-size: 16px; }
    .bot { background: var(--card); border: 1px solid rgba(0,0,0,.04); border-bottom-left-radius: 6px; box-shadow: 0 1px 2px rgba(0,0,0,.04); }
    .me { display: none; }
    .quick { display: flex; flex-direction: column; gap: 8px; margin: 8px 0 4px; max-width: 88%; }
    .quick button { border: 0; background: var(--card); color: var(--pink); border-radius: 14px; padding: 12px 14px; font-size: 16px; font-weight: 500; cursor: pointer; text-align: left; box-shadow: 0 1px 2px rgba(0,0,0,.06); }
    .quick button:active { background: var(--pink-soft); }
    .panel { padding: 10px 12px; border-top: 1px solid rgba(0,0,0,.06); background: var(--card); }
    .panel.hidden { display: none !important; }
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
    #complete-selection { background: var(--pink); color: #fff; }
    #clear-selection { background: #aeaeb2; color: #fff; }
    .composer { display: flex; gap: 8px; padding: 10px 12px calc(10px + env(safe-area-inset-bottom)); background: var(--card); border-top: 1px solid rgba(0,0,0,.06); }
    .composer input { flex: 1; border: 1px solid rgba(0,0,0,.08); border-radius: 20px; padding: 10px 14px; font-size: 16px; background: var(--bg); }
    .composer button { border: 0; background: var(--pink); color: #fff; border-radius: 20px; padding: 10px 16px; font-size: 15px; font-weight: 600; cursor: pointer; }
    #reset { background: transparent; color: var(--muted); font-weight: 500; }
    .cta-bar { display: none; position: fixed; left: 0; right: 0; bottom: 0; max-width: 430px; margin: 0 auto; padding: 10px 14px calc(10px + env(safe-area-inset-bottom)); background: rgba(255,255,255,.92); backdrop-filter: blur(12px); border-top: 1px solid rgba(0,0,0,.06); z-index: 20; }
    .cta-bar.show { display: block; }
    .cta-bar button { width: 100%; border: 0; background: var(--pink); color: #fff; font-size: 16px; font-weight: 600; padding: 14px; border-radius: 14px; margin-top: 6px; }
    .cta-bar button.secondary { background: #fff; color: var(--pink); border: 1px solid var(--pink); }
    .cta-bar button.copy { background: #4a5568; }
    .cta-trust { text-align: center; font-size: 13px; color: var(--muted); margin: 0 0 8px; line-height: 1.4; }
    .row { display: none; }
  </style>
</head>
<body>
  <div class="phone">
    <div class="head">
      <h1>슈핏케어</h1>
      <p id="head-greet">내 발에 맞는 편한 신발, 간단하게 찾아보세요.</p>
      <p style="font-size:11px;color:#c97b84;margin:4px 0 0">빌드 __DEMO_BUILD__</p>
      <span id="ui-status" class="status-badge">UI</span>
    </div>
    <div class="row">session_id: <span id="sid">없음</span></div>
    <div id="chat" class="chat"></div>
    <div id="quick-start-panel" class="panel hidden">
      <div class="label">빠른 시작</div>
      <div class="chips"></div>
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
    <div class="composer">
      <input id="msg" placeholder="숫자·사이즈 입력" />
      <button id="send">보내기</button>
      <button id="reset">새로</button>
    </div>
    <div id="cta-bar" class="cta-bar">
      <p class="cta-trust">진단 상품으로 주문하시거나, 다른 상품을 둘러보실 수 있어요</p>
      <button type="button" id="cta-buy">진단 상품 바로가기</button>
      <button type="button" id="cta-browse-other" class="secondary">다른 상품 보러가기</button>
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
    const urlParams = new URLSearchParams(window.location.search);
    const basePayload = {
      channel: "web",
      customer_id: "demo_user",
      shop_id: "default_shop",
      policy_version: "v1",
      product_id: urlParams.get("product_id") || null,
      traffic_src: urlParams.get("src") || "html_detail",
    };
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

    function clearChatView() {
      chat.innerHTML = "";
    }

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
      quickStartPanel.classList.add("hidden");
      const showSymptom = state === "Q_FOOT" || state === "Q_FOOT_DETAIL";
      symptomPanel.classList.toggle("hidden", !showSymptom);
      setSymptomPanelEnabled(showSymptom);
    }

    const ctaBar = document.getElementById("cta-bar");
    let lastCheckout = null;
    let lastInquiryCopy = "";
    let chatBusy = false;

    async function postCtaEvent(eventName) {
      if (!sessionId) return;
      try {
        await fetch("/ops/cta-event", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            session_id: sessionId,
            event: eventName,
            shop_id: basePayload.shop_id,
            policy_version: basePayload.policy_version,
          }),
        });
      } catch (e) { /* ignore */ }
    }

    async function sendMessage(text, opts) {
      const t = (text || "").trim();
      if (!t) return;
      if (bootPromise) await bootPromise;
      await callChat(t, opts);
    }

    async function callChat(userText, opts) {
      if (chatBusy) return null;
      chatBusy = true;
      chat.querySelectorAll(".quick button").forEach((b) => { b.disabled = true; });
      const payload = { ...basePayload, session_id: sessionId, message: userText };
      let data;
      try {
        const res = await fetch("/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
        data = await res.json();
      } catch (e) {
        setUiStatus("err", "UI 오류: API 호출 실패");
        chatBusy = false;
        throw e;
      } finally {
        chatBusy = false;
      }
      sessionId = data.session_id || sessionId;
      sidEl.textContent = sessionId || "없음";
      updateInputPlaceholder(data.state);
      updateGuidedPanels(data.state);
      clearChatView();
      if (["Q_FOOT", "Q_FOOT_DETAIL"].includes(data.state)) {
        chat.querySelectorAll(".quick").forEach((el) => el.remove());
      }
      add(data.text || "(응답 없음)", "bot");
      if (data.checkout_payload) lastCheckout = data.checkout_payload;
      lastInquiryCopy = data.inquiry_copy_text || (lastCheckout && lastCheckout.inquiry_copy_text) || "";
      ctaBar.classList.toggle("show", Boolean(data.show_cta));
      const useInlineQuickReplies = !["Q_FOOT", "Q_FOOT_DETAIL"].includes(data.state);
      if (useInlineQuickReplies && Array.isArray(data.quick_replies) && data.quick_replies.length) {
        const q = document.createElement("div");
        q.className = "quick";
        data.quick_replies.forEach((x) => {
          const b = document.createElement("button");
          b.textContent = x;
          b.onclick = () => { if (!chatBusy) sendMessage(x, { echo: false }); };
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

    document.getElementById("cta-buy").onclick = async () => {
      await postCtaEvent("cta_buy_diagnosed");
      const url = (lastCheckout && lastCheckout.product_url) ? String(lastCheckout.product_url).trim() : "";
      if (url) {
        window.open(url, "_blank", "noopener");
        return;
      }
      alert("상품 링크를 불러오지 못했습니다. CSV product_url을 확인해 주세요.");
    };
    document.getElementById("cta-browse-other").onclick = async () => {
      await postCtaEvent("cta_browse_other");
      const url = (lastCheckout && lastCheckout.browse_url) ? String(lastCheckout.browse_url).trim() : "";
      if (url) window.open(url, "_blank", "noopener");
    };
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
      const response = await callChat(baseMessage, { echo: false });
      if (response && response.state === "Q_FOOT_DETAIL") {
        const detailMessage = composeDetailMessage();
        if (detailMessage) await callChat(detailMessage, { echo: false });
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
      ctaBar.classList.remove("show");
      bootPromise = callChat("", { echo: false });
      await bootPromise;
      bootPromise = null;
    };
    msg.addEventListener("keydown", (e) => { if (e.key === "Enter") document.getElementById("send").click(); });
    clearSelectionUI();
    updateGuidedPanels("Q_ENTRY");
    updateInputPlaceholder("Q_ENTRY");
    setUiStatus("ok", "UI 로드 완료");
    bootPromise = (async () => {
      const mode = (urlParams.get("mode") || "").toLowerCase();
      if (mode === "lite") {
        await callChat("간단하게 추천받기", { echo: false });
      } else if (mode === "full") {
        await callChat("내 발에 맞게 자세히 진단하기", { echo: false });
      } else {
        await callChat("", { echo: false });
      }
    })();
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
        product_id: str | None = None
        traffic_src: str | None = None

    class CtaEventRequest(BaseModel):
        session_id: str
        event: str
        shop_id: str = "default_shop"
        policy_version: str = "v1"

    @app.get("/")
    def root():
        return RedirectResponse(url="/pilot", status_code=302)

    @app.get("/health/build")
    def health_build():
        from pilot_engine import PILOT_RULE_VERSION
        from pilot_links import (
            PILOT_GO,
            PILOT_SHORT_CODE,
            naver_pilot_registry,
            naver_sms_short_code_map,
        )

        from pilot_copy import PILOT_COPY_VERSION

        return {
            "demo_ui_build": DEMO_UI_BUILD,
            "pilot_build": PILOT_BUILD,
            "pilot_copy_version": PILOT_COPY_VERSION,
            "pilot_short_paths": sorted(PILOT_GO.keys()),
            "pilot_short_codes": dict(PILOT_SHORT_CODE),
            "naver_pilot_skus": sorted(naver_pilot_registry().keys()),
            "naver_sms_short_codes": naver_sms_short_code_map(),
            "pilot_rule_version": PILOT_RULE_VERSION,
            "pilot_4_questions": True,
            "pilot_5_questions": False,
            "lite_2_questions": False,
            "demo_clear_each_step": True,
            "full_without_comfort_block": True,
            "coupang_inquiry_cta": True,
            "admin_dashboard": True,
            "seller_quick": True,
            "pilot_precision_photo_upload": True,
            "product_detail_html": True,
        }

    @app.get("/c/{sku}")
    def pilot_short_link(sku: str):
        """문자·CS용 짧은 URL → /pilot (상품별 return_url은 pilot_links.PILOT_GO)."""
        from pilot_links import pilot_path_for_sku

        path = pilot_path_for_sku(sku)
        if not path:
            raise HTTPException(status_code=404, detail="unknown pilot sku")
        return RedirectResponse(url=path, status_code=302)

    @app.get("/nv/{sku}")
    def naver_pilot_by_sku(sku: str):
        """네이버 CS 회신 — 상품 ID 직접 (예: /nv/SR266, /nv/NAVER_SKU_01)."""
        from pilot_links import naver_pilot_path_for_sku

        path = naver_pilot_path_for_sku(sku)
        if not path:
            raise HTTPException(status_code=404, detail="invalid naver product_id")
        return RedirectResponse(url=path, status_code=302)

    @app.get("/n/{code}")
    def naver_sms_short_link(code: str):
        """네이버 CS·톡톡: 짧은코드(/n/1) 또는 product_id(/n/SR266) → pilot?src=naver_sms"""
        from pilot_links import naver_pilot_path_for_code

        path = naver_pilot_path_for_code(code)
        if not path:
            raise HTTPException(status_code=404, detail="unknown naver short code")
        return RedirectResponse(
            url=path,
            status_code=302,
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"},
        )

    @app.get("/s/{code}")
    def pilot_ultra_short_link(code: str):
        """초단축 코드 (예: /s/1) → /pilot. 매핑: pilot_links.PILOT_SHORT_CODE."""
        from pilot_links import pilot_path_for_sku, sku_from_short_code

        sku = sku_from_short_code(code)
        if not sku:
            raise HTTPException(status_code=404, detail="unknown short code")
        path = pilot_path_for_sku(sku)
        if not path:
            raise HTTPException(status_code=404, detail="unknown pilot sku")
        return RedirectResponse(url=path, status_code=302)

    @app.get("/pilot", response_class=HTMLResponse)
    def pilot_page():
        html = PILOT_HTML.replace("__PILOT_BUILD__", PILOT_BUILD).replace(
            "__PILOT_COPY_JSON__", PILOT_COPY_JSON
        )
        return HTMLResponse(html, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

    @app.get("/admin", response_class=HTMLResponse)
    def admin_page():
        return HTMLResponse(ADMIN_HTML, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

    @app.get("/seller/quick", response_class=HTMLResponse)
    def seller_quick_page():
        return HTMLResponse(SELLER_QUICK_HTML, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

    def _seller_diagnosis_summary(row: dict) -> dict:
        return {
            "id": row.get("id"),
            "diagnosis_code": row.get("diagnosis_code"),
            "recommendation_code": row.get("recommendation_code"),
            "q4": row.get("q4"),
            "product_id": row.get("product_id"),
            "channel": row.get("channel"),
            "r_code": row.get("r_code"),
            "p_code": row.get("p_code"),
            "s_code": row.get("s_code"),
            "actual_work_step": row.get("actual_work_step"),
            "memo": row.get("memo"),
            "created_at": row.get("created_at"),
        }

    @app.get("/api/seller/diagnosis")
    def api_seller_diagnosis(
        code: str = "",
        x_admin_token: str | None = Header(None, alias="X-Admin-Token"),
        token: str | None = None,
    ):
        _require_admin(_resolve_admin_token(x_admin_token, token))
        row = get_diagnosis_by_code(code)
        if not row:
            raise HTTPException(status_code=404, detail="진단번호를 찾을 수 없습니다.")
        return _seller_diagnosis_summary(row)

    class SellerReplyRequest(BaseModel):
        diagnosis_code: str
        seller_fit_line: str = "기본핏"
        actual_work_step: int | None = None
        save: bool = False
        memo: str | None = None

    @app.post("/api/seller/reply")
    def api_seller_reply(
        body: SellerReplyRequest,
        x_admin_token: str | None = Header(None, alias="X-Admin-Token"),
        token: str | None = None,
    ):
        _require_admin(_resolve_admin_token(x_admin_token, token))
        row = get_diagnosis_by_code(body.diagnosis_code)
        if not row:
            raise HTTPException(status_code=404, detail="진단번호를 찾을 수 없습니다.")
        try:
            replies = build_seller_reply(
                row,
                seller_fit_line=body.seller_fit_line,
                actual_work_step=body.actual_work_step,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        if body.save and row.get("id"):
            step = body.actual_work_step
            if step is None:
                step = int(replies.get("suggested_work_step") or 0)
            memo_bits = [f"핏:{replies.get('seller_fit_line', '')}"]
            if body.memo:
                memo_bits.append(body.memo.strip())
            update_diagnosis(
                row["id"],
                {
                    "actual_work_step": step,
                    "memo": " · ".join(memo_bits),
                },
            )
        return {
            **replies,
            "diagnosis": _seller_diagnosis_summary(row),
        }

    class PilotDiagnoseRequest(BaseModel):
        q1: str
        q2: list[str] = []
        q3: str = ""
        q4: int = 235
        q5: str = ""
        product_id: str | None = None
        channel: str = "web"

    @app.post("/pilot/diagnose")
    def pilot_diagnose(req: PilotDiagnoseRequest):
        if req.q4 not in range(225, 256, 5):
            return {"error": "Q4 사이즈는 225~255 (5mm) 만 허용됩니다."}
        return create_diagnosis(
            req.model_dump(),
            channel=req.channel,
            product_id=req.product_id,
        )

    @app.get("/api/pilot/store-links")
    def api_pilot_store_links():
        from pilot_store_links import naver_store_links

        return naver_store_links()

    class PilotPrecisionRequest(BaseModel):
        diagnosis_id: str
        left_length_cm: float
        right_length_cm: float
        left_width_cm: float
        right_width_cm: float
        contact: str
        consent: bool = False

    @app.post("/pilot/precision")
    def pilot_precision(req: PilotPrecisionRequest):
        try:
            return complete_precision(
                req.diagnosis_id,
                left_length_cm=req.left_length_cm,
                right_length_cm=req.right_length_cm,
                left_width_cm=req.left_width_cm,
                right_width_cm=req.right_width_cm,
                contact=req.contact,
                consent=req.consent,
            )
        except ValueError as e:
            return {"error": str(e)}

    @app.post("/pilot/precision-photo")
    async def pilot_precision_photo(
        diagnosis_id: str = Form(...),
        photo: UploadFile = File(...),
    ):
        try:
            raw = await photo.read()
            result = save_precision_photo(
                diagnosis_id.strip(),
                content=raw,
                content_type=photo.content_type or "",
            )
            record_funnel_event(
                "precision_photo_uploaded",
                channel="pilot",
                diagnosis_id=diagnosis_id.strip(),
            )
            return result
        except ValueError as e:
            return {"ok": False, "error": str(e)}

    class PilotFunnelEventRequest(BaseModel):
        event: str
        product_id: str | None = None
        channel: str = "html_detail"
        diagnosis_id: str | None = None

    @app.post("/pilot/event")
    def pilot_funnel_event(req: PilotFunnelEventRequest):
        try:
            record_funnel_event(
                req.event.strip(),
                product_id=req.product_id,
                channel=req.channel,
                diagnosis_id=req.diagnosis_id,
            )
        except ValueError as e:
            return {"ok": False, "error": str(e)}
        return {"ok": True}

    class AdminPhotoDailyRequest(BaseModel):
        log_date: str
        photo_count: int
        memo: str = ""

    @app.put("/api/admin/photo-daily")
    def api_admin_photo_daily(
        body: AdminPhotoDailyRequest,
        x_admin_token: str | None = Header(None, alias="X-Admin-Token"),
    ):
        _require_admin(x_admin_token)
        try:
            upsert_photo_daily(body.log_date, body.photo_count, body.memo)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        return {"ok": True, "funnel": funnel_kpi()}

    @app.get("/api/admin/diagnoses/{diagnosis_id}/photo")
    def api_admin_diagnosis_photo(
        diagnosis_id: str,
        x_admin_token: str | None = Header(None, alias="X-Admin-Token"),
        token: str | None = None,
    ):
        _require_admin(_resolve_admin_token(x_admin_token, token))
        path = resolve_precision_photo_path(diagnosis_id)
        if not path:
            raise HTTPException(status_code=404, detail="photo not found")
        return FileResponse(path)

    @app.get("/api/admin/kpi")
    def api_admin_kpi(
        from_date: str | None = None,
        to_date: str | None = None,
        x_admin_token: str | None = Header(None, alias="X-Admin-Token"),
        token: str | None = None,
    ):
        _require_admin(_resolve_admin_token(x_admin_token, token))
        from pilot_ui import PILOT_BUILD as _pb

        dates = _admin_date_params(from_date, to_date)
        fd, td = dates["from_date"], dates["to_date"]
        return {
            "counts": kpi_counts(from_date=fd, to_date=td),
            "cohort": return_rate_by_cohort(from_date=fd, to_date=td),
            "funnel": funnel_kpi(from_date=fd, to_date=td),
            "storage": pilot_storage_meta(),
            "foot_profile": foot_profile_kpi(from_date=fd, to_date=td),
            "coupang": coupang_pilot_kpi(from_date=fd, to_date=td),
            "naver": naver_pilot_kpi(from_date=fd, to_date=td),
            "daily_diagnoses": daily_diagnosis_counts(from_date=fd, to_date=td),
            "daily_naver": daily_diagnosis_counts(
                from_date=fd, to_date=td, channel_like="naver%"
            ),
            "daily_coupang": daily_diagnosis_counts(
                from_date=fd, to_date=td, channel_like="coupang%"
            ),
            "pilot_build": _pb,
            "pilot_rule_version": PILOT_RULE_VERSION,
            "from_date": fd,
            "to_date": td,
        }

    class AdminCoupangOpsRequest(BaseModel):
        wing_orders: int = 0
        sms_sent: int = 0
        inquiry_inbound: int = 0
        memo: str = ""

    @app.put("/api/admin/coupang-ops")
    def api_admin_coupang_ops(
        body: AdminCoupangOpsRequest,
        x_admin_token: str | None = Header(None, alias="X-Admin-Token"),
    ):
        _require_admin(x_admin_token)
        memo = body.memo or ""
        upsert_ops_counter("coupang_wing_orders", body.wing_orders, memo)
        upsert_ops_counter("coupang_sms_sent", body.sms_sent, memo)
        upsert_ops_counter("coupang_inquiry_inbound", body.inquiry_inbound, memo)
        return {"ok": True, "coupang": coupang_pilot_kpi()}

    class AdminNaverOpsRequest(BaseModel):
        store_orders: int = 0
        sms_sent: int = 0
        talktalk_inbound: int = 0
        memo: str = ""

    @app.put("/api/admin/naver-ops")
    def api_admin_naver_ops(
        body: AdminNaverOpsRequest,
        x_admin_token: str | None = Header(None, alias="X-Admin-Token"),
    ):
        _require_admin(x_admin_token)
        memo = body.memo or ""
        upsert_ops_counter("naver_store_orders", body.store_orders, memo)
        upsert_ops_counter("naver_sms_sent", body.sms_sent, memo)
        upsert_ops_counter("naver_talktalk_inbound", body.talktalk_inbound, memo)
        return {"ok": True, "naver": naver_pilot_kpi()}

    @app.get("/api/admin/diagnoses/by-code/{diagnosis_code}")
    def api_admin_diagnosis_by_code(
        diagnosis_code: str,
        x_admin_token: str | None = Header(None, alias="X-Admin-Token"),
        token: str | None = None,
    ):
        _require_admin(_resolve_admin_token(x_admin_token, token))
        row = get_diagnosis_by_code(diagnosis_code)
        if not row:
            raise HTTPException(status_code=404, detail="진단번호를 찾을 수 없습니다.")
        return _admin_diagnosis_detail_payload(row)

    @app.get("/api/admin/return-prior")
    def api_admin_return_prior(
        r_code: str,
        p_code: str,
        s_code: str,
        product_id: str | None = None,
        x_admin_token: str | None = Header(None, alias="X-Admin-Token"),
        token: str | None = None,
    ):
        _require_admin(_resolve_admin_token(x_admin_token, token))
        return return_prior_lookup(r_code, p_code, s_code, product_id=product_id)

    @app.get("/api/admin/diagnoses")
    def api_admin_diagnoses(
        q: str = "",
        r_code: str = "",
        p_code: str = "",
        from_date: str | None = None,
        to_date: str | None = None,
        workshop: bool = False,
        pending_work: bool = False,
        x_admin_token: str | None = Header(None, alias="X-Admin-Token"),
        token: str | None = None,
    ):
        _require_admin(_resolve_admin_token(x_admin_token, token))
        dates = _admin_date_params(from_date, to_date)
        return {
            "items": list_diagnoses(
                q=q,
                r_code=r_code,
                p_code=p_code,
                from_date=dates["from_date"],
                to_date=dates["to_date"],
                workshop_only=workshop,
                pending_work_only=pending_work,
            )
        }

    class AdminDiagnosisPatch(BaseModel):
        order_no: str | None = None
        return_status: int | None = None
        return_reason: str | None = None
        actual_work_step: int | None = None
        memo: str | None = None

    @app.patch("/api/admin/diagnoses/{diagnosis_id}")
    def api_admin_patch(
        diagnosis_id: str,
        body: AdminDiagnosisPatch,
        x_admin_token: str | None = Header(None, alias="X-Admin-Token"),
    ):
        _require_admin(x_admin_token)
        fields = {k: v for k, v in body.model_dump().items() if v is not None}
        update_diagnosis(diagnosis_id, fields)
        return {"ok": True}

    class AdminOrderNoDx(BaseModel):
        order_no: str
        return_status: int = 0
        return_reason: str = ""
        product_id: str | None = None

    @app.post("/api/admin/orders/no-diagnosis")
    def api_admin_order_no_dx(
        body: AdminOrderNoDx,
        x_admin_token: str | None = Header(None, alias="X-Admin-Token"),
    ):
        _require_admin(x_admin_token)
        oid = register_order_no_diagnosis(
            body.order_no,
            product_id=body.product_id,
            return_status=body.return_status,
            return_reason=body.return_reason,
        )
        return {"ok": True, "id": oid}

    @app.get("/product-detail", response_class=HTMLResponse)
    def product_detail_page(product_id: str | None = None):
        """쿠팡 연동용 자사 HTML 상세 — 간단/정밀 진단 링크."""
        path = os.path.join(_ROOT, "docs", "demo", "product_detail.html")
        if not os.path.isfile(path):
            return HTMLResponse("<h1>product_detail.html not found</h1>", status_code=404)
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        pid = (product_id or "").strip()
        html = html.replace("__PRODUCT_ID__", pid or "13352256777")
        return HTMLResponse(html, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

    @app.get("/demo", response_class=HTMLResponse)
    def demo_page():
        """추천엔진 시연용 간단 프론트."""
        html = _DEMO_HTML.replace("__DEMO_BUILD__", DEMO_UI_BUILD)
        return HTMLResponse(
            content=html,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
            },
        )

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
            if req.product_id:
                session.pinned_product_id = str(req.product_id).strip()
            if req.traffic_src:
                session.traffic_src = str(req.traffic_src).strip()
            _audit_event("chat_start", session.session_id, session.channel, session.shop_id, session.policy_version, req.message)
            msg = (req.message or "").strip()
            if msg:
                result = _safe_handle_message(session, msg)
                store.save(session)
                return {"session_id": session.session_id, **result}
            intro = ctrl.get_initial_prompt(session)
            store.save(session)
            return {"session_id": session.session_id, **intro}
        session.shop_id = req.shop_id
        session.policy_version = req.policy_version
        if req.product_id:
            session.pinned_product_id = str(req.product_id).strip()
        if req.traffic_src:
            session.traffic_src = str(req.traffic_src).strip()

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

        # 네이버 채널에 빈 텍스트가 전달되면 콘솔에서 "-"로 보일 수 있으므로 방어.
        text_out = str(result.get("text") or "").strip()
        if text_out in ("", "-"):
            result["text"] = _FALLBACK_TEXT
            _audit_event(
                "naver_empty_text_fallback",
                session.session_id,
                session.channel,
                session.shop_id,
                session.policy_version,
                inbound.message,
            )

        # 톡톡 UI는 웹훅 동기 본문(event: send)에 의존한다. {ok:true}만 반환하면 무반응처럼 보일 수 있음.
        # 보내기 API는 NAVER_WEBHOOK_ALSO_PUSH=true 일 때만 추가 호출(기본 off, 중복·UI 미반영 방지).
        _also_push = os.environ.get("NAVER_WEBHOOK_ALSO_PUSH", "false").strip().lower() in (
            "1", "true", "yes", "on",
        )
        if _NAVER_SEND_API_ENABLED and _also_push:
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
        from hybrid_recommender import HybridProductRecommender

        payload = get_return_rate_report(shop_id=shop_id, policy_version=policy_version)
        payload["scoring_policy"] = HybridProductRecommender().score_policy_snapshot(policy_version)
        return payload

    @app.post("/ops/cta-event")
    def cta_event(req: CtaEventRequest):
        """데모 CTA: 구매 의도 / 이탈 / 문의 복사 (민감 원문 없음)."""
        allowed = {"cta_buy_diagnosed", "cta_browse_other", "cta_copy_inquiry"}
        if req.event not in allowed:
            return {"ok": False, "error": "invalid event"}
        _audit_event(
            req.event,
            req.session_id,
            "web",
            req.shop_id,
            req.policy_version,
            "",
        )
        return {"ok": True, "event": req.event}

    @app.post("/ops/rag-sync-products")
    def rag_sync_products():
        """상품 CSV -> RAG 상품 문서 동기화"""
        from rag_product_sync import sync_product_rag_docs

        result = sync_product_rag_docs()
        return {"ok": True, "result": result}

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
        recent_samples = []
        for row in filtered[-5:]:
            recent_samples.append(
                {
                    "ts": row.get("ts"),
                    "event": row.get("event"),
                    "session_id": row.get("session_id"),
                    "shop_id": row.get("shop_id"),
                    "policy_version": row.get("policy_version"),
                    "message_len": row.get("message_len", 0),
                }
            )
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
            "recent_samples": recent_samples,
        }

except ImportError:
    # fastapi 미설치 시 스킵 (CLI 모드에서는 불필요)
    pass
