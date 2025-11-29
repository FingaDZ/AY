"""
Pydantic schemas for Attendance Integration
"""

from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List
from enum import Enum

# Enums
class SyncMethodEnum(str, Enum):
    SECU_SOCIALE = "secu_sociale"
    NAME_DOB = "name_dob"

class ConflictStatusEnum(str, Enum):
    PENDING = "pending"
    RESOLVED_KEEP_HR = "resolved_keep_hr"
    RESOLVED_USE_ATTENDANCE = "resolved_use_attendance"

class LogTypeEnum(str, Enum):
    ENTRY = "ENTRY"
    EXIT = "EXIT"

# Employee Mapping Schemas
class AttendanceEmployeeMappingBase(BaseModel):
    hr_employee_id: int
    attendance_employee_id: int
    attendance_employee_name: Optional[str] = None
    sync_method: SyncMethodEnum = SyncMethodEnum.NAME_DOB

class AttendanceEmployeeMappingCreate(AttendanceEmployeeMappingBase):
    pass

class AttendanceEmployeeMappingResponse(AttendanceEmployeeMappingBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Sync Log Schemas
class AttendanceSyncLogBase(BaseModel):
    attendance_log_id: int
    hr_employee_id: int
    sync_date: date
    worked_minutes: Optional[int] = None
    overtime_minutes: Optional[int] = None
    log_type: LogTypeEnum = LogTypeEnum.EXIT

class AttendanceSyncLogResponse(AttendanceSyncLogBase):
    id: int
    imported_at: datetime
    
    class Config:
        from_attributes = True

# Conflict Schemas
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
    employee_name: Optional[str] = None
    employee_poste: Optional[str] = None
    
    class Config:
        from_attributes = True
        use_enum_values = True

class ConflictResolution(BaseModel):
    resolution: str = Field(..., description="'keep_hr' or 'use_attendance'")
    resolved_by: str = Field(..., description="Username of resolver")

# Import Request/Response
class AttendanceImportRequest(BaseModel):
    start_date: date
    end_date: date
    employee_id: Optional[int] = None

class AttendanceImportSummary(BaseModel):
    total_logs: int
    imported: int
    skipped_duplicate: int
    skipped_no_mapping: int
    conflicts: int
    errors: int
    incomplete_pending_validation: int = 0
    details: List[dict] = []  # List of {log_id, status, message, employee_name}

# Employee Sync
class EmployeeSyncRequest(BaseModel):
    employee_id: int

class EmployeeSyncResponse(BaseModel):
    success: bool
    message: str
    mapping: Optional[AttendanceEmployeeMappingResponse] = None
