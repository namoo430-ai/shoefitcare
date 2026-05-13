# -*- coding: utf-8 -*-
"""Round2: TC06~TC10 via POST /chat (same path as /demo). Run from repo root: python scripts/round2_chat_smoke_tc06_10.py"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from api import app  # noqa: E402

client = TestClient(app)


def post_chat(session_id: str | None, message: str) -> dict:
    r = client.post(
        "/chat",
        json={
            "session_id": session_id,
            "message": message,
            "channel": "web",
            "shop_id": "default_shop",
            "policy_version": "v1",
        },
    )
    assert r.status_code == 200, r.text
    return r.json()


def run_flow(messages: list[str]) -> dict:
    first = post_chat(None, "시작")
    sid = first["session_id"]
    last = first
    for m in messages:
        last = post_chat(sid, m)
    return last


def count_top3_lines(text: str) -> int:
    return len(re.findall(r"^\s*-\s*[123]\)\s", text, re.MULTILINE))


CASES: list[tuple[str, list[str], dict]] = [
    (
        "TC06",
        [
            "2",
            "아니요",
            "넓음",
            "1",
            "로퍼",
            "240",
            "편한핏",
            "잘 맞아요",
        ],
        {"fit": "편한핏", "size": 240, "stretch": 0, "top3_lines": 3},
    ),
    (
        "TC07",
        [
            "2",
            "아니요",
            "통통함",
            "운동화",
            "245",
            "아주 편한핏",
            "잘 맞아요",
        ],
        {"fit": "아주 편한핏", "size": 245, "stretch": 0, "top3_lines": 3},
    ),
    (
        "TC08",
        [
            "2",
            "아니요",
            "넓음",
            "1",
            "구두",
            "240",
            "편한핏",
            "볼이 꽉 껴서 불편해요",
            "신어본 적 없음",
        ],
        {"fit": "편한핏", "size": 240, "stretch": 1, "top3_lines": 3},
    ),
    (
        "TC09",
        [
            "2",
            "아니요",
            "넓음",
            "2",
            "구두",
            "240",
            "기본핏",
            "볼이 꽉 껴서 불편해요",
            "아니요",
        ],
        {"fit": "편한핏", "size": 240, "stretch": 1, "top3_lines": 3},
    ),
    (
        "TC10",
        [
            "2",
            "아니요",
            "넓음,무지외반",
            "2,1",
            "구두",
            "240",
            "기본핏",
            "볼이 꽉 껴서 불편해요",
            "아니요",
        ],
        {"fit": "편한핏", "size": 245, "stretch": 0, "top3_lines": 3},
    ),
]


def main() -> int:
    failed: list[str] = []
    for tid, msgs, want in CASES:
        out = run_flow(msgs)
        diag = out.get("diagnosis") or {}
        fit = diag.get("recommended_fit")
        size = diag.get("final_size")
        stretch = diag.get("stretch_step")
        text = out.get("text") or ""
        nlines = count_top3_lines(text)
        ok = (
            fit == want["fit"]
            and size == want["size"]
            and stretch == want["stretch"]
            and nlines == want["top3_lines"]
            and out.get("done") is True
        )
        if not ok:
            failed.append(
                f"{tid}: want {want} got fit={fit!r} size={size!r} "
                f"stretch={stretch!r} top3_lines={nlines} done={out.get('done')!r}"
            )
        top3 = diag.get("top3_recommendations") or []
        t_ok = (
            len(top3) >= 3
            and all(
                x.get("fit") == want["fit"] and x.get("size_mm") == want["size"]
                for x in top3[:3]
            )
        )
        if not t_ok:
            failed.append(f"{tid}: top3 mismatch {top3[:3]!r}")

    if failed:
        print("FAIL")
        for line in failed:
            print(line)
        return 1
    print("OK TC06-TC10 /chat flow + diagnosis + TOP3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
