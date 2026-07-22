"""네이버 스토어팜 카테고리·톡톡 링크 (config)."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Any

_ROOT = os.path.dirname(os.path.abspath(__file__))
_LINKS_JSON = os.path.join(_ROOT, "config", "naver_pilot_store_links.json")

FIT_LINE_KEYS = ("기본핏", "편한핏", "아주 편한핏")


@lru_cache(maxsize=1)
def _load_raw() -> dict[str, Any]:
    if not os.path.isfile(_LINKS_JSON):
        return {}
    with open(_LINKS_JSON, encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, dict) else {}


def reload_store_links_config() -> None:
    _load_raw.cache_clear()


def naver_store_links() -> dict[str, Any]:
    raw = _load_raw()
    cats_in = raw.get("fit_category_urls") or {}
    cats: dict[str, str] = {}
    if isinstance(cats_in, dict):
        for key in FIT_LINE_KEYS:
            cats[key] = (cats_in.get(key) or "").strip()
    talk = (raw.get("talktalk_url") or "").strip()
    return {
        "talktalk_url": talk,
        "fit_category_urls": cats,
        "has_talktalk": bool(talk),
        "has_fit_categories": any(cats.values()),
    }
