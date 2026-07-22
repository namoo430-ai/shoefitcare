# 네이버 파일럿 · 테스트 체크리스트

갱신: **2026-06-19** · 빌드: `pilot_ui.PILOT_BUILD` · 룰: `pilot_engine.PILOT_RULE_VERSION` (`20260619-sf04-loose-copy` 이상)

로드맵: [PILOT_UX_ROADMAP.md](../../plans/PILOT_UX_ROADMAP.md)

## 전날 밤 (5분)

```powershell
cd c:\DongaAI\project02\mvp_v1
.\scripts\start_pilot_local.ps1
```

또는 더블클릭: `START_PILOT_LOCAL.cmd`  
상세·트러블슈팅: [PILOT_LOCAL_START.md](./PILOT_LOCAL_START.md)

다른 터미널:

```powershell
python scripts/preflight_naver_test_day.py
```

`OK` 가 모두 나오면 로컬 준비 완료.  
휴대폰까지 보려면 Windows 방화벽에서 **8001 인바운드 허용** (같은 Wi‑Fi).

Render로 CS 링크 테스트 시: 최신 코드 **배포 후** 아래 스모크.

```powershell
$env:SMOKE_BASE_URL="https://shoefitcare-chatbot.onrender.com"
python scripts/smoke_naver_detail_link.py
```

배포 절차: [DEPLOY_RENDER.md](../deploy/DEPLOY_RENDER.md) · 디스크: [RENDER_PERSISTENT_DISK_CHECKLIST.md](../deploy/RENDER_PERSISTENT_DISK_CHECKLIST.md)

## 테스트 당일 URL

| 용도 | URL |
|------|-----|
| PC 로컬 (짧은 링크) | http://127.0.0.1:8001/n/1 |
| PC 로컬 (직접) | http://127.0.0.1:8001/pilot?src=naver&product_id=SR266 |
| 휴대폰 (LAN) | `preflight_naver_test_day.py` 출력의 `http://<PC IP>:8001/n/1` |
| 운영 CS 링크 | https://shoefitcare-chatbot.onrender.com/n/1 |

`src` 는 짧은 링크 시 `naver_sms`, 쿼리 `src=naver` 도 동일 UX.

## 고객 플로우 (10분)

1. 링크 열기 → **「발 편안 지도 만들기」** 첫 화면 (빈 화면이면 **Ctrl+Shift+R** 또는 서버 재시작).
2. Q1~Q4 완료 → **「발 편안 지도가 완성됐어요」** + 지도 + 핏 3줄 + 주문 팁.
3. **1회 교환 인증 문구 받기** 복사 (SF00·이벤트 OFF 제외).
4. 하단 **톡톡문의** → 시트 → 한 줄 복사 → **톡톡 열기** (`talk.naver.com/ct/wc82wv`, 로그인).
5. **핏별상품** · **정밀진단** 탭: URL/조건 미충족 시 비활성 — 정상.

### SF04 (헐거운 편) — 1차 범위

- Q1 「대부분 신발이 여유 있는 편」→ **SF04**
- 안내에 **길이 때문에 크게 신어 헐거움** 가정 · **앞깔창** 톡톡 안내 문구 확인
- **SF05·정밀 완료·칼발 라벨**은 1차 성공 기준 **제외** (2차)

## 판매자·운영 (5분)

| 항목 | URL |
|------|-----|
| Admin KPI | `/admin?token=<ADMIN_TOKEN>` |
| 빠른 답변 | `/seller/quick?token=<ADMIN_TOKEN>` |

진단번호 → 핏 선택 → 짧은/긴/교환 문구 복사 → 톡톡 회신 연습.

## 설정 (테스트 전에 채우면 좋음)

`config/naver_pilot_store_links.json`

- `talktalk_url` — **설정됨** (wc82wv)
- `fit_category_urls` — 비어 있으면 핏별상품 탭만 꺼짐

`config/naver_pilot_products.json` (SR266)

- `return_url` — 스마트스토어 상품 URL 넣고 재시작 → 결과 하단 「스마트스토어에서 주문하기」
- `stretch_on_option: true` — 실제 옵션 있을 때만

JSON 수정 후 **uvicorn 재시작** (`pilot_store_links` 캐시).

## 상세 페이지 (스마트스토어)

붙여넣기 HTML: `docs/demo/naver_SR266_detail_paste.html`  
(외부 링크 없음 → 톡톡으로 `/n/1` 안내)

## 문제 해결

| 증상 | 조치 |
|------|------|
| 빈 화면 | `/health/build` 의 `pilot_build` 확인 · `python scripts/check_pilot_page.py` |
| 결과만 안 나옴 | F12 콘솔 오류 · 네트워크 `POST /pilot/diagnose` 200 여부 |
| Render 느림 | 30~60초 대기 후 새로고침 (슬립) |
| 집계 0 | Persistent Disk 미적용 시 재배포 후 DB 초기화 가능 |

## 관련 문서

- [NAVER_PILOT_HTML_TEST.md](./NAVER_PILOT_HTML_TEST.md)
- [NAVER_COMFORT_MAP_UX.md](../../plans/NAVER_COMFORT_MAP_UX.md)
- [NAVER_PILOT_PRODUCTS.md](./NAVER_PILOT_PRODUCTS.md)
