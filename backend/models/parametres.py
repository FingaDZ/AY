from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from datetime import datetime


class Parametres(Base):
    __tablename__ = 'parametres_entreprise'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    raison_sociale = Column(String(255), nullable=True)
    nom_entreprise = Column(String(255), nullable=True)
    adresse = Column(String(500), nullable=True)
    rc = Column(String(100), nullable=True)
    nif = Column(String(100), nullable=True)
    nis = Column(String(100), nullable=True)
    art = Column(String(100), nullable=True)
    numero_secu_employeur = Column(String(100), nullable=True)
    telephone = Column(String(100), nullable=True)
    compte_bancaire = Column(String(255), nullable=True)
    banque = Column(String(255), nullable=True)
    date_creation = Column(DateTime, default=datetime.now)
    derniere_mise_a_jour = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'raison_sociale': self.raison_sociale,
            'nom_entreprise': self.nom_entreprise,
            'adresse': self.adresse,
            'rc': self.rc,
            'nif': self.nif,
            'nis': self.nis,
            'art': self.art,
            'numero_secu_employeur': self.numero_secu_employeur,
            'telephone': self.telephone,
            'compte_bancaire': self.compte_bancaire,
            'banque': self.banque,
        }
