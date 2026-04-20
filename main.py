"""
슈핏케어 메인 실행 (main.py)
=============================
현재: CLI 실행
전환 가능: FastAPI / 카카오 챗봇 / Slack 앱 — ConversationController만 재사용
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from core.session import ConversationController, SessionStore, SessionState
from core.storage import init_db, get_return_rate_report


def run_cli():
    """CLI 인터페이스 — 챗봇 전환 시 이 함수만 교체"""
    ctrl = ConversationController()
    session = ctrl.new_session(channel="cli")

    print("\n" + "=" * 60)
    # 시작 안내
    intro = ctrl.get_initial_prompt()
    print(intro["text"])
    print()

    while not session.is_complete():
        quick = intro.get("quick_replies", [])
        if quick:
            print(f"  선택지: {' / '.join(quick)}")

        user_input = input("입력 → ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("q", "quit", "exit"):
            print("진단을 종료합니다.")
            break

        intro = ctrl.handle_message(session, user_input)
        print()
        print(intro["text"])
        print()

    print("=" * 60)
    print(f"세션 ID: {session.session_id}")
    print("진단 데이터가 저장되었습니다.")

    # 반품 피드백 데모 (실제: 주문 완료 후 별도 수집)
    demo_feedback = input("\n[데모] 만족하셨나요? (y/n): ").strip().lower()
    if demo_feedback in ("y", "n"):
        from core.storage import save_return_feedback, update_rag_return_status
        returned = demo_feedback == "n"
        reason = ""
        if returned:
            reason = input("반품 이유: ").strip()
        save_return_feedback(session.session_id, returned, reason)
        update_rag_return_status(session.session_id, returned, reason)
        print("피드백이 저장되었습니다. 반품율 추적에 활용됩니다.")


def run_report():
    """반품율 리포트 출력"""
    init_db()
    report = get_return_rate_report()
    print("\n📊 슈핏케어 반품율 리포트")
    print("=" * 40)
    print(f"총 진단 수       : {report['total_diagnoses']}건")
    print(f"피드백 수집      : {report['feedback_collected']}건")
    print(f"전체 반품율      : {report['overall_return_rate']}")
    print()
    if report["by_design"]:
        print("디자인별 반품율:")
        for k, v in report["by_design"].items():
            print(f"  {k}: {v['return_rate']}% ({v['count']}건)")
    if report["by_stretch_step"]:
        print("\n가공 단계별 반품율:")
        for k, v in report["by_stretch_step"].items():
            print(f"  {k}: {v['return_rate']}% ({v['count']}건)")


if __name__ == "__main__":
    init_db()
    if "--report" in sys.argv:
        run_report()
    else:
        run_cli()
