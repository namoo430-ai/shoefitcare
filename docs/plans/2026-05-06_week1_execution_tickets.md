# Week 1 Execution Tickets (2026-05-06 기준)

프로젝트 이후 방향을 잃지 않기 위한 "이번 주 실행 티켓 3개"입니다.
원칙은 "새 기능보다 기준선 안정화 -> 작게 개선 -> 기록 고정"입니다.

## Ticket 1. 기준선 스모크 + 증빙 고정

- 목표: 지금 동작하는 핵심 사용자 흐름 3개를 고정하고, 이후 변경 시 회귀를 빠르게 찾는다.
- 작업:
  - `python scripts/purge_local_data.py`
  - `python -m py_compile api.py session.py engine.py storage.py`
  - `/demo`, `/ops/naver-events-summary`, `/report`, `/webhook/naver` 응답 확인
  - 핵심 흐름 3개 수동 검증:
    - 상품 먼저 추천받기 -> 스타일 -> 증상 -> 세부 -> 결과
    - 실측 경로(발볼 -> 발길이) 정상 진입
    - 재질문/복구 흐름 1회 확인
- 완료조건(DoD):
  - `docs/portfolio/05_test_evidence.md`에 실행 날짜와 결과 추가
  - 실패 케이스가 있으면 `docs/portfolio/04_debug_cases.md`에 1건 등록
- 예상시간: 1.5h

## Ticket 2. NLP 하이브리드 보강 설계 (코딩 전 설계 티켓)

- 목표: 자유입력 처리 정확도를 높이되, 기존 `session` 안정성을 유지한다.
- 작업:
  - 입력/출력 계약서 초안 작성:
    - 입력: user_text, state, expected_options
    - 출력: intent, symptom_entities, confidence
  - fallback 규칙 정의:
    - confidence 임계치 미만이면 기존 재질문 흐름으로 복귀
  - 룰 파서와 충돌 시 우선순위 규칙 문서화
- 완료조건(DoD):
  - `docs/plans/2026-05-06_huggingface_ideas_meeting.md`에 "NLP 구현 규칙" 섹션 추가
  - `docs/portfolio/10_decisions.md`에 임계치/fallback 정책 결정 1건 업데이트(또는 ADR 추가)
- 예상시간: 2h

## Ticket 3. 백로그 슬림화 + 이번 달 1건 확정

- 목표: 아이디어 과밀 상태를 줄이고, 실제 실행 1건만 확정한다.
- 작업:
  - `docs/portfolio/09_ideas_backlog.md`에서 상태를 `이번 달`, `다음 달`, `보류`로 재분류
  - 이번 달 실행 1건(권장: NLP 하이브리드) 확정
  - 결정 사유(왜 지금 이걸 하는지) 3줄 기록
- 완료조건(DoD):
  - `09_ideas_backlog.md` 인덱스 상태가 최신화됨
  - `10_decisions.md`에 채택/보류 근거가 반영됨
- 예상시간: 0.5h

---

## 이번 주 실행 순서

1. Ticket 1 (안정화)
2. Ticket 3 (우선순위 확정)
3. Ticket 2 (설계 고정 후 구현 시작)

총 예상: 약 4h

## 메모

- 코어 추천 엔진은 유지하고, HF/NLP/CV는 보조 레이어로만 단계 도입
- 외부 API 경로는 항상 timeout + fallback 유지
