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

    @staticmethod
    def _pick_first_str(*values: Any) -> str:
        """Return first non-empty value as stripped string."""
        for value in values:
            if value is None:
                continue
            if isinstance(value, str):
                text = value.strip()
                if text:
                    return text
                continue
            text = str(value).strip()
            if text:
                return text
        return ""

    @classmethod
    def _extract_text_from_nested(cls, value: Any, depth: int = 0) -> str:
        """
        Fallback extractor for payload variants:
        find first non-empty string in text-like keys only.
        """
        if depth > 4:
            return ""
        if isinstance(value, str):
            text = value.strip()
            return text if text else ""
        if isinstance(value, list):
            for item in value:
                found = cls._extract_text_from_nested(item, depth + 1)
                if found:
                    return found
            return ""
        if not isinstance(value, dict):
            return ""

        preferred_keys = ("text", "utterance", "message", "code", "value", "label", "payload")
        for key in preferred_keys:
            if key in value:
                found = cls._extract_text_from_nested(value.get(key), depth + 1)
                if found:
                    return found

        for sub_value in value.values():
            found = cls._extract_text_from_nested(sub_value, depth + 1)
            if found:
                return found
        return ""

    def parse_inbound(self, payload: dict[str, Any]) -> InboundMessage:
        raw_user = payload.get("user")
        user: dict[str, Any] = raw_user if isinstance(raw_user, dict) else {}
        event_raw = payload.get("event")
        event = event_raw if isinstance(event_raw, dict) else {}
        text_content = payload.get("textContent", {}) if isinstance(payload.get("textContent"), dict) else {}
        event_text_content = event.get("textContent", {}) if isinstance(event.get("textContent"), dict) else {}
        session = payload.get("session", {}) if isinstance(payload.get("session"), dict) else {}

        # 공식 웹훅은 `"user": "..."` 문자열(사용자 식별값)로 올 수 있음(chatbot-api README).
        user_id = self._pick_first_str(
            raw_user if isinstance(raw_user, str) else None,
            user.get("id"),
            user.get("userId"),
            user.get("uid"),
            payload.get("user_id"),
            payload.get("userId"),
            payload.get("senderId"),
            payload.get("sender_id"),
            payload.get("uid"),
            "anonymous",
        )
        postback = event.get("postback", {}) if isinstance(event.get("postback"), dict) else {}
        action = event.get("action", {}) if isinstance(event.get("action"), dict) else {}
        action_data = action.get("data", {}) if isinstance(action.get("data"), dict) else {}
        postback_data = postback.get("data", {}) if isinstance(postback.get("data"), dict) else {}
        text = self._pick_first_str(
            # event-level content first
            event_text_content.get("code"),
            event_text_content.get("text"),
            event.get("code"),
            event.get("text"),
            event.get("utterance"),
            event.get("message"),
            event.get("value"),
            event.get("payload"),
            event_raw if isinstance(event_raw, str) else None,
            # action/postback-style payloads
            action.get("code"),
            action.get("text"),
            action.get("label"),
            action.get("payload"),
            action.get("value"),
            action_data.get("code"),
            action_data.get("text"),
            action_data.get("label"),
            action_data.get("payload"),
            action_data.get("value"),
            postback.get("text"),
            postback.get("label"),
            postback.get("payload"),
            postback.get("code"),
            postback_data.get("code"),
            postback_data.get("text"),
            postback_data.get("label"),
            postback_data.get("payload"),
            postback_data.get("value"),
            # root-level text content
            event_text_content.get("code")
            or text_content.get("code"),
            text_content.get("text"),
            text_content.get("value"),
            # root-level fallback
            payload.get("text"),
            payload.get("message"),
            payload.get("utterance"),
            payload.get("code"),
            payload.get("value"),
            payload.get("postback"),
            payload.get("action"),
            # broad fallback for unexpected schema
            self._extract_text_from_nested(payload),
            "",
        )

        session_key = self._pick_first_str(
            session.get("id"),
            session.get("sessionId"),
            payload.get("session_id"),
            payload.get("sessionId"),
            payload.get("conversationId"),
            payload.get("conversation_id"),
            event.get("sessionId"),
            event.get("conversationId"),
            user_id,
        )
        return InboundMessage(
            user_id=user_id,
            message=text,
            session_key=session_key,
            channel=self.channel_name,
            raw=payload,
        )

    def build_outbound(self, result: dict[str, Any]) -> dict[str, Any]:
        quick = result.get("quick_replies", []) or []
        button_list = []
        quick_replies_legacy = []
        for item in quick:
            raw = str(item).strip()
            code = "1" if (("추천" in raw and "단계" in raw) or ("상담" in raw)) else raw[:1000]
            title = raw[:18] if len(raw) > 18 else raw
            button_list.append({"type": "TEXT", "data": {"title": title, "code": code}})
            quick_replies_legacy.append({"label": title, "text": code})

        text = str(result.get("text") or "").strip()
        if not text:
            text = "잠시 후 다시 시도해 주세요."

        text_content: dict[str, Any] = {"text": text}
        if button_list:
            text_content["quickReply"] = {"buttonList": button_list}

        # Naver webhook synchronous response schema.
        # 일부 콘솔/게이트웨이 변형을 고려해 text/quickReplies도 함께 제공한다.
        payload: dict[str, Any] = {"event": "send", "textContent": text_content, "text": text}
        if quick_replies_legacy:
            payload["quickReplies"] = quick_replies_legacy
        return payload

