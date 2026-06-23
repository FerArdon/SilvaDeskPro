"""
utils/pdf_dashboard.py – Generador de Reporte PDF Consolidado por Predio
SilvaDesk Pro · SEDCAF / ICF / FEMA Honduras
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image as RLImage
import os
from datetime import datetime

# Paleta premium del dashboard (Esmeralda oscuro / Judicial integrado)
COLOR_OSC = HexColor("#004D40")   # Esmeralda oscuro
COLOR_MED = HexColor("#00796B")   # Esmeralda medio
COLOR_CLR = HexColor("#E0F2F1")   # Esmeralda tenue
COLOR_FEMA = HexColor("#005FB8")  # Azul FEMA
COLOR_ALERTA = HexColor("#D32F2F")# Rojo alerta
GRIS_BG = HexColor("#F5F5F5")
GRIS_TXT = HexColor("#555555")
NEGRO = HexColor("#111111")

def _logo_path():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for name in ("icon_blue.png", "logo.png"):
        p = os.path.join(base, "assets", name)
        if os.path.exists(p): return p
    return ""

def _seccion_titulo(titulo, story, st, color=COLOR_MED):
    tbl = Table([[Paragraph(f"  {titulo}", ParagraphStyle(
        "sec_title", parent=st["Normal"],
        fontSize=9.5, fontName="Helvetica-Bold",
        textColor=white, leading=13
    ))]], colWidths=[17.5*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), color),
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
    ]))
    story.append(Spacer(1, 10))
    story.append(tbl)
    story.append(Spacer(1, 6))

def generar_pdf_ficha_consolidada(ruta_pdf: str, datos: dict) -> str:
    os.makedirs(os.path.dirname(ruta_pdf) if os.path.dirname(ruta_pdf) else ".", exist_ok=True)
    
    doc = SimpleDocTemplate(ruta_pdf, pagesize=letter,
        leftMargin=2.0*cm, rightMargin=2.0*cm,
        topMargin=1.8*cm, bottomMargin=2.0*cm,
        title=f"Ficha Consolidada - {datos.get('predio','')}",
        author="SilvaDesk Pro Honduras")

    st = getSampleStyleSheet()
    story = []
    
    predio = datos.get("predio", "")
    volumen_total = datos.get("volumen_total", 0.0)
    inspecciones_total = datos.get("inspecciones_total", 0)
    plagas_total = datos.get("plagas_total", 0)
    lista_tfc = datos.get("lista_tfc", [])
    lista_fema = datos.get("lista_fema", [])
    fecha_gen = datos.get("fecha_generacion", "")
    perito_nombre = datos.get("perito_nombre", "Ing. Fernando Rafael Ardon Rodriguez")
    empresa_nombre = datos.get("empresa_nombre", "SEDCAF")

    # 1. CABECERA
    logo_p = _logo_path()
    logo_img = RLImage(logo_p, width=1.6*cm, height=1.6*cm) if logo_p else Paragraph("🌿", ParagraphStyle(
        "em_logo", parent=st["Normal"], fontSize=24, textColor=white, alignment=TA_CENTER))

    s_tit = ParagraphStyle("h_tit", parent=st["Normal"], fontSize=11, leading=14, fontName="Helvetica-Bold", textColor=white)
    s_sub = ParagraphStyle("h_sub", parent=st["Normal"], fontSize=8.5, leading=12, textColor=white)
    s_rc = ParagraphStyle("h_rc", parent=st["Normal"], fontSize=13, leading=16, fontName="Helvetica-Bold", textColor=white, alignment=TA_RIGHT)
    s_rf = ParagraphStyle("h_rf", parent=st["Normal"], fontSize=8.5, leading=11, textColor=HexColor("#B2DFDB"), alignment=TA_RIGHT)

    hdr = Table([[
        logo_img,
        [
            Paragraph("SILVADESK PRO · REGISTRO FORESTAL UNIFICADO", s_tit),
            Paragraph("Gestión Técnica Silvicultural y Control Ambiental de Honduras", s_sub),
            Paragraph("SEDCAF / ICF / FEMA - Sistema Integrado de Expedientes", ParagraphStyle("h_mini", parent=st["Normal"], fontSize=7.5, leading=10, textColor=HexColor("#B2DFDB"))),
        ],
        [
            Paragraph("FICHA CONSOLIDADA", s_rc),
            Paragraph(f"Predio: <b>{predio[:20]}</b>", s_rf),
            Paragraph(f"Emitido: {fecha_gen[:10]}", s_rf),
        ]
    ]], colWidths=[2.2*cm, 9.8*cm, 5.5*cm])

    hdr.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), COLOR_OSC),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1), 8),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
        ("LEFTPADDING",   (1,0),(1,0),   4),
        ("RIGHTPADDING",  (2,0),(2,0),   8),
        ("LINEBELOW",     (0,0),(-1,-1), 2.5, COLOR_MED),
    ]))
    story.append(hdr)
    story.append(Spacer(1, 10))

    # 2. INFORMACIÓN GENERAL Y CONTROLES
    s_label = ParagraphStyle("flbl", parent=st["Normal"], fontSize=8, fontName="Helvetica-Bold", textColor=COLOR_MED, leading=10)
    s_value = ParagraphStyle("fval", parent=st["Normal"], fontSize=8.5, textColor=NEGRO, leading=11)
    
    info_table = Table([
        [
            Paragraph("PREDIO / SITIO FORESTAL:", s_label),
            Paragraph(f"<b>{predio}</b>", s_value),
            Paragraph("PERITO FORESTAL:", s_label),
            Paragraph(perito_nombre, s_value),
        ],
        [
            Paragraph("FECHA DE EXPORTACIÓN:", s_label),
            Paragraph(fecha_gen, s_value),
            Paragraph("CONSULTORA / EMPRESA:", s_label),
            Paragraph(empresa_nombre, s_value),
        ]
    ], colWidths=[4.2*cm, 4.8*cm, 3.8*cm, 4.7*cm])
    
    info_table.setStyle(TableStyle([
        ("VALIGN", (0,0),(-1,-1), "TOP"),
        ("LINEBELOW", (0,0),(-1,-1), 0.5, HexColor("#E0E0E0")),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("TOPPADDING", (0,0),(-1,-1), 4),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 10))

    # 3. MÓDULO KPIs EN TARJETAS
    # Formatear el volumen con comas para miles
    vol_formateado = f"{volumen_total:,.2f}"
    
    kpi_cols = [5.8*cm, 5.8*cm, 5.9*cm]
    kpi_tbl = Table([
        [
            [
                Paragraph("<b>VOLUMEN TOTAL CUBICADO</b>", ParagraphStyle("k1", parent=st["Normal"], fontSize=8, textColor=COLOR_MED, alignment=TA_CENTER)),
                Spacer(1, 4),
                Paragraph(f"<b>{vol_formateado} m³</b>", ParagraphStyle("k1v", parent=st["Normal"], fontSize=15, fontName="Helvetica-Bold", textColor=NEGRO, alignment=TA_CENTER)),
                Spacer(1, 2),
                Paragraph("Madera cubicada en campo", ParagraphStyle("k1n", parent=st["Normal"], fontSize=7, textColor=GRIS_TXT, alignment=TA_CENTER))
            ],
            [
                Paragraph("<b>ALERTAS SALUD FORESTAL</b>", ParagraphStyle("k2", parent=st["Normal"], fontSize=8, textColor=COLOR_ALERTA, alignment=TA_CENTER)),
                Spacer(1, 4),
                Paragraph(f"<b>{plagas_total}</b>", ParagraphStyle("k2v", parent=st["Normal"], fontSize=15, fontName="Helvetica-Bold", textColor=COLOR_ALERTA if plagas_total > 0 else NEGRO, alignment=TA_CENTER)),
                Spacer(1, 2),
                Paragraph("Brotes / Incidencias de plagas", ParagraphStyle("k2n", parent=st["Normal"], fontSize=7, textColor=GRIS_TXT, alignment=TA_CENTER))
            ],
            [
                Paragraph("<b>ACTUACIONES FEMA</b>", ParagraphStyle("k3", parent=st["Normal"], fontSize=8, textColor=COLOR_FEMA, alignment=TA_CENTER)),
                Spacer(1, 4),
                Paragraph(f"<b>{inspecciones_total}</b>", ParagraphStyle("k3v", parent=st["Normal"], fontSize=15, fontName="Helvetica-Bold", textColor=NEGRO, alignment=TA_CENTER)),
                Spacer(1, 2),
                Paragraph("Actas de peritaje judicial", ParagraphStyle("k3n", parent=st["Normal"], fontSize=7, textColor=GRIS_TXT, alignment=TA_CENTER))
            ]
        ]
    ], colWidths=kpi_cols)
    
    kpi_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(0,0), HexColor("#E0F2F1")),
        ("BACKGROUND", (1,0),(1,0), HexColor("#FFEBEE") if plagas_total > 0 else HexColor("#F5F5F5")),
        ("BACKGROUND", (2,0),(2,0), HexColor("#E3F2FD")),
        ("BOX", (0,0),(0,0), 1, HexColor("#B2DFDB")),
        ("BOX", (1,0),(1,0), 1, HexColor("#FFCDD2") if plagas_total > 0 else HexColor("#E0E0E0")),
        ("BOX", (2,0),(2,0), 1, HexColor("#BBDEFB")),
        ("VALIGN", (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0),(-1,-1), 8),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
    ]))
    story.append(kpi_tbl)
    story.append(Spacer(1, 10))

    # 4. REGISTROS TFC (BITÁCORAS DE CAMPO)
    _seccion_titulo("1. DETALLE DE ACTIVIDADES OPERATIVAS EN EJECUCIÓN (BITÁCORAS TFC)", story, st, COLOR_MED)
    
    if lista_tfc:
        tfc_headers = [
            Paragraph("<b>Bitácora No.</b>", ParagraphStyle("th", parent=st["Normal"], fontSize=8, fontName="Helvetica-Bold", textColor=white)),
            Paragraph("<b>Fecha</b>", ParagraphStyle("th", parent=st["Normal"], fontSize=8, fontName="Helvetica-Bold", textColor=white)),
            Paragraph("<b>Tipo de Actividad</b>", ParagraphStyle("th", parent=st["Normal"], fontSize=8, fontName="Helvetica-Bold", textColor=white)),
            Paragraph("<b>Volumen (m³)</b>", ParagraphStyle("th", parent=st["Normal"], fontSize=8, fontName="Helvetica-Bold", textColor=white, alignment=TA_RIGHT)),
            Paragraph("<b>Técnico Responsable</b>", ParagraphStyle("th", parent=st["Normal"], fontSize=8, fontName="Helvetica-Bold", textColor=white)),
            Paragraph("<b>Estado</b>", ParagraphStyle("th", parent=st["Normal"], fontSize=8, fontName="Helvetica-Bold", textColor=white, alignment=TA_CENTER))
        ]
        
        tfc_rows = [tfc_headers]
        for row in lista_tfc:
            # row: num_bitacora, fecha, actividad_tipo, volumen_m3, estado, tfc_nombre
            num_bit, fec, act, vol, est, tec = row
            tfc_rows.append([
                Paragraph(num_bit, s_value),
                Paragraph(fec, s_value),
                Paragraph(act, s_value),
                Paragraph(f"{float(vol or 0.0):,.2f} m³", ParagraphStyle("tr_v", parent=s_value, alignment=TA_RIGHT)),
                Paragraph(tec, s_value),
                Paragraph(est, ParagraphStyle("tr_e", parent=s_value, fontName="Helvetica-Bold", alignment=TA_CENTER, textColor=HexColor("#1B5E20") if est=="Activo" else HexColor("#777777")))
            ])
            
        t_tfc = Table(tfc_rows, colWidths=[2.8*cm, 2.2*cm, 4.5*cm, 2.4*cm, 3.8*cm, 1.8*cm])
        t_tfc.setStyle(TableStyle([
            ("BACKGROUND", (0,0),(-1,0), COLOR_MED),
            ("VALIGN", (0,0),(-1,-1), "MIDDLE"),
            ("GRID", (0,0),(-1,-1), 0.5, HexColor("#E0E0E0")),
            ("ROWBACKGROUNDS", (0,1),(-1,-1), [white, HexColor("#F9FBF9")]),
            ("TOPPADDING", (0,0),(-1,-1), 4),
            ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ]))
        story.append(t_tfc)
    else:
        story.append(Paragraph("<i>No se registran actividades de campo TFC asentadas para este predio.</i>", ParagraphStyle("no_t", parent=st["Normal"], fontSize=8.5, textColor=GRIS_TXT)))
    
    story.append(Spacer(1, 10))

    # 5. REGISTROS FEMA (ACTAS JURÍDICAS PERICIALES)
    _seccion_titulo("2. ACTAS DE PERITAJE FORESTAL Y DILIGENCIAS JUDICIALES (FEMA)", story, st, COLOR_FEMA)
    
    if lista_fema:
        fema_headers = [
            Paragraph("<b>Acta No.</b>", ParagraphStyle("fh", parent=st["Normal"], fontSize=8, fontName="Helvetica-Bold", textColor=white)),
            Paragraph("<b>Fecha</b>", ParagraphStyle("fh", parent=st["Normal"], fontSize=8, fontName="Helvetica-Bold", textColor=white)),
            Paragraph("<b>Tipo de Diligencia</b>", ParagraphStyle("fh", parent=st["Normal"], fontSize=8, fontName="Helvetica-Bold", textColor=white)),
            Paragraph("<b>Expediente FEMA</b>", ParagraphStyle("fh", parent=st["Normal"], fontSize=8, fontName="Helvetica-Bold", textColor=white)),
            Paragraph("<b>Estado del Acta</b>", ParagraphStyle("fh", parent=st["Normal"], fontSize=8, fontName="Helvetica-Bold", textColor=white, alignment=TA_CENTER))
        ]
        
        fema_rows = [fema_headers]
        for row in lista_fema:
            # row: num_acta, fecha, tipo_diligencia, num_expediente_fema, estado
            num_a, fec, tipo_d, exp_f, est = row
            fema_rows.append([
                Paragraph(num_a, s_value),
                Paragraph(fec, s_value),
                Paragraph(tipo_d, s_value),
                Paragraph(exp_f if exp_f else "(No asignado)", s_value),
                Paragraph(est, ParagraphStyle("fr_e", parent=s_value, fontName="Helvetica-Bold", alignment=TA_CENTER, textColor=HexColor("#005FB8") if est=="Activa" else HexColor("#D32F2F") if est=="Anulada" else HexColor("#777777")))
            ])
            
        t_fema = Table(fema_rows, colWidths=[2.8*cm, 2.2*cm, 6.5*cm, 3.8*cm, 2.2*cm])
        t_fema.setStyle(TableStyle([
            ("BACKGROUND", (0,0),(-1,0), COLOR_FEMA),
            ("VALIGN", (0,0),(-1,-1), "MIDDLE"),
            ("GRID", (0,0),(-1,-1), 0.5, HexColor("#E0E0E0")),
            ("ROWBACKGROUNDS", (0,1),(-1,-1), [white, HexColor("#F5F9FC")]),
            ("TOPPADDING", (0,0),(-1,-1), 4),
            ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ]))
        story.append(t_fema)
    else:
        story.append(Paragraph("<i>No se registran actas de protocolo pericial de la fiscalía FEMA en este predio.</i>", ParagraphStyle("no_f", parent=st["Normal"], fontSize=8.5, textColor=GRIS_TXT)))

    story.append(Spacer(1, 20))

    # 6. FIRMA Y CERTIFICACIÓN
    s_firma = ParagraphStyle("fsig", parent=st["Normal"], fontSize=8, alignment=TA_CENTER, leading=10)
    sig_table = Table([
        [
            [
                Spacer(1, 25),
                HRFlowable(width="65%", thickness=1, color=HexColor("#999"), spaceBefore=2, spaceAfter=2),
                Paragraph("<b>Firma del Perito Responsable</b>", s_firma),
                Paragraph(perito_nombre, s_firma),
                Paragraph("Consultor Técnico Autorizado", s_firma),
            ],
            [
                Spacer(1, 25),
                HRFlowable(width="65%", thickness=1, color=HexColor("#999"), spaceBefore=2, spaceAfter=2),
                Paragraph("<b>Sello y Firma SEDCAF</b>", s_firma),
                Paragraph(empresa_nombre, s_firma),
                Paragraph("Control Unificado de Calidad", s_firma),
            ]
        ]
    ], colWidths=[8.7*cm, 8.8*cm])
    sig_table.setStyle(TableStyle([
        ("VALIGN", (0,0),(-1,-1), "TOP"),
        ("TOPPADDING", (0,0),(-1,-1), 5),
    ]))
    
    # Keep the signature together to avoid page orphan lines
    from reportlab.platypus import KeepTogether
    story.append(KeepTogether(sig_table))

    # Construir documento
    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(HexColor("#666666"))
        page_num = canvas.getPageNumber()
        canvas.drawString(2.0*cm, 1.2*cm, "SilvaDesk Pro — Ficha Consolidada Forestal (SEDCAF / ICF / FEMA)")
        canvas.drawRightString(doc.pagesize[0] - 2.0*cm, 1.2*cm, f"Página {page_num}")
        canvas.restoreState()
        
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    return ruta_pdf
