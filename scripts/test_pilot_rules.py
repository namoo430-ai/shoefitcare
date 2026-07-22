"""파일럿 룰 엔진 스모크 테스트."""



from __future__ import annotations



import sys

from pathlib import Path



_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(_ROOT))



from pilot_engine import (

    Q1_INSTEP,

    Q1_LOOSE,

    Q1_SLIP,

    Q1_NONE,

    Q1_TIGHT,

    Q2_BALL,

    Q2_HALLUX,

    Q2_INSTEP,

    Q2_NONE,

    Q3_MID,

    Q3_NONE,

    Q3_SEVERE,

    Q3_SLIGHT,

    Q5_LOOSE,

    PilotInput,

    evaluate,

)





def _run(inp: PilotInput, expect: str) -> None:

    got = evaluate(inp).recommendation_code

    assert got == expect, f"expected {expect}, got {got} for {inp}"


def _run_msg(inp: PilotInput, expect: str, *needles: str) -> None:
    res = evaluate(inp)
    assert res.recommendation_code == expect, f"expected {expect}, got {res.recommendation_code}"
    for n in needles:
        assert n in res.message, f"missing {n!r} in message: {res.message[:120]}..."





def main() -> None:

    _run(

        PilotInput(Q1_TIGHT, [Q2_BALL], Q3_NONE, 235, ""),

        "SF00",

    )

    _run(

        PilotInput(Q1_TIGHT, [Q2_HALLUX], Q3_SEVERE, 235, ""),

        "SF03",

    )

    _run(

        PilotInput(Q1_TIGHT, [Q2_BALL], Q3_SEVERE, 235, ""),

        "SF02",

    )

    _run(

        PilotInput(Q1_SLIP, [], Q3_MID, 240, ""),

        "SF01",

    )

    _run_msg(

        PilotInput(Q1_SLIP, [], Q3_MID, 240, ""),

        "SF01",

        "헐떡임 대응",

        "235mm",

        "발볼 늘림 1단계",

    )

    _run(

        PilotInput(Q1_SLIP, [Q2_BALL], Q3_SEVERE, 235, ""),

        "SF02",

    )

    _run_msg(

        PilotInput(Q1_SLIP, [Q2_BALL], Q3_SEVERE, 235, ""),

        "SF02",

        "헐떡임 대응",

        "230mm",

        "발볼 늘림 2단계",

    )

    _run(

        PilotInput(Q1_TIGHT, [], Q3_SLIGHT, 235, ""),

        "SF01",

    )

    res_tight = evaluate(PilotInput(Q1_TIGHT, [], Q3_SLIGHT, 235, ""))

    assert "헐떡임 대응" not in res_tight.message

    _run(

        PilotInput(Q1_TIGHT, [], Q3_SEVERE, 235, Q5_LOOSE),

        "SF03",

    )

    _run(

        PilotInput(Q1_INSTEP, [Q2_INSTEP], Q3_SLIGHT, 235, ""),

        "SF01",

    )

    _run_msg(

        PilotInput(Q1_INSTEP, [Q2_INSTEP], Q3_MID, 235, ""),

        "SF01",

        "발볼 늘림 1단계가 적합",

        "발볼 늘림 1단계",

    )

    _run(

        PilotInput(Q1_INSTEP, [Q2_INSTEP, Q2_BALL], Q3_MID, 235, ""),

        "SF01",

    )

    _run(

        PilotInput(Q1_INSTEP, [Q2_BALL], Q3_MID, 235, ""),

        "SF01",

    )

    res_instep_ball = evaluate(PilotInput(Q1_INSTEP, [Q2_BALL], Q3_MID, 235, ""))

    assert "전체적인 압박 완화" not in res_instep_ball.message

    _run(

        PilotInput(Q1_INSTEP, [Q2_BALL], Q3_SEVERE, 235, ""),

        "SF03",

    )

    _run(

        PilotInput(Q1_INSTEP, [Q2_HALLUX], Q3_SEVERE, 235, ""),

        "SF03",

    )

    _run(

        PilotInput(Q1_INSTEP, [Q2_INSTEP], Q3_SEVERE, 235, ""),

        "SF03",

    )

    res_instep_dup = evaluate(

        PilotInput(Q1_INSTEP, [Q2_INSTEP, Q2_HALLUX], Q3_SEVERE, 235, ""),

    )

    assert res_instep_dup.recommendation_code == "SF03"

    assert res_instep_dup.precision_recommended is False

    res_instep_only_sev = evaluate(

        PilotInput(Q1_INSTEP, [Q2_INSTEP], Q3_SEVERE, 235, ""),

    )

    assert res_instep_only_sev.recommendation_code == "SF03"

    assert res_instep_only_sev.precision_recommended is False

    res_tight_ball_sev = evaluate(

        PilotInput(Q1_TIGHT, [Q2_BALL], Q3_SEVERE, 240, ""),

    )

    assert res_tight_ball_sev.recommendation_code == "SF02"

    assert res_tight_ball_sev.precision_recommended is False

    _run(

        PilotInput("", [Q2_HALLUX], Q3_SEVERE, 235, ""),

        "SF02",

    )

    _run(
        PilotInput(Q1_INSTEP, [Q2_INSTEP, Q2_BALL], Q3_SEVERE, 235, ""),
        "SF03",
    )

    _run(
        PilotInput(Q1_LOOSE, [], Q3_MID, 235, ""),
        "SF04",
    )

    _run(
        PilotInput(Q1_LOOSE, [Q2_NONE], Q3_NONE, 235, ""),
        "SF04",
    )

    _run(

        PilotInput("", [], Q3_MID, 235, Q5_LOOSE),

        "SF04",

    )

    _run(

        PilotInput(Q1_NONE, [], "", 235, ""),

        "SF00",

    )

    print("OK pilot rules")





if __name__ == "__main__":

    main()

