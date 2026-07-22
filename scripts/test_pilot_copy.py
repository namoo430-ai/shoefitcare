"""pilot_copy.ko.json 로드·engine_keys 검증."""

from __future__ import annotations

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

from pilot_copy import load_pilot_copy, validate_pilot_copy


def main() -> None:
    copy = load_pilot_copy()
    validate_pilot_copy(copy)
    assert copy["intro"]["title"]
    assert len(copy["steps"]) == 4
    print("test_pilot_copy: ok")


if __name__ == "__main__":
    main()
