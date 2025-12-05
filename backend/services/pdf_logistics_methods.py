"""
Méthodes additionnelles pour PDFGenerator - Logistique Clients
À ajouter à la classe PDFGenerator dans pdf_generator.py
"""

def generate_client_logistics_balance(self, client_data: dict):
    """Générer PDF du solde logistique pour un client"""
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
    
    # Titre
    title = Paragraph(f"<b>Solde Logistique - {client_data['client_nom']}</b>", self.styles['CustomTitle'])
    elements.append(title)
    elements.append(Spacer(1, 0.5*cm))
    
    # Date
    date_str = datetime.now().strftime('%d/%m/%Y')
    date_para = Paragraph(f"Généré le {date_str}", self.styles['CustomBody'])
    elements.append(date_para)
    elements.append(Spacer(1, 0.5*cm))
    
    # Tableau des soldes
    if client_data['balance']:
        table_data = [['Type', 'Prises', 'Retournées', 'Solde']]
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
    """Générer PDF global des soldes logistiques de tous les clients"""
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
    
    # Titre
    title = Paragraph("<b>Rapport Logistique Global - Tous les Clients</b>", self.styles['CustomTitle'])
    elements.append(title)
    elements.append(Spacer(1, 0.5*cm))
    
    # Date
    date_str = datetime.now().strftime('%d/%m/%Y')
    date_para = Paragraph(f"Généré le {date_str}", self.styles['CustomBody'])
    elements.append(date_para)
    elements.append(Spacer(1, 0.8*cm))
    
    if not clients_data:
        no_data = Paragraph("Aucun client avec mouvements logistiques.", self.styles['CustomBody'])
        elements.append(no_data)
    else:
        # Pour chaque client
        for idx, client in enumerate(clients_data):
            # Nom du client
            client_name = Paragraph(f"<b>{client['client_nom']}</b>", self.styles['CustomHeading'])
            elements.append(client_name)
            elements.append(Spacer(1, 0.3*cm))
            
            # Tableau
            table_data = [['Type', 'Prises', 'Retournées', 'Solde']]
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
            
            # Espace entre clients
            if idx < len(clients_data) - 1:
                elements.append(Spacer(1, 0.8*cm))
    
    elements.append(Spacer(1, 1*cm))
    elements.append(self._create_footer())
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
