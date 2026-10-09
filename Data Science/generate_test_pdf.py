import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def create_healthos_sample_pdf(filename="sample_health_facility_spec.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom Brand Palette (#0B839E, #16303B)
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor("#0B839E"),
        spaceAfter=12
    )
    
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor("#16303B"),
        spaceBefore=14,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#333333"),
        spaceAfter=8
    )

    story = []

    # Document Header
    story.append(Paragraph("HealthOS™ Facility Operational Specifications", title_style))
    story.append(Paragraph("<b>Document ID:</b> HOS-SPEC-2026-V1 &nbsp;&nbsp;|&nbsp;&nbsp; <b>Facility Type:</b> Regional Medical Center", body_style))
    story.append(Spacer(1, 12))

    # Section 1: Facility Overview
    story.append(Paragraph("1. Facility Room & Layout Standards", heading_style))
    story.append(Paragraph(
        "This specification document outlines room operational guidelines, HVAC airflow requirements, and power specifications for primary medical care zones. "
        "All facility managers must ensure strict compliance with cleanroom ISO class 7 parameters in surgical areas.",
        body_style
    ))

    # Section 2: Structured Table Data
    story.append(Paragraph("2. Operational Room Parameters", heading_style))
    
    table_data = [
        ["Room ID", "Zone Name", "Target Temp (°C)", "Air Exchanges/Hr", "Backup Power"],
        ["ICU-101", "Intensive Care Unit", "21.5°C", "12 exchanges", "UPS + Generator"],
        ["OR-202", "Surgical Operating Room", "19.0°C", "20 exchanges", "Dual UPS Isolated"],
        ["LAB-305", "Diagnostic Pathology Lab", "22.0°C", "8 exchanges", "Standard Generator"],
        ["RAD-401", "Radiology MRI Suite", "18.5°C", "15 exchanges", "Dedicated Line"]
    ]

    t = Table(table_data, colWidths=[70, 150, 95, 105, 120])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0B839E")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#F9F9F9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor("#16303B")),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8.5),
        ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
    ]))

    story.append(t)
    story.append(Spacer(1, 14))

    # Section 3: Safety & Emergency Protocols
    story.append(Paragraph("3. Emergency Protocol & Maintenance Schedule", heading_style))
    story.append(Paragraph(
        "Emergency oxygen shut-off valves are positioned adjacent to primary nurse station consoles on levels 1 through 4. "
        "Comprehensive HVAC filter inspections and HEPA filter replacements must occur bi-monthly (every 60 days).",
        body_style
    ))

    # Build PDF
    doc.build(story)
    print(f"PDF successfully generated at: {os.path.abspath(filename)}")

if __name__ == "__main__":
    create_healthos_sample_pdf()