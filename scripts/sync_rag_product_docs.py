from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from rag_product_sync import sync_product_rag_docs


def main() -> None:
    os.chdir(ROOT)
    result = sync_product_rag_docs()
    print(json.dumps({"ok": True, "action": "sync_rag_product_docs", "result": result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
