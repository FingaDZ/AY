from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
import enum

class TypeJour(str, enum.Enum):
    TRAVAILLE = "Tr"  # Valeur 1
    ABSENT = "Ab"     # Valeur 0
    CONGE = "Co"      # Valeur 0
    MALADIE = "Ma"    # Valeur 0
    FERIE = "Fe"      # Valeur 1
    ARRET = "Ar"      # Valeur 0

class Pointage(Base):
    __tablename__ = "pointages"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employe_id = Column(Integer, ForeignKey("employes.id", ondelete="CASCADE"), nullable=False)
    annee = Column(Integer, nullable=False, index=True)
    mois = Column(Integer, nullable=False, index=True)
    
    # Jours du mois (1 à 31)
    jour_01 = Column(SQLEnum(TypeJour), nullable=True)
    jour_02 = Column(SQLEnum(TypeJour), nullable=True)
    jour_03 = Column(SQLEnum(TypeJour), nullable=True)
    jour_04 = Column(SQLEnum(TypeJour), nullable=True)
    jour_05 = Column(SQLEnum(TypeJour), nullable=True)
    jour_06 = Column(SQLEnum(TypeJour), nullable=True)
    jour_07 = Column(SQLEnum(TypeJour), nullable=True)
    jour_08 = Column(SQLEnum(TypeJour), nullable=True)
    jour_09 = Column(SQLEnum(TypeJour), nullable=True)
    jour_10 = Column(SQLEnum(TypeJour), nullable=True)
    jour_11 = Column(SQLEnum(TypeJour), nullable=True)
    jour_12 = Column(SQLEnum(TypeJour), nullable=True)
    jour_13 = Column(SQLEnum(TypeJour), nullable=True)
    jour_14 = Column(SQLEnum(TypeJour), nullable=True)
    jour_15 = Column(SQLEnum(TypeJour), nullable=True)
    jour_16 = Column(SQLEnum(TypeJour), nullable=True)
    jour_17 = Column(SQLEnum(TypeJour), nullable=True)
    jour_18 = Column(SQLEnum(TypeJour), nullable=True)
    jour_19 = Column(SQLEnum(TypeJour), nullable=True)
    jour_20 = Column(SQLEnum(TypeJour), nullable=True)
    jour_21 = Column(SQLEnum(TypeJour), nullable=True)
    jour_22 = Column(SQLEnum(TypeJour), nullable=True)
    jour_23 = Column(SQLEnum(TypeJour), nullable=True)
    jour_24 = Column(SQLEnum(TypeJour), nullable=True)
    jour_25 = Column(SQLEnum(TypeJour), nullable=True)
    jour_26 = Column(SQLEnum(TypeJour), nullable=True)
    jour_27 = Column(SQLEnum(TypeJour), nullable=True)
    jour_28 = Column(SQLEnum(TypeJour), nullable=True)
    jour_29 = Column(SQLEnum(TypeJour), nullable=True)
    jour_30 = Column(SQLEnum(TypeJour), nullable=True)
    jour_31 = Column(SQLEnum(TypeJour), nullable=True)
    
    # Verrouillage
    verrouille = Column(Integer, default=0, nullable=False)  # 0 = Non verrouillé, 1 = Verrouillé
    
    # Relation
    employe = relationship("Employe", back_populates="pointages")
    
    def get_jour(self, numero_jour: int):
        """Obtenir la valeur d'un jour spécifique"""
        return getattr(self, f"jour_{numero_jour:02d}")
    
    def set_jour(self, numero_jour: int, valeur: TypeJour):
        """Définir la valeur d'un jour spécifique"""
        setattr(self, f"jour_{numero_jour:02d}", valeur)
    
    def calculer_totaux(self):
        """Calculer les totaux pour ce pointage"""
        totaux = {
            "travailles": 0,
            "absents": 0,
            "conges": 0,
            "maladies": 0,
            "feries": 0,
            "arrets": 0
        }
        
        for jour in range(1, 32):
            valeur = self.get_jour(jour)
            if valeur:
                if valeur == TypeJour.TRAVAILLE:
                    totaux["travailles"] += 1
                elif valeur == TypeJour.ABSENT:
                    totaux["absents"] += 1
                elif valeur == TypeJour.CONGE:
                    totaux["conges"] += 1
                elif valeur == TypeJour.MALADIE:
                    totaux["maladies"] += 1
                elif valeur == TypeJour.FERIE:
                    totaux["feries"] += 1
                elif valeur == TypeJour.ARRET:
                    totaux["arrets"] += 1
        
        # Total jours travaillés = Tr + Fe
        totaux["total_travailles"] = totaux["travailles"] + totaux["feries"]
        
        return totaux
    
    def __repr__(self):
        return f"<Pointage {self.employe_id} - {self.mois}/{self.annee}>"
