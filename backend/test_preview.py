"""
Test script to debug preview import
"""

from schemas.import_preview import LogPreviewItem, LogPreviewStatus, MatchMethod
from datetime import datetime

# Test creating LogPreviewItem with all fields
try:
    item = LogPreviewItem(
        log_id="test_1",
        employee_name="Test Employee",
        timestamp=datetime.now(),
        log_type="DAILY",
        worked_minutes=480,
        matched_employee_id=1,
        matched_employee_name="Test Employee",
        matched_employee_poste="Agent",
        match_confidence=100,
        match_method=MatchMethod.EXACT_NAME,
        alternative_matches=[],
        status=LogPreviewStatus.OK,
        warnings=[],
        errors=[],
        has_conflict=False,
        existing_value=None,
        conflict_date=None,
        # New fields
        work_date="2025-11-29",
        entry_time="08:00:00",
        exit_time="17:00:00",
        worked_hours=8.0,
        overtime_hours=1.0,
        day_value=1,
        was_estimated=False
    )
    print("✅ LogPreviewItem created successfully")
    print(f"Item: {item.model_dump()}")
except Exception as e:
    print(f"❌ Error creating LogPreviewItem: {e}")
    import traceback
    traceback.print_exc()
