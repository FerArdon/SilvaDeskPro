"""
tabs/facturador.py – Módulo Facturador
SilvaDesk Pro · SEDCAF / FEMA Honduras
CAI conforme SAR Honduras · ISV 15% · ISR 12.5% referencial
Todas las facturas emitidas quedan registradas en la BD con su PDF.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import customtkinter as ctk
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

V_OSC="#005FB8"; V_MED="#0078D4"; V_CLR="#DDEEFF"; BLANCO="#FFFFFF"
GRIS_F="#F2F5F0"; GRIS_B="#DDDDDD"; AMARILL="#FFF8DC"; NARANJ="#C0392B"

SERVICIOS_ARANCEL = [
    # ── Planes de Manejo ─────────────────────────────────────────────────────
    ("Plan de Manejo Forestal (PMF) – <100 ha",           "L. 60,000.00"),
    ("Plan de Manejo Forestal (PMF) – >100 ha",           "Variable (L.80/m³)"),
    ("Plan Operativo Anual (POA) – Elaboración",          "L.150/m³"),
    ("Plan Operativo Anual (POA) – Administración",       "L.120/m³"),
    ("Plan Operativo Anual (POA) – Elaboración+Admón.",   "L.270/m³"),
    ("Plan de Protección Forestal",                       "Variable"),
    # ── Inventarios y Evaluaciones ───────────────────────────────────────────
    ("Inventario Forestal",                               "Variable"),
    ("Evaluación de Regeneración Natural",                "Variable"),
    ("Medición de propiedades – <100 ha",                 "L. 15,000.00"),
    ("Medición de propiedades – >100 ha",                 "Variable"),
    # ── Plantaciones ─────────────────────────────────────────────────────────
    ("Establecimiento de Plantaciones",                   "L.10,000/ha"),
    ("Certificación de Plantaciones (1-10 ha)",           "L. 5,000.00"),
    ("Certificación de Plantaciones (>10 ha)",            "L.2,000/ha adicional"),
    # ── Industria Forestal ───────────────────────────────────────────────────
    ("Memoria Técnica – Industria Primaria",              "Variable"),
    ("Memoria Técnica – Industria Secundaria",            "Variable"),
    ("Informe Mensual Industria – <500 m³",               "L. 3,500.00"),
    ("Informe Mensual Industria – >500 m³",               "L. 5,000.00"),
    # ── Peritajes y Dictámenes ───────────────────────────────────────────────
    ("Dictamen Técnico Pericial Forestal",                "L. 15,000.00"),
    ("Peritaje – Avalúo de volumen (L./m³)",              "L.300/m³"),
    ("Peritaje Judicial / Reclamo Civil o Adm.",          "15% s/demanda (Art.12)"),
    ("Peritaje Forestal – Proceso Penal",                 "Variable (CPP Art.124)"),
    ("Inspección Ocular / Constatación de Daños",         "L. 8,000.00"),
    ("Certificación Técnica Forestal",                    "L. 6,000.00"),
    ("Avalúo Forestal de Daños y Perjuicios",             "L. 18,000.00"),
    # ── Finiquitos y Regla 3×1 ───────────────────────────────────────────────
    ("Finiquito (Regla 3×1) – <100 ha",                   "L. 30,000.00"),
    ("Finiquito (Regla 3×1) – >100 ha",                   "L. 50,000.00"),
    # ── SIG y Ambiental ──────────────────────────────────────────────────────
    ("Evaluación Viabilidad Licencia Ambiental",          "Variable"),
    ("EIA – Categoría 4",                                 "Variable"),
    ("Elaboración de Mapa Temático / SIG",                "L. 8,500.00"),
    ("Análisis NDVI / Teledetección Multitemporal",       "L. 12,000.00"),
    ("Supervisión de Aprovechamiento Forestal",           "L. 10,000.00"),
    ("Verificación de Cumplimiento de PMF/POA",           "L. 8,000.00"),
    ("Regencia Forestal (mensual)",                       "L. 12,000.00"),
    ("Vivero / Reforestación – asesoría técnica",         "L. 7,000.00"),
    # ── Consultoría ──────────────────────────────────────────────────────────
    ("Consultoría Técnica – Por hora (Cat. C)",           "L. 722.66/h"),
    ("Consultoría Técnica – Por día",                     "L. 4,500.00"),
    ("Capacitación / Taller técnico (por día)",           "L. 5,000.00"),
    ("Elaboración de Denuncia Técnica",                   "L. 5,000.00"),
    ("Acta de Decomiso / Marcación de Árboles",           "L. 4,000.00"),
    # ── Software e Informática Forestal/Ambiental Especializada ──────────────
    ("Desarrollo de Software Forestal/Ambiental Especializado",  "Variable"),
    ("Sistema de Gestión de Expedientes Forestales",             "Variable"),
    ("Desarrollo de Aplicación SIG / Geoespacial",               "Variable"),
    ("Módulo de Facturación y Bitácora Forestal (licencia)",      "Variable"),
    ("Implementación / Configuración de Sistema Especializado",   "Variable"),
    ("Soporte Técnico de Software Forestal (por hora)",           "L. 800.00"),
    ("Capacitación en Software SIG / Forestal (por día)",         "L. 5,500.00"),
    ("Mantenimiento Anual de Sistema Especializado",              "Variable"),
    # ── General ───────────────────────────────────────────────────────────────
    ("Zona Especial – Recargo 50% (Gracias a Dios / Islas Bahía / Iriona)", "+50% sobre base"),
    ("Otro servicio / Honorarios libres",                        "Variable"),
]

ISV   = 0.15
ISR   = 0.125

class FacturadorTab:
    def __init__(self, parent, app):
        self.parent = parent; self.app = app
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)
        self._items  = []       # líneas de servicio
        self._edit_id = None    # None = nueva factura | int = ID editando

        # PanedWindow horizontal
        self._paned = tk.PanedWindow(
            parent,
            orient=tk.HORIZONTAL,
            sashwidth=6,          # ancho del divisor (px)
            sashrelief="flat",
            bg="#C0D4EC",         # color del sash (tono acento)
            handlesize=0,         # sin manija extra
        )
        self._paned.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        self._build_form()
        self._build_historial()

    # ══════════════════════════════════════════════════════════════════════════
    # PANEL IZQUIERDO: Formulario de factura
    # ══════════════════════════════════════════════════════════════════════════
    def _build_form(self):
        # tk.PanedWindow solo acepta widgets Tkinter puros como panes
        pane_left = tk.Frame(self._paned, bg=GRIS_F)
        pane_left.rowconfigure(0, weight=1)
        pane_left.columnconfigure(0, weight=1)
        self._paned.add(pane_left, minsize=420, stretch="always")

        frame = ctk.CTkScrollableFrame(pane_left, fg_color=GRIS_F, corner_radius=6)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure(1, weight=1)

        # ── Header del panel ─────────────────────────────────────────────────
        hdr = ctk.CTkFrame(frame, fg_color=V_OSC, corner_radius=6, height=40)
        hdr.grid(row=0,column=0,columnspan=2,sticky="ew",pady=(0,10)); hdr.grid_propagate(False)
        ctk.CTkLabel(hdr,text="🧾  Nueva Factura",font=("Segoe UI",14,"bold"),text_color=BLANCO).pack(side="left",padx=14,pady=8)
        self.lbl_num = ctk.CTkLabel(hdr,text=f"No. {db.siguiente_num_factura()}",
            font=("Segoe UI",12,"bold"),text_color="#B4D6FA")
        self.lbl_num.pack(side="right",padx=14)

        def lbl(r,t): ctk.CTkLabel(frame,text=t,font=("Segoe UI",13),text_color="#333",anchor="e").grid(row=r,column=0,sticky="e",padx=(6,8),pady=3)
        def ent(r,ph="",w=None):
            e=ctk.CTkEntry(frame,placeholder_text=ph,height=30,fg_color=BLANCO,border_color=V_OSC,text_color="#111",width=w or 100,font=("Segoe UI", 13))
            e.grid(row=r,column=1,sticky="ew",padx=(0,12),pady=3); return e
        def sec(r,t,color=V_MED):
            f = ctk.CTkFrame(frame, fg_color=color, corner_radius=4, height=32)
            f.grid(row=r, column=0, columnspan=2, sticky="ew", padx=6, pady=(10,4))
            f.grid_propagate(False)
            ctk.CTkLabel(f, text=f"  {t}", font=("Segoe UI", 14, "bold"), text_color=BLANCO, anchor="w").pack(fill="both", expand=True, padx=8)

        # ── Sección CAI ───────────────────────────────────────────────────────
        sec(1,"⚠  DATOS SAR – CAI (obligatorio por ley)",NARANJ)

        ctk.CTkLabel(frame,
            text="  El CAI, fecha límite y rango deben coincidir exactamente con la autorización impresa de SAR.",
            font=("Segoe UI",12,"italic"),text_color=NARANJ,anchor="w"
        ).grid(row=2,column=0,columnspan=2,sticky="w",padx=12)

        lbl(3,"CAI:"); self.e_cai = ent(3,"XXXXXX-XXXXXX-XXXXXX-XXXXXX-XXXXXX-XX")
        lbl(4,"Fecha límite emisión:"); self.e_fecha_lim = ent(4,"DD/MM/AAAA")
        lbl(5,"Rango inicio:"); self.e_rng_ini = ent(5,"0000-0000-0000")
        lbl(6,"Rango fin:");    self.e_rng_fin = ent(6,"0000-0000-0000")

        # ── Sección Emisor ───────────────────────────────────────────────────────
        conf = db.config_obtener()
        sec(7,"1.  DATOS DEL EMISOR")
        lbl(8,"Nombre / Razón social:"); self.e_em_nom = ent(8)
        self.e_em_nom.insert(0, conf[1])
        lbl(9,"RTN Emisor:"); self.e_em_rtn = ent(9, "0000-0000-000000")
        if conf[4]:
            self.e_em_rtn.delete(0, "end")
            self.e_em_rtn.insert(0, conf[4])
        lbl(10,"Dirección:"); self.e_em_dir = ent(10)
        self.e_em_dir.insert(0, conf[5])
        lbl(11,"Teléfono:"); self.e_em_tel = ent(11, "+504 ____-____")
        if conf[6]:
            self.e_em_tel.delete(0, "end")
            self.e_em_tel.insert(0, conf[6])

        # ── Sección Cliente ───────────────────────────────────────────────────
        sec(12,"2.  DATOS DEL CLIENTE")
        lbl(13,"Nombre / Razón social:"); self.e_cl_nom = ent(13)
        lbl(14,"RTN Cliente:");           self.e_cl_rtn = ent(14,"0000-0000-000000")
        lbl(15,"Dirección:");             self.e_cl_dir = ent(15)

        # ── Fecha de emisión ──────────────────────────────────────────────────
        sec(16,"3.  FECHA")
        lbl(17,"Fecha de emisión:"); self.e_fecha = ent(17)
        self.e_fecha.insert(0, date.today().strftime("%d/%m/%Y"))

        # ── Servicios ─────────────────────────────────────────────────────────
        sec(18,"4.  SERVICIOS")

        add_frame = ctk.CTkFrame(frame, fg_color=GRIS_F)
        add_frame.grid(row=19,column=0,columnspan=2,sticky="ew",padx=6,pady=4)
        add_frame.grid_columnconfigure(0, weight=1)

        self.cb_svc = ctk.CTkComboBox(add_frame,
            values=[f"{s[0]}  ({s[1]})" for s in SERVICIOS_ARANCEL],
            height=30, fg_color=BLANCO, text_color="#111", border_color=V_OSC,
            button_color=V_OSC, width=360, font=("Segoe UI", 13), dropdown_font=("Segoe UI", 13))
        self.cb_svc.set(f"{SERVICIOS_ARANCEL[0][0]}  ({SERVICIOS_ARANCEL[0][1]})")
        self.cb_svc.grid(row=0,column=0,padx=4,pady=4)

        self._v_cant = tk.StringVar(value="1")
        self._v_prec = tk.StringVar()
        ctk.CTkEntry(add_frame, textvariable=self._v_cant,
            placeholder_text="Cant.", width=60, height=30, fg_color=BLANCO, border_color=V_OSC,
            font=("Segoe UI", 13)
        ).grid(row=0,column=1,padx=4)
        ctk.CTkEntry(add_frame, textvariable=self._v_prec,
            placeholder_text="Precio Unit. L.", width=120, height=30, fg_color=BLANCO, border_color=V_OSC,
            font=("Segoe UI", 13)
        ).grid(row=0,column=2,padx=4)
        ctk.CTkButton(add_frame, text="➕ Agregar",
            command=self._agregar_item,
            fg_color=V_OSC, hover_color="#00488F", text_color=BLANCO,
            font=("Segoe UI",13,"bold"), width=90, height=30, corner_radius=5
        ).grid(row=0,column=3,padx=4)

        # Tabla de ítems
        cols_i = ("Descripción","Cant.","Precio Unit.","Total","")
        self.tree_items = ttk.Treeview(frame, columns=cols_i, show="headings", height=6)
        widths = [280,50,100,100,30]
        for col,w in zip(cols_i,widths):
            self.tree_items.heading(col,text=col)
            self.tree_items.column(col,width=w,minwidth=30)
        self.tree_items.grid(row=20,column=0,columnspan=2,sticky="ew",padx=6,pady=4)

        # Estilo de la tabla
        s = ttk.Style(); s.configure("Treeview.Heading",background=V_OSC,foreground=BLANCO,font=("Segoe UI",12,"bold"))
        s.map("Treeview.Heading",background=[("active",V_MED)])
        self.tree_items.bind("<Delete>", lambda e: self._quitar_item())

        ctk.CTkButton(frame, text="🗑  Quitar seleccionado",
            command=self._quitar_item,
            fg_color="#8B2020", hover_color="#5C1515", text_color=BLANCO,
            font=("Segoe UI",13), width=160, height=26, corner_radius=4
        ).grid(row=21,column=0,columnspan=2,sticky="e",padx=6,pady=2)

        # ── Totales live ──────────────────────────────────────────────────────
        sec(22,"5.  TOTALES")

        tot_frame = ctk.CTkFrame(frame, fg_color=BLANCO, corner_radius=6, border_width=1, border_color=GRIS_B)
        tot_frame.grid(row=23,column=0,columnspan=2,sticky="ew",padx=6,pady=6)
        tot_frame.grid_columnconfigure(1,weight=1)

        def trow(r,lbl_t,var,bold=False,color=None):
            f = ("Segoe UI",13,"bold") if bold else ("Segoe UI",13)
            tc = color or "#333"
            ctk.CTkLabel(tot_frame,text=lbl_t,font=f,text_color=tc,anchor="e").grid(row=r,column=0,sticky="e",padx=12,pady=2)
            v = tk.StringVar(value="L. 0.00"); var.append(v)
            ctk.CTkLabel(tot_frame,textvariable=v,font=f,text_color=tc,anchor="w").grid(row=r,column=1,sticky="w",padx=12,pady=2)

        self._tvars = []
        trow(0,"Subtotal:",       self._tvars)
        trow(1,"ISV (15%):",      self._tvars)
        trow(2,"TOTAL FACTURA:",  self._tvars, bold=True, color=V_OSC)
        ctk.CTkFrame(tot_frame,fg_color=GRIS_B,height=1).grid(row=3,column=0,columnspan=2,sticky="ew",padx=8,pady=2)
        trow(3,"ISR 12.5%*:",     self._tvars, color="#888")
        trow(4,"Neto a cobrar*:", self._tvars, color="#888")

        ctk.CTkLabel(tot_frame,
            text="* ISR no aparece en la factura (Art. 50 Ley ISR). Es retenido por el cliente al pagar.",
            font=("Segoe UI",12,"italic"),text_color="#888",anchor="w"
        ).grid(row=5,column=0,columnspan=2,sticky="w",padx=12,pady=(0,6))

        # ── Nota / observaciones ──────────────────────────────────────────────
        sec(24,"6.  OBSERVACIONES (OPCIONAL)")
        self.t_nota = ctk.CTkTextbox(frame, height=60, fg_color=BLANCO,
            border_color=GRIS_B, border_width=1, text_color="#111", font=("Segoe UI",13))
        self.t_nota.grid(row=25,column=0,columnspan=2,sticky="ew",padx=6,pady=4)

        # ── Botón emitir ───────────────────────────────────────────────────────
        self.btn_emitir = ctk.CTkButton(frame,
            text="💾  EMITIR FACTURA  (Guardar + PDF)",
            command=self._emitir,
            fg_color=V_OSC, hover_color="#00488F", text_color=BLANCO,
            font=("Segoe UI",13,"bold"), height=44, corner_radius=8
        )
        self.btn_emitir.grid(row=26,column=0,columnspan=2,sticky="ew",padx=6,pady=(10,6))

    # ══════════════════════════════════════════════════════════════════════════
    # PANEL DERECHO: Historial de facturas (copia en sistema)
    # ══════════════════════════════════════════════════════════════════════════
    def _build_historial(self):
        # tk.PanedWindow solo acepta widgets Tkinter puros como panes
        pane_right = tk.Frame(self._paned, bg=GRIS_F)
        pane_right.rowconfigure(0, weight=1)
        pane_right.columnconfigure(0, weight=1)
        self._paned.add(pane_right, minsize=320, stretch="always")

        frame = ctk.CTkFrame(pane_right, fg_color=GRIS_F, corner_radius=6)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        # Header
        hdr = ctk.CTkFrame(frame, fg_color=V_MED, corner_radius=6, height=40)
        hdr.grid(row=0,column=0,sticky="ew"); hdr.grid_propagate(False)
        ctk.CTkLabel(hdr,text="📋  Historial de Facturas Emitidas",
            font=("Segoe UI",14,"bold"),text_color=BLANCO).pack(side="left",padx=12,pady=8)

        # Filtro de estado
        flt_frame = ctk.CTkFrame(frame, fg_color=GRIS_F)
        flt_frame.grid(row=1,column=0,sticky="ew",padx=6,pady=(4,0))
        ctk.CTkLabel(flt_frame,text="Mostrar:",
            font=("Segoe UI",13),text_color="#555").pack(side="left",padx=(6,4),pady=4)
        self._filtro_estado = tk.StringVar(value="TODAS")
        for lbl, val in [("Todas","TODAS"),("✅ Activas","ACTIVA"),("⛔ Anuladas","ANULADA")]:
            ctk.CTkRadioButton(flt_frame, text=lbl, variable=self._filtro_estado, value=val,
                command=self._buscar_facturas,
                font=("Segoe UI",13), text_color="#222",
                fg_color=V_OSC, hover_color=V_MED
            ).pack(side="left",padx=6,pady=4)

        # Búsqueda
        srch_frame = ctk.CTkFrame(frame, fg_color=GRIS_F)
        srch_frame.grid(row=2,column=0,sticky="ew",padx=6,pady=(0,4))
        self.busq_fac = tk.StringVar(); self.busq_fac.trace_add("write", self._buscar_facturas)
        ctk.CTkEntry(srch_frame, textvariable=self.busq_fac,
            placeholder_text="🔍  Buscar por No., cliente, fecha…",
            height=28, fg_color=BLANCO, border_color=V_OSC, text_color="#111",
            font=("Segoe UI", 13)
        ).pack(fill="x",padx=4,pady=4)


        # Tabla historial
        tf = tk.Frame(frame, bg=GRIS_F)
        tf.grid(row=3,column=0,sticky="nsew",padx=6,pady=(0,4)); frame.grid_rowconfigure(3,weight=1)
        tf.grid_columnconfigure(0,weight=1); tf.grid_rowconfigure(0,weight=1)

        cols_h = ("No. Factura","Fecha","Cliente","Total","Estado")
        self.tree_hist = ttk.Treeview(tf, columns=cols_h, show="headings", selectmode="browse")
        for col,w in zip(cols_h,[90,80,150,100,80]):
            self.tree_hist.heading(col,text=col)
            self.tree_hist.column(col,width=w,minwidth=30)

        # Tag visual para facturas anuladas (texto rojo tachado simulado)
        self.tree_hist.tag_configure("anulada",
            foreground="#C42B1C", font=("Segoe UI", 12, "overstrike"))
        self.tree_hist.tag_configure("activa", foreground="#1A3A6B")

        sb = ttk.Scrollbar(tf,orient="vertical",command=self.tree_hist.yview)
        self.tree_hist.configure(yscrollcommand=sb.set)
        self.tree_hist.grid(row=0,column=0,sticky="nsew"); sb.grid(row=0,column=1,sticky="ns")
        self.tree_hist.bind("<Double-1>", lambda e: self._abrir_pdf_sel())

        # Botones historial
        btn_frame = ctk.CTkFrame(frame, fg_color=GRIS_F)
        btn_frame.grid(row=4,column=0,sticky="ew",padx=6,pady=(0,6))
        bc = dict(fg_color=V_OSC,hover_color="#00488F",text_color=BLANCO,
                  font=("Segoe UI",13,"bold"),height=30,corner_radius=5)
        ctk.CTkButton(btn_frame,text="📄  Abrir PDF",command=self._abrir_pdf_sel,width=95,**bc).pack(side="left",padx=3,pady=4)
        ctk.CTkButton(btn_frame,text="✏️  Editar",command=self._cargar_en_formulario,width=80,**bc).pack(side="left",padx=3,pady=4)
        ctk.CTkButton(btn_frame,text="⛔  Anular",command=self._anular_factura,width=85,
            fg_color="#7B3400",hover_color="#5A2600",text_color=BLANCO,
            font=("Segoe UI",13,"bold"),height=30,corner_radius=5).pack(side="left",padx=3,pady=4)
        ctk.CTkButton(btn_frame,text="🔄  Actualizar",command=self._cargar_historial,
            width=95,fg_color=V_MED,hover_color=V_OSC,text_color=BLANCO,
            font=("Segoe UI",13),height=30,corner_radius=5).pack(side="right",padx=4)

        self.lbl_hist_count = ctk.CTkLabel(frame,text="0 facturas",
            font=("Segoe UI",12),text_color="#666",anchor="e")
        self.lbl_hist_count.grid(row=5,column=0,sticky="e",padx=12,pady=(0,4))

        self._cargar_historial()

    # ══════════════════════════════════════════════════════════════════════════
    # Lógica interna
    # ══════════════════════════════════════════════════════════════════════════
    def _agregar_item(self):
        desc_raw = self.cb_svc.get().split("  (")[0].strip()
        try:    cant = float(self._v_cant.get().replace(",","."))
        except: cant = 1.0
        try:    prec = float(self._v_prec.get().replace(",","").replace("L.","").strip())
        except: prec = 0.0
        total = cant * prec
        iid   = str(len(self._items))
        self.tree_items.insert("","end",iid=iid,
            values=(desc_raw, f"{cant:.2f}", f"L. {prec:,.2f}", f"L. {total:,.2f}", "🗑"))
        self._items.append({"descripcion":desc_raw,"cantidad":cant,"precio_unit":prec,"total":total})
        self._v_prec.set(""); self._recalcular()

    def _quitar_item(self):
        sel = self.tree_items.selection()
        if not sel: return
        idx = int(sel[0])
        self.tree_items.delete(sel[0])
        if 0 <= idx < len(self._items): self._items.pop(idx)
        # Rebuild iids
        kids = list(self.tree_items.get_children())
        for i,k in enumerate(kids): self.tree_items.item(k,tags=())
        self._recalcular()

    def _recalcular(self):
        sub = sum(i["total"] for i in self._items)
        isv = sub * ISV
        tot = sub + isv
        isr = tot * ISR
        net = tot - isr
        vals = [f"L. {sub:,.2f}", f"L. {isv:,.2f}", f"L. {tot:,.2f}", f"L. {isr:,.2f}", f"L. {net:,.2f}"]
        for v,tv in zip(vals, self._tvars): tv.set(v)

    def _emitir(self):
        # Validaciones
        if not self._items:
            messagebox.showwarning("SilvaDesk","Agrega al menos un servicio."); return
        cai = self.e_cai.get().strip()
        if not cai:
            messagebox.showwarning("SilvaDesk","El CAI es obligatorio (requerido por SAR Honduras)."); return
        cl_nom = self.e_cl_nom.get().strip()
        if not cl_nom:
            messagebox.showwarning("SilvaDesk","Ingresa el nombre del cliente."); return

        editando = self._edit_id is not None

        # ── Verificación de límite de licencia (solo para facturas nuevas) ──────
        if not editando:
            total_facturas = len(db.facturas_todos())
            if not self.app.check_record_limit(total_facturas, "Facturador"):
                return

        sub = sum(i["total"] for i in self._items)
        isv = sub * ISV; tot = sub + isv
        isr = tot * ISR; net = tot - isr

        num_fac = self.lbl_num.cget("text").replace("No. ","").strip()

        datos = {
            "num_factura":   num_fac,
            "emisor_nombre": self.e_em_nom.get().strip() or "SEDCAF",
            "emisor_rtn":    self.e_em_rtn.get().strip(),
            "emisor_dir":    self.e_em_dir.get().strip(),
            "emisor_tel":    self.e_em_tel.get().strip(),
            "cai":           cai,
            "fecha_limite":  self.e_fecha_lim.get().strip(),
            "rango_inicio":  self.e_rng_ini.get().strip(),
            "rango_fin":     self.e_rng_fin.get().strip(),
            "cliente_nombre":cl_nom,
            "cliente_rtn":   self.e_cl_rtn.get().strip(),
            "cliente_dir":   self.e_cl_dir.get().strip(),
            "fecha_emision": self.e_fecha.get().strip() or date.today().strftime("%d/%m/%Y"),
            "servicios":     self._items,
            "subtotal":      sub,
            "isv":           isv,
            "total":         tot,
            "isr":           isr,
            "neto":          net,
            "nota":          self.t_nota.get("1.0","end").strip(),
        }

        base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Facturas")
        os.makedirs(base, exist_ok=True)
        safe = "".join(c for c in num_fac if c.isalnum() or c in "_-")
        ruta = os.path.join(base, f"Factura_{safe}.pdf")

        try:
            from utils.pdf_invoice import generar_factura
            generar_factura(ruta, datos)
        except Exception as ex:
            messagebox.showerror("Error PDF", f"No se pudo generar el PDF:\n{ex}"); return

        try:
            if editando:
                db.factura_actualizar(
                    self._edit_id,
                    num_fac,
                    datos["fecha_emision"],
                    datos["fecha_limite"],
                    cai,
                    datos["rango_inicio"],
                    datos["rango_fin"],
                    cl_nom,
                    datos["cliente_rtn"],
                    datos["cliente_dir"],
                    json.dumps(self._items, ensure_ascii=False),
                    sub, isv, tot,
                    ruta
                )
            else:
                db.factura_agregar(
                    num_fac,
                    datos["fecha_emision"],
                    datos["fecha_limite"],
                    cai,
                    datos["rango_inicio"],
                    datos["rango_fin"],
                    cl_nom,
                    datos["cliente_rtn"],
                    datos["cliente_dir"],
                    json.dumps(self._items, ensure_ascii=False),
                    sub, isv, tot,
                    ruta
                )
        except Exception as ex:
            messagebox.showwarning("SilvaDesk",
                f"PDF generado, pero no se pudo guardar en la BD:\n{ex}")

        accion = "actualizada" if editando else "emitida y registrada"
        self.app.set_status(f"Factura {num_fac} {accion}. PDF: {ruta}")
        msg = (f"\u2705 Factura {num_fac} actualizada.\n" if editando else
               f"\u2705 Factura {num_fac} emitida y guardada.\n")
        messagebox.showinfo("SilvaDesk", msg +
            f"\ud83d\udcc4 PDF: {ruta}\n"
            f"\ud83d\udcbe Copia en el historial del sistema.")
        if messagebox.askyesno("SilvaDesk", "¿Abrir el PDF de la factura?"):
            try: os.startfile(ruta)
            except: pass

        # Reset formulario y modo edición
        self._edit_id = None
        self.btn_emitir.configure(text="💾  Emitir Factura")
        self._items.clear()
        self.tree_items.delete(*self.tree_items.get_children())
        self.e_cl_nom.delete(0,"end"); self.e_cl_rtn.delete(0,"end"); self.e_cl_dir.delete(0,"end")
        self.t_nota.delete("1.0","end"); self._recalcular()
        nuevo_num = db.siguiente_num_factura()
        self.lbl_num.configure(text=f"No. {nuevo_num}")
        self._cargar_historial()

    def _cargar_historial(self, filas=None):
        self.tree_hist.delete(*self.tree_hist.get_children())
        if filas is None:
            filas = db.facturas_todos()
        activas = anuladas = 0
        for row in filas:
            # row: id, num_factura, fecha, cliente_nombre, total, ruta_pdf, estado
            estado  = (row[6] or "ACTIVA").upper()
            monto   = f"L. {float(row[4] or 0):,.2f}"
            tag     = "anulada" if estado == "ANULADA" else "activa"
            lbl_est = "⛔ ANULADA" if estado == "ANULADA" else "✅ ACTIVA"
            self.tree_hist.insert("", "end", iid=row[0], tags=(tag,),
                values=(row[1], row[2], row[3], monto, lbl_est))
            if estado == "ANULADA": anuladas += 1
            else:                   activas  += 1
        total_n = activas + anuladas
        resumen = f"{total_n} factura{'s' if total_n!=1 else ''}"
        if anuladas: resumen += f"  (⛔ {anuladas} anulada{'s' if anuladas!=1 else ''})"
        self.lbl_hist_count.configure(text=resumen)

    def _buscar_facturas(self, *_):
        """Filtra el historial por texto de búsqueda y/o estado seleccionado."""
        q      = self.busq_fac.get().strip().lower()
        estado = self._filtro_estado.get()   # "TODAS", "ACTIVA" o "ANULADA"
        todas  = db.facturas_todos()

        filtradas = [
            r for r in todas
            if (estado == "TODAS" or (r[6] or "ACTIVA").upper() == estado)
            and (
                not q
                or q in str(r[1]).lower()   # num_factura
                or q in str(r[2]).lower()   # fecha
                or q in str(r[3]).lower()   # cliente
            )
        ]
        self._cargar_historial(filas=filtradas)

    def _abrir_pdf_sel(self):
        """Abre el PDF de la factura seleccionada en el historial."""
        sel = self.tree_hist.selection()
        if not sel:
            messagebox.showinfo("SilvaDesk", "Seleccioná una factura de la lista primero.")
            return
        row_id = sel[0]
        todas = db.facturas_todos()
        for r in todas:
            if str(r[0]) == str(row_id):
                ruta = r[5]
                if ruta and os.path.exists(ruta):
                    try:
                        os.startfile(ruta)
                    except Exception as ex:
                        messagebox.showerror("Error", f"No se pudo abrir el PDF:\n{ex}")
                else:
                    messagebox.showwarning("SilvaDesk",
                        f"El archivo PDF no se encuentra en:\n{ruta}")
                return
        messagebox.showwarning("SilvaDesk", "No se encontró información para esa factura.")

    def _cargar_en_formulario(self):
        """Carga la factura seleccionada en el formulario para editarla."""
        sel = self.tree_hist.selection()
        if not sel:
            messagebox.showinfo("SilvaDesk", "Seleccioná una factura del historial primero."); return
        row_id = int(sel[0])
        row = db.factura_por_id(row_id)
        if not row:
            messagebox.showerror("SilvaDesk", "No se encontró la factura en la base de datos."); return

        # Impedir editar facturas ANULADAS
        estado = ""
        try: estado = (row[15] or "ACTIVA").upper()   # columna estado
        except: pass
        if estado == "ANULADA":
            messagebox.showwarning("SilvaDesk",
                f"La factura {row[1]} está ANULADA y no puede editarse.\n"
                f"Motivo: {row[16] or '—'}")
            return

        self._edit_id = row_id

        def _set(entry, val):
            entry.delete(0, "end")
            entry.insert(0, val or "")

        # CAI y rangos
        _set(self.e_cai,      row[4])
        _set(self.e_fecha_lim,row[3])
        _set(self.e_rng_ini,  row[5])
        _set(self.e_rng_fin,  row[6])
        # Cliente
        _set(self.e_cl_nom,   row[7])
        _set(self.e_cl_rtn,   row[8])
        _set(self.e_cl_dir,   row[9])
        # Fecha emisión
        _set(self.e_fecha,    row[2])

        # Servicios
        self._items.clear()
        self.tree_items.delete(*self.tree_items.get_children())
        try:
            servicios = json.loads(row[10] or "[]")
            for i, svc in enumerate(servicios):
                iid = str(i)
                cant  = svc.get("cantidad",  1)
                prec  = svc.get("precio_unit",0)
                total = svc.get("total",    cant*prec)
                desc  = svc.get("descripcion","")
                self.tree_items.insert("","end",iid=iid,
                    values=(desc, f"{cant:.2f}", f"L. {prec:,.2f}", f"L. {total:,.2f}", "🗑"))
                self._items.append(svc)
        except Exception:
            pass
        self._recalcular()

        # Cambiar botón al modo edición
        self.btn_emitir.configure(
            text=f"✏️  GUARDAR CAMBIOS EN {row[1]}  (Actualizar + PDF)",
            fg_color="#1A6B3A", hover_color="#0D4A27"
        )
        self.app.set_status(f"Editando factura {row[1]} — modificá los campos y pulsá Guardar Cambios.")

    def _eliminar_factura(self):
        """Elimina la factura seleccionada del historial tras confirmación."""
        sel = self.tree_hist.selection()
        if not sel:
            messagebox.showinfo("SilvaDesk", "Seleccioná una factura del historial primero."); return
        row_id = int(sel[0])
        row = db.factura_por_id(row_id)
        if not row: return
        num = row[1]
        if not messagebox.askyesno("Confirmar eliminación",
                f"¿Estás seguro de eliminar la factura {num}?\n"
                f"Esta acción NO se puede deshacer.\n"
                f"El archivo PDF en disco NO será borrado."):
            return
        db.factura_eliminar(row_id)
        self._cargar_historial()
        self.app.set_status(f"Factura {num} eliminada del historial.")

    def _anular_factura(self):
        """Anula la factura seleccionada. Queda permanentemente en el registro como ANULADA."""
        sel = self.tree_hist.selection()
        if not sel:
            messagebox.showinfo("SilvaDesk", "Seleccioná una factura del historial primero."); return
        row_id = int(sel[0])
        row = db.factura_por_id(row_id)
        if not row: return
        num = row[1]

        # Verificar si ya está anulada
        try:
            estado = (row[15] or "ACTIVA").upper()
        except:
            estado = "ACTIVA"
        if estado == "ANULADA":
            messagebox.showinfo("SilvaDesk",
                f"La factura {num} ya está anulada.\nMotivo: {row[16] or '—'}")
            return

        # Diálogo para ingresar el motivo de anulación (obligatorio)
        dlg = tk.Toplevel()
        dlg.title(f"Anular Factura {num}")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.configure(bg="#F3F3F3")

        tk.Label(dlg, text=f"⛔  ANULAR FACTURA {num}",
            font=("Segoe UI", 14, "bold"), fg="#7B3400", bg="#F3F3F3"
        ).pack(padx=24, pady=(18,4))
        tk.Label(dlg,
            text="La factura quedará permanentemente en el registro como ANULADA.\n"
                 "Esta acción NO se puede revertir.",
            font=("Segoe UI", 12), fg="#555", bg="#F3F3F3", justify="center"
        ).pack(padx=24, pady=(0,10))
        tk.Label(dlg, text="Motivo de anulación (obligatorio):",
            font=("Segoe UI", 13, "bold"), fg="#333", bg="#F3F3F3", anchor="w"
        ).pack(padx=24, anchor="w")

        motivo_var = tk.StringVar()
        entry_mot = tk.Entry(dlg, textvariable=motivo_var,
            font=("Segoe UI", 13), width=44, relief="solid", bd=1)
        entry_mot.pack(padx=24, pady=(4,16), ipady=5)
        entry_mot.focus_set()

        def confirmar():
            motivo = motivo_var.get().strip()
            if not motivo:
                messagebox.showwarning("SilvaDesk",
                    "Debés ingresar el motivo de anulación.", parent=dlg)
                return

            # 1. Marcar como ANULADA en la BD
            db.factura_anular(row_id, motivo)

            # 2. Regenerar el PDF con marca de agua ANULADA
            fila = db.factura_por_id(row_id)
            pdf_regenerado = False
            try:
                import json as _json
                from utils.pdf_invoice import generar_factura
                servicios = _json.loads(fila[10] or "[]")
                sub  = float(fila[11] or 0)
                isv  = sub * 0.15
                tot  = sub + isv
                isr  = tot * 0.125
                datos_anul = {
                    "num_factura":    fila[1],
                    "fecha_emision":  fila[2],
                    "fecha_limite":   fila[3],
                    "cai":            fila[4],
                    "rango_inicio":   fila[5],
                    "rango_fin":      fila[6],
                    "cliente_nombre": fila[7],
                    "cliente_rtn":    fila[8],
                    "cliente_dir":    fila[9],
                    "emisor_nombre":  self.e_em_nom.get().strip() or "SEDCAF",
                    "emisor_rtn":     self.e_em_rtn.get().strip(),
                    "emisor_dir":     self.e_em_dir.get().strip(),
                    "emisor_tel":     self.e_em_tel.get().strip(),
                    "servicios":      servicios,
                    "subtotal": sub, "isv": isv, "total": tot,
                    "isr": isr, "neto": tot - isr,
                    "nota": f"⛔ FACTURA ANULADA — Motivo: {motivo}",
                }
                ruta_pdf = fila[14] or os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "Facturas", f"Factura_{fila[1]}.pdf")
                generar_factura(ruta_pdf, datos_anul, anulada=True)
                pdf_regenerado = True
            except Exception as ex:
                pass  # La anulación en BD ya quedó registrada

            dlg.destroy()
            self._cargar_historial()
            self.app.set_status(
                f"⛔ Factura {num} ANULADA. Motivo: {motivo} — Permanece en el registro.")
            msg = (f"⛔ Factura {num} anulada correctamente.\n"
                   f"Motivo registrado: {motivo}\n\n")
            if pdf_regenerado:
                msg += "✅ PDF regenerado con marca de agua ANULADA.\n\n"
            msg += ("La factura permanece en el historial como ANULADA "
                    "para efectos de trazabilidad y cumplimiento SAR.")
            messagebox.showinfo("SilvaDesk", msg)


        btn_f = tk.Frame(dlg, bg="#F3F3F3")
        btn_f.pack(pady=(0,18))
        tk.Button(btn_f, text="⛔  Confirmar Anulación",
            command=confirmar,
            font=("Segoe UI", 13, "bold"), bg="#7B3400", fg="white",
            relief="flat", padx=16, pady=6, cursor="hand2"
        ).pack(side="left", padx=8)
        tk.Button(btn_f, text="  Cancelar  ",
            command=dlg.destroy,
            font=("Segoe UI", 13), bg="#E0E0E0", fg="#333",
            relief="flat", padx=16, pady=6, cursor="hand2"
        ).pack(side="left", padx=8)