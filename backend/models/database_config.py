from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database import Base
from datetime import datetime
from urllib.parse import quote_plus


class DatabaseConfig(Base):
    __tablename__ = 'database_config'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    host = Column(String(255), nullable=False, default='localhost')
    port = Column(Integer, nullable=False, default=3306)
    database_name = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    charset = Column(String(50), default='utf8mb4')
    is_active = Column(Boolean, default=True)
    date_creation = Column(DateTime, default=datetime.now)
    derniere_modification = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'host': self.host,
            'port': self.port,
            'database_name': self.database_name,
            'username': self.username,
            'password': '***HIDDEN***',
            'charset': self.charset,
            'is_active': self.is_active,
            'date_creation': self.date_creation.isoformat() if self.date_creation else None,
            'derniere_modification': self.derniere_modification.isoformat() if self.derniere_modification else None,
        }

    def connection_string(self):
        encoded_password = quote_plus(self.password)
        return f"mysql+pymysql://{self.username}:{encoded_password}@{self.host}:{self.port}/{self.database_name}?charset={self.charset}"
