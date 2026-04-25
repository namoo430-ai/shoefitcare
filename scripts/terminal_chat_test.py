from __future__ import annotations

"""
터미널에서 챗봇 대화를 직접 테스트하는 도구.

사용법:
1) 대화형(수동 입력)
   python scripts/terminal_chat_test.py

2) 시나리오형(자동 재생)
   python scripts/terminal_chat_test.py --script "1||사이즈 추천은 어떤 기준으로 해?||2"
"""

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from core.session import ConversationController, SessionStore


def _safe_out(text: str) -> str:
    enc = sys.stdout.encoding or "utf-8"
    return (text or "").encode(enc, errors="replace").decode(enc, errors="replace")


def _print_bot(resp: dict) -> None:
    print("\n[BOT]")
    print(_safe_out(resp.get("text", "")))
    quick = resp.get("quick_replies") or []
    if quick:
        print("[선택지]", " / ".join(quick))
    print("[state]", resp.get("state"), "| [done]", resp.get("done"))


def _run_script(ctrl: ConversationController, script: str) -> None:
    session = ctrl.new_session(channel="cli", customer_id="terminal_script_user")
    print("[INFO] session_id:", session.session_id)
    _print_bot(ctrl.get_initial_prompt())

    inputs = [x.strip() for x in script.split("||") if x.strip()]
    for idx, user_msg in enumerate(inputs, start=1):
        print(f"\n[USER {idx}] {user_msg}")
        resp = ctrl.handle_message(session, user_msg)
        _print_bot(resp)
        if resp.get("done"):
            break

    print("\n[PASS] script replay finished.")


def _run_interactive(ctrl: ConversationController) -> None:
    session = ctrl.new_session(channel="cli", customer_id="terminal_manual_user")
    print("[INFO] session_id:", session.session_id)
    _print_bot(ctrl.get_initial_prompt())
    print("\n입력을 계속하세요. 종료하려면 q 입력.")

    while True:
        user_msg = input("\n[YOU] ").strip()
        if not user_msg:
            continue
        if user_msg.lower() in ("q", "quit", "exit"):
            print("[INFO] 종료합니다.")
            return
        resp = ctrl.handle_message(session, user_msg)
        _print_bot(resp)
        if resp.get("done"):
            print("[INFO] 진단이 완료되어 세션을 종료합니다.")
            return


def main() -> None:
    parser = argparse.ArgumentParser(description="Terminal chatbot test runner")
    parser.add_argument(
        "--script",
        default="",
        help='자동 재생 입력. 예: "1||사이즈 추천은 어떤 기준으로 해?||2"',
    )
    args = parser.parse_args()

    store = SessionStore(store_dir="data/sessions_terminal_test")
    ctrl = ConversationController(store=store)

    if args.script:
        _run_script(ctrl, args.script)
    else:
        _run_interactive(ctrl)


if __name__ == "__main__":
    main()
