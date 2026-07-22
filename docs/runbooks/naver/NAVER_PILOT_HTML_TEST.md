# 네이버 스마트스토어 · SR266 파일럿 (외부 링크 불가)

**내일 테스트:** [NAVER_TEST_DAY.md](./NAVER_TEST_DAY.md) · `python scripts/preflight_naver_test_day.py`

쿠팡과 같이 **상품 상세 HTML에 외부 URL(진단 링크)을 넣을 수 없습니다.**
운영 패턴은 **상세 = 이미지 + 안내 문구**, **진단 URL = 톡톡·문의·문자 회신** 입니다.

## 1) 상세에 붙여넣을 HTML

```text
docs/demo/naver_SR266_detail_paste.html
```

- 클릭 링크 없음 → 「톡톡·상품 문의에 발볼 확인」 안내
- 이미지는 Render `product-images` 절대 URL (필요 시 스마트스토어 이미지 업로드로 교체 가능)

## 2) CS가 보내는 진단 링크 (쿠팡 `/s/1` 대응)

```text
https://shoefitcare-chatbot.onrender.com/n/1          ← SR266 짧은 코드
https://shoefitcare-chatbot.onrender.com/nv/SR266     ← 상품 ID 직접 (다른 SKU 도 동일 패턴)
```

→ `/pilot?product_id=...&src=naver_sms` · 상품 추가·`return_url`: **`config/naver_pilot_products.json`** ([NAVER_PILOT_PRODUCTS.md](./NAVER_PILOT_PRODUCTS.md))

편안 지도 UI·복사 버튼·룰 요약: [NAVER_COMFORT_MAP_UX.md](../../plans/NAVER_COMFORT_MAP_UX.md)

톡톡·문의 회신 예:

```text
[엄마신발 발볼 확인]
아래 링크에서 발볼 확인을 진행해 주세요.
https://shoefitcare-chatbot.onrender.com/n/1
완료 후 안내에 따라 스마트스토어 문의에 진단번호를 남겨 주세요.
```

## 3) 테스트 순서 (배포 후)

| # | 확인 |
|---|------|
| 1 | 상세 HTML 붙여넣기 → 미리보기에서 이미지·안내 문구 표시 |
| 2 | 본인 휴대폰에서 `/n/1` 열기 → pilot 4문항 진행 |
| 3 | JSON에 `return_url` 넣고 재배포 → 결과 화면 「스마트스토어에서 주문하기」 (URL 있을 때만) |
| 4 | Admin 진단 목록 · channel `naver_sms` |
| 5 | `/seller/quick?token=...` → 진단번호·핏 선택 → 답변 복사 (톡톡/카톡) |

스모크:

```powershell
python scripts/preflight_naver_test_day.py
```

### 판매자 빠른 답변

- 북마크: `/seller/quick?token=<ADMIN_TOKEN>` (관리자 토큰과 동일)
- 진단번호 조회 → **기본핏 / 편한핏 / 아주 편한핏** 선택 → 짧은/긴/1회 교환 문구 복사
- 「생성 시 실작업·메모 저장」 체크 시 `actual_work_step`·메모를 Admin DB에 반영

## 4) 쿠팡과 대응

| | 쿠팡 | 네이버 |
|---|------|--------|
| 상세 | 이미지 위주 | `naver_SR266_detail_paste.html` |
| CS 링크 | `/s/1` | `/n/{code}`, `/nv/{sku}` |
| `src` | `coupang_sms` | `naver_sms` |
| 주문 복귀 | `PILOT_GO` | `config/naver_pilot_products.json` |

## 5) 코드

- `config/naver_pilot_products.json` — 다상품·짧은코드·return_url
- `pilot_links.py` — JSON 로드
- `api.py` — `GET /n/{code}`, `GET /nv/{sku}`, `GET /seller/quick`, `POST /api/seller/reply`
- `pilot_seller_reply.py` — 핏 라인 + SF 코드 → 답변문
- 상세 paste: `docs/demo/naver_SR266_detail_paste.html`

관련: [COUPANG_PILOT_HTML_TEST.md](../coupang/COUPANG_PILOT_HTML_TEST.md)
