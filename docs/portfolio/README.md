# Portfolio Docs Guide

정부지원사업 제출용 증빙 문서 모음입니다.

## Files

- `01_requirements.md`: 문제정의/목표/범위
- `02_architecture.md`: 시스템 구조/핵심 모듈/데이터 흐름
- `03_dev_log.md`: 일자별 개발 기록
- `04_debug_cases.md`: 디버깅 사례 기록
- `05_test_evidence.md`: 테스트/검증 증빙
- `06_deploy_ops.md`: 배포/운영 이슈 및 조치
- `07_gov_roadmap_2026_2027.md`: 정부지원(2026 혁신 소상공인 AI → 2027 AI 바우처 예상) 확장 로드맵
- `08_milestones_to_july_2026.md`: ~7월 발표 마일스톤
- `09_ideas_backlog.md`: 아이디어 후보 백로그 (미결정)
- `10_decisions.md`: 채택·보류·연기 결정 기록 (ADR 스타일)
- `NOTION_HOME_TEMPLATE.md`: 노션 홈·DB·주간 루틴 복붙 템플릿

## Usage Rules

- 각 항목은 "문제 -> 조치 -> 결과" 순서로 기록
- 커밋 해시와 날짜를 같이 남겨 추적 가능하도록 유지
- 민감정보(개인정보, 키, 토큰, raw payload)는 기록 금지
- 화면 캡처/로그는 경로만 참조하고 원문 노출 최소화

## 운영 루틴 (권장)

- **매주 금요일, 약 15분**: `03_dev_log.md`에 이번 주 작업 **1건** 추가 (날짜, 변경 요약, 관련 커밋 해시, 테스트 여부)
- **이슈가 있었던 주**: `04_debug_cases.md`에 **1건** 추가 (증상 → 원인 → 조치)
- **배포·URL·환경 변경이 있을 때**: `06_deploy_ops.md`에 한 줄이라도 기록
- **새 아이디어가 나왔을 때**: `09_ideas_backlog.md`에 블록 1개 추가
- **채택/보류를 확정했을 때**: `10_decisions.md`에 한 건 추가하고, 필요하면 `09` 항목 상태 갱신

## 금요일 루틴 — 에이전트에 요청할 때 (복붙)

- 짧게: `이번 주 포트폴리오 dev_log 정리해줘.` (+ 한 줄 메모 있으면 덧붙이기)
- 구체적으로: `금요일 루틴으로 docs/portfolio/03_dev_log.md에 이번 주 1건 추가해줘. 이번 주 한 일: …`
- 디버깅 포함: `이번 주 dev_log랑 debug_cases도 docs/portfolio에 반영해줘. 이슈: …`
- 커밋만 있는 주: `이번 주 git 로그 기준으로 dev_log 초안 써줘`
