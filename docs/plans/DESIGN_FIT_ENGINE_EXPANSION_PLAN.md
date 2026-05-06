# Design-Fit Engine Expansion Plan

## Goal

현재 추천엔진의 뼈대는 유지하면서, 핏 적합도 기준을 디자인별로 정교화한다.

- 공통 엔진 유지: 입력 수집 -> 후보 필터 -> 점수화 -> TOP-N 추천 -> 설명 생성
- 디자인별 기준 추가: 구두/로퍼/단화/운동화 별 가중치와 리스크 보정
- 타브랜드 매핑은 후속 단계로 분리 (이번 범위 제외)

---

## 1) Target Architecture

### 1.1 Common Core (공통)

모든 디자인에 공통 적용되는 코어 점수 축:

- `fit_base`: 발볼/무지외반/발등/앞코 증상 적합도
- `size_base`: 사이즈 일치/인접도
- `risk_base`: 반품 리스크, 과도한 늘림 리스크
- `preference_base`: 선호 스타일, 최근 착화 경험 일치

최종 점수 기본식:

`score = fit_base + size_base + preference_base - risk_base`

### 1.2 Design Adapter (디자인별 어댑터)

공통 점수에 디자인별 보정치를 더한다.

`final_score = score + design_bonus - design_penalty`

디자인별 보정 항목은 별도 정책 테이블에서 로드한다.

---

## 2) Design-specific Criteria

### 2.1 구두 (Pumps/Heels)

- 민감도 상향:
  - 앞코 압박
  - 발볼 압박
  - 힐 슬립(헐떡임)
- 리스크 패널티:
  - 사이즈 업에 따른 뒤꿈치 유격 리스크
  - 무지외반 + 좁은 토박스 조합

### 2.2 로퍼 (Loafers)

- 민감도 상향:
  - 발등 볼륨 여유
  - 뒤꿈치 고정감
- 리스크 패널티:
  - 발등 높음 + 발등 낮은 패턴 조합

### 2.3 단화 (Flats)

- 민감도 상향:
  - 전족부(앞코/발볼) 여유
  - 장시간 착화 시 압박 누적
- 리스크 패널티:
  - 쿠션 부족 + 통증 민감 조합

### 2.4 운동화 (Sneakers)

- 민감도 상향:
  - 발볼 여유
  - 보행 안정감/쿠션감
- 리스크 패널티:
  - 발등 압박, 끈/갑피 조절 불가 조합

---

## 3) Policy Data Model (초안)

### 3.1 디자인 정책 테이블

`design_fit_policy.csv` (또는 DB 테이블)

- `design`: 구두|로퍼|단화|운동화
- `w_fit_wide`
- `w_fit_hallux`
- `w_fit_instep`
- `w_fit_toe`
- `w_heel_slip_penalty`
- `w_return_risk_penalty`
- `w_stretch_risk_penalty`
- `updated_at`

### 3.2 제품 메타 확장

제품 데이터에 다음 속성 추가 권장:

- `toe_box_type` (narrow/regular/wide)
- `instep_volume` (low/normal/high)
- `heel_grip_level` (1~3)
- `cushion_level` (1~3)

---

## 4) Engine Integration Plan

### Phase 1 (즉시)

- 공통 엔진 함수는 유지
- 디자인별 가중치 로딩 계층 추가
- 최종 점수 계산에 `design_bonus/penalty` 반영

### Phase 2 (안정화)

- 반품/교환 결과 기반 디자인별 패널티 자동 보정
- 주요 케이스(무지외반/발등 높음/헐떡임) 회귀 테스트셋 추가

### Phase 3 (후속)

- 타브랜드 핏 매핑 레이어 도입
- 교차 브랜드 추천과 발볼늘림 단계 권장으로 확장

---

## 5) Acceptance Criteria

- 동일 입력에 대해 결과 재현성 유지
- 디자인 변경 시 추천 결과가 정책 의도대로 변화
- 위험 조합(압박/헐떡임)에서 패널티 반영 확인
- 추천 설명에 디자인별 선택 근거가 노출됨

---

## 6) Demo-ready Message (발표용 한 줄)

"엔진의 뼈대는 공통으로 유지하고, 디자인별 핏 민감도를 정책 레이어로 분리해 정확도와 운영성을 동시에 확보했습니다."

