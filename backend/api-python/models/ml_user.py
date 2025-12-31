from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from database import Base

class MLUser(Base):
    __tablename__ = "ml_users"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(String, unique=True, index=True)
    nickname = Column(String)
    site_id = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
