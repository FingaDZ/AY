from decimal import Decimal
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Optional
import calendar

from models import (
    Employe, Pointage, Mission, Avance, Credit, RetenueCredit, 
    ProrogationCredit, StatutCredit
)
from .irg_calculator import get_irg_calculator


class SalaireCalculator:
    """Service de calcul des salaires"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculer_salaire(
        self,
        employe_id: int,
        annee: int,
        mois: int,
        jours_supplementaires: int = 0,
        prime_objectif: Decimal = Decimal(0),
        prime_variable: Decimal = Decimal(0)
    ) -> Dict:
        """
        Calculer le salaire complet d'un employé pour un mois donné
        """
        
        # Récupérer l'employé
        employe = self.db.query(Employe).filter(Employe.id == employe_id).first()
        if not employe:
            raise ValueError("Employé non trouvé")
        
        # Récupérer le pointage
        pointage = self.db.query(Pointage).filter(
            Pointage.employe_id == employe_id,
            Pointage.annee == annee,
            Pointage.mois == mois
        ).first()
        
        if not pointage:
            raise ValueError("Pointage non trouvé pour cette période")
        
        # Calculer les totaux du pointage
        totaux = pointage.calculer_totaux()
        jours_travailles = totaux["total_travailles"]  # Tr + Fe
        
        # Nombre de jours ouvrables du mois (on suppose 26 jours ouvrables)
        jours_ouvrables = 26
        
        # 1. SALAIRE DE BASE PRORATISÉ
        if jours_ouvrables > 0:
            salaire_base_proratis = employe.salaire_base * Decimal(jours_travailles) / Decimal(jours_ouvrables)
        else:
            salaire_base_proratis = Decimal(0)
        
        # 2. HEURES SUPPLÉMENTAIRES (50% de majoration)
        salaire_journalier = employe.salaire_base / Decimal(26)
        heures_supplementaires = Decimal(jours_supplementaires) * salaire_journalier * Decimal("1.5")
        
        # 3. INDEMNITÉ DE NUISANCE (IN) = 5% du salaire de base
        indemnite_nuisance = employe.salaire_base * Decimal("0.05")
        
        # 4. IFSP - Indemnité Forfaitaire de Service Permanent = 5% du salaire de base
        ifsp = employe.salaire_base * Decimal("0.05")
        
        # 5. IEP - Indemnité d'Expérience Professionnelle
        # Calculer l'ancienneté en années
        anciennete = self._calculer_anciennete(employe.date_recrutement, annee, mois)
        iep = employe.salaire_base * Decimal(anciennete) * Decimal("0.01")
        
        # 6. PRIME D'ENCOURAGEMENT (10% si > 1 an d'expérience)
        prime_encouragement = Decimal(0)
        if anciennete > 1:
            prime_encouragement = employe.salaire_base * Decimal("0.10")
        
        # 7. PRIME CHAUFFEUR (100 DA × jours travaillés si poste = Chauffeur)
        prime_chauffeur = Decimal(0)
        if "chauffeur" in employe.poste_travail.lower():
            prime_chauffeur = Decimal(100) * Decimal(jours_travailles)
        
        # 8. PRIME DE DÉPLACEMENT (missions du mois)
        prime_deplacement = self._calculer_prime_deplacement(employe_id, annee, mois)
        
        # 9. SALAIRE COTISABLE
        salaire_cotisable = (
            salaire_base_proratis +
            heures_supplementaires +
            indemnite_nuisance +
            ifsp +
            iep +
            prime_encouragement +
            prime_chauffeur +
            prime_deplacement +
            prime_objectif +
            prime_variable
        )
        
        # 10. RETENUE SÉCURITÉ SOCIALE (9% du salaire cotisable)
        retenue_securite_sociale = salaire_cotisable * Decimal("0.09")
        
        # 11. PANIER (100 DA × jours travaillés)
        panier = Decimal(100) * Decimal(jours_travailles)
        
        # 12. PRIME TRANSPORT (100 DA × jours travaillés)
        prime_transport = Decimal(100) * Decimal(jours_travailles)
        
        # 13. CALCUL DE L'IRG
        # Salaire brut pour IRG = Salaire cotisable + Panier + Prime Transport - Retenue SS
        salaire_brut_irg = salaire_cotisable + panier + prime_transport - retenue_securite_sociale
        irg = self._calculer_irg(salaire_brut_irg)
        
        # 14. SALAIRE IMPOSABLE
        salaire_imposable = salaire_cotisable + panier + prime_transport - retenue_securite_sociale - irg
        
        # 15. DÉDUCTIONS FINALES
        # Total des avances du mois
        total_avances = self._calculer_total_avances(employe_id, annee, mois)
        
        # Retenue crédit du mois
        retenue_credit = self._calculer_retenue_credit(employe_id, annee, mois)
        
        # 16. PRIME FEMME AU FOYER (1000 DA si applicable)
        prime_femme_foyer = Decimal(1000) if employe.femme_au_foyer else Decimal(0)
        
        # 17. SALAIRE NET FINAL
        salaire_net = salaire_imposable - total_avances - retenue_credit + prime_femme_foyer
        
        return {
            "employe_id": employe_id,
            "annee": annee,
            "mois": mois,
            "jours_travailles": jours_travailles,
            "jours_ouvrables": jours_ouvrables,
            "salaire_base_proratis": salaire_base_proratis,
            "heures_supplementaires": heures_supplementaires,
            "indemnite_nuisance": indemnite_nuisance,
            "ifsp": ifsp,
            "iep": iep,
            "prime_encouragement": prime_encouragement,
            "prime_chauffeur": prime_chauffeur,
            "prime_deplacement": prime_deplacement,
            "prime_objectif": prime_objectif,
            "prime_variable": prime_variable,
            "salaire_cotisable": salaire_cotisable,
            "retenue_securite_sociale": retenue_securite_sociale,
            "panier": panier,
            "prime_transport": prime_transport,
            "irg": irg,
            "salaire_imposable": salaire_imposable,
            "total_avances": total_avances,
            "retenue_credit": retenue_credit,
            "prime_femme_foyer": prime_femme_foyer,
            "salaire_net": salaire_net,
            # Informations supplémentaires
            "employe_nom": employe.nom,
            "employe_prenom": employe.prenom,
            "employe_poste": employe.poste_travail,
            "numero_compte": employe.numero_compte_bancaire,
            "date_naissance": employe.date_naissance,
            "lieu_naissance": employe.lieu_naissance,
            "situation_familiale": employe.situation_familiale.value,
            "telephone": employe.mobile,
            "date_recrutement": employe.date_recrutement,
            "date_fin_contrat": employe.date_fin_contrat,
            "numero_secu_sociale": employe.numero_secu_sociale,
        }
    
    def _calculer_anciennete(self, date_recrutement: date, annee: int, mois: int) -> int:
        """Calculer l'ancienneté en années"""
        date_calcul = date(annee, mois, 1)
        delta = date_calcul - date_recrutement
        annees = delta.days // 365
        return annees
    
    def _calculer_prime_deplacement(self, employe_id: int, annee: int, mois: int) -> Decimal:
        """Calculer le total des primes de déplacement du mois"""
        result = self.db.query(func.sum(Mission.prime_calculee)).filter(
            Mission.chauffeur_id == employe_id,
            func.year(Mission.date_mission) == annee,
            func.month(Mission.date_mission) == mois
        ).scalar()
        
        return result or Decimal(0)
    
    def _calculer_total_avances(self, employe_id: int, annee: int, mois: int) -> Decimal:
        """Calculer le total des avances à déduire pour le mois"""
        result = self.db.query(func.sum(Avance.montant)).filter(
            Avance.employe_id == employe_id,
            Avance.annee_deduction == annee,
            Avance.mois_deduction == mois
        ).scalar()
        
        return result or Decimal(0)
    
    def _calculer_retenue_credit(self, employe_id: int, annee: int, mois: int) -> Decimal:
        """Calculer la retenue de crédit pour le mois"""
        # Trouver les crédits en cours de l'employé
        credits = self.db.query(Credit).filter(
            Credit.employe_id == employe_id,
            Credit.statut == StatutCredit.EN_COURS
        ).all()
        
        total_retenue = Decimal(0)
        
        for credit in credits:
            # Vérifier s'il y a une prorogation pour ce mois
            prorogation = self.db.query(ProrogationCredit).filter(
                ProrogationCredit.credit_id == credit.id,
                ProrogationCredit.mois_initial == mois,
                ProrogationCredit.annee_initiale == annee
            ).first()
            
            if prorogation:
                # Pas de retenue ce mois-ci, elle est prorogée
                continue
            
            # Vérifier si une retenue existe déjà pour ce mois
            retenue_existante = self.db.query(RetenueCredit).filter(
                RetenueCredit.credit_id == credit.id,
                RetenueCredit.mois == mois,
                RetenueCredit.annee == annee
            ).first()
            
            if retenue_existante:
                total_retenue += retenue_existante.montant
            else:
                # Calculer la retenue à effectuer
                montant_restant = credit.montant_restant
                if montant_restant > 0:
                    montant_retenue = min(credit.montant_mensualite, montant_restant)
                    total_retenue += montant_retenue
                    
                    # Enregistrer la retenue
                    retenue = RetenueCredit(
                        credit_id=credit.id,
                        mois=mois,
                        annee=annee,
                        montant=montant_retenue,
                        date_retenue=date.today()
                    )
                    self.db.add(retenue)
                    
                    # Mettre à jour le crédit
                    credit.montant_retenu += montant_retenue
                    if credit.montant_retenu >= credit.montant_total:
                        credit.statut = StatutCredit.SOLDE
        
        self.db.commit()
        return total_retenue
    
    def _calculer_irg(self, salaire_brut: Decimal) -> Decimal:
        """
        Calculer l'IRG selon le barème fiscal depuis le fichier irg.xlsx
        """
        irg_calc = get_irg_calculator()
        return irg_calc.calculer_irg(salaire_brut)
