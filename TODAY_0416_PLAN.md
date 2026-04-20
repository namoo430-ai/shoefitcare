## 4/16 실행 체크리스트

### 완료
- 채널 어댑터 구조 추가 (`adapters/base.py`)
- 네이버 어댑터 추가 (`adapters/naver.py`)
- 카카오 어댑터 추가 (`adapters/kakao.py`)
- FastAPI 웹훅 엔드포인트 추가 (`/webhook/naver`, `/webhook/kakao`)

### 오늘 남은 작업
- 네이버 실제 웹훅 페이로드 샘플 확보 후 `adapters/naver.py` 필드 확정 (완료: `NAVER_WEBHOOK_PAYLOAD.md` 기준 명세화)
- 로컬 E2E 테스트: 신규 세션/기존 세션/빈 메시지 (완료: `scripts/local_e2e_today.py`)
- 운영 로그 필드 확정: `channel`, `shop_id`, `policy_version` (완료: `data/logs/chat_events.jsonl`)

### 내일(4/17) 시작 작업
- 네이버 챗봇 콘솔과 실제 연동 테스트
- 실패 응답(fallback) 문구 및 timeout 대응
- 데모 시나리오 3개 자동 리플레이 스크립트 작성

