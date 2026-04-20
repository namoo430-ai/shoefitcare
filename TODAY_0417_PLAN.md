## 4/17 실행 체크리스트

### 완료
- API timeout/fallback 보호 로직 반영 (`api.py`)
- 에러/타임아웃 운영 로그 이벤트 반영 (`data/logs/chat_events.jsonl`)
- 데모 자동 리플레이 3시나리오 추가 (`scripts/demo_replay_3cases.py`)
- 네이버 콘솔 실연동 체크리스트 작성 (`NAVER_CONSOLE_0417_CHECKLIST.md`)

### 사용 커맨드
- `python scripts/demo_replay_3cases.py`
- `uvicorn api:app --reload`

### 실연동 시 확인
- 콘솔 webhook URL 및 payload 키 매핑
- shop/policy 메타 반영 여부
- fallback/timeout 문구 동작 여부

