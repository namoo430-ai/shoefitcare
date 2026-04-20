## Naver Webhook Payload (현재 구현 기준)

현재 `adapters/naver.py`는 네이버 연동 초기 단계에서 여러 키 형태를 허용합니다.
실제 콘솔 스펙 확정 후 아래 필드 중 사용하는 키를 고정하면 됩니다.

### Inbound 허용 필드

- 사용자 ID:
  - `user.id`
  - `user_id`
  - `senderId`
- 메시지 텍스트:
  - `text`
  - `message`
  - `event.text`
  - `event.utterance`
- 세션 키:
  - `session.id`
  - `session_id`
  - `conversationId`
  - 없으면 `user_id` fallback
- 운영 메타:
  - `shop_id` (없으면 `default_shop`)
  - `policy_version` (없으면 `v1`)

### 권장 요청 예시

```json
{
  "user": { "id": "nv_user_001" },
  "session": { "id": "nv_session_001" },
  "event": { "utterance": "3" },
  "shop_id": "naver_shop_001",
  "policy_version": "v1"
}
```

### Outbound 응답 형식

```json
{
  "text": "응답 텍스트",
  "quickReplies": [
    { "label": "1", "text": "1" }
  ],
  "done": false,
  "diagnosis": null,
  "session_id": "nv_session_001"
}
```

