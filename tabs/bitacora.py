"""
tabs/bitacora.py – Protocolo de Actuaciones Técnicas
SilvaDesk Pro · SEDCAF / FEMA Honduras
El Ing. Forestal, en su calidad de Ministro de Fe, asienta aquí
actas con valor jurídico pleno.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, datetime
import customtkinter as ctk
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

V_OSC="#005FB8"; V_MED="#0078D4"; V_CLR="#DDEEFF"; BLANCO="#FFFFFF"
GRIS_F="#F2F5F0"; AMARILL="#FFF2CC"

ESTADOS = ["Activa","En trámite","Elevada a proceso penal","Archivada","Anulada"]

TIPOS_DILIGENCIA = [
    "Inspección Ocular",
    "Acta de Peritaje Forestal",
    "Acta de Toma de Muestra",
    "Acta de Constatación de Daños",
    "Acta de Decomiso",
    "Acta de Marcación de Árboles",
    "Acta de Inventario Forestal",
    "Dictamen Técnico Pericial",
    "Acta de Denuncia",
    "Certificación Técnica",
    "Diligencia de Seguimiento",
    "Acta de Finiquito – Regla 3×1",
    "Verificación de Cumplimiento de Medidas Ambientales",
    "Otra diligencia técnica",
]

DEPARTAMENTOS = [
    "Atlántida","Choluteca","Colón","Comayagua","Copán","Cortés","El Paraíso",
    "Francisco Morazán","Gracias a Dios","Intibucá","Islas de la Bahía","La Paz",
    "Lempira","Ocotepeque","Olancho","Santa Bárbara","Valle","Yoro",
]

FUNDAMENTOS = [
    "Art. 100 LFAPVS – Aprovechamiento ilegal",
    "Art. 103 LFAPVS – Daño a ecosistemas",
    "Art. 67 LFAPVS – Áreas protegidas",
    "Art. 9 Ley Forestal – Actividades sin permiso",
    "Art. 172 Código Penal – Daños al medio ambiente",
    "Art. 174 Código Penal – Tráfico de fauna/flora",
    "PCM-002-2006 – Incumplimiento Regla 3×1",
    "Acuerdo 041-2022 ICF – Incumplimiento PMF/POA",
    "Art. 2e Arancel COLPROFORH 2024",
    "Libre (especificar en el campo)",
]

class BitacoraTab:
    def __init__(self, parent, app):
        self.parent = parent; self.app = app
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(1, weight=1)
        self._build_toolbar()
        self._build_tabla()
        self._estilizar_tree()
        self._cargar_datos()

    # ── Barra de herramientas ─────────────────────────────────────────────────
    def _build_toolbar(self):
        tb = ctk.CTkFrame(self.parent, fg_color=V_MED, corner_radius=6, height=44)
        tb.grid(row=0, column=0, sticky="ew", padx=6, pady=(6,4))
        tb.grid_propagate(False); tb.grid_columnconfigure(9, weight=1)

        bc = dict(fg_color=V_OSC, hover_color="#00488F", text_color=BLANCO,
                  font=("Segoe UI",13,"bold"), corner_radius=5, height=32, width=120)

        ctk.CTkButton(tb, text="📜  Nueva Acta",  command=self._nueva_acta,   **bc).grid(row=0,column=0,padx=(8,4),pady=6)
        ctk.CTkButton(tb, text="✏️  Editar",       command=self._editar_sel,   **bc).grid(row=0,column=1,padx=4,pady=6)
        ctk.CTkButton(tb, text="📄  Ver / Imprimir",command=self._imprimir_sel,**bc).grid(row=0,column=2,padx=4,pady=6)
        ctk.CTkButton(tb, text="🗑  Anular",
            command=self._anular_sel,
            fg_color="#8B2020", hover_color="#5C1515",
            text_color=BLANCO, font=("Segoe UI",13,"bold"),
            corner_radius=5, height=32, width=100
        ).grid(row=0, column=3, padx=4, pady=6)

        ctk.CTkLabel(tb, text="|", text_color="#B4D6FA", font=("Segoe UI",13)).grid(row=0,column=4,padx=8)

        ctk.CTkLabel(tb, text="Estado:", text_color=BLANCO, font=("Segoe UI",13)).grid(row=0,column=5,padx=(4,2))
        self.filtro_estado = ctk.CTkComboBox(tb, values=["Todos"]+ESTADOS, width=150, height=30,
            fg_color=BLANCO, text_color=V_OSC, button_color=V_OSC, border_color=V_OSC,
            font=("Segoe UI", 13), dropdown_font=("Segoe UI", 13),
            command=self._filtrar)
        self.filtro_estado.set("Todos"); self.filtro_estado.grid(row=0,column=6,padx=4)

        self.busq_var = tk.StringVar(); self.busq_var.trace_add("write", self._on_busqueda)
        ctk.CTkEntry(tb, textvariable=self.busq_var,
            placeholder_text="🔍  Buscar acta, expediente, lugar…",
            width=240, height=30, fg_color=BLANCO, text_color="#333", border_color=V_OSC,
            font=("Segoe UI", 13)
        ).grid(row=0, column=7, padx=(4,8))

    # ── Tabla de actas ────────────────────────────────────────────────────────
    def _build_tabla(self):
        main = ctk.CTkFrame(self.parent, fg_color=GRIS_F, corner_radius=6)
        main.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0,6))
        main.grid_columnconfigure(0, weight=1); main.grid_rowconfigure(0, weight=1)

        ft = tk.Frame(main, bg=GRIS_F)
        ft.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        ft.grid_columnconfigure(0, weight=1); ft.grid_rowconfigure(0, weight=1)

        cols = ("Acta No.","Folio","Fecha","Hora","Lugar","Tipo de Diligencia","Exp. FEMA","Estado")
        self.tree = ttk.Treeview(ft, columns=cols, show="headings", selectmode="browse")
        widths    = [90, 50, 90, 60, 160, 200, 130, 100]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col, command=lambda c=col: self._sort(c))
            self.tree.column(col, width=w, minwidth=40)

        sb_y = ttk.Scrollbar(ft, orient="vertical",   command=self.tree.yview)
        sb_x = ttk.Scrollbar(ft, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        sb_y.grid(row=0, column=1, sticky="ns")
        sb_x.grid(row=1, column=0, sticky="ew")
        self.tree.bind("<Double-1>", lambda e: self._imprimir_sel())

        self.lbl_count = ctk.CTkLabel(main, text="0 actas", font=("Segoe UI",12),
            text_color="#666", anchor="e")
        self.lbl_count.grid(row=1, column=0, sticky="e", padx=12, pady=(0,4))

    def _estilizar_tree(self):
        s = ttk.Style(); s.theme_use("clam")
        s.configure("Treeview", background=BLANCO, foreground="#111",
            rowheight=26, fieldbackground=BLANCO, font=("Segoe UI",12))
        s.configure("Treeview.Heading", background=V_OSC, foreground=BLANCO,
            font=("Segoe UI",12,"bold"), relief="flat")
        s.map("Treeview.Heading", background=[("active",V_MED)])
        s.map("Treeview", background=[("selected",V_MED)], foreground=[("selected",BLANCO)])
        self.tree.tag_configure("activa",    background="#EAF4EA")
        self.tree.tag_configure("tramite",   background="#FFF8E1")
        self.tree.tag_configure("penal",     background="#FCE4D6")
        self.tree.tag_configure("archivada", background="#F0F0F0")
        self.tree.tag_configure("anulada",   background="#EBEBEB", foreground="#999")

    def _cargar_datos(self, filas=None):
        self.tree.delete(*self.tree.get_children())
        if filas is None: filas = db.protocolo_todos()
        tm = {"Activa":"activa","En trámite":"tramite","Elevada a proceso penal":"penal",
              "Archivada":"archivada","Anulada":"anulada"}
        for row in filas:
            self.tree.insert("","end", iid=row[0], values=row[1:], tags=(tm.get(row[8],""),))
        self.lbl_count.configure(text=f"{len(filas)} actas")

    def _on_busqueda(self, *_):
        q = self.busq_var.get().strip()
        filas = db.protocolo_buscar(q) if q else db.protocolo_todos()
        self._cargar_datos(filas)

    def _filtrar(self, val):
        self._cargar_datos() if val=="Todos" else self._cargar_datos(db.protocolo_por_estado(val))

    def _sort(self, col):
        items = [(self.tree.set(k,col),k) for k in self.tree.get_children()]
        items.sort(key=lambda x:x[0])
        for i,(_,k) in enumerate(items): self.tree.move(k,"",i)

    # ── Acciones ──────────────────────────────────────────────────────────────
    def _nueva_acta(self):
        total = len(db.protocolo_todos())
        if not self.app.check_record_limit(total, "Protocolo Judicial"):
            return
        self._dialogo()

    def _editar_sel(self):
        sel = self.tree.selection()
        if not sel: messagebox.showinfo("SilvaDesk","Selecciona un acta para editar."); return
        row = db.protocolo_por_id(int(sel[0]))
        if row:
            if row[16] in ["Anulada", "Archivada"]:
                messagebox.showerror("SilvaDesk - Registro Cerrado", f"Esta acta está en estado '{row[16]}' y no puede ser editada ni alterada para garantizar la inmutabilidad de los datos oficiales periciales.")
                return
            self._dialogo(row)

    def _imprimir_sel(self):
        sel = self.tree.selection()
        if not sel: messagebox.showinfo("SilvaDesk","Selecciona un acta para imprimir."); return
        row = db.protocolo_por_id(int(sel[0]))
        if not row: return
        ruta = self._generar_pdf_acta(row)
        if ruta and os.path.exists(ruta):
            if messagebox.askyesno("SilvaDesk",f"Acta generada.\n¿Abrir PDF ahora?\n{ruta}"):
                os.startfile(ruta)
        self.app.set_status(f"Acta No. {row[1]} generada → {ruta}")

    def _anular_sel(self):
        sel = self.tree.selection()
        if not sel: messagebox.showinfo("SilvaDesk","Selecciona un acta."); return
        row = db.protocolo_por_id(int(sel[0]))
        if not row: return
        if row[16] in ["Anulada", "Archivada"]:
            messagebox.showerror("SilvaDesk - Acción No Permitida", f"Esta acta ya se encuentra en estado '{row[16]}' y no puede ser modificada.")
            return
        if messagebox.askyesno("Confirmar",
            f"¿Anular el Acta No. {row[1]}?\n\n"
            "NOTA: En un protocolo de actuaciones periciales las actas no se eliminan,\n"
            "se anulan (quedan con constancia de la anulación)."):
            db.protocolo_editar(
                row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8],
                row[9], row[10], row[11], row[12], row[13], row[14], row[15],
                row[18], row[19], row[20], row[21], row[22], "Anulada", row[17],
                row[24] if len(row) > 24 else "",
                row[25] if len(row) > 25 else "",
                row[26] if len(row) > 26 else "",
                row[27] if len(row) > 27 else "",
                row[28] if len(row) > 28 else ""
            )
            self._cargar_datos()
            self.app.set_status(f"Acta {row[1]} anulada.")

    # ── Diálogo de acta ───────────────────────────────────────────────────────
    def _dialogo(self, datos=None):
        editar = datos is not None
        anio   = str(date.today().year)
        num_acta_def = datos[1] if editar else db.protocolo_siguiente_num(anio)
        folio_def    = datos[2] if editar else db.protocolo_siguiente_folio()

        dlg = ctk.CTkToplevel(self.parent)
        dlg.title(f"Acta No. {num_acta_def}" if editar else "Nueva Acta de Protocolo")
        dlg.geometry("760x720")
        dlg.resizable(True, True)
        dlg.grab_set()
        dlg.configure(fg_color=GRIS_F)

        # Header
        hdr = ctk.CTkFrame(dlg, fg_color=V_OSC, corner_radius=0, height=52)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr,
            text=f"📜  {'Editar' if editar else 'Nueva'} Acta de Protocolo  –  SEDCAF / FEMA Honduras",
            font=("Segoe UI",14,"bold"), text_color=BLANCO
        ).pack(pady=14)

        scroll = ctk.CTkScrollableFrame(dlg, fg_color=GRIS_F)
        scroll.pack(fill="both", expand=True, padx=0, pady=0)
        scroll.grid_columnconfigure(1, weight=1); scroll.grid_columnconfigure(3, weight=1)

        # ── Fila de ayuda ─────────────────────────────────────────────────────
        ctk.CTkFrame(scroll, fg_color=V_CLR, corner_radius=4, height=28).grid(
            row=0,column=0,columnspan=4,sticky="ew",padx=12,pady=(10,6))
        ctk.CTkLabel(scroll,
            text="  ℹ  Todos los campos con asterisco (*) son obligatorios. Esta acta tiene valor jurídico como ministro de fe.",
            font=("Segoe UI",12,"italic"), text_color=V_MED, anchor="w"
        ).grid(row=0,column=0,columnspan=4,sticky="w",padx=20)

        def sec(r,txt):
            f=ctk.CTkFrame(scroll,fg_color=V_MED,corner_radius=4,height=32)
            f.grid(row=r,column=0,columnspan=4,sticky="ew",padx=12,pady=(10,4))
            f.grid_propagate(False)
            ctk.CTkLabel(f,text=f"  {txt}",font=("Segoe UI",14,"bold"),text_color=BLANCO,anchor="w").pack(fill="both",expand=True,padx=8)

        def lbl(r,c,txt): ctk.CTkLabel(scroll,text=txt,font=("Segoe UI",13),text_color="#333",anchor="e").grid(row=r,column=c,sticky="e",padx=(12,6),pady=4)

        def entry(r,c,cs=1,w=None):
            e=ctk.CTkEntry(scroll,height=30,fg_color=BLANCO,border_color=V_OSC,text_color="#111",width=w or 200,font=("Segoe UI", 13))
            e.grid(row=r,column=c,columnspan=cs,sticky="ew",padx=(0,12),pady=4); return e

        def combo(r,c,vals,cs=1):
            cb=ctk.CTkComboBox(scroll,values=vals,height=30,fg_color=BLANCO,text_color="#111",border_color=V_OSC,button_color=V_OSC,font=("Segoe UI", 13),dropdown_font=("Segoe UI", 13))
            cb.grid(row=r,column=c,columnspan=cs,sticky="ew",padx=(0,12),pady=4); return cb

        def textbox(r,c,h=80,cs=3):
            t=ctk.CTkTextbox(scroll,height=h,fg_color=BLANCO,border_color=V_OSC,border_width=2,text_color="#111",font=("Segoe UI",13))
            t.grid(row=r,column=c,columnspan=cs,sticky="ew",padx=(0,12),pady=4); return t

        # ── Sección 1: Identificación del Acta ───────────────────────────────
        sec(1,"1.  IDENTIFICACIÓN DEL ACTA")

        lbl(2,0,"Acta No. *:"); e_num=entry(2,1)
        e_num.insert(0,num_acta_def)

        lbl(2,2,"Folio:"); e_folio=entry(2,3,w=80)
        e_folio.insert(0,str(folio_def))

        lbl(3,0,"Tipo de Diligencia *:"); cb_tipo=combo(3,1,TIPOS_DILIGENCIA,cs=3)
        cb_tipo.set(datos[10] if editar and datos[10] else TIPOS_DILIGENCIA[0])

        # Cargar técnicos desde BD
        lista_tecs = db.tecnicos_tfc_todos()
        dict_tecs = {t[1]: t[2] for t in lista_tecs}
        nombres_tecs = [t[1] for t in lista_tecs]
        if not nombres_tecs:
            nombres_tecs = ["Ing. Fernando Rafael Ardon Rodriguez"]
            dict_tecs = {"Ing. Fernando Rafael Ardon Rodriguez": "COLPROFORH N.- 0226"}

        lbl(4,0,"Expediente FEMA No.:"); e_exp=entry(4,1)
        if editar and datos[9]: e_exp.insert(0,datos[9])

        lbl(4,2,"Perito Responsable *:")
        cb_perito = combo(4,3,nombres_tecs)
        cb_perito.set(datos[27] if editar and len(datos) > 27 and datos[27] else nombres_tecs[0])

        # ── Sección 2: Lugar y Tiempo ─────────────────────────────────────────
        sec(5,"2.  LUGAR Y TIEMPO")

        lbl(6,0,"Fecha *:"); e_fecha=entry(6,1)
        e_fecha.insert(0,datos[4] if editar else date.today().strftime("%d/%m/%Y"))

        lbl(6,2,"Hora *:"); e_hora=entry(6,3,w=100)
        e_hora.insert(0,datos[5] if editar else datetime.now().strftime("%H:%M"))

        lbl(7,0,"Lugar / Sitio:"); e_lugar=entry(7,1)
        if editar and datos[6]: e_lugar.insert(0,datos[6])

        lbl(8,0,"Municipio:"); e_mun=entry(8,1)
        if editar and datos[7]: e_mun.insert(0,datos[7])

        lbl(8,2,"Departamento:"); cb_dept=combo(8,3,DEPARTAMENTOS)
        cb_dept.set(datos[8] if editar and datos[8] else "Francisco Morazán")

        # Fila 9: Coordenadas UTM
        lbl(9,0,"Zona UTM:")
        cb_utm_z = combo(9,1,["16N", "17N"])
        if editar and len(datos) > 18 and datos[18]:
            cb_utm_z.set(datos[18])
        else:
            cb_utm_z.set("16N")

        lbl(9,2,"Este (X) / Norte (Y):")
        f_coord = ctk.CTkFrame(scroll, fg_color="transparent")
        f_coord.grid(row=9, column=3, sticky="ew", padx=(0,12), pady=4)
        f_coord.columnconfigure(0, weight=1); f_coord.columnconfigure(1, weight=1)

        e_este = ctk.CTkEntry(f_coord, height=30, fg_color=BLANCO, border_color=V_OSC, text_color="#111", font=("Segoe UI", 13), placeholder_text="Este (m)")
        e_este.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        if editar and len(datos) > 19 and datos[19] is not None:
            e_este.insert(0, f"{datos[19]:.1f}")

        e_norte = ctk.CTkEntry(f_coord, height=30, fg_color=BLANCO, border_color=V_OSC, text_color="#111", font=("Segoe UI", 13), placeholder_text="Norte (m)")
        e_norte.grid(row=0, column=1, sticky="ew", padx=(2, 0))
        if editar and len(datos) > 20 and datos[20] is not None:
            e_norte.insert(0, f"{datos[20]:.1f}")

        # ── Sección 3: Comparecientes ─────────────────────────────────────────
        sec(10,"3.  COMPARECIENTES Y PRESENTES")
        lbl(11,0,"Personas presentes *:")
        t_comp=textbox(11,1,h=80)
        if editar and datos[11]: t_comp.insert("1.0",datos[11])
        ctk.CTkLabel(scroll,text="(Un nombre por línea: nombre, cargo, identidad)",
            font=("Segoe UI",12,"italic"),text_color="#888",anchor="w"
        ).grid(row=12,column=1,columnspan=3,sticky="nw",padx=(0,12))

        # ── Sección 4: Contenido Técnico ──────────────────────────────────────
        sec(13,"4.  CONTENIDO TÉCNICO")

        lbl(14,0,"Hechos constatados *:")
        t_hechos=textbox(14,1,h=110)
        if editar and datos[12]: t_hechos.insert("1.0",datos[12])

        lbl(15,0,"Hallazgos técnicos *:")
        t_hall=textbox(15,1,h=110)
        if editar and datos[13]: t_hall.insert("1.0",datos[13])

        # ── Sección 5: Marco Legal y Disposición ──────────────────────────────
        sec(16,"5.  FUNDAMENTO LEGAL Y DISPOSICIÓN")

        lbl(17,0,"Fundamento legal:"); cb_fund=combo(17,1,FUNDAMENTOS,cs=3)
        cb_fund.set(datos[14] if editar and datos[14] else FUNDAMENTOS[0])

        lbl(18,0,"Disposición / Recomendación:")
        t_disp=textbox(18,1,h=80)
        if editar and datos[15]: t_disp.insert("1.0",datos[15])

        lbl(19,0,"Estado del acta:"); cb_est=combo(19,1,ESTADOS)
        cb_est.set(datos[16] if editar and datos[16] else "Activa")

        lbl(20,0,"Observaciones:")
        t_obs=textbox(20,1,h=60)
        if editar and datos[17]: t_obs.insert("1.0",datos[17])

        # ── Sección 6: Organización Documental y Archivos Escaneados ──────────
        sec(21,"6.  ORGANIZACIÓN DOCUMENTAL Y ARCHIVOS ESCANEADOS")
        
        # Variables de ruta
        ruta_caso_var = tk.StringVar(value=datos[24] if editar and len(datos) > 24 and datos[24] else "")
        scan_exp_var = tk.StringVar(value=datos[25] if editar and len(datos) > 25 and datos[25] else "")
        scan_ot_var = tk.StringVar(value=datos[26] if editar and len(datos) > 26 and datos[26] else "")

        # Carpeta del caso
        lbl(22,0,"Carpeta del Caso:")
        f_folder = ctk.CTkFrame(scroll, fg_color="transparent")
        f_folder.grid(row=22, column=1, columnspan=3, sticky="ew", padx=(0,12), pady=4)
        f_folder.columnconfigure(0, weight=1)

        ent_folder = ctk.CTkEntry(f_folder, height=30, fg_color=BLANCO, border_color=V_OSC, text_color="#111", font=("Segoe UI", 12), textvariable=ruta_caso_var)
        ent_folder.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        
        # Si el registro no está activo, bloquear los campos
        registro_listo = editar and datos[16] in ["Anulada", "Archivada"]
        if registro_listo:
            ent_folder.configure(state="disabled")

        def buscar_carpeta():
            if registro_listo: return
            from tkinter import filedialog
            d = filedialog.askdirectory(title="Seleccionar Carpeta del Caso")
            if d: ruta_caso_var.set(os.path.abspath(d))

        btn_browse_folder = ctk.CTkButton(f_folder, text="📁 Buscar...", command=buscar_carpeta, width=80, height=30, fg_color=V_MED, hover_color=V_OSC, text_color=BLANCO, font=("Segoe UI", 11, "bold"))
        btn_browse_folder.grid(row=0, column=1)
        if registro_listo:
            btn_browse_folder.configure(state="disabled")

        import shutil
        def seleccionar_y_copiar(var_dest, prefix):
            if registro_listo: return
            folder = ruta_caso_var.get().strip()
            if not folder:
                messagebox.showwarning("Carpeta del caso requerida", "Por favor seleccione primero la Carpeta de Trabajo del Caso."); return
            
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(
                title=f"Seleccionar archivo escaneado para {prefix}",
                filetypes=[("Archivos PDF e Imágenes", "*.pdf;*.png;*.jpg;*.jpeg"), ("Todos los archivos", "*.*")]
            )
            if not file_path: return
            
            try:
                os.makedirs(folder, exist_ok=True)
                ext = os.path.splitext(file_path)[1]
                safe_prefix = prefix.replace(" ", "_")
                dest_name = f"{safe_prefix}{ext}"
                dest_path = os.path.join(folder, dest_name)
                
                if os.path.abspath(file_path) != os.path.abspath(dest_path):
                    shutil.copy2(file_path, dest_path)
                
                var_dest.set(dest_path)
                messagebox.showinfo("Archivo Vinculado", f"El documento fue copiado y guardado en:\n{dest_path}")
            except Exception as ex:
                messagebox.showerror("Error de copia", f"No se pudo copiar el archivo:\n{str(ex)}")

        def abrir_adjunto(var_path):
            p = var_path.get().strip()
            if not p or not os.path.exists(p):
                messagebox.showerror("Archivo no encontrado", "El archivo escaneado no existe o no ha sido vinculado."); return
            try:
                os.startfile(p)
            except Exception as ex:
                messagebox.showerror("Error al abrir", f"No se pudo abrir el archivo:\n{str(ex)}")

        def build_row_file(r, label, var):
            lbl(r, 0, label)
            f = ctk.CTkFrame(scroll, fg_color="transparent")
            f.grid(row=r, column=1, columnspan=3, sticky="ew", padx=(0,12), pady=4)
            f.columnconfigure(0, weight=1)

            e = ctk.CTkEntry(f, height=30, fg_color=BLANCO, border_color=V_OSC, text_color="#111", font=("Segoe UI", 11), textvariable=var)
            e.grid(row=0, column=0, sticky="ew", padx=(0, 4))
            if registro_listo:
                e.configure(state="disabled")

            btn_link = ctk.CTkButton(f, text="🔗 Vincular...", command=lambda: seleccionar_y_copiar(var, label.replace("*","").replace(":","").strip()), width=80, height=30, fg_color=V_MED, hover_color=V_OSC, text_color=BLANCO, font=("Segoe UI", 11))
            btn_link.grid(row=0, column=1, padx=(0,4))
            if registro_listo:
                btn_link.configure(state="disabled")

            ctk.CTkButton(f, text="👁", command=lambda: abrir_adjunto(var), width=30, height=30, fg_color=V_OSC, hover_color=V_MED, text_color=BLANCO, font=("Segoe UI", 12)).grid(row=0, column=2)

        build_row_file(23, "Expediente Escaneado:", scan_exp_var)
        build_row_file(24, "Otros Documentos:", scan_ot_var)

        # ── Botones ───────────────────────────────────────────────────────────
        frm_btn = ctk.CTkFrame(dlg, fg_color=GRIS_F, height=58)
        frm_btn.pack(fill="x", side="bottom"); frm_btn.pack_propagate(False)
        ctk.CTkFrame(frm_btn, fg_color=V_CLR, height=1).pack(fill="x")

        btn_frame = ctk.CTkFrame(frm_btn, fg_color=GRIS_F)
        btn_frame.pack(pady=8)

        def guardar():
            num   = e_num.get().strip()
            fecha = e_fecha.get().strip()
            hora  = e_hora.get().strip()
            comp  = t_comp.get("1.0","end").strip()
            hecho = t_hechos.get("1.0","end").strip()
            hall  = t_hall.get("1.0","end").strip()
            if not num or not fecha or not hora or not comp or not hecho:
                messagebox.showwarning("SilvaDesk","Completa los campos obligatorios (*)."); return
            try: folio_n = int(e_folio.get().strip())
            except: folio_n = db.protocolo_siguiente_folio()

            # Lógica de conversión UTM a GPS
            from utils.geo_conv import utm_to_latlon
            zona_utm = cb_utm_z.get()
            este_s = e_este.get().strip()
            norte_s = e_norte.get().strip()

            lat_val = lon_val = None
            este_val = norte_val = None
            if este_s or norte_s:
                try:
                    este_val = float(este_s.replace(",","").strip())
                    norte_val = float(norte_s.replace(",","").strip())
                    lat_val, lon_val = utm_to_latlon(este_val, norte_val, zona_utm)
                    if lat_val is None or lon_val is None:
                        messagebox.showwarning("SilvaDesk", "Las coordenadas UTM (Este/Norte) no son válidas o están fuera de rango.")
                        return
                    # Validar coordenadas dentro del marco geográfico de Honduras
                    if not (12.9 <= lat_val <= 16.6) or not (-89.5 <= lon_val <= -83.1):
                        messagebox.showwarning("SilvaDesk", "Las coordenadas UTM convertidas quedan fuera de Honduras.")
                        return
                except ValueError:
                    messagebox.showwarning("SilvaDesk", "Las coordenadas UTM deben ser números válidos.")
                    return

            perito_sel = cb_perito.get()
            perito_reg_sel = dict_tecs.get(perito_sel, "")

            args = (num, folio_n, anio, fecha, hora, e_lugar.get().strip(),
                    e_mun.get().strip(), cb_dept.get(), e_exp.get().strip(),
                    cb_tipo.get(), comp, hecho, hall, cb_fund.get(),
                    t_disp.get("1.0","end").strip(), zona_utm, este_val, norte_val,
                    lat_val, lon_val, cb_est.get(), t_obs.get("1.0","end").strip(),
                    ruta_caso_var.get().strip(),
                    scan_exp_var.get().strip(),
                    scan_ot_var.get().strip(),
                    perito_sel,
                    perito_reg_sel)

            if editar: db.protocolo_editar(datos[0], *args)
            else:      db.protocolo_agregar(*args)
            self.app.set_status(f"Acta {num} {'actualizada' if editar else 'registrada'}.")
            dlg.destroy(); self._cargar_datos()

        def guardar_e_imprimir():
            guardar()
            filas = db.protocolo_todos()
            if filas:
                row = db.protocolo_por_id(filas[0][0])
                if row:
                    ruta = self._generar_pdf_acta(row)
                    if ruta and messagebox.askyesno("SilvaDesk",f"¿Abrir PDF ahora?\n{ruta}"):
                        os.startfile(ruta)

        ctk.CTkButton(btn_frame, text="💾  Guardar", command=guardar,
            fg_color=V_OSC, hover_color="#00488F", text_color=BLANCO,
            font=("Segoe UI",13,"bold"), width=140, height=38, corner_radius=6
        ).pack(side="left", padx=6)
        ctk.CTkButton(btn_frame, text="💾📄  Guardar e Imprimir", command=guardar_e_imprimir,
            fg_color=V_MED, hover_color=V_OSC, text_color=BLANCO,
            font=("Segoe UI",13,"bold"), width=180, height=38, corner_radius=6
        ).pack(side="left", padx=6)
        ctk.CTkButton(btn_frame, text="Cancelar", command=dlg.destroy,
            fg_color="#888", hover_color="#666", text_color=BLANCO,
            font=("Segoe UI",13), width=100, height=38, corner_radius=6
        ).pack(side="left", padx=6)

    # ── Generar PDF del acta ──────────────────────────────────────────────────
    def _generar_pdf_acta(self, row):
        from utils.pdf_acta import generar_acta
        conf = db.config_obtener()
        base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Actas")
        os.makedirs(base, exist_ok=True)
        safe = "".join(c for c in f"Acta_{row[1]}" if c.isalnum() or c in "_-")
        ruta = os.path.join(base, f"{safe}.pdf")
        
        # Recuperar perito del acta o usar el global por defecto
        perito_nom = row[27] if len(row) > 27 and row[27] else conf[2]
        perito_reg = row[28] if len(row) > 28 and row[28] else conf[3]

        datos = {
            "num_acta":            row[1],
            "folio":               row[2],
            "anio":                row[3],
            "fecha":               row[4],
            "hora":                row[5],
            "lugar":               row[6],
            "municipio":           row[7],
            "departamento":        row[8],
            "num_expediente_fema": row[9],
            "tipo_diligencia":     row[10],
            "comparecientes":      row[11],
            "hechos":              row[12],
            "hallazgos":           row[13],
            "fundamento_legal":    row[14],
            "disposicion":         row[15],
            "estado":              row[16],
            "observaciones":       row[17],
            "perito_nombre":       perito_nom,
            "perito_registro":     perito_reg,
            "seccion":             conf[1],
        }
        return generar_acta(ruta, datos)
