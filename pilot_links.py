"""짧은 파일럿 진입 URL (/c/{sku}, /s/{code}) → /pilot 쿼리 리다이렉트."""

from __future__ import annotations

from urllib.parse import urlencode

# 문자용 초단축 코드 → SKU (예: /s/1)
PILOT_SHORT_CODE: dict[str, str] = {
    "1": "SR266",
    "266": "SR266",
}

# Wing 상품별: 문자·CS용 짧은 링크 (return_url은 itemId·vendorItemId만 유지)
PILOT_GO: dict[str, dict[str, str]] = {
    "SR266": {
        "product_id": "SR266",
        "src": "coupang_sms",
        "return_url": (
            "https://www.coupang.com/vp/products/6547505721"
            "?itemId=14603242244&vendorItemId=81845050827"
        ),
    },
}


def sku_from_short_code(code: str) -> str | None:
    raw = (code or "").strip()
    if not raw:
        return None
    if raw in PILOT_SHORT_CODE:
        return PILOT_SHORT_CODE[raw]
    low = raw.lower()
    if low in PILOT_SHORT_CODE:
        return PILOT_SHORT_CODE[low]
    key = raw.upper()
    if key in PILOT_GO:
        return key
    return None


def pilot_path_for_sku(sku: str) -> str | None:
    key = (sku or "").strip().upper()
    row = PILOT_GO.get(key)
    if not row:
        return None
    params: dict[str, str] = {
        "product_id": row["product_id"],
        "src": row.get("src") or "coupang_sms",
    }
    ret = (row.get("return_url") or "").strip()
    if ret:
        params["return_url"] = ret
    return f"/pilot?{urlencode(params)}"
