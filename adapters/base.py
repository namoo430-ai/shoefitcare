from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class InboundMessage:
    user_id: str
    message: str
    session_key: str
    channel: str
    raw: dict[str, Any]


class ChannelAdapter:
    """Provider payload <-> internal payload conversion contract."""

    channel_name = "unknown"

    def parse_inbound(self, payload: dict[str, Any]) -> InboundMessage:
        raise NotImplementedError

    def build_outbound(self, result: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

