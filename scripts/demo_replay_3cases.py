from __future__ import annotations

"""
발표용 데모 리플레이 3시나리오:
1) 잘 맞음(기성화기본)
2) 헐떡임(다운사이즈 보정)
3) 꽉낌(적용점수 기반 분기)
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from core.session import ConversationController, SessionStore


SCENARIOS = [
    {
        "name": "A_잘맞음",
        "inputs": ["2", "2", "1", "240", "1", "1"],
    },
    {
        "name": "B_헐떡임",
        "inputs": ["2", "3", "1", "2", "245", "2", "2"],
    },
    {
        "name": "C_꽉낌",
        "inputs": ["2", "3,4", "2,1", "1", "245", "2", "3"],
    },
]


def run_one(ctrl: ConversationController, scenario: dict) -> None:
    sess = ctrl.new_session(channel="demo", customer_id=scenario["name"])
    print(_safe_text(f"\n=== {scenario['name']} ==="))
    intro = ctrl.get_initial_prompt()
    print("[BOT]", _safe_text(intro["text"].split("\n")[0]))
    for user_input in scenario["inputs"]:
        result = ctrl.handle_message(sess, user_input)
        print("[USR]", user_input)
        print("[BOT]", _safe_text(result["text"].split("\n")[0]))
        if result.get("done"):
            print("[DONE] session_id=", sess.session_id)
            break


def _safe_text(text: str) -> str:
    return text.encode("cp949", errors="replace").decode("cp949", errors="replace")


def main() -> None:
    ctrl = ConversationController(store=SessionStore())
    for scenario in SCENARIOS:
        run_one(ctrl, scenario)


if __name__ == "__main__":
    main()

