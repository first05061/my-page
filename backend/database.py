"""DB 연결 설정.

접속 문자열만 환경변수로 바꿔 끼우면 SQLite -> PostgreSQL(Supabase) 전환이 된다.
기본값은 로컬 개발용 SQLite 파일이다.
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# 환경변수 DATABASE_URL 이 있으면 그것을, 없으면 로컬 SQLite 파일을 쓴다.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./guestbook.db")

# SQLite 는 기본적으로 한 스레드만 허용하므로 FastAPI 에서 쓰려면 이 옵션이 필요하다.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """ORM 모델들이 상속할 기반 클래스 (SQLAlchemy 2.0 방식)."""
    pass


def get_db():
    """요청마다 DB 세션을 열고, 끝나면 반드시 닫는 의존성 함수."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
