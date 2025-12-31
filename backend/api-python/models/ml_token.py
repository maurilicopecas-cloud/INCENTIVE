from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from database import Base

class MLToken(Base):
    __tablename__ = "ml_tokens"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(String, index=True)  # Mercado Livre user_id
    access_token = Column(String)
    refresh_token = Column(String)

    expires_in = Column(Integer)
    scope = Column(String)
    token_type = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
