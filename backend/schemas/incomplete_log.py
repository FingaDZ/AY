from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class IncompleteLogBase(BaseModel):
    attendance_log_id: int
    hr_employee_id: int
    employee_name: str
    log_date: date
    log_type: str
    log_timestamp: datetime
    estimated_minutes: int
    estimation_rule: str
    status: str
    validated_by: Optional[str] = None
    validated_at: Optional[datetime] = None
    corrected_minutes: Optional[int] = None
    correction_note: Optional[str] = None

class IncompleteLogResponse(IncompleteLogBase):
    id: int
    attendance_sync_log_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class IncompleteLogValidation(BaseModel):
    action: str  # 'validate', 'correct', 'reject'
    validated_by: str
    corrected_minutes: Optional[int] = None
    note: Optional[str] = None

class IncompleteLogStats(BaseModel):
    total: int
    pending: int
    validated: int
    corrected: int
