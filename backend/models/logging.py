from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum, JSON
from database import Base
from datetime import datetime
import enum


class ActionType(enum.Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class Logging(Base):
    __tablename__ = 'logging'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    user_email = Column(String(255), nullable=True)
    module_name = Column(String(100), nullable=False, index=True)
    action_type = Column(SQLEnum(ActionType), nullable=False, index=True)
    record_id = Column(Integer, nullable=True, index=True)
    old_data = Column(JSON, nullable=True)
    new_data = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'user_id': self.user_id,
            'user_email': self.user_email,
            'module_name': self.module_name,
            'action_type': self.action_type.value if self.action_type else None,
            'record_id': self.record_id,
            'old_data': self.old_data,
            'new_data': self.new_data,
            'description': self.description,
            'ip_address': self.ip_address,
        }
