"""
Attendance Calculation Service
Implements business rules for daily attendance calculation
"""

from typing import List, Dict, Tuple, Optional
from datetime import datetime, date, time, timedelta
from sqlalchemy.orm import Session
from models import Pointage
import logging

logger = logging.getLogger(__name__)

# Business Rules Constants (Critères A-J)
MIN_WORK_HOURS = 4              # B: Minimum pour journée valide
STANDARD_DAY_HOURS = 8          # D: Journée standard (inclus pause)
LUNCH_BREAK_HOURS = 1           # C: Pause déjeuner (chomée et payée)
EFFECTIVE_WORK_HOURS = 7        # 8h - 1h pause = 7h travail effectif
MAX_DAILY_HOURS = 12            # I: Maximum enregistrable par jour
MAX_MONTHLY_HOURS = 208         # E: Maximum heures/mois
WORK_DAYS_PER_MONTH = 30        # F: Jours par mois (inclus vendredis)
NORMAL_MONTHLY_HOURS = 173.33   # G: Heures normales/mois
MAX_OVERTIME_MONTHLY = 34.67    # H: Heures sup max/mois

class AttendanceCalculationService:
    """Service for calculating daily attendance from logs"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_daily_attendance(
        self,
        entry_time: Optional[datetime],
        exit_time: Optional[datetime],
        work_date: date,
        employee_id: int
    ) -> Dict:
        """
        Calculate daily attendance according to business rules A-J
        
        Returns:
            {
                'worked_minutes': int,
                'worked_hours': float,
                'is_valid_day': bool,
                'overtime_hours': float,
                'status': 'ok' | 'warning' | 'error',
                'warnings': List[str],
                'errors': List[str],
                'day_value': 0 | 1,
                'entry_time': datetime,
                'exit_time': datetime,
                'was_estimated': bool
            }
        """
        
        warnings = []
        errors = []
        was_estimated = False
        
        # 1. Vérifier présence entrée ET sortie
        if not entry_time and not exit_time:
            return {
                'worked_minutes': 0,
                'worked_hours': 0.0,
                'is_valid_day': False,
                'overtime_hours': 0.0,
                'status': 'error',
                'warnings': [],
                'errors': ['Aucun log (ni entrée ni sortie)'],
                'day_value': 0,
                'entry_time': None,
                'exit_time': None,
                'was_estimated': False
            }
        
        # 2. Estimer entrée ou sortie si manquante
        if not entry_time and exit_time:
            entry_time = self._estimate_entry(exit_time)
            warnings.append('Entrée estimée à 08:00')
            was_estimated = True
        elif entry_time and not exit_time:
            exit_time = self._estimate_exit(entry_time)
            warnings.append('Sortie estimée à 17:00')
            was_estimated = True
        
        # 3. Calculer durée brute
        duration = exit_time - entry_time
        worked_minutes = int(duration.total_seconds() / 60)
        worked_hours = round(worked_minutes / 60, 2)
        
        # 4. Vérifier cohérence (sortie après entrée)
        if worked_minutes < 0:
            return {
                'worked_minutes': 0,
                'worked_hours': 0.0,
                'is_valid_day': False,
                'overtime_hours': 0.0,
                'status': 'error',
                'warnings': warnings,
                'errors': ['Sortie avant entrée - Logs incohérents'],
                'day_value': 0,
                'entry_time': entry_time,
                'exit_time': exit_time,
                'was_estimated': was_estimated
            }
        
        # 5. Vérifier maximum journalier (12h) - Règle I
        if worked_hours > MAX_DAILY_HOURS:
            return {
                'worked_minutes': worked_minutes,
                'worked_hours': worked_hours,
                'is_valid_day': False,
                'overtime_hours': 0.0,
                'status': 'error',
                'warnings': warnings,
                'errors': [f'Durée excessive: {worked_hours}h > {MAX_DAILY_HOURS}h max'],
                'day_value': 0,
                'entry_time': entry_time,
                'exit_time': exit_time,
                'was_estimated': was_estimated
            }
        
        # 6. Vérifier minimum (4h) - Règle B
        if worked_hours < MIN_WORK_HOURS:
            return {
                'worked_minutes': worked_minutes,
                'worked_hours': worked_hours,
                'is_valid_day': False,
                'overtime_hours': 0.0,
                'status': 'warning',
                'warnings': warnings + [f'Durée insuffisante: {worked_hours}h < {MIN_WORK_HOURS}h min'],
                'errors': [],
                'day_value': 0,
                'entry_time': entry_time,
                'exit_time': exit_time,
                'was_estimated': was_estimated
            }
        
        # 7. Calculer heures supplémentaires - Règle J
        # Heures sup = au-delà de 7h effectives (8h - 1h pause)
        overtime_hours = max(0, worked_hours - EFFECTIVE_WORK_HOURS)
        overtime_hours = round(overtime_hours, 2)
        
        # 8. Vérifier jour spécial
        is_friday = work_date.weekday() == 4
        
        if is_friday:
            warnings.append('Vendredi - Jour chomé et payé')
        
        # 9. Vérifier conflit avec pointage existant
        has_conflict = self._check_existing_pointage(employee_id, work_date)
        if has_conflict:
            warnings.append('Conflit: Pointage déjà existant pour ce jour')
        
        # 10. Déterminer statut final
        status = 'ok'
        if errors:
            status = 'error'
        elif warnings or overtime_hours > 0:
            status = 'warning'
        
        return {
            'worked_minutes': worked_minutes,
            'worked_hours': worked_hours,
            'is_valid_day': True,
            'overtime_hours': overtime_hours,
            'status': status,
            'warnings': warnings,
            'errors': errors,
            'day_value': 1,  # Journée travaillée
            'entry_time': entry_time,
            'exit_time': exit_time,
            'was_estimated': was_estimated
        }
    
    def group_logs_by_employee_date(self, logs: List[Dict]) -> Dict[Tuple[int, date], List[Dict]]:
        """
        Group logs by (employee_id, date)
        
        Returns:
            {(employee_id, date): [log1, log2, ...]}
        """
        grouped = {}
        
        for log in logs:
            # Extract employee_id (from matched or manual mapping)
            employee_id = log.get('_manual_employee_id') or log.get('matched_employee_id')
            if not employee_id:
                continue
            
            # Extract date
            timestamp = log.get('timestamp')
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            log_date = timestamp.date()
            
            # Group
            key = (employee_id, log_date)
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(log)
        
        return grouped
    
    def extract_entry_exit(self, day_logs: List[Dict]) -> Tuple[Optional[datetime], Optional[datetime]]:
        """
        Extract first entry and last exit from daily logs
        Handles multiple logs per day (Règle A: 1 entrée + 1 sortie)
        
        Returns:
            (entry_time, exit_time)
        """
        entries = []
        exits = []
        
        for log in day_logs:
            timestamp = log.get('timestamp')
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            
            log_type = log.get('type', log.get('log_type', '')).upper()
            
            if log_type == 'ENTRY':
                entries.append(timestamp)
            elif log_type == 'EXIT':
                exits.append(timestamp)
        
        # Take first entry and last exit
        entry = min(entries) if entries else None
        exit = max(exits) if exits else None
        
        return entry, exit
    
    def _estimate_entry(self, exit_time: datetime) -> datetime:
        """Estimate entry time at 08:00 if missing"""
        return datetime.combine(exit_time.date(), time(8, 0))
    
    def _estimate_exit(self, entry_time: datetime) -> datetime:
        """Estimate exit time at 17:00 if missing"""
        return datetime.combine(entry_time.date(), time(17, 0))
    
    def _check_existing_pointage(self, employee_id: int, work_date: date) -> bool:
        """Check if pointage already exists for this employee and date"""
        year = work_date.year
        month = work_date.month
        day = work_date.day
        
        pointage = self.db.query(Pointage).filter(
            Pointage.employe_id == employee_id,
            Pointage.annee == year,
            Pointage.mois == month
        ).first()
        
        if pointage:
            existing_value = pointage.get_jour(day)
            return existing_value is not None
        
        return False
