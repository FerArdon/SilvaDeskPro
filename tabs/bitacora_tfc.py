"""
tabs/bitacora_tfc.py – Pestaña de Bitácora de Campo TFC (Técnico Forestal Calificado)
SilvaDesk Pro · SEDCAF / ICF Honduras
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
import customtkinter as ctk
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

V_OSC="#1B5E20"; V_MED="#2E7D32"; V_CLR="#E8F5E9"; BLANCO="#FFFFFF"
GRIS_F="#F2F5F0"; AMARILL="#FFF2CC"

ESTADOS_TFC = ["Activo", "En trámite", "Archivada", "Anulada"]

ACTIVIDADES_TFC = [
    "Apertura de Operaciones",
    "Protección Forestal y Prevención de Incendios",
    "Monitoreo y Combate de Plagas",
    "Aprovechamiento y Cubicación de Madera",
    "Mitigación de Impacto Ambiental",
    "Apertura y Mantenimiento de Caminos",
    "Monitoreo de Vida Silvestre",
    "Gestión y Aspectos Sociales",
    "Indicaciones al Titular y Personal",
    "Control de Guías de Movilización",
    "Marcación e Inventario",
    "Cierre de Operaciones del POA",
    "Otra actividad de campo",
]

class BitacoraTFCTab:
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
                  font=("Segoe UI",13,"bold"), corner_radius=5, height=32, width=130)

        ctk.CTkButton(tb, text="📜  Nueva Anotación", command=self._nueva_anotacion, **bc).grid(row=0,column=0,padx=(8,4),pady=6)
        ctk.CTkButton(tb, text="✏️  Editar",          command=self._editar_sel,      **bc).grid(row=0,column=1,padx=4,pady=6)
        ctk.CTkButton(tb, text="📄  Ver / Imprimir",   command=self._imprimir_sel,    **bc).grid(row=0,column=2,padx=4,pady=6)
        ctk.CTkButton(tb, text="🗑  Anular",
            command=self._anular_sel,
            fg_color="#8B2020", hover_color="#5C1515",
            text_color=BLANCO, font=("Segoe UI",13,"bold"),
            corner_radius=5, height=32, width=100
        ).grid(row=0, column=3, padx=4, pady=6)

        ctk.CTkButton(tb, text="❌  Eliminar",
            command=self._eliminar_sel,
            fg_color="#A93226", hover_color="#7B241C",
            text_color=BLANCO, font=("Segoe UI",13,"bold"),
            corner_radius=5, height=32, width=100
        ).grid(row=0, column=4, padx=4, pady=6)

        ctk.CTkButton(tb, text="👥  Técnicos",
            command=self._administrar_tecnicos,
            fg_color=V_OSC, hover_color="#0D47A1",
            text_color=BLANCO, font=("Segoe UI",13,"bold"),
            corner_radius=5, height=32, width=100
        ).grid(row=0, column=5, padx=4, pady=6)

        ctk.CTkLabel(tb, text="|", text_color="#B4D6FA", font=("Segoe UI",13)).grid(row=0,column=6,padx=8)

        ctk.CTkLabel(tb, text="Estado:", text_color=BLANCO, font=("Segoe UI",13)).grid(row=0,column=7,padx=(4,2))
        self.filtro_estado = ctk.CTkComboBox(tb, values=["Todos"]+ESTADOS_TFC, width=130, height=30,
            fg_color=BLANCO, text_color=V_OSC, button_color=V_OSC, border_color=V_OSC,
            font=("Segoe UI", 13), dropdown_font=("Segoe UI", 13),
            command=self._filtrar)
        self.filtro_estado.set("Todos"); self.filtro_estado.grid(row=0,column=8,padx=4)

        self.busq_var = tk.StringVar(); self.busq_var.trace_add("write", self._on_busqueda)
        ctk.CTkEntry(tb, textvariable=self.busq_var,
            placeholder_text="🔍  Buscar por predio, POA, actividad…",
            width=260, height=30, fg_color=BLANCO, text_color="#333", border_color=V_OSC,
            font=("Segoe UI", 13)
        ).grid(row=0, column=9, padx=(4,8))

    # ── Tabla de registros TFC ────────────────────────────────────────────────
    def _build_tabla(self):
        main = ctk.CTkFrame(self.parent, fg_color=GRIS_F, corner_radius=6)
        main.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0,6))
        main.grid_columnconfigure(0, weight=1); main.grid_rowconfigure(0, weight=1)

        ft = tk.Frame(main, bg=GRIS_F)
        ft.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        ft.grid_columnconfigure(0, weight=1); ft.grid_rowconfigure(0, weight=1)

        cols = ("Bitácora Reg.","Folio","Fecha","Sitio / Predio","Código POA","Actividad","Volumen (m³)","Estado")
        self.tree = ttk.Treeview(ft, columns=cols, show="headings", selectmode="browse")
        widths    = [100, 50, 90, 160, 120, 180, 100, 100]
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

        self.lbl_count = ctk.CTkLabel(main, text="0 registros", font=("Segoe UI",12),
            text_color="#666", anchor="e")
        self.lbl_count.grid(row=1, column=0, sticky="e", padx=12, pady=(0,4))

    def _estilizar_tree(self):
        s = ttk.Style()
        s.configure("Treeview", background=BLANCO, foreground="#111",
            rowheight=26, fieldbackground=BLANCO, font=("Segoe UI",12))
        s.configure("Treeview.Heading", background=V_OSC, foreground=BLANCO,
            font=("Segoe UI",12,"bold"), relief="flat")
        s.map("Treeview.Heading", background=[("active",V_MED)])
        s.map("Treeview", background=[("selected",V_MED)], foreground=[("selected",BLANCO)])
        
        self.tree.tag_configure("activo",    background="#EAF4EA")
        self.tree.tag_configure("tramite",   background="#FFF8E1")
        self.tree.tag_configure("archivada", background="#F0F0F0")
        self.tree.tag_configure("anulada",   background="#EBEBEB", foreground="#999")

    def _cargar_datos(self, filas=None):
        self.tree.delete(*self.tree.get_children())
        if filas is None: filas = db.bitacora_tfc_todos()
        tm = {"Activo":"activo", "En trámite":"tramite", "Archivada":"archivada", "Anulada":"anulada"}
        for row in filas:
            # row: id, num_bitacora, folio, fecha, sitio_predio, poa_codigo, actividad_tipo, volumen_m3, estado
            m_vol = f"{float(row[7] or 0):,.2f} m³"
            self.tree.insert("", "end", iid=row[0], values=(row[1], row[2], row[3], row[4], row[5], row[6], m_vol, row[8]), tags=(tm.get(row[8], "activo"),))
        self.lbl_count.configure(text=f"{len(filas)} registros de campo")

    def _on_busqueda(self, *_):
        q = self.busq_var.get().strip()
        filas = db.bitacora_tfc_buscar(q) if q else db.bitacora_tfc_todos()
        self._cargar_datos(filas)

    def _filtrar(self, val):
        self._cargar_datos() if val=="Todos" else self._cargar_datos(db.bitacora_tfc_por_estado(val))

    def _sort(self, col):
        items = [(self.tree.set(k,col),k) for k in self.tree.get_children()]
        items.sort(key=lambda x:x[0])
        for i,(_,k) in enumerate(items): self.tree.move(k,"",i)

    # ── Acciones ──────────────────────────────────────────────────────────────
    def _nueva_anotacion(self):
        total = len(db.bitacora_tfc_todos())
        if not self.app.check_record_limit(total, "Bitácora de Campo TFC"):
            return
        self._dialogo()

    def _editar_sel(self):
        sel = self.tree.selection()
        if not sel: messagebox.showinfo("SilvaDesk","Selecciona un registro de bitácora para editar."); return
        row = db.bitacora_tfc_por_id(int(sel[0]))
        if row:
            if row[21] in ["Archivada", "Anulada"]:
                messagebox.showerror("SilvaDesk - Registro Cerrado", f"Este registro está en estado '{row[21]}' y no puede ser editado ni alterado para garantizar la inmutabilidad de los datos oficiales.")
                return
            self._dialogo(row)

    def _imprimir_sel(self):
        sel = self.tree.selection()
        if not sel: messagebox.showinfo("SilvaDesk","Selecciona un registro para imprimir."); return
        row = db.bitacora_tfc_por_id(int(sel[0]))
        if not row: return
        ruta = self._generar_pdf_bitacora(row)
        if ruta and os.path.exists(ruta):
            if messagebox.askyesno("SilvaDesk", f"Registro de Bitácora generado.\n¿Abrir PDF ahora?\n{ruta}"):
                os.startfile(ruta)
        self.app.set_status(f"Registro No. {row[1]} generado en PDF → {ruta}")

    def _anular_sel(self):
        sel = self.tree.selection()
        if not sel: messagebox.showinfo("SilvaDesk","Selecciona un registro."); return
        row = db.bitacora_tfc_por_id(int(sel[0]))
        if not row: return
        if row[21] in ["Archivada", "Anulada"]:
            messagebox.showerror("SilvaDesk - Acción No Permitida", f"El registro ya se encuentra en estado '{row[21]}' y no puede ser modificado.")
            return
        if messagebox.askyesno("Confirmar",
            f"¿Anular el Registro No. {row[1]}?\n\n"
            "NOTA: Esta acción cambiará el estado a 'Anulada' y bloqueará ediciones posteriores."):
            db.bitacora_tfc_anular(row[0])
            self._cargar_datos()
            self.app.set_status(f"Registro {row[1]} anulado.")

    def _eliminar_sel(self):
        sel = self.tree.selection()
        if not sel: messagebox.showinfo("SilvaDesk","Selecciona un registro de bitácora para eliminar."); return
        row = db.bitacora_tfc_por_id(int(sel[0]))
        if not row: return
        if row[21] != "Activo":
            messagebox.showerror("SilvaDesk - Acción No Permitida", f"Solo se pueden eliminar registros que estén en estado 'Activo'.\nEste registro está en estado '{row[21]}' (listo/cerrado) y no puede ser alterado.")
            return
        if messagebox.askyesno("Confirmar Eliminación",
            f"¿Desea eliminar físicamente el Registro No. {row[1]} de la base de datos?\n\n"
            "Esta acción no se puede deshacer y borrará permanentemente la anotación."):
            db.bitacora_tfc_eliminar(row[0])
            self._cargar_datos()
            self.app.set_status(f"Registro {row[1]} eliminado físicamente.")

    # ── Diálogo de Registro ───────────────────────────────────────────────────
    def _dialogo(self, datos=None):
        editar = datos is not None
        anio   = str(date.today().year)
        num_def   = datos[1] if editar else db.bitacora_tfc_siguiente_num(anio)
        folio_def = datos[2] if editar else db.bitacora_tfc_siguiente_folio()

        dlg = ctk.CTkToplevel(self.parent)
        dlg.title(f"Registro No. {num_def}" if editar else "Nueva Anotación de Bitácora Campo TFC")
        dlg.geometry("780x740")
        dlg.resizable(True, True)
        dlg.grab_set()
        dlg.configure(fg_color=GRIS_F)

        # Header
        hdr = ctk.CTkFrame(dlg, fg_color=V_OSC, corner_radius=0, height=52)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr,
            text=f"📓  {'Editar' if editar else 'Nueva'} Anotación de Bitácora  –  Técnico Forestal Calificado",
            font=("Segoe UI",14,"bold"), text_color=BLANCO
        ).pack(pady=14)

        scroll = ctk.CTkScrollableFrame(dlg, fg_color=GRIS_F)
        scroll.pack(fill="both", expand=True, padx=0, pady=0)
        scroll.grid_columnconfigure(1, weight=1); scroll.grid_columnconfigure(3, weight=1)

        # Fila de ayuda
        ctk.CTkFrame(scroll, fg_color=V_CLR, corner_radius=4, height=28).grid(
            row=0,column=0,columnspan=4,sticky="ew",padx=12,pady=(10,6))
        ctk.CTkLabel(scroll,
            text="  ℹ  Los campos con asterisco (*) son requeridos según el Reglamento TFC (La Gaceta No. 36,401).",
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

        # ── Sección 1: Identificación ──────────────────────────────────────────
        sec(1,"1.  DATOS DE CONTROL DE BITÁCORA")
        lbl(2,0,"Registro No. *:"); e_num=entry(2,1)
        e_num.insert(0, num_def)
        lbl(2,2,"Folio:"); e_folio=entry(2,3,w=80)
        e_folio.insert(0, str(folio_def))

        lbl(3,0,"Sitio / Predio *:"); e_sitio=entry(3,1,cs=3)
        if editar and datos[6]: e_sitio.insert(0, datos[6])

        lbl(4,0,"Código POA *:"); e_poa=entry(4,1)
        if editar and datos[7]: e_poa.insert(0, datos[7])

        lbl(4,2,"Tipo de Actividad *:"); cb_act = combo(4,3,ACTIVIDADES_TFC)
        cb_act.set(datos[10] if editar and datos[10] else ACTIVIDADES_TFC[0])

        # Cargar técnicos desde BD
        lista_tecs = db.tecnicos_tfc_todos()
        dict_tecs = {t[1]: t[2] for t in lista_tecs}
        nombres_tecs = [t[1] for t in lista_tecs]
        if not nombres_tecs:
            nombres_tecs = ["Ing. Fernando Rafael Ardon Rodriguez"]
            dict_tecs = {"Ing. Fernando Rafael Ardon Rodriguez": "COLPROFORH N.- 0226"}

        lbl(5,0,"Técnico Responsable *:")
        cb_tecnico = combo(5,1,nombres_tecs,cs=3)
        cb_tecnico.set(datos[8] if editar and datos[8] else nombres_tecs[0])

        # ── Sección 2: Lugar y Tiempo ──────────────────────────────────────────
        sec(6,"2.  FECHA Y HORA")
        lbl(7,0,"Fecha *:"); e_fecha=entry(7,1)
        e_fecha.insert(0, datos[4] if editar else date.today().strftime("%d/%m/%Y"))

        lbl(7,2,"Hora *:"); e_hora=entry(7,3,w=100)
        e_hora.insert(0, datos[5] if editar else datetime.now().strftime("%H:%M"))

        # Fila 8: Coordenadas UTM
        lbl(8,0,"Zona UTM:")
        cb_utm_z = combo(8,1,["16N", "17N"])
        if editar and len(datos) > 16 and datos[16]:
            cb_utm_z.set(datos[16])
        else:
            cb_utm_z.set("16N")

        lbl(8,2,"Este (X) / Norte (Y):")
        f_coord = ctk.CTkFrame(scroll, fg_color="transparent")
        f_coord.grid(row=8, column=3, sticky="ew", padx=(0,12), pady=4)
        f_coord.columnconfigure(0, weight=1); f_coord.columnconfigure(1, weight=1)

        e_este = ctk.CTkEntry(f_coord, height=30, fg_color=BLANCO, border_color=V_OSC, text_color="#111", font=("Segoe UI", 13), placeholder_text="Este (m)")
        e_este.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        if editar and len(datos) > 17 and datos[17] is not None:
            e_este.insert(0, f"{datos[17]:.1f}")

        e_norte = ctk.CTkEntry(f_coord, height=30, fg_color=BLANCO, border_color=V_OSC, text_color="#111", font=("Segoe UI", 13), placeholder_text="Norte (m)")
        e_norte.grid(row=0, column=1, sticky="ew", padx=(2, 0))
        if editar and len(datos) > 18 and datos[18] is not None:
            e_norte.insert(0, f"{datos[18]:.1f}")

        # ── Sección 3: Contenido Técnico Forestal ──────────────────────────────
        sec(9,"3.  REGISTROS TÉCNICOS FORESTALES")
        lbl(10,0,"Volumen Cubicada (m³):"); e_vol=entry(10,1)
        e_vol.insert(0, f"{float(datos[12] or 0.0):.2f}" if editar else "0.00")

        lbl(11,0,"Detalles Técnicos *:")
        t_detalles = textbox(11,1,h=100)
        if editar and datos[11]: t_detalles.insert("1.0", datos[11])

        lbl(12,0,"Plagas e Incidencias:")
        t_plagas = textbox(12,1,h=80)
        if editar and datos[13]: t_plagas.insert("1.0", datos[13])

        lbl(13,0,"Mitigación Ambiental:")
        t_ambient = textbox(13,1,h=80)
        if editar and datos[14]: t_ambient.insert("1.0", datos[14])

        lbl(14,0,"Comentarios:")
        t_comentarios = textbox(14,1,h=60)
        if editar and datos[15]: t_comentarios.insert("1.0", datos[15])

        lbl(15,0,"Estado:"); cb_est = combo(15,1,ESTADOS_TFC)
        cb_est.set(datos[21] if editar and datos[21] else "Activo")

        # ── Sección 4: Organización Documental y Archivos Escaneados ──────────
        sec(16,"4.  ORGANIZACIÓN DOCUMENTAL Y ARCHIVOS ESCANEADOS")
        
        # Variables de ruta
        ruta_caso_var = tk.StringVar(value=datos[23] if editar and len(datos) > 23 and datos[23] else "")
        scan_pm_var = tk.StringVar(value=datos[24] if editar and len(datos) > 24 and datos[24] else "")
        scan_poa_var = tk.StringVar(value=datos[25] if editar and len(datos) > 25 and datos[25] else "")
        scan_res_var = tk.StringVar(value=datos[26] if editar and len(datos) > 26 and datos[26] else "")

        # Carpeta del caso
        lbl(17,0,"Carpeta del Caso:")
        f_folder = ctk.CTkFrame(scroll, fg_color="transparent")
        f_folder.grid(row=17, column=1, columnspan=3, sticky="ew", padx=(0,12), pady=4)
        f_folder.columnconfigure(0, weight=1)

        ent_folder = ctk.CTkEntry(f_folder, height=30, fg_color=BLANCO, border_color=V_OSC, text_color="#111", font=("Segoe UI", 12), textvariable=ruta_caso_var)
        ent_folder.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        
        # Si el registro no está activo, bloquear los campos
        registro_listo = editar and datos[21] in ["Archivada", "Anulada"]
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

        build_row_file(18, "Plan de Manejo Escaneado:", scan_pm_var)
        build_row_file(19, "POA Escaneado:", scan_poa_var)
        build_row_file(20, "Resolución ICF Escaneada:", scan_res_var)

        # ── Botones ───────────────────────────────────────────────────────────
        frm_btn = ctk.CTkFrame(dlg, fg_color=GRIS_F, height=58)
        frm_btn.pack(fill="x", side="bottom"); frm_btn.pack_propagate(False)
        ctk.CTkFrame(frm_btn, fg_color=V_CLR, height=1).pack(fill="x")

        btn_frame = ctk.CTkFrame(frm_btn, fg_color=GRIS_F)
        btn_frame.pack(pady=8)

        def guardar():
            num      = e_num.get().strip()
            fecha_v  = e_fecha.get().strip()
            hora_v   = e_hora.get().strip()
            sitio    = e_sitio.get().strip()
            poa      = e_poa.get().strip()
            detalles_t = t_detalles.get("1.0","end").strip()
            if not num or not fecha_v or not hora_v or not sitio or not poa or not detalles_t:
                messagebox.showwarning("SilvaDesk","Completa los campos requeridos (*)."); return
            
            try: folio_n = int(e_folio.get().strip())
            except: folio_n = db.bitacora_tfc_siguiente_folio()

            try: vol_n = float(e_vol.get().replace(",",".").strip())
            except: vol_n = 0.0

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
                    # Validar coordenadas dentro de Honduras
                    if not (12.9 <= lat_val <= 16.6) or not (-89.5 <= lon_val <= -83.1):
                        messagebox.showwarning("SilvaDesk", "Las coordenadas UTM convertidas quedan fuera de Honduras.")
                        return
                except ValueError:
                    messagebox.showwarning("SilvaDesk", "Las coordenadas UTM deben ser números válidos.")
                    return

            t_nom = cb_tecnico.get().strip()
            t_reg = dict_tecs.get(t_nom, "COLPROFORH N.- 0226")

            args = (
                num, folio_n, anio, fecha_v, hora_v, sitio, poa,
                t_nom, t_reg, cb_act.get(), detalles_t, vol_n,
                t_plagas.get("1.0","end").strip(), t_ambient.get("1.0","end").strip(),
                t_comentarios.get("1.0","end").strip(), zona_utm, este_val, norte_val,
                lat_val, lon_val, cb_est.get(),
                ruta_caso_var.get().strip(),
                scan_pm_var.get().strip(),
                scan_poa_var.get().strip(),
                scan_res_var.get().strip()
            )

            if editar: db.bitacora_tfc_editar(datos[0], *args)
            else:      db.bitacora_tfc_agregar(*args)
            self.app.set_status(f"Registro {num} {'actualizado' if editar else 'asentado'}.")
            dlg.destroy(); self._cargar_datos()

        def guardar_e_imprimir():
            guardar()
            filas = db.bitacora_tfc_todos()
            if filas:
                row = db.bitacora_tfc_por_id(filas[0][0])
                if row:
                    ruta = self._generar_pdf_bitacora(row)
                    if ruta and messagebox.askyesno("SilvaDesk",f"¿Abrir PDF de Bitácora ahora?\n{ruta}"):
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

    # ── Generar PDF ───────────────────────────────────────────────────────────
    def _generar_pdf_bitacora(self, row):
        from utils.pdf_bitacora_tfc import generar_pdf_bitacora
        base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "BitacorasTFC")
        os.makedirs(base, exist_ok=True)
        safe = "".join(c for c in f"Bitacora_{row[1]}" if c.isalnum() or c in "_-")
        ruta = os.path.join(base, f"{safe}.pdf")
        
        datos = {
            "num_bitacora":            row[1],
            "folio":               row[2],
            "anio":                row[3],
            "fecha":               row[4],
            "hora":                row[5],
            "sitio_predio":        row[6],
            "poa_codigo":          row[7],
            "tfc_nombre":          row[8],
            "tfc_registro":        row[9],
            "actividad_tipo":     row[10],
            "detalles_tecnicos":   row[11],
            "volumen_m3":          row[12],
            "plagas_observadas":   row[13],
            "cumplimiento_ambiental": row[14],
            "comentarios":         row[15],
            "scan_plan_manejo":        row[24] if len(row) > 24 else "",
            "scan_poa":                row[25] if len(row) > 25 else "",
            "scan_resolucion":         row[26] if len(row) > 26 else "",
            "estado":                  row[21],
        }
        return generar_pdf_bitacora(ruta, datos)

    def _administrar_tecnicos(self):
        dlg = ctk.CTkToplevel(self.parent)
        dlg.title("👥 Administración de Técnicos Asociados")
        dlg.geometry("520x460")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.configure(fg_color=GRIS_F)

        # Header
        hdr = ctk.CTkFrame(dlg, fg_color=V_OSC, corner_radius=0, height=50)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="👥  Técnicos Forestales Calificados (TFC)", font=("Segoe UI", 14, "bold"), text_color=BLANCO).pack(pady=12)

        # Contenedor principal
        frm = ctk.CTkFrame(dlg, fg_color=GRIS_F)
        frm.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Subframe izquierdo para listado
        f_list = ctk.CTkFrame(frm, fg_color=BLANCO, corner_radius=6, border_width=1, border_color="#C0D4EC")
        f_list.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Treeview de técnicos
        cols = ("Nombre", "Registro COLPROFORH")
        tree = ttk.Treeview(f_list, columns=cols, show="headings", selectmode="browse")
        tree.heading("Nombre", text="Nombre del Técnico")
        tree.heading("Registro COLPROFORH", text="N.° Registro")
        tree.column("Nombre", width=160)
        tree.column("Registro COLPROFORH", width=110)
        tree.pack(fill="both", expand=True, padx=4, pady=4)
        
        # Subframe derecho para formulario de agregar y botón de borrar
        f_ops = ctk.CTkFrame(frm, fg_color=GRIS_F)
        f_ops.pack(side="right", fill="y")
        
        lbl_add = ctk.CTkLabel(f_ops, text="Añadir Técnico", font=("Segoe UI", 12, "bold"), text_color=V_OSC)
        lbl_add.pack(anchor="w", pady=(0, 4))
        
        ent_nombre = ctk.CTkEntry(f_ops, placeholder_text="Nombre Técnico", width=180, font=("Segoe UI", 12), fg_color=BLANCO, border_color=V_MED, text_color="#111")
        ent_nombre.pack(pady=4)
        
        ent_registro = ctk.CTkEntry(f_ops, placeholder_text="N.° COLPROFORH", width=180, font=("Segoe UI", 12), fg_color=BLANCO, border_color=V_MED, text_color="#111")
        ent_registro.pack(pady=4)
        
        def cargar_tecnicos():
            tree.delete(*tree.get_children())
            rows = db.tecnicos_tfc_todos()
            for r in rows:
                tree.insert("", "end", iid=r[0], values=(r[1], r[2]))
                
        def agregar_tecnico():
            nom = ent_nombre.get().strip()
            reg = ent_registro.get().strip()
            if not nom or not reg:
                messagebox.showwarning("Campos vacíos", "Por favor escriba el nombre y el número de registro."); return
            db.tecnicos_tfc_agregar(nom, reg)
            ent_nombre.delete(0, tk.END)
            ent_registro.delete(0, tk.END)
            cargar_tecnicos()
            messagebox.showinfo("Técnico Agregado", f"Se registró a {nom} correctamente.")
            
        def eliminar_tecnico():
            sel = tree.selection()
            if not sel:
                messagebox.showinfo("Selección requerida", "Selecciona un técnico del listado para eliminarlo."); return
            t_id = int(sel[0])
            all_t = tree.get_children()
            if len(all_t) <= 1:
                messagebox.showerror("Error", "No se puede eliminar el único técnico registrado. Debe haber al menos uno para firmar las bitácoras."); return
            
            t_nom = tree.item(sel[0], "values")[0]
            if messagebox.askyesno("Confirmar", f"¿Desea eliminar a {t_nom} de la lista de técnicos asociados?\n\nEsta acción no afectará los registros históricos de bitácora ya guardados."):
                db.tecnicos_tfc_eliminar(t_id)
                cargar_tecnicos()
                
        btn_add = ctk.CTkButton(f_ops, text="➕ Agregar", command=agregar_tecnico, fg_color=V_MED, hover_color=V_OSC, text_color=BLANCO, font=("Segoe UI", 12, "bold"))
        btn_add.pack(fill="x", pady=6)
        
        btn_del = ctk.CTkButton(f_ops, text="🗑 Eliminar", command=eliminar_tecnico, fg_color="#8B2020", hover_color="#5C1515", text_color=BLANCO, font=("Segoe UI", 12, "bold"))
        btn_del.pack(fill="x", pady=20)
        
        btn_close = ctk.CTkButton(f_ops, text="Cerrar", command=dlg.destroy, fg_color="#888", hover_color="#666", text_color=BLANCO, font=("Segoe UI", 12))
        btn_close.pack(fill="x", side="bottom")
        
        cargar_tecnicos()
