from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Pointage(Base):
    __tablename__ = "pointages"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employe_id = Column(Integer, ForeignKey("employes.id", ondelete="CASCADE"), nullable=False)
    annee = Column(Integer, nullable=False, index=True)
    mois = Column(Integer, nullable=False, index=True)
    
    # Jours du mois (1 à 31) - Valeur: 1=Travaillé/Férié, 0=Absent/Congé/Maladie/Arrêt, NULL=Non défini
    jour_01 = Column(Integer, nullable=True)
    jour_02 = Column(Integer, nullable=True)
    jour_03 = Column(Integer, nullable=True)
    jour_04 = Column(Integer, nullable=True)
    jour_05 = Column(Integer, nullable=True)
    jour_06 = Column(Integer, nullable=True)
    jour_07 = Column(Integer, nullable=True)
    jour_08 = Column(Integer, nullable=True)
    jour_09 = Column(Integer, nullable=True)
    jour_10 = Column(Integer, nullable=True)
    jour_11 = Column(Integer, nullable=True)
    jour_12 = Column(Integer, nullable=True)
    jour_13 = Column(Integer, nullable=True)
    jour_14 = Column(Integer, nullable=True)
    jour_15 = Column(Integer, nullable=True)
    jour_16 = Column(Integer, nullable=True)
    jour_17 = Column(Integer, nullable=True)
    jour_18 = Column(Integer, nullable=True)
    jour_19 = Column(Integer, nullable=True)
    jour_20 = Column(Integer, nullable=True)
    jour_21 = Column(Integer, nullable=True)
    jour_22 = Column(Integer, nullable=True)
    jour_23 = Column(Integer, nullable=True)
    jour_24 = Column(Integer, nullable=True)
    jour_25 = Column(Integer, nullable=True)
    jour_26 = Column(Integer, nullable=True)
    jour_27 = Column(Integer, nullable=True)
    jour_28 = Column(Integer, nullable=True)
    jour_29 = Column(Integer, nullable=True)
    jour_30 = Column(Integer, nullable=True)
    jour_31 = Column(Integer, nullable=True)
    
    # Verrouillage
    verrouille = Column(Integer, default=0, nullable=False)  # 0 = Non verrouillé, 1 = Verrouillé
    
    # Relation
    employe = relationship("Employe", back_populates="pointages")
    
    
    def get_jour(self, numero_jour: int):
        """Obtenir la valeur d'un jour spécifique (0 ou 1)"""
        return getattr(self, f"jour_{numero_jour:02d}")
    
    def set_jour(self, numero_jour: int, valeur: int):
        """Définir la valeur d'un jour spécifique (0 ou 1)"""
        setattr(self, f"jour_{numero_jour:02d}", valeur)
    
    def calculer_totaux(self):
        """
        Calculer les totaux pour ce pointage
        NOTE: Le système actuel stocke seulement 0 ou 1:
        - 1 = Travaillé ou Férié  
        - 0 = Absent, Congé, Maladie ou Arrêt (non différenciables)
        """
        totaux = {
            "jours_travailles": 0,
            "heures_supplementaires": 0,
            "jours_absences": 0,  # Inclut congés, maladies, arrêts (tous = 0 dans la DB)
            "jours_conges": 0,
            "jours_maladie": 0,
            "jours_arret": 0,
            "jours_feries": 0
        }
        
        # Compter les jours
        for jour in range(1, 32):
            valeur = self.get_jour(jour)
            if valeur == 1:  # Travaillé ou Férié
                totaux["jours_travailles"] += 1
            elif valeur == 0:  # Absence (toutes catégories confondues dans la DB)
                totaux["jours_absences"] += 1
        
        # Calculer les heures supplémentaires (si la colonne existe)
        if hasattr(self, 'heures_supplementaires') and self.heures_supplementaires:
            totaux["heures_supplementaires"] = float(self.heures_supplementaires)
        
        # Compatibilité avec anciens noms
        totaux["total_travailles"] = totaux["jours_travailles"]
        totaux["travailles"] = totaux["jours_travailles"]
        
        return totaux
    
    def __repr__(self):
        return f"<Pointage {self.employe_id} - {self.mois}/{self.annee}>"
