# 02. Architecture

## High-level Structure

1. `api.py`
   - FastAPI 엔드포인트(`/chat`, `/webhook/naver`, `/demo`, `/report`)
   - 채널 어댑터 연계 및 운영 요약 API 제공
2. `session.py`
   - 상태머신 기반 대화 제어
   - 입력 검증, 질문 흐름, 결과 메시지 포맷
3. `hybrid_recommender.py`
   - CSV 데이터 로드
   - 후보 필터/랭킹/설명 생성
4. `engine.py`
   - 진단 로직 및 점수 계산의 코어 정책
5. `storage.py`
   - 입력/결과 저장 및 리포팅 연계

## Data Flow

1. 사용자 입력 수신
2. 상태머신에서 단계별 파싱/검증
3. 추천엔진 스코어링 및 TOP-N 생성
4. 설명 문구 생성 및 응답 반환
5. 이벤트/진단 결과 저장 (운영 요약용)

## Current Design Principles

- 결정(진단/추천)과 설명(LLM/RAG)을 분리
- 공통 엔진을 유지하고 정책 레이어로 확장
- 민감정보 최소 저장/마스킹 우선

## Missing Design Decisions Filled

### 1) 상태머신 실패/복구 정책

현재 구현 근거:
- `session.py`는 `ConversationController.handle_message()`에서 예외를 잡아 `_build_hybrid_recovery()`로 복구한다.
- 각 상태별 `quick_replies`가 있어 불완전 입력 시 선택지를 재제시한다.
- `ChatSession.from_json()`에서 레거시 상태를 승격해 세션 재진입 호환을 처리한다.

설계 결정:
- 정상 경로 외 입력은 "상태 유지 + 재질문"을 기본으로 한다.
- 복구는 2단계로 분리한다: `규칙 기반 파싱 재시도` -> 실패 시 `LLM 설명형 복구`.
- 세션 이탈 후 재진입 시 상태/필수 필드 무결성 검사 후, 누락 필드가 있으면 해당 질문부터 재개한다.
- 모순 입력(예: 이전 답과 충돌)은 즉시 재확인 질문으로 수렴시키고, 임의 자동 보정은 금지한다.

즉시 개선 TODO:
- `error_count` 임계치(예: 3회) 초과 시 "처음으로/상담 연결" 강제 분기 추가.
- 상태별 입력 스키마 검증 함수를 분리해 모순 감지 로직을 명시화.
- "재진입 복구 테스트셋"을 `scripts/`에 추가해 회귀 테스트 자동화.

### 2) 스코어링 가중치 명세

현재 구현 근거:
- `hybrid_recommender.py`는 적합도/사이즈/증상/가공용이성/인기도 점수와 반품 페널티를 합산한다.
- 주요 가중치는 `.env` 오버라이드 가능하며, 반품 고위험 페널티가 포함되어 있다.

설계 결정:
- 공식 점수식은 아래로 고정한다.
  - `total = fit + size + symptom + workability + popularity - risk_penalty`
- 가중치 변경은 `policy_version` 단위로만 허용하고, 운영 리포트에서 버전별 성능을 비교한다.
- 비즈니스 규칙(재고, 마진, 프로모션)은 "추천 후보 제한"에만 적용하고, 코어 점수와 분리 표기한다.
- 사용자 출력에는 "왜 추천됐는지"를 점수 항목 단위로 요약해 투명성을 유지한다.

즉시 개선 TODO:
- 현재 미반영 항목인 재고/마진 가중치 정책을 문서화하고 적용 위치를 결정.
- `/report` 또는 별도 리포트에 `score_breakdown` 집계 추가.
- 가중치 변경 이력 ADR 템플릿을 `10_decisions.md`로 강제 기록.

### 3) 데이터 보존 정책 (학습 vs 개인정보)

현재 구현 근거:
- `storage.py`는 `diagnosis_results`, `return_feedback`를 저장하고 `session_id`로 연결한다.
- RAG 문서 생성/업데이트(`save_rag_case_json`, `update_rag_return_status`)로 학습용 요약을 별도 보관한다.

설계 결정:
- 운영 DB와 학습(RAG) 저장소를 논리 분리하고, 공통 키는 익명화된 `session_id`로 유지한다.
- 직접식별자(전화번호/실명/원문 payload)는 저장 금지, 운영 요약 필드만 유지한다.
- 학습용 저장 범위는 "진단 입력 요약 + 추천 결과 + 반품 여부/사유"로 제한한다.
- 원본 대화 전문은 기본 미보관, 필요 시 기간 제한된 임시 로그만 허용한다.

즉시 개선 TODO:
- `session_id` 생성 규칙에 해시 salt 정책을 명시하고 문서화.
- 데이터 보존 기간(예: 운영 12개월, 학습 24개월)과 파기 배치를 운영 문서에 추가.
- "고객 삭제 요청" 처리 절차(운영 DB + RAG 동시 삭제) 명문화.

### 4) RAG 소스 문서 동기화 정책

현재 구현 근거:
- 진단 시 케이스 JSON을 만들고, 반품 피드백 수신 시 해당 문서를 갱신한다.
- 상품 지식 문서는 `rag_product_sync.py` / `scripts/sync_rag_product_docs.py`로 재생성할 수 있다.
- 운영 트리거로 `POST /ops/rag-sync-products`를 제공해 수동/배치 동기화를 지원한다.

설계 결정:
- RAG를 "고객 케이스 인덱스"와 "상품 지식 문서" 2종으로 분리한다.
- 상품 데이터 변경 이벤트(재고 0, 가격 급변, 단종)는 상품 문서 재생성 트리거로 연결한다.
- 문서 버전은 `doc_version`과 `source_updated_at`로 관리해 재현성을 확보한다.
- 동기화 실패 시 해당 문서를 검색 대상에서 임시 제외하는 안전모드를 둔다.

즉시 개선 TODO:
- 배치 스케줄러(cron/작업 스케줄러)로 `scripts/sync_rag_product_docs.py` 정기 실행.
- `policy_version`과 RAG 문서 버전 교차 추적 리포트 추가.
- 동기화 지연/실패 KPI(지연 시간, 누락 문서 수) 운영 대시보드에 추가.

### 5) 쿠팡 문의 연동 (HTML 상세 → 진단 → 문의 복사)

배경:
- 쿠팡 옵션에 발볼 늘림(1·2단계)을 넣을 수 없어 **판매자 문의**로 가공·사이즈를 접수한다.
- 쿠팡 상세 안 임베드: **자사 HTML 상세**에서 진단 링크로 이동한다.

유입 URL (예):
- 상세 랜딩: `/product-detail?product_id=<쿠팡상품번호>`
- 진단: `/demo?product_id=<SKU>&src=html_detail&mode=lite|full` (상세 버튼에서 자동 연결)
- `product_id` → 세션 `pinned_product_id`, CSV/RAG 상품 메타 조회
- 쿠팡 유입 결과: **TOP3 문구 제외**, `build_coupang_lite_result_display` / `build_coupang_full_result_display`

진단 완료 후 CTA (의도 분리):
| CTA | 이벤트 | KPI 의미 |
|-----|--------|----------|
| 진단 상품 바로가기 | `cta_buy_diagnosed` | 전환 성공(의도 proxy) |
| 다른 상품 보러가기 | `cta_browse_other` | 전환 실패(이탈 proxy) |

복사본 구성 (`comfort_result_copy.build_coupang_inquiry_copy_text`):
1. **[슈핏케어 진단·주문 양식]** — `진단번호(SF-xxxxxxxx)`, 상품코드, 권장사이즈·핏·발볼늘림, 경로  
2. **---**  
3. **(진단 안내)** — 챗봇 결과 본문 전체  

구현 근거:
- `session.py`: Full/Lite 완료 시 `inquiry_copy_text`, `checkout_payload` 생성  
- `api.py`: `/demo` 복사·구매·이탈 버튼, `POST /ops/cta-event`, `POST /chat`에 `product_id`/`traffic_src`  
- 운영 문서: `docs/runbooks/coupang/COUPANG_INQUIRY_INTEGRATION.md`

## Design Completion Re-evaluation (Engine-aligned)

| 설계 영역 | 현재 완성도 | 근거/판단 |
|---|---|---|
| 전체 플로우 구조 | ★★★★☆ | 상태 전이와 저장 흐름은 명확, 실패 케이스 문서화가 부족 |
| 결정/설명 분리 원칙 | ★★★★★ | 엔진 결정 + LLM/RAG 설명 분리가 코드/문서 모두 일관됨 |
| 상태머신 실패 처리 | ★★★☆☆ | 예외 복구는 있으나 모순 감지·임계치 분기가 미완성 |
| 스코어링 투명성 | ★★★☆☆ | 점수 항목은 있으나 가중치 정책/변경 관리 공개가 부족 |
| 데이터 루프 완결성 | ★★★☆☆ | 반품 피드백 연결은 존재, 익명화/보존 정책 문서화 부족 |
| 운영 안정성 | ★★★☆☆ | 기본 운영 가능, RAG 상품문서 동기화 체계 부재 |
| 법적 리스크 대비 | ★★★★☆ | 최소 저장 원칙 양호, 삭제요청/보존기간 정책 보강 필요 |

## Priority Improvements (Next 2 Sprints)

1. 상태머신: 모순 입력 감지 + 복구 임계치 분기(초기화/상담 연결) 추가.
2. 스코어링: 재고/마진 규칙을 코어 점수와 분리하고 버전 관리 도입.
3. 데이터 정책: 보존기간·파기·삭제요청 처리 정책 문서와 운영 스크립트 정리.
4. RAG 운영: 상품 데이터 변경 트리거 기반 동기화 배치 및 버전 필드 도입.

