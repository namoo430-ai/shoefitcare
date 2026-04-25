from __future__ import annotations

"""
/chat 엔드포인트 로컬 스모크 테스트 (웹훅 제외).
"""

import argparse
import json
import sys
import urllib.error
import urllib.request


def _post_json(base_url: str, path: str, payload: dict) -> dict:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url=f"{base_url}{path}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _check_server(base_url: str) -> None:
    try:
        with urllib.request.urlopen(f"{base_url}/docs", timeout=5) as resp:
            if int(getattr(resp, "status", 0)) != 200:
                raise RuntimeError("docs status not 200")
    except Exception as exc:
        raise RuntimeError("API not reachable. Run: uvicorn api:app --reload") from exc


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")

    _check_server(base_url)
    print("[OK] API reachable:", base_url)

    r1 = _post_json(base_url, "/chat", {
        "session_id": None,
        "message": "시작",
        "channel": "web",
        "customer_id": "http_smoke_user",
        "shop_id": "default_shop",
        "policy_version": "v1",
    })
    sid = r1.get("session_id")
    if not sid:
        raise RuntimeError("session_id not returned")
    print("[OK] session created:", sid)
    print("[OK] start state:", r1.get("state"))

    r2 = _post_json(base_url, "/chat", {
        "session_id": sid, "message": "상품부터 고를게요", "channel": "web",
        "customer_id": "http_smoke_user", "shop_id": "default_shop", "policy_version": "v1",
    })
    print("[OK] after entry:", r2.get("state"))

    r3 = _post_json(base_url, "/chat", {
        "session_id": sid, "message": "사이즈 추천은 어떤 기준으로 해?", "channel": "web",
        "customer_id": "http_smoke_user", "shop_id": "default_shop", "policy_version": "v1",
    })
    print("[OK] drift state:", r3.get("state"), "done:", r3.get("done"))

    r4 = _post_json(base_url, "/chat", {
        "session_id": sid, "message": "로퍼", "channel": "web",
        "customer_id": "http_smoke_user", "shop_id": "default_shop", "policy_version": "v1",
    })
    print("[OK] recover state:", r4.get("state"), "done:", r4.get("done"))
    print("[PASS] Local /chat HTTP smoke test completed.")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as e:
        print(f"[FAIL] HTTPError {e.code}: {e.reason}")
        sys.exit(1)
    except Exception as e:
        print("[FAIL]", e)
        sys.exit(1)
