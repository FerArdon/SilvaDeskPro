"""
utils/pdf_acta.py – Generador de Actas de Protocolo (Ministro de Fe)
SilvaDesk Pro · SEDCAF / FEMA Honduras
Formato notarial – valor jurídico pleno
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, Image as RLImage,
                                 KeepTogether)
from reportlab.platypus import PageBreak
import os
from datetime import date as Date

VERDE      = HexColor("#1A3A6B")
VERDE_M    = HexColor("#1F4E79")
VERDE_CLR  = HexColor("#DDEEFF")
GRIS_L     = HexColor("#F7F9F7")
GRIS_B     = HexColor("#CCCCCC")
GRIS_MED   = HexColor("#666666")
AMARILLO   = HexColor("#FFFDE7")
ROJO_TENUE = HexColor("#FFEBEE")
NEGRO      = black

def _logo_path():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for name in ("icon_blue.png", "logo.png"):
        p = os.path.join(base, "assets", name)
        if os.path.exists(p): return p
    return ""

def _seccion(titulo, story, st):
    """Agrega un separador de sección institucional."""
    tbl = Table([[Paragraph(f"  {titulo}", ParagraphStyle(
        "shtit", parent=st["Normal"],
        fontSize=9, fontName="Helvetica-Bold",
        textColor=white, leading=13
    ))]], colWidths=[17.4*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), VERDE_M),
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
    ]))
    story.append(Spacer(1, 6))
    story.append(tbl)
    story.append(Spacer(1, 4))

def _campo(label, valor, st, justify=False):
    """Par etiqueta-valor en bloque de texto."""
    aln = TA_JUSTIFY if justify else TA_LEFT
    s_lbl = ParagraphStyle("lbl",parent=st["Normal"],fontSize=8.5,
                           fontName="Helvetica-Bold",textColor=VERDE_M,leading=12)
    s_val = ParagraphStyle("val",parent=st["Normal"],fontSize=9.5,
                           leading=14,textColor=HexColor("#111111"),alignment=aln)
    parts = [Paragraph(label, s_lbl)]
    if valor and valor.strip():
        parts.append(Paragraph(valor, s_val))
    else:
        parts.append(Paragraph("(No especificado)", ParagraphStyle(
            "ns",parent=st["Normal"],fontSize=9,textColor=GRIS_MED,
            fontName="Helvetica-Oblique",leading=12)))
    return parts

def generar_acta(ruta_pdf: str, datos: dict) -> str:
    os.makedirs(os.path.dirname(ruta_pdf) if os.path.dirname(ruta_pdf) else ".", exist_ok=True)

    doc = SimpleDocTemplate(ruta_pdf, pagesize=letter,
        leftMargin=2.0*cm, rightMargin=2.0*cm,
        topMargin=1.8*cm, bottomMargin=2.5*cm,
        title=f"Acta No. {datos.get('num_acta','')}",
        author="SilvaDesk Pro – FEMA Honduras")

    st   = getSampleStyleSheet()
    story= []
    W    = 17.0*cm

    perito   = datos.get("perito_nombre","Ing. FERNANDO RAFAEL ARDON RODRIGUEZ")
    perito_reg = datos.get("perito_registro","COLPROFORH N.- 0226")
    seccion  = datos.get("seccion","Sección Técnica Ambiental – Fiscalía Especial de Medio Ambiente")
    num_acta = datos.get("num_acta","")
    folio    = datos.get("folio","")
    fecha    = datos.get("fecha","")
    hora     = datos.get("hora","")
    lugar    = datos.get("lugar","")
    mun      = datos.get("municipio","")
    dept     = datos.get("departamento","")
    exp_fema = datos.get("num_expediente_fema","")
    tipo_dil = datos.get("tipo_diligencia","")
    compar   = datos.get("comparecientes","")
    hechos   = datos.get("hechos","")
    hallazgos= datos.get("hallazgos","")
    fund_leg = datos.get("fundamento_legal","")
    disposic = datos.get("disposicion","")
    estado   = datos.get("estado","")
    obs      = datos.get("observaciones","")

    # ── Construir cadena de localización ──────────────────────────────────────
    loc_parts = [p for p in [lugar, mun, dept] if p and p.strip()]
    loc_str   = ", ".join(loc_parts) if loc_parts else "lugar consignado en expediente"

    # ═══════════════════════════════════════════════════════════════════════════
    # 1. MEMBRETE / CABECERA
    # ═══════════════════════════════════════════════════════════════════════════
    logo_img = None
    logo_p   = _logo_path()
    if os.path.exists(logo_p):
        logo_img = RLImage(logo_p, width=2.0*cm, height=2.0*cm)

    logo_cell = logo_img if logo_img else Paragraph("🌿", ParagraphStyle(
        "em2",parent=st["Normal"],fontSize=24,textColor=white,alignment=TA_CENTER))

    s_wl  = ParagraphStyle("wl2",parent=st["Normal"],fontSize=8.5,leading=12,textColor=white)
    s_wlb = ParagraphStyle("wlb",parent=st["Normal"],fontSize=10,leading=14,
                           fontName="Helvetica-Bold",textColor=white)
    s_wac = ParagraphStyle("wac",parent=st["Normal"],fontSize=18,leading=22,
                           fontName="Helvetica-Bold",textColor=white,alignment=TA_RIGHT)
    s_wn  = ParagraphStyle("wn",parent=st["Normal"],fontSize=9,leading=12,
                           textColor=HexColor("#A8C8E8"),alignment=TA_RIGHT)

    hdr = Table([[
        logo_cell,
        [
            Paragraph("SILVADESK PRO", s_wlb),
            Paragraph(seccion.upper(), s_wl),
            Paragraph("Sistema de Control y Gestión Forestal", ParagraphStyle("wls",parent=st["Normal"],fontSize=8,
                               leading=11,textColor=HexColor("#A8C8E8"))),
        ],
        [
            Paragraph(tipo_dil.upper() if tipo_dil else "ACTA", s_wac),
            Paragraph(f"Acta No.  <b>{num_acta}</b>", s_wn),
            Paragraph(f"Folio:  {folio}  ·  Estado: {estado}", s_wn),
        ],
    ]], colWidths=[2.2*cm, 9.8*cm, 5*cm])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), VERDE),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0),(-1,-1), 12),
        ("BOTTOMPADDING", (0,0),(-1,-1), 12),
        ("LEFTPADDING",   (0,0),(0,0),   10),
        ("LEFTPADDING",   (1,0),(1,0),   8),
        ("RIGHTPADDING",  (2,0),(2,0),   10),
        ("LINEBELOW",     (0,0),(-1,-1), 3, VERDE_M),
    ]))
    story.append(hdr)
    story.append(Spacer(1, 10))

    # ═══════════════════════════════════════════════════════════════════════════
    # 2. TEXTO NARRATIVO DE APERTURA (fórmula notarial)
    # ═══════════════════════════════════════════════════════════════════════════
    apertura = (
        f"En <b>{loc_str}</b>, siendo las <b>{hora}</b> horas del día <b>{fecha}</b>, "
        f"el suscrito <b>{perito}</b>, en su calidad de perito forestal adscrito a la "
        f"<b>{seccion}</b>, del Ministerio Público de Honduras, procedió a realizar "
        f"la siguiente diligencia de naturaleza técnica, de conformidad con las "
        f"facultades conferidas por la legislación aplicable, dejando constancia de "
        f"lo siguiente:"
    )
    story.append(Paragraph(apertura, ParagraphStyle(
        "apertura", parent=st["Normal"],
        fontSize=10, leading=16, alignment=TA_JUSTIFY,
        textColor=HexColor("#111111"),
        borderColor=VERDE_M, borderWidth=1,
        borderPadding=(8,8,8,8),
        backColor=VERDE_CLR,
    )))
    story.append(Spacer(1, 10))

    # ═══════════════════════════════════════════════════════════════════════════
    # 3. DATOS DE IDENTIFICACIÓN
    # ═══════════════════════════════════════════════════════════════════════════
    _seccion("I.  IDENTIFICACIÓN DE LA DILIGENCIA", story, st)

    id_data = [
        ["Acta No.:", num_acta,    "Folio:",      str(folio)],
        ["Tipo:",     tipo_dil,    "Fecha:",      fecha],
        ["Hora:",     hora,        "Estado:",     estado],
        ["Lugar:",    lugar,       "Municipio:",  mun],
        ["Dpto.:",    dept,        "Exp. FEMA:",  exp_fema],
    ]
    s_lbl2 = ParagraphStyle("lbl2",parent=st["Normal"],fontSize=8.5,
                            fontName="Helvetica-Bold",textColor=VERDE_M)
    s_val2 = ParagraphStyle("val2",parent=st["Normal"],fontSize=9,textColor=NEGRO)

    id_rows = []
    for row in id_data:
        id_rows.append([
            Paragraph(row[0], s_lbl2), Paragraph(row[1] or "—", s_val2),
            Paragraph(row[2], s_lbl2), Paragraph(row[3] or "—", s_val2),
        ])
    id_tbl = Table(id_rows, colWidths=[2.5*cm, 6*cm, 2.5*cm, 6*cm])
    id_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), GRIS_L),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [GRIS_L, white]),
        ("BOX",           (0,0),(-1,-1), 0.5, GRIS_B),
        ("INNERGRID",     (0,0),(-1,-1), 0.25, GRIS_B),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 8),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    story.append(id_tbl)

    # ═══════════════════════════════════════════════════════════════════════════
    # 4. COMPARECIENTES
    # ═══════════════════════════════════════════════════════════════════════════
    _seccion("II.  COMPARECIENTES Y PERSONAS PRESENTES", story, st)
    for p in _campo("Personas que comparecen o están presentes en la diligencia:", compar, st, justify=False):
        story.append(p)
        story.append(Spacer(1,2))

    # ═══════════════════════════════════════════════════════════════════════════
    # 5. HECHOS CONSTATADOS
    # ═══════════════════════════════════════════════════════════════════════════
    _seccion("III.  HECHOS CONSTATADOS", story, st)
    for p in _campo("El suscrito perito constató los siguientes hechos:", hechos, st, justify=True):
        story.append(p)
        story.append(Spacer(1,2))

    # ═══════════════════════════════════════════════════════════════════════════
    # 6. HALLAZGOS TÉCNICOS
    # ═══════════════════════════════════════════════════════════════════════════
    _seccion("IV.  HALLAZGOS TÉCNICOS", story, st)
    for p in _campo("Del análisis técnico forestal se desprenden los siguientes hallazgos:", hallazgos, st, justify=True):
        story.append(p)
        story.append(Spacer(1,2))

    # ═══════════════════════════════════════════════════════════════════════════
    # 7. FUNDAMENTO LEGAL
    # ═══════════════════════════════════════════════════════════════════════════
    _seccion("V.  FUNDAMENTO LEGAL", story, st)
    for p in _campo("La presente diligencia se fundamenta en:", fund_leg, st, justify=False):
        story.append(p)
        story.append(Spacer(1,2))

    # ═══════════════════════════════════════════════════════════════════════════
    # 8. DISPOSICIÓN / RECOMENDACIÓN
    # ═══════════════════════════════════════════════════════════════════════════
    _seccion("VI.  DISPOSICIÓN Y RECOMENDACIÓN TÉCNICA", story, st)
    for p in _campo("Con base en los hechos y hallazgos, se dispone o recomienda:", disposic, st, justify=True):
        story.append(p)
        story.append(Spacer(1,2))

    # ═══════════════════════════════════════════════════════════════════════════
    # 9. OBSERVACIONES (opcional)
    # ═══════════════════════════════════════════════════════════════════════════
    if obs and obs.strip():
        _seccion("VII.  OBSERVACIONES ADICIONALES", story, st)
        for p in _campo("", obs, st, justify=True):
            story.append(p)
            story.append(Spacer(1,2))

    # ═══════════════════════════════════════════════════════════════════════════
    # 10. CIERRE NOTARIAL
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 14))
    cierre_txt = (
        "No habiendo más que hacer constar, se da por concluida la presente diligencia en el "
        f"lugar y fecha indicados, siendo las <b>{hora}</b> horas, y se levanta la presente acta "
        f"que se incorpora al <b>Folio {folio}</b> del Protocolo de Actuaciones Técnicas "
        "de la Sección Técnica Ambiental de la Fiscalía Especial de Medio Ambiente, para los "
        "fines legales que correspondan."
    )
    cierre_tbl = Table([[Paragraph(cierre_txt, ParagraphStyle(
        "cierre", parent=st["Normal"],
        fontSize=9.5, leading=15, alignment=TA_JUSTIFY,
        textColor=HexColor("#111111"),
    ))]], colWidths=[W])
    cierre_tbl.setStyle(TableStyle([
        ("BOX",           (0,0),(-1,-1), 0.5, VERDE_M),
        ("BACKGROUND",    (0,0),(-1,-1), GRIS_L),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ("LEFTPADDING",   (0,0),(-1,-1), 12),
        ("RIGHTPADDING",  (0,0),(-1,-1), 12),
    ]))
    story.append(cierre_tbl)
    story.append(Spacer(1, 24))

    # ═══════════════════════════════════════════════════════════════════════════
    # 11. BLOQUE DE FIRMA
    # ═══════════════════════════════════════════════════════════════════════════
    firma_l = Table([
        [HRFlowable(width=6.5*cm, thickness=1.2, color=VERDE)],
        [Paragraph(f"<b>{perito}</b>", ParagraphStyle(
            "fnom",parent=st["Normal"],fontSize=9.5,fontName="Helvetica-Bold",
            alignment=TA_CENTER))],
        [Paragraph(f"Perito Forestal · {perito_reg}" if perito_reg else "Perito Forestal · Ministro de Fe", ParagraphStyle(
            "fcarg",parent=st["Normal"],fontSize=8.5,textColor=VERDE_M,
            alignment=TA_CENTER))],
        [Paragraph(seccion, ParagraphStyle(
            "fsec",parent=st["Normal"],fontSize=8,textColor=GRIS_MED,
            alignment=TA_CENTER))],
        [Paragraph("SilvaDesk Pro — Gestión Forestal", ParagraphStyle(
            "fmp",parent=st["Normal"],fontSize=8,textColor=GRIS_MED,
            alignment=TA_CENTER))],
    ], colWidths=[8*cm])
    firma_l.setStyle(TableStyle([
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("TOPPADDING",(0,0),(-1,-1),3),
        ("BOTTOMPADDING",(0,0),(-1,-1),3),
    ]))

    firma_r = Table([
        [Paragraph(f"Acta No.: <b>{num_acta}</b>", ParagraphStyle(
            "fr1",parent=st["Normal"],fontSize=8.5,textColor=GRIS_MED))],
        [Paragraph(f"Folio: <b>{folio}</b>", ParagraphStyle(
            "fr2",parent=st["Normal"],fontSize=8.5,textColor=GRIS_MED))],
        [Paragraph(f"Fecha: <b>{fecha}</b>", ParagraphStyle(
            "fr3",parent=st["Normal"],fontSize=8.5,textColor=GRIS_MED))],
        [Paragraph(f"Lugar: {loc_str}", ParagraphStyle(
            "fr4",parent=st["Normal"],fontSize=8,textColor=GRIS_MED))],
        [Spacer(1,6)],
        [Paragraph("Generado con SilvaDesk Pro", ParagraphStyle(
            "fr5",parent=st["Normal"],fontSize=7,textColor=HexColor("#BBBBBB")))],
    ], colWidths=[7.5*cm])
    firma_r.setStyle(TableStyle([
        ("ALIGN",(0,0),(-1,-1),"RIGHT"),
        ("TOPPADDING",(0,0),(-1,-1),3),
        ("BOTTOMPADDING",(0,0),(-1,-1),3),
    ]))

    firma_tbl = Table([[firma_l, Spacer(1,1), firma_r]],
                      colWidths=[8*cm, 1.5*cm, 7.5*cm])
    firma_tbl.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LINEABOVE",(0,0),(-1,0),0.5,GRIS_B),
        ("TOPPADDING",(0,0),(-1,-1),8),
    ]))
    story.append(KeepTogether(firma_tbl))

    doc.build(story)
    return ruta_pdf
