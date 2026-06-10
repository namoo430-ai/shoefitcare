from __future__ import annotations

"""
데이터 보존/파기 운영 스크립트.

사용 예시:
1) 보존기간 기반 일괄 파기
   python scripts/data_retention_admin.py purge

2) 특정 세션 삭제 요청 처리
   python scripts/data_retention_admin.py delete-session --session-id <SESSION_ID>
"""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from core.storage import (
    init_db,
    delete_session_artifacts,
    purge_expired_data,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Shoefitcare retention/admin utilities")
    sub = parser.add_subparsers(dest="command", required=True)

    p_purge = sub.add_parser("purge", help="Purge expired rows/files by retention policy")
    p_purge.add_argument("--ops-days", type=int, default=None, help="Operational DB retention days")
    p_purge.add_argument("--learning-days", type=int, default=None, help="Learning RAG retention days")

    p_delete = sub.add_parser("delete-session", help="Delete one session artifacts")
    p_delete.add_argument("--session-id", required=True, help="Target session_id")

    args = parser.parse_args()
    init_db()

    if args.command == "purge":
        kwargs = {}
        if args.ops_days is not None:
            kwargs["retention_days_ops"] = args.ops_days
        if args.learning_days is not None:
            kwargs["retention_days_learning"] = args.learning_days
        result = purge_expired_data(**kwargs)
        print(json.dumps({"ok": True, "action": "purge", "result": result}, ensure_ascii=False, indent=2))
        return

    if args.command == "delete-session":
        result = delete_session_artifacts(session_id=args.session_id)
        print(json.dumps({"ok": True, "action": "delete-session", "result": result}, ensure_ascii=False, indent=2))
        return


if __name__ == "__main__":
    main()
