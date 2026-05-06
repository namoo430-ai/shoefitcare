# 03. Development Log

## 2026-04-28

- Commit: `b581524`
- Title: Refine demo flow for guided input and sharing
- Changes:
  - `/demo` 시연 UI 추가 및 상태 연동 UX 개선
  - 복수 증상 선택/세부 단계 버튼/단일 전송 로직 적용
  - 실측 입력을 단계형(`발볼 -> 발길이`)으로 전환
  - 공유 URL 실행 배치 파일(`open_demo_url.bat`) 추가
- Result:
  - 시연 동선 단순화, 발표용 사용성 향상

## 2026-04-26

- Commit: `83a25e4`
- Title: Refine chatbot UX copy and simplify recommendation result messaging
- Changes:
  - 고객 노출 문구 정리 및 관리자성 문구 제거
  - 추천 이유의 중복 표현 축소 및 모바일 가독성 개선
- Result:
  - 사용자 이해도 및 대화 친화성 개선

## 2026-04-25

- Commit: `542a787`, `67071f2`
- Title: Hybrid CSV recommender integration and validation
- Changes:
  - CSV 기반 추천 데이터 로딩/정규화/스코어링 강화
  - 추천 점수 가시화 및 로컬 검증 스크립트 정리
- Result:
  - 룰 기반 정확도 유지 + 운영 튜닝 가능성 확보

## 2026-04-22 ~ 2026-04-21

- Commit: `1bdd432`, `a1de513`, `8a34342`, `8c5eb0f`, `03c1415`, `72056e7`
- Title: Naver webhook integration stability improvements
- Changes:
  - 버튼 code 정규화, AI 진입 처리, 중복 응답 방지
  - webhook payload/스키마 대응 강화
- Result:
  - 서버측 연동 안정성 개선, 운영 디버깅 근거 확보

## 2026-04-20

- Commit: `4512df5`
- Title: Initialize Shoefitcare MVP backend and webhook integration
- Changes:
  - FastAPI 백엔드 및 webhook 초기 구조 구축
- Result:
  - MVP 개발 베이스라인 확립

