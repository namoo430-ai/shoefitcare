#!/usr/bin/env python3
"""내일 네이버 파일럿 테스트 전 원클릭 점검 (로컬)."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import urllib.request

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

BASE = (os.environ.get("SMOKE_BASE_URL") or "http://127.0.0.1:8001").rstrip("/")
PORT = 8001


def _lan_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


def _run(cmd: list[str], label: str) -> bool:
    print(f"... {label}")
    r = subprocess.run(cmd, cwd=_ROOT)
    if r.returncode != 0:
        print(f"FAIL: {label} (exit {r.returncode})")
        return False
    print(f"OK  {label}")
    return True


def _http_json(path: str) -> dict | None:
    try:
        raw = urllib.request.urlopen(f"{BASE}{path}", timeout=8).read()
        import json

        return json.loads(raw)
    except OSError as e:
        print(f"FAIL: {BASE}{path} - {e}")
        return None


def main() -> int:
    print("=== 네이버 파일럿 테스트 전 점검 ===\n")
    ok = True
    ok &= _run(
        [sys.executable, "-m", "py_compile", "api.py", "pilot_ui.py", "pilot_storage.py"],
        "py_compile",
    )
    for script in (
        "check_pilot_page.py",
        "smoke_naver_detail_link.py",
        "test_pilot_fit_result.py",
        "test_pilot_seller_reply.py",
    ):
        ok &= _run([sys.executable, os.path.join("scripts", script)], script)

    h = _http_json("/health/build")
    if not h:
        print(
            f"\n서버가 안 떠 있습니다. 터미널에서:\n"
            f"  uvicorn api:app --reload --port {PORT}\n"
        )
        return 1
    build = h.get("pilot_build", "?")
    print(f"\n서버: {BASE}")
    print(f"pilot_build: {build}")
    if "js-syntax" not in str(build) and "submit-fix" not in str(build):
        print("WARN: pilot_build가 최근 수정(b3)이 아닐 수 있습니다. uvicorn 재시작·강력 새로고침.")

    sl = _http_json("/api/pilot/store-links")
    if sl:
        talk = sl.get("talktalk_url") or "(없음)"
        print(f"TalkTalk: {talk}")
        if not sl.get("has_talktalk"):
            print("WARN: talktalk_url 비어 있음 → 톡톡 시트 '열기' 비활성")
        if not sl.get("has_fit_categories"):
            print("INFO: 핏별상품 URL 미설정 → 하단 '핏별상품' 탭 비활성 (테스트 가능)")

    ip = _lan_ip()
    print("\n--- 내일 휴대폰 테스트 URL (같은 Wi-Fi, PC 방화벽 8001 허용) ---")
    print(f"  http://{ip}:{PORT}/n/1")
    print(f"  http://{ip}:{PORT}/pilot?src=naver&product_id=SR266")
    print("\n--- Render(배포) CS 링크 ---")
    print("  https://shoefitcare-chatbot.onrender.com/n/1")
    print("\n체크리스트: docs/runbooks/naver/NAVER_TEST_DAY.md")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
