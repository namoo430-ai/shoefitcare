# 05. Test Evidence

## Local Preflight

- Purge:
  - `python scripts/purge_local_data.py` 실행 완료
- Compile:
  - `python -m py_compile api.py session.py engine.py storage.py` 통과

## Endpoint Smoke Test (Local)

- `/demo` -> 200
- `/ops/naver-events-summary` -> 200
- `/report` -> 200 (isolated run 기준)
- `/webhook/naver` -> 200 (isolated run 기준)

## Flow Verification

- 상품 먼저 추천받기 -> 스타일 선택 -> 증상 선택 -> 세부 선택 -> 결과 출력
- 실측 경로:
  - `발볼 너비 입력` -> `발길이 입력` -> 다음 단계 진입 확인

## Security Verification

- `.gitignore` 확인:
  - `data/`, `.env*`, `*.db`, `*.log`, key/json secret 패턴 포함
- 코드 스캔:
  - 하드코딩 credential 패턴 미검출(정규식 기반 점검)

