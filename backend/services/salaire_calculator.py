from decimal import Decimal
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Optional
import calendar

from models import (
    Employe, Pointage, Mission, Avance, Credit, RetenueCredit, 
    ProrogationCredit, StatutCredit, ParametresSalaire, IRGBareme
)
from .irg_calculator import get_irg_calculator


class SalaireCalculator:
    """Service de calcul des salaires V3.0"""
    
    def __init__(self, db: Session):
        self.db = db
        self.params = self._get_parametres_salaire()

    def _get_parametres_salaire(self) -> ParametresSalaire:
        """Récupérer les paramètres globaux ou créer les défauts"""
        params = self.db.query(ParametresSalaire).first()
        if not params:
            # Créer paramètres par défaut si inexistants
            params = ParametresSalaire()
            self.db.add(params)
            self.db.commit()
            self.db.refresh(params)
        return params
    
    def calculer_salaire(
        self,
        employe_id: int,
        annee: int,
        mois: int,
        jours_supplementaires: int = 0,
        prime_objectif: Decimal = Decimal(0),
        prime_variable: Decimal = Decimal(0),
        jours_conges: int = 0
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
        
        # ⭐ CORRECTION v3.6.1: Récupérer les congés dont le mois_deduction correspond au bulletin
        # Si mois_deduction est NULL, on utilise le mois d'acquisition (comportement par défaut)
        from models import Conge
        from sqlalchemy import or_, and_
        
        # Récupérer TOUS les congés dont la déduction pointe vers ce mois
        conges_a_deduire = self.db.query(Conge).filter(
            Conge.employe_id == employe_id,
            or_(
                # Cas 1: mois_deduction est défini et correspond au mois du bulletin
                and_(
                    Conge.mois_deduction == mois,
                    Conge.annee_deduction == annee
                ),
                # Cas 2: mois_deduction est NULL, on utilise le mois d'acquisition (ancien comportement)
                and_(
                    Conge.mois_deduction.is_(None),
                    Conge.mois == mois,
                    Conge.annee == annee
                )
            )
        ).all()
        
        # Somme de tous les jours de congés à déduire de CE bulletin
        jours_conges = sum(float(c.jours_conges_pris or 0) for c in conges_a_deduire)
        
        # Nombre de jours ouvrables du mois
        jours_ouvrables = self.params.jours_ouvrables_base
        
        # Calculer les jours ouvrables réellement travaillés (exclure les vendredis/fériés)
        # On estime qu'il y a 4-5 vendredis par mois, donc environ 4 jours fériés
        # Pour être précis, on compte les vendredis dans le mois
        import calendar
        _, nb_jours_mois = calendar.monthrange(annee, mois)
        jours_feries = sum(1 for jour in range(1, nb_jours_mois + 1) 
                          if calendar.weekday(annee, mois, jour) == 4)  # 4 = Vendredi
        
        # Jours ouvrables travaillés = total travaillés - jours fériés
        jours_ouvrables_travailles = max(0, jours_travailles - jours_feries)
        
        # 1. SALAIRE DE BASE AVEC CONGÉS
        salaire_base_proratis = self._calculer_salaire_avec_conges(
            employe, jours_travailles, jours_conges
        )
        
        # 2. HEURES SUPPLÉMENTAIRES
        heures_supplementaires = Decimal(0)
        if self.params.calculer_heures_supp:
            # Calcul: 34.67 heures pour 26 jours = 1.33346 heures par jour
            # Formule: jours × 1.33346h × taux horaire × 1.5 (majoration)
            # Taux horaire = salaire_base / 30 jours / 8 heures
            taux_horaire = employe.salaire_base / Decimal(30) / Decimal(8)
            heures_supp_par_jour = Decimal("1.33346")
            heures_supplementaires = (
                Decimal(jours_ouvrables_travailles) * 
                heures_supp_par_jour * 
                taux_horaire * 
                Decimal("1.5")  # 50% de majoration
            )
        
        # 3. INDEMNITÉ DE NUISANCE (IN)
        indemnite_nuisance = employe.salaire_base * (self.params.taux_in / Decimal(100))
        
        # 4. IFSP - Indemnité Forfaitaire de Service Permanent
        ifsp = employe.salaire_base * (self.params.taux_ifsp / Decimal(100))
        
        # 5. IEP - Indemnité d'Expérience Professionnelle
        # Calculer l'ancienneté en années
        anciennete = self._calculer_anciennete(employe.date_recrutement, annee, mois)
        iep = employe.salaire_base * Decimal(anciennete) * (self.params.taux_iep_par_an / Decimal(100))
        
        # 6. PRIME D'ENCOURAGEMENT
        prime_encouragement = Decimal(0)
        if anciennete >= self.params.anciennete_min_encouragement:
            prime_encouragement = employe.salaire_base * (self.params.taux_prime_encouragement / Decimal(100))
        
        # 7. PRIME CHAUFFEUR
        prime_chauffeur = Decimal(0)
        if "chauffeur" in (employe.poste_travail or "").lower():
            prime_chauffeur = self.params.prime_chauffeur_jour * Decimal(jours_travailles)
        
        # 8. PRIME DE NUIT AGENT SÉCURITÉ
        prime_nuit_agent_securite = Decimal(0)
        if employe.prime_nuit_agent_securite:
            prime_nuit_agent_securite = self.params.prime_nuit_securite
        
        # 9. PRIME DE DÉPLACEMENT (missions du mois)
        prime_deplacement = self._calculer_prime_deplacement(employe_id, annee, mois)
        
        # 10. SALAIRE COTISABLE (SANS panier et prime transport)
        salaire_cotisable = (
            salaire_base_proratis +
            heures_supplementaires +
            indemnite_nuisance +
            ifsp +
            iep +
            prime_encouragement +
            prime_chauffeur +
            prime_nuit_agent_securite +
            prime_deplacement +
            prime_objectif +
            prime_variable
        )
        
        # 11. RETENUE SÉCURITÉ SOCIALE
        retenue_securite_sociale = salaire_cotisable * (self.params.taux_securite_sociale / Decimal(100))
        
        # 12. PANIER
        panier = self.params.panier_jour * Decimal(jours_travailles)
        
        # 13. PRIME TRANSPORT
        prime_transport = self.params.transport_jour * Decimal(jours_travailles)
        
        # 14. SALAIRE IMPOSABLE
        salaire_imposable = salaire_cotisable - retenue_securite_sociale + panier + prime_transport
        
        # 15. CALCUL DE L'IRG PRORATISÉ
        irg = self._calculer_irg_proratise(salaire_imposable, jours_travailles)
        
        # 16. DÉDUCTIONS FINALES
        # Total des avances du mois
        total_avances = self._calculer_total_avances(employe_id, annee, mois)
        
        # Retenue crédit du mois
        retenue_credit = self._calculer_retenue_credit(employe_id, annee, mois)
        
        # 17. PRIME FEMME AU FOYER
        prime_femme_foyer = self.params.prime_femme_foyer if employe.femme_au_foyer else Decimal(0)
        
        # 17. SALAIRE NET FINAL
        salaire_net = salaire_imposable - irg - total_avances - retenue_credit + prime_femme_foyer
        
        return {
            "employe_id": employe_id,
            "annee": annee,
            "mois": mois,
            "jours_travailles": jours_travailles,
            "jours_conges": jours_conges,  # ⭐ AJOUTÉ v3.5.3: Congés pris ce mois
            "jours_ouvrables": jours_ouvrables,
            "salaire_base_proratis": salaire_base_proratis,
            "heures_supplementaires": heures_supplementaires,
            "indemnite_nuisance": indemnite_nuisance,
            "ifsp": ifsp,
            "iep": iep,
            "prime_encouragement": prime_encouragement,
            "prime_chauffeur": prime_chauffeur,
            "prime_nuit_agent_securite": prime_nuit_agent_securite,
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
        
        # Si l'employé est recruté après la date de calcul, ancienneté = 0
        if date_recrutement > date_calcul:
            return 0
        
        delta = date_calcul - date_recrutement
        annees = delta.days // 365
        return max(0, annees)  # S'assurer que l'ancienneté est toujours >= 0
    
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
        irg_calc = get_irg_calculator(self.db)  # CORRECTION: passer self.db
        return irg_calc.calculer_irg(salaire_brut)


    def _calculer_irg_proratise(self, salaire_imposable: Decimal, jours_travailles: int) -> Decimal:
        """Calcul d'IRG proratisé basé sur l'extrapolation à 30 jours"""
        if not self.params.irg_proratise or jours_travailles == 0:
            return self._calculer_irg(salaire_imposable)
        
        # Extrapoler à 30 jours
        salaire_30j = (salaire_imposable / Decimal(jours_travailles)) * Decimal(30)
        
        # IRG sur salaire 30j
        irg_30j = self._calculer_irg(salaire_30j)
        
        # Proratiser IRG : (IRG_30j / 30) * jours_travailles
        irg_final = (irg_30j / Decimal(30)) * Decimal(jours_travailles)
        
        # Arrondir (JAMAIS de décimales)
        return Decimal(int(irg_final))

    def _calculer_salaire_avec_conges(self, employe, jours_travailles: int, jours_conges: int) -> Decimal:
        """Calculer le salaire de base selon le mode de gestion des congés"""
        mode = self.params.mode_calcul_conges or "complet"
        salaire_base = employe.salaire_base
        
        if mode == "complet":
            # Salaire complet basé sur 30 jours (jours_travailles from pointage + jours_conges)
            jours_total = jours_travailles + jours_conges
            # Si le total dépasse 30, on plafonne à 30 jours pour le paiement complet
            jours_remunerables = min(30, jours_total) if jours_total > 30 else jours_total
            return salaire_base * Decimal(jours_remunerables) / Decimal(30)
            
        elif mode == "proratise":
            # Deux parts séparées
            part_travail = salaire_base * Decimal(jours_travailles) / Decimal(30)
            part_conges = salaire_base * Decimal(jours_conges) / Decimal(30)
            return part_travail + part_conges
            
        elif mode == "hybride":
            # Salaire sur jours ouvrables base (ex: 26)
            jours_base = self.params.jours_ouvrables_base or 26
            part_travail = salaire_base * Decimal(jours_travailles) / Decimal(jours_base)
            part_conges = salaire_base * Decimal(jours_conges) / Decimal(jours_base)
            return part_travail + part_conges
        
        return Decimal(0)
