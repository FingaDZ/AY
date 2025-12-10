"""Service pour générer des PDFs pour les ordres de mission et rapports"""

from reportlab.lib.pagesizes import A4, A5, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas
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
                if params.numero_secu_employeur:
                    ids.append(f"N° SS EMPLOYEUR: {params.numero_secu_employeur}")
                
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
        """Créer le footer 'Powered by AIRBAND HR'"""
        footer_style = ParagraphStyle(
            name='PoweredBy',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        return Paragraph("Powered by AIRBAND HR", footer_style)
    
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
        
        # Footer
        story.append(Spacer(1, 0.5*cm))
        story.append(self._create_footer())
        
        # Générer le PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    def generate_ordre_mission_enhanced(self, mission_data: Dict) -> BytesIO:
        """
        Générer un ordre de mission PDF pour un client spécifique avec logistique (format A5)
        
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
                - montant_encaisse: Montant espèce
                - observations: Observations du client
                - logistics: Liste des mouvements logistiques
                    [{type_name, quantity_out, quantity_in}, ...]
        
        Returns:
            BytesIO: Buffer contenant le PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A5, topMargin=1*cm, bottomMargin=1*cm, 
                                leftMargin=1*cm, rightMargin=1*cm)
        
        story = []
        
        # En-tête avec numéro d'ordre
        ordre_num = self._generate_ordre_numero(mission_data['id'], mission_data['date_mission'])
        
        header_data = [
            ['ORDRE DE MISSION', f'N° {ordre_num}']
        ]
        
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
        
        # Date
        date_str = datetime.strptime(mission_data['date_mission'], '%Y-%m-%d').strftime('%d/%m/%Y')
        date_para = Paragraph(f"<b>Date:</b> {date_str}", self.styles['CustomBody'])
        story.append(date_para)
        story.append(Spacer(1, 0.4*cm))
        
        # Informations principales
        info_data = [
            ['CHAUFFEUR', f"{mission_data['chauffeur_prenom']} {mission_data['chauffeur_nom']}"],
            ['CLIENT', f"{mission_data['client_prenom']} {mission_data['client_nom']}"],
        ]
        
        if mission_data.get('montant_encaisse', 0) > 0:
            info_data.append(['Espèce', f"{mission_data['montant_encaisse']:.2f} DA"])
        
        info_table = Table(info_data, colWidths=[3.5*cm, 9.3*cm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.4*cm))
        
        # Montant versé (case agrandie x3 pour inscription manuelle)
        montant_title = Paragraph("<b>MONTANT VERSÉ</b>", self.styles['CustomBody'])
        story.append(montant_title)
        story.append(Spacer(1, 0.2*cm))
        
        montant_data = [['']]
        montant_table = Table(montant_data, colWidths=[12.8*cm], rowHeights=[1.8*cm])
        montant_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(montant_table)
        story.append(Spacer(1, 0.4*cm))
        
        # Logistique (si présente)
        if mission_data.get('logistics') and len(mission_data['logistics']) > 0:
            logistics_title = Paragraph("<b>LOGISTIQUE</b>", self.styles['CustomBody'])
            story.append(logistics_title)
            story.append(Spacer(1, 0.2*cm))
            
            logistics_data = [['Type', 'Prises', 'Retournées', 'Solde']]
            for log in mission_data['logistics']:
                q_out = log.get('quantity_out', 0)
                q_in = log.get('quantity_in', 0)
                solde = q_out - q_in
                logistics_data.append([
                    log['type_name'],
                    str(q_out),
                    str(q_in),
                    str(solde)
                ])
            
            logistics_table = Table(logistics_data, colWidths=[5.3*cm, 2.5*cm, 2.5*cm, 2.5*cm])
            logistics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('PADDING', (0, 0), (-1, -1), 4),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(logistics_table)
            story.append(Spacer(1, 0.4*cm))
        
        # Observations (Toujours afficher)
        obs_title = Paragraph("<b>OBSERVATIONS (Retours, Casse, Détérioration...)</b>", self.styles['CustomBody'])
        story.append(obs_title)
        story.append(Spacer(1, 0.2*cm))
        
        obs_content = mission_data.get('observations', '')
        if not obs_content:
            # Créer un cadre vide pour écrire manuellement (2.5x plus grand)
            obs_data = [['']]
            obs_table = Table(obs_data, colWidths=[12.8*cm], rowHeights=[3.75*cm])
            obs_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(obs_table)
        else:
            # Afficher le texte existant dans un cadre
            obs_para = Paragraph(obs_content, self.styles['CustomBody'])
            obs_data = [[obs_para]]
            obs_table = Table(obs_data, colWidths=[12.8*cm])
            obs_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(obs_table)
            
        story.append(Spacer(1, 0.4*cm))
        
        # Signatures
        signatures = [
            ['Signature chauffeur', 'Signature client', 'Signature responsable'],
            ['', '', ''],
            ['', '', ''],
        ]
        
        sig_table = Table(signatures, colWidths=[4.27*cm, 4.27*cm, 4.26*cm])
        sig_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 7),
            ('BOTTOMPADDING', (0, 1), (-1, 2), 0.8*cm),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(sig_table)
        
        # Footer
        story.append(Spacer(1, 0.3*cm))
        story.append(self._create_footer())
        
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
        
        # Footer
        story.append(Spacer(1, 0.5*cm))
        story.append(self._create_footer())
        
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
        
        # Footer standard
        story.append(Spacer(1, 0.3*cm))
        story.append(self._create_footer())
        
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
        
        # Générer QR Code avec toutes les informations
        salaire_net_format = f"{float(salaire_data.get('salaire_net', 0)):,.2f}".replace(',', ' ')
        salaire_brut_format = f"{float(salaire_data.get('salaire_brut', 0)):,.2f}".replace(',', ' ')
        qr_data = f"ID: {employe_data.get('id', '')}\n" \
                  f"Nom: {employe_data.get('prenom', '')} {employe_data.get('nom', '')}\n" \
                  f"Poste: {employe_data.get('poste_travail', 'N/A')}\n" \
                  f"N°SS: {employe_data.get('numero_secu_sociale', 'N/A')}\n" \
                  f"Date Recrutement: {employe_data.get('date_recrutement', 'N/A')}\n" \
                  f"Mois: {salaire_data.get('mois', '')}/{salaire_data.get('annee', '')}\n" \
                  f"Salaire Brut: {salaire_brut_format} DA\n" \
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
        company_name = (params.raison_sociale or params.nom_entreprise or "Entreprise") if params else "Entreprise"
        company_address = params.adresse if params and params.adresse else "Adresse non définie"
        company_rc = params.rc if params and params.rc else "Non défini"
        company_ss_employeur = params.numero_secu_employeur if params and params.numero_secu_employeur else "Non défini"
        
        # Fusionner tableaux EMPLOYEUR et EMPLOYÉ côte à côte
        info_data = [
            # En-têtes fusionnés
            [Paragraph("<b>EMPLOYEUR</b>", self.styles['CustomBody']), '', 
             Paragraph("<b>EMPLOYÉ</b>", self.styles['CustomBody']), ''],
            # Lignes de données
            ['Raison Sociale:', Paragraph(company_name, self.styles['CustomBody']),
             'Nom:', f"{employe_data.get('prenom', '')} {employe_data.get('nom', '')}"],
            ['RC:', company_rc,
             'Poste:', employe_data.get('poste_travail', '')],
            ['N° SS EMPLOYEUR:', company_ss_employeur,
             'N° Sécurité Sociale:', employe_data.get('numero_secu_sociale', 'N/A')],
            ['Adresse:', Paragraph(company_address, self.styles['CustomBody']),
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
        
        # En-tête entreprise
        company_header = self._create_company_header(include_details=True)
        for element in company_header:
            story.append(element)
        story.append(Spacer(1, 0.3*cm))
        
        # Titre du rapport avec QR Code
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
        
        # Footer standard
        story.append(Spacer(1, 0.3*cm))
        story.append(self._create_footer())
        
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
        
        # Footer standard
        story.append(Spacer(1, 0.3*cm))
        story.append(self._create_footer())
        
        # Générer le PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer

    def generate_rapport_pointages(self, pointages_data: List[Dict], periode: Dict, company_info: Dict = None) -> BytesIO:
        """
        Générer un rapport PDF des pointages par mois (format portrait)
        
        Args:
            pointages_data: Liste des pointages groupés par employé
            periode: {'mois': int, 'annee': int}
            company_info: Informations de l'entreprise (optionnel)
        """
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1*cm,
            leftMargin=1*cm,
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
        
        # Créer le tableau avec colonnes dynamiques adaptées au format portrait
        # Largeur disponible: A4 portrait = 21cm - 2cm marges = 19cm
        col_widths = [
            0.8*cm,   # N°
            1.5*cm,   # Matricule
            5.5*cm,   # Nom et Prénom
            4.2*cm,   # Poste (tronqué à 20 chars)
            1.5*cm,   # Jours Travaillés
            1.5*cm,   # Absences
            1.5*cm,   # Jours Congé
            2.5*cm    # Statut
        ]
        
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
        
        # Footer standard
        story.append(Spacer(1, 0.3*cm))
        story.append(self._create_footer())
        
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
        
        # Footer standard
        story.append(Spacer(1, 0.3*cm))
        story.append(self._create_footer())
        
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
        
        # Footer standard
        story.append(Spacer(1, 0.3*cm))
        story.append(self._create_footer())
        
        # Générer le PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    def generate_attestation_travail(self, employe_data: Dict) -> BytesIO:
        """
        Générer une attestation de travail pour un employé actif
        
        Args:
            employe_data: Dictionnaire contenant les informations de l'employé
                - nom, prenom, date_naissance, lieu_naissance
                - adresse, numero_secu_sociale
                - poste_travail, date_recrutement
                - salaire_base
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        story = []
        
        # Récupérer les paramètres entreprise
        params = self._get_parametres()
        company_name = (params.raison_sociale or params.nom_entreprise or "Entreprise") if params else "Entreprise"
        company_address = params.adresse if params and params.adresse else ""
        company_rc = params.rc if params and params.rc else ""
        company_nif = params.nif if params and params.nif else ""
        
        # En-tête entreprise
        header_style = ParagraphStyle(
            name='CompanyHeader',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#1a1a1a'),
            alignment=TA_CENTER,
            spaceAfter=5
        )
        
        story.append(Paragraph(f"<b>{company_name}</b>", header_style))
        if company_address:
            addr_style = ParagraphStyle(name='Address', parent=self.styles['Normal'], 
                                       fontSize=9, alignment=TA_CENTER, spaceAfter=3)
            story.append(Paragraph(company_address, addr_style))
        
        if company_rc or company_nif:
            details = []
            if company_rc:
                details.append(f"RC: {company_rc}")
            if company_nif:
                details.append(f"NIF: {company_nif}")
            detail_style = ParagraphStyle(name='Details', parent=self.styles['Normal'],
                                         fontSize=8, alignment=TA_CENTER, spaceAfter=20)
            story.append(Paragraph(" | ".join(details), detail_style))
        else:
            story.append(Spacer(1, 0.5*cm))
        
        story.append(Spacer(1, 1*cm))
        
        # Titre du document
        title_style = ParagraphStyle(
            name='DocTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=30,
            spaceBefore=10
        )
        story.append(Paragraph("<b>ATTESTATION DE TRAVAIL</b>", title_style))
        story.append(Spacer(1, 1*cm))
        
        # Corps du texte
        body_style = ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=18,
            alignment=TA_LEFT,
            spaceAfter=12
        )
        
        # Date du jour
        date_aujourdhui = datetime.now().strftime("%d/%m/%Y")
        
        # Calcul de l'ancienneté
        date_recrutement = employe_data.get('date_recrutement')
        if isinstance(date_recrutement, str):
            date_recrutement = datetime.strptime(date_recrutement, "%Y-%m-%d").date()
        
        today = datetime.now().date()
        anciennete_jours = (today - date_recrutement).days
        anciennete_annees = anciennete_jours // 365
        anciennete_mois = (anciennete_jours % 365) // 30
        
        anciennete_text = []
        if anciennete_annees > 0:
            anciennete_text.append(f"{anciennete_annees} an{'s' if anciennete_annees > 1 else ''}")
        if anciennete_mois > 0:
            anciennete_text.append(f"{anciennete_mois} mois")
        anciennete_str = " et ".join(anciennete_text) if anciennete_text else "moins d'un mois"
        
        # Contenu de l'attestation
        text_parts = [
            f"Je soussigné(e), représentant(e) de <b>{company_name}</b>, atteste par la présente que :",
            "",
            f"<b>Monsieur/Madame {employe_data.get('prenom', '')} {employe_data.get('nom', '')}</b>",
            f"Né(e) le {employe_data.get('date_naissance', 'N/A')} à {employe_data.get('lieu_naissance', 'N/A')}",
            f"Demeurant à : {employe_data.get('adresse', 'N/A')}",
            f"N° Sécurité Sociale : {employe_data.get('numero_secu_sociale', 'N/A')}",
            "",
            f"Est employé(e) au sein de notre entreprise depuis le <b>{date_recrutement.strftime('%d/%m/%Y')}</b>, "
            f"<b>Jusqu'à ce jour</b>.",
            "",
            f"Poste de Travail : <b>{employe_data.get('poste_travail', 'N/A')}</b>.",
        ]
        
        for part in text_parts:
            if part:
                story.append(Paragraph(part, body_style))
            else:
                story.append(Spacer(1, 0.3*cm))
        
        story.append(Spacer(1, 1*cm))
        
        # Texte centré final
        centered_style = ParagraphStyle(
            name='CenteredText',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_CENTER,
            spaceAfter=12
        )
        story.append(Paragraph("Cette attestation est délivrée à l'intéressé(e) pour servir et valoir ce que de droit.", centered_style))
        
        story.append(Spacer(1, 1*cm))
        
        # Signature
        signature_style = ParagraphStyle(
            name='Signature',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_RIGHT,
            spaceAfter=8
        )
        
        story.append(Paragraph(f"Fait à : Chelghoum Laid, le {date_aujourdhui}", signature_style))
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph("<b>Le Responsable</b>", signature_style))
        story.append(Spacer(1, 2*cm))
        story.append(Paragraph("(Signature et cachet)", signature_style))
        
        # Générer le PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_certificat_travail(self, employe_data: Dict) -> BytesIO:
        """
        Générer un certificat de travail pour un employé ayant cessé ses fonctions
        
        Args:
            employe_data: Dictionnaire contenant les informations de l'employé
                - nom, prenom, date_naissance, lieu_naissance
                - adresse, numero_secu_sociale
                - poste_travail, date_recrutement, date_fin_contrat
                - salaire_base
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        story = []
        
        # Récupérer les paramètres entreprise
        params = self._get_parametres()
        company_name = (params.raison_sociale or params.nom_entreprise or "Entreprise") if params else "Entreprise"
        company_address = params.adresse if params and params.adresse else ""
        company_rc = params.rc if params and params.rc else ""
        company_nif = params.nif if params and params.nif else ""
        
        # En-tête entreprise
        header_style = ParagraphStyle(
            name='CompanyHeader',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#1a1a1a'),
            alignment=TA_CENTER,
            spaceAfter=5
        )
        
        story.append(Paragraph(f"<b>{company_name}</b>", header_style))
        if company_address:
            addr_style = ParagraphStyle(name='Address', parent=self.styles['Normal'], 
                                       fontSize=9, alignment=TA_CENTER, spaceAfter=3)
            story.append(Paragraph(company_address, addr_style))
        
        if company_rc or company_nif:
            details = []
            if company_rc:
                details.append(f"RC: {company_rc}")
            if company_nif:
                details.append(f"NIF: {company_nif}")
            detail_style = ParagraphStyle(name='Details', parent=self.styles['Normal'],
                                         fontSize=8, alignment=TA_CENTER, spaceAfter=20)
            story.append(Paragraph(" | ".join(details), detail_style))
        else:
            story.append(Spacer(1, 0.5*cm))
        
        story.append(Spacer(1, 1*cm))
        
        # Titre du document
        title_style = ParagraphStyle(
            name='DocTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.black,
            alignment=TA_CENTER,
            spaceAfter=30,
            spaceBefore=10
        )
        story.append(Paragraph("<b>CERTIFICAT DE TRAVAIL</b>", title_style))
        story.append(Spacer(1, 1*cm))
        
        # Corps du texte
        body_style = ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=18,
            alignment=TA_LEFT,
            spaceAfter=12
        )
        
        # Date du jour
        date_aujourdhui = datetime.now().strftime("%d/%m/%Y")
        
        # Dates de début et fin
        date_recrutement = employe_data.get('date_recrutement')
        if isinstance(date_recrutement, str):
            date_recrutement = datetime.strptime(date_recrutement, "%Y-%m-%d").date()
        
        date_fin_contrat = employe_data.get('date_fin_contrat')
        if isinstance(date_fin_contrat, str):
            date_fin_contrat = datetime.strptime(date_fin_contrat, "%Y-%m-%d").date()
        elif date_fin_contrat is None:
            date_fin_contrat = datetime.now().date()
        
        # Calcul de la durée totale
        duree_jours = (date_fin_contrat - date_recrutement).days
        duree_annees = duree_jours // 365
        duree_mois = (duree_jours % 365) // 30
        
        duree_text = []
        if duree_annees > 0:
            duree_text.append(f"{duree_annees} an{'s' if duree_annees > 1 else ''}")
        if duree_mois > 0:
            duree_text.append(f"{duree_mois} mois")
        duree_str = " et ".join(duree_text) if duree_text else "moins d'un mois"
        
        # Contenu du certificat
        text_parts = [
            f"Je soussigné(e), représentant(e) de <b>{company_name}</b>, certifie par la présente que :",
            "",
            f"<b>Monsieur/Madame {employe_data.get('prenom', '')} {employe_data.get('nom', '')}</b>",
            f"Né(e) le {employe_data.get('date_naissance', 'N/A')} à {employe_data.get('lieu_naissance', 'N/A')}",
            f"Demeurant à : {employe_data.get('adresse', 'N/A')}",
            f"N° Sécurité Sociale : {employe_data.get('numero_secu_sociale', 'N/A')}",
            "",
            f"A été employé(e) au sein de notre entreprise du <b>{date_recrutement.strftime('%d/%m/%Y')}</b> "
            f"au <b>{date_fin_contrat.strftime('%d/%m/%Y')}</b>, "
            f"soit une durée totale de <b>{duree_str}</b>.",
            "",
            f"Durant cette période, il/elle a occupé le poste de <b>{employe_data.get('poste_travail', 'N/A')}</b>.",
        ]
        
        for part in text_parts:
            if part:
                story.append(Paragraph(part, body_style))
            else:
                story.append(Spacer(1, 0.3*cm))
        
        story.append(Spacer(1, 1*cm))
        
        # Texte centré final
        centered_style = ParagraphStyle(
            name='CenteredText',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_CENTER,
            spaceAfter=12
        )
        story.append(Paragraph("Le présent certificat est délivré pour servir et valoir ce que de droit.", centered_style))
        
        story.append(Spacer(1, 1*cm))
        
        # Signature
        signature_style = ParagraphStyle(
            name='Signature',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_RIGHT,
            spaceAfter=8
        )
        
        story.append(Paragraph(f"Fait à : Chelghoum Laid, le {date_aujourdhui}", signature_style))
        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph("<b>Le Responsable</b>", signature_style))
        story.append(Spacer(1, 2*cm))
        story.append(Paragraph("(Signature et cachet)", signature_style))
        
        # Générer le PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_contrat_travail(self, employe_data: Dict) -> BytesIO:
        """
        Générer un contrat de travail pour un employé - Nouveau modèle propre
        """
        buffer = BytesIO()
        
        # Récupérer les paramètres entreprise
        params = self._get_parametres()
        company_name = (params.raison_sociale or params.nom_entreprise or "Entreprise") if params else "Entreprise"
        company_address = params.adresse if params and params.adresse else "Chelghoum Laid"
        company_rc = params.rc if params and params.rc else ""
        company_nif = params.nif if params and params.nif else ""
        company_nis = params.nis if params and params.nis else ""
        
        # Informations employé
        nom = employe_data.get('nom', '')
        prenom = employe_data.get('prenom', '')
        date_naissance = employe_data.get('date_naissance', '')
        lieu_naissance = employe_data.get('lieu_naissance', '')
        adresse = employe_data.get('adresse', '')
        numero_ss = employe_data.get('numero_secu_sociale', '')
        poste = employe_data.get('poste_travail', '')
        date_debut = employe_data.get('date_recrutement', '')
        duree_contrat = employe_data.get('duree_contrat')
        date_fin = employe_data.get('date_fin_contrat')
        salaire = employe_data.get('salaire_base', 0)
        
        # Formater les dates
        if isinstance(date_debut, str):
            date_debut_str = date_debut
        else:
            date_debut_str = date_debut.strftime('%d/%m/%Y') if date_debut else ''
            
        if isinstance(date_fin, str):
            date_fin_str = date_fin
        elif date_fin:
            date_fin_str = date_fin.strftime('%d/%m/%Y')
        else:
            date_fin_str = "Indéterminée"
        
        if isinstance(date_naissance, str):
            date_naissance_str = date_naissance
        else:
            date_naissance_str = date_naissance.strftime('%d/%m/%Y') if date_naissance else ''
            
        date_aujourdhui = datetime.now().strftime("%d/%m/%Y")
        
        # Créer le PDF avec ReportLab
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Fonction pour créer une nouvelle page si nécessaire
        def check_new_page(y_position, needed_space=100):
            if y_position < needed_space:
                c.showPage()
                return height - 50
            return y_position
        
        y = height - 50
        
        # ========== EN-TÊTE ==========
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(width/2, y, company_name)
        y -= 20
        
        c.setFont("Helvetica", 9)
        c.drawCentredString(width/2, y, company_address)
        y -= 15
        
        if company_rc or company_nif or company_nis:
            info_parts = []
            if company_rc:
                info_parts.append(f"RC: {company_rc}")
            if company_nif:
                info_parts.append(f"NIF: {company_nif}")
            if company_nis:
                info_parts.append(f"NIS: {company_nis}")
            c.drawCentredString(width/2, y, " | ".join(info_parts))
            y -= 30
        else:
            y -= 20
        
        # ========== TITRE ==========
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width/2, y, "CONTRAT DE TRAVAIL")
        y -= 20
        
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(width/2, y, "À DURÉE DÉTERMINÉE")
        y -= 35
        
        # ========== ENTRE LES SOUSSIGNÉS ==========
        y = check_new_page(y, 150)
        
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, "ENTRE LES SOUSSIGNÉS :")
        y -= 25
        
        # L'EMPLOYEUR (simplifié - déjà dans l'en-tête)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(70, y, "L'EMPLOYEUR :")
        y -= 18
        
        c.setFont("Helvetica", 10)
        c.drawString(90, y, "Représenté par son gérant légalement habilité")
        y -= 18
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(70, y, "D'UNE PART,")
        y -= 25
        
        # LE SALARIÉ
        c.setFont("Helvetica-Bold", 10)
        c.drawString(70, y, "LE SALARIÉ :")
        y -= 18
        
        c.setFont("Helvetica", 10)
        c.drawString(90, y, f"Nom et Prénom : ")
        c.setFont("Helvetica-Bold", 10)
        c.drawString(180, y, f"{nom} {prenom}")
        y -= 14
        
        c.setFont("Helvetica", 10)
        c.drawString(90, y, f"Date de naissance : {date_naissance_str}")
        y -= 14
        c.drawString(90, y, f"Lieu de naissance : {lieu_naissance}")
        y -= 14
        c.drawString(90, y, f"Adresse : {adresse}")
        y -= 14
        c.drawString(90, y, f"N° Sécurité Sociale : {numero_ss}")
        y -= 18
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(70, y, "D'AUTRE PART,")
        y -= 30
        
        # ========== CONDITIONS ==========
        y = check_new_page(y, 100)
        
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, "IL A ÉTÉ CONVENU ET ARRÊTÉ CE QUI SUIT :")
        y -= 25
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(70, y, "Date de début :")
        c.setFont("Helvetica", 10)
        c.drawString(200, y, date_debut_str)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(350, y, "Date de fin :")
        c.setFont("Helvetica", 10)
        c.drawString(450, y, date_fin_str)
        y -= 16
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(70, y, "Durée :")
        c.setFont("Helvetica", 10)
        duree_text = f"{duree_contrat} mois" if duree_contrat else "À déterminer"
        c.drawString(200, y, duree_text)
        y -= 30
        
        # ========== ARTICLES ==========
        y = check_new_page(y, 150)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Article 1 : Objet du contrat")
        y -= 14
        c.setFont("Helvetica", 9)
        c.drawString(70, y, f"Le salarié est engagé en qualité de {poste} et s'engage à exécuter")
        y -= 12
        c.drawString(70, y, "les tâches qui lui seront confiées dans le cadre de cette fonction.")
        y -= 20
        
        y = check_new_page(y)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Article 2 : Durée du contrat")
        y -= 14
        c.setFont("Helvetica", 9)
        if duree_contrat:
            c.drawString(70, y, f"Le présent contrat prend effet le {date_debut_str}. Il est conclu pour")
            y -= 12
            c.drawString(70, y, f"une durée déterminée de {duree_contrat} mois et prendra fin le {date_fin_str}.")
        else:
            c.drawString(70, y, f"Le présent contrat prend effet le {date_debut_str}. Il est conclu pour")
            y -= 12
            c.drawString(70, y, f"une durée déterminée et prendra fin le {date_fin_str}.")
        y -= 20
        
        y = check_new_page(y)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Article 3 : Lieu de travail")
        y -= 14
        c.setFont("Helvetica", 9)
        c.drawString(70, y, f"Le salarié exercera ses fonctions à {company_address}.")
        y -= 20
        
        y = check_new_page(y)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Article 4 : Horaires de travail")
        y -= 14
        c.setFont("Helvetica", 9)
        c.drawString(70, y, "La durée du travail est fixée à 173,33 heures par mois")
        y -= 12
        c.drawString(70, y, "(base de calcul légale conformément à la législation algérienne).")
        y -= 20
        
        y = check_new_page(y)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Article 5 : Rémunération")
        y -= 14
        c.setFont("Helvetica", 9)
        c.drawString(70, y, f"Le salaire mensuel brut est fixé à {salaire:,.2f} DA.")
        y -= 12
        c.drawString(70, y, "Ce salaire pourra être complété par les primes prévues")
        y -= 12
        c.drawString(70, y, "par le règlement intérieur et la législation en vigueur.")
        y -= 20
        
        y = check_new_page(y, 120)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Article 6 : Primes et indemnités")
        y -= 14
        c.setFont("Helvetica", 9)
        c.drawString(70, y, "Le salarié pourra bénéficier des primes suivantes :")
        y -= 12
        c.drawString(85, y, "• Prime de rendement : 5% du salaire de base")
        y -= 12
        c.drawString(85, y, "• Prime de fidélité : 5% du salaire de base")
        y -= 12
        c.drawString(85, y, "• Prime d'expérience : 1% par année d'ancienneté")
        y -= 12
        c.drawString(85, y, "• Prime de panier : 100 DA/jour travaillé")
        y -= 20
        
        y = check_new_page(y)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Article 7 : Congés payés")
        y -= 14
        c.setFont("Helvetica", 9)
        c.drawString(70, y, "Le salarié bénéficiera des congés payés conformément")
        y -= 12
        c.drawString(70, y, "aux dispositions de la loi 90-11 et du règlement intérieur.")
        y -= 20
        
        y = check_new_page(y)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Article 8 : Obligations du salarié")
        y -= 14
        c.setFont("Helvetica", 9)
        c.drawString(70, y, "Le salarié s'engage à respecter le règlement intérieur,")
        y -= 12
        c.drawString(70, y, "exécuter ses tâches avec soin et préserver la confidentialité.")
        y -= 20
        
        y = check_new_page(y)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Article 9 : Préavis")
        y -= 14
        c.setFont("Helvetica", 9)
        c.drawString(70, y, "En cas de rupture, un préavis d'un (1) mois devra être respecté,")
        y -= 12
        c.drawString(70, y, "sauf en cas de faute grave.")
        y -= 20
        
        y = check_new_page(y)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Article 10 : Litiges")
        y -= 14
        c.setFont("Helvetica", 9)
        c.drawString(70, y, "Tout différend sera soumis aux juridictions compétentes.")
        y -= 30
        
        # ========== DATE ET SIGNATURES ==========
        y = check_new_page(y, 120)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(width/2, y, f"Fait à Chelghoum Laid, le {date_aujourdhui}")
        y -= 14
        c.setFont("Helvetica", 8)
        c.drawCentredString(width/2, y, "En deux exemplaires originaux")
        y -= 40
        
        # Signatures
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(150, y, "L'EMPLOYEUR")
        c.drawCentredString(width - 150, y, "LE SALARIÉ")
        y -= 50
        
        c.setFont("Helvetica", 8)
        c.drawCentredString(150, y, "(Signature et cachet)")
        c.drawCentredString(width - 150, y, "(Signature)")
        
        # Finaliser le PDF
        c.save()
        buffer.seek(0)
        return buffer
    
    def generate_g29(self, annee: int, g29_data) -> bytes:
        """
        Génère le document G29 complet (2 pages en format paysage)
        
        Args:
            annee: Année du rapport
            g29_data: Données G29Response avec recap et employes
        
        Returns:
            Bytes du PDF généré
        """
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
        
        # Page 1: Récapitulatif mensuel
        story.extend(self._build_g29_page1(annee, g29_data.recap))
        story.append(PageBreak())
        
        # Page 2: Détails employés
        story.extend(self._build_g29_page2(annee, g29_data.employes))
        
        # Générer le PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    
    def _build_g29_page1(self, annee: int, recap):
        """Construit la page 1 du G29 (récapitulatif mensuel)"""
        elements = []
        parametres = self._get_parametres()
        
        # En-tête administratif
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=11
        )
        
        elements.append(Paragraph("<b>ADMINISTRATION DES IMPOTS</b>", header_style))
        elements.append(Paragraph("WILAYA DE: MILA", header_style))
        elements.append(Paragraph("COMMUNE DE: CHELGHOUM LAID", header_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Titre
        title_style = ParagraphStyle(
            'G29Title',
            parent=self.styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            spaceAfter=10
        )
        
        elements.append(Paragraph(f"DÉCLARATION ANNUELLE DES SALAIRES - série G29", title_style))
        elements.append(Paragraph(f"<b>ANNÉE {annee}</b>", title_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Informations entreprise
        if parametres:
            info_style = ParagraphStyle(
                'InfoStyle',
                parent=self.styles['Normal'],
                fontSize=9,
                leading=12
            )
            elements.append(Paragraph("<b>ENTREPRISE:</b>", info_style))
            elements.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;{parametres.nom_entreprise or ''}", info_style))
            elements.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;NIF: {parametres.nif or ''}", info_style))
            elements.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;N° ART. IMPOS.: {parametres.numero_article_imposition or ''}", info_style))
            elements.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;Activité: {parametres.activite or ''}", info_style))
            elements.append(Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;Adresse: {parametres.adresse or ''}", info_style))
        
        elements.append(Spacer(1, 0.7*cm))
        
        # Tableau récapitulatif
        elements.append(Paragraph("<b>RÉCAPITULATIF MENSUEL:</b>", self.styles['Normal']))
        elements.append(Spacer(1, 0.3*cm))
        
        # Données du tableau
        mois_noms = [
            "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
        ]
        
        mois_fields = [
            "janvier", "fevrier", "mars", "avril", "mai", "juin",
            "juillet", "aout", "septembre", "octobre", "novembre", "decembre"
        ]
        
        table_data = [["MOIS", "SALAIRES BRUTS (DA)", "IRG RETENU (DA)"]]
        
        total_brut = 0
        total_irg = 0
        
        for mois_nom, mois_field in zip(mois_noms, mois_fields):
            brut = float(getattr(recap, f"{mois_field}_brut", 0))
            irg = float(getattr(recap, f"{mois_field}_irg", 0))
            total_brut += brut
            total_irg += irg
            
            table_data.append([
                mois_nom,
                f"{brut:,.2f}",
                f"{irg:,.2f}"
            ])
        
        # Ligne de total
        table_data.append([
            Paragraph("<b>TOTAL ANNUEL</b>", self.styles['Normal']),
            Paragraph(f"<b>{total_brut:,.2f}</b>", self.styles['Normal']),
            Paragraph(f"<b>{total_irg:,.2f}</b>", self.styles['Normal'])
        ])
        
        # Créer le tableau avec quadrillage (largeurs ajustées pour paysage)
        table = Table(table_data, colWidths=[5*cm, 6*cm, 6*cm])
        table.setStyle(TableStyle([
            # En-têtes
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            
            # Données
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
            
            # Ligne de total
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            
            # Quadrillage complet
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 1*cm))
        
        # Pied de page
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=self.styles['Normal'],
            fontSize=8
        )
        elements.append(Paragraph(f"Date d'établissement: {datetime.now().strftime('%d/%m/%Y')}", footer_style))
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph("Signature et cachet de l'entreprise:", footer_style))
        
        return elements
    
    
    def _build_g29_page2(self, annee: int, employes: list):
        """Construit la page 2 du G29 (détails par employé)"""
        elements = []
        
        # Titre
        title_style = ParagraphStyle(
            'G29Page2Title',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            spaceAfter=10
        )
        
        elements.append(Paragraph(f"DÉTAIL DES SALAIRES PAR EMPLOYÉ - ANNÉE {annee}", title_style))
        elements.append(Spacer(1, 0.3*cm))
        
        # Préparer les données du tableau
        mois_abbr = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
        mois_fields = [
            "janvier", "fevrier", "mars", "avril", "mai", "juin",
            "juillet", "aout", "septembre", "octobre", "novembre", "decembre"
        ]
        
        table_data = []
        
        # Première ligne d'en-têtes: Nom, SF, les 12 mois, TOTAUX
        header_row1 = ["NOM ET PRÉNOM", "SF"]
        for mois in mois_abbr:
            header_row1.extend([mois, ""])  # Chaque mois occupe 2 colonnes (Net + IRG)
        header_row1.extend(["TOTAUX", ""])
        table_data.append(header_row1)
        
        # Deuxième ligne: Net/IRG pour chaque mois + Net/IRG pour totaux
        header_row2 = ["", ""]  # Vides sous Nom et SF
        for _ in range(12):  # 12 mois
            header_row2.extend(["Net", "IRG"])
        header_row2.extend(["Net", "IRG"])  # Totaux
        table_data.append(header_row2)
        
        # Initialiser uniquement les totaux généraux
        total_general_net = 0
        total_general_irg = 0
        
        # Données des employés
        for employe in employes:
            row = []
            
            # Nom et prénom (ajusté pour colonne 3.2cm)
            nom_complet = f"{employe.nom} {employe.prenom}"
            if len(nom_complet) > 24:
                nom_complet = nom_complet[:21] + "..."
            row.append(nom_complet)
            
            # Situation familiale
            row.append(employe.situation_familiale or "")
            
            # Valeurs mensuelles
            for mois_field in mois_fields:
                net = float(getattr(employe, f"{mois_field}_net", 0))
                irg = float(getattr(employe, f"{mois_field}_irg", 0))
                
                row.append(f"{net:,.0f}" if net > 0 else "-")
                row.append(f"{irg:,.0f}" if irg > 0 else "-")
            
            # Totaux individuels
            emp_total_net = float(employe.total_imposable)
            emp_total_irg = float(employe.total_irg)
            total_general_net += emp_total_net
            total_general_irg += emp_total_irg
            
            row.append(f"{emp_total_net:,.0f}")
            row.append(f"{emp_total_irg:,.0f}")
            
            table_data.append(row)
        
        # Ligne de totaux (seulement colonne TOTAUX, pas les mois)
        totaux_row = ["<b>TOTAL GÉNÉRAL</b>", ""]  # Texte simple sans Paragraph
        # Colonnes mensuelles vides (24 colonnes pour 12 mois)
        for _ in range(24):
            totaux_row.append("")
        # Totaux généraux (2 colonnes)
        totaux_row.append(f"{total_general_net:,.0f}")
        totaux_row.append(f"{total_general_irg:,.0f}")
        table_data.append(totaux_row)
        
        # Créer le tableau avec largeurs de colonnes optimisées pour format paysage
        # Largeur disponible: A4 paysage (29.7cm) - marges (3cm) = 26.7cm
        col_widths = [3.2*cm, 0.7*cm]  # Nom, SF
        col_widths.extend([0.85*cm, 0.7*cm] * 12)  # 12 mois × (Net + IRG) = 18.6cm
        col_widths.extend([1.3*cm, 1.3*cm])  # Totaux = 2.6cm
        # Total: 3.2 + 0.7 + 18.6 + 2.6 = 25.1cm (reste 1.6cm de marge interne)
        
        table = Table(table_data, colWidths=col_widths, repeatRows=2)
        
        # Style du tableau avec quadrillage complet
        table_style = [
            # En-têtes
            ('BACKGROUND', (0, 0), (-1, 1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 1), colors.black),
            ('ALIGN', (0, 0), (-1, 1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 1), 6.5),  # Optimisé pour colonnes compactes
            ('BOTTOMPADDING', (0, 0), (-1, 1), 3),
            ('TOPPADDING', (0, 0), (-1, 1), 3),
            
            # Fusion de cellules pour l'en-tête des mois (ligne 1)
            ('SPAN', (0, 0), (0, 1)),  # Nom
            ('SPAN', (1, 0), (1, 1)),  # SF
            ('SPAN', (26, 0), (27, 0)),  # TOTAUX
        ]
        
        # Fusion des en-têtes de mois
        for i in range(12):
            col = 2 + (i * 2)
            table_style.append(('SPAN', (col, 0), (col + 1, 0)))
        
        # Style des données
        table_style.extend([
            ('ALIGN', (0, 2), (0, -1), 'LEFT'),  # Noms à gauche
            ('ALIGN', (1, 2), (1, -1), 'CENTER'),  # SF centré
            ('ALIGN', (2, 2), (-1, -1), 'RIGHT'),  # Valeurs à droite
            ('FONTNAME', (0, 2), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 2), (-1, -1), 5.5),  # Optimisé pour largeurs réduites
            ('TOPPADDING', (0, 2), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 2), (-1, -1), 2),
            ('LEFTPADDING', (0, 2), (-1, -1), 1.5),
            ('RIGHTPADDING', (0, 2), (-1, -1), 1.5),
            
            # Colonnes totaux individuels en gras (2 dernières colonnes)
            ('FONTNAME', (-2, 2), (-1, -2), 'Helvetica-Bold'),
            ('BACKGROUND', (-2, 2), (-1, -2), colors.beige),
            
            # Ligne de total général (dernière ligne)
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 6),
            ('ALIGN', (0, -1), (-1, -1), 'RIGHT'),
            ('LINEABOVE', (0, -1), (-1, -1), 1.5, colors.black),
            ('TOPPADDING', (0, -1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 4),
            
            # Quadrillage complet
            ('GRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.75, colors.black),
            
            # Lignes horizontales plus épaisses tous les 5 employés
            ('LINEBELOW', (0, 1), (-1, 1), 1, colors.black),
        ])
        
        # Ajouter des lignes de séparation tous les 5 employés (sauf dernière ligne qui est le total)
        for i in range(2, len(table_data) - 1, 5):
            if i < len(table_data) - 1:
                table_style.append(('LINEBELOW', (0, i), (-1, i), 0.5, colors.grey))
        
        table.setStyle(TableStyle(table_style))
        
        elements.append(table)
        elements.append(Spacer(1, 0.5*cm))
        
        # Pied de page
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=self.styles['Normal'],
            fontSize=7
        )
        elements.append(Paragraph(f"Date d'établissement: {datetime.now().strftime('%d/%m/%Y')} | Total: {len(employes)} employé(s)", footer_style))
        
        return elements
    









    
    def generate_client_logistics_balance(self, client_data: dict):
        """Generer PDF du solde logistique pour un client"""
        from io import BytesIO
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from datetime import datetime
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, 
                                topMargin=2*cm, bottomMargin=2*cm)
        
        elements = []
        title = Paragraph(f"<b>Solde Logistique - {client_data['client_nom']}</b>", self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))
        date_str = datetime.now().strftime('%d/%m/%Y')
        date_para = Paragraph(f"Genere le {date_str}", self.styles['CustomBody'])
        elements.append(date_para)
        elements.append(Spacer(1, 0.5*cm))
        
        if client_data['balance']:
            table_data = [['Type', 'Prises', 'Retournees', 'Solde']]
            for item in client_data['balance']:
                table_data.append([
                    item['type_name'],
                    str(item['total_prises']),
                    str(item['total_retournees']),
                    str(item['solde'])
                ])
            
            table = Table(table_data, colWidths=[6*cm, 3*cm, 3*cm, 3*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
        else:
            no_data = Paragraph("Aucun mouvement logistique pour ce client.", self.styles['CustomBody'])
            elements.append(no_data)
        
        elements.append(Spacer(1, 1*cm))
        elements.append(self._create_footer())
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def generate_all_clients_logistics_balance(self, clients_data: list):
        """Generer PDF global des soldes logistiques de tous les clients"""
        from io import BytesIO
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.lib import colors
        from datetime import datetime
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, 
                                topMargin=2*cm, bottomMargin=2*cm)
        
        elements = []
        title = Paragraph("<b>Rapport Logistique Global - Tous les Clients</b>", self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))
        date_str = datetime.now().strftime('%d/%m/%Y')
        date_para = Paragraph(f"Genere le {date_str}", self.styles['CustomBody'])
        elements.append(date_para)
        elements.append(Spacer(1, 0.8*cm))
        
        if not clients_data:
            no_data = Paragraph("Aucun client avec mouvements logistiques.", self.styles['CustomBody'])
            elements.append(no_data)
        else:
            for idx, client in enumerate(clients_data):
                client_name = Paragraph(f"<b>{client['client_nom']}</b>", self.styles['CustomHeading'])
                elements.append(client_name)
                elements.append(Spacer(1, 0.3*cm))
                
                table_data = [['Type', 'Prises', 'Retournees', 'Solde']]
                for item in client['balance']:
                    table_data.append([
                        item['type_name'],
                        str(item['total_prises']),
                        str(item['total_retournees']),
                        str(item['solde'])
                    ])
                
                table = Table(table_data, colWidths=[6*cm, 3*cm, 3*cm, 3*cm])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
                ]))
                elements.append(table)
                
                if idx < len(clients_data) - 1:
                    elements.append(Spacer(1, 0.8*cm))
        
        elements.append(Spacer(1, 1*cm))
        elements.append(self._create_footer())
        doc.build(elements)
        buffer.seek(0)
        return buffer

    def generate_tous_bulletins_combines(self, employes_data: List[Dict], periode: Dict) -> BytesIO:
        """
        Générer un PDF combiné contenant tous les bulletins de paie
        + Page de garde
        + Tableau récapitulatif
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm,
            leftMargin=1.5*cm,
            rightMargin=1.5*cm
        )
        
        story = []
        
        # 1. PAGE DE GARDE
        # ----------------
        params = self._get_parametres()
        company_name = params.raison_sociale or params.nom_entreprise or "AY HR"
        
        # Logo (si disponible)
        # TODO: Gestion logo
        
        story.append(Spacer(1, 5*cm))
        
        # Titre
        title_style = ParagraphStyle(
            name='CoverTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            alignment=TA_CENTER,
            spaceAfter=30
        )
        story.append(Paragraph("BULLETINS DE PAIE", title_style))
        
        # Période
        date_obj = datetime(periode['annee'], periode['mois'], 1)
        mois_str = date_obj.strftime("%B %Y").capitalize()
        subtitle_style = ParagraphStyle(
            name='CoverSubtitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            alignment=TA_CENTER,
            textColor=colors.grey,
            spaceAfter=50
        )
        story.append(Paragraph(mois_str, subtitle_style))
        
        # Infos entreprise
        story.append(Spacer(1, 2*cm))
        story.append(Paragraph(f"<b>Entreprise:</b> {company_name}", self.styles['CustomBody']))
        
        # Résumé
        total_net = sum(e['salaire_data'].get('salaire_net', 0) for e in employes_data)
        story.append(Paragraph(f"<b>Nombre d'employés:</b> {len(employes_data)}", self.styles['CustomBody']))
        story.append(Paragraph(f"<b>Total Net à Payer:</b> {total_net:,.2f} DA", self.styles['CustomBody']))
        
        date_generation = datetime.now().strftime("%d/%m/%Y")
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(f"Généré le: {date_generation}", self.styles['Footer']))
        
        story.append(PageBreak())
        
        # 2. BULLETINS INDIVIDUELS
        # ------------------------
        for i, emp in enumerate(employes_data):
            # Utiliser la logique existante pour générer un bulletin
            # Note: On réimplémente une version simplifiée ou on appelle une méthode interne qui retourne des flowables
            # Pour simplifier ici, on va recréer le contenu du bulletin
            
            # En-tête société
            story.extend(self._create_company_header())
            story.append(Spacer(1, 0.5*cm))
            
            # Titre bulletin
            story.append(Paragraph(f"BULLETIN DE PAIE - {mois_str}", self.styles['CustomTitle']))
            
            # Infos Employé (Tableau)
            emp_info = emp['employe_data']
            sal_data = emp['salaire_data']
            
            # ... (logique similaire à generate_bulletin_paie mais ajoutée à story)
            # Pour l'instant on met un résumé pour ne pas dupliquer tout le code complexe
            # Idéalement il faudrait refactoriser generate_bulletin_paie pour retourner une liste de Flowables
            
            info_data = [
                ['Matricule', str(emp_info.get('id', '')), 'Département', emp_info.get('poste_travail', '')],
                ['Nom', emp_info.get('nom', ''), 'Prénom', emp_info.get('prenom', '')],
                ['Date entrée', emp_info.get('date_recrutement', ''), 'N° SS', emp_info.get('numero_secu_sociale', '')],
                ['Situation', emp_info.get('situation_familiale', ''), 'Enfants', str(emp_info.get('nombre_enfants', 0))]
            ]
            
            t = Table(info_data, colWidths=[2.5*cm, 6*cm, 2.5*cm, 6*cm])
            t.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
                ('BACKGROUND', (2,0), (2,-1), colors.lightgrey),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('PADDING', (0,0), (-1,-1), 4),
            ]))
            story.append(t)
            story.append(Spacer(1, 0.5*cm))
            
            # Corps du bulletin (simplifié pour cet exemple, à étoffer)
            # Ligne de salaire de base
            rubriques = [
                ['Rubrique', 'Base', 'Taux', 'Gains', 'Retenues'],
                ['Salaire de base', f"{sal_data.get('salaire_base_proratis', 0):,.2f}", '', f"{sal_data.get('salaire_base_proratis', 0):,.2f}", ''],
                ['Heures Supplémentaires', '', '', f"{sal_data.get('heures_supplementaires', 0):,.2f}", ''],
                ['Primes & Indemnités', '', '', f"{(sal_data.get('salaire_cotisable', 0) - sal_data.get('salaire_base_proratis', 0) - sal_data.get('heures_supplementaires', 0)):,.2f}", ''],
                ['Sécurité Sociale (9%)', f"{sal_data.get('salaire_cotisable', 0):,.2f}", '9%', '', f"{sal_data.get('retenue_securite_sociale', 0):,.2f}"],
                ['IRG', f"{sal_data.get('salaire_imposable', 0):,.2f}", '', '', f"{sal_data.get('irg', 0):,.2f}"],
                ['Avances', '', '', '', f"{sal_data.get('total_avances', 0):,.2f}"],
                ['TOTAL', '', '', f"{sal_data.get('total_gains', 0):,.2f}", f"{sal_data.get('total_retenues', 0):,.2f}"],
            ]
            
            # Net à payer en grand
            story.append(Spacer(1, 1*cm))
            net_table = Table([
                ['NET À PAYER', f"{sal_data.get('salaire_net', 0):,.2f} DA"]
            ], colWidths=[12*cm, 5*cm])
            net_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.lightgrey),
                ('FONTSIZE', (0,0), (-1,-1), 12),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
                ('ALIGN', (1,0), (1,0), 'RIGHT'),
                ('BOX', (0,0), (-1,-1), 1, colors.black),
                ('PADDING', (0,0), (-1,-1), 10),
            ]))
            story.append(net_table)
            
            # Footer bulletin
            story.append(Spacer(1, 1*cm))
            story.append(Paragraph("Pour acquit,", self.styles['Normal']))
            
            # Saut de page après chaque bulletin sauf le dernier
            story.append(PageBreak())

        # 3. TABLEAU RÉCAPITULATIF
        # ------------------------
        story.append(Paragraph("RÉCAPITULATIF GÉNÉRAL", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        recap_data = [['Nom & Prénom', 'Salaire Base', 'Cotisable', 'Net à Payer']]
        for emp in employes_data:
            d = emp['salaire_data']
            recap_data.append([
                f"{emp['employe_data']['nom']} {emp['employe_data']['prenom']}",
                f"{d.get('salaire_base_proratis', 0):,.2f}",
                f"{d.get('salaire_cotisable', 0):,.2f}",
                f"{d.get('salaire_net', 0):,.2f}"
            ])
            
        # Totaux
        recap_data.append([
            'TOTAL GÉNÉRAL',
            f"{sum(e['salaire_data'].get('salaire_base_proratis', 0) for e in employes_data):,.2f}",
            f"{sum(e['salaire_data'].get('salaire_cotisable', 0) for e in employes_data):,.2f}",
            f"{total_net:,.2f}"
        ])
        
        recap_table = Table(recap_data, colWidths=[7*cm, 3.5*cm, 3.5*cm, 3.5*cm])
        recap_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
            ('BACKGROUND', (0,-1), (-1,-1), colors.lightgrey),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ]))
        story.append(recap_table)
        
        doc.build(story)
        buffer.seek(0)
        return buffer

    def generate_rapport_salaires(self, resultats: List[Dict], periode: Dict) -> BytesIO:
        """
        Générer rapport récapitulatif des salaires du mois (nouveau module v3.0)
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, 
                               topMargin=2*cm, bottomMargin=2*cm)
        story = []
        
        # Titre
        mois_nom = datetime(periode['annee'], periode['mois'], 1).strftime('%B %Y').capitalize()
        story.append(Paragraph(f"<b>RAPPORT DES SALAIRES - {mois_nom}</b>", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.5*cm))
        
        # Statistiques globales
        total_employes = len(resultats)
        total_brut = sum(float(r['salaire_cotisable']) for r in resultats)
        total_net = sum(float(r['salaire_net']) for r in resultats)
        total_irg = sum(float(r['irg']) for r in resultats)
        total_ss = sum(float(r['retenue_securite_sociale']) for r in resultats)
        
        stats_data = [
            ['STATISTIQUES GÉNÉRALES', ''],
            ['Nombre d\'employés:', str(total_employes)],
            ['Masse salariale brute (cotisable):', f"{total_brut:,.2f} DA"],
            ['Total retenues Séc. Sociale:', f"{total_ss:,.2f} DA"],
            ['Total IRG:', f"{total_irg:,.2f} DA"],
            ['Masse salariale nette:', f"{total_net:,.2f} DA"],
        ]
        
        stats_table = Table(stats_data, colWidths=[10*cm, 7*cm])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#366092')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('FONTNAME', (0,1), (0,-1), 'Helvetica-Bold'),
            ('ALIGN', (1,1), (1,-1), 'RIGHT'),
            ('BACKGROUND', (0,-1), (-1,-1), colors.lightgrey),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ]))
        story.append(stats_table)
        story.append(Spacer(1, 0.7*cm))
        
        # Détail par employé
        story.append(Paragraph("<b>DÉTAIL PAR EMPLOYÉ</b>", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.3*cm))
        
        detail_data = [
            ['Employé', 'J.Trav', 'Base', 'Cotisable', 'IRG', 'Net']
        ]
        
        for r in resultats:
            detail_data.append([
                f"{r['employe_nom']} {r['employe_prenom']}",
                str(r['jours_travailles']),
                f"{float(r['salaire_base']):,.0f}",
                f"{float(r['salaire_cotisable']):,.0f}",
                f"{float(r['irg']):,.0f}",
                f"{float(r['salaire_net']):,.0f}"
            ])
        
        # Ligne de totaux
        detail_data.append([
            'TOTAUX',
            '',
            f"{sum(float(r['salaire_base']) for r in resultats):,.0f}",
            f"{total_brut:,.0f}",
            f"{total_irg:,.0f}",
            f"{total_net:,.0f}"
        ])
        
        detail_table = Table(detail_data, colWidths=[6*cm, 1.5*cm, 2.5*cm, 2.5*cm, 2.5*cm, 2.5*cm])
        detail_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#366092')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('FONTSIZE', (0,1), (-1,-1), 8),
            ('ALIGN', (1,0), (-1,-1), 'CENTER'),
            ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
            ('BACKGROUND', (0,-1), (-1,-1), colors.lightgrey),
            ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ]))
        story.append(detail_table)
        
        # Footer
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(
            f"<i>Rapport généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}</i>",
            self.styles['CustomBody']
        ))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
