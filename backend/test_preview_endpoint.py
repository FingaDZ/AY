"""
Test script to directly call preview endpoint
"""
import sys
sys.path.insert(0, r'F:\Code\AY HR\backend')

from services.import_service import ImportService
from services.preview_service import preview_import_endpoint
from database import SessionLocal
import asyncio

async def test_preview():
    # Read file
    file_path = r"F:\Code\AY HR\attendance_report (10).xlsx"
    with open(file_path, 'rb') as f:
        content = f.read()
    
    # Create mock upload file
    class MockUploadFile:
        def __init__(self, content, filename):
            self.content = content
            self.filename = filename
        
        async def read(self):
            return self.content
    
    mock_file = MockUploadFile(content, "attendance_report (10).xlsx")
    
    # Get DB session
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("Testing preview endpoint...")
        print("=" * 60)
        
        # Call preview endpoint
        result = await preview_import_endpoint(mock_file, db)
        
        print(f"\n✓ Preview generated successfully")
        print(f"Session ID: {result.session_id}")
        print(f"\nStats:")
        print(f"  Total logs: {result.stats.total_logs}")
        print(f"  OK: {result.stats.ok_count}")
        print(f"  Warnings: {result.stats.warning_count}")
        print(f"  Errors: {result.stats.error_count}")
        print(f"  Matched employees: {result.stats.matched_employees}")
        
        print(f"\nItems ({len(result.items)}):")
        for item in result.items:
            print(f"\n  - {item.employee_name} ({item.work_date})")
            print(f"    Status: {item.status}")
            print(f"    Photo: {item.has_photo}")
            print(f"    Warnings: {item.warnings}")
            print(f"    Errors: {item.errors}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_preview())
