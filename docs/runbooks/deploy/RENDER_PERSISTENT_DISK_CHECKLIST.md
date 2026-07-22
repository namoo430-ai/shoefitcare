# SQLite + Render Persistent Disk — 추후 적용 체크리스트

**목표:** 재배포·인스턴스 교체 후에도 `pilot_diagnoses`·SF01 집계·정밀 사진이 유지되도록 SQLite 파일을 디스크 볼륨에 둡니다 (외부 Postgres 없음).

**전제:** 웹 서비스 **인스턴스 1개** 유지 (SQLite는 다중 인스턴스 동시 쓰기에 부적합).

---

## A. Render 콘솔

- [ ] 웹 서비스 플랜 확인 (Free만으로 Disk 연결 가능한지 — 불가 시 **Starter + Disk**).
- [ ] **Persistent Disk** 생성 (리전: **Singapore**, 웹 서비스와 동일).
- [ ] 디스크 **마운트 경로** 결정 (예: `/var/data`).
- [ ] 디스크를 `shoefitcare-chatbot` 웹 서비스에 **연결·마운트**.
- [ ] **스케일 / Instance count = 1** 확인 (2 이상이면 SQLite 위험).

---

## B. 환경 변수 (`render.yaml` 또는 Dashboard → Environment)

- [ ] `SHOEFITCARE_DB` = `/var/data/shoefitcare.db` (마운트 경로에 맞게).
- [ ] `SHOEFITCARE_RAG_DIR` = `/var/data/rag_docs` (RAG도 유지할 때).
- [ ] (기존 유지) `ADMIN_TOKEN`, `PYTHON_VERSION` 등.

**참고:** `pilot_storage.py` — 정밀 사진은 DB 파일과 **같은 디렉터리** 아래 `pilot_photos/` (`PILOT_PHOTO_DIR`).

---

## C. 휘발 가능 데이터 (정책 결정)

| 경로 | 용도 | 디스크에 둘지 |
|------|------|----------------|
| `shoefitcare.db` | 파일럿 + core SQLite | **필수** |
| `pilot_photos/` | 정밀 사진 | **권장** (DB와 같은 부모) |
| `data/sessions/` | 톡톡·채팅 세션 (`SessionStore` 기본값) | 선택* |
| `data/logs/` | `chat_events.jsonl` | 선택 |
| `rag_docs/` | RAG JSON | 선택 (`SHOEFITCARE_RAG_DIR`) |

\* 세션은 `api.py`에서 `SessionStore()` 기본 경로 사용 — 디스크에 두려면 추후 `store_dir` env 지원 또는 마운트 전체를 `data`로 맞추는 **추가 작업** 필요. **파일럿 KPI만**이면 DB+사진만 디스크에도 충분.

---

## D. 배포·검증

- [ ] 배포 전 로컬: `python scripts/purge_local_data.py` (민감 데이터 정리).
- [ ] 배포 후 **진단 1건** (`/pilot` 또는 `/n/1`) → Admin 진단 수 **1** 확인.
- [ ] **재배포 1회** (Manual Deploy 등) → Admin 진단 수 **유지** 확인.
- [ ] `GET /api/admin/kpi` → `storage.diagnosis_count`, `db_file_bytes` 확인.
- [ ] (정밀 사용 시) 사진 업로드 → Admin **보기** → 재배포 후에도 유지 확인.

---

## E. 운영·백업

- [ ] 주기적 **DB 파일 백업** (디스크 ≠ 자동 스냅샷).
- [ ] Admin `ephemeral_warning` 문구는 코드 고정 — 디스크 적용 후에도 **0건일 때** 안내가 남을 수 있음 (필요 시 추후 문구 조정).
- [ ] 이 체크리스트 완료 후 [DEPLOY_RENDER.md](./DEPLOY_RENDER.md) 참고 섹션과 env 예시 일치 여부 확인.

---

## F. 이번 범위에서 하지 않는 것

- [ ] Postgres 마이그레이션 — **하지 않음**.
- [ ] 인스턴스 2대 스케일 아웃 — **하지 않음** (SQLite 유지 시).

---

## G. 완료 기준

- 재배포 후 **진단번호·SF 집계·(업로드한) 사진**이 Admin에서 이전과 동일하게 보인다.
- 팀이 **실제 데이터는 디스크에 영속**됨을 확인했다.

---

**관련:** `render.yaml` (`SHOEFITCARE_DB`), `pilot_storage.py`, `storage.py`, [DEPLOY_RENDER.md](./DEPLOY_RENDER.md).
