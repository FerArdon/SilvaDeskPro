"""
tabs/contratos.py - Biblioteca de Contratos Forestales (Arancel COLPROFORH)
SilvaDesk Pro - SEDCAF / ICF Honduras
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from datetime import date, datetime
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

V_OSC  = "#1B5E20"
V_MED  = "#2E7D32"
BLANCO = "#FFFFFF"
GRIS_F = "#F2F5F0"

CONTRATOS_TIPOS = [
    "Elaboración de Plan de Manejo Forestal (PMF)",
    "Elaboración de Plan Operativo Anual (POA)",
    "Regencia Forestal (Servicios Mensuales)",
    "Inventario Forestal y Cubicaciones de Madera",
    "Servicios de Asesoría Técnica General y SIG",
    "Dictamen Técnico Pericial / Avalúo de Daños",
]

_PH = (
    "Ej: El CONSULTOR podrá contratar personal técnico auxiliar bajo su exclusiva "
    "responsabilidad, sin que ello genere relación laboral alguna con el PROPIETARIO."
)


class ContratosTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self._modo_edicion = False
        self._id_editando  = None

        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)

        self._paned = tk.PanedWindow(
            parent, orient=tk.HORIZONTAL, sashwidth=6,
            sashrelief="flat", bg="#C8E6C9"
        )
        self._paned.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        self._build_formulario()
        self._build_listado_contratos()
        self._cargar_contratos()

    # ------------------------------------------------------------------ Form
    def _build_formulario(self):
        pane_left = tk.Frame(self._paned, bg=GRIS_F)
        pane_left.rowconfigure(0, weight=1)
        pane_left.columnconfigure(0, weight=1)
        self._paned.add(pane_left, minsize=420, stretch="always")

        self.scroll = ctk.CTkScrollableFrame(pane_left, fg_color=GRIS_F, corner_radius=6)
        self.scroll.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        self.scroll.grid_columnconfigure(1, weight=1)

        hdr = ctk.CTkFrame(self.scroll, fg_color=V_OSC, corner_radius=6, height=40)
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        hdr.grid_propagate(False)
        ctk.CTkLabel(
            hdr, text="📝  Generador de Contratos de Servicios",
            font=("Segoe UI", 14, "bold"), text_color=BLANCO
        ).pack(side="left", padx=14, pady=8)

        def lbl(r, t):
            ctk.CTkLabel(
                self.scroll, text=t, font=("Segoe UI", 13),
                text_color="#333", anchor="e"
            ).grid(row=r, column=0, sticky="e", padx=(12, 6), pady=4)

        def ent(r, ph=""):
            e = ctk.CTkEntry(
                self.scroll, placeholder_text=ph, height=30,
                fg_color=BLANCO, border_color=V_OSC,
                text_color="#111", font=("Segoe UI", 13)
            )
            e.grid(row=r, column=1, sticky="ew", padx=(0, 12), pady=4)
            return e

        def sec(r, t):
            f = ctk.CTkFrame(self.scroll, fg_color=V_MED, corner_radius=4, height=30)
            f.grid(row=r, column=0, columnspan=2, sticky="ew", padx=6, pady=(12, 6))
            f.grid_propagate(False)
            ctk.CTkLabel(
                f, text="  " + t, font=("Segoe UI", 13, "bold"),
                text_color=BLANCO, anchor="w"
            ).pack(fill="both", expand=True, padx=8)

        # Sección 1
        sec(1, "1.  IDENTIFICACIÓN Y COMPARECIENTES")

        lbl(2, "Tipo de Actividad *:")
        self.cb_actividad = ctk.CTkComboBox(
            self.scroll, values=CONTRATOS_TIPOS, height=30,
            fg_color=BLANCO, text_color="#111", border_color=V_OSC,
            button_color=V_OSC, font=("Segoe UI", 13),
            dropdown_font=("Segoe UI", 13)
        )
        self.cb_actividad.set(CONTRATOS_TIPOS[0])
        self.cb_actividad.grid(row=2, column=1, sticky="ew", padx=(0, 12), pady=4)

        lbl(3, "Cliente / Propietario *:")
        self.e_cliente = ent(3, "Nombre Completo del Cliente")

        lbl(4, "RTN Cliente:")
        self.e_rtn_cliente = ent(4, "0000-0000-000000")

        lista_tecs   = db.tecnicos_tfc_todos()
        self.dict_tecs = {t[1]: t[2] for t in lista_tecs}
        nombres_tecs = [t[1] for t in lista_tecs]
        if not nombres_tecs:
            nombres_tecs = ["Ing. Fernando Rafael Ardon Rodriguez"]
            self.dict_tecs = {"Ing. Fernando Rafael Ardon Rodriguez": "COLPROFORH N.- 0226"}

        lbl(5, "Consultor Forestal *:")
        self.cb_consultor = ctk.CTkComboBox(
            self.scroll, values=nombres_tecs, height=30,
            fg_color=BLANCO, text_color="#111", border_color=V_OSC,
            button_color=V_OSC, font=("Segoe UI", 13),
            dropdown_font=("Segoe UI", 13)
        )
        self.cb_consultor.set(nombres_tecs[0])
        self.cb_consultor.grid(row=5, column=1, sticky="ew", padx=(0, 12), pady=4)

        # Sección 2
        sec(6, "2.  LOCALIZACIÓN DEL TRABAJO")

        lbl(7, "Sitio / Predio *:")
        self.e_predio = ent(7, "Nombre de la Finca/Propiedad")

        lbl(8, "Municipio:")
        self.e_municipio = ent(8, "Municipio donde se ubica")

        lbl(9, "Departamento:")
        self.e_depto = ent(9, "Departamento")
        self.e_depto.insert(0, "Francisco Morazán")

        # Sección 3
        sec(10, "3.  CONDICIONES ECONÓMICAS Y PLAZOS")

        lbl(11, "Monto Total (L.) *:")
        self.e_monto = ent(11, "Honorarios Pactados")

        lbl(12, "Forma de Pago:")
        self.e_forma_pago = ent(12, "Ej. 50% anticipo, 50% al entregar")
        self.e_forma_pago.insert(0, "50% de anticipo y 50% a la entrega del informe final")

        lbl(13, "Plazo de Ejecución:")
        self.e_plazo = ent(13, "Ej. 30 días calendario")
        self.e_plazo.insert(0, "45 días calendario")

        lbl(14, "Fecha de Firma *:")
        self.e_fecha = ent(14, "DD/MM/AAAA")
        self.e_fecha.insert(0, date.today().strftime("%d/%m/%Y"))

        # Sección 4: Cláusulas adicionales
        sec(15, "4.  CLÁUSULAS ADICIONALES O ESPECIALES  (opcional)")

        ctk.CTkLabel(
            self.scroll,
            text="  Se insertará como CLÁUSULA OCTAVA. Las cláusulas estándar (1ª–7ª) siempre se incluyen.",
            font=("Segoe UI", 11, "italic"), text_color="#555", anchor="w"
        ).grid(row=16, column=0, columnspan=2, sticky="w", padx=12, pady=(0, 0))

        ctk.CTkLabel(
            self.scroll,
            text='  Para EXCLUIR una cláusula estándar, indíquelo aquí (ej: "Se omite la Cláusula Quinta").',
            font=("Segoe UI", 11, "italic"), text_color="#555", anchor="w"
        ).grid(row=16, column=0, columnspan=2, sticky="w", padx=12, pady=(16, 4))

        self.t_clausulas = ctk.CTkTextbox(
            self.scroll, height=100,
            fg_color=BLANCO, border_color=V_MED, border_width=1,
            text_color="#AAAAAA", font=("Segoe UI", 13)
        )
        self.t_clausulas.grid(row=17, column=0, columnspan=2,
                              sticky="ew", padx=12, pady=(0, 6))
        self.t_clausulas.insert("1.0", _PH)

        def _fi(e):
            if self.t_clausulas.cget("text_color") == "#AAAAAA":
                self.t_clausulas.delete("1.0", "end")
                self.t_clausulas.configure(text_color="#111111")

        def _fo(e):
            if not self.t_clausulas.get("1.0", "end").strip():
                self.t_clausulas.delete("1.0", "end")
                self.t_clausulas.insert("1.0", _PH)
                self.t_clausulas.configure(text_color="#AAAAAA")

        self.t_clausulas.bind("<FocusIn>", _fi)
        self.t_clausulas.bind("<FocusOut>", _fo)

        self.btn_generar = ctk.CTkButton(
            self.scroll, text="💾📄  Generar Contrato y Guardar",
            command=self._generar_contrato,
            fg_color=V_OSC, hover_color="#0d3f11",
            text_color=BLANCO, font=("Segoe UI", 13, "bold"), height=38
        )
        self.btn_generar.grid(row=18, column=0, columnspan=2,
                              pady=(6, 4), padx=12, sticky="ew")

        self.btn_cancelar = ctk.CTkButton(
            self.scroll, text="✖  Cancelar Edición",
            command=self._cancelar_edicion,
            fg_color="#8B2020", hover_color="#5C1515",
            text_color=BLANCO, font=("Segoe UI", 12), height=30
        )
        # oculto hasta activar modo edición

    # ------------------------------------------------------------------ List
    def _build_listado_contratos(self):
        pane_right = tk.Frame(self._paned, bg=GRIS_F)
        pane_right.rowconfigure(1, weight=1)
        pane_right.columnconfigure(0, weight=1)
        self._paned.add(pane_right, minsize=420, stretch="always")

        tb = ctk.CTkFrame(pane_right, fg_color=V_MED, corner_radius=6, height=44)
        tb.grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        tb.grid_propagate(False)
        tb.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tb, text="👥  Contratos Forestales Registrados",
            font=("Segoe UI", 13, "bold"), text_color=BLANCO
        ).grid(row=0, column=0, sticky="w", padx=12, pady=6)

        ctk.CTkButton(
            tb, text="✏️ Editar", command=self._editar_contrato_sel,
            width=90, height=30, fg_color="#1565C0", hover_color="#0D47A1",
            text_color=BLANCO, font=("Segoe UI", 12, "bold")
        ).grid(row=0, column=1, padx=4, pady=6)

        ctk.CTkButton(
            tb, text="👁 Abrir PDF", command=self._abrir_pdf_sel,
            width=100, height=30, fg_color=V_OSC, hover_color="#0d3f11",
            text_color=BLANCO, font=("Segoe UI", 12, "bold")
        ).grid(row=0, column=2, padx=4, pady=6)

        ctk.CTkButton(
            tb, text="📄 Word", command=self._exportar_word_sel,
            width=80, height=30, fg_color="#6A1B9A", hover_color="#4A148C",
            text_color=BLANCO, font=("Segoe UI", 12, "bold")
        ).grid(row=0, column=3, padx=4, pady=6)

        ctk.CTkButton(
            tb, text="🗑 Eliminar", command=self._eliminar_contrato_sel,
            width=90, height=30, fg_color="#8B2020", hover_color="#5C1515",
            text_color=BLANCO, font=("Segoe UI", 12, "bold")
        ).grid(row=0, column=4, padx=6, pady=6)

        cols = ("ID", "Predio", "Actividad / Tipo", "Cliente", "Monto Total", "Fecha Firma")
        self.tree_contratos = ttk.Treeview(
            pane_right, columns=cols, show="headings", selectmode="browse"
        )
        for col, w in zip(cols, [40, 110, 150, 120, 90, 90]):
            self.tree_contratos.heading(col, text=col)
            self.tree_contratos.column(col, width=w, minwidth=35)

        sb_y = ttk.Scrollbar(pane_right, orient="vertical",
                             command=self.tree_contratos.yview)
        sb_x = ttk.Scrollbar(pane_right, orient="horizontal",
                             command=self.tree_contratos.xview)
        self.tree_contratos.configure(yscrollcommand=sb_y.set,
                                      xscrollcommand=sb_x.set)
        self.tree_contratos.grid(row=1, column=0, sticky="nsew",
                                 padx=(6, 0), pady=(0, 6))
        sb_y.grid(row=1, column=1, sticky="ns", pady=(0, 6))
        sb_x.grid(row=2, column=0, sticky="ew", padx=(6, 0))
        self.tree_contratos.bind("<Double-1>", lambda e: self._abrir_pdf_sel())

    # ------------------------------------------------------------------ CRUD
    def _cargar_contratos(self):
        self.tree_contratos.delete(*self.tree_contratos.get_children())
        for c in db.contratos_todos():
            c_id, predio, act, cliente, monto, fecha = c[0],c[1],c[2],c[3],c[4],c[5]
            self.tree_contratos.insert(
                "", "end", iid=c_id,
                values=(c_id, predio, act, cliente,
                        f"L. {float(monto or 0):,.2f}", fecha)
            )

    def _clausulas_val(self):
        if self.t_clausulas.cget("text_color") == "#AAAAAA":
            return ""
        return self.t_clausulas.get("1.0", "end").strip()

    def _generar_contrato(self):
        actividad       = self.cb_actividad.get()
        cliente         = self.e_cliente.get().strip()
        rtn_c           = self.e_rtn_cliente.get().strip()
        predio          = self.e_predio.get().strip()
        municipio       = self.e_municipio.get().strip()
        depto           = self.e_depto.get().strip()
        monto_str       = (self.e_monto.get().strip()
                           .replace("L.", "").replace("L", "")
                           .replace(",", "").strip())
        forma_p         = self.e_forma_pago.get().strip()
        plazo           = self.e_plazo.get().strip()
        fecha_firma     = self.e_fecha.get().strip()
        clausulas_extra = self._clausulas_val()

        if not cliente or not predio or not monto_str or not fecha_firma:
            messagebox.showwarning(
                "Campos obligatorios",
                "Complete todos los campos requeridos con asterisco (*)."
            )
            return

        try:
            monto = float(monto_str)
            if monto <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Monto no válido",
                                 "Introduzca un monto contractual válido.")
            return

        try:
            datetime.strptime(fecha_firma, "%d/%m/%Y")
        except ValueError:
            messagebox.showerror("Fecha no válida",
                                 "La fecha debe tener formato DD/MM/AAAA.")
            return

        # Buscar carpeta del caso
        conn = db.get_conn()
        cur  = conn.cursor()
        cur.execute(
            "SELECT ruta_carpeta_caso FROM bitacora_tfc "
            "WHERE sitio_predio=? AND ruta_carpeta_caso IS NOT NULL "
            "AND ruta_carpeta_caso != '' LIMIT 1", (predio,)
        )
        r = cur.fetchone()
        carpeta_def = r[0] if r else ""
        if not carpeta_def:
            cur.execute(
                "SELECT ruta_carpeta_caso FROM protocolo "
                "WHERE lugar=? AND ruta_carpeta_caso IS NOT NULL "
                "AND ruta_carpeta_caso != '' LIMIT 1", (predio,)
            )
            r = cur.fetchone()
            carpeta_def = r[0] if r else ""
        conn.close()

        safe_name = "".join(
            ch for ch in f"Contrato_{cliente}_{predio}"
            if ch.isalnum() or ch in " _-"
        ).strip().replace(" ", "_")

        # Ruta del PDF
        if self._modo_edicion:
            conn2 = db.get_conn()
            cur2  = conn2.cursor()
            cur2.execute("SELECT ruta_pdf FROM contratos_tfc WHERE id=?",
                         (self._id_editando,))
            row2 = cur2.fetchone()
            conn2.close()
            ruta_anterior = row2[0] if row2 else ""

            if ruta_anterior and os.path.exists(ruta_anterior):
                sobrescribir = messagebox.askyesno(
                    "Sobreescribir PDF",
                    f"¿Desea sobreescribir el PDF original?\n\n{ruta_anterior}\n\nPresione NO para elegir nueva ruta."
                )
                if sobrescribir:
                    ruta_pdf = ruta_anterior
                else:
                    ruta_pdf = filedialog.asksaveasfilename(
                        title="Guardar Contrato Actualizado",
                        initialfile=f"{safe_name}_v2.pdf",
                        filetypes=[("Documentos PDF", "*.pdf")],
                        defaultextension=".pdf"
                    )
                    if not ruta_pdf:
                        return
            else:
                initial_dir = (carpeta_def if carpeta_def
                               and os.path.exists(carpeta_def) else os.getcwd())
                ruta_pdf = filedialog.asksaveasfilename(
                    title="Guardar Contrato Actualizado",
                    initialdir=initial_dir,
                    initialfile=f"{safe_name}.pdf",
                    filetypes=[("Documentos PDF", "*.pdf")],
                    defaultextension=".pdf"
                )
                if not ruta_pdf:
                    return
        else:
            initial_dir = (carpeta_def if carpeta_def
                           and os.path.exists(carpeta_def) else os.getcwd())
            ruta_pdf = filedialog.asksaveasfilename(
                title="Guardar Contrato de Servicios Forestales",
                initialdir=initial_dir,
                initialfile=f"{safe_name}.pdf",
                filetypes=[("Documentos PDF", "*.pdf")],
                defaultextension=".pdf"
            )
            if not ruta_pdf:
                return

        # Generar PDF
        try:
            from utils.pdf_contrato import generar_pdf_contrato
            conf = db.config_obtener()
            consultor_nom = self.cb_consultor.get()
            consultor_reg = self.dict_tecs.get(consultor_nom, "")

            datos_contrato = {
                "consultor_nombre":      consultor_nom,
                "consultor_registro":    consultor_reg,
                "empresa_nombre":        conf[1],
                "empresa_direccion":     conf[5],
                "empresa_telefono":      conf[6],
                "cliente_nombre":        cliente,
                "cliente_rtn":           rtn_c,
                "predio":                predio,
                "municipio":             municipio,
                "departamento":          depto,
                "actividad_tipo":        actividad,
                "monto_total":           monto,
                "forma_pago":            forma_p,
                "plazo_ejecucion":       plazo,
                "fecha_firma":           fecha_firma,
                "clausulas_adicionales": clausulas_extra,
            }

            generar_pdf_contrato(ruta_pdf, datos_contrato)

            if self._modo_edicion:
                db.contratos_editar(
                    self._id_editando,
                    predio, actividad, cliente, monto, fecha_firma,
                    ruta_pdf, consultor_nom, consultor_reg, clausulas_extra,
                    rtn_c, municipio, depto, forma_p, plazo
                )
                msg_ok = "Contrato actualizado y PDF regenerado."
            else:
                db.contratos_agregar(
                    predio, actividad, cliente, monto, fecha_firma,
                    ruta_pdf, consultor_nom, consultor_reg, clausulas_extra,
                    rtn_c, municipio, depto, forma_p, plazo
                )
                msg_ok = "Contrato generado y registrado en el sistema."

            if carpeta_def and os.path.exists(carpeta_def):
                dest = os.path.join(carpeta_def, f"{safe_name}.pdf")
                if os.path.abspath(ruta_pdf) != os.path.abspath(dest):
                    import shutil
                    os.makedirs(carpeta_def, exist_ok=True)
                    shutil.copy2(ruta_pdf, dest)

            messagebox.showinfo("Contrato",
                                f"{msg_ok}\n\nArchivo:\n{ruta_pdf}")
            self._limpiar_formulario()
            self._cargar_contratos()

            if messagebox.askyesno("Abrir documento",
                                   "¿Desea abrir el contrato PDF ahora?"):
                os.startfile(ruta_pdf)

            self.app.set_status(
                f"Contrato forestal guardado para {cliente} en {predio}"
            )

        except Exception as ex:
            messagebox.showerror("Error de generación",
                                 f"No se pudo generar el contrato:\n{ex}")

    # ------------------------------------------------------------------ Edit
    def _editar_contrato_sel(self):
        sel = self.tree_contratos.selection()
        if not sel:
            messagebox.showinfo("Selección requerida",
                                "Seleccione un contrato del listado para editar.")
            return

        c_id     = int(sel[0])
        contrato = next((c for c in db.contratos_todos() if c[0] == c_id), None)
        if not contrato:
            messagebox.showerror("Error", "No se encontró el contrato.")
            return

        # contratos_todos: [0]id [1]predio [2]act [3]cliente [4]monto
        #  [5]fecha [6]ruta_pdf [7]creado [8]consul_nom [9]consul_reg
        #  [10]clausulas [11]cliente_rtn [12]municipio [13]depto
        #  [14]forma_pago [15]plazo
        row = contrato
        _, predio, act, cliente, monto, fecha = row[0], row[1], row[2], row[3], row[4], row[5]
        consul_nom  = row[8]  if len(row) > 8  else ""
        clausulas   = row[10] if len(row) > 10 else ""
        cli_rtn     = row[11] if len(row) > 11 else ""
        municipio   = row[12] if len(row) > 12 else ""
        depto       = row[13] if len(row) > 13 else ""
        forma_pago  = row[14] if len(row) > 14 else ""
        plazo       = row[15] if len(row) > 15 else ""

        if act in CONTRATOS_TIPOS:
            self.cb_actividad.set(act)

        for widget, val in [
            (self.e_cliente,     cliente    or ""),
            (self.e_rtn_cliente, cli_rtn    or ""),
            (self.e_predio,      predio     or ""),
            (self.e_municipio,   municipio  or ""),
            (self.e_depto,       depto      or "Francisco Morazán"),
            (self.e_monto,       str(monto  or "")),
            (self.e_forma_pago,  forma_pago or ""),
            (self.e_plazo,       plazo      or ""),
            (self.e_fecha,       fecha      or date.today().strftime("%d/%m/%Y")),
        ]:
            widget.delete(0, tk.END)
            widget.insert(0, val)

        if consul_nom and consul_nom in self.dict_tecs:
            self.cb_consultor.set(consul_nom)

        self.t_clausulas.configure(text_color="#111111")
        self.t_clausulas.delete("1.0", "end")
        if clausulas and clausulas.strip():
            self.t_clausulas.insert("1.0", clausulas.strip())
        else:
            self.t_clausulas.insert("1.0", _PH)
            self.t_clausulas.configure(text_color="#AAAAAA")

        self._modo_edicion = True
        self._id_editando  = c_id
        self.btn_generar.configure(
            text="🔄📄  Actualizar Contrato y Regenerar PDF"
        )
        self.btn_cancelar.grid(row=19, column=0, columnspan=2,
                               pady=(0, 12), padx=12, sticky="ew")
        self.app.set_status(
            f"Modo edición: Contrato ID {c_id} — {cliente} | {predio}"
        )

    def _cancelar_edicion(self):
        self._limpiar_formulario()
        self.app.set_status("Modo edición cancelado.")

    def _limpiar_formulario(self):
        self._modo_edicion = False
        self._id_editando  = None
        self.btn_generar.configure(text="💾📄  Generar Contrato y Guardar")
        self.btn_cancelar.grid_remove()
        for w in (self.e_cliente, self.e_rtn_cliente,
                  self.e_predio, self.e_municipio, self.e_monto):
            w.delete(0, tk.END)
        self.t_clausulas.delete("1.0", "end")
        self.t_clausulas.insert("1.0", _PH)
        self.t_clausulas.configure(text_color="#AAAAAA")

    # ------------------------------------------------------------------ PDF
    def _abrir_pdf_sel(self):
        sel = self.tree_contratos.selection()
        if not sel:
            messagebox.showinfo("Selección requerida",
                                "Seleccione un contrato para ver su PDF.")
            return
        c_id = int(sel[0])
        conn = db.get_conn()
        cur  = conn.cursor()
        cur.execute("SELECT ruta_pdf FROM contratos_tfc WHERE id=?", (c_id,))
        r = cur.fetchone()
        conn.close()
        if r and r[0] and os.path.exists(r[0]):
            os.startfile(r[0])
        else:
            messagebox.showerror(
                "Archivo no encontrado",
                "El PDF del contrato no existe en la ruta registrada o fue movido."
            )

    def _exportar_word_sel(self):
        sel = self.tree_contratos.selection()
        if not sel:
            messagebox.showinfo("Selección requerida",
                                "Seleccione un contrato del listado para exportar a Word.")
            return

        c_id     = int(sel[0])
        contrato = next((c for c in db.contratos_todos() if c[0] == c_id), None)
        if not contrato:
            messagebox.showerror("Error", "No se encontró el contrato.")
            return

        row        = contrato
        predio     = row[1]
        actividad  = row[2]
        cliente    = row[3]
        monto      = row[4]
        fecha      = row[5]
        consul_nom = row[8]  if len(row) > 8  else ""
        clausulas  = row[10] if len(row) > 10 else ""
        cli_rtn    = row[11] if len(row) > 11 else ""
        municipio  = row[12] if len(row) > 12 else ""
        depto      = row[13] if len(row) > 13 else ""
        forma_pago = row[14] if len(row) > 14 else ""
        plazo      = row[15] if len(row) > 15 else ""

        consul_reg = self.dict_tecs.get(consul_nom, "")
        conf = db.config_obtener()
        datos = {
            "consultor_nombre":      consul_nom or "Ing. Fernando Rafael Ardon Rodriguez",
            "consultor_registro":    consul_reg or "COLPROFORH N.- 0226",
            "empresa_nombre":        conf[1] if conf else "SEDCAF",
            "cliente_nombre":        cliente,
            "cliente_rtn":           cli_rtn,
            "predio":                predio,
            "municipio":             municipio,
            "departamento":          depto,
            "actividad_tipo":        actividad,
            "monto_total":           float(monto or 0),
            "forma_pago":            forma_pago,
            "plazo_ejecucion":       plazo,
            "fecha_firma":           fecha,
            "clausulas_adicionales": clausulas,
        }

        safe_name = "".join(
            ch for ch in f"Contrato_{cliente}_{predio}"
            if ch.isalnum() or ch in " _-"
        ).strip().replace(" ", "_")

        ruta_word = filedialog.asksaveasfilename(
            title="Exportar Contrato a Word",
            initialfile=f"{safe_name}.docx",
            filetypes=[("Documento Word", "*.docx")],
            defaultextension=".docx"
        )
        if not ruta_word:
            return

        try:
            from utils.word_contrato import generar_word_contrato
            generar_word_contrato(ruta_word, datos)
            messagebox.showinfo("Exportación exitosa",
                                f"Contrato exportado a Word:\n{ruta_word}")
            if messagebox.askyesno("Abrir documento",
                                   "¿Desea abrir el archivo Word ahora?"):
                os.startfile(ruta_word)
        except Exception as ex:
            messagebox.showerror("Error al exportar",
                                 f"No se pudo generar el archivo Word:\n{ex}")

    def _eliminar_contrato_sel(self):
        sel = self.tree_contratos.selection()
        if not sel:
            messagebox.showinfo("Selección requerida",
                                "Seleccione un contrato para eliminar.")
            return
        c_id   = int(sel[0])
        c_vals = self.tree_contratos.item(c_id, "values")
        c_act  = c_vals[2]
        c_cli  = c_vals[3]
        if messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Eliminar contrato de {c_act} para {c_cli}?\n\nNOTA: No se borrará el PDF del disco."
        ):
            try:
                db.contratos_eliminar(c_id)
                self._cargar_contratos()
                self.app.set_status(f"Contrato ID {c_id} eliminado.")
            except Exception as ex:
                messagebox.showerror("Error al eliminar", f"No se pudo eliminar el contrato: {str(ex)}")
