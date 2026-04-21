from __future__ import annotations

from typing import Any

from adapters.base import ChannelAdapter, InboundMessage


class NaverAdapter(ChannelAdapter):
    """
    Naver payload normalizer.

    Supports multiple key shapes so we can integrate quickly and
    tighten to exact schema once webhook spec is finalized.
    """

    channel_name = "naver"

    def parse_inbound(self, payload: dict[str, Any]) -> InboundMessage:
        raw_user = payload.get("user")
        user: dict[str, Any] = raw_user if isinstance(raw_user, dict) else {}
        event = payload.get("event", {}) if isinstance(payload.get("event"), dict) else {}
        text_content = payload.get("textContent", {}) if isinstance(payload.get("textContent"), dict) else {}
        session = payload.get("session", {}) if isinstance(payload.get("session"), dict) else {}

        # 공식 웹훅은 `"user": "..."` 문자열(사용자 식별값)로 올 수 있음(chatbot-api README).
        if isinstance(raw_user, str) and raw_user.strip():
            user_id = raw_user.strip()
        else:
            user_id = str(user.get("id") or payload.get("user_id") or payload.get("senderId") or "anonymous")
        postback = event.get("postback", {}) if isinstance(event.get("postback"), dict) else {}
        action = event.get("action", {}) if isinstance(event.get("action"), dict) else {}
        text = (
            text_content.get("code")
            or text_content.get("text")
            or payload.get("text")
            or payload.get("message")
            or event.get("text")
            or event.get("utterance")
            or event.get("postback")
            or postback.get("text")
            or postback.get("label")
            or postback.get("payload")
            or action.get("text")
            or action.get("label")
            or action.get("payload")
            or ""
        )
        if not isinstance(text, str):
            text = str(text)

        session_key = (
            str(session.get("id") or payload.get("session_id") or payload.get("conversationId") or user_id)
        )
        return InboundMessage(
            user_id=user_id,
            message=text.strip(),
            session_key=session_key,
            channel=self.channel_name,
            raw=payload,
        )

    def build_outbound(self, result: dict[str, Any]) -> dict[str, Any]:
        quick = result.get("quick_replies", []) or []
        chips = [{"label": str(item), "text": str(item)} for item in quick]
        return {
            "text": result.get("text", ""),
            "quickReplies": chips,
            "done": bool(result.get("done")),
            "diagnosis": result.get("diagnosis"),
        }

