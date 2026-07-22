"""판매자 답변 생성기 스모크 테스트."""

from __future__ import annotations

import sys
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

from pilot_seller_reply import build_seller_reply, normalize_fit_line


def _dx(code: str, q4: int = 235) -> dict:
    return {
        "diagnosis_code": f"{code}-000001",
        "recommendation_code": code,
        "q4": q4,
        "product_id": "SR266",
        "r_code": "R2",
        "p_code": "P1",
        "s_code": "S0",
    }


def main() -> None:
    assert normalize_fit_line("아주편한핏") == "아주 편한핏"

    r1 = build_seller_reply(_dx("SF01"), seller_fit_line="편한핏")
    assert "1단계" in r1["reply_long"]
    assert "편한핏" in r1["reply_short"]
    assert r1["reply_exchange"]

    r2 = build_seller_reply(_dx("SF02"), seller_fit_line="기본핏", actual_work_step=2)
    assert "2단계" in r2["reply_long"]

    r3 = build_seller_reply(_dx("SF03"), seller_fit_line="아주 편한핏")
    assert "한 사이즈" in r3["reply_long"]
    assert r3["reply_exchange"] == ""

    r0 = build_seller_reply(_dx("SF00"), seller_fit_line="기본핏")
    assert "늘림 없이" in r0["reply_long"]

    try:
        build_seller_reply(_dx("SF01"), seller_fit_line="잘못된핏")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for bad fit line")

    print("test_pilot_seller_reply: ok")


if __name__ == "__main__":
    main()
