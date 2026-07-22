#!/usr/bin/env python3
"""네이버 SR266: /n/1 → pilot (naver_sms). 상세 paste HTML 은 링크 없음."""

from __future__ import annotations

import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def main() -> int:
    from fastapi.testclient import TestClient

    from api import app
    from pilot_links import naver_pilot_path_for_code, naver_pilot_path_for_sku

    c = TestClient(app)

    r = c.get("/n/1", follow_redirects=False)
    assert r.status_code == 302, r.status_code
    loc = r.headers.get("location", "")
    assert "/pilot" in loc and "SR266" in loc and "naver_sms" in loc, loc

    assert naver_pilot_path_for_code("1") == naver_pilot_path_for_sku("SR266")

    r3 = c.get("/nv/NAVER_TEST_SKU", follow_redirects=False)
    assert r3.status_code == 302, r3.status_code
    assert "NAVER_TEST_SKU" in r3.headers.get("location", "")
    assert "naver_sms" in r3.headers.get("location", "")

    paste_path = os.path.join(_ROOT, "docs", "demo", "naver_SR266_detail_paste.html")
    with open(paste_path, encoding="utf-8") as f:
        paste = f.read()
    assert "/pilot" not in paste, "paste HTML must not embed pilot URL"
    assert "발볼 확인" in paste

    r2 = c.get("/n/1", follow_redirects=True)
    assert r2.status_code == 200, r2.status_code
    assert "pilot" in r2.text.lower() or "발볼" in r2.text

    base = (os.environ.get("SMOKE_BASE_URL") or "").strip()
    if base:
        import urllib.request

        url = base.rstrip("/") + "/n/1"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=90) as resp:
            final = resp.geturl()
            body = resp.read().decode("utf-8", errors="replace")
        assert "naver_sms" in final or "naver_sms" in body, final

    print("OK smoke_naver_detail_link")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
