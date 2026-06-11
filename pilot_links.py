"""짧은 파일럿 진입 URL (/c/{sku}) → /pilot 쿼리 리다이렉트."""

from __future__ import annotations

from urllib.parse import urlencode

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
