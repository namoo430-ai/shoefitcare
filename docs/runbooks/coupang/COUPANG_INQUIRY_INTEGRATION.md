# 쿠팡 문의 연동 (진단 → 문의글)

**배포·연동 순서:** [COUPANG_DEPLOY_CHECKLIST.md](./COUPANG_DEPLOY_CHECKLIST.md)

## 배경

- 쿠팡 상품 옵션에 **발볼 늘림 1·2단계**를 추가할 수 없음.
- 발볼 가공·사이즈 안내는 **판매자 문의**로 접수.
- 진단 고객 식별: 고객이 **진단·주문 양식 + 진단 안내**를 통째로 복사해 문의에 붙임.

## 고객 여정

1. 자사 HTML 상세 (`GET /product-detail?product_id=<SKU>`)  
   - CTA → **`/pilot?product_id=...&src=html_detail`** (4문항 파일럿)  
   - 템플릿: `docs/demo/product_detail.html`  
   - 쿠팡 연동·테스트: `docs/runbooks/coupang/COUPANG_PILOT_HTML_TEST.md`
2. 진단 완료 → 화면 안내 + CTA  
3. **문의용 양식+진단안내 복사** → 쿠팡 판매자 문의 붙여넣기  
4. **진단 상품 바로 구매하기** → `product_url` (전환 성공 proxy)  
5. **다른 상품 보기** → 전환 실패(이탈) proxy  

주문번호·이름은 쿠팡 문의 스레드에서 확인 (고객 재입력 불필요).

## 복사본 구조

```text
[슈핏케어 진단·주문 양식]
진단번호: SF-xxxxxxxx
...
---
(진단 안내)
(챗봇 결과 본문)
```

- `진단번호`: `session_id` 기반 `SF-` + 8자  
- 코드: `comfort_result_copy.build_coupang_inquiry_copy_text`

## API·로그

| 항목 | 설명 |
|------|------|
| `POST /chat` | `product_id`, `traffic_src` 세션 저장 |
| 응답 필드 | `inquiry_copy_text`, `checkout_payload.product_url` |
| `POST /ops/cta-event` | `cta_copy_inquiry`, `cta_buy_diagnosed`, `cta_browse_other` |
| 로그 | `data/logs/chat_events.jsonl` |

## 운영 KPI (파일럿)

- 진단 완료 수  
- `cta_buy_diagnosed` / `cta_browse_other` / `cta_copy_inquiry`  
- 전환율(의도) = buy / 진단완료  
- 이탈율 = browse_other / 진단완료  

## 관련 코드

- `comfort_result_copy.py` — 양식·복사 텍스트·CTA 라벨  
- `session.py` — Full/Lite 결과에 `inquiry_copy_text` 부착  
- `api.py` — `/demo` CTA 3종, `/ops/cta-event`  
