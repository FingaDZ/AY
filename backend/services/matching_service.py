"""
Employee Matching Service
Provides intelligent employee matching for attendance imports
"""

from typing import Tuple, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Employe, AttendanceEmployeeMapping
import logging

logger = logging.getLogger(__name__)

class EmployeeMatchingService:
    """Service for matching attendance logs to HR employees"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def match_employee(
        self, 
        employee_name: str, 
        attendance_employee_id: Optional[int] = None
    ) -> Tuple[Optional[int], str, int, List[dict]]:
        """
        Match employee using cascade strategy
        
        Returns:
            (employee_id, match_method, confidence, alternatives)
        """
        
        # Strategy 1: By existing mapping
        if attendance_employee_id:
            mapping = self.db.query(AttendanceEmployeeMapping).filter(
                AttendanceEmployeeMapping.attendance_employee_id == attendance_employee_id
            ).first()
            
            if mapping:
                return mapping.hr_employee_id, "mapping", 100, []
        
        # Strategy 2: Exact name match
        search_name = employee_name.upper().strip()
        
        # Try "Nom Prenom"
        employee = self.db.query(Employe).filter(
            func.upper(func.concat(Employe.nom, ' ', Employe.prenom)) == search_name
        ).first()
        
        if employee:
            return employee.id, "exact_name", 95, []
        
        # Try "Prenom Nom"
        employee = self.db.query(Employe).filter(
            func.upper(func.concat(Employe.prenom, ' ', Employe.nom)) == search_name
        ).first()
        
        if employee:
            return employee.id, "exact_name", 95, []
        
        # Strategy 3: Fuzzy matching
        alternatives = self._fuzzy_match(employee_name)
        
        if alternatives and alternatives[0]['confidence'] >= 85:
            # Auto-match if confidence >= 85%
            best_match = alternatives[0]
            return best_match['id'], "fuzzy", best_match['confidence'], alternatives[1:]
        elif alternatives:
            # Return alternatives for manual selection
            return None, "none", 0, alternatives
        
        # No match found
        return None, "none", 0, []
    
    def _fuzzy_match(self, name: str, threshold: int = 70) -> List[dict]:
        """
        Find similar employee names using Levenshtein distance
        
        Returns list of {id, name, poste, confidence} sorted by confidence
        """
        try:
            from Levenshtein import ratio
        except ImportError:
            logger.warning("python-Levenshtein not installed, fuzzy matching disabled")
            return []
        
        employees = self.db.query(Employe).filter(Employe.actif == True).all()
        matches = []
        
        search_name = name.upper().strip()
        
        for emp in employees:
            emp_name_1 = f"{emp.nom} {emp.prenom}".upper()
            emp_name_2 = f"{emp.prenom} {emp.nom}".upper()
            
            # Calculate similarity for both name orders
            similarity_1 = ratio(search_name, emp_name_1) * 100
            similarity_2 = ratio(search_name, emp_name_2) * 100
            
            confidence = int(max(similarity_1, similarity_2))
            
            if confidence >= threshold:
                matches.append({
                    'id': emp.id,
                    'name': f"{emp.nom} {emp.prenom}",
                    'poste': emp.poste_travail,
                    'confidence': confidence
                })
        
        # Sort by confidence descending
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        
        return matches[:5]  # Return top 5 matches
    
    def get_employee_details(self, employee_id: int) -> Optional[dict]:
        """Get employee details for display"""
        employee = self.db.query(Employe).filter(Employe.id == employee_id).first()
        
        if not employee:
            return None
        
        return {
            'id': employee.id,
            'name': f"{employee.nom} {employee.prenom}",
            'poste': employee.poste_travail,
            'actif': employee.actif
        }
