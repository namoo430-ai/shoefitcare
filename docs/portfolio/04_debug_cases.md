# 04. Debug Cases

## Case 1 - Naver webhook event not counted

- Symptom:
  - `/ops/naver-events-summary`에서 이벤트 증가 없음
- Hypothesis:
  - webhook URL/이벤트 설정 불일치 또는 배포 코드 불일치
- Action:
  - Render 배포 버전 재확인
  - webhook URL/메서드/이벤트 항목 재점검
  - 서버 직접 호출로 채널 문제와 서버 문제 분리
- Result:
  - 서버 로직 정상 확인, 채널 라우팅/운영 설정 이슈로 분류

## Case 2 - `/demo` route shows 404 on Render

- Symptom:
  - `https://shoefitcare.onrender.com/demo` -> 404
- Hypothesis:
  - 최신 커밋 미배포
- Action:
  - Render endpoint 상태 비교(`/report` 200, `/demo` 404)
  - 최신 커밋 배포 필요성 확인
- Result:
  - 배포 버전과 로컬 코드 차이로 원인 확정

## Case 3 - Demo UI progression confusion

- Symptom:
  - "빠른 시작"과 "증상 선택"이 항상 보여 단계 혼선
- Hypothesis:
  - 상태 비연동 패널 고정 노출
- Action:
  - 상태별 패널 가시성 제어(Q_ENTRY only, Q_FOOT only)
  - 기존 quick reply 노출 제거/숨김
- Result:
  - 단계 맥락에 맞는 UI로 정리

## Case 4 - JS syntax error stopped demo behavior

- Symptom:
  - 버튼 클릭 시 응답 진행 없음
- Root Cause:
  - 이벤트 핸들러 종료 구문 오류(`});` vs `};`)
- Action:
  - 스크립트 문법 수정 및 상태 배지 추가
- Result:
  - 초기화/버튼 동작 정상화

