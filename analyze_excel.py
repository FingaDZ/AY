
import pandas as pd
import os

file_path = 'attendance_report (7).xlsx'
print(f"Analyzing {file_path}...")

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit(1)

try:
    df = pd.read_excel(file_path)
    print("\n--- Columns ---")
    print(df.columns.tolist())
    print("\n--- First 5 Rows ---")
    print(df.head().to_string())
    
    # Check for likely columns
    print("\n--- Data Types ---")
    print(df.dtypes)
except Exception as e:
    print(f"Error reading Excel: {e}")
