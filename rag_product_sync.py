from __future__ import annotations

import csv
import json
import os
from datetime import datetime
from pathlib import Path


ACTIVE_STATUSES = {"판매중", "on_sale", "active"}
_PROJECT_ROOT = Path(__file__).resolve().parent


def sync_product_rag_docs(
    csv_dir: str | None = None,
    rag_dir: str | None = None,
    doc_version: str | None = None,
) -> dict:
    """
    상품 CSV를 RAG 상품 문서로 동기화한다.
    - source CSV: products/product_fit_specs/product_tags
    - target docs: data/rag_docs/products/product_<id>.json
    """
    csv_base = Path(csv_dir) if csv_dir else (_PROJECT_ROOT / "csv_templates")
    rag_base = Path(rag_dir) if rag_dir else (_PROJECT_ROOT / "data" / "rag_docs")
    products_path = csv_base / "products.csv"
    specs_path = csv_base / "product_fit_specs.csv"
    tags_path = csv_base / "product_tags.csv"
    for required in (products_path, specs_path, tags_path):
        if not required.exists():
            raise FileNotFoundError(f"missing source csv: {required}")

    version = (doc_version or os.environ.get("RAG_PRODUCT_DOC_VERSION", "v1")).strip() or "v1"
    source_updated_at = _latest_iso_mtime([products_path, specs_path, tags_path])
    now_iso = datetime.now().isoformat()

    products = _read_csv(products_path)
    specs = _read_csv(specs_path)
    tags = _read_csv(tags_path)
    specs_map = _group_by(specs, "product_id")
    tags_map = _group_by(tags, "product_id")

    out_dir = rag_base / "products"
    out_dir.mkdir(parents=True, exist_ok=True)
    existing_ids = _existing_product_ids(out_dir)
    source_ids: set[str] = set()

    created = 0
    updated = 0
    unchanged = 0
    inactive = 0

    for product in products:
        pid = str((product.get("product_id") or "")).strip()
        if not pid:
            continue
        source_ids.add(pid)
        status = str((product.get("status") or "")).strip()
        is_active = status in ACTIVE_STATUSES
        if not is_active:
            inactive += 1

        doc = _build_product_doc(
            product=product,
            spec_rows=specs_map.get(pid, []),
            tag_rows=tags_map.get(pid, []),
            doc_version=version,
            source_updated_at=source_updated_at,
            synced_at=now_iso,
            is_active=is_active,
        )
        out_path = out_dir / f"product_{pid}.json"
        if not out_path.exists():
            _write_json(out_path, doc)
            created += 1
            continue
        old = _read_json(out_path)
        if old == doc:
            unchanged += 1
            continue
        _write_json(out_path, doc)
        updated += 1

    deleted = 0
    for stale_pid in sorted(existing_ids - source_ids):
        stale_path = out_dir / f"product_{stale_pid}.json"
        if stale_path.exists():
            stale_path.unlink()
            deleted += 1

    manifest = {
        "doc_type": "product_sync_manifest",
        "doc_version": version,
        "source_updated_at": source_updated_at,
        "synced_at": now_iso,
        "source_count": len(source_ids),
        "created": created,
        "updated": updated,
        "unchanged": unchanged,
        "deleted": deleted,
        "inactive_products": inactive,
    }
    _write_json(out_dir / "_sync_manifest.json", manifest)
    return manifest


def _build_product_doc(
    product: dict,
    spec_rows: list[dict],
    tag_rows: list[dict],
    doc_version: str,
    source_updated_at: str,
    synced_at: str,
    is_active: bool,
) -> dict:
    pid = str((product.get("product_id") or "")).strip()
    name = str((product.get("name") or "")).strip()
    category = str((product.get("category") or "")).strip()
    brand = str((product.get("brand") or "")).strip()
    price = str((product.get("price") or "")).strip()
    status = str((product.get("status") or "")).strip()
    sizes = sorted({str((r.get("size_mm") or "")).strip() for r in spec_rows if str((r.get("size_mm") or "")).strip()})
    fits = sorted({str((r.get("fit_line") or "")).strip() for r in spec_rows if str((r.get("fit_line") or "")).strip()})
    widths = sorted({str((r.get("width_code") or "")).strip() for r in spec_rows if str((r.get("width_code") or "")).strip()})
    tag_values = sorted({str((r.get("tag_value") or "")).strip() for r in tag_rows if str((r.get("tag_value") or "")).strip()})
    searchable = "\n".join(
        [
            f"상품명: {name}",
            f"카테고리: {category}",
            f"브랜드: {brand}",
            f"가격: {price}",
            f"판매상태: {status}",
            f"사이즈(mm): {', '.join(sizes) if sizes else '정보 없음'}",
            f"핏 라인: {', '.join(fits) if fits else '정보 없음'}",
            f"폭 코드: {', '.join(widths) if widths else '정보 없음'}",
            f"태그: {', '.join(tag_values) if tag_values else '정보 없음'}",
            f"검색 포함 여부: {'포함' if is_active else '제외'}",
        ]
    )
    return {
        "doc_id": f"product:{pid}",
        "doc_type": "product_knowledge",
        "doc_version": doc_version,
        "source_updated_at": source_updated_at,
        "synced_at": synced_at,
        "searchable_text": searchable,
        "metadata": {
            "product_id": pid,
            "name": name,
            "category": category,
            "brand": brand,
            "price": price,
            "status": status,
            "product_url": str((product.get("product_url") or "")).strip(),
            "image_url": str((product.get("image_url") or "")).strip(),
            "is_active": is_active,
            "search_excluded": not is_active,
            "size_options_mm": sizes,
            "fit_options": fits,
            "width_codes": widths,
            "tag_values": tag_values,
        },
    }


def _latest_iso_mtime(paths: list[Path]) -> str:
    latest = 0.0
    for p in paths:
        latest = max(latest, p.stat().st_mtime)
    return datetime.fromtimestamp(latest).isoformat()


def _read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _group_by(rows: list[dict], key: str) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for row in rows:
        k = str((row.get(key) or "")).strip()
        if not k:
            continue
        out.setdefault(k, []).append(row)
    return out


def _existing_product_ids(directory: Path) -> set[str]:
    ids: set[str] = set()
    if not directory.exists():
        return ids
    for p in directory.glob("product_*.json"):
        name = p.stem
        if name.startswith("product_"):
            ids.add(name.replace("product_", "", 1))
    return ids


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
