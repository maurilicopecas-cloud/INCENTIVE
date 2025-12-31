from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.sql import func
from database import Base

class MLItem(Base):
    __tablename__ = "ml_items"

    id = Column(Integer, primary_key=True, index=True)

    item_id = Column(String, unique=True, index=True)  # MLB123...
    user_id = Column(String, index=True)

    title = Column(String)
    category_id = Column(String)
    price = Column(Float)
    currency_id = Column(String)

    available_quantity = Column(Integer)
    sold_quantity = Column(Integer)

    status = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
