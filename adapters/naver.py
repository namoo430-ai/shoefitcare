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
        user = payload.get("user", {}) if isinstance(payload.get("user"), dict) else {}
        event = payload.get("event", {}) if isinstance(payload.get("event"), dict) else {}
        session = payload.get("session", {}) if isinstance(payload.get("session"), dict) else {}

        user_id = (
            str(user.get("id") or payload.get("user_id") or payload.get("senderId") or "anonymous")
        )
        text = (
            payload.get("text")
            or payload.get("message")
            or event.get("text")
            or event.get("utterance")
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

