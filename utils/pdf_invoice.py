"""
utils/pdf_invoice.py – Generador de Facturas PDF
SilvaDesk Pro · SEDCAF – Servicios de Consultoría y Asesoría Forestal
CAI conforme SAR Honduras (Acuerdo SAR-DS-007-2019)
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, HRFlowable, Image as RLImage)
from reportlab.lib import colors
from datetime import date as Date
import os

# ── Paleta corporativa ────────────────────────────────────────────────────────
AZUL       = HexColor("#1A3A6B")   # azul oscuro SEDCAF
AZUL_M     = HexColor("#1F4E79")   # azul medio
AZUL_CLR   = HexColor("#DDEEFF")   # azul muy claro
GRIS_L     = HexColor("#F5F7FA")   # fondo tabla
GRIS_B     = HexColor("#CCCCCC")   # borde
GRIS_MED   = HexColor("#777777")   # texto secundario
AMARILLO   = HexColor("#FFFDE7")   # fondo CAI
NARANJA    = HexColor("#BF360C")   # acento CAI/advertencia
NEGRO      = black

def _fmt(n):
    try:    return f"L. {float(n):,.2f}"
    except: return str(n)

def _logo_path():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Preferir el árbol azul; si no existe, caer al logo circular
    for name in ("icon_blue.png", "logo.png"):
        p = os.path.join(base, "assets", name)
        if os.path.exists(p):
            return p
    return ""

def _draw_anulada_watermark(canvas, doc):
    """Dibuja 'ANULADA' diagonal en rojo semitransparente sobre la página."""
    canvas.saveState()
    page_w, page_h = letter
    canvas.translate(page_w / 2, page_h / 2)
    canvas.rotate(45)
    # Texto principal grande
    canvas.setFont("Helvetica-Bold", 96)
    canvas.setFillColorRGB(0.78, 0.08, 0.08, alpha=0.13)   # rojo muy transparente
    canvas.drawCentredString(0, 20, "ANULADA")
    # Borde del texto (stroke) para mejor visibilidad
    canvas.setStrokeColorRGB(0.78, 0.08, 0.08, alpha=0.18)
    canvas.setLineWidth(0.6)
    canvas.drawCentredString(0, 20, "ANULADA")
    # Línea decorativa superior e inferior
    canvas.setStrokeColorRGB(0.78, 0.08, 0.08, alpha=0.22)
    canvas.setLineWidth(2)
    canvas.line(-220, 80, 220, 80)
    canvas.line(-220, -40, 220, -40)
    canvas.restoreState()

def generar_factura(ruta_pdf: str, datos: dict, anulada: bool = False) -> str:
    os.makedirs(os.path.dirname(ruta_pdf) if os.path.dirname(ruta_pdf) else ".", exist_ok=True)

    doc = SimpleDocTemplate(ruta_pdf, pagesize=letter,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=1.5*cm, bottomMargin=2.5*cm,
        title=f"Factura {datos.get('num_factura','')}",
        author="SilvaDesk Pro – SEDCAF")

    st = getSampleStyleSheet()
    def s(name, **kw):
        return ParagraphStyle(name, parent=st["Normal"], **kw)

    # ── Estilos ───────────────────────────────────────────────────────────────
    s_n    = s("n",   fontSize=9,  leading=13)
    s_sm   = s("sm",  fontSize=7.5,leading=11, textColor=GRIS_MED)
    s_b    = s("b",   fontSize=9,  leading=13, fontName="Helvetica-Bold")
    s_c    = s("c",   fontSize=9,  leading=13, alignment=TA_CENTER)
    s_r    = s("r",   fontSize=9,  leading=13, alignment=TA_RIGHT)
    s_wc   = s("wc",  fontSize=10, leading=14, fontName="Helvetica-Bold",
                textColor=white, alignment=TA_CENTER)
    s_wl   = s("wl",  fontSize=9,  leading=13, textColor=white)
    s_wr   = s("wr",  fontSize=8,  leading=12, textColor=HexColor("#A8C8E8"), alignment=TA_RIGHT)
    s_cai  = s("cai", fontSize=7.5,leading=11, fontName="Helvetica-Bold",
                textColor=NARANJA, alignment=TA_CENTER)
    s_cai_v= s("caiv",fontSize=9,  leading=12, fontName="Courier-Bold",
                textColor=NEGRO, alignment=TA_CENTER)
    s_h2   = s("h2",  fontSize=9,  leading=12, fontName="Helvetica-Bold", textColor=AZUL)
    s_tot  = s("tot", fontSize=11, leading=14, fontName="Helvetica-Bold",
                textColor=AZUL, alignment=TA_RIGHT)

    story = []
    W = 17.4 * cm   # ancho útil

    # ══════════════════════════════════════════════════════════════════════════
    # 1. CABECERA
    # ══════════════════════════════════════════════════════════════════════════
    logo_p = _logo_path()
    logo_cell = RLImage(logo_p, width=1.8*cm, height=1.8*cm) if logo_p else Spacer(1.8*cm, 1.8*cm)

    emisor  = datos.get("emisor_nombre", "SEDCAF")
    e_rtn   = datos.get("emisor_rtn",   "")
    e_dir   = datos.get("emisor_dir",   "Honduras")
    e_tel   = datos.get("emisor_tel",   "")
    e_email = datos.get("emisor_email", "")
    num_fac = datos.get("num_factura",  "")
    fecha   = datos.get("fecha_emision", Date.today().strftime("%d/%m/%Y"))

    info_lines = [
        Paragraph("<b><font size='13' color='#1A3A6B'>SilvaDesk Pro</font></b>", s_wl),
        Paragraph(f"<b>{emisor}</b>", s("en", fontSize=10, leading=13, textColor=white, fontName="Helvetica-Bold")),
    ]
    if e_rtn:   info_lines.append(Paragraph(f"RTN: {e_rtn}", s_wl))
    if e_dir:   info_lines.append(Paragraph(e_dir, s_wl))
    if e_tel:   info_lines.append(Paragraph(f"Tel.: {e_tel}", s_wl))
    if e_email: info_lines.append(Paragraph(e_email, s_wl))

    hdr_data = [[
        logo_cell,
        info_lines,
        [
            Paragraph("FACTURA", s("ft", fontSize=22, fontName="Helvetica-Bold",
                                   textColor=white, alignment=TA_RIGHT, spaceAfter=4)),
            Paragraph(f"No. <b>{num_fac}</b>",
                      s("fn", fontSize=11, textColor=HexColor("#A8C8E8"), alignment=TA_RIGHT, spaceAfter=2)),
            Paragraph(f"Fecha: {fecha}",
                      s("fd", fontSize=9,  textColor=HexColor("#7EB8E0"), alignment=TA_RIGHT)),
        ],
    ]]
    hdr_tbl = Table(hdr_data, colWidths=[2.2*cm, 9.8*cm, 5.4*cm])
    hdr_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), AZUL),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING",   (0,0), (0,0),   10),
        ("LEFTPADDING",   (1,0), (1,0),   8),
        ("RIGHTPADDING",  (2,0), (2,0),   12),
        ("LINEBELOW",     (0,0), (-1,-1),  2, AZUL_M),
    ]))
    story.append(hdr_tbl)
    story.append(Spacer(1, 8))

    # ══════════════════════════════════════════════════════════════════════════
    # 2. BLOQUE CAI  (SAR Honduras – obligatorio)
    # ══════════════════════════════════════════════════════════════════════════
    cai       = datos.get("cai",          "—")
    fecha_lim = datos.get("fecha_limite", "—")
    rng_ini   = datos.get("rango_inicio", "—")
    rng_fin   = datos.get("rango_fin",    "—")

    # Fila de etiquetas
    cai_lbl_row = [
        Paragraph("<b>CAI:</b>",                          s_cai),
        Paragraph("<b>Fecha límite de emisión:</b>",      s_cai),
        Paragraph("<b>Rango autorizado inicio:</b>",      s_cai),
        Paragraph("<b>Rango autorizado fin:</b>",         s_cai),
    ]
    # Fila de valores — se usa str() con fallback para evitar Paragraph(None)
    cai_val_row = [
        Paragraph(str(cai      or "Sin CAI registrado"),     s_cai_v),
        Paragraph(str(fecha_lim or "Sin fecha registrada"),   s_cai_v),
        Paragraph(str(rng_ini  or "Sin rango registrado"),    s_cai_v),
        Paragraph(str(rng_fin  or "Sin rango registrado"),    s_cai_v),
    ]
    cai_inner = Table([cai_lbl_row, cai_val_row],
                      colWidths=[5.0*cm, 3.5*cm, 4.45*cm, 4.45*cm])
    cai_inner.setStyle(TableStyle([
        ("ALIGN",        (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING",   (0,0), (-1,-1), 3),
        ("BOTTOMPADDING",(0,0), (-1,-1), 3),
    ]))

    cai_wrap = Table([
        [Paragraph("⚠  CÓDIGO DE AUTORIZACIÓN DE IMPRESIÓN (CAI) – SAR HONDURAS", s_cai)],
        [cai_inner],
    ], colWidths=[W])
    cai_wrap.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), AMARILLO),
        ("BOX",           (0,0), (-1,-1), 1.5, NARANJA),
        ("LINEBELOW",     (0,0), (0,0),   0.5, HexColor("#FFCCBC")),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
    ]))
    story.append(cai_wrap)
    story.append(Spacer(1, 8))

    # ══════════════════════════════════════════════════════════════════════════
    # 3. EMISOR / CLIENTE
    # ══════════════════════════════════════════════════════════════════════════
    c_nom = datos.get("cliente_nombre", "")
    c_rtn = datos.get("cliente_rtn",   "")
    c_dir = datos.get("cliente_dir",   "")

    def info_block(titulo, lineas):
        rows = [[Paragraph(titulo, s_h2)]]
        for l in lineas:
            if l:
                st_use = s_b if l.startswith("<b>") else s_n
                rows.append([Paragraph(l, st_use)])
        t = Table(rows, colWidths=[8.4*cm])
        t.setStyle(TableStyle([
            ("TOPPADDING",    (0,0), (-1,-1), 1),
            ("BOTTOMPADDING", (0,0), (-1,-1), 1),
            ("LEFTPADDING",   (0,0), (-1,-1), 0),
        ]))
        return t

    emi_blk = info_block("EMISOR", [
        f"<b>{emisor}</b>",
        "SEDCAF – Servicios de Consultoría y Asesoría Forestal",
        f"RTN: {e_rtn}" if e_rtn else "",
        f"Dirección: {e_dir}" if e_dir else "",
        f"Tel.: {e_tel}" if e_tel else "",
    ])
    cli_blk = info_block("CLIENTE / OBLIGADO TRIBUTARIO", [
        f"<b>{c_nom}</b>" if c_nom else "(—)",
        f"RTN: {c_rtn}" if c_rtn else "RTN: —",
        f"Dirección: {c_dir}" if c_dir else "",
    ])

    info_tbl = Table([[emi_blk, cli_blk]], colWidths=[8.7*cm, 8.7*cm])
    info_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), GRIS_L),
        ("BOX",           (0,0), (-1,-1), 0.5,  GRIS_B),
        ("LINEAFTER",     (0,0), (0,-1),  0.5,  GRIS_B),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
    ]))
    story.append(info_tbl)
    story.append(Spacer(1, 10))

    # ══════════════════════════════════════════════════════════════════════════
    # 4. DETALLE DE SERVICIOS
    # ══════════════════════════════════════════════════════════════════════════
    def mk_hdr(txt):
        return Paragraph(f"<b>{txt}</b>", s_wc)

    svc_header = [
        mk_hdr("No."),
        mk_hdr("Descripción del Servicio Profesional"),
        mk_hdr("Cant."),
        mk_hdr("Unidad / Tarifa"),
        mk_hdr("P. Unit. (L.)"),
        mk_hdr("Total (L.)"),
    ]
    rows = [svc_header]
    servicios = datos.get("servicios", [])
    for i, svc in enumerate(servicios, 1):
        # Compatibilidad: formato antiguo era lista [desc, cant, unidad, precio]
        if isinstance(svc, (list, tuple)):
            desc   = str(svc[0]) if len(svc) > 0 else ""
            cant   = float(svc[1]) if len(svc) > 1 else 1.0
            unidad = str(svc[2]) if len(svc) > 2 else "Servicio"
            precio = float(svc[3]) if len(svc) > 3 else 0.0
            total_ = cant * precio
        else:
            desc   = str(svc.get("descripcion", ""))
            cant   = float(svc.get("cantidad", 1))
            unidad = str(svc.get("unidad", "Servicio"))
            precio = float(svc.get("precio_unit", 0))
            total_ = float(svc.get("total", cant * precio))
        rows.append([
            Paragraph(str(i), s_c),
            Paragraph(desc, s_n),
            Paragraph(f"{cant:.2f}", s_c),
            Paragraph(unidad, s_c),
            Paragraph(_fmt(precio), s_r),
            Paragraph(_fmt(total_), s_r),
        ])

    # Ancho total = 17.4 cm
    svc_tbl = Table(rows, colWidths=[0.9*cm, 8.1*cm, 1.4*cm, 2.5*cm, 2.3*cm, 2.2*cm])
    svc_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0),  AZUL),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [white, GRIS_L]),
        ("GRID",          (0,0), (-1,-1), 0.35, GRIS_B),
        ("LINEBELOW",     (0,0), (-1,0),  1.5,  AZUL_M),
        ("ALIGN",         (0,0), (0,-1),  "CENTER"),
        ("ALIGN",         (2,0), (2,-1),  "CENTER"),
        ("ALIGN",         (3,0), (3,-1),  "CENTER"),
        ("ALIGN",         (4,1), (5,-1),  "RIGHT"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 4),
        ("RIGHTPADDING",  (0,0), (-1,-1), 4),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
    ]))
    story.append(svc_tbl)
    story.append(Spacer(1, 10))

    # ══════════════════════════════════════════════════════════════════════════
    # 5. TOTALES
    # ══════════════════════════════════════════════════════════════════════════
    sub  = datos.get("subtotal", 0)
    isv  = datos.get("isv",      0)
    tot  = datos.get("total",    0)
    isr  = datos.get("isr",      0)
    neto = datos.get("neto",     0)

    def tot_row(label, valor, bold=False, color=None, bg=None, size=9):
        tc = color or NEGRO
        fn = "Helvetica-Bold" if bold else "Helvetica"
        lp = Paragraph(label, s(f"tl{size}{bold}", fontSize=size, fontName=fn,
                                 textColor=tc, alignment=TA_RIGHT))
        vp = Paragraph(valor, s(f"tv{size}{bold}", fontSize=size, fontName=fn,
                                 textColor=tc, alignment=TA_RIGHT))
        return [Paragraph("", s_n), lp, vp], bg

    tot_rows, bgs = [], []
    for row, bg in [
        tot_row("Subtotal (Honorario base):",              _fmt(sub)),
        tot_row("+ ISV 15% (cobrar al cliente):",          _fmt(isv)),
        tot_row("TOTAL A FACTURAR:", _fmt(tot), bold=True, color=AZUL, bg=AZUL_CLR, size=11),
        tot_row("– ISR 12.5% (cliente retiene – no en factura):", _fmt(isr), color=GRIS_MED),
        tot_row("Neto estimado a recibir:",                _fmt(neto), color=GRIS_MED),
    ]:
        tot_rows.append(row); bgs.append(bg)

    tot_tbl = Table(tot_rows, colWidths=[8.1*cm, 6.5*cm, 2.8*cm])
    ts2 = [
        ("TOPPADDING",    (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ("RIGHTPADDING",  (2,0), (2,-1),  6),
        ("LINEABOVE",     (1,0), (2,0),   0.5, GRIS_B),
        ("LINEABOVE",     (1,2), (2,2),   1.5, AZUL),
        ("LINEBELOW",     (1,2), (2,2),   1.5, AZUL),
    ]
    for i, bg in enumerate(bgs):
        if bg:
            ts2.append(("BACKGROUND", (0,i), (2,i), bg))
    tot_tbl.setStyle(TableStyle(ts2))
    story.append(tot_tbl)
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "* La retención ISR (12.5%, Art. 50 Ley ISR Honduras) es aplicada "
        "por el cliente al momento del pago y NO forma parte del valor de esta factura.",
        s("isr_nota", fontSize=7, textColor=GRIS_MED, leading=10)))
    story.append(Spacer(1, 14))

    # ══════════════════════════════════════════════════════════════════════════
    # 6. OBSERVACIONES
    # ══════════════════════════════════════════════════════════════════════════
    nota = datos.get("nota", "").strip()
    if nota:
        obs_tbl = Table([[Paragraph(f"<b>Observaciones:</b> {nota}", s_n)]], colWidths=[W])
        obs_tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), GRIS_L),
            ("BOX",           (0,0), (-1,-1), 0.5, GRIS_B),
            ("TOPPADDING",    (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ]))
        story.append(obs_tbl)
        story.append(Spacer(1, 14))

    # ══════════════════════════════════════════════════════════════════════════
    # 7. FIRMA Y PIE DE PÁGINA
    # ══════════════════════════════════════════════════════════════════════════
    firma_inner = Table([
        [HRFlowable(width=7*cm, thickness=1, color=AZUL)],
        [Paragraph(f"<b>{emisor}</b>",
                   s("fn2", fontSize=9, fontName="Helvetica-Bold", alignment=TA_CENTER))],
        [Paragraph("SEDCAF<br/>Servicios de Consultoría y Asesoría Forestal<br/>Honduras",
                   s("fs2", fontSize=8, alignment=TA_CENTER, textColor=GRIS_MED, leading=12))],
    ], colWidths=[8*cm])
    firma_inner.setStyle(TableStyle([
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("TOPPADDING",    (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))

    pie_inner = Table([
        [Paragraph(f"Factura No.: <b>{num_fac}</b>",    s_sm)],
        [Paragraph(f"Fecha emisión: <b>{fecha}</b>",     s_sm)],
        [Paragraph(f"CAI: <font name='Courier'>{cai}</font>", s_sm)],
        [Paragraph("Documento autorizado – SAR Honduras", s_sm)],
        [Paragraph("Generado con SilvaDesk Pro · SEDCAF Honduras",
                   s("pie_g", fontSize=7, textColor=HexColor("#BBBBBB")))],
    ], colWidths=[7.4*cm])
    pie_inner.setStyle(TableStyle([
        ("ALIGN",         (0,0), (-1,-1), "RIGHT"),
        ("TOPPADDING",    (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
    ]))

    firma_tbl = Table([[firma_inner, Spacer(1,1), pie_inner]],
                      colWidths=[8*cm, 1.4*cm, 8*cm])
    firma_tbl.setStyle(TableStyle([
        ("VALIGN",    (0,0), (-1,-1), "BOTTOM"),
        ("LINEABOVE", (0,0), (-1,0),  0.5, GRIS_B),
        ("TOPPADDING",(0,0), (-1,-1), 8),
    ]))
    story.append(firma_tbl)

    # ── Nota legal al pie ─────────────────────────────────────────────────────
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GRIS_B))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "ISV 15% declarado mensualmente ante SAR Honduras (DMR/ISV).  "
        "ISR 12.5%: el cliente retiene y entera al SAR según Art. 50 Ley ISR (no aparece como cargo en factura).  "
        "Arancel de Honorarios: COLPROFORH · La Gaceta No. 36,609 (10/08/2024).  "
        "Documento generado por SilvaDesk Pro · SEDCAF · Honduras.",
        s("legal", fontSize=6.5, textColor=GRIS_MED, leading=9.5, alignment=TA_CENTER)))

    if anulada:
        doc.build(story,
                  onFirstPage=_draw_anulada_watermark,
                  onLaterPages=_draw_anulada_watermark)
    else:
        doc.build(story)
    return ruta_pdf
