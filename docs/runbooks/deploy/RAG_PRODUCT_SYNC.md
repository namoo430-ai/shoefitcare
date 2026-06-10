# RAG Product Sync Runbook

## 목적
- 상품 CSV 변경(재고/가격/단종/스펙/태그)을 RAG 상품 문서에 동기화한다.
- 문서 버전(`doc_version`)과 소스 갱신 시각(`source_updated_at`)을 기록해 재현성을 확보한다.

## 동기화 대상
- Source CSV:
  - `csv_templates/products.csv`
  - `csv_templates/product_fit_specs.csv`
  - `csv_templates/product_tags.csv`
- Target Docs:
  - `data/rag_docs/products/product_<product_id>.json`
  - `data/rag_docs/products/_sync_manifest.json`

## 실행 방법
1) 로컬/운영 배치 (프로젝트 루트에서 권장):
- `cd C:\DongaAI\project02\mvp_v1`
- `python scripts/sync_rag_product_docs.py`

실행 위치와 무관하게 동기화 모듈은 `mvp_v1` 루트의 `csv_templates` / `data/rag_docs`를 사용한다.

2) API 트리거:
- `POST /ops/rag-sync-products`

## 문서 정책
- `doc_type`: `product_knowledge`
- `doc_version`: `RAG_PRODUCT_DOC_VERSION`(기본 `v1`)
- `source_updated_at`: source CSV 3종의 최신 수정 시각
- `metadata.search_excluded`:
  - `status`가 `판매중/on_sale/active`가 아니면 `true` (검색 제외 안전모드)

## 운영 체크포인트
- `_sync_manifest.json`에서 `created/updated/deleted` 추이 확인
- `inactive_products` 증가 시 단종/재고 정책 점검
- 동기화 실패 시 검색 인덱스 재빌드 전에 원인 해결
