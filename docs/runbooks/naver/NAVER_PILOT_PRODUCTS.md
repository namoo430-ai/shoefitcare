# 네이버 다상품 · pilot 링크 등록

진단은 **pilot 하나**이며, `product_id`·`channel=naver_sms` 로 상품별 데이터가 쌓입니다.

## 1) 상품 추가

`config/naver_pilot_products.json` 의 `products` 에 항목을 추가합니다.

```json
"MY_SKU_02": {
  "short_codes": ["2", "sku02"],
  "return_url": "https://smartstore.naver.com/스토어/products/1234567890",
  "memo": "네이버 전용 내부 SKU"
}
```

- **키·product_id:** 영문·숫자·`_`·`-` (최대 64자). Admin·DB에 그대로 저장됩니다.
- **short_codes:** 문자·톡톡에 넣기 쉬운 짧은 코드 → `https://<domain>/n/2`
- **return_url:** 선택. 있으면 진단 결과 「스마트스토어에서 주문하기」 버튼에 사용.
- **stretch_on_option**, **stretch_option_label**, **exchange_event_active:** 상품별 늘림 옵션·교환 CTA (`config/naver_pilot_products.json`).

스토어 링크(전역): `config/naver_pilot_store_links.json` — `talktalk_url`, `fit_category_urls`.

JSON 수정 후 **재배포**(또는 서버 재시작)해야 반영됩니다.

## 2) CS가 보내는 링크

| 방식 | URL 예 | 용도 |
|------|--------|------|
| 짧은 코드 | `/n/1` | JSON `short_codes` |
| 상품 ID | `/nv/SR266` 또는 `/n/SR266` | 등록·미등록 SKU 모두 가능* |
| 긴 URL | `/pilot?product_id=MY_SKU_02&src=naver_sms` | 디버그 |

\* **미등록 SKU**도 `product_id` 형식만 맞으면 `/nv/<id>` 로 진단 수집 가능 (`return_url` 없음).

## 3) 확인

```text
GET /health/build
```

→ `naver_pilot_skus`, `naver_sms_short_codes`

```powershell
python scripts/smoke_naver_detail_link.py
```

## 4) 상세 HTML

상품마다 `docs/demo/naver_<SKU>_detail_paste.html` 을 두거나, 공통 안내만 쓰고 **링크는 CS가 상품별 `/nv/...` 로 회신**합니다.

관련: [NAVER_PILOT_HTML_TEST.md](./NAVER_PILOT_HTML_TEST.md)
