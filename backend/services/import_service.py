
import pandas as pd
from io import BytesIO
from typing import List, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ImportService:
    """Service for importing attendance logs from files"""
    
    def parse_excel(self, file_content: bytes) -> List[Dict]:
        """
        Parse Excel file and return list of log dicts
        Expected columns: Date, Time, Employee, Type
        """
        try:
            df = pd.read_excel(BytesIO(file_content))
            logs = []
            
            # Normalize column names
            df.columns = [c.strip() for c in df.columns]
            
            required_cols = ['Date', 'Time', 'Employee']
            missing_cols = [c for c in required_cols if c not in df.columns]
            
            if missing_cols:
                raise ValueError(f"Colonnes manquantes: {', '.join(missing_cols)}")
            
            for index, row in df.iterrows():
                try:
                    # Skip empty rows
                    if pd.isna(row['Date']) or pd.isna(row['Employee']):
                        continue
                        
                    # Parse Date and Time
                    date_str = str(row['Date'])
                    time_str = str(row['Time'])
                    
                    # Handle various date formats
                    # Excel might return datetime objects or strings
                    if isinstance(row['Date'], datetime):
                        date_obj = row['Date'].date()
                    else:
                        # Try parsing DD/MM/YYYY
                        try:
                            date_obj = datetime.strptime(date_str.split()[0], "%d/%m/%Y").date()
                        except ValueError:
                            # Try YYYY-MM-DD
                            date_obj = datetime.strptime(date_str.split()[0], "%Y-%m-%d").date()
                            
                    # Handle time
                    if isinstance(row['Time'], datetime):
                        time_obj = row['Time'].time()
                    else:
                        # Try HH:MM:SS
                        try:
                            time_obj = datetime.strptime(str(time_str), "%H:%M:%S").time()
                        except ValueError:
                            # Try HH:MM
                            time_obj = datetime.strptime(str(time_str), "%H:%M").time()
                            
                    timestamp = datetime.combine(date_obj, time_obj)
                    
                    # Parse Type
                    log_type = "EXIT" # Default
                    if 'Type' in row and not pd.isna(row['Type']):
                        type_val = str(row['Type']).upper()
                        if "ENTRY" in type_val or "ENTRÉE" in type_val or "IN" in type_val:
                            log_type = "ENTRY"
                        elif "EXIT" in type_val or "SORTIE" in type_val or "OUT" in type_val:
                            log_type = "EXIT"
                        # If just "Face", maybe assume based on time? 
                        # For now default to EXIT if unknown, but maybe "Face" means check time?
                        # The user sample had "Type" column.
                    
                    # Parse Photo (Column F / Index 5)
                    has_photo = None
                    # Try by name first
                    if 'Photo' in row:
                        has_photo = str(row['Photo']) if not pd.isna(row['Photo']) else None
                    elif 'Presence Photo' in row:
                        has_photo = str(row['Presence Photo']) if not pd.isna(row['Presence Photo']) else None
                    else:
                        # Try by index (F is 5th index, 0-based is 5)
                        try:
                            val = df.iloc[index, 5]
                            has_photo = str(val) if not pd.isna(val) else None
                        except IndexError:
                            pass

                    # Generate ID
                    log_id = f"excel_{timestamp.strftime('%Y%m%d%H%M%S')}_{index}"
                    
                    logs.append({
                        "id": log_id,
                        "employee_name": str(row['Employee']).strip(),
                        "timestamp": timestamp.isoformat(),
                        "type": log_type,
                        "source": "excel",
                        "has_photo": has_photo
                    })
                    
                except Exception as e:
                    logger.warning(f"Skipping row {index}: {e}")
                    continue
            
            return logs
            
        except Exception as e:
            logger.error(f"Error parsing Excel: {e}")
            raise ValueError(f"Erreur lors de la lecture du fichier Excel: {str(e)}")
