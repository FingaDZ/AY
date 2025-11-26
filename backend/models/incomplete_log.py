from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, Text, Float
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class IncompleteAttendanceLog(Base):
    """Logs incomplets nécessitant validation RH"""
    __tablename__ = "incomplete_attendance_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Référence au log Attendance
    attendance_log_id = Column(Integer, unique=True, nullable=False)
    attendance_sync_log_id = Column(Integer, nullable=True)  # Lien vers AttendanceSyncLog
    
    # Employé concerné
    hr_employee_id = Column(Integer, nullable=False)
    employee_name = Column(String(200))
    
    # Détails du log
    log_date = Column(Date, nullable=False)
    log_type = Column(String(10))  # 'ENTRY' ou 'EXIT'
    log_timestamp = Column(DateTime, nullable=False)
    
    # Calcul automatique
    estimated_minutes = Column(Integer, nullable=False)  # Temps estimé par règle smart
    estimation_rule = Column(String(50))  # 'entry_assume_17h', 'exit_assume_8h', etc.
    
    # Validation RH
    status = Column(String(20), default='pending')  # 'pending', 'validated', 'corrected', 'rejected'
    validated_by = Column(String(100), nullable=True)
    validated_at = Column(DateTime, nullable=True)
    
    # Correction manuelle
    corrected_minutes = Column(Integer, nullable=True)
    correction_note = Column(Text, nullable=True)
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
