# 쿠팡 연동·배포 체크리스트

버전: 20260605  
목적: **쿠팡 Wing 상품**에 슈핏케어 파일럿(`/product-detail` → `/pilot`)을 붙이기까지의 **순서·게이트**를 한 장으로 고정한다.

관련: [COUPANG_PILOT_HTML_TEST.md](./COUPANG_PILOT_HTML_TEST.md) · [COUPANG_INQUIRY_INTEGRATION.md](./COUPANG_INQUIRY_INTEGRATION.md) · [DEPLOY_RENDER.md](../deploy/DEPLOY_RENDER.md) · [SECURITY_PREP_1MIN_CHECKLIST.md](../security/SECURITY_PREP_1MIN_CHECKLIST.md) · [PILOT_DATA_RETURN_LOOP.md](../../plans/PILOT_DATA_RETURN_LOOP.md)

---

## Phase 0 — 쿠팡 셀러·상품 (플랫폼)

| # | 할 일 | 완료 |
|---|--------|:----:|
| 0.1 | 쿠팡 **Wing** 판매자 계정·정산·배송·CS 채널 준비 | ☐ |
| 0.2 | 상품 등록 (옵션: **사이즈 등만** — 발볼 늘림 1·2단계는 옵션에 넣지 않음) | ☐ |
| 0.3 | **내부 SKU** ↔ 쿠팡 노출 ID 정리 (예: `SR266` + URL의 `product_id` 값) | ☐ |
| 0.4 | CS SOP: 문의에서 **`diagnosis_code`** + **주문번호** 확인 → admin 연결 ([데이터 루프 §6](../../plans/PILOT_DATA_RETURN_LOOP.md)) | ☐ |
| 0.5 | 복합 증상은 당장 SF 승격하지 않음 — [복합증상 정책 §5](../../plans/PILOT_DATA_RETURN_LOOP.md) 팀 합의 공유 | ☐ |

---

## Phase 1 — 저장소·보안 (GitHub 업로드 전)

**하나라도 실패하면 업로드·배포 중단.**

| # | 할 일 | 완료 |
|---|--------|:----:|
| 1.1 | `python scripts/purge_local_data.py` | ☐ |
| 1.2 | `.gitignore`에 `data/`, `*.db`, 로그, `.env` 포함 확인 | ☐ |
| 1.3 | 코드·문서에 API 키·토큰 하드코딩 없음 | ☐ |
| 1.4 | 커밋 목록에 세션/로그/DB/고객 원문 없음 | ☐ |
| 1.5 | `python -m py_compile api.py session.py engine.py storage.py pilot_engine.py pilot_storage.py pilot_ui.py` | ☐ |
| 1.6 | `python scripts/test_pilot_rules.py` | ☐ |

체크리스트 상세: [SECURITY_PREP_1MIN_CHECKLIST.md](../security/SECURITY_PREP_1MIN_CHECKLIST.md)

---

## Phase 2 — 공개 HTTPS 배포

쿠팡 앱에서는 **로컬 URL 불가**. 이 단계가 끝나야 Phase 4 이후 테스트 가능.

| # | 할 일 | 완료 |
|---|--------|:----:|
| 2.1 | GitHub 저장소 push (민감 파일 제외) | ☐ |
| 2.2 | Render Blueprint → `render.yaml` 웹 서비스 생성 ([DEPLOY_RENDER.md](../deploy/DEPLOY_RENDER.md)) | ☐ |
| 2.3 | 환경변수 **`ADMIN_TOKEN`** (및 필요 시 기타 secret) Render 대시보드에만 설정 | ☐ |
| 2.4 | `images/prouct_SR266/` 등 상세용 이미지가 **배포 산출물에 포함**되는지 확인 | ☐ |
| 2.5 | `GET https://<도메인>/health/build` → `pilot_build`, `pilot_rule_version` 기대값 | ☐ |
| 2.6 | (선택) 유휴 슬립 대비 데모·라이브 전 워밍업 호출 | ☐ |

**Render 주의:** `data/`·SQLite는 디스크 의존 — 재배포·스케일 시 유실 가능. 파일럿 기간 인지 후 admin 백업·연결률 모니터.

배포 후 URL 템플릿:

```text
https://<YOUR_DOMAIN>/product-detail?product_id=<SKU>
https://<YOUR_DOMAIN>/pilot?product_id=<SKU>&src=html_detail
https://<YOUR_DOMAIN>/admin?token=<ADMIN_TOKEN>
```

---

## Phase 3 — 배포 직후 기능 스모크 (데스크톱)

| # | 할 일 | 완료 |
|---|--------|:----:|
| 3.1 | `python scripts/smoke_pilot_photo_upload.py` (로컬 또는 CI; 배포 전에도 권장) | ☐ |
| 3.2 | 상세 → **내 발에 맞는 발볼 확인** → `/pilot` 4문항 → 결과 | ☐ |
| 3.3 | **SF00**: 복사 버튼 없음 · **주문 페이지로 돌아가기** | ☐ |
| 3.4 | **SF01/SF02**: **발볼 늘림 안내문 복사** → 클립보드·진단번호 포함 | ☐ |
| 3.5 | 정밀 폼 → 사진 업로드 → 완료 문구 · admin **사진 보기** | ☐ |
| 3.6 | `/api/admin/kpi` · 진단 PATCH (`order_no`, `return_status`, `actual_work_step`) | ☐ |

상세 시나리오: [COUPANG_PILOT_HTML_TEST.md](./COUPANG_PILOT_HTML_TEST.md)

---

## Phase 4 — 쿠팡 상세에 연결

| # | 할 일 | 완료 |
|---|--------|:----:|
| 4.1 | Wing 상품 상세에 **자사 상세 URL** 연결 (HTML 블록 / 이미지+링크 등 셀러 도구에 맞는 방식) | ☐ |
| 4.2 | 링크의 `product_id=` 를 **실제 등록 SKU**와 일치 | ☐ |
| 4.3 | 상세 문구·이미지가 `docs/demo/product_detail.html` 의도와 맞는지 육안 확인 | ☐ |
| 4.4 | 고객 여정 문서 팀 공유: 복사는 **늘림 해당(SF01/SF02)** 위주 ([문의 연동](./COUPANG_INQUIRY_INTEGRATION.md) + 파일럿 UI) | ☐ |

---

## Phase 5 — 모바일 E2E (쿠팡 앱)

| # | 할 일 | 완료 |
|---|--------|:----:|
| 5.1 | 쿠팡 앱 → 해당 상품 상세 → 자사 링크 열림 (HTTPS·인증서) | ☐ |
| 5.2 | CTA → 파일럿 전 구간 (선택 피드백·뒤로가기·결과 화면) | ☐ |
| 5.3 | SF01/SF02: 복사 후 쿠팡 **판매자 문의** 붙여넣기 테스트 | ☐ |
| 5.4 | SF00: 주문 페이지 복귀 → 옵션 사이즈 선택까지 시나리오 확인 | ☐ |

---

## Phase 6 — 라이브 후 운영 (주 1회 루틴)

[PILOT_DATA_RETURN_LOOP.md §6](../../plans/PILOT_DATA_RETURN_LOOP.md) 와 동일.

| # | 할 일 | 완료 |
|---|--------|:----:|
| 6.1 | 문의·주문에서 `diagnosis_code` ↔ `order_no` admin 입력 | ☐ |
| 6.2 | KPI: 연결률, SF·`complex_case` 코호트 반품률 | ☐ |
| 6.3 | 룰/문구 변경 시 `PILOT_RULE_VERSION` bump + `test_pilot_rules.py` | ☐ |
| 6.4 | 문자·카카오만 온 사진 → admin **일별 사진 수신** 수기 | ☐ |

---

## Release gate (라이브 선언 조건)

**아래를 모두 만족할 때만** 쿠팡 상세에 고객 트래픽을 연다.

- Phase **1** 전항 통과  
- Phase **2.5** health/build 확인  
- Phase **3.2~3.4** 최소 1회씩 통과  
- Phase **5.1~5.2** 모바일 통과  
- CS가 **diagnosis_code·주문번호·발볼 단계** SOP 숙지  

---

## 빠른 명령 모음

```bash
python scripts/purge_local_data.py
python -m py_compile api.py session.py engine.py storage.py pilot_engine.py pilot_storage.py pilot_ui.py
python scripts/test_pilot_rules.py
python scripts/smoke_pilot_photo_upload.py
```
