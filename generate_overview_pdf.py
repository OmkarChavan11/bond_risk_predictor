from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime

# Create PDF
pdf_file = "BondRisk_AI_Project_Overview.pdf"
doc = SimpleDocTemplate(pdf_file, pagesize=letter,
                        rightMargin=0.75*inch, leftMargin=0.75*inch,
                        topMargin=0.75*inch, bottomMargin=0.75*inch)

# Container for PDF elements
elements = []

# Define styles
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=24,
    textColor=colors.HexColor('#1f77b4'),
    spaceAfter=12,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=14,
    textColor=colors.HexColor('#2ca02c'),
    spaceAfter=8,
    spaceBefore=8,
    fontName='Helvetica-Bold'
)

subheading_style = ParagraphStyle(
    'CustomSubHeading',
    parent=styles['Heading3'],
    fontSize=11,
    textColor=colors.HexColor('#d62728'),
    spaceAfter=6,
    fontName='Helvetica-Bold'
)

body_style = ParagraphStyle(
    'CustomBody',
    parent=styles['BodyText'],
    fontSize=10,
    alignment=TA_JUSTIFY,
    spaceAfter=6
)

# Title
elements.append(Paragraph("🛡️ BondRisk AI: Varthana Credit Analysis", title_style))
elements.append(Paragraph("Project Overview & Technical Documentation", styles['Normal']))
elements.append(Spacer(1, 0.2*inch))

# Date
elements.append(Paragraph(f"<i>Generated: {datetime.now().strftime('%B %d, %Y')}</i>", styles['Normal']))
elements.append(Spacer(1, 0.3*inch))

# Table of Contents
elements.append(Paragraph("<b>TABLE OF CONTENTS</b>", heading_style))
toc_items = [
    "1. Project Overview",
    "2. Project Architecture",
    "3. File Structure & Components",
    "4. Data Ingestion Pipeline",
    "5. Risk Calculation Engine",
    "6. Web Dashboard",
    "7. Complete Workflow",
    "8. Key Technologies",
    "9. Project Goals"
]
for item in toc_items:
    elements.append(Paragraph(item, body_style))
elements.append(Spacer(1, 0.2*inch))

# Section 1: Project Overview
elements.append(PageBreak())
elements.append(Paragraph("1. PROJECT OVERVIEW", heading_style))
elements.append(Paragraph(
    "BondRisk AI is a comprehensive <b>Bond Risk Assessment platform</b> that automatically extracts financial metrics from OCR-processed documents and calculates credit risk breach probabilities using artificial intelligence and machine learning algorithms. The system is specifically designed to analyze Varthana (an NBFC) financial documents and assess compliance with regulatory covenants.",
    body_style
))
elements.append(Spacer(1, 0.15*inch))

# Section 2: Architecture
elements.append(Paragraph("2. PROJECT ARCHITECTURE", heading_style))
elements.append(Paragraph(
    "<b>Data Flow:</b>",
    body_style
))
elements.append(Paragraph(
    "OCR Documents → Ingestion (DB) → Chunking → Retrieval → LLM Extraction → Risk Engine → Dashboard",
    body_style
))
elements.append(Spacer(1, 0.15*inch))

# Section 3: File Structure
elements.append(Paragraph("3. FILE STRUCTURE & COMPONENTS", heading_style))
elements.append(Paragraph(
    "The project is organized into three main components:",
    body_style
))
elements.append(Spacer(1, 0.1*inch))

# Main components table
components_data = [
    ['Component', 'Location', 'Purpose'],
    ['Data Ingestion', 'src/ingestion/', 'Process OCR files and store in database'],
    ['Risk Engine', 'src/models/', 'Calculate breach probability using ML'],
    ['Web Dashboard', 'src/web_app/', 'Visualize metrics and risk scores']
]
comp_table = Table(components_data, colWidths=[1.5*inch, 1.5*inch, 2.5*inch])
comp_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ca02c')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
]))
elements.append(comp_table)
elements.append(Spacer(1, 0.2*inch))

# Section 4: Data Ingestion
elements.append(Paragraph("4. DATA INGESTION PIPELINE", heading_style))
elements.append(Paragraph("4.1 watcher.py - File System Monitor", subheading_style))
elements.append(Paragraph(
    "<b>Purpose:</b> Monitors the data/ocr_output/varthana/ directory for new OCR files using the watchdog library. When a .txt file is detected, it is automatically classified based on filename (Quarterly_Report or IM) and triggers the ingestion process.",
    body_style
))
elements.append(Spacer(1, 0.1*inch))

elements.append(Paragraph("4.2 db_ingestion.py - Database Ingestion & Chunking", subheading_style))
elements.append(Paragraph(
    "<b>Purpose:</b> Processes OCR text and stores it in PostgreSQL (Neon DB). The script:<br/>"
    "• Connects to Neon PostgreSQL database<br/>"
    "• Creates/retrieves issuer (Varthana) records<br/>"
    "• Registers documents with metadata<br/>"
    "• Chunks text using RecursiveCharacterTextSplitter (1000 char chunks, 200 char overlap)<br/>"
    "• Bulk inserts chunks into database for high performance",
    body_style
))
elements.append(Spacer(1, 0.1*inch))

elements.append(Paragraph("4.3 auto_extractor.py - AI-Powered Metric Extraction", subheading_style))
elements.append(Paragraph(
    "<b>Purpose:</b> Uses Google Gemini 2.5 Flash LLM to extract key financial metrics from document chunks. Extracts 4 key metrics: Capital Adequacy Ratio (CRAR), Leverage Ratio, Asset Quality (Net NPA), and Security Cover. Evaluates compliance status and stores results in database.",
    body_style
))
elements.append(Spacer(1, 0.1*inch))

elements.append(Paragraph("4.4 verify.py - Data Verification Tool", subheading_style))
elements.append(Paragraph(
    "<b>Purpose:</b> Validates data retrieval from database by searching for keywords (e.g., 'Leverage') and returning top matching chunks. Used for testing and debugging the retrieval pipeline.",
    body_style
))
elements.append(Spacer(1, 0.15*inch))

# Database Schema
elements.append(Paragraph("Database Schema:", subheading_style))
schema_text = "issuers → documents → document_sections → financial_metrics"
elements.append(Paragraph(schema_text, body_style))
elements.append(Spacer(1, 0.2*inch))

# Section 5: Risk Engine
elements.append(PageBreak())
elements.append(Paragraph("5. RISK CALCULATION ENGINE", heading_style))
elements.append(Paragraph("5.1 risk_engine.py - ML-Based Risk Scoring", subheading_style))
elements.append(Paragraph(
    "<b>Purpose:</b> Calculates bond breach probability using XGBoost machine learning model. The engine:<br/>"
    "• Fetches latest 4 financial metrics from database<br/>"
    "• Cleans data (converts percentages/ratios to floats)<br/>"
    "• Calculates safety headroom margins<br/>"
    "• Runs XGBoost inference to predict breach probability<br/>"
    "• Outputs risk score as 0-100%<br/>"
    "• Uses weighted heuristic fallback if model unavailable",
    body_style
))
elements.append(Spacer(1, 0.15*inch))

elements.append(Paragraph("<b>Risk Scoring Formula:</b>", subheading_style))
elements.append(Paragraph(
    "Probability = (1 - CAR_headroom) × 0.4 + (1 - Leverage_headroom) × 0.6",
    body_style
))
elements.append(Spacer(1, 0.2*inch))

# Section 6: Dashboard
elements.append(Paragraph("6. WEB DASHBOARD", heading_style))
elements.append(Paragraph("6.1 app.py - Streamlit Interactive Dashboard", subheading_style))
elements.append(Paragraph(
    "<b>Features:</b><br/>"
    "• Page Title: BondRisk AI: Varthana Credit Analysis<br/>"
    "• Left Column: Financial metrics table + risk insights<br/>"
    "• Right Column: Risk probability gauge chart<br/>"
    "• Color coding: Green (0-30%), Orange (30-70%), Red (70-100%)<br/>"
    "<b>Technology Stack:</b> Streamlit (UI), Plotly (visualization)",
    body_style
))
elements.append(Spacer(1, 0.2*inch))

# Section 7: Workflow
elements.append(Paragraph("7. COMPLETE WORKFLOW EXAMPLE", heading_style))
workflow_steps = [
    "1. User places OCR file in monitoring directory",
    "2. watcher.py detects the new file",
    "3. db_ingestion chunks the text (1000 char chunks)",
    "4. auto_extractor searches for covenant-related chunks",
    "5. Chunks sent to Gemini LLM for metric extraction",
    "6. Metrics saved to financial_metrics table",
    "7. User opens Streamlit dashboard",
    "8. Dashboard fetches latest metrics from database",
    "9. risk_engine calculates breach probability via XGBoost",
    "10. Dashboard displays metrics + risk gauge visualization"
]
for step in workflow_steps:
    elements.append(Paragraph(step, body_style))
elements.append(Spacer(1, 0.2*inch))

# Section 8: Technologies
elements.append(PageBreak())
elements.append(Paragraph("8. KEY TECHNOLOGIES", heading_style))

tech_data = [
    ['Technology', 'Purpose'],
    ['Python 3.x', 'Core programming language'],
    ['PostgreSQL (Neon)', 'Cloud database for documents & metrics'],
    ['LangChain', 'Text chunking & splitting'],
    ['Google Gemini API', 'LLM-based metric extraction'],
    ['XGBoost', 'Machine learning risk model'],
    ['Streamlit', 'Web dashboard UI framework'],
    ['Plotly', 'Interactive data visualization'],
    ['Watchdog', 'File system monitoring'],
    ['psycopg2', 'PostgreSQL Python driver']
]
tech_table = Table(tech_data, colWidths=[2*inch, 3.5*inch])
tech_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
    ('GRID', (0, 0), (-1, -1), 1, colors.black)
]))
elements.append(tech_table)
elements.append(Spacer(1, 0.2*inch))

# Section 9: Project Goals
elements.append(Paragraph("9. PROJECT GOALS", heading_style))
goals = [
    "<b>Automate Extraction:</b> Extract financial covenants from quarterly/IM documents",
    "<b>Validate Compliance:</b> Validate compliance against regulatory limits",
    "<b>Predict Default Probability:</b> Use ML models to predict default/breach probability",
    "<b>Visualize Risk:</b> Display risk metrics through interactive dashboard"
]
for goal in goals:
    elements.append(Paragraph("• " + goal, body_style))
elements.append(Spacer(1, 0.2*inch))

# Key Metrics Extracted
elements.append(Paragraph("Key Financial Metrics Extracted:", subheading_style))
metrics_data = [
    ['Metric', 'Target Limit', 'Status', 'Significance'],
    ['Capital Adequacy Ratio', '15%', 'Higher is safer', 'Bank stability & regulatory compliance'],
    ['Leverage Ratio', '4.0x', 'Lower is safer', 'Debt burden relative to equity'],
    ['Asset Quality (Net NPA)', '1-2%', 'Lower is safer', 'Credit quality of loan portfolio'],
    ['Security Cover', '1.1x+', 'Higher is safer', 'Collateral coverage for bondholders']
]
metrics_table = Table(metrics_data, colWidths=[1.5*inch, 1.3*inch, 1.2*inch, 2*inch])
metrics_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d62728')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 9),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffe6e6')),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 9)
]))
elements.append(metrics_table)
elements.append(Spacer(1, 0.3*inch))

# Footer
elements.append(Spacer(1, 0.2*inch))
elements.append(Paragraph("_" * 80, styles['Normal']))
elements.append(Paragraph(
    "<i>This document provides a comprehensive overview of the BondRisk AI project architecture, components, and workflow. "
    "For technical implementation details, refer to individual Python source files in the repository.</i>",
    styles['Normal']
))

# Build PDF
doc.build(elements)
print(f"✅ PDF created successfully: {pdf_file}")
