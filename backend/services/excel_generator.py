import xlsxwriter
from io import BytesIO
from typing import List, Dict
from decimal import Decimal
from datetime import datetime


class ExcelGenerator:
    """Générateur de rapports Excel"""
    
    def generer_rapport_pointages_excel(
        self,
        pointages: List[Dict],
        annee: int,
        mois: int
    ) -> BytesIO:
        """Générer un rapport Excel des pointages"""
        
        buffer = BytesIO()
        workbook = xlsxwriter.Workbook(buffer, {'in_memory': True})
        worksheet = workbook.add_worksheet("Pointages")
        
        # Formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#366092',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter'
        })
        
        cell_format = workbook.add_format({
            'border': 1,
            'align': 'center'
        })
        
        # Titre
        worksheet.merge_range('A1:I1', f'ÉTAT DES POINTAGES - {self._nom_mois(mois)} {annee}', title_format)
        worksheet.write('A2', f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
        
        # En-têtes
        headers = [
            "ID", "Nom", "Prénom", "Jours Travaillés",
            "Absents", "Congés", "Maladie", "Féries", "Arrêts"
        ]
        
        row = 3
        for col, header in enumerate(headers):
            worksheet.write(row, col, header, header_format)
        
        # Données
        row = 4
        for p in pointages:
            totaux = p.get("totaux", {})
            worksheet.write(row, 0, p.get("employe_id", ""), cell_format)
            worksheet.write(row, 1, p.get("employe_nom", ""), cell_format)
            worksheet.write(row, 2, p.get("employe_prenom", ""), cell_format)
            worksheet.write(row, 3, totaux.get("total_travailles", 0), cell_format)
            worksheet.write(row, 4, totaux.get("absents", 0), cell_format)
            worksheet.write(row, 5, totaux.get("conges", 0), cell_format)
            worksheet.write(row, 6, totaux.get("maladies", 0), cell_format)
            worksheet.write(row, 7, totaux.get("feries", 0), cell_format)
            worksheet.write(row, 8, totaux.get("arrets", 0), cell_format)
            row += 1
        
        # Ajuster les largeurs de colonnes
        worksheet.set_column('A:A', 8)
        worksheet.set_column('B:C', 15)
        worksheet.set_column('D:I', 12)
        
        workbook.close()
        buffer.seek(0)
        return buffer
    
    def generer_rapport_salaires_excel(
        self,
        salaires: List[Dict],
        annee: int,
        mois: int,
        totaux: Dict[str, Decimal]
    ) -> BytesIO:
        """Générer un rapport Excel des salaires"""
        
        buffer = BytesIO()
        workbook = xlsxwriter.Workbook(buffer, {'in_memory': True})
        worksheet = workbook.add_worksheet("Salaires")
        
        # Formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#366092',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center'
        })
        
        cell_format = workbook.add_format({
            'border': 1
        })
        
        money_format = workbook.add_format({
            'border': 1,
            'num_format': '#,##0.00',
            'align': 'right'
        })
        
        total_format = workbook.add_format({
            'bold': True,
            'bg_color': '#d9e1f2',
            'border': 1,
            'num_format': '#,##0.00',
            'align': 'right'
        })
        
        # Titre
        worksheet.merge_range('A1:P1', f'ÉTAT DES SALAIRES - {self._nom_mois(mois)} {annee}', title_format)
        worksheet.write('A2', f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
        
        # En-têtes
        headers = [
            "Nom", "Prénom", "Poste", "Jours Trav.", "Sal. Base Proratisé",
            "H. Supp.", "IN", "IFSP", "IEP", "Prime Enc.", "Prime Ch.",
            "Prime Dép.", "Sal. Cotisable", "Ret. SS", "IRG",
            "Avances", "Crédit", "Sal. Net"
        ]
        
        row = 3
        for col, header in enumerate(headers):
            worksheet.write(row, col, header, header_format)
        
        # Données
        row = 4
        for s in salaires:
            worksheet.write(row, 0, s.get("employe_nom", ""), cell_format)
            worksheet.write(row, 1, s.get("employe_prenom", ""), cell_format)
            worksheet.write(row, 2, s.get("employe_poste", ""), cell_format)
            worksheet.write(row, 3, s.get("jours_travailles", 0), cell_format)
            worksheet.write(row, 4, float(s.get("salaire_base_proratis", 0)), money_format)
            worksheet.write(row, 5, float(s.get("heures_supplementaires", 0)), money_format)
            worksheet.write(row, 6, float(s.get("indemnite_nuisance", 0)), money_format)
            worksheet.write(row, 7, float(s.get("ifsp", 0)), money_format)
            worksheet.write(row, 8, float(s.get("iep", 0)), money_format)
            worksheet.write(row, 9, float(s.get("prime_encouragement", 0)), money_format)
            worksheet.write(row, 10, float(s.get("prime_chauffeur", 0)), money_format)
            worksheet.write(row, 11, float(s.get("prime_deplacement", 0)), money_format)
            worksheet.write(row, 12, float(s.get("salaire_cotisable", 0)), money_format)
            worksheet.write(row, 13, float(s.get("retenue_securite_sociale", 0)), money_format)
            worksheet.write(row, 14, float(s.get("irg", 0)), money_format)
            worksheet.write(row, 15, float(s.get("total_avances", 0)), money_format)
            worksheet.write(row, 16, float(s.get("retenue_credit", 0)), money_format)
            worksheet.write(row, 17, float(s.get("salaire_net", 0)), money_format)
            row += 1
        
        # Ligne de totaux
        row += 1
        worksheet.write(row, 0, "TOTAUX", header_format)
        worksheet.write(row, 1, "", header_format)
        worksheet.write(row, 2, "", header_format)
        worksheet.write(row, 3, "", header_format)
        worksheet.write(row, 12, float(totaux.get("salaire_cotisable", 0)), total_format)
        worksheet.write(row, 13, float(totaux.get("retenue_securite_sociale", 0)), total_format)
        worksheet.write(row, 14, float(totaux.get("irg", 0)), total_format)
        worksheet.write(row, 15, float(totaux.get("total_avances", 0)), total_format)
        worksheet.write(row, 16, float(totaux.get("retenue_credit", 0)), total_format)
        worksheet.write(row, 17, float(totaux.get("salaire_net", 0)), total_format)
        
        # Ajuster les largeurs de colonnes
        worksheet.set_column('A:B', 12)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 10)
        worksheet.set_column('E:R', 13)
        
        workbook.close()
        buffer.seek(0)
        return buffer
    
    def _nom_mois(self, mois: int) -> str:
        """Convertir le numéro de mois en nom"""
        mois_noms = [
            "", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
        ]
        return mois_noms[mois] if 1 <= mois <= 12 else str(mois)
