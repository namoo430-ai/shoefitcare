from __future__ import annotations

from typing import Any

from adapters.base import ChannelAdapter, InboundMessage


class KakaoAdapter(ChannelAdapter):
    channel_name = "kakao"

    def parse_inbound(self, payload: dict[str, Any]) -> InboundMessage:
        req = payload.get("userRequest", {}) if isinstance(payload.get("userRequest"), dict) else {}
        user = req.get("user", {}) if isinstance(req.get("user"), dict) else {}
        user_id = str(user.get("id") or "anonymous")
        text = req.get("utterance") or ""
        if not isinstance(text, str):
            text = str(text)
        return InboundMessage(
            user_id=user_id,
            message=text.strip(),
            session_key=user_id,
            channel=self.channel_name,
            raw=payload,
        )

    def build_outbound(self, result: dict[str, Any]) -> dict[str, Any]:
        quick_replies = [
            {"label": str(q), "action": "message", "messageText": str(q)}
            for q in (result.get("quick_replies", []) or [])
        ]
        return {
            "version": "2.0",
            "template": {
                "outputs": [{"simpleText": {"text": result.get("text", "")}}],
                "quickReplies": quick_replies,
            },
        }

