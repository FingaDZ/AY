"""
Pydantic schemas for Import Preview functionality
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from enum import Enum

# Enums
class LogPreviewStatus(str, Enum):
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"

class MatchMethod(str, Enum):
    MAPPING = "mapping"
    EXACT_NAME = "exact_name"
    FUZZY_NAME = "fuzzy"
    MANUAL = "manual"
    NONE = "none"

# Preview Schemas
class LogPreviewItem(BaseModel):
    """Individual log item in preview"""
    log_id: str
    employee_name: str
    timestamp: datetime
    log_type: str
    worked_minutes: Optional[int] = None
    
    # Employee Matching
    matched_employee_id: Optional[int] = None
    matched_employee_name: Optional[str] = None
    matched_employee_poste: Optional[str] = None
    match_confidence: int = Field(ge=0, le=100)
    match_method: MatchMethod
    
    # Alternative matches (for fuzzy)
    alternative_matches: List[dict] = []  # [{id, name, confidence}]
    
    # Validation
    status: LogPreviewStatus
    warnings: List[str] = []
    errors: List[str] = []
    
    # Conflict Detection
    has_conflict: bool = False
    existing_value: Optional[int] = None
    conflict_date: Optional[str] = None

class ImportPreviewStats(BaseModel):
    """Statistics for preview"""
    total_logs: int
    ok_count: int
    warning_count: int
    error_count: int
    matched_employees: int
    unmatched_employees: int
    conflicts_detected: int
    duplicates_detected: int

class ImportPreviewResponse(BaseModel):
    """Response for preview endpoint"""
    session_id: str
    items: List[LogPreviewItem]
    stats: ImportPreviewStats
    
class ImportConfirmRequest(BaseModel):
    """Request to confirm and execute import"""
    session_id: str
    selected_log_ids: List[str]  # Only import these logs
    employee_mappings: dict = {}  # Manual mappings: {log_id: employee_id}
