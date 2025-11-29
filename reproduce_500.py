
import sys
import os
from datetime import date, datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel

# Mock SQLAlchemy Model Enum
class ConflictStatus(str, Enum):
    PENDING = "pending"
    RESOLVED_KEEP_HR = "resolved_keep_hr"
    RESOLVED_USE_ATTENDANCE = "resolved_use_attendance"

# Mock SQLAlchemy Model
class AttendanceImportConflict:
    def __init__(self):
        self.id = 1
        self.hr_employee_id = 101
        self.attendance_log_id = 500
        self.conflict_date = date.today()
        self.hr_existing_value = 1
        self.attendance_worked_minutes = 480
        self.status = ConflictStatus.PENDING  # This is the Enum member
        self.created_at = datetime.now()
        self.resolved_at = None
        self.resolved_by = None

# Mock Pydantic Schema Enum
class ConflictStatusEnum(str, Enum):
    PENDING = "pending"
    RESOLVED_KEEP_HR = "resolved_keep_hr"
    RESOLVED_USE_ATTENDANCE = "resolved_use_attendance"

# Mock Pydantic Schemas
class AttendanceImportConflictBase(BaseModel):
    hr_employee_id: int
    attendance_log_id: int
    conflict_date: date
    hr_existing_value: Optional[int] = None
    attendance_worked_minutes: Optional[int] = None

class AttendanceImportConflictResponse(AttendanceImportConflictBase):
    id: int
    status: ConflictStatusEnum
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    
    class Config:
        from_attributes = True

try:
    # Simulate DB object
    db_obj = AttendanceImportConflict()
    print(f"DB Object Status Type: {type(db_obj.status)}")
    print(f"DB Object Status Value: {db_obj.status}")
    
    # Try to serialize
    response = AttendanceImportConflictResponse.from_orm(db_obj)
    print("Serialization Successful!")
    print(response.json())
except Exception as e:
    print(f"Serialization Failed: {e}")
