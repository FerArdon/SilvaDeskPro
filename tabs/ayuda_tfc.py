"""
tabs/ayuda_tfc.py – Pestaña de Ayuda y Guía de Llenado para Bitácora TFC
SilvaDesk Pro · SEDCAF / ICF Honduras
"""
import customtkinter as ctk
import tkinter as tk

V_OSC="#1B5E20"; V_MED="#2E7D32"; V_CLR="#E8F5E9"; BLANCO="#FFFFFF"; GRIS_F="#F2F5F0"

class AyudaTFCTab:
    def __init__(self, parent, app):
        self.parent = parent; self.app = app
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)

        # Contenedor principal con scroll
        self.scroll = ctk.CTkScrollableFrame(parent, fg_color=GRIS_F)
        self.scroll.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self.scroll.grid_columnconfigure(0, weight=1)

        self._build_ayuda_content()

    def _build_ayuda_content(self):
        # ── Título Principal ──────────────────────────────────────────────────
        title_lbl = ctk.CTkLabel(self.scroll, 
            text="❓ Guía Oficial para el Llenado de la Bitácora de Campo TFC",
            font=("Segoe UI", 20, "bold"), text_color=V_OSC, anchor="w")
        title_lbl.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))

        subtitle_lbl = ctk.CTkLabel(self.scroll,
            text="Lineamientos técnicos e instrucciones conforme al Reglamento Especial (La Gaceta No. 36,401).",
            font=("Segoe UI", 14, "italic"), text_color="#555", anchor="w")
        subtitle_lbl.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 15))

        # ── 1. Apertura de Operaciones ─────────────────────────────────────────
        self._add_card(2, "1. Apertura de Operaciones Forestales",
            "Al dar inicio a un nuevo Plan Operativo Anual (POA), se debe asentar una nota de apertura en el Folio No. 1 de la bitácora física.",
            [
                "• Registrar con exactitud la fecha y hora de la inspección o inicio físico.",
                "• Declarar la identidad y colegiación del Técnico Forestal Calificado (TFC) responsable.",
                "• Vincular el número de autorización oficial del POA y del Plan de Manejo emitido por el ICF.",
                "• Listar a los propietarios del bosque y a los contratistas encargados de la extracción.",
                "• Describir los linderos, superficie en hectáreas y estado inicial de la masa forestal."
            ])

        # ── 2. Registro Técnico Diario (Corte y Cubicacion) ───────────────────
        self._add_card(3, "2. Seguimiento y Cubicaciones Técnicas",
            "Las actividades de corta y extracción de producto forestal deben detallarse indicando el volumen cubicado en metros cúbicos (m³).",
            [
                "• Detallar diariamente el avance de corta en campo por sector o bloque de aprovechamiento.",
                "• Registrar el número de trozas o volumen en metros cúbicos (m³) cubicado, separándolo por especie forestal.",
                "• Anotar las eficiencias del aserrío o motosierrista si el procesamiento es directo en el predio.",
                "• Registrar los números de las guías de transporte forestal utilizadas para movilizar la madera."
            ])

        # ── 3. Monitoreo de Plagas e Incidencias ──────────────────────────────
        self._add_card(4, "3. Monitoreo de Salud Forestal (Plagas e Incendios)",
            "Es responsabilidad directa del TFC alertar y registrar incidencias de agentes nocivos, especialmente el gorgojo descortezador del pino.",
            [
                "• Anotar observaciones sobre presencia de ataques del gorgojo descortezador del pino (brotes activos o controlados).",
                "• Describir el número del brote del gorgojo y las medidas de saneamiento aplicadas (corta, descortezado, apilado).",
                "• Reportar incidencias o conatos de incendios forestales indicando el área afectada en hectáreas.",
                "• Registrar cualquier afectación por vientos, tormentas o plagas secundarias observadas en campo."
            ])

        # ── 4. Mitigación y Cumplimiento Ambiental ────────────────────────────
        self._add_card(5, "4. Mitigación de Impactos Ambientales",
            "La bitácora debe reflejar el estricto cumplimiento de las medidas de protección ambiental y social reguladas por el ICF.",
            [
                "• Dejar constancia de la protección y delimitación de fajas protectoras alrededor de microcuencas y fuentes de agua.",
                "• Registrar las actividades de construcción y mantenimiento de caminos forestales para evitar la erosión del suelo.",
                "• Anotar la disposición final de los residuos y copas de árboles (apilamiento o remoción para reducción de combustible de incendios).",
                "• Registrar el cumplimiento de convenios o beneficios acordados con comunidades locales circunvecinas."
            ])

        # ── 5. Cierre del POA (Clausura) ──────────────────────────────────────
        self._add_card(6, "5. Cierre Técnico de Operaciones (Clausura)",
            "Una vez concluido el volumen autorizado en el POA o finalizado el plazo de ejecución, se asienta la clausura de operaciones.",
            [
                "• Realizar un resumen comparativo del volumen cubicado y extraído frente al volumen total autorizado por el ICF.",
                "• Certificar que no quedaron trozas de madera abandonadas en el área de corta o en los patios de acopio.",
                "• Declarar la limpieza técnica del área y el cierre oficial de la bitácora física.",
                "• Firmar y sellar en calidad de TFC responsable del POA."
            ])

        # Espaciador al final
        ctk.CTkLabel(self.scroll, text="", height=10).grid(row=7, column=0)

    def _add_card(self, r, title, intro, items):
        # Marco de la tarjeta
        card = ctk.CTkFrame(self.scroll, fg_color=BLANCO, corner_radius=6, border_width=1, border_color="#A5D6A7")
        card.grid(row=r, column=0, sticky="ew", padx=15, pady=8)
        card.grid_columnconfigure(0, weight=1)

        # Cabecera de la tarjeta
        hdr = ctk.CTkFrame(card, fg_color=V_MED, corner_radius=4, height=30)
        hdr.grid(row=0, column=0, sticky="ew", padx=4, pady=(4, 2))
        hdr.grid_propagate(False)
        ctk.CTkLabel(hdr, text=f"  {title}", font=("Segoe UI", 15, "bold"), text_color=BLANCO, anchor="w").pack(fill="both", expand=True)

        # Introducción
        intro_lbl = ctk.CTkLabel(card, text=intro, font=("Segoe UI", 14, "bold"), text_color=V_OSC, anchor="w", justify="left", wraplength=1050)
        intro_lbl.grid(row=1, column=0, sticky="w", padx=15, pady=(8, 4))

        # Recomendaciones en lista
        for i, item in enumerate(items, 2):
            lbl_item = ctk.CTkLabel(card, text=item, font=("Segoe UI", 14), text_color="#333", anchor="w", justify="left", wraplength=1050)
            lbl_item.grid(row=i, column=0, sticky="w", padx=(30, 15), pady=2)

        # Espacio inferior
        ctk.CTkLabel(card, text="", height=4).grid(row=len(items)+2, column=0)
