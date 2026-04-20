from __future__ import annotations

"""
오늘 체크용 로컬 E2E:
1) 신규 세션 시작
2) 기존 세션 메시지 처리
3) 빈 메시지(네이버 webhook fallback) 처리
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from core.session import ConversationController, SessionStore
from adapters.naver import NaverAdapter


def main() -> None:
    store = SessionStore()
    ctrl = ConversationController(store=store)
    nav = NaverAdapter()

    # 1) 신규 세션
    sess = ctrl.new_session(channel="naver", customer_id="e2e_user")
    sess.shop_id = "e2e_shop"
    sess.policy_version = "v1"
    intro = ctrl.get_initial_prompt()
    print("[OK] new_session:", sess.session_id, intro.get("state"))

    # 2) 기존 세션 메시지
    result = ctrl.handle_message(sess, "2")
    print("[OK] existing_session_message:", result.get("state"))

    # 3) 빈 메시지 payload 처리 (fallback)
    inbound = nav.parse_inbound(
        {
            "user": {"id": "e2e_user"},
            "session": {"id": sess.session_id},
            "event": {"utterance": ""},
            "shop_id": "e2e_shop",
            "policy_version": "v1",
        }
    )
    loaded = store.load(inbound.session_key)
    if loaded is None:
        raise RuntimeError("session load failed in empty-message flow")
    fallback = ctrl.get_initial_prompt()
    print("[OK] empty_message_fallback:", fallback.get("state"))


if __name__ == "__main__":
    main()

