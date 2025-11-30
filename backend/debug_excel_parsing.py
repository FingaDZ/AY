import pandas as pd
from datetime import datetime
import sys

# Test parsing the Excel file
file_path = r"F:\Code\AY HR\attendance_report (10).xlsx"

try:
    df = pd.read_excel(file_path)
    print(f"✓ File loaded successfully")
    print(f"✓ Total rows: {len(df)}")
    print(f"✓ Columns: {list(df.columns)}")
    print("\n" + "="*50)
    print("First 3 rows:")
    print(df.head(3))
    print("\n" + "="*50)
    
    # Test parsing logic
    df.columns = [c.strip() for c in df.columns]
    print(f"\n✓ Normalized columns: {list(df.columns)}")
    
    required_cols = ['Date', 'Time', 'Employee']
    missing_cols = [c for c in required_cols if c not in df.columns]
    
    if missing_cols:
        print(f"✗ Missing columns: {missing_cols}")
        sys.exit(1)
    
    print(f"✓ All required columns present")
    
    # Test parsing first row
    print("\n" + "="*50)
    print("Testing first row parsing:")
    row = df.iloc[0]
    
    print(f"Date value: {row['Date']} (type: {type(row['Date'])})")
    print(f"Time value: {row['Time']} (type: {type(row['Time'])})")
    print(f"Employee value: {row['Employee']}")
    print(f"Type value: {row.get('Type', 'N/A')}")
    print(f"Photo value: {row.get('Photo', 'N/A')}")
    
    # Try parsing date
    if isinstance(row['Date'], datetime):
        date_obj = row['Date'].date()
        print(f"✓ Date parsed as datetime object: {date_obj}")
    else:
        date_str = str(row['Date'])
        print(f"Date string: '{date_str}'")
        try:
            date_obj = datetime.strptime(date_str.split()[0], "%d/%m/%Y").date()
            print(f"✓ Date parsed with DD/MM/YYYY: {date_obj}")
        except Exception as e:
            print(f"✗ Failed DD/MM/YYYY: {e}")
            try:
                date_obj = datetime.strptime(date_str.split()[0], "%Y-%m-%d").date()
                print(f"✓ Date parsed with YYYY-MM-DD: {date_obj}")
            except Exception as e2:
                print(f"✗ Failed YYYY-MM-DD: {e2}")
    
    # Try parsing time
    if isinstance(row['Time'], datetime):
        time_obj = row['Time'].time()
        print(f"✓ Time parsed as datetime object: {time_obj}")
    else:
        time_str = str(row['Time'])
        print(f"Time string: '{time_str}'")
        try:
            time_obj = datetime.strptime(time_str, "%H:%M:%S").time()
            print(f"✓ Time parsed with HH:MM:SS: {time_obj}")
        except Exception as e:
            print(f"✗ Failed HH:MM:SS: {e}")
            try:
                time_obj = datetime.strptime(time_str, "%H:%M").time()
                print(f"✓ Time parsed with HH:MM: {time_obj}")
            except Exception as e2:
                print(f"✗ Failed HH:MM: {e2}")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
