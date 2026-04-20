## 4/17 네이버 콘솔 실연동 체크리스트

- [ ] 네이버 챗봇 콘솔 Webhook URL 등록: `https://<domain>/webhook/naver`
- [ ] 테스트 payload에 `shop_id`, `policy_version` 포함 확인
- [ ] 빈 발화(또는 텍스트 누락) 시 초기 안내가 정상 반환되는지 확인
- [ ] 응답 지연 시 fallback 문구 반환 확인
- [ ] 오류 발생 시 재입력 안내 문구 반환 확인
- [ ] 로그 파일 `data/logs/chat_events.jsonl`에 이벤트 기록 확인
- [ ] `GET /report?shop_id=<id>&policy_version=v1` 집계 확인

## 테스트 요청 예시

```json
{
  "user": {"id": "nv_user_demo"},
  "session": {"id": "nv_sess_demo"},
  "event": {"utterance": "2"},
  "shop_id": "naver_shop_demo",
  "policy_version": "v1"
}
```

## 성공 기준

- 네이버 콘솔에서 3턴 이상 대화가 끊기지 않고 이어짐
- 결과 응답에 `session_id`가 유지됨
- 로그에 `naver_webhook` 이벤트가 누락 없이 기록됨

