"""
Service de calcul des salaires v3.0 - Refonte complète
Remplace salary_engine et salaire_calculator
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List, Optional, Tuple
import calendar

from models import (
    Employe, Pointage, Mission, Avance, Credit, StatutCredit,
    ParametresSalaire, IRGBareme, ReportAvanceCredit, SituationFamiliale
)
from services.irg_calculator import get_irg_calculator


class SalaireProcessor:
    """
    Service de traitement des salaires mensuels
    Architecture claire, traçable et maintenable
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.params = self._get_parametres_salaire()
        self.irg_calculator = get_irg_calculator(db)
    
    def _get_parametres_salaire(self) -> ParametresSalaire:
        """Récupérer paramètres globaux ou créer défauts"""
        params = self.db.query(ParametresSalaire).first()
        if not params:
            params = ParametresSalaire()
            self.db.add(params)
            self.db.commit()
            self.db.refresh(params)
        return params
    
    def calculer_anciennete(self, date_recrutement: date, annee: int, mois: int) -> int:
        """Calculer ancienneté en années complètes"""
        if not date_recrutement:
            return 0
        
        date_calcul = date(annee, mois, 1)
        delta = date_calcul - date_recrutement
        return delta.days // 365
    
    def calculer_salaire_employe(
        self,
        employe_id: int,
        annee: int,
        mois: int,
        prime_objectif: Decimal = Decimal(0),
        prime_variable: Decimal = Decimal(0)
    ) -> Dict:
        """
        Calculer le salaire complet d'un employé
        Retourne dict avec tous les détails ou erreur
        """
        try:
            # 1. Récupérer employé
            employe = self.db.query(Employe).filter(
                Employe.id == employe_id,
                Employe.actif == True
            ).first()
            
            if not employe:
                return self._erreur_response(employe_id, "Employé non trouvé")
            
            # 2. Récupérer pointage
            pointage = self.db.query(Pointage).filter(
                Pointage.employe_id == employe_id,
                Pointage.annee == annee,
                Pointage.mois == mois
            ).first()
            
            if not pointage:
                return self._erreur_response(
                    employe_id,
                    f"Aucun pointage pour {mois}/{annee}",
                    employe.nom,
                    employe.prenom
                )
            
            # 3. Calcul ancienneté
            anciennete = self.calculer_anciennete(employe.date_recrutement, annee, mois)
            
            # 4. Calcul totaux pointage
            totaux = pointage.calculer_totaux()
            jours_travailles = totaux.get("jours_travailles", 0)
            heures_supplementaires_pointage = totaux.get("heures_supplementaires", 0)
            jours_ouvrables = 30  # v3.5.3: Base 30 jours au lieu de 26
            
            # ⭐ NOUVEAU v3.5.3: Récupérer les congés RÉELS depuis la table conges
            from models import Conge
            conge_record = self.db.query(Conge).filter(
                Conge.employe_id == employe_id,
                Conge.annee == annee,
                Conge.mois == mois
            ).first()
            
            jours_conges = float(conge_record.jours_conges_pris or 0) if conge_record else 0
            
            # 5. Calcul salaire de base proratisé
            salaire_base = Decimal(str(employe.salaire_base))
            
            # Si congés payés → pas de proratisation
            if jours_conges > 0:
                salaire_base_proratis = salaire_base
            else:
                salaire_base_proratis = (salaire_base / jours_ouvrables) * jours_travailles
            
            # 6. Heures supplémentaires
            heures_supp = Decimal(0)
            if self.params.activer_heures_supp and heures_supplementaires_pointage > 0:
                taux_horaire = salaire_base / (jours_ouvrables * 8)
                heures_supp = Decimal(str(heures_supplementaires_pointage)) * taux_horaire * Decimal('1.5')
            
            # 7. Primes COTISABLES (proratisées base 30 jours)
            # Si congés payés → montant plein, sinon proratisation
            facteur_proratisation = Decimal(1) if jours_conges > 0 else (Decimal(str(jours_travailles)) / Decimal('30'))
            
            indemnite_nuisance = (Decimal(str(self.params.indemnite_nuisance)) * facteur_proratisation).quantize(Decimal('0.01'), ROUND_HALF_UP)
            ifsp = (Decimal(str(self.params.ifsp)) * facteur_proratisation).quantize(Decimal('0.01'), ROUND_HALF_UP)
            iep = (Decimal(str(self.params.iep)) * facteur_proratisation).quantize(Decimal('0.01'), ROUND_HALF_UP) if anciennete >= 1 else Decimal(0)
            prime_encouragement = (Decimal(str(self.params.prime_encouragement)) * facteur_proratisation).quantize(Decimal('0.01'), ROUND_HALF_UP) if anciennete >= 1 else Decimal(0)
            
            # Primes conditionnelles (proratisées base 30 jours)
            prime_chauffeur = (Decimal(str(self.params.prime_chauffeur)) * facteur_proratisation).quantize(Decimal('0.01'), ROUND_HALF_UP) if employe.poste_travail == "Chauffeur" else Decimal(0)
            prime_nuit = (Decimal(str(self.params.prime_nuit_agent_securite)) * facteur_proratisation).quantize(Decimal('0.01'), ROUND_HALF_UP) if employe.prime_nuit_agent_securite else Decimal(0)
            
            # Prime déplacement (missions du mois)
            prime_deplacement = self._calculer_prime_missions(employe_id, annee, mois)
            
            # 8. Salaire cotisable
            salaire_cotisable = (
                salaire_base_proratis
                + heures_supp
                + indemnite_nuisance
                + ifsp
                + iep
                + prime_encouragement
                + prime_chauffeur
                + prime_nuit
                + prime_deplacement
                + prime_objectif
                + prime_variable
            )
            
            # 8. Retenue Sécurité Sociale (9%)
            taux_ss = Decimal(str(self.params.taux_securite_sociale)) / 100
            retenue_ss = (salaire_cotisable * taux_ss).quantize(Decimal('0.01'), ROUND_HALF_UP)
            
            # 9. Primes NON COTISABLES (proratisées base 30 jours)
            panier = (Decimal(str(self.params.panier)) * facteur_proratisation).quantize(Decimal('0.01'), ROUND_HALF_UP)
            prime_transport = (Decimal(str(self.params.prime_transport)) * facteur_proratisation).quantize(Decimal('0.01'), ROUND_HALF_UP)
            
            # 10. Salaire imposable
            salaire_imposable = salaire_cotisable - retenue_ss + panier + prime_transport
            
            # 11. IRG (proratisé selon jours travaillés)
            irg = self._calculer_irg_proratise(
                salaire_imposable,
                jours_travailles,
                employe.situation_familiale
            )
            
            # 12. Déductions (avances + crédits) avec gestion insuffisance
            deductions_data = self._calculer_deductions(
                employe_id,
                annee,
                mois,
                salaire_imposable - irg
            )
            
            # 13. Prime femme foyer (proratisée base 30 jours)
            prime_femme_foyer = (Decimal(str(self.params.prime_femme_foyer)) * facteur_proratisation).quantize(Decimal('0.01'), ROUND_HALF_UP) if employe.femme_au_foyer else Decimal(0)
            
            # 14. Salaire net final
            salaire_net = (
                salaire_imposable
                - irg
                - deductions_data['total_deduit']
                + prime_femme_foyer
            )
            
            # 15. Construire réponse complète
            return {
                "employe_id": employe.id,
                "employe_nom": employe.nom,
                "employe_prenom": employe.prenom,
                "annee": annee,
                "mois": mois,
                
                # Salaire de base
                "salaire_base": str(salaire_base),
                "salaire_base_proratis": str(salaire_base_proratis.quantize(Decimal('0.01'), ROUND_HALF_UP)),
                "jours_travailles": jours_travailles,
                "jours_conges": jours_conges,
                "jours_ouvrables_travailles": jours_ouvrables,
                "heures_supplementaires": str(heures_supp.quantize(Decimal('0.01'), ROUND_HALF_UP)),
                
                # Primes cotisables
                "indemnite_nuisance": str(indemnite_nuisance),
                "ifsp": str(ifsp),
                "iep": str(iep),
                "prime_encouragement": str(prime_encouragement),
                "prime_chauffeur": str(prime_chauffeur),
                "prime_nuit_agent_securite": str(prime_nuit),
                "prime_deplacement": str(prime_deplacement),
                "prime_objectif": str(prime_objectif),
                "prime_variable": str(prime_variable),
                
                # Cotisations
                "salaire_cotisable": str(salaire_cotisable.quantize(Decimal('0.01'), ROUND_HALF_UP)),
                "retenue_securite_sociale": str(retenue_ss),
                
                # Primes non cotisables
                "panier": str(panier),
                "prime_transport": str(prime_transport),
                
                # Imposable et IRG
                "salaire_imposable": str(salaire_imposable.quantize(Decimal('0.01'), ROUND_HALF_UP)),
                "irg": str(irg),
                
                # Déductions
                "total_avances": str(deductions_data['avances']),
                "retenue_credit": str(deductions_data['credits']),
                "avances_reportees": str(deductions_data['avances_reportees']),
                "credits_reportes": str(deductions_data['credits_reportes']),
                
                # Prime finale
                "prime_femme_foyer": str(prime_femme_foyer),
                
                # Résultat
                "salaire_net": str(salaire_net.quantize(Decimal('0.01'), ROUND_HALF_UP)),
                
                # Métadonnées
                "status": "OK",
                "error": None,
                "alerte": deductions_data.get('alerte'),
                
                # Détails calcul
                "details_calcul": {
                    "anciennete_annees": anciennete,
                    "nombre_missions_mois": deductions_data.get('nb_missions', 0),
                    "nombre_avances_mois": deductions_data.get('nb_avances', 0),
                    "nombre_credits_actifs": deductions_data.get('nb_credits', 0)
                }
            }
            
        except Exception as e:
            return self._erreur_response(employe_id, f"Erreur technique: {str(e)}")
    
    def _calculer_prime_missions(self, employe_id: int, annee: int, mois: int) -> Decimal:
        """Calculer prime de déplacement (missions du mois)"""
        missions = self.db.query(Mission).filter(
            Mission.chauffeur_id == employe_id,
            func.year(Mission.date_mission) == annee,
            func.month(Mission.date_mission) == mois
        ).all()
        
        total = sum(Decimal(str(m.prime_calculee or 0)) for m in missions)
        return total
    
    def _calculer_irg_proratise(
        self,
        salaire_imposable: Decimal,
        jours_travailles: int,
        situation_familiale: str
    ) -> Decimal:
        """
        Calculer IRG proratisé selon jours travaillés
        
        Logique:
        1. Le barème irg.xlsx contient les montants pour 1 mois complet (30 jours)
        2. Si l'employé a travaillé moins de 30 jours, il faut ajuster l'IRG
        3. Méthode: Extrapoler le salaire à 30 jours → chercher IRG → proratiser
        
        Exemple:
        - Employé travaille 20 jours, salaire imposable = 25,000 DA
        - Salaire extrapolé 30j = (25,000 / 20) × 30 = 37,500 DA
        - IRG pour 37,500 DA dans barème = 2,465 DA
        - IRG proratisé = (2,465 / 30) × 20 = 1,643 DA
        """
        if jours_travailles == 0:
            return Decimal(0)
        
        # Vérifier si proratisation activée dans paramètres
        if not self.params.activer_irg_proratise:
            # Mode simple: IRG direct sur salaire réel
            return self._calculer_irg_simple(salaire_imposable)
        
        # 1. Extrapoler à 30 jours
        salaire_30j = (salaire_imposable / Decimal(jours_travailles)) * Decimal(30)
        
        # 2. Chercher IRG pour salaire 30j
        irg_30j = self._calculer_irg_simple(salaire_30j)
        
        # 3. Proratiser IRG selon jours réellement travaillés
        irg_final = (irg_30j / Decimal(30)) * Decimal(jours_travailles)
        
        # Arrondir à l'entier (IRG sans décimales)
        return Decimal(int(irg_final.quantize(Decimal('1'), ROUND_HALF_UP)))
    
    def _calculer_irg_simple(self, salaire_imposable: Decimal) -> Decimal:
        """
        Calculer IRG selon barème depuis irg.xlsx (sans proratisation)
        Utilise IRGCalculator qui lit le fichier Excel
        """
        irg_base = self.irg_calculator.calculer_irg(salaire_imposable)
        return Decimal(str(irg_base)).quantize(Decimal('0.01'), ROUND_HALF_UP)
    
    def _calculer_deductions(
        self,
        employe_id: int,
        annee: int,
        mois: int,
        salaire_disponible: Decimal
    ) -> Dict:
        """
        Calculer déductions (avances + crédits)
        Gérer report si salaire insuffisant
        """
        # Avances du mois
        avances = self.db.query(Avance).filter(
            Avance.employe_id == employe_id,
            Avance.annee_deduction == annee,
            Avance.mois_deduction == mois
        ).all()
        total_avances = sum(Decimal(str(a.montant)) for a in avances)
        
        # Crédits actifs
        credits = self.db.query(Credit).filter(
            Credit.employe_id == employe_id,
            Credit.statut == StatutCredit.EN_COURS
        ).all()
        total_credits = sum(Decimal(str(c.montant_mensualite)) for c in credits)
        
        total_deductions = total_avances + total_credits
        
        # Vérifier suffisance salaire
        avances_reportees = Decimal(0)
        credits_reportes = Decimal(0)
        alerte = None
        
        if salaire_disponible < total_deductions:
            # Salaire insuffisant → limiter à 30% max
            deduction_max = salaire_disponible * Decimal('0.30')
            
            # Prioriser avances
            if total_avances > 0:
                if total_avances <= deduction_max:
                    avances_deduites = total_avances
                    deduction_max -= total_avances
                else:
                    avances_deduites = deduction_max
                    avances_reportees = total_avances - deduction_max
                    deduction_max = Decimal(0)
                    alerte = "AVANCES_REPORTEES"
            else:
                avances_deduites = Decimal(0)
            
            # Puis crédits
            if total_credits > 0 and deduction_max > 0:
                if total_credits <= deduction_max:
                    credits_deduits = total_credits
                else:
                    credits_deduits = deduction_max
                    credits_reportes = total_credits - deduction_max
                    alerte = "CREDITS_REPORTES" if not alerte else "AVANCES_ET_CREDITS_REPORTES"
            else:
                credits_deduits = Decimal(0) if total_credits > 0 else total_credits
                if total_credits > 0 and deduction_max == 0:
                    credits_reportes = total_credits
                    alerte = "CREDITS_REPORTES" if not alerte else "AVANCES_ET_CREDITS_REPORTES"
            
            total_deduit = avances_deduites + credits_deduits
        else:
            # Salaire suffisant
            avances_deduites = total_avances
            credits_deduits = total_credits
            total_deduit = total_deductions
        
        return {
            "avances": avances_deduites,
            "credits": credits_deduits,
            "total_deduit": total_deduit,
            "avances_reportees": avances_reportees,
            "credits_reportes": credits_reportes,
            "alerte": alerte,
            "nb_avances": len(avances),
            "nb_credits": len(credits),
            "nb_missions": 0  # Sera calculé ailleurs si nécessaire
        }
    
    def _erreur_response(
        self,
        employe_id: int,
        message: str,
        nom: str = "",
        prenom: str = ""
    ) -> Dict:
        """Réponse standardisée en cas d'erreur"""
        return {
            "employe_id": employe_id,
            "employe_nom": nom,
            "employe_prenom": prenom,
            "status": "ERROR",
            "error": message,
            "salaire_net": "0"
        }
    
    def calculer_tous_salaires(self, annee: int, mois: int) -> List[Dict]:
        """
        Calculer salaires de tous les employés actifs
        Retourne liste avec résultats ou erreurs
        """
        # Vider le cache SQLAlchemy pour forcer le rechargement des données
        self.db.expire_all()
        
        employes = self.db.query(Employe).filter(Employe.actif == True).all()
        resultats = []
        
        for employe in employes:
            resultat = self.calculer_salaire_employe(employe.id, annee, mois)
            resultats.append(resultat)
        
        return resultats
