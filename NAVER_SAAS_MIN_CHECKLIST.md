# NAVER 연동 최소 구현 체크리스트

목표: 톡톡 자동응답과 우리 진단 백엔드를 함께 써서, 운영 효율과 SaaS 데이터 축적을 동시에 달성한다.

## 1) 일정 기준 최소 범위 (이번 스프린트)

- Day 1: 톡톡 절차형 문의 자동응답(자동종결) + 진단형 문의 기존 세션 연결
- Day 2: 자동종결/추가질문/상담전환 이벤트 로깅 점검, 저장 데이터 필드 확인
- Day 3: 샘플 대화 20건 리플레이, 오분류 문구 보정

## 2) 필수 연동 항목 (Release Minimum)

- [ ] `/webhook/naver`로 톡톡 메시지가 유입된다.
- [ ] 세션 키 기준으로 `SessionStore` 저장/복구가 동작한다.
- [ ] 절차형 문의는 챗봇 템플릿으로 즉시 응답(자동종결)한다.
- [ ] 개인 맞춤 문의는 `ConversationController`로 전달되어 진단 플로우를 탄다.
- [ ] 이벤트 로그는 원문 대신 해시/길이만 기록한다.
- [ ] DB에 고객 입력/진단 결과가 저장된다.
- [ ] RAG 문서가 생성되고 `shop_id`, `policy_version` 메타를 가진다.

## 3) 자동응답/진단 분기 기준

- 자동종결(절차형): 신청, 방법, 옵션, 주문, 선택, 어떻게
- 진단연결(개인화형): 넓은데, 괜찮나요, 무지외반, 꽉, 헐떡, 통증
- 상담전환 후보: 심한 통증, 모순 답변, 특수 케이스

## 4) 저장 데이터 최소 스키마 체크

- 세션: `session_id`, `channel`, `shop_id`, `policy_version`, 상태
- 입력: `design`, `original_size`, `foot_issues`, `fit_experience`
- 결과: `recommended_product`, `final_size`, `stretch_step`, `is_consult`
- 로그: `event`, `session_id`, `channel`, `shop_id`, `policy_version`, `message_hash`, `message_len`

## 5) 운영 전 확인

- [ ] `.gitignore`에 데이터/로그/DB/비밀파일 제외 규칙 유지
- [ ] `python scripts/purge_local_data.py` 실행
- [ ] `python -m py_compile api.py session.py engine.py storage.py` 통과
- [ ] 테스트 페이로드로 `/webhook/naver` 왕복 확인

