from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class MercadoLivreToken(Base):
    __tablename__ = "mercadolivre_tokens"

    id = Column(Integer, primary_key=True, index=True)

    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)

    token_type = Column(String, default="bearer")
    expires_in = Column(Integer)

    scope = Column(String)
    user_id = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
