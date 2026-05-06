# 01. Requirements

## Project Summary

- 프로젝트명: Shoefitcare MVP
- 목표: 발볼/핏 진단 기반 신발 추천 챗봇 구현
- 채널: Web(FastAPI demo), Naver TalkTalk webhook 연동

## Problem Definition

- 기존 온라인 구매 과정에서 사이즈/핏 불일치로 인한 교환/반품이 반복됨
- 상담 노하우가 담당자 의존적이라 응대 일관성이 떨어짐
- 사용자는 "왜 이 상품이 맞는지" 설명 부족으로 구매 확신이 낮음

## Scope (Current)

- 고객 입력 기반 진단 상태머신 (`session.py`)
- 하이브리드 추천엔진 + CSV 데이터 기반 후보/스코어링
- 결과 설명 UX 개선 (모바일 친화 출력)
- `/demo` 시연용 프론트 제공

## Scope (Planned)

- 디자인별 핏 정책 레이어 추가 (공통 엔진 + 디자인 보정)
- 피드백 데이터 기반 반자동 튜닝
- 타 브랜드 매핑/교차 추천(후속 단계)

는는