# 정밀 진단 발 모양 사진 — 업로드 주력 + 문자 보조

## 목표

- 고객: pilot 정밀 폼에서 **사진 업로드가 기본 경로**
- 보조: 업로드가 어려우면 **010-8931-6325** 문자·카카오 (기존 안내 유지)
- 운영: admin에서 **앱 업로드 건수·비율** 자동 집계, 일별 문자 수신은 **수기 보조**

## 고객 흐름

```
간편 진단 완료
  → 정밀 폼 (치수 · 연락처 · 동의)
  → [권장] 사진 선택/촬영 (미리보기)
  → 「정확하게 진단받기」
       ① POST /pilot/precision (JSON)
       ② (사진 있으면) POST /pilot/precision-photo (multipart)
  → 접수 완료 화면 (업로드 여부에 따라 문구 분기)
```

사진 없이 제출 가능 → 문자 보조 경로. 퍼널에서 `precision_completed` vs `photo_storage_key` 로 앱 업로드율 측정.

## API (FastAPI)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/pilot/precision` | 기존 치수·연락처 (JSON) |
| POST | `/pilot/precision-photo` | `Form: diagnosis_id`, `File: photo` |
| GET | `/api/admin/diagnoses/{id}/photo` | 관리자만 원본 조회 (`X-Admin-Token` 또는 `?token=`) |

### `/pilot/precision-photo` 검증

- `precision_completed = 1` 인 진단만
- MIME: `image/jpeg`, `image/png`, `image/webp`
- 최대 5MB
- 저장: `data/pilot_photos/{diagnosis_id}.jpg` (로컬, `data/`는 gitignore)

## DB

`pilot_diagnoses` 컬럼 추가 (마이그레이션):

- `photo_storage_key` — 저장 파일명
- `photo_uploaded_at` — ISO 시각

## 퍼널·admin

- 이벤트: `precision_photo_uploaded` (업로드 성공 시)
- KPI: `precision_photo_app_uploads`, `photo_app_after_precision_pct`
- admin 진단 목록: 사진 Y/N, 썸네일 링크
- ③ 일별 문자 수신: 기존 유지 (앱 외 경로 보조)

## 보안·운영

- 응답에 사진 URL 공개하지 않음
- purge 시 `data/pilot_photos/` 삭제 정책은 `data_retention_admin` 확장 시 반영
- Render 배포: 디스크 휘발성 → 추후 S3/R2 이전 권장

## 난이도 (요약)

| 구간 | 난이도 | 비고 |
|------|--------|------|
| pilot UI 파일 input + 2단계 POST | ★★☆ | 일반 웹 |
| FastAPI `UploadFile` + Form | ★★☆ | 공식 패턴 |
| 로컬 파일 저장 + DB 연결 | ★★☆ | MVP |
| admin 사진 조회·권한 | ★★☆ | 토큰 |
| Render 영구 스토리지 | ★★★★ | 별도 객체 스토리지 필요 |

전체 MVP: **중하~중 (2~3일)** — S3·리사이즈·바이러스 스캔 제외.
