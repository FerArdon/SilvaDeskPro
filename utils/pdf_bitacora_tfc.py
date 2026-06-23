"""
utils/pdf_bitacora_tfc.py – Generador de Reporte PDF para Bitácora de Campo TFC
SilvaDesk Pro · SEDCAF / ICF Honduras
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, Image as RLImage,
                                 KeepTogether)
import os
from datetime import date as Date

AZUL_O      = HexColor("#1B5E20")   # Verde bosque oscuro
AZUL_M      = HexColor("#2E7D32")   # Verde bosque medio
AZUL_CLR    = HexColor("#E8F5E9")   # Verde de fondo tenue
GRIS_L      = HexColor("#F7F9F7")   # Gris de fondo
GRIS_B      = HexColor("#CCCCCC")   # Gris borde
GRIS_MED    = HexColor("#666666")   # Gris de texto secundario
NEGRO       = black

def _logo_path():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Buscar el ícono del árbol
    for name in ("icon_blue.png", "logo.png"):
        p = os.path.join(base, "assets", name)
        if os.path.exists(p):
            return p
    return ""

def _seccion(titulo, story, st):
    """Agrega un separador de sección institucional en el PDF."""
    tbl = Table([[Paragraph(f"  {titulo}", ParagraphStyle(
        "shtit_tfc", parent=st["Normal"],
        fontSize=9, fontName="Helvetica-Bold",
        textColor=white, leading=13
    ))]], colWidths=[17.4*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), AZUL_M),
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
    ]))
    story.append(Spacer(1, 6))
    story.append(tbl)
    story.append(Spacer(1, 4))

def _campo(label, valor, st, justify=False):
    """Genera el bloque etiqueta-valor con espaciado."""
    aln = TA_JUSTIFY if justify else TA_LEFT
    s_lbl = ParagraphStyle("lbl_tfc", parent=st["Normal"], fontSize=8.5,
                           fontName="Helvetica-Bold", textColor=AZUL_M, leading=12)
    s_val = ParagraphStyle("val_tfc", parent=st["Normal"], fontSize=9.5,
                           leading=14, textColor=HexColor("#111111"), alignment=aln)
    parts = [Paragraph(label, s_lbl)]
    if valor and str(valor).strip():
        parts.append(Paragraph(str(valor), s_val))
    else:
        parts.append(Paragraph("(No registrado)", ParagraphStyle(
            "ns_tfc", parent=st["Normal"], fontSize=9, textColor=GRIS_MED,
            fontName="Helvetica-Oblique", leading=12)))
    return parts

def _draw_anulada_watermark(canvas, doc):
    """Dibuja marca de agua 'ANULADA' sobre la hoja de bitácora."""
    canvas.saveState()
    page_w, page_h = letter
    canvas.translate(page_w / 2, page_h / 2)
    canvas.rotate(45)
    canvas.setFont("Helvetica-Bold", 84)
    canvas.setFillColorRGB(0.78, 0.08, 0.08, alpha=0.10)
    canvas.drawCentredString(0, 20, "ANULADA")
    canvas.setStrokeColorRGB(0.78, 0.08, 0.08, alpha=0.14)
    canvas.setLineWidth(1)
    canvas.drawCentredString(0, 20, "ANULADA")
    canvas.restoreState()

def generar_pdf_bitacora(ruta_pdf: str, datos: dict, anulada: bool = False) -> str:
    os.makedirs(os.path.dirname(ruta_pdf) if os.path.dirname(ruta_pdf) else ".", exist_ok=True)

    doc = SimpleDocTemplate(ruta_pdf, pagesize=letter,
        leftMargin=2.0*cm, rightMargin=2.0*cm,
        topMargin=1.8*cm, bottomMargin=2.5*cm,
        title=f"Bitacora Campo {datos.get('num_bitacora','')}",
        author="SilvaDesk Pro – TFC Honduras")

    st = getSampleStyleSheet()
    story = []
    W = 17.0*cm

    num_bitacora = datos.get("num_bitacora", "")
    folio        = datos.get("folio", "")
    fecha        = datos.get("fecha", "")
    hora         = datos.get("hora", "")
    sitio_predio = datos.get("sitio_predio", "")
    poa_codigo   = datos.get("poa_codigo", "")
    tfc_nombre   = datos.get("tfc_nombre", "")
    tfc_registro = datos.get("tfc_registro", "")
    actividad    = datos.get("actividad_tipo", "")
    detalles     = datos.get("detalles_tecnicos", "")
    volumen      = datos.get("volumen_m3", 0.0)
    plagas       = datos.get("plagas_observadas", "")
    ambiental    = datos.get("cumplimiento_ambiental", "")
    comentarios  = datos.get("comentarios", "")
    estado       = datos.get("estado", "Activo")

    # ═══════════════════════════════════════════════════════════════════════════
    # 1. CABECERA INSTITUCIONAL
    # ═══════════════════════════════════════════════════════════════════════════
    logo_p = _logo_path()
    logo_img = RLImage(logo_p, width=1.8*cm, height=1.8*cm) if logo_p else Paragraph("🌿", ParagraphStyle(
        "em_tfc", parent=st["Normal"], fontSize=24, textColor=white, alignment=TA_CENTER))

    s_wlb = ParagraphStyle("wlb_tfc", parent=st["Normal"], fontSize=10, leading=14,
                           fontName="Helvetica-Bold", textColor=white)
    s_wl = ParagraphStyle("wl_tfc", parent=st["Normal"], fontSize=8.5, leading=12, textColor=white)
    s_wac = ParagraphStyle("wac_tfc", parent=st["Normal"], fontSize=14, leading=18,
                           fontName="Helvetica-Bold", textColor=white, alignment=TA_RIGHT)
    s_wn = ParagraphStyle("wn_tfc", parent=st["Normal"], fontSize=9, leading=12,
                           textColor=HexColor("#A8C8E8"), alignment=TA_RIGHT)

    hdr = Table([[
        logo_img,
        [
            Paragraph("COLEGIO DE PROFESIONALES FORESTALES (COLPROFORH)", s_wlb),
            Paragraph("Instituto de Conservación Forestal (ICF) – Honduras", s_wl),
            Paragraph("Control de Planes Operativos y Aprovechamiento Sostenible", ParagraphStyle("wls2", parent=st["Normal"], fontSize=8, leading=11, textColor=HexColor("#A8C8E8"))),
        ],
        [
            Paragraph("BITÁCORA TFC", s_wac),
            Paragraph(f"Registro: <b>{num_bitacora}</b>", s_wn),
            Paragraph(f"Folio: {folio} · Estado: {estado}", s_wn),
        ],
    ]], colWidths=[2.2*cm, 9.8*cm, 5*cm])

    hdr.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), AZUL_O),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ("LEFTPADDING",   (0,0),(0,0),   10),
        ("LEFTPADDING",   (1,0),(1,0),   8),
        ("RIGHTPADDING",  (2,0),(2,0),   10),
        ("LINEBELOW",     (0,0),(-1,-1), 3, AZUL_M),
    ]))
    story.append(hdr)
    story.append(Spacer(1, 10))

    # ═══════════════════════════════════════════════════════════════════════════
    # 2. INTRODUCCIÓN DE LA ANOTACIÓN DIARIA
    # ═══════════════════════════════════════════════════════════════════════════
    apertura = (
        f"El Técnico Forestal Calificado (TFC) <b>{tfc_nombre}</b>, colegiado bajo el registro "
        f"<b>{tfc_registro}</b>, asienta formalmente en el folio no. <b>{folio}</b> del "
        f"cuaderno de bitácora el reporte del día <b>{fecha}</b> a las <b>{hora}</b> horas, "
        f"correspondiente a las operaciones forestales descritas a continuación:"
    )
    story.append(Paragraph(apertura, ParagraphStyle(
        "apertura_tfc", parent=st["Normal"],
        fontSize=10, leading=16, alignment=TA_JUSTIFY,
        textColor=HexColor("#111111"),
        borderColor=AZUL_M, borderWidth=1,
        borderPadding=(8,8,8,8),
        backColor=AZUL_CLR,
    )))
    story.append(Spacer(1, 10))

    # ═══════════════════════════════════════════════════════════════════════════
    # 3. DATOS DE CONTROL TÉCNICO
    # ═══════════════════════════════════════════════════════════════════════════
    _seccion("I. IDENTIFICACIÓN Y DATOS GENERALES", story, st)

    id_data = [
        ["Predio / Sitio:", sitio_predio, "Código POA:", poa_codigo],
        ["Fecha Actividad:", fecha,        "Hora Acto:", hora],
        ["Actividad Tipo:", actividad,     "Estado Registro:", estado],
    ]
    s_lbl2 = ParagraphStyle("lbl2_tfc", parent=st["Normal"], fontSize=8.5,
                            fontName="Helvetica-Bold", textColor=AZUL_M)
    s_val2 = ParagraphStyle("val2_tfc", parent=st["Normal"], fontSize=9, textColor=NEGRO)

    id_rows = []
    for row in id_data:
        id_rows.append([
            Paragraph(row[0], s_lbl2), Paragraph(row[1] or "—", s_val2),
            Paragraph(row[2], s_lbl2), Paragraph(row[3] or "—", s_val2),
        ])
    id_tbl = Table(id_rows, colWidths=[2.7*cm, 5.8*cm, 2.7*cm, 5.8*cm])
    id_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), GRIS_L),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [GRIS_L, white]),
        ("BOX",           (0,0),(-1,-1), 0.5, GRIS_B),
        ("INNERGRID",     (0,0),(-1,-1), 0.25, GRIS_B),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ]))
    story.append(id_tbl)

    # ═══════════════════════════════════════════════════════════════════════════
    # 4. DETALLES DE CAMPO (HECHOS)
    # ═══════════════════════════════════════════════════════════════════════════
    _seccion("II. ACTIVIDAD REALIZADA Y DETALLES TÉCNICOS DE CAMPO", story, st)
    for p in _campo("Detalles de las actividades realizadas, avance del plan e hitos técnicos:", detalles, st, justify=True):
        story.append(p)
        story.append(Spacer(1, 4))

    # ═══════════════════════════════════════════════════════════════════════════
    # 5. VOLUMEN APROVECHADO (CUBICACIÓN)
    # ═══════════════════════════════════════════════════════════════════════════
    _seccion("III. VOLUMEN DE APROVECHAMIENTO CUBICADO (m³)", story, st)
    vol_text = f"<b>{volumen:,.2f} m³</b> de producto forestal cubicado e intervenido en la jornada."
    for p in _campo("Volumen registrado de extracción:", vol_text, st, justify=False):
        story.append(p)
        story.append(Spacer(1, 4))

    # ═══════════════════════════════════════════════════════════════════════════
    # 6. REGISTRO DE PLAGAS E INCIDENCIAS FORESTALES
    # ═══════════════════════════════════════════════════════════════════════════
    _seccion("IV. MONITOREO DE PLAGAS E INCIDENCIAS", story, st)
    for p in _campo("Monitoreo de gorgojo descortezador, plagas o focos de incendios forestales observados:", plagas, st, justify=True):
        story.append(p)
        story.append(Spacer(1, 4))

    # ═══════════════════════════════════════════════════════════════════════════
    # 7. MEDIDAS AMBIENTALES APLICADAS
    # ═══════════════════════════════════════════════════════════════════════════
    _seccion("V. CUMPLIMIENTO Y MEDIDAS MITIGACIÓN AMBIENTAL", story, st)
    for p in _campo("Medidas aplicadas de mitigación de impacto sobre suelo y microcuencas protectoras:", ambiental, st, justify=True):
        story.append(p)
        story.append(Spacer(1, 4))

    # ═══════════════════════════════════════════════════════════════════════════
    # 8. COMENTARIOS ADICIONALES (opcional)
    # ═══════════════════════════════════════════════════════════════════════════
    if comentarios and comentarios.strip():
        _seccion("VI. OBSERVACIONES Y COMENTARIOS", story, st)
        for p in _campo("", comentarios, st, justify=True):
            story.append(p)
            story.append(Spacer(1, 4))

    # ═══════════════════════════════════════════════════════════════════════════
    # 9. CIERRE Y FIRMA DEL PERITO TFC
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 14))
    cierre_txt = (
        "El suscrito Técnico Forestal Calificado (TFC) da fe del registro de las anteriores actuaciones "
        "técnicas de campo, en pleno acatamiento de las directrices del ICF y el Reglamento Especial para el "
        "Uso de la Bitácora del TFC (La Gaceta No. 36,401). Se firma para constancia legal.<br/>"
        "<b>Nota Reglamentaria</b>: Este folio se emite en duplicado de copia desprendible: Original para "
        "custodia del TFC (mínimo 5 años), Primera Copia para el archivo local del ICF, y Segunda Copia para el "
        "propietario del predio forestal. Las anotaciones deben asentarse en el sitio del POA al menos dos veces "
        "por mes (Art. 8) y presentarse ante el ICF para cierre oficial a más tardar 30 días después de concluido el POA (Art. 11)."
    )
    cierre_tbl = Table([[Paragraph(cierre_txt, ParagraphStyle(
        "cierre_tfc", parent=st["Normal"], fontSize=9.5, leading=15, alignment=TA_JUSTIFY, textColor=HexColor("#111111")
    ))]], colWidths=[W])
    cierre_tbl.setStyle(TableStyle([
        ("BOX",           (0,0),(-1,-1), 0.5, AZUL_M),
        ("BACKGROUND",    (0,0),(-1,-1), GRIS_L),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ("LEFTPADDING",   (0,0),(-1,-1), 12),
        ("RIGHTPADDING",  (0,0),(-1,-1), 12),
    ]))
    story.append(cierre_tbl)
    story.append(Spacer(1, 24))

    # Bloque de firma
    firma_l = Table([
        [HRFlowable(width=6.5*cm, thickness=1.2, color=AZUL_O)],
        [Paragraph(f"<b>{tfc_nombre}</b>", ParagraphStyle("fnom_tfc", parent=st["Normal"], fontSize=9.5, fontName="Helvetica-Bold", alignment=TA_CENTER))],
        [Paragraph("Técnico Forestal Calificado (TFC)", ParagraphStyle("fcarg_tfc", parent=st["Normal"], fontSize=8.5, textColor=AZUL_M, alignment=TA_CENTER))],
        [Paragraph(tfc_registro, ParagraphStyle("fsec_tfc", parent=st["Normal"], fontSize=8, textColor=GRIS_MED, alignment=TA_CENTER))],
        [Paragraph("COLPROFORH / CIFH – Honduras", ParagraphStyle("fmp_tfc", parent=st["Normal"], fontSize=8, textColor=GRIS_MED, alignment=TA_CENTER))],
    ], colWidths=[8*cm])
    firma_l.setStyle(TableStyle([
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))

    firma_r = Table([
        [Paragraph(f"Registro No.: <b>{num_bitacora}</b>", ParagraphStyle("fr1_tfc", parent=st["Normal"], fontSize=8.5, textColor=GRIS_MED))],
        [Paragraph(f"Folio: <b>{folio}</b>", ParagraphStyle("fr2_tfc", parent=st["Normal"], fontSize=8.5, textColor=GRIS_MED))],
        [Paragraph(f"Código POA: <b>{poa_codigo}</b>", ParagraphStyle("fr3_tfc", parent=st["Normal"], fontSize=8.5, textColor=GRIS_MED))],
        [Paragraph(f"Sitio: {sitio_predio}", ParagraphStyle("fr4_tfc", parent=st["Normal"], fontSize=8, textColor=GRIS_MED))],
        [Spacer(1, 6)],
        [Paragraph("Generado con SilvaDesk Pro", ParagraphStyle("fr5_tfc", parent=st["Normal"], fontSize=7, textColor=HexColor("#BBBBBB")))],
    ], colWidths=[7.5*cm])
    firma_r.setStyle(TableStyle([
        ("ALIGN", (0,0), (-1,-1), "RIGHT"),
        ("TOPPADDING", (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
    ]))

    firma_tbl = Table([[firma_l, Spacer(1,1), firma_r]], colWidths=[8*cm, 1.5*cm, 7.5*cm])
    firma_tbl.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LINEABOVE", (0,0), (-1,0), 0.5, GRIS_B),
        ("TOPPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(KeepTogether(firma_tbl))

    if estado == "Anulada" or anulada:
        doc.build(story, onFirstPage=_draw_anulada_watermark, onLaterPages=_draw_anulada_watermark)
    else:
        doc.build(story)
    return ruta_pdf
