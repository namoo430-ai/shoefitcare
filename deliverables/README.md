# Deliverables

발표 자료·제출 패키지·아카이브를 한곳에 모아 둡니다. 앱 코드(`api.py`, `core/` 등)와 분리합니다.

| 폴더 | 용도 |
|------|------|
| `presentations/` | PPT/PDF, 슬라이드별 발표 멘트 등 |
| `submission/` | 시연 URL 안내, 배치 파일, 제출용 PDF 등 |
| `archives/` | 과거 제출용 ZIP 등 (중복 보관 시) |

PPT를 다시 생성할 때는 저장소 루트에서:

- `python scripts/generate_project_ppt.py` → `presentations/슈핏케어_프로젝트_발표자료.pptx`
- `python scripts/generate_ppt_versions.py` → `presentations/` 아래 5분·10분 버전
