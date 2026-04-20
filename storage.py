"""
슈핏케어 데이터 저장 레이어 (core/storage.py)
==============================================
역할:
  - 고객 입력 원본 + 진단 결과 → SQLite 저장
  - RAG 학습용 JSON 문서 자동 생성
  - 반품 피드백 저장 (반품율 추적)
  - 데이터 검색 (유사 케이스 조회)
"""

from __future__ import annotations
import sqlite3
import json
import os
from datetime import datetime
from dataclasses import asdict
from typing import Optional
from core.engine import CustomerInput, DiagnosisResult


DB_PATH = os.environ.get("SHOEFITCARE_DB", "data/shoefitcare.db")
RAG_DIR = os.environ.get("SHOEFITCARE_RAG_DIR", "data/rag_docs")


# ──────────────────────────────────────────────
# 1. DB 초기화
# ──────────────────────────────────────────────
def init_db(db_path: str = DB_PATH) -> None:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # 고객 입력 원본
    c.execute("""
        CREATE TABLE IF NOT EXISTS customer_inputs (
            session_id   TEXT PRIMARY KEY,
            shop_id      TEXT,
            policy_version TEXT,
            preferred_style TEXT,
            foot_issues  TEXT,  -- JSON array
            hallux_severity TEXT,
            instep_severity TEXT,
            toe_detail   TEXT,
            design       TEXT,
            original_size INTEGER,
            fit_experience TEXT,
            measurement_available INTEGER,
            foot_length_mm INTEGER,
            foot_ball_width_mm REAL,
            instep_circumference_mm REAL,
            created_at   TEXT
        )
    """)

    # 진단 결과
    c.execute("""
        CREATE TABLE IF NOT EXISTS diagnosis_results (
            session_id             TEXT PRIMARY KEY,
            shop_id                TEXT,
            policy_version         TEXT,
            recommended_product_id TEXT,
            recommended_product_name TEXT,
            recommended_fit        TEXT,
            recommendation_reason  TEXT,
            ready_made_option      TEXT,
            stretch_option         TEXT,
            ready_made_possible    INTEGER,
            original_size          INTEGER,
            final_size             INTEGER,
            size_adjusted          INTEGER,
            stretch_step           INTEGER,
            stretch_mm             REAL,
            stretch_reason         TEXT,
            additional_works       TEXT,  -- JSON array
            is_consult             INTEGER,
            consult_reason         TEXT,
            design                 TEXT,
            failure_experience     TEXT,
            composite_score        INTEGER,
            measurement_available  INTEGER,
            recommendation_path    TEXT,
            confidence_score       REAL,
            created_at             TEXT,
            FOREIGN KEY(session_id) REFERENCES customer_inputs(session_id)
        )
    """)

    # 반품 피드백 (사후 수집 → 반품율 추적)
    c.execute("""
        CREATE TABLE IF NOT EXISTS return_feedback (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id   TEXT,
            was_returned INTEGER,        -- 1=반품, 0=만족
            return_reason TEXT,          -- 반품 이유
            satisfaction_score INTEGER,  -- 1~5
            recorded_at  TEXT,
            FOREIGN KEY(session_id) REFERENCES diagnosis_results(session_id)
        )
    """)

    # 스키마 마이그레이션 (기존 DB 호환)
    _ensure_column(c, "customer_inputs", "measurement_available", "INTEGER")
    _ensure_column(c, "customer_inputs", "foot_length_mm", "INTEGER")
    _ensure_column(c, "customer_inputs", "foot_ball_width_mm", "REAL")
    _ensure_column(c, "customer_inputs", "instep_circumference_mm", "REAL")
    _ensure_column(c, "customer_inputs", "shop_id", "TEXT")
    _ensure_column(c, "customer_inputs", "policy_version", "TEXT")
    _ensure_column(c, "customer_inputs", "heel_slip_when_one_size_up", "INTEGER")

    _ensure_column(c, "diagnosis_results", "ready_made_option", "TEXT")
    _ensure_column(c, "diagnosis_results", "stretch_option", "TEXT")
    _ensure_column(c, "diagnosis_results", "composite_score", "INTEGER")
    _ensure_column(c, "diagnosis_results", "measurement_available", "INTEGER")
    _ensure_column(c, "diagnosis_results", "recommendation_path", "TEXT")
    _ensure_column(c, "diagnosis_results", "confidence_score", "REAL")
    _ensure_column(c, "diagnosis_results", "shop_id", "TEXT")
    _ensure_column(c, "diagnosis_results", "policy_version", "TEXT")

    conn.commit()
    conn.close()


def _ensure_column(cursor: sqlite3.Cursor, table: str, column: str, definition: str) -> None:
    cursor.execute(f"PRAGMA table_info({table})")
    cols = {row[1] for row in cursor.fetchall()}
    if column not in cols:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


# ──────────────────────────────────────────────
# 2. 저장 함수
# ──────────────────────────────────────────────
def save_customer_input(inp: CustomerInput, db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    heel = inp.heel_slip_when_one_size_up
    heel_sql = None if heel is None else (1 if heel else 0)
    c.execute("""
        INSERT OR REPLACE INTO customer_inputs (
            session_id, shop_id, policy_version, preferred_style, foot_issues, hallux_severity, instep_severity,
            toe_detail, design, original_size, fit_experience, measurement_available,
            foot_length_mm, foot_ball_width_mm, instep_circumference_mm,
            heel_slip_when_one_size_up, created_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        inp.session_id,
        inp.shop_id,
        inp.policy_version,
        inp.preferred_style,
        json.dumps(inp.foot_issues, ensure_ascii=False),
        inp.hallux_severity,
        inp.instep_severity,
        inp.toe_detail,
        inp.design,
        inp.original_size,
        inp.fit_experience,
        int(inp.measurement_available),
        inp.foot_length_mm,
        inp.foot_ball_width_mm,
        inp.instep_circumference_mm,
        heel_sql,
        inp.created_at,
    ))
    conn.commit()
    conn.close()


def save_diagnosis_result(res: DiagnosisResult, db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO diagnosis_results (
            session_id, shop_id, policy_version, recommended_product_id, recommended_product_name, recommended_fit,
            recommendation_reason, ready_made_option, stretch_option, ready_made_possible,
            original_size, final_size, size_adjusted, stretch_step, stretch_mm, stretch_reason,
            additional_works, is_consult, consult_reason, design, failure_experience,
            composite_score, measurement_available, recommendation_path, confidence_score, created_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        res.session_id,
        res.shop_id,
        res.policy_version,
        res.recommended_product_id,
        res.recommended_product_name,
        res.recommended_fit,
        res.recommendation_reason,
        res.ready_made_option,
        res.stretch_option,
        int(res.ready_made_possible),
        res.original_size,
        res.final_size,
        int(res.size_adjusted),
        res.stretch_step,
        res.stretch_mm,
        res.stretch_reason,
        json.dumps(res.additional_works, ensure_ascii=False),
        int(res.is_consult),
        res.consult_reason,
        res.design,
        res.failure_experience,
        res.composite_score,
        int(res.measurement_available),
        res.recommendation_path,
        res.confidence_score,
        res.created_at,
    ))
    conn.commit()
    conn.close()


def save_return_feedback(
    session_id: str,
    was_returned: bool,
    return_reason: str = "",
    satisfaction_score: int = 5,
    db_path: str = DB_PATH,
) -> None:
    """반품 여부 피드백 저장 — 핵심 반품율 추적 데이터"""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        INSERT INTO return_feedback (session_id, was_returned, return_reason, satisfaction_score, recorded_at)
        VALUES (?,?,?,?,?)
    """, (
        session_id,
        int(was_returned),
        return_reason,
        satisfaction_score,
        datetime.now().isoformat(),
    ))
    conn.commit()
    conn.close()


# ──────────────────────────────────────────────
# 3. RAG 문서 생성
# ──────────────────────────────────────────────
def export_rag_document(
    inp: CustomerInput,
    res: DiagnosisResult,
    rag_dir: str = RAG_DIR,
) -> str:
    """
    고객 케이스 1건 → RAG 검색용 JSON 문서 생성
    LLM이 유사 케이스를 참조해 더 나은 추천을 할 수 있도록
    """
    os.makedirs(rag_dir, exist_ok=True)

    # 자연어 요약 (RAG 검색의 핵심 텍스트)
    summary = _build_rag_summary(inp, res)

    doc = {
        "doc_id": inp.session_id,
        "doc_type": "diagnosis_case",
        "created_at": inp.created_at,
        # 검색에 사용될 텍스트
        "searchable_text": summary,
        # 메타데이터 (필터링용)
        "metadata": {
            "shop_id": inp.shop_id,
            "policy_version": inp.policy_version,
            "design": inp.design,
            "foot_issues": inp.foot_issues,
            "hallux_severity": inp.hallux_severity,
            "instep_severity": inp.instep_severity,
            "original_size": inp.original_size,
            "final_size": res.final_size,
            "recommended_product": res.recommended_product_name,
            "recommended_fit": res.recommended_fit,
            "ready_made_possible": res.ready_made_possible,
            "stretch_step": res.stretch_step,
            "is_consult": res.is_consult,
            "was_returned": None,  # 피드백 수신 후 업데이트
        },
        # 원본 데이터
        "customer_input": asdict(inp),
        "diagnosis_result": asdict(res),
    }

    path = os.path.join(rag_dir, f"{inp.session_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)

    return path


def update_rag_return_status(
    session_id: str,
    was_returned: bool,
    return_reason: str = "",
    rag_dir: str = RAG_DIR,
) -> None:
    """반품 피드백을 RAG 문서에 반영 → 추후 학습 데이터로 활용"""
    path = os.path.join(rag_dir, f"{session_id}.json")
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        doc = json.load(f)

    doc["metadata"]["was_returned"] = was_returned
    doc["metadata"]["return_reason"] = return_reason
    doc["searchable_text"] += (
        f"\n[결과] {'반품' if was_returned else '만족'}"
        + (f": {return_reason}" if return_reason else "")
    )

    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)


def _rag_heel_slip_label(inp: CustomerInput) -> str:
    h = getattr(inp, "heel_slip_when_one_size_up", None)
    if h is None:
        return "미응답/해당없음"
    return "있음" if h else "없음"


def _build_rag_summary(inp: CustomerInput, res: DiagnosisResult) -> str:
    """RAG 검색을 위한 자연어 요약문"""
    issues_str = ", ".join(inp.foot_issues) if inp.foot_issues else "특이사항 없음"
    stretch_str = (
        f"{res.stretch_step}단계({res.stretch_mm}mm) — {res.stretch_reason}"
        if res.stretch_step > 0 else "발볼늘림 불필요"
    )
    additional_str = ", ".join(res.additional_works) if res.additional_works else "없음"

    return f"""
디자인: {inp.design} / 발 유형: {issues_str}
무지외반 정도: {inp.hallux_severity} / 발등 높이: {inp.instep_severity}
기존 사이즈: {inp.original_size}mm / 착화 경험: {inp.fit_experience}
한 치수 업 시 헐떡임(꽉낌 보정 질문): {_rag_heel_slip_label(inp)}
→ [기성화 추천] {res.recommended_product_name}({res.recommended_fit}) — {res.recommendation_reason}
→ 기성화만으로 해결: {'가능' if res.ready_made_possible else '불가 (가공 필요)'}
→ 보정 사이즈: {res.final_size}mm {'(다운 보정)' if res.size_adjusted else ''}
→ [발볼늘림 보완] {stretch_str}
→ 추가 가공: {additional_str}
→ 상담 필요: {'예 — ' + res.consult_reason if res.is_consult else '아니오'}
""".strip()


# ──────────────────────────────────────────────
# 4. 데이터 조회 (유사 케이스 검색)
# ──────────────────────────────────────────────
def find_similar_cases(
    design: str,
    foot_issues: list[str],
    original_size: int,
    limit: int = 5,
    db_path: str = DB_PATH,
) -> list[dict]:
    """
    유사 발 유형 케이스 조회
    RAG 시스템에서 컨텍스트로 주입하거나, 추천 로직 개선에 활용
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # 같은 디자인 + 사이즈 ±10mm 범위
    c.execute("""
        SELECT ci.*, dr.recommended_product_name, dr.recommended_fit,
               dr.ready_made_possible, dr.stretch_step, dr.is_consult,
               rf.was_returned, rf.satisfaction_score
        FROM customer_inputs ci
        JOIN diagnosis_results dr ON ci.session_id = dr.session_id
        LEFT JOIN return_feedback rf ON ci.session_id = rf.session_id
        WHERE ci.design = ?
          AND ci.original_size BETWEEN ? AND ?
        ORDER BY ci.created_at DESC
        LIMIT ?
    """, (design, original_size - 10, original_size + 10, limit))

    rows = [dict(row) for row in c.fetchall()]
    conn.close()

    # 발 유형 일치도 기준으로 정렬
    issue_set = set(foot_issues)
    for row in rows:
        stored_issues = set(json.loads(row.get("foot_issues", "[]")))
        row["issue_overlap"] = len(issue_set & stored_issues)

    return sorted(rows, key=lambda x: -x["issue_overlap"])


def get_return_rate_report(
    db_path: str = DB_PATH,
    shop_id: Optional[str] = None,
    policy_version: Optional[str] = None,
) -> dict:
    """반품율 리포트 — 핵심 KPI"""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    filters_diag = []
    filters_join = []
    params: list[str] = []
    if shop_id:
        filters_diag.append("shop_id = ?")
        filters_join.append("dr.shop_id = ?")
        params.append(shop_id)
    if policy_version:
        filters_diag.append("policy_version = ?")
        filters_join.append("dr.policy_version = ?")
        params.append(policy_version)
    where_diag = f" WHERE {' AND '.join(filters_diag)}" if filters_diag else ""
    where_join = f" WHERE {' AND '.join(filters_join)}" if filters_join else ""
    q_params = tuple(params)

    c.execute(f"SELECT COUNT(*) FROM diagnosis_results{where_diag}", q_params)
    total = c.fetchone()[0]

    c.execute(
        f"""
        SELECT COUNT(*), AVG(rf.was_returned)
        FROM return_feedback rf
        JOIN diagnosis_results dr ON dr.session_id = rf.session_id
        {where_join}
        """,
        q_params,
    )
    row = c.fetchone()
    feedback_count, return_rate = row[0], (row[1] or 0)

    # 디자인별 반품율
    c.execute(f"""
        SELECT dr.design,
               COUNT(*) as cnt,
               AVG(rf.was_returned) as return_rate
        FROM diagnosis_results dr
        JOIN return_feedback rf ON dr.session_id = rf.session_id
        {where_join}
        GROUP BY dr.design
    """, q_params)
    by_design = {row[0]: {"count": row[1], "return_rate": round((row[2] or 0)*100, 1)}
                 for row in c.fetchall()}

    # 가공 단계별 반품율
    c.execute(f"""
        SELECT dr.stretch_step,
               COUNT(*) as cnt,
               AVG(rf.was_returned) as return_rate
        FROM diagnosis_results dr
        JOIN return_feedback rf ON dr.session_id = rf.session_id
        {where_join}
        GROUP BY dr.stretch_step
    """, q_params)
    by_stretch = {f"{row[0]}단계": {"count": row[1], "return_rate": round((row[2] or 0)*100, 1)}
                  for row in c.fetchall()}

    conn.close()
    return {
        "shop_id": shop_id or "all",
        "policy_version": policy_version or "all",
        "total_diagnoses": total,
        "feedback_collected": feedback_count,
        "overall_return_rate": f"{return_rate*100:.1f}%",
        "by_design": by_design,
        "by_stretch_step": by_stretch,
    }
