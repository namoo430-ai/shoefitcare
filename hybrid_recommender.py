from __future__ import annotations

"""
하이브리드 추천기 (태깅 + 룰/점수 + LLM 보조설명)

1) 태깅/메타 기반 후보 필터
2) 진단결과 매칭 점수 랭킹
3) 설명문 생성 (기본 템플릿, 선택적으로 LLM 보강 가능)
"""

import csv
from dataclasses import dataclass
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from core.engine import PRODUCT_CATALOG


@dataclass
class Candidate:
    product_id: str
    name: str
    category: str
    size_mm: int
    fit: str
    width_code: str
    tags: list[str]
    review_count: int
    rating: float
    score_fit: int = 0
    score_size: int = 0
    score_symptom: int = 0
    score_workability: int = 0
    score_popularity: int = 0
    penalty_risk: int = 0
    total_score: int = 0
    reason: str = ""


# 샘플 메타(실운영은 DB/CSV로 교체 권장)
PRODUCT_META = {
    "dress_slim": {"tags": ["기본", "슬림"], "review_count": 72, "rating": 4.3},
    "dress_wide": {"tags": ["넓은발볼_우호", "무지외반_우호", "앞코여유"], "review_count": 181, "rating": 4.7},
    "dress_extra": {"tags": ["무지외반_우호", "넓은발볼_우호", "편안함_우선"], "review_count": 95, "rating": 4.6},
    "loafer_std": {"tags": ["기본"], "review_count": 88, "rating": 4.4},
    "loafer_wide": {"tags": ["넓은발볼_우호", "무지외반_우호"], "review_count": 211, "rating": 4.8},
    "flat_basic": {"tags": ["기본"], "review_count": 65, "rating": 4.2},
    "flat_wide": {"tags": ["넓은발볼_우호", "앞코여유"], "review_count": 154, "rating": 4.6},
    "sneaker_std": {"tags": ["기본"], "review_count": 120, "rating": 4.4},
    "sneaker_wide": {"tags": ["넓은발볼_우호", "발등_우호"], "review_count": 260, "rating": 4.7},
    "sneaker_xtra": {"tags": ["무지외반_우호", "넓은발볼_우호", "편안함_우선"], "review_count": 170, "rating": 4.8},
}

FIT_ORDER = ["기본핏", "편한핏", "아주 편한핏"]


class HybridProductRecommender:
    def __init__(self):
        self.llm_enabled = os.environ.get("HYBRID_RECO_LLM_ENABLED", "false").strip().lower() in ("1", "true", "yes", "on")
        self.api_url = os.environ.get("HYBRID_LLM_API_URL", "").strip()
        self.api_key = os.environ.get("HYBRID_LLM_API_KEY", "").strip()
        self.model = os.environ.get("HYBRID_LLM_MODEL", "gpt-4o-mini").strip()
        self._base_dir = Path(__file__).resolve().parent
        self._csv_dir = self._base_dir / "csv_templates"
        # Scoring weights (.env override 가능)
        self.w_fit_exact = self._env_int("HYBRID_RECO_WEIGHT_FIT_EXACT", 40)
        self.w_fit_near = self._env_int("HYBRID_RECO_WEIGHT_FIT_NEAR", 20)
        self.w_size_exact = self._env_int("HYBRID_RECO_WEIGHT_SIZE_EXACT", 25)
        self.w_size_near = self._env_int("HYBRID_RECO_WEIGHT_SIZE_NEAR", 10)
        self.w_symptom_wide = self._env_int("HYBRID_RECO_WEIGHT_SYMPTOM_WIDE", 10)
        self.w_symptom_hallux = self._env_int("HYBRID_RECO_WEIGHT_SYMPTOM_HALLUX", 10)
        self.w_symptom_toe = self._env_int("HYBRID_RECO_WEIGHT_SYMPTOM_TOE", 8)
        self.w_symptom_instep = self._env_int("HYBRID_RECO_WEIGHT_SYMPTOM_INSTEP", 8)
        self.w_design_match = self._env_int("HYBRID_RECO_WEIGHT_DESIGN_MATCH", 10)
        self.w_work_stretch_friendly = self._env_int("HYBRID_RECO_WEIGHT_WORK_STRETCH", 10)
        self.w_work_no_stretch = self._env_int("HYBRID_RECO_WEIGHT_WORK_NOSTRETCH", 5)
        self.w_pop_review_high = self._env_int("HYBRID_RECO_WEIGHT_POP_REVIEW_HIGH", 8)
        self.w_pop_review_mid = self._env_int("HYBRID_RECO_WEIGHT_POP_REVIEW_MID", 5)
        self.w_pop_rating_high = self._env_int("HYBRID_RECO_WEIGHT_POP_RATING_HIGH", 8)
        self.w_pop_rating_mid = self._env_int("HYBRID_RECO_WEIGHT_POP_RATING_MID", 5)
        self.penalty_return_high = self._env_int("HYBRID_RECO_PENALTY_RETURN_HIGH", 30)

    def recommend_top3(self, inp, res) -> list[dict]:
        candidates = self._build_candidates(inp, res)
        if not candidates:
            return []

        # 1차 필터: 디자인 + 핏 근접도
        filtered = self._filter_candidates(candidates, res.recommended_fit)
        if not filtered:
            filtered = candidates

        # 2차 랭킹: 룰/점수
        ranked = self._rank(filtered, inp, res)
        top3 = ranked[:3]

        # 3차 설명문: 기본 템플릿 + (옵션) LLM 보강
        self._attach_explanations(top3, inp, res)

        result = []
        for c in top3:
            result.append(
                {
                    "product_id": c.product_id,
                    "name": c.name,
                    "fit": c.fit,
                    "size_mm": c.size_mm,
                    "total_score": c.total_score,
                    "score_breakdown": {
                        "fit": c.score_fit,
                        "size": c.score_size,
                        "symptom": c.score_symptom,
                        "workability": c.score_workability,
                        "popularity": c.score_popularity,
                        "risk_penalty": c.penalty_risk,
                    },
                    "reason": c.reason,
                }
            )
        return result

    def _build_candidates(self, inp, res) -> list[Candidate]:
        csv_rows = self._build_candidates_from_csv(inp, res)
        if csv_rows:
            return csv_rows
        return self._build_candidates_from_catalog(inp, res)

    def _build_candidates_from_catalog(self, inp, res) -> list[Candidate]:
        rows = []
        for p in PRODUCT_CATALOG.get(inp.design, []):
            meta = PRODUCT_META.get(p["id"], {"tags": [], "review_count": 0, "rating": 0.0})
            rows.append(
                Candidate(
                    product_id=p["id"],
                    name=p["name"],
                    category=inp.design,
                    size_mm=int(res.final_size),
                    fit=p["fit"],
                    width_code=p["width_code"],
                    tags=list(meta.get("tags", [])),
                    review_count=int(meta.get("review_count", 0)),
                    rating=float(meta.get("rating", 0.0)),
                )
            )
        return rows

    def _build_candidates_from_csv(self, inp, res) -> list[Candidate]:
        products_path = self._csv_dir / "products.csv"
        specs_path = self._csv_dir / "product_fit_specs.csv"
        tags_path = self._csv_dir / "product_tags.csv"
        feedback_path = self._csv_dir / "orders_returns_fit_feedback.csv"

        if not products_path.exists() or not specs_path.exists():
            return []

        products = self._load_products(products_path)
        fit_specs = self._load_fit_specs(specs_path)
        tags_map = self._load_tags(tags_path) if tags_path.exists() else {}
        feedback_stats = self._load_return_stats(feedback_path) if feedback_path.exists() else {}

        rows: list[Candidate] = []
        target_size = int(res.final_size)
        target_design = str(inp.design).strip()

        for pid, prod in products.items():
            category = str(prod.get("category", "")).strip()
            if category != target_design:
                continue

            status = str(prod.get("status", "")).strip()
            if status and status not in ("판매중", "on_sale", "active"):
                continue

            specs = fit_specs.get(pid, [])
            if not specs:
                continue
            chosen = self._pick_nearest_size_spec(specs, target_size)
            if not chosen:
                continue

            ret = feedback_stats.get(pid, {"count": 0, "returned": 0})
            return_rate = (ret["returned"] / ret["count"]) if ret["count"] > 0 else 0.0
            penalty = self.penalty_return_high if ret["count"] >= 3 and return_rate >= 0.3 else 0

            rows.append(
                Candidate(
                    product_id=pid,
                    name=str(prod.get("name", pid)).strip(),
                    category=category,
                    size_mm=int(chosen.get("size_mm", target_size)),
                    fit=str(chosen.get("fit_line", "편한핏")).strip(),
                    width_code=str(chosen.get("width_code", "")).strip(),
                    tags=tags_map.get(pid, []),
                    review_count=int(self._to_int(prod.get("review_count"), 0)),
                    rating=float(self._to_float(prod.get("rating"), 0.0)),
                    penalty_risk=penalty,
                )
            )
        return rows

    def _fit_distance(self, a: str, b: str) -> int:
        try:
            return abs(FIT_ORDER.index(a) - FIT_ORDER.index(b))
        except ValueError:
            return 2

    def _filter_candidates(self, rows: list[Candidate], target_fit: str) -> list[Candidate]:
        # 타깃핏 ±1 단계까지만 우선 후보
        return [r for r in rows if self._fit_distance(r.fit, target_fit) <= 1]

    def _rank(self, rows: list[Candidate], inp, res) -> list[Candidate]:
        issues = set(inp.foot_issues or [])
        for r in rows:
            # Fit (가중치 중심)
            dist = self._fit_distance(r.fit, res.recommended_fit)
            if dist == 0:
                r.score_fit = self.w_fit_exact
            elif dist == 1:
                r.score_fit = self.w_fit_near
            else:
                r.score_fit = 0

            # Size (추천 사이즈와 근접할수록 가산)
            diff = abs(int(r.size_mm) - int(res.final_size))
            if diff == 0:
                r.score_size = self.w_size_exact
            elif diff == 5:
                r.score_size = self.w_size_near
            else:
                r.score_size = 0

            # Symptom tags
            sym = 0
            if "넓음" in issues and "넓은발볼_우호" in r.tags:
                sym += self.w_symptom_wide
            if "무지외반" in issues and "무지외반_우호" in r.tags:
                sym += self.w_symptom_hallux
            if "앞코" in issues and "앞코여유" in r.tags:
                sym += self.w_symptom_toe
            if "발등 높음" in issues and "발등_우호" in r.tags:
                sym += self.w_symptom_instep
            if str(r.category).strip() == str(inp.design).strip():
                sym += self.w_design_match
            r.score_symptom = sym

            # Workability
            work = 0
            if res.stretch_step > 0 and ("앞코여유" in r.tags or "넓은발볼_우호" in r.tags):
                work += self.w_work_stretch_friendly
            elif res.stretch_step == 0:
                work += self.w_work_no_stretch
            r.score_workability = work

            # Popularity (후기 보조점수)
            pop = 0
            if r.review_count >= 200:
                pop += self.w_pop_review_high
            elif r.review_count >= 100:
                pop += self.w_pop_review_mid
            if r.rating >= 4.7:
                pop += self.w_pop_rating_high
            elif r.rating >= 4.5:
                pop += self.w_pop_rating_mid
            r.score_popularity = pop

            r.total_score = (
                r.score_fit
                + r.score_size
                + r.score_symptom
                + r.score_workability
                + r.score_popularity
                - r.penalty_risk
            )
        rows.sort(key=lambda x: x.total_score, reverse=True)
        return rows

    def _attach_explanations(self, rows: list[Candidate], inp, res) -> None:
        # 기본 템플릿 설명
        for r in rows:
            reasons = [f"{res.recommended_fit} 추천 기준과 잘 맞아요"]
            if "넓은발볼_우호" in r.tags and "넓음" in (inp.foot_issues or []):
                reasons.append("넓은 발볼 대응 태그가 있어요")
            if "무지외반_우호" in r.tags and "무지외반" in (inp.foot_issues or []):
                reasons.append("무지외반 완화에 유리한 태그가 있어요")
            if r.review_count >= 100 and r.rating >= 4.5:
                reasons.append("후기 수와 평점이 안정적이에요")
            r.reason = " / ".join(reasons[:3])

        if not self.llm_enabled:
            return
        if not self.api_url:
            return

        # 옵션: LLM 보강 (실패 시 무시)
        try:
            payload = [
                {"name": r.name, "fit": r.fit, "reason": r.reason, "score": r.total_score}
                for r in rows
            ]
            enriched = self._llm_rewrite(payload)
            if isinstance(enriched, list):
                for i, text in enumerate(enriched[: len(rows)]):
                    if isinstance(text, str) and text.strip():
                        rows[i].reason = text.strip()
        except Exception:
            return

    def _llm_rewrite(self, payload: list[dict]) -> list[str] | None:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        body = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "각 상품 추천 사유를 1문장으로 간결하게 다듬어라. 사실값을 바꾸지 마라.",
                },
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            "temperature": 0.2,
        }
        req = urllib.request.Request(
            self.api_url,
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                parsed = json.loads(resp.read().decode("utf-8"))
            text = parsed.get("choices", [{}])[0].get("message", {}).get("content", "")
            # 간단 파싱: 줄 단위
            lines = [ln.strip("- ").strip() for ln in str(text).splitlines() if ln.strip()]
            return lines if lines else None
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError, KeyError, TypeError):
            return None

    def _load_products(self, path: Path) -> dict[str, dict]:
        out: dict[str, dict] = {}
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                pid = str((row.get("product_id") or "")).strip()
                if pid:
                    out[pid] = row
        return out

    def _load_fit_specs(self, path: Path) -> dict[str, list[dict]]:
        out: dict[str, list[dict]] = {}
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                pid = str((row.get("product_id") or "")).strip()
                if not pid:
                    continue
                size = self._to_int(row.get("size_mm"), None)
                if size is None:
                    continue
                fit_line = str((row.get("fit_line") or "")).strip() or "편한핏"
                if fit_line == "아주편한핏":
                    fit_line = "아주 편한핏"
                row["size_mm"] = int(size)
                row["fit_line"] = fit_line
                out.setdefault(pid, []).append(row)
        return out

    def _load_tags(self, path: Path) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                pid = str((row.get("product_id") or "")).strip()
                if not pid:
                    continue
                tag_type = str((row.get("tag_type") or "")).strip()
                tag_value = str((row.get("tag_value") or "")).strip()
                if not tag_value:
                    continue
                if tag_type == "궆높이":
                    tag_type = "굽높이"
                if tag_value == "무외외반_우호":
                    tag_value = "무지외반_우호"
                out.setdefault(pid, []).append(tag_value)
        return out

    def _load_return_stats(self, path: Path) -> dict[str, dict]:
        out: dict[str, dict] = {}
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                pid = str((row.get("product_id") or "")).strip()
                if not pid:
                    continue
                was_returned = str((row.get("was_returned") or "")).strip().lower() in ("1", "true", "yes", "y")
                bucket = out.setdefault(pid, {"count": 0, "returned": 0})
                bucket["count"] += 1
                if was_returned:
                    bucket["returned"] += 1
        return out

    def _pick_nearest_size_spec(self, specs: list[dict], target_size: int) -> dict | None:
        if not specs:
            return None
        return sorted(specs, key=lambda row: abs(int(row.get("size_mm", target_size)) - target_size))[0]

    def _to_int(self, value, default):
        try:
            return int(str(value).strip())
        except Exception:
            return default

    def _to_float(self, value, default):
        try:
            return float(str(value).strip())
        except Exception:
            return default

    def _env_int(self, key: str, default: int) -> int:
        raw = os.environ.get(key, "")
        if raw is None or str(raw).strip() == "":
            return default
        try:
            return int(str(raw).strip())
        except Exception:
            return default
