"""DB 테이블 구조(ORM 모델). 클래스 하나 = 테이블 하나."""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String

from database import Base


class Entry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), nullable=False)
    message = Column(String(200), nullable=False)
    # 서버 시간대에 상관없이 항상 UTC 기준으로 저장한다.
    # (프론트엔드가 이 값을 브라우저의 지역 시간으로 바꿔 보여준다)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
