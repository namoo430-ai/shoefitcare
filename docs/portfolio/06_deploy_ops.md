# 06. Deploy & Ops Notes

## Deploy Target

- Service: Render `shoefitcare`
- Demo URL (target): `https://shoefitcare.onrender.com/demo`

## Known Operational Notes

- `/demo` 404 발생 시:
  - 원인 대부분 최신 커밋 미배포
  - 조치: Render `Deploy latest commit` 후 재확인

- Naver 연동 이슈:
  - 서버 로직과 채널 라우팅 이슈를 분리 진단 필요
  - 운영 요약 API(`/ops/naver-events-summary`)로 이벤트 추적

## Submission-safe Checklist

1. 로컬 민감데이터 purge
2. 핵심 파일 compile 성공
3. 문서 3종 확인
4. 배포 URL 검증(`/demo`, `/report`, webhook)
5. 제출 자료에는 고정 URL만 사용(임시 터널 제외)

