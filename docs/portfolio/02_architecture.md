# 02. Architecture

## High-level Structure

1. `api.py`
   - FastAPI 엔드포인트(`/chat`, `/webhook/naver`, `/demo`, `/report`)
   - 채널 어댑터 연계 및 운영 요약 API 제공
2. `session.py`
   - 상태머신 기반 대화 제어
   - 입력 검증, 질문 흐름, 결과 메시지 포맷
3. `hybrid_recommender.py`
   - CSV 데이터 로드
   - 후보 필터/랭킹/설명 생성
4. `engine.py`
   - 진단 로직 및 점수 계산의 코어 정책
5. `storage.py`
   - 입력/결과 저장 및 리포팅 연계

## Data Flow

1. 사용자 입력 수신
2. 상태머신에서 단계별 파싱/검증
3. 추천엔진 스코어링 및 TOP-N 생성
4. 설명 문구 생성 및 응답 반환
5. 이벤트/진단 결과 저장 (운영 요약용)

## Current Design Principles

- 결정(진단/추천)과 설명(LLM/RAG)을 분리
- 공통 엔진을 유지하고 정책 레이어로 확장
- 민감정보 최소 저장/마스킹 우선

