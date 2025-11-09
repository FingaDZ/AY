from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from datetime import datetime
from typing import List, Dict
from decimal import Decimal


class RapportGenerator:
    """Générateur de rapports PDF"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """Configurer les styles personnalisés"""
        # Style pour le titre
        self.styles.add(ParagraphStyle(
            name='TitreRapport',
            parent=self.styles['Title'],
            fontSize=16,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=20,
            alignment=1  # Centré
        ))
        
        # Style pour les sous-titres
        self.styles.add(ParagraphStyle(
            name='SousTitre',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#2e6ba6'),
            spaceAfter=10
        ))
    
    def generer_rapport_pointages(
        self,
        pointages: List[Dict],
        annee: int,
        mois: int
    ) -> BytesIO:
        """
        Générer un rapport PDF des pointages
        
        Args:
            pointages: Liste des données de pointage
            annee: Année du rapport
            mois: Mois du rapport
            
        Returns:
            BytesIO contenant le PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Contenu du rapport
        story = []
        
        # Titre
        titre = Paragraph(
            f"ÉTAT DES POINTAGES - {self._nom_mois(mois)} {annee}",
            self.styles['TitreRapport']
        )
        story.append(titre)
        story.append(Spacer(1, 0.5*cm))
        
        # Date de génération
        date_gen = Paragraph(
            f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
            self.styles['Normal']
        )
        story.append(date_gen)
        story.append(Spacer(1, 1*cm))
        
        # Tableau des pointages
        if pointages:
            data = self._preparer_donnees_pointages(pointages)
            table = Table(data, repeatRows=1)
            table.setStyle(self._style_tableau_pointages())
            story.append(table)
        else:
            story.append(Paragraph("Aucun pointage trouvé pour cette période.", self.styles['Normal']))
        
        # Générer le PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generer_rapport_salaires(
        self,
        salaires: List[Dict],
        annee: int,
        mois: int,
        totaux: Dict[str, Decimal]
    ) -> BytesIO:
        """
        Générer un rapport PDF des salaires
        
        Args:
            salaires: Liste des données de salaire
            annee: Année du rapport
            mois: Mois du rapport
            totaux: Totaux globaux
            
        Returns:
            BytesIO contenant le PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=0.5*cm,
            leftMargin=0.5*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # Titre
        titre = Paragraph(
            f"ÉTAT DES SALAIRES - {self._nom_mois(mois)} {annee}",
            self.styles['TitreRapport']
        )
        story.append(titre)
        story.append(Spacer(1, 0.5*cm))
        
        # Date de génération
        date_gen = Paragraph(
            f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
            self.styles['Normal']
        )
        story.append(date_gen)
        story.append(Spacer(1, 1*cm))
        
        # Tableau des salaires
        if salaires:
            data = self._preparer_donnees_salaires(salaires)
            table = Table(data, repeatRows=1)
            table.setStyle(self._style_tableau_salaires())
            story.append(table)
            story.append(Spacer(1, 1*cm))
            
            # Tableau des totaux
            data_totaux = self._preparer_totaux(totaux)
            table_totaux = Table(data_totaux)
            table_totaux.setStyle(self._style_tableau_totaux())
            story.append(table_totaux)
        else:
            story.append(Paragraph("Aucun salaire calculé pour cette période.", self.styles['Normal']))
        
        # Générer le PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _preparer_donnees_pointages(self, pointages: List[Dict]) -> List[List]:
        """Préparer les données pour le tableau de pointages"""
        # En-tête
        headers = [
            "ID", "Nom", "Prénom", "Jours\nTravaillés",
            "Absents", "Congés", "Maladie", "Féries", "Arrêts"
        ]
        
        data = [headers]
        
        # Lignes de données
        for p in pointages:
            totaux = p.get("totaux", {})
            row = [
                str(p.get("employe_id", "")),
                p.get("employe_nom", ""),
                p.get("employe_prenom", ""),
                str(totaux.get("total_travailles", 0)),
                str(totaux.get("absents", 0)),
                str(totaux.get("conges", 0)),
                str(totaux.get("maladies", 0)),
                str(totaux.get("feries", 0)),
                str(totaux.get("arrets", 0)),
            ]
            data.append(row)
        
        return data
    
    def _preparer_donnees_salaires(self, salaires: List[Dict]) -> List[List]:
        """Préparer les données pour le tableau de salaires"""
        # En-tête
        headers = [
            "Nom", "Prénom", "Sal. Cotisable", "Ret. SS",
            "IRG", "Sal. Imposable", "Avances", "Crédit", "Sal. Net"
        ]
        
        data = [headers]
        
        # Lignes de données
        for s in salaires:
            row = [
                s.get("employe_nom", ""),
                s.get("employe_prenom", ""),
                f"{float(s.get('salaire_cotisable', 0)):,.2f}",
                f"{float(s.get('retenue_securite_sociale', 0)):,.2f}",
                f"{float(s.get('irg', 0)):,.2f}",
                f"{float(s.get('salaire_imposable', 0)):,.2f}",
                f"{float(s.get('total_avances', 0)):,.2f}",
                f"{float(s.get('retenue_credit', 0)):,.2f}",
                f"{float(s.get('salaire_net', 0)):,.2f}",
            ]
            data.append(row)
        
        return data
    
    def _preparer_totaux(self, totaux: Dict[str, Decimal]) -> List[List]:
        """Préparer les données pour le tableau des totaux"""
        data = [
            ["TOTAUX GÉNÉRAUX", ""],
            ["Total Salaire Cotisable", f"{float(totaux.get('salaire_cotisable', 0)):,.2f} DA"],
            ["Total Retenue SS", f"{float(totaux.get('retenue_securite_sociale', 0)):,.2f} DA"],
            ["Total IRG", f"{float(totaux.get('irg', 0)):,.2f} DA"],
            ["Total Avances", f"{float(totaux.get('total_avances', 0)):,.2f} DA"],
            ["Total Retenues Crédits", f"{float(totaux.get('retenue_credit', 0)):,.2f} DA"],
            ["Total Salaire Imposable", f"{float(totaux.get('salaire_imposable', 0)):,.2f} DA"],
            ["Total Salaire Net", f"{float(totaux.get('salaire_net', 0)):,.2f} DA"],
        ]
        return data
    
    def _style_tableau_pointages(self) -> TableStyle:
        """Style pour le tableau des pointages"""
        return TableStyle([
            # En-tête
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Corps
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ])
    
    def _style_tableau_salaires(self) -> TableStyle:
        """Style pour le tableau des salaires"""
        return TableStyle([
            # En-tête
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Corps
            ('ALIGN', (0, 1), (1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
        ])
    
    def _style_tableau_totaux(self) -> TableStyle:
        """Style pour le tableau des totaux"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e6ba6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ])
    
    def _nom_mois(self, mois: int) -> str:
        """Convertir le numéro de mois en nom"""
        mois_noms = [
            "", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
        ]
        return mois_noms[mois] if 1 <= mois <= 12 else str(mois)
