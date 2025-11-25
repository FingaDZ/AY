from sqlalchemy import Column, Integer, String, DateTime, Date, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import enum

class SyncMethod(str, enum.Enum):
    SECU_SOCIALE = "secu_sociale"
    NAME_DOB = "name_dob"

class ConflictStatus(str, enum.Enum):
    PENDING = "pending"
    RESOLVED_KEEP_HR = "resolved_keep_hr"
    RESOLVED_USE_ATTENDANCE = "resolved_use_attendance"

class LogType(str, enum.Enum):
    ENTRY = "ENTRY"
    EXIT = "EXIT"

class AttendanceEmployeeMapping(Base):
    __tablename__ = "attendance_employee_mapping"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hr_employee_id = Column(Integer, ForeignKey("employes.id", ondelete="CASCADE"), nullable=False)
    attendance_employee_id = Column(Integer, nullable=False, index=True)
    attendance_employee_name = Column(String(200), nullable=True)
    sync_method = Column(SQLEnum(SyncMethod), default=SyncMethod.NAME_DOB, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationship
    employe = relationship("Employe", backref="attendance_mapping")
    
    def __repr__(self):
        return f"<AttendanceMapping HR:{self.hr_employee_id} <-> Attendance:{self.attendance_employee_id}>"

class AttendanceSyncLog(Base):
    __tablename__ = "attendance_sync_log"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    attendance_log_id = Column(Integer, nullable=False, unique=True)
    hr_employee_id = Column(Integer, ForeignKey("employes.id", ondelete="CASCADE"), nullable=False)
    sync_date = Column(Date, nullable=False, index=True)
    worked_minutes = Column(Integer, nullable=True)
    overtime_minutes = Column(Integer, nullable=True)
    log_type = Column(SQLEnum(LogType), default=LogType.EXIT, nullable=False)
    imported_at = Column(DateTime, server_default=func.now())
    
    # Relationship
    employe = relationship("Employe", backref="attendance_sync_logs")
    
    def __repr__(self):
        return f"<AttendanceSyncLog {self.sync_date} - {self.worked_minutes}min>"

class AttendanceImportConflict(Base):
    __tablename__ = "attendance_import_conflicts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hr_employee_id = Column(Integer, ForeignKey("employes.id", ondelete="CASCADE"), nullable=False)
    attendance_log_id = Column(Integer, nullable=False)
    conflict_date = Column(Date, nullable=False, index=True)
    hr_existing_value = Column(Integer, nullable=True)  # 0 or 1
    attendance_worked_minutes = Column(Integer, nullable=True)
    status = Column(SQLEnum(ConflictStatus), default=ConflictStatus.PENDING, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(100), nullable=True)
    
    # Relationship
    employe = relationship("Employe", backref="attendance_conflicts")
    
    def __repr__(self):
        return f"<AttendanceConflict {self.conflict_date} - {self.status}>"
