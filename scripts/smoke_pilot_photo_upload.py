"""정밀 접수 + 사진 업로드 스모크 (로컬 API)."""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8001"

# minimal valid JPEG ( > 32 bytes for server check)
JPEG = (
    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
    + b"\xff\xdb\x00C\x00"
    + b"\x08" * 64
    + b"\xff\xd9"
)


def post_json(path: str, body: dict) -> dict:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        BASE + path,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.loads(res.read().decode())


def post_multipart(path: str, fields: dict, file_field: str, filename: str, content: bytes, mime: str) -> dict:
    boundary = "----SmokeBoundary7MA4YWxk"
    parts: list[bytes] = []
    for key, val in fields.items():
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode())
        parts.append(f"{val}\r\n".encode())
    parts.append(f"--{boundary}\r\n".encode())
    parts.append(
        f'Content-Disposition: form-data; name="{file_field}"; filename="{filename}"\r\n'.encode()
    )
    parts.append(f"Content-Type: {mime}\r\n\r\n".encode())
    parts.append(content)
    parts.append(f"\r\n--{boundary}--\r\n".encode())
    body = b"".join(parts)
    req = urllib.request.Request(
        BASE + path,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.loads(res.read().decode())


def main() -> int:
    print("base:", BASE)
    dx = post_json(
        "/pilot/diagnose",
        {
            "q1": "길이는 맞는데 발볼이 조이는 편이에요",
            "q2": ["발볼 부분"],
            "q3": "매우 불편해요",
            "q4": 235,
            "product_id": "SR266",
            "channel": "html_detail",
        },
    )
    if dx.get("error"):
        print("diagnose failed:", dx)
        return 1
    dx_id = dx["id"]
    print("diagnosis:", dx.get("diagnosis_code"), "precision_recommended:", dx.get("precision_recommended"))

    prec = post_json(
        "/pilot/precision",
        {
            "diagnosis_id": dx_id,
            "left_length_cm": 25.0,
            "right_length_cm": 25.2,
            "left_width_cm": 9.5,
            "right_width_cm": 9.6,
            "contact": "01012345678",
            "consent": True,
        },
    )
    if prec.get("error"):
        print("precision failed:", prec)
        return 1
    print("precision ok:", prec.get("recommendation_code"))

    up = post_multipart(
        "/pilot/precision-photo",
        {"diagnosis_id": dx_id},
        "photo",
        "foot.jpg",
        JPEG,
        "image/jpeg",
    )
    if up.get("error") or not up.get("ok"):
        print("photo upload failed:", up)
        return 1
    print("photo upload ok:", up.get("photo_uploaded_at"))

    health = urllib.request.urlopen(BASE + "/health/build", timeout=10)
    print("health/build:", health.read().decode())
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except urllib.error.URLError as e:
        print("API not reachable:", e)
        raise SystemExit(2)
