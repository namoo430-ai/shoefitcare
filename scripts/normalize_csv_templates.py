from __future__ import annotations

"""
csv_templates 데이터 정규화 도구.

기본은 dry-run이며, --apply를 주면 파일에 반영합니다.
"""

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CSV_DIR = ROOT / "csv_templates"


def _read_rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def _write_rows(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _normalize_fit_specs(rows: list[dict]) -> tuple[list[dict], int]:
    changed = 0
    out: list[dict] = []
    for row in rows:
        new_row = dict(row)
        fit_line = (new_row.get("fit_line") or "").strip()
        color = (new_row.get("color") or "").strip()
        age_group = (new_row.get("age_group") or "").strip()

        if fit_line == "아주편한핏":
            new_row["fit_line"] = "아주 편한핏"
        else:
            new_row["fit_line"] = fit_line

        # 색상+연령대 혼합값 분리 보정 (예: 브라운40-50, 베이지60-70)
        for suffix in ("40-50", "60-70", "80대이상"):
            if color.endswith(suffix) and color != suffix:
                new_row["color"] = color[: -len(suffix)].strip()
                if not age_group:
                    new_row["age_group"] = suffix
                break

        if new_row != row:
            changed += 1
        out.append(new_row)
    return out, changed


def _normalize_tags(rows: list[dict]) -> tuple[list[dict], int]:
    changed = 0
    out: list[dict] = []
    for row in rows:
        new_row = dict(row)
        tag_type = (new_row.get("tag_type") or "").strip()
        tag_value = (new_row.get("tag_value") or "").strip()

        if tag_type == "궆높이":
            new_row["tag_type"] = "굽높이"
        else:
            new_row["tag_type"] = tag_type

        if tag_value == "무외외반_우호":
            new_row["tag_value"] = "무지외반_우호"
        else:
            new_row["tag_value"] = tag_value

        # 빈 태그값 행은 제거
        if not (new_row.get("tag_value") or "").strip():
            changed += 1
            continue

        if new_row != row:
            changed += 1
        out.append(new_row)
    return out, changed


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize csv_templates data.")
    parser.add_argument("--apply", action="store_true", help="Write changes to files.")
    args = parser.parse_args()

    fit_path = CSV_DIR / "product_fit_specs.csv"
    tags_path = CSV_DIR / "product_tags.csv"

    fit_rows = _read_rows(fit_path)
    tags_rows = _read_rows(tags_path)

    norm_fit, fit_changed = _normalize_fit_specs(fit_rows)
    norm_tags, tags_changed = _normalize_tags(tags_rows)

    print(f"[CHECK] product_fit_specs.csv changes: {fit_changed}")
    print(f"[CHECK] product_tags.csv changes: {tags_changed}")

    if not args.apply:
        print("[INFO] dry-run complete. Use --apply to write changes.")
        return

    if fit_rows:
        _write_rows(fit_path, list(fit_rows[0].keys()), norm_fit)
    if tags_rows:
        _write_rows(tags_path, list(tags_rows[0].keys()), norm_tags)
    print("[OK] normalization applied.")


if __name__ == "__main__":
    main()
