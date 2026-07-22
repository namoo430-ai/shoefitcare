"""짧은 파일럿 진입 URL (/c/{sku}, /s/{code}, /n/{code}, /nv/{sku}) → /pilot 리다이렉트."""

from __future__ import annotations

import json
import os
import re
from functools import lru_cache
from urllib.parse import urlencode

_ROOT = os.path.dirname(os.path.abspath(__file__))
_NAVER_PRODUCTS_JSON = os.path.join(_ROOT, "config", "naver_pilot_products.json")

# 문자용 초단축 코드 → SKU (쿠팡, 예: /s/1)
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

_PRODUCT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")


def is_valid_product_id(raw: str) -> bool:
    s = (raw or "").strip()
    return bool(s and _PRODUCT_ID_RE.match(s))


@lru_cache(maxsize=1)
def _naver_products_config() -> dict:
    if not os.path.isfile(_NAVER_PRODUCTS_JSON):
        return {"default_src": "naver_sms", "products": {}}
    with open(_NAVER_PRODUCTS_JSON, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        return {"default_src": "naver_sms", "products": {}}
    products = data.get("products")
    if not isinstance(products, dict):
        data["products"] = {}
    return data


def naver_default_src() -> str:
    return (_naver_products_config().get("default_src") or "naver_sms").strip()[:32]


def naver_pilot_registry() -> dict[str, dict]:
    """등록 상품 (return_url·짧은코드). 키 = 대문자 product_id."""
    out: dict[str, dict] = {}
    for key, row in (_naver_products_config().get("products") or {}).items():
        if not isinstance(row, dict):
            continue
        pid = (row.get("product_id") or key or "").strip().upper()
        if not is_valid_product_id(pid):
            continue
        out[pid] = {
            "product_id": pid,
            "return_url": (row.get("return_url") or "").strip(),
            "short_codes": list(row.get("short_codes") or []),
            "memo": (row.get("memo") or "").strip(),
            "display_name": (row.get("display_name") or "").strip(),
            "stretch_on_option": bool(row.get("stretch_on_option")),
            "stretch_option_label": (row.get("stretch_option_label") or "발볼 늘림").strip(),
            "exchange_event_active": row.get("exchange_event_active", True) is not False,
        }
    return out


def naver_product_ops(product_id: str | None) -> dict[str, object]:
    """SKU별 늘림 옵션·교환 이벤트 (미등록 SKU는 기본값)."""
    key = (product_id or "").strip().upper()
    defaults: dict[str, object] = {
        "product_id": key or None,
        "display_name": "",
        "stretch_on_option": False,
        "stretch_option_label": "발볼 늘림",
        "exchange_event_active": True,
    }
    if not key:
        return defaults
    reg = naver_pilot_registry().get(key)
    if not reg:
        return {**defaults, "product_id": key}
    return {
        "product_id": key,
        "display_name": reg.get("display_name") or "",
        "stretch_on_option": bool(reg.get("stretch_on_option")),
        "stretch_option_label": reg.get("stretch_option_label") or "발볼 늘림",
        "exchange_event_active": reg.get("exchange_event_active", True) is not False,
    }


def naver_sms_short_code_map() -> dict[str, str]:
    """짧은 코드 → product_id (JSON short_codes)."""
    m: dict[str, str] = {}
    for pid, row in naver_pilot_registry().items():
        for code in row.get("short_codes") or []:
            c = str(code).strip()
            if c:
                m[c] = pid
                m[c.lower()] = pid
    return m


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


def product_detail_path_for_sku(sku: str, *, src: str = "naver") -> str | None:
    key = (sku or "").strip().upper()
    if not is_valid_product_id(key):
        return None
    params = {"product_id": key, "src": (src or "naver").strip()[:32]}
    return f"/product-detail?{urlencode(params)}"


def naver_sku_from_short_code(code: str) -> str | None:
    raw = (code or "").strip()
    if not raw:
        return None
    short = naver_sms_short_code_map()
    if raw in short:
        return short[raw]
    low = raw.lower()
    if low in short:
        return short[low]
    key = raw.upper()
    if key in naver_pilot_registry():
        return key
    if is_valid_product_id(key):
        return key
    return None


def naver_pilot_path_for_sku(sku: str) -> str | None:
    key = (sku or "").strip().upper()
    if not is_valid_product_id(key):
        return None
    reg = naver_pilot_registry().get(key)
    src = naver_default_src()
    return_url = ""
    product_id = key
    if reg:
        product_id = reg.get("product_id") or key
        return_url = (reg.get("return_url") or "").strip()
    params: dict[str, str] = {
        "product_id": product_id,
        "src": src,
    }
    if return_url:
        params["return_url"] = return_url
    return f"/pilot?{urlencode(params)}"


def naver_pilot_path_for_code(code: str) -> str | None:
    sku = naver_sku_from_short_code(code)
    if not sku:
        return None
    return naver_pilot_path_for_sku(sku)


def naver_detail_path_for_code(code: str) -> str | None:
    sku = naver_sku_from_short_code(code)
    if not sku:
        return None
    return product_detail_path_for_sku(sku, src="naver")


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


def reload_naver_pilot_config() -> None:
    _naver_products_config.cache_clear()
