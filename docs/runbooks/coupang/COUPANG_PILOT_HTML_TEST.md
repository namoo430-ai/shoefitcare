# 쿠팡 상세 HTML · 파일럿(pilot) 연동 테스트

**전체 순서·게이트:** [COUPANG_DEPLOY_CHECKLIST.md](./COUPANG_DEPLOY_CHECKLIST.md)

## 1) 공개 URL (필수)

쿠팡·모바일 테스트는 **HTTPS 공개 도메인**이 필요합니다 (로컬 `127.0.0.1`은 쿠팡 상세에서 고객이 열 수 없음).

배포 후 예시:

```text
https://<YOUR_DOMAIN>/product-detail?product_id=<SKU>&src=html_detail
https://<YOUR_DOMAIN>/pilot?product_id=<SKU>&src=coupang_sms&return_url=<쿠팡상품페이지_URL_인코딩>
```

- **문자·쿠팡 유입:** `product-detail` 생략 가능 → **`/pilot` 직행** 권장.
- **`return_url`:** 쿠팡 Wing 상품 페이지 URL (`encodeURIComponent`). 결과 화면 **「쿠팡에서 주문하기」** 버튼.
- **`product-detail`:** 자사 이미지 상세 + CTA + admin 퍼널(`detail_view`)용. 쿠팡 링크 불가·문자만 쓸 때는 필수 아님.

### SR266 · 문자 회신 링크 (운영 예시)

**짧은 URL (권장, 문자용):**

```text
https://shoefitcare-chatbot.onrender.com/c/SR266
```

→ `/pilot?...&return_url=`(쿠팡 상품) 로 자동 이동. 매핑: `pilot_links.py` · `GET /health/build` → `pilot_short_paths`

긴 URL (동일 동작, 디버그용):

```text
https://shoefitcare-chatbot.onrender.com/pilot?product_id=SR266&src=coupang_sms&return_url=...
```

CS 문자 본문 예:

```text
[엄마신발 발볼 확인]
위 링크를 눌러 발볼 확인을 진행해 주세요.
완료 후 안내에 따라 쿠팡 판매자 문의 또는 진단번호를 알려 주세요.
```

- 상품 이미지: `https://<YOUR_DOMAIN>/product-images/prouct_SR266/001_01.jpg` (배포 시 `images/` 포함 확인)
- 상태: `GET https://<YOUR_DOMAIN>/health/build` → `pilot_build` 확인

## 2) 쿠팡에 넣을 것

1. **상품 상세 HTML** 영역에 자사 상세 URL 연결  
   - 방식은 쿠팡 셀러 도구에 맞게: HTML 블록, 이미지+링크, 외부 상세 URL 등  
2. CTA는 상세 페이지 안의 **「내 발에 맞는 발볼 확인 하기」** → 자동으로 `/pilot` 이동 (`src=html_detail`)
3. `product_id` 쿼리는 **실제 등록 상품번호**로 교체 (테스트: `SR266` 또는 쿠팡 SKU)

## 3) 오늘 확인 체크리스트 (배포 전·후)

| # | 확인 |
|---|------|
| 1 | 로컬: `python scripts/smoke_pilot_photo_upload.py` 성공 |
| 2 | 브라우저: 상세 → pilot 4문항 → 정밀 폼 → **사진 선택** → 제출 → “사진 접수” 문구 |
| 3 | admin: `/admin?token=<ADMIN_TOKEN>` 퍼널·**앱 사진 업로드**·진단 목록 **사진 보기** |
| 4 | 배포: `ADMIN_TOKEN` 환경변수, `data/`·DB는 서버 디스크 (Render는 재배포 시 유실 가능 — 파일럿 인지) |
| 5 | 모바일: 쿠팡 앱에서 상세 → CTA → pilot 전 구간 |

## 4) 사진 업로드 (주력) + 문자 (보조)

- **주력:** pilot 정밀 폼 `POST /pilot/precision-photo` (jpg/png/webp, 5MB)
- **보조:** 미업로드 시 완료 화면·폼 하단 `010-8931-6325` 안내
- **운영:** 문자로만 받은 건 admin **③ 일별 사진 수신** 수기 입력

## 5) 배포 전 (저장소 업로드 시)

```bash
python scripts/purge_local_data.py
python -m py_compile api.py pilot_storage.py pilot_ui.py
```

민감 데이터·`.env`·`data/` 커밋 금지. `images/prouct_SR266/` 는 상세용으로 **저장소에 포함** 필요.

## 6) 관련 코드

- 상세: `docs/demo/product_detail.html`
- pilot UI: `pilot_ui.py`
- 사진 API: `api.py` `/pilot/precision-photo`
- 설계: `docs/plans/PILOT_PHOTO_UPLOAD_DESIGN.md`
