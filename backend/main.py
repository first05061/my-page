"""개인 소개 페이지 백엔드 API (FastAPI).

- GET    /            서비스 안내
- GET    /health      서버 생존 확인
- GET    /profile     개인 소개 정보(JSON)
- GET    /entries     방명록 목록 조회
- POST   /entries     방명록 등록
- DELETE /entries/{id} 방명록 삭제
"""
import os
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

import models
from database import Base, engine, get_db

# 앱이 시작될 때 테이블이 없으면 만든다. (import models 뒤에 와야 한다)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="김현준 개인 소개 페이지 API",
    description="개인 소개 페이지에서 호출하는 백엔드 API입니다. 소개 정보 조회와 방명록 CRUD를 제공합니다.",
    version="1.0.0",
)

# ── CORS ──────────────────────────────────────────────────────────
# 배포 후 프론트 주소(Vercel)가 달라지므로 코드가 아니라 환경변수로 뺀다.
# 쉼표로 여러 개를 넣을 수 있고, 값이 없으면 로컬 개발 주소를 쓴다.
_default_origins = ",".join([
    "http://localhost:8080", "http://127.0.0.1:8080",   # python -m http.server 8080
    "http://localhost:5500", "http://127.0.0.1:5500",   # VS Code Live Server
])
# 값이 비어 있으면(변수는 있는데 내용이 없는 경우 포함) 기본값을 쓴다.
origins = [o.strip() for o in (os.getenv("ALLOWED_ORIGINS") or _default_origins).split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # 쿠키·인증정보를 주고받지 않으므로 False. 이렇게 두면 ALLOWED_ORIGINS 에
    # "*" 를 넣어도 브라우저가 거부하지 않는다.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 소개 정보 (정적 데이터) ────────────────────────────────────────
PROFILE = {
    "name": "김현준",
    "title": "디지털금융 MBA",
    "organization": "KB국민은행",
    "summary": "KB국민은행에서 시스템 개발 및 유지보수를 맡고 있습니다.",
    "interests": ["AI Agent", "클라우드 컴퓨팅", "백엔드 개발"],
    "github": "https://github.com/first05061",
}


# ── 주고받을 데이터의 모양 (Pydantic) ──────────────────────────────
class EntryIn(BaseModel):
    """요청 본문: 클라이언트가 보내는 데이터."""
    name: str = Field(min_length=1, max_length=30, examples=["방문자"])
    message: str = Field(min_length=1, max_length=200, examples=["페이지 잘 봤습니다!"])


class EntryOut(BaseModel):
    """응답 본문: 서버가 돌려주는 데이터."""
    id: int
    name: str
    message: str
    created_at: datetime

    model_config = {"from_attributes": True}  # ORM 객체 -> Pydantic 변환 허용


# ── 엔드포인트 ─────────────────────────────────────────────────────
@app.get("/", tags=["기본"], summary="서비스 안내")
def read_root():
    return {"message": "김현준 개인 소개 페이지 API 입니다. 문서는 /docs 에서 확인하세요."}


@app.get("/health", tags=["기본"], summary="서버 생존 확인")
def health_check():
    return {"status": "ok"}


@app.get("/profile", tags=["소개"], summary="개인 소개 정보 조회")
def get_profile():
    return PROFILE


@app.get("/entries", response_model=list[EntryOut], tags=["방명록"], summary="방명록 목록 조회")
def list_entries(db: Session = Depends(get_db)):
    # 최신 글이 위로 오도록 id 내림차순 정렬
    return db.query(models.Entry).order_by(models.Entry.id.desc()).all()


@app.post(
    "/entries",
    response_model=EntryOut,
    status_code=status.HTTP_201_CREATED,
    tags=["방명록"],
    summary="방명록 등록",
)
def create_entry(payload: EntryIn, db: Session = Depends(get_db)):
    entry = models.Entry(name=payload.name, message=payload.message)
    db.add(entry)
    db.commit()
    db.refresh(entry)  # DB가 매긴 id·created_at 을 다시 읽어 온다
    return entry


@app.delete("/entries/{entry_id}", tags=["방명록"], summary="방명록 삭제")
def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.get(models.Entry, entry_id)
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entry_id}번 방명록을 찾을 수 없습니다",
        )
    db.delete(entry)
    db.commit()
    return {"ok": True}
