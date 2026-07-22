## Render 무료 배포 가이드

### 1) 준비
- 현재 프로젝트를 GitHub 저장소로 올립니다.
- Render 계정을 생성/로그인합니다.

### 2) 배포
- Render Dashboard -> New -> Blueprint 선택
- GitHub 저장소 연결 후 배포
- 루트의 `render.yaml`을 읽어 자동으로 웹 서비스 생성

### 3) 완료 후 확인
- 배포 완료 시 Render가 도메인을 발급합니다.
  - 예: `https://shoefitcare-chatbot.onrender.com`
- 아래 URL로 상태 확인:
  - `GET /report`
  - 예: `https://shoefitcare-chatbot.onrender.com/report`

### 4) 네이버 콘솔 Webhook URL
- 네이버 콘솔에 아래 URL 등록:
  - `https://<render-domain>/webhook/naver`

### 5) 테스트 payload 예시
```json
{
  "user": { "id": "nv_user_demo" },
  "session": { "id": "nv_sess_demo" },
  "event": { "utterance": "2" },
  "shop_id": "naver_shop_demo",
  "policy_version": "v1"
}
```

### 참고
- Render free 플랜은 유휴 시 슬립이 발생할 수 있습니다. `/admin` 첫 로딩이 느리면 30~60초 후 새로고침.
- 루트 `/` 는 **파일럿(`/pilot`)** 으로 리다이렉트됩니다. 관리자는 **`/admin?token=...`** 북마크를 사용하세요.
- **파일럿 진단·SF01 집계**는 `data/shoefitcare.db`(SQLite)에 저장됩니다. **재배포·디스크 없는 인스턴스**에서는 DB가 비워져 집계가 0으로 돌아갈 수 있습니다. 운영 KPI 유지가 필요하면 Render **Persistent Disk** 마운트 또는 외부 DB를 검토하세요. SQLite + Disk 적용 절차: [RENDER_PERSISTENT_DISK_CHECKLIST.md](./RENDER_PERSISTENT_DISK_CHECKLIST.md).
- 발표 데모 전에는 한 번 호출해 워밍업해두는 것을 권장합니다.

