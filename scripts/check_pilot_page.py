"""Smoke: pilot HTML loads and script parses (node if available)."""
from __future__ import annotations

import re
import subprocess
import sys
import urllib.request

URL = "http://127.0.0.1:8001/pilot?src=naver&product_id=SR266"


def _fetch_html() -> str:
    try:
        return urllib.request.urlopen(URL, timeout=10).read().decode("utf-8")
    except OSError:
        import os

        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if root not in sys.path:
            sys.path.insert(0, root)
        from fastapi.testclient import TestClient

        from api import app

        r = TestClient(app).get("/pilot?src=naver&product_id=SR266")
        return r.text


def main() -> int:
    html = _fetch_html()
    if len(html) < 5000:
        print("FAIL: HTML too short", len(html))
        return 1
    if 'id="step"' not in html:
        print("FAIL: missing #step")
        return 1
    m = re.search(r"<script>(.*)</script>\s*</body>", html, re.DOTALL)
    if not m:
        print("FAIL: no script block")
        return 1
    js = m.group(1)
    with open("_pilot_check.js", "w", encoding="utf-8") as f:
        f.write(js)
    try:
        r = subprocess.run(
            ["node", "--check", "_pilot_check.js"],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except FileNotFoundError:
        print("OK: HTML len", len(html), "(node not installed, skip JS syntax)")
        return 0
    if r.returncode != 0:
        print("FAIL: JS syntax error")
        print(r.stderr)
        return 1
    print("OK: HTML + JS syntax")
    return 0


if __name__ == "__main__":
    sys.exit(main())
