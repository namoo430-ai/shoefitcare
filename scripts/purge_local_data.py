from __future__ import annotations

"""
로컬 민감 데이터 정리 스크립트.
- data/ 하위 세션/로그/DB/RAG를 삭제
- 코드/설정 파일은 유지
"""

import os
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


def _safe_remove(path: Path) -> None:
    if not path.exists():
        return
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    else:
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def main() -> None:
    targets = [
        DATA_DIR / "sessions",
        DATA_DIR / "rag_docs",
        DATA_DIR / "logs",
        DATA_DIR / "shoefitcare.db",
    ]
    for target in targets:
        _safe_remove(target)
        print(f"[PURGED] {target}")
    (DATA_DIR / ".gitkeep").parent.mkdir(parents=True, exist_ok=True)
    print("[DONE] local sensitive data purged")


if __name__ == "__main__":
    main()

