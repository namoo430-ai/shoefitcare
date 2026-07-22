# 파일럿 로컬 서버 (내일 재시작용)

갱신: **2026-06-20** · 포트 **8001** · 빌드 예: `20260620-foot-intro-compare-c23`

## 1) 서버 켜기 (권장)

**PowerShell** — 프로젝트 루트에서:

```powershell
cd c:\DongaAI\project02\mvp_v1
.\scripts\start_pilot_local.ps1
```

창을 **닫지 마세요.** `Uvicorn running on http://127.0.0.1:8001` 이 보이면 OK.

또는 수동:

```powershell
cd c:\DongaAI\project02\mvp_v1
python -m uvicorn api:app --reload --host 127.0.0.1 --port 8001
```

## 2) 브라우저

| 용도 | URL |
|------|-----|
| 네이버 SMS 링크와 동일 | http://127.0.0.1:8001/pilot?product_id=SR266&src=naver_sms |
| 짧은 링크 | http://127.0.0.1:8001/n/1 |
| 빌드 확인 | http://127.0.0.1:8001/health/build |

**인트로(5종 발형)** 는 페이지를 **새로 열 때마다** 표시됩니다. 생략: `?nointro=1`

## 3) 동작 확인 (다른 터미널)

```powershell
cd c:\DongaAI\project02\mvp_v1
python scripts/preflight_naver_test_day.py
```

`pilot_build` 가 `health/build` 와 같으면 최신 UI 로드 중입니다.

## 4) `ERR_CONNECTION_REFUSED` 일 때

1. 8001 서버가 **꺼져 있음** → 위 1) 다시 실행  
2. 예전 uvicorn **좀비** → `start_pilot_local.ps1` 이 포트 정리 후 기동  
3. Cursor 내장 브라우저만 실패 시 → Chrome/Edge에서 같은 URL 직접 열기  

## 5) 오늘 반영된 UX (요약)

- **인트로**: 보통발→칼발 순환 애니 (약 1.4초) · 큰 이미지  
- **결과**: 기준 발 vs 고객 발 **2단 비교** (`foot_compare`)  
- 상세: `docs/plans/PILOT_RESULT_FOOT_COMPARE.md`

## 6) 끌 때

서버 터미널에서 `Ctrl+C` 한 번 (reload 자식까지 종료될 때까지 1~2초).
