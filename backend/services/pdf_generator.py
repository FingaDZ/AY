"""Service pour générer des PDFs pour les ordres de mission et rapports"""

from reportlab.lib.pagesizes import A4, A5
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from io import BytesIO
from typing import List, Dict, Optional
import qrcode
from sqlalchemy.orm import Session
from models import Parametres


class PDFGenerator:
    """Générateur de PDFs pour les missions"""
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        self._parametres = None
    
    def _get_parametres(self) -> Optional[Parametres]:
        """Récupérer les paramètres de l'entreprise"""
        if self._parametres is None and self.db:
            self._parametres = self.db.query(Parametres).first()
        return self._parametres
    
    def _setup_styles(self):
        """Configurer les styles personnalisés"""
        # Style pour le titre (noir, sans couleur)
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=14,
            textColor=colors.black,
            spaceAfter=20,
            alignment=TA_CENTER,
        ))
        
        # Style pour les sous-titres
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=10,
            textColor=colors.black,
            spaceAfter=8,
        ))
        
        # Style pour le texte normal
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=8,
        ))
        
        # Style pour le footer
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=7,
            textColor=colors.grey,
            alignment=TA_CENTER,
        ))
    
    def _create_company_header(self, include_details=True) -> List:
        """Créer l'en-tête avec les informations de l'entreprise"""
        elements = []
        params = self._get_parametres()
        
        if params:
            company_name = params.raison_sociale or params.nom_entreprise or "AY HR"
            
            # Titre principal
            elements.append(Paragraph(f"<b>{company_name}</b>", self.styles['CustomTitle']))
            
            if include_details:
                # Détails de l'entreprise
                details = []
                if params.adresse:
                    details.append(params.adresse)
                if params.telephone:
                    details.append(f"Tél: {params.telephone}")
                
                detail_text = " | ".join(details)
                if detail_text:
                    detail_style = ParagraphStyle(
                        name='CompanyDetails',
                        parent=self.styles['Normal'],
                        fontSize=8,
                        alignment=TA_CENTER,
                        spaceAfter=4
                    )
                    elements.append(Paragraph(detail_text, detail_style))
                
                # Identifiants
                ids = []
                if params.rc:
                    ids.append(f"RC: {params.rc}")
                if params.nif:
                    ids.append(f"NIF: {params.nif}")
                if params.nis:
                    ids.append(f"NIS: {params.nis}")
                
                id_text = " | ".join(ids)
                if id_text:
                    id_style = ParagraphStyle(
                        name='CompanyIds',
                        parent=self.styles['Normal'],
                        fontSize=7,
                        alignment=TA_CENTER,
                        spaceAfter=10
                    )
                    elements.append(Paragraph(id_text, id_style))
        
        return elements
    
    def _create_footer(self) -> Paragraph:
        """Créer le footer 'Powered by AIRBAND'"""
        return Paragraph("Powered by AIRBAND", self.styles['Footer'])
    
    def _generate_ordre_numero(self, mission_id: int, date_mission: str) -> str:
        """
        Générer le numéro d'ordre au format YYMMDD-XXXXX
        Le compteur se réinitialise chaque mois
        
        Args:
            mission_id: ID de la mission
            date_mission: Date de la mission (format YYYY-MM-DD)
        
        Returns:
            str: Numéro d'ordre au format YYMMDD-XXXXX
        """
        date_obj = datetime.strptime(date_mission, '%Y-%m-%d')
        yymmdd = date_obj.strftime('%y%m%d')
        # Pour le compteur mensuel, on utilise simplement l'ID formaté sur 5 chiffres
        # Note: Dans une vraie application, il faudrait compter les missions du mois
        return f"{yymmdd}-{mission_id:05d}"
    
    def generate_ordre_mission(self, mission_data: Dict) -> BytesIO:
        """
        Générer un ordre de mission PDF pour un chauffeur (format A5)
        
        Args:
            mission_data: Dict contenant les données de la mission
                - id: ID de la mission
                - date_mission: Date de la mission
                - chauffeur_nom: Nom du chauffeur
                - chauffeur_prenom: Prénom du chauffeur
                - client_nom: Nom du client
                - client_prenom: Prénom du client
                - distance: Distance en km
                - prime_calculee: Prime calculée
        
        Returns:
            BytesIO: Buffer contenant le PDF
        """
        buffer = BytesIO()
        # Format A5 (148mm × 210mm) avec marges réduites
        doc = SimpleDocTemplate(buffer, pagesize=A5, topMargin=1*cm, bottomMargin=1*cm, 
                                leftMargin=1*cm, rightMargin=1*cm)
        
        story = []
        
        # En-tête avec numéro d'ordre sur la même ligne
        ordre_num = self._generate_ordre_numero(mission_data['id'], mission_data['date_mission'])
        
        # Tableau pour l'en-tête (titre et numéro sur même ligne)
        header_data = [
            ['ORDRE DE MISSION', f'N° {ordre_num}']
        ]
        
        # Largeur disponible: A5 = 14.8cm - 2cm marges = 12.8cm
        header_table = Table(header_data, colWidths=[8*cm, 4.8*cm])
        header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 14),
            ('FONTSIZE', (1, 0), (1, 0), 10),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 0.3*cm))
        
        # Date juste en dessous du titre
        date_str = datetime.strptime(mission_data['date_mission'], '%Y-%m-%d').strftime('%d/%m/%Y')
        date_para = Paragraph(
            f"<b>Date:</b> {date_str}",
            self.styles['CustomBody']
        )
        story.append(date_para)
        story.append(Spacer(1, 0.5*cm))
        
        # Tableau des informations (3 lignes)
        # Ligne 1: CHAUFFEUR -- Nom et prénom
        # Ligne 2: Destination -- Nom et prénom du client
        # Ligne 3: Prime -- Montant
        
        info_data = [
            ['CHAUFFEUR', f"{mission_data['chauffeur_prenom']} {mission_data['chauffeur_nom']}"],
            ['Destination', f"{mission_data['client_prenom']} {mission_data['client_nom']}"],
            ['Prime', f"{mission_data['prime_calculee']:.2f} DA"],
        ]
        
        # Largeurs dynamiques pour éviter chevauchement
        # Colonne 1: 3.5cm pour les labels
        # Colonne 2: 9.3cm pour le contenu (12.8cm - 3.5cm)
        info_table = Table(info_data, colWidths=[3.5*cm, 9.3*cm])
        info_table.setStyle(TableStyle([
            # En-tête de chaque ligne en gras
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            # Bordures
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            # Padding pour éviter le chevauchement
            ('PADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            # Alignement
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.8*cm))
        
        # Signatures (3 colonnes: chauffeur, client, responsable)
        signatures = [
            ['Signature chauffeur', 'Signature client', 'Signature responsable'],
            ['', '', ''],
            ['', '', ''],
        ]
        
        sig_table = Table(signatures, colWidths=[4.27*cm, 4.27*cm, 4.26*cm])
        sig_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 1), (-1, 2), 1*cm),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(sig_table)
        
        # Générer le PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    def generate_rapport_missions(self, missions: List[Dict], filters: Dict = None) -> BytesIO:
        """
        Générer un rapport PDF des missions filtrées
        
        Args:
            missions: Liste des missions à inclure
            filters: Filtres appliqués (optionnel)
        
        Returns:
            BytesIO: Buffer contenant le PDF
        """
        buffer = BytesIO()
        # Format A4 avec marges de 1cm (comme l'ordre de mission)
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4, 
            topMargin=1*cm, 
            bottomMargin=1*cm,
            leftMargin=1*cm,
            rightMargin=1*cm
        )
        
        story = []
        
        # Largeur disponible A4: 21cm - 2cm marges = 19cm
        available_width = 19*cm
        
        # En-tête avec nombre de missions (sur même ligne)
        header_data = [
            ['RAPPORT DES MISSIONS', f'Total: {len(missions)} mission(s)']
        ]
        header_table = Table(header_data, colWidths=[13*cm, 6*cm])
        header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 14),
            ('FONTSIZE', (1, 0), (1, 0), 10),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 0.3*cm))
        
        # Date de génération juste en dessous
        date_generation = datetime.now().strftime('%d/%m/%Y %H:%M')
        date_para = Paragraph(
            f"<b>Généré le:</b> {date_generation}",
            self.styles['CustomBody']
        )
        story.append(date_para)
        
        # Période si filtre
        if filters and filters.get('date_debut') and filters.get('date_fin'):
            date_debut = datetime.strptime(filters['date_debut'], '%Y-%m-%d').strftime('%d/%m/%Y')
            date_fin = datetime.strptime(filters['date_fin'], '%Y-%m-%d').strftime('%d/%m/%Y')
            periode = Paragraph(
                f"<b>Période:</b> du {date_debut} au {date_fin}",
                self.styles['CustomBody']
            )
            story.append(periode)
        
        story.append(Spacer(1, 0.5*cm))
        
        # Tableau des missions (noir et blanc, pas de couleurs)
        data = [['Date', 'Chauffeur', 'Client', 'Distance\n(km)', 'Prime\n(DA)']]
        
        total_distance = 0
        total_primes = 0
        
        for mission in missions:
            date_str = datetime.strptime(mission['date_mission'], '%Y-%m-%d').strftime('%d/%m/%Y')
            chauffeur = f"{mission['chauffeur_prenom']} {mission['chauffeur_nom']}"
            client = f"{mission['client_prenom']} {mission['client_nom']}"
            distance = float(mission['distance'])
            prime = float(mission['prime_calculee'])
            
            data.append([
                date_str,
                chauffeur,
                client,
                f"{distance:.2f}",
                f"{prime:.2f}"
            ])
            
            total_distance += distance
            total_primes += prime
        
        # Ligne de totaux
        data.append([
            'TOTAL',
            '',
            '',
            f"{total_distance:.2f}",
            f"{total_primes:.2f}"
        ])
        
        # Créer le tableau avec largeurs dynamiques (19cm disponibles)
        # Date: 2.5cm, Chauffeur: 5cm, Client: 5cm, Distance: 3.25cm, Prime: 3.25cm
        col_widths = [2.5*cm, 5*cm, 5*cm, 3.25*cm, 3.25*cm]
        table = Table(data, colWidths=col_widths)
        
        # Style du tableau (noir et blanc, sans couleurs)
        style_list = [
            # En-tête (fond gris clair au lieu de bleu)
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            
            # Corps
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 9),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Date centrée
            ('ALIGN', (1, 1), (2, -2), 'LEFT'),    # Noms alignés à gauche
            ('ALIGN', (3, 1), (4, -2), 'RIGHT'),   # Chiffres alignés à droite
            
            # Ligne de total (gris clair)
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 10),
            ('ALIGN', (0, -1), (0, -1), 'CENTER'),
            ('ALIGN', (3, -1), (4, -1), 'RIGHT'),
            
            # Grille (noir)
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Padding augmenté pour éviter chevauchement
            ('PADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]
        
        table.setStyle(TableStyle(style_list))
        story.append(table)
        
        # Générer le PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer

    def generate_credits_pdf(self, credits: List[Dict], filters: Dict = None) -> BytesIO:
        """
        Générer un PDF pour la liste des crédits
        
        Args:
            credits: Liste des crédits avec leurs informations
            filters: Filtres appliqués (optionnel)
        
        Returns:
            BytesIO: Buffer contenant le PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )
        
        story = []
        
        # Titre principal
        titre = Paragraph("LISTE DES CRÉDITS SALARIAUX", self.styles['CustomTitle'])
        story.append(titre)
        story.append(Spacer(1, 0.5*cm))
        
        # Informations de génération
        date_generation = datetime.now().strftime("%d/%m/%Y à %H:%M")
        info = Paragraph(
            f"<b>Date de génération:</b> {date_generation}",
            self.styles['CustomBody']
        )
        story.append(info)
        
        # Filtres appliqués
        if filters:
            filter_text = "<b>Filtres appliqués:</b> "
            filter_parts = []
            if filters.get('employe_nom'):
                filter_parts.append(f"Employé: {filters['employe_nom']}")
            if filters.get('statut'):
                filter_parts.append(f"Statut: {filters['statut']}")
            
            if filter_parts:
                filter_text += ", ".join(filter_parts)
                filter_info = Paragraph(filter_text, self.styles['CustomBody'])
                story.append(filter_info)
        
        story.append(Spacer(1, 0.5*cm))
        
        # Résumé statistique
        total_credits = len(credits)
        en_cours = sum(1 for c in credits if c['statut'] == 'En cours')
        soldes = sum(1 for c in credits if c['statut'] == 'Soldé')
        montant_total = sum(float(c['montant_total']) for c in credits)
        montant_retenu = sum(float(c['montant_retenu']) for c in credits)
        montant_restant = montant_total - montant_retenu
        
        resume = Paragraph(
            f"<b>Résumé:</b> {total_credits} crédit(s) | "
            f"En cours: {en_cours} | Soldés: {soldes} | "
            f"<b>Total:</b> {montant_total:,.2f} DA | "
            f"<b>Retenu:</b> {montant_retenu:,.2f} DA | "
            f"<b>Restant:</b> {montant_restant:,.2f} DA",
            self.styles['CustomBody']
        )
        story.append(resume)
        story.append(Spacer(1, 0.5*cm))
        
        # Tableau des crédits
        data = [
            ['N°', 'Employé', 'Date', 'Montant\nTotal', 'Mens.', 'Retenu', 'Restant', 'Statut']
        ]
        
        for i, credit in enumerate(credits, 1):
            montant_total_credit = float(credit['montant_total'])
            montant_retenu_credit = float(credit['montant_retenu'])
            montant_restant_credit = montant_total_credit - montant_retenu_credit
            
            data.append([
                str(i),
                credit['employe_nom'],
                credit['date_octroi'],
                f"{montant_total_credit:,.0f}".replace(',', ' '),
                str(credit['nombre_mensualites']),
                f"{montant_retenu_credit:,.0f}".replace(',', ' '),
                f"{montant_restant_credit:,.0f}".replace(',', ' '),
                credit['statut']
            ])
        
        # Créer le tableau
        table = Table(data, colWidths=[
            0.8*cm,  # N°
            4.5*cm,  # Employé
            2*cm,    # Date
            2.3*cm,  # Montant Total
            1.3*cm,  # Mensualités
            2.3*cm,  # Retenu
            2.3*cm,  # Restant
            1.9*cm   # Statut
        ])
        
        # Style du tableau (noir et blanc)
        style_list = [
            # En-tête (gris foncé)
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#404040')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Corps du tableau
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # N°
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Employé
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Date
            ('ALIGN', (3, 1), (-2, -1), 'RIGHT'),  # Montants
            ('ALIGN', (-1, 1), (-1, -1), 'CENTER'),# Statut
            
            # Alternance de couleurs (gris clair)
            *[('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f0f0f0'))
              for i in range(2, len(data), 2)],
            
            # Grille
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Padding
            ('PADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]
        
        table.setStyle(TableStyle(style_list))
        story.append(table)
        
        # Pied de page avec informations
        story.append(Spacer(1, 0.8*cm))
        footer = Paragraph(
            "<b>Légende:</b> Mens. = Nombre de mensualités | "
            "Retenu = Montant déjà remboursé | "
            "Restant = Montant restant à rembourser",
            ParagraphStyle(
                'Footer',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_LEFT
            )
        )
        story.append(footer)
        
        # Générer le PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer

    def generate_bulletin_paie(self, employe_data: Dict, salaire_data: Dict, periode: Dict) -> BytesIO:
        """
        Générer un bulletin de paie individuel
        
        Args:
            employe_data: Informations de l'employé
            salaire_data: Détails du calcul du salaire
            periode: {'mois': int, 'annee': int}
        """
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )
        
        story = []
        
        # Générer QR Code avec salaire net
        salaire_net_format = f"{float(salaire_data.get('salaire_net', 0)):,.2f}".replace(',', ' ')
        qr_data = f"ID: {employe_data.get('id', '')}\n" \
                  f"Nom: {employe_data.get('prenom', '')} {employe_data.get('nom', '')}\n" \
                  f"N°SS: {employe_data.get('numero_secu_sociale', 'N/A')}\n" \
                  f"Recrutement: {employe_data.get('date_recrutement', 'N/A')}\n" \
                  f"Salaire Net: {salaire_net_format} DA"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=1)
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Sauvegarder QR dans un buffer
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        qr_image = Image(qr_buffer, width=2*cm, height=2*cm)
        
        # En-tête avec titre et QR code
        header_data = [
            [Paragraph("<b>BULLETIN DE PAIE</b>", self.styles['CustomTitle']), qr_image]
        ]
        header_table = Table(header_data, colWidths=[15*cm, 3*cm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 0.3*cm))
        
        # Période
        mois_nom = datetime(periode['annee'], periode['mois'], 1).strftime('%B %Y').capitalize()
        periode_text = Paragraph(
            f"<b>Période:</b> {mois_nom}",
            self.styles['CustomBody']
        )
        story.append(periode_text)
        story.append(Spacer(1, 0.5*cm))
        
        # Récupérer les paramètres de l'entreprise
        params = self._get_parametres()
        company_name = params.raison_sociale or params.nom_entreprise or "AY HR Management" if params else "AY HR Management"
        company_address = params.adresse or "Alger, Algérie" if params else "Alger, Algérie"
        company_cnas = params.numero_cnas or "000000000000000" if params else "000000000000000"
        
        # Fusionner tableaux EMPLOYEUR et EMPLOYÉ côte à côte
        info_data = [
            # En-têtes fusionnés
            [Paragraph("<b>EMPLOYEUR</b>", self.styles['CustomBody']), '', 
             Paragraph("<b>EMPLOYÉ</b>", self.styles['CustomBody']), ''],
            # Lignes de données
            ['Raison Sociale:', company_name,
             'Nom:', f"{employe_data.get('prenom', '')} {employe_data.get('nom', '')}"],
            ['Adresse:', company_address,
             'Poste:', employe_data.get('poste_travail', '')],
            ['CNAS:', company_cnas,
             'N° Sécurité Sociale:', employe_data.get('numero_secu_sociale', 'N/A')],
            ['', '',
             'Date de recrutement:', str(employe_data.get('date_recrutement', 'N/A'))],
        ]
        
        info_table = Table(info_data, colWidths=[3.5*cm, 5*cm, 3.5*cm, 6*cm])
        info_table.setStyle(TableStyle([
            # En-têtes
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#404040')),
            ('BACKGROUND', (2, 0), (3, 0), colors.HexColor('#404040')),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.white),
            ('TEXTCOLOR', (2, 0), (3, 0), colors.white),
            ('FONTNAME', (0, 0), (3, 0), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (3, 0), 'CENTER'),
            # Corps
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Tableau détaillé du salaire (sans en-tête "DÉTAIL DU SALAIRE")
        salaire_detail_data = [
            ['DÉSIGNATION', 'BASE', 'TAUX', 'GAIN', 'RETENUE'],
            # Salaire de base
            ['Salaire de base (contrat)', 
             f"{float(employe_data.get('salaire_base', 0)):,.2f}".replace(',', ' '),
             f"{salaire_data.get('jours_travailles', 0)}/{salaire_data.get('jours_ouvrables', 26)} j",
             f"{float(salaire_data.get('salaire_base_proratis', 0)):,.2f}".replace(',', ' '),
             ''],
            # Heures supplémentaires
            ['Heures supplémentaires (1.33h/j × 150%)',
             '',
             '',
             f"{float(salaire_data.get('heures_supplementaires', 0)):,.2f}".replace(',', ' '),
             ''],
            # Indemnités
            ['Indemnité de Nuisance (IN)',
             f"{float(employe_data.get('salaire_base', 0)):,.2f}".replace(',', ' '),
             '5%',
             f"{float(salaire_data.get('indemnite_nuisance', 0)):,.2f}".replace(',', ' '),
             ''],
            ['Indemnité Forfaitaire Service Permanent (IFSP)',
             f"{float(employe_data.get('salaire_base', 0)):,.2f}".replace(',', ' '),
             '5%',
             f"{float(salaire_data.get('ifsp', 0)):,.2f}".replace(',', ' '),
             ''],
            ['Indemnité Expérience Professionnelle (IEP)',
             f"{float(employe_data.get('salaire_base', 0)):,.2f}".replace(',', ' '),
             'Ancienneté',
             f"{float(salaire_data.get('iep', 0)):,.2f}".replace(',', ' '),
             ''],
            # Primes
            ['Prime d\'Encouragement',
             '',
             '10%',
             f"{float(salaire_data.get('prime_encouragement', 0)):,.2f}".replace(',', ' '),
             ''],
            ['Prime Chauffeur',
             '',
             '100 DA/j',
             f"{float(salaire_data.get('prime_chauffeur', 0)):,.2f}".replace(',', ' '),
             ''],
            ['Prime de Nuit Agent Sécurité',
             '',
             '750 DA/mois',
             f"{float(salaire_data.get('prime_nuit_agent_securite', 0)):,.2f}".replace(',', ' '),
             ''],
            ['Prime de Déplacement (Missions)',
             '',
             '',
             f"{float(salaire_data.get('prime_deplacement', 0)):,.2f}".replace(',', ' '),
             ''],
            # Ligne de total brut (SALAIRE COTISABLE)
            ['SALAIRE COTISABLE', '', '', 
             f"{float(salaire_data.get('salaire_cotisable', 0)):,.2f}".replace(',', ' '), 
             ''],
            # Retenue SS
            ['Retenue Sécurité Sociale',
             f"{float(salaire_data.get('salaire_cotisable', 0)):,.2f}".replace(',', ' '),
             '9%',
             '',
             f"{float(salaire_data.get('retenue_securite_sociale', 0)):,.2f}".replace(',', ' ')],
            # ÉLÉMENTS IMPOSABLES NON COTISABLES
            ['Panier (imposable non cotisable)',
             '',
             '100 DA/j',
             f"{float(salaire_data.get('panier', 0)):,.2f}".replace(',', ' '),
             ''],
            ['Prime de Transport (imposable non cotisable)',
             '',
             '100 DA/j',
             f"{float(salaire_data.get('prime_transport', 0)):,.2f}".replace(',', ' '),
             ''],
            # SALAIRE IMPOSABLE après retenue SS + panier + transport
            ['SALAIRE IMPOSABLE', '', '', 
             f"{float(salaire_data.get('salaire_imposable', 0)):,.2f}".replace(',', ' '), 
             ''],
            ['IRG (Impôt sur le Revenu Global)',
             '',
             'Barème',
             '',
             f"{float(salaire_data.get('irg', 0)):,.2f}".replace(',', ' ')],
            ['Avances sur salaire',
             '',
             '',
             '',
             f"{float(salaire_data.get('total_avances', 0)):,.2f}".replace(',', ' ')],
            ['Retenue Crédit',
             '',
             '',
             '',
             f"{float(salaire_data.get('retenue_credit', 0)):,.2f}".replace(',', ' ')],
            # Prime finale
            ['Prime Femme au Foyer',
             '',
             '',
             f"{float(salaire_data.get('prime_femme_foyer', 0)):,.2f}".replace(',', ' '),
             ''],
        ]
        
        salaire_table = Table(salaire_detail_data, colWidths=[6*cm, 3.5*cm, 2.5*cm, 3*cm, 3*cm])
        
        table_style = [
            # En-tête
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#404040')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Corps
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            
            # Ligne salaire cotisable (row 12)
            ('BACKGROUND', (0, 12), (-1, 12), colors.HexColor('#e6f2ff')),
            ('FONTNAME', (0, 12), (-1, 12), 'Helvetica-Bold'),
            
            # Ligne salaire imposable (row 14)
            ('BACKGROUND', (0, 14), (-1, 14), colors.HexColor('#fff7e6')),
            ('FONTNAME', (0, 14), (-1, 14), 'Helvetica-Bold'),
            
            # Grille
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ]
        
        salaire_table.setStyle(TableStyle(table_style))
        story.append(salaire_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Total final
        total_data = [
            ['SALAIRE NET À PAYER', 
             f"{float(salaire_data.get('salaire_net', 0)):,.2f}".replace(',', ' ') + ' DA'],
        ]
        
        total_table = Table(total_data, colWidths=[12*cm, 6*cm])
        total_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#52c41a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(total_table)
        
        # Pied de page
        story.append(Spacer(1, 0.5*cm))
        footer = Paragraph(
            f"<i>Bulletin généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</i><br/>"
            "<i>Ce bulletin ne doit pas être divulgué à des tiers.</i>",
            ParagraphStyle(
                'FooterInfo',
                parent=self.styles['Normal'],
                fontSize=7,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
        )
        story.append(footer)
        story.append(Spacer(1, 0.3*cm))
        
        # Footer "Powered by AIRBAND"
        story.append(self._create_footer())
        
        # Générer le PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer

    def generate_rapport_salaires(self, salaires_data: List[Dict], periode: Dict, totaux: Dict) -> BytesIO:
        """
        Générer un rapport PDF complet des salaires pour tous les employés (format paysage)
        
        Args:
            salaires_data: Liste des calculs de salaire pour chaque employé
            periode: {'mois': int, 'annee': int}
            totaux: Dictionnaire des totaux globaux
        """
        from reportlab.lib.pagesizes import landscape
        
        buffer = BytesIO()
        
        # Format paysage (A4 horizontal)
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )
        
        story = []
        
        # En-tête avec QR Code
        header_data = [[
            Paragraph("<b>RAPPORT DÉTAILLÉ DES SALAIRES</b>", self.styles['CustomTitle']),
            self._generate_qr_rapport(periode, len(salaires_data), totaux.get('total_net', 0))
        ]]
        header_table = Table(header_data, colWidths=[24*cm, 3*cm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 0.3*cm))
        
        # Période et statistiques
        mois_nom = datetime(periode['annee'], periode['mois'], 1).strftime('%B %Y').capitalize()
        info_text = Paragraph(
            f"<b>Période:</b> {mois_nom} | <b>Nombre d'employés:</b> {len(salaires_data)}",
            self.styles['CustomBody']
        )
        story.append(info_text)
        story.append(Spacer(1, 0.4*cm))
        
        # Tableau des salaires avec TOUTES les colonnes
        table_data = [
            ['N°', 'Employé', 'Poste', 'Base', 'H.Supp', 'IN', 'IFSP', 'IEP', 
             'Enc.', 'Chauf.', 'Nuit', 'Dépl.', 'Panier', 'Trans.', 
             'Cotisable', 'SS(9%)', 'Imposable', 'IRG', 'Femme', 'Avances', 'Crédit', 'NET']
        ]
        
        for idx, sal in enumerate(salaires_data, 1):
            table_data.append([
                str(idx),
                f"{sal.get('employe_prenom', '')} {sal.get('employe_nom', '')}",
                sal.get('employe_poste', '')[:12],
                self._format_amount(sal.get('salaire_base_proratis', 0)),
                self._format_amount(sal.get('heures_supplementaires', 0)),
                self._format_amount(sal.get('indemnite_nuisance', 0)),
                self._format_amount(sal.get('ifsp', 0)),
                self._format_amount(sal.get('iep', 0)),
                self._format_amount(sal.get('prime_encouragement', 0)),
                self._format_amount(sal.get('prime_chauffeur', 0)),
                self._format_amount(sal.get('prime_nuit_agent_securite', 0)),
                self._format_amount(sal.get('prime_deplacement', 0)),
                self._format_amount(sal.get('panier', 0)),
                self._format_amount(sal.get('prime_transport', 0)),
                self._format_amount(sal.get('salaire_cotisable', 0)),
                self._format_amount(sal.get('retenue_securite_sociale', 0)),
                self._format_amount(sal.get('salaire_imposable', 0)),
                self._format_amount(sal.get('irg', 0)),
                self._format_amount(sal.get('prime_femme_foyer', 0)),
                self._format_amount(sal.get('total_avances', 0)),
                self._format_amount(sal.get('retenue_credit', 0)),
                self._format_amount(sal.get('salaire_net', 0))
            ])
        
        # Ligne de totaux
        table_data.append([
            '',
            'TOTAUX',
            '',
            self._format_amount(totaux.get('total_base', 0)),
            self._format_amount(totaux.get('total_heures_supp', 0)),
            self._format_amount(totaux.get('total_in', 0)),
            self._format_amount(totaux.get('total_ifsp', 0)),
            self._format_amount(totaux.get('total_iep', 0)),
            self._format_amount(totaux.get('total_encouragement', 0)),
            self._format_amount(totaux.get('total_chauffeur', 0)),
            self._format_amount(totaux.get('total_nuit', 0)),
            self._format_amount(totaux.get('total_deplacement', 0)),
            self._format_amount(totaux.get('total_panier', 0)),
            self._format_amount(totaux.get('total_transport', 0)),
            self._format_amount(totaux.get('total_cotisable', 0)),
            self._format_amount(totaux.get('total_ss', 0)),
            self._format_amount(totaux.get('total_imposable', 0)),
            self._format_amount(totaux.get('total_irg', 0)),
            self._format_amount(totaux.get('total_femme_foyer', 0)),
            self._format_amount(totaux.get('total_avances', 0)),
            self._format_amount(totaux.get('total_credits', 0)),
            self._format_amount(totaux.get('total_net', 0))
        ])
        
        # Largeurs de colonnes optimisées pour occuper toute la largeur (27.7cm disponibles)
        col_widths = [
            0.7*cm,   # N°
            3.2*cm,   # Employé
            2.0*cm,   # Poste
            1.4*cm,   # Base
            1.2*cm,   # H.Supp
            1.0*cm,   # IN
            1.0*cm,   # IFSP
            1.0*cm,   # IEP
            1.0*cm,   # Enc
            1.0*cm,   # Chauf
            1.0*cm,   # Nuit
            1.0*cm,   # Dépl
            1.0*cm,   # Panier
            1.0*cm,   # Trans
            1.4*cm,   # Cotisable
            1.2*cm,   # SS
            1.4*cm,   # Imposable
            1.2*cm,   # IRG
            1.0*cm,   # Femme
            1.2*cm,   # Avances
            1.2*cm,   # Crédit
            1.6*cm    # NET
        ]
        
        rapport_table = Table(table_data, colWidths=col_widths)
        
        # Style du tableau
        table_style = [
            # En-tête
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1890ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Corps
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 7),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # N°
            ('ALIGN', (1, 1), (2, -1), 'LEFT'),    # Nom et Poste
            ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),  # Tous les montants
            
            # Ligne totaux
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#52c41a')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 8),
            
            # Grille
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]
        
        rapport_table.setStyle(TableStyle(table_style))
        story.append(rapport_table)
        story.append(Spacer(1, 0.5*cm))
        
        # Pied de page
        footer = Paragraph(
            f"<i>Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</i> | "
            "<i>Document confidentiel - Usage interne uniquement</i>",
            ParagraphStyle(
                'Footer',
                parent=self.styles['Normal'],
                fontSize=7,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
        )
        story.append(footer)
        
        # Générer le PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer

    def _generate_qr_rapport(self, periode: Dict, nb_employes: int, total_net: float) -> Image:
        """Générer un QR code pour le rapport des salaires"""
        qr_data = (
            f"Année: {periode['annee']}\n"
            f"Mois: {periode['mois']}\n"
            f"Employés: {nb_employes}\n"
            f"Total Net: {total_net:,.2f} DA"
        )
        
        qr = qrcode.QRCode(version=1, box_size=4, border=1)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        return Image(qr_buffer, width=2.5*cm, height=2.5*cm)

    def _format_amount(self, amount) -> str:
        """Formater un montant avec séparateur de milliers"""
        if amount is None or amount == 0:
            return "-"
        return f"{float(amount):,.0f}".replace(',', ' ')

    def generate_rapport_employes(self, employes_data: List[Dict], periode: Dict = None, company_info: Dict = None) -> BytesIO:
        """
        Générer un rapport PDF de la liste des employés actifs
        
        Args:
            employes_data: Liste des employés
            periode: {'mois': int, 'annee': int} optionnel
            company_info: Informations de l'entreprise (optionnel)
        """
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # En-tête avec informations de l'entreprise
        if company_info:
            company_name = company_info.get('nom_entreprise') or company_info.get('raison_sociale') or ''
            compact_items = []
            if company_info.get('rc'):
                compact_items.append(f"RC: {company_info.get('rc')}")
            if company_info.get('nif'):
                compact_items.append(f"NIF: {company_info.get('nif')}")
            if company_info.get('nis'):
                compact_items.append(f"NIS: {company_info.get('nis')}")
            if company_info.get('art'):
                compact_items.append(f"ART: {company_info.get('art')}")

            compact_line = ' | '.join(compact_items)
            if company_name:
                title_para = Paragraph(f"<b>{company_name}</b>", ParagraphStyle('CompanyTitle', parent=self.styles['CustomTitle'], fontSize=16))
                story.append(title_para)
            if compact_line:
                compact_para = Paragraph(f"<small>{compact_line}</small>", ParagraphStyle('CompanyCompact', parent=self.styles['CustomBody'], fontSize=8, alignment=TA_CENTER))
                story.append(compact_para)

            addr_parts = []
            if company_info.get('adresse'):
                addr_parts.append(company_info.get('adresse'))
            if company_info.get('telephone'):
                addr_parts.append(f"Tél: {company_info.get('telephone')}")
            if company_info.get('banque') or company_info.get('compte_bancaire'):
                bank = company_info.get('banque') or ''
                compte = company_info.get('compte_bancaire') or ''
                addr_parts.append(f"{bank} {compte}".strip())
            if addr_parts:
                addr_line = ' | '.join(addr_parts)
                addr_para = Paragraph(f"<i>{addr_line}</i>", ParagraphStyle('CompanyAddr', parent=self.styles['CustomBody'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey))
                story.append(addr_para)
            story.append(Spacer(1, 0.3*cm))
        
        # En-tête
        titre = Paragraph(
            "<b>LISTE DES EMPLOYÉS ACTIFS</b>", 
            self.styles['CustomTitle']
        )
        story.append(titre)
        story.append(Spacer(1, 0.5*cm))
        
        # Période si spécifiée
        if periode:
            mois_nom = datetime(periode['annee'], periode['mois'], 1).strftime('%B %Y').capitalize()
            periode_text = Paragraph(
                f"<b>Période:</b> {mois_nom}",
                self.styles['CustomBody']
            )
            story.append(periode_text)
            story.append(Spacer(1, 0.3*cm))
        
        # Statistiques
        stats_text = Paragraph(
            f"<b>Nombre d'employés:</b> {len(employes_data)} | "
            f"<b>Date:</b> {datetime.now().strftime('%d/%m/%Y')}",
            self.styles['CustomBody']
        )
        story.append(stats_text)
        story.append(Spacer(1, 0.5*cm))
        
        # Tableau des employés
        table_data = [
            ['N°', 'Matricule', 'Nom et Prénom', 'Date Naissance', 
             'Poste de travail', 'N° SS', 'Recrutement', 'Statut']
        ]
        
        for emp in employes_data:
            table_data.append([
                str(emp.get('numero', '-')),
                emp.get('matricule', '-'),
                emp.get('nom_complet', '-'),
                emp.get('date_naissance', '-'),
                emp.get('poste_travail', '-'),
                emp.get('numero_secu_sociale', '-'),
                emp.get('date_recrutement', '-'),
                emp.get('statut', '-')
            ])
        
        # Créer le tableau
        col_widths = [1*cm, 1.8*cm, 4*cm, 2.5*cm, 3.5*cm, 2.5*cm, 2.2*cm, 2*cm]
        
        employes_table = Table(table_data, colWidths=col_widths)
        
        # Style du tableau
        table_style = [
            # En-tête
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1890ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Corps
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # N°
            ('ALIGN', (1, 1), (-1, -1), 'LEFT'),
            ('ALIGN', (6, 1), (6, -1), 'RIGHT'),   # Salaire
            
            # Grille
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]
        
        employes_table.setStyle(TableStyle(table_style))
        story.append(employes_table)
        story.append(Spacer(1, 1*cm))
        
        # Pied de page
        footer = Paragraph(
            f"<i>Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</i>",
            ParagraphStyle(
                'Footer',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
        )
        story.append(footer)
        
        # Générer le PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer

    def generate_rapport_pointages(self, pointages_data: List[Dict], periode: Dict, company_info: Dict = None) -> BytesIO:
        """
        Générer un rapport PDF des pointages par mois
        
        Args:
            pointages_data: Liste des pointages groupés par employé
            periode: {'mois': int, 'annee': int}
            company_info: Informations de l'entreprise (optionnel)
        """
        from reportlab.lib.pagesizes import landscape
        
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=landscape(A4),
            rightMargin=1.5*cm,
            leftMargin=1.5*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )
        
        story = []
        
        # En-tête avec informations de l'entreprise
        if company_info:
            company_name = company_info.get('nom_entreprise') or company_info.get('raison_sociale') or ''
            compact_items = []
            if company_info.get('rc'):
                compact_items.append(f"RC: {company_info.get('rc')}")
            if company_info.get('nif'):
                compact_items.append(f"NIF: {company_info.get('nif')}")
            if company_info.get('nis'):
                compact_items.append(f"NIS: {company_info.get('nis')}")
            if company_info.get('art'):
                compact_items.append(f"ART: {company_info.get('art')}")

            compact_line = ' | '.join(compact_items)
            if company_name:
                title_para = Paragraph(f"<b>{company_name}</b>", ParagraphStyle('CompanyTitle', parent=self.styles['CustomTitle'], fontSize=16))
                story.append(title_para)
            if compact_line:
                compact_para = Paragraph(f"<small>{compact_line}</small>", ParagraphStyle('CompanyCompact', parent=self.styles['CustomBody'], fontSize=8, alignment=TA_CENTER))
                story.append(compact_para)

            addr_parts = []
            if company_info.get('adresse'):
                addr_parts.append(company_info.get('adresse'))
            if company_info.get('telephone'):
                addr_parts.append(f"Tél: {company_info.get('telephone')}")
            if company_info.get('banque') or company_info.get('compte_bancaire'):
                bank = company_info.get('banque') or ''
                compte = company_info.get('compte_bancaire') or ''
                addr_parts.append(f"{bank} {compte}".strip())
            if addr_parts:
                addr_line = ' | '.join(addr_parts)
                addr_para = Paragraph(f"<i>{addr_line}</i>", ParagraphStyle('CompanyAddr', parent=self.styles['CustomBody'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey))
                story.append(addr_para)
            story.append(Spacer(1, 0.3*cm))
        
        # En-tête
        mois_nom = datetime(periode['annee'], periode['mois'], 1).strftime('%B %Y').capitalize()
        titre = Paragraph(
            f"<b>RAPPORT DES POINTAGES - {mois_nom}</b>", 
            self.styles['CustomTitle']
        )
        story.append(titre)
        story.append(Spacer(1, 0.5*cm))
        
        # Statistiques
        total_employes = len(pointages_data)
        total_jours_travailles = sum(p.get('jours_travailles', 0) for p in pointages_data)
        
        stats_text = Paragraph(
            f"<b>Employés:</b> {total_employes} | "
            f"<b>Total jours travaillés:</b> {total_jours_travailles} | "
            f"<b>Date:</b> {datetime.now().strftime('%d/%m/%Y')}",
            self.styles['CustomBody']
        )
        story.append(stats_text)
        story.append(Spacer(1, 0.5*cm))
        
        # Tableau des pointages
        table_data = [
            ['N°', 'Matricule', 'Nom et Prénom', 'Poste de travail', 'Jours\nTravaillés', 
             'Absences\nGénérales', 'Jours\nCongé', 'Statut']
        ]
        
        for p in pointages_data:
            table_data.append([
                str(p.get('numero', '-')),
                p.get('matricule', '-'),
                p.get('nom_complet', '-'),
                p.get('poste_travail', '-')[:25],
                str(p.get('jours_travailles', 0)),
                str(p.get('absences', 0)),
                f"{p.get('jours_conges_acquis', 0):.1f}",
                p.get('statut', '-')
            ])
        
        # Créer le tableau
        col_widths = [1*cm, 2*cm, 5*cm, 4.5*cm, 2*cm, 2*cm, 2*cm, 2.5*cm]
        
        pointages_table = Table(table_data, colWidths=col_widths)
        
        # Style du tableau
        table_style = [
            # En-tête
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1890ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Corps
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # N°
            ('ALIGN', (1, 1), (3, -1), 'LEFT'),
            ('ALIGN', (4, 1), (-1, -1), 'CENTER'),
            
            # Grille
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]
        
        pointages_table.setStyle(TableStyle(table_style))
        story.append(pointages_table)
        story.append(Spacer(1, 1*cm))
        
        # Pied de page
        footer = Paragraph(
            f"<i>Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</i>",
            ParagraphStyle(
                'Footer',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
        )
        story.append(footer)
        
        # Générer le PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer

    def generate_rapport_clients(self, clients_data: List[Dict], company_info: Dict = None) -> BytesIO:
        """
        Générer un rapport PDF de la liste des clients
        
        Args:
            clients_data: Liste des clients
        """
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # En-tête
        # Si company_info est fourni, afficher l'identité compacte de l'entreprise
        if company_info:
            company_name = company_info.get('nom_entreprise') or company_info.get('raison_sociale') or ''
            compact_items = []
            if company_info.get('rc'):
                compact_items.append(f"RC: {company_info.get('rc')}")
            if company_info.get('nif'):
                compact_items.append(f"NIF: {company_info.get('nif')}")
            if company_info.get('nis'):
                compact_items.append(f"NIS: {company_info.get('nis')}")
            if company_info.get('art'):
                compact_items.append(f"ART: {company_info.get('art')}")

            # Ligne compacte (petit) pour RC/NIF/NIS/ART
            compact_line = ' | '.join(compact_items)
            if company_name:
                title_para = Paragraph(f"<b>{company_name}</b>", ParagraphStyle('CompanyTitle', parent=self.styles['CustomTitle'], fontSize=16))
                story.append(title_para)
            if compact_line:
                compact_para = Paragraph(f"<small>{compact_line}</small>", ParagraphStyle('CompanyCompact', parent=self.styles['CustomBody'], fontSize=8, alignment=TA_CENTER))
                story.append(compact_para)

            # Adresse / contact sur une seule ligne réduite
            addr_parts = []
            if company_info.get('adresse'):
                addr_parts.append(company_info.get('adresse'))
            if company_info.get('telephone'):
                addr_parts.append(f"Tél: {company_info.get('telephone')}")
            if company_info.get('banque') or company_info.get('compte_bancaire'):
                bank = company_info.get('banque') or ''
                compte = company_info.get('compte_bancaire') or ''
                addr_parts.append(f"{bank} {compte}".strip())
            if addr_parts:
                addr_line = ' | '.join(addr_parts)
                addr_para = Paragraph(f"<i>{addr_line}</i>", ParagraphStyle('CompanyAddr', parent=self.styles['CustomBody'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey))
                story.append(addr_para)
            story.append(Spacer(1, 0.3*cm))

        titre = Paragraph(
            "<b>LISTE DES CLIENTS</b>", 
            self.styles['CustomTitle']
        )
        story.append(titre)
        story.append(Spacer(1, 0.5*cm))
        
        # Statistiques
        stats_text = Paragraph(
            f"<b>Nombre de clients:</b> {len(clients_data)} | "
            f"<b>Date:</b> {datetime.now().strftime('%d/%m/%Y')}",
            self.styles['CustomBody']
        )
        story.append(stats_text)
        story.append(Spacer(1, 0.5*cm))
        
        # Tableau des clients
        table_data = [
            ['N°', 'Nom et Prénom', 'Distance', 'Téléphone', 'Tarif/km']
        ]
        
        for client in clients_data:
            table_data.append([
                str(client.get('numero', '-')),
                client.get('nom', '-'),
                client.get('distance', '-'),
                client.get('telephone', '-'),
                client.get('tarif_km', '-')
            ])
        
        # Créer le tableau
        col_widths = [1.5*cm, 6*cm, 3*cm, 3.5*cm, 3*cm]
        
        clients_table = Table(table_data, colWidths=col_widths)
        
        # Style du tableau
        table_style = [
            # En-tête
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1890ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Corps
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # N°
            ('ALIGN', (1, 1), (-1, -1), 'LEFT'),
            
            # Grille
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]
        
        clients_table.setStyle(TableStyle(table_style))
        story.append(clients_table)
        story.append(Spacer(1, 1*cm))
        
        # Pied de page
        footer = Paragraph(
            f"<i>Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</i>",
            ParagraphStyle(
                'Footer',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
        )
        story.append(footer)
        
        # Générer le PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer

    def generate_rapport_avances(self, avances_data: List[Dict], periode: Dict = None, company_info: Dict = None) -> BytesIO:
        """
        Générer un rapport PDF des avances par période
        
        Args:
            avances_data: Liste des avances
            periode: {'mois': int, 'annee': int} optionnel
            company_info: Informations de l'entreprise (optionnel)
        """
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # En-tête avec informations de l'entreprise
        if company_info:
            company_name = company_info.get('nom_entreprise') or company_info.get('raison_sociale') or ''
            compact_items = []
            if company_info.get('rc'):
                compact_items.append(f"RC: {company_info.get('rc')}")
            if company_info.get('nif'):
                compact_items.append(f"NIF: {company_info.get('nif')}")
            if company_info.get('nis'):
                compact_items.append(f"NIS: {company_info.get('nis')}")
            if company_info.get('art'):
                compact_items.append(f"ART: {company_info.get('art')}")

            compact_line = ' | '.join(compact_items)
            if company_name:
                title_para = Paragraph(f"<b>{company_name}</b>", ParagraphStyle('CompanyTitle', parent=self.styles['CustomTitle'], fontSize=16))
                story.append(title_para)
            if compact_line:
                compact_para = Paragraph(f"<small>{compact_line}</small>", ParagraphStyle('CompanyCompact', parent=self.styles['CustomBody'], fontSize=8, alignment=TA_CENTER))
                story.append(compact_para)

            addr_parts = []
            if company_info.get('adresse'):
                addr_parts.append(company_info.get('adresse'))
            if company_info.get('telephone'):
                addr_parts.append(f"Tél: {company_info.get('telephone')}")
            if company_info.get('banque') or company_info.get('compte_bancaire'):
                bank = company_info.get('banque') or ''
                compte = company_info.get('compte_bancaire') or ''
                addr_parts.append(f"{bank} {compte}".strip())
            if addr_parts:
                addr_line = ' | '.join(addr_parts)
                addr_para = Paragraph(f"<i>{addr_line}</i>", ParagraphStyle('CompanyAddr', parent=self.styles['CustomBody'], fontSize=8, alignment=TA_CENTER, textColor=colors.grey))
                story.append(addr_para)
            story.append(Spacer(1, 0.3*cm))
        
        # En-tête
        if periode:
            mois_nom = datetime(periode['annee'], periode['mois'], 1).strftime('%B %Y').capitalize()
            titre_text = f"<b>RAPPORT DES AVANCES - {mois_nom}</b>"
        else:
            titre_text = "<b>RAPPORT DES AVANCES</b>"
        
        titre = Paragraph(titre_text, self.styles['CustomTitle'])
        story.append(titre)
        story.append(Spacer(1, 0.5*cm))
        
        # Statistiques
        total_montant = sum(float(a.get('montant', 0)) for a in avances_data)
        
        stats_text = Paragraph(
            f"<b>Nombre d'avances:</b> {len(avances_data)} | "
            f"<b>Montant total:</b> {self._format_amount(total_montant)} DA | "
            f"<b>Date:</b> {datetime.now().strftime('%d/%m/%Y')}",
            self.styles['CustomBody']
        )
        story.append(stats_text)
        story.append(Spacer(1, 0.5*cm))
        
        # Tableau des avances
        table_data = [
            ['N°', 'Date', 'Employé', 'Montant', 'Motif', 'Statut']
        ]
        
        for idx, avance in enumerate(avances_data, 1):
            table_data.append([
                str(idx),
                avance.get('date_avance', '-'),
                f"{avance.get('employe_prenom', '')} {avance.get('employe_nom', '')}",
                self._format_amount(avance.get('montant', 0)),
                avance.get('motif', '-')[:25],
                avance.get('statut', 'En cours')
            ])
        
        # Ligne total
        table_data.append([
            '',
            '',
            'TOTAL',
            self._format_amount(total_montant),
            '',
            ''
        ])
        
        # Créer le tableau
        col_widths = [1*cm, 2.5*cm, 4*cm, 2.5*cm, 6*cm, 3*cm]
        
        avances_table = Table(table_data, colWidths=col_widths)
        
        # Style du tableau
        table_style = [
            # En-tête
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1890ff')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Corps
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 8),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # N°
            ('ALIGN', (1, 1), (2, -1), 'LEFT'),
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'),   # Montant
            ('ALIGN', (4, 1), (-1, -1), 'LEFT'),
            
            # Ligne total
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#52c41a')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 9),
            
            # Grille
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]
        
        avances_table.setStyle(TableStyle(table_style))
        story.append(avances_table)
        story.append(Spacer(1, 1*cm))
        
        # Pied de page
        footer = Paragraph(
            f"<i>Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</i>",
            ParagraphStyle(
                'Footer',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
        )
        story.append(footer)
        
        # Générer le PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer



