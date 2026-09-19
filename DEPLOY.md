# 배포 절차

GitHub → Render(백엔드) → Vercel(프론트엔드) 순서로 진행합니다.
두 배포 주소가 서로를 가리켜야 하므로, **마지막 5단계까지 끝내야 연동이 완성됩니다.**

---

## 1. GitHub에 올리기

이미 `my-page` 저장소가 있으므로 커밋하고 push 하면 됩니다.

```bash
git add .
git commit -m "개인 소개 페이지에 방명록 API 연동 추가"
git push
```

**확인** — GitHub 저장소에 `backend/` 폴더와 `guestbook.html` 이 보이고,
`backend/.venv/` 와 `backend/guestbook.db` 는 **없다**(`.gitignore` 가 막았다).

---

## 2. Render에 백엔드 배포

[render.com](https://render.com) 로그인 → **New → Web Service** → `my-page` 저장소 선택.

| 항목 | 값 |
|---|---|
| Name | `my-page-api` (원하는 이름 — 인터넷 주소의 앞부분이 된다) |
| Language | **Python 3** |
| **Root Directory** | **`backend`** ← 이 저장소는 백엔드가 하위 폴더에 있으므로 반드시 지정 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Compute plan | **Free** |
| Environment Variables | `ALLOWED_ORIGINS` = `*` (5단계에서 Vercel 주소로 바꾼다) |

**Deploy Web Service** 를 누릅니다.

- `--host 0.0.0.0` 이 없으면 외부에서 접근이 안 됩니다.
- `--port $PORT` 를 `8000` 같은 숫자로 고정하면 **502** 가 납니다.
- Root Directory 를 비워 두면 `Error loading ASGI app. Could not import module "main"` 이 납니다.

**확인** — 상태가 **Live** 가 되고 `https://<서비스>.onrender.com` 주소가 생깁니다.
브라우저로 `https://<서비스>.onrender.com/docs` 를 열면 Swagger UI 가 뜹니다.
**→ 이 주소가 제출할 「백엔드 Swagger UI 주소」입니다.**

> 첫 접속이 30~60초 느린 것은 무료 플랜의 콜드 스타트라 정상입니다.

---

## 3. 프론트엔드에 백엔드 주소 알려주기

`config.js` 를 열어 2단계에서 받은 Render 주소로 바꿉니다(**끝에 `/` 없이**).

```js
window.API_BASE_URL = "https://my-page-api.onrender.com";
```

```bash
git add config.js
git commit -m "백엔드 API 주소 설정"
git push
```

---

## 4. Vercel에 프론트엔드 배포

[vercel.com](https://vercel.com) 을 GitHub 계정으로 로그인 → **Add New → Project** → `my-page` 저장소 **Import**.

| 항목 | 값 |
|---|---|
| Framework Preset | **Other** (정적 HTML 이므로 빌드가 필요 없다) |
| Root Directory | `./` (그대로) |
| Build Command · Output Directory | 비워 둔다 |

**Deploy** 를 누릅니다.

**확인** — `https://<프로젝트>.vercel.app` 주소가 생기고 개인 소개 페이지가 뜹니다.
상단 링크로 `/guestbook.html` 에 들어가집니다.
**→ 이 주소가 제출할 「Vercel 배포 페이지 주소」입니다.**

이 시점에는 방명록이 아직 **연결 실패** 로 보일 수 있습니다 — 5단계가 남았기 때문입니다.

---

## 5. 백엔드에 Vercel 주소 허용시키기 (연동 완성)

Render 대시보드 → 해당 서비스 → **Environment** →
`ALLOWED_ORIGINS` 값을 4단계에서 받은 Vercel 주소로 바꿉니다.

```
https://<프로젝트>.vercel.app
```

- **끝에 `/` 를 붙이지 않습니다.**
- 주소가 여러 개면 쉼표로 이어 씁니다.

저장하면 Render 가 자동으로 재배포합니다. 상태가 다시 **Live** 가 될 때까지 기다립니다.

---

## 6. 최종 확인

1. `https://<프로젝트>.vercel.app` 접속 → 개인 소개 페이지가 뜬다.
2. 상단 **방명록** 링크 → 「백엔드 연결 상태」가 **연결됨 (ok)** 으로 바뀐다.
3. 「API로 받아온 소개 정보」에 이름·소속 등이 채워진다.
4. 이름과 메시지를 넣고 **등록** → 목록에 나타나고, 새로고침해도 남아 있다.
5. `https://<서비스>.onrender.com/docs` → `GET /entries` 실행 → 방금 쓴 글이 응답에 보인다.
6. 휴대폰에서도 Vercel 주소를 열어 동작을 확인한다.

여기까지 되면 **배포된 프론트엔드에서 백엔드 API 호출 결과를 확인할 수 있는 상태**입니다.

마지막으로 `README.md` 의 「배포 주소」 표에 있는 두 개의 `TODO` 를 실제 주소로 채우고 push 합니다.

---

## 제출할 주소 3가지

| 제출 항목 | 주소 |
|---|---|
| GitHub 저장소 | `https://github.com/first05061/my-page` |
| Vercel 배포 페이지 | `https://<프로젝트>.vercel.app` |
| 백엔드 Swagger UI | `https://<서비스>.onrender.com/docs` |

---

## 막혔을 때

| 증상 | 먼저 해볼 것 |
|---|---|
| Render 502 / `Could not import module "main"` | **Root Directory** 가 `backend` 인지, Start Command 가 `uvicorn main:app --host 0.0.0.0 --port $PORT` 인지 확인 |
| Render Logs 에 `ModuleNotFoundError` | Root Directory 가 비어 있어 `requirements.txt` 를 못 찾은 경우가 대부분 |
| 방명록이 「연결 실패」 | `config.js` 의 주소가 Render 주소인지, 끝에 `/` 가 없는지 확인. 고쳤으면 **push 해야** Vercel 에 반영된다 |
| 브라우저 콘솔(F12)에 `blocked by CORS policy` | Render 의 `ALLOWED_ORIGINS` 에 Vercel 주소가 **끝의 `/` 없이** 들어갔는지 확인 (5단계) |
| 첫 요청이 30~60초 걸린다 | 무료 플랜 콜드 스타트라 정상 |
| 며칠 뒤 방명록 글이 사라졌다 | SQLite 파일이 Render 재배포 때 초기화되기 때문. 정상이며, 영구 보관은 Supabase(PostgreSQL) 연결이 필요하다 |
