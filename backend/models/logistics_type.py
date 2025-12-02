from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class LogisticsType(Base):
    __tablename__ = "logistics_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
