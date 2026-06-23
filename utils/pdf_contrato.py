"""
utils/pdf_contrato.py – Generador de Contrato PDF (Minuta Legal Arancel COLPROFORH)
SilvaDesk Pro · SEDCAF / ICF Honduras
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
import os

# Paleta formal institucional
COLOR_OSC = HexColor("#1B5E20")   # Verde TFC
COLOR_MED = HexColor("#2E7D32")
GRIS_TXT = HexColor("#333333")
NEGRO = HexColor("#000000")

def _logo_path():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for name in ("icon_blue.png", "logo.png"):
        p = os.path.join(base, "assets", name)
        if os.path.exists(p): return p
    return ""

def generar_pdf_contrato(ruta_pdf: str, datos: dict) -> str:
    os.makedirs(os.path.dirname(ruta_pdf) if os.path.dirname(ruta_pdf) else ".", exist_ok=True)
    
    doc = SimpleDocTemplate(ruta_pdf, pagesize=letter,
        leftMargin=2.5*cm, rightMargin=2.5*cm,
        topMargin=2.0*cm, bottomMargin=2.2*cm,
        title=f"Contrato de Servicios Forestales - {datos.get('cliente_nombre','')}",
        author="SilvaDesk Pro – COLPROFORH")

    st = getSampleStyleSheet()
    story = []
    
    # Extraer variables
    c_nom = datos.get("consultor_nombre", "Ing. Fernando Rafael Ardon Rodriguez")
    c_reg = datos.get("consultor_registro", "COLPROFORH N.- 0226")
    e_nom = datos.get("empresa_nombre", "SEDCAF")
    cl_nom = datos.get("cliente_nombre", "")
    cl_rtn = datos.get("cliente_rtn", "")
    predio = datos.get("predio", "")
    municipio = datos.get("municipio", "")
    depto = datos.get("departamento", "")
    actividad = datos.get("actividad_tipo", "")
    monto = datos.get("monto_total", 0.0)
    forma_pago = datos.get("forma_pago", "")
    plazo = datos.get("plazo_ejecucion", "")
    fecha_firma = datos.get("fecha_firma", "")
    clausulas_adicionales = datos.get("clausulas_adicionales", "")

    # Convertir monto a letras (español sencillo) y formatear número
    monto_num_str = f"L. {monto:,.2f}"
    
    # Título del Documento
    s_title = ParagraphStyle("c_title", parent=st["Normal"], fontSize=12, leading=16, fontName="Helvetica-Bold", alignment=TA_CENTER, textColor=NEGRO)
    s_subtitle = ParagraphStyle("c_subtitle", parent=st["Normal"], fontSize=10, leading=14, fontName="Helvetica-Bold", alignment=TA_CENTER, textColor=COLOR_MED)
    
    story.append(Paragraph("CONTRATO PRIVADO DE PRESTACIÓN DE SERVICIOS PROFESIONALES FORESTALES", s_title))
    story.append(Spacer(1, 4))
    story.append(Paragraph("CONFORME AL ARANCEL DE PROFESIONALES DE LAS CIENCIAS FORESTALES DE HONDURAS", s_subtitle))
    story.append(Spacer(1, 15))
    
    # Estilos del cuerpo
    s_body = ParagraphStyle("c_body", parent=st["Normal"], fontSize=10, leading=15, textColor=GRIS_TXT, alignment=TA_JUSTIFY)
    s_clause = ParagraphStyle("c_clause", parent=st["Normal"], fontSize=10, leading=14, fontName="Helvetica-Bold", textColor=NEGRO, spaceBefore=8, spaceAfter=4)

    # 1. Comparecientes
    intro_text = (
        f"Nosotros, por una parte, <b>{c_nom}</b>, Ingeniero Forestal de nacionalidad hondureña, "
        f"miembro activo del Colegio de Profesionales Forestales de Honduras (COLPROFORH) con registro "
        f"número <b>{c_reg}</b>, en adelante denominado el <b>CONSULTOR</b>; y por otra parte, "
        f"<b>{cl_nom}</b>, mayor de edad, con Registro Tributario Nacional (RTN) número <b>{cl_rtn if cl_rtn else 'N/A'}</b>, "
        f"actuando en su condición de propietario o representante legal de la propiedad, en adelante denominado "
        f"el <b>PROPIETARIO</b>; convenimos de mutuo acuerdo celebrar el presente Contrato de Prestación de "
        f"Servicios Profesionales Forestales, el cual se regirá por las cláusulas siguientes:"
    )
    story.append(Paragraph(intro_text, s_body))
    story.append(Spacer(1, 10))

    # 2. Cláusulas
    # Primera: Objeto
    story.append(Paragraph("CLÁUSULA PRIMERA: OBJETO DEL CONTRATO", s_clause))
    cl1_txt = (
        f"El <b>CONSULTOR</b> se compromete a realizar para el <b>PROPIETARIO</b> la asistencia técnica y ejecución "
        f"del servicio forestal de: <b>{actividad}</b>. Dicha labor técnica se desarrollará en el predio "
        f"denominado <b>\"{predio}\"</b>, ubicado en el municipio de <b>{municipio if municipio else '______'}</b>, "
        f"departamento de <b>{depto if depto else '______'}</b>, República de Honduras."
    )
    story.append(Paragraph(cl1_txt, s_body))
    
    # Segunda: Obligaciones del Consultor
    story.append(Paragraph("CLÁUSULA SEGUNDA: OBLIGACIONES DEL CONSULTOR", s_clause))
    cl2_txt = (
        "El <b>CONSULTOR</b> se obliga formalmente a: a) Ejecutar los servicios contratados con estricto apego "
        "a las normativas vigentes del Instituto de Conservación Forestal (ICF) y la Ley Forestal, Áreas Protegidas y "
        "Vida Silvestre de Honduras (Decreto No. 98-2007). b) Elaborar los dictámenes, informes o planes correspondientes "
        "siguiendo las directrices éticas y técnicas de COLPROFORH. c) Entregar la documentación final en los plazos "
        "convenidos."
    )
    story.append(Paragraph(cl2_txt, s_body))
    
    # Tercera: Obligaciones del Propietario
    story.append(Paragraph("CLÁUSULA TERCERA: OBLIGACIONES DEL PROPIETARIO", s_clause))
    cl3_txt = (
        "El <b>PROPIETARIO</b> se obliga a: a) Proporcionar de manera oportuna toda la documentación legal de la propiedad "
        "necesaria (título de propiedad, escrituras públicas, planos de colindancias). b) Brindar las facilidades de acceso "
        "al predio para el levantamiento de datos de campo y cubicaciones. c) Cancelar los honorarios pactados en la forma "
        "y plazos establecidos en el presente contrato."
    )
    story.append(Paragraph(cl3_txt, s_body))
    
    # Cuarta: Valor del Contrato e Impuestos
    story.append(Paragraph("CLÁUSULA CUARTA: VALOR DEL CONTRATO Y RETENCIONES", s_clause))
    cl4_txt = (
        f"Los honorarios profesionales totales acordados por la prestación del servicio forestal ascienden a la cantidad "
        f"neta de <b>{monto_num_str} Lempiras</b>. Este monto no incluye los gastos de tasas de inspección oficial "
        f"o cobros administrativos del ICF, los cuales correrán por cuenta del <b>PROPIETARIO</b>. "
        f"Ambas partes acuerdan que el <b>PROPIETARIO</b> efectuará la retención del Impuesto sobre la Renta (ISR) "
        f"conforme a la tasa del 12.5% de conformidad al Artículo 50 de la Ley del Impuesto sobre la Renta de Honduras, "
        f"entregando al <b>CONSULTOR</b> la respectiva constancia de retención en un plazo máximo de quince (15) días "
        f"posteriores al pago."
    )
    story.append(Paragraph(cl4_txt, s_body))

    # Quinta: Forma de Pago
    story.append(Paragraph("CLÁUSULA QUINTA: FORMA DE PAGO", s_clause))
    cl5_txt = (
        f"El pago por los servicios profesionales se realizará de la siguiente manera: <b>{forma_pago}</b>."
    )
    story.append(Paragraph(cl5_txt, s_body))

    # Sexta: Plazo de Ejecución
    story.append(Paragraph("CLÁUSULA SEXTA: PLAZO DE ENTREGA", s_clause))
    cl6_txt = (
        f"El plazo de ejecución de los servicios objeto de este contrato será de <b>{plazo}</b>, contados a partir "
        f"de la firma del presente instrumento y de la entrega completa de la información catastral e inicial por "
        f"parte del <b>PROPIETARIO</b>."
    )
    story.append(Paragraph(cl6_txt, s_body))

    # Séptima: Resolución de Conflictos
    story.append(Paragraph("CLÁUSULA SÉPTIMA: CONCILIACIÓN Y ARBITRAJE", s_clause))
    cl7_txt = (
        "Cualquier diferencia o conflicto derivado de la interpretación, ejecución o rescisión de este contrato "
        "se someterá en primera instancia al procedimiento de conciliación amigable ante la junta directiva o tribunal "
        "de honor de COLPROFORH. En caso de persistir el conflicto, se someterán a la jurisdicción de los tribunales de "
        "la República de Honduras."
    )
    story.append(Paragraph(cl7_txt, s_body))
    
    # Cláusulas Adicionales (si se especifican)
    cl_num = "OCTAVA"
    if clausulas_adicionales and clausulas_adicionales.strip():
        story.append(Paragraph("CLÁUSULA OCTAVA: CONDICIONES ESPECIALES Y ACUERDOS ADICIONALES", s_clause))
        story.append(Paragraph(clausulas_adicionales.strip(), s_body))
        cl_num = "NOVENA"

    # Aceptación
    story.append(Paragraph(f"CLÁUSULA {cl_num}: ACEPTACIÓN", s_clause))
    story.append(Spacer(1, 4))
    cl_acc_txt = (
        f"En fe de lo cual, y estando de acuerdo con todas y cada una de las cláusulas aquí redactadas, firmamos "
        f"el presente contrato en duplicado en fecha: <b>{fecha_firma}</b>."
    )
    story.append(Paragraph(cl_acc_txt, s_body))
    story.append(Spacer(1, 28))

    # 3. Firmas
    s_firma = ParagraphStyle("fsig", parent=st["Normal"], fontSize=8.5, alignment=TA_CENTER, leading=11)
    
    sig_table = Table([
        [
            [
                Spacer(1, 25),
                HRFlowable(width="75%", thickness=1, color=HexColor("#999"), spaceBefore=2, spaceAfter=2),
                Paragraph("<b>EL CONSULTOR</b>", s_firma),
                Paragraph(c_nom, s_firma),
                Paragraph(c_reg, s_firma),
            ],
            [
                Spacer(1, 25),
                HRFlowable(width="75%", thickness=1, color=HexColor("#999"), spaceBefore=2, spaceAfter=2),
                Paragraph("<b>EL PROPIETARIO / CLIENTE</b>", s_firma),
                Paragraph(cl_nom, s_firma),
                Paragraph(f"RTN: {cl_rtn if cl_rtn else '______'}", s_firma),
            ]
        ]
    ], colWidths=[8.5*cm, 8.5*cm])
    sig_table.setStyle(TableStyle([
        ("VALIGN", (0,0),(-1,-1), "TOP"),
        ("TOPPADDING", (0,0),(-1,-1), 10),
    ]))
    
    from reportlab.platypus import KeepTogether
    story.append(KeepTogether(sig_table))

    # Construir documento
    def add_page_decorations(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(HexColor("#666666"))
        page_num = canvas.getPageNumber()
        canvas.drawString(2.5*cm, 1.2*cm, "SilvaDesk Pro — Contrato de Servicios Profesionales Forestales")
        canvas.drawRightString(doc.pagesize[0] - 2.5*cm, 1.2*cm, f"Página {page_num}")
        canvas.restoreState()
        
    doc.build(story, onFirstPage=add_page_decorations, onLaterPages=add_page_decorations)
    return ruta_pdf
