"""
tabs/finanzas.py – Módulo de Control de Finanzas, Facturación y Pagos
SilvaDesk Pro · SEDCAF / ICF / FEMA Honduras
"""
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from datetime import date, datetime
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

# Colores de finanzas (Azul-Gris / Azul transacciones)
V_OSC = "#0D47A1"      # Azul marino oscuro
V_MED = "#1976D2"      # Azul medio
V_CLR = "#E3F2FD"      # Azul claro
BLANCO = "#FFFFFF"
GRIS_F = "#F2F5F0"
GRIS_B = "#DDDDDD"

METODOS_PAGO = ["Transferencia Bancaria", "Depósito Bancario", "Efectivo", "Cheque"]

class FinanzasTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.selected_factura_id = None
        
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)
        
        # PanedWindow para dividir la lista de facturas de la sección de pagos
        self._paned = tk.PanedWindow(
            parent,
            orient=tk.HORIZONTAL,
            sashwidth=6,
            sashrelief="flat",
            bg="#BBDEFB"
        )
        self._paned.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        
        self._build_historial_facturas()
        self._build_panel_pagos()
        
        self._cargar_facturas()

    # ── panel Izquierdo: Historial de Facturas Emitidas ────────────────────────
    def _build_historial_facturas(self):
        pane_left = tk.Frame(self._paned, bg=GRIS_F)
        pane_left.rowconfigure(1, weight=1)
        pane_left.columnconfigure(0, weight=1)
        self._paned.add(pane_left, minsize=420, stretch="always")
        
        # Toolbar superior
        tb = ctk.CTkFrame(pane_left, fg_color=V_MED, corner_radius=6, height=44)
        tb.grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        tb.grid_propagate(False)
        tb.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(tb, text="🧾  Historial de Facturas y Saldos", font=("Segoe UI", 13, "bold"), text_color=BLANCO).grid(row=0, column=0, sticky="w", padx=12, pady=6)
        
        self.btn_refresh = ctk.CTkButton(tb, text="🔄 Actualizar", command=self._cargar_facturas, width=100, height=30, fg_color=V_OSC, hover_color="#002171", text_color=BLANCO, font=("Segoe UI", 12, "bold"))
        self.btn_refresh.grid(row=0, column=1, padx=6, pady=6)
        
        # Tabla de facturas
        cols = ("ID", "Factura No.", "Fecha", "Cliente", "Total", "Pagado", "Saldo", "Estado")
        self.tree_facturas = ttk.Treeview(pane_left, columns=cols, show="headings", selectmode="browse")
        widths = [40, 90, 80, 150, 90, 90, 90, 90]
        for col, w in zip(cols, widths):
            self.tree_facturas.heading(col, text=col)
            self.tree_facturas.column(col, width=w, minwidth=35)
            
        sb_y = ttk.Scrollbar(pane_left, orient="vertical", command=self.tree_facturas.yview)
        sb_x = ttk.Scrollbar(pane_left, orient="horizontal", command=self.tree_facturas.xview)
        self.tree_facturas.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
        
        self.tree_facturas.grid(row=1, column=0, sticky="nsew", padx=(6, 0), pady=(0, 6))
        sb_y.grid(row=1, column=1, sticky="ns", pady=(0, 6))
        sb_x.grid(row=2, column=0, sticky="ew", padx=(6, 0))
        
        self.tree_facturas.bind("<<TreeviewSelect>>", self._on_factura_seleccionada)
        
        # Tags de estilos para estados de cobro
        self.tree_facturas.tag_configure("pagada", background="#E8F5E9")
        self.tree_facturas.tag_configure("parcial", background="#FFF3E0")
        self.tree_facturas.tag_configure("pendiente", background="#FFEBEE")
        self.tree_facturas.tag_configure("anulada", background="#EEEEEE", foreground="#999")

    # ── panel Derecho: Registrar Pagos y Ver Abonos ──────────────────────────
    def _build_panel_pagos(self):
        pane_right = tk.Frame(self._paned, bg=GRIS_F)
        pane_right.rowconfigure(0, weight=1)
        pane_right.columnconfigure(0, weight=1)
        self._paned.add(pane_right, minsize=420, stretch="always")
        
        self.scroll_pagos = ctk.CTkScrollableFrame(pane_right, fg_color=GRIS_F, corner_radius=6)
        self.scroll_pagos.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        self.scroll_pagos.grid_columnconfigure(1, weight=1)
        
        # Header del panel
        hdr = ctk.CTkFrame(self.scroll_pagos, fg_color=V_OSC, corner_radius=6, height=40)
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        hdr.grid_propagate(False)
        ctk.CTkLabel(hdr, text="💵  Detalle de Pagos y Abonos", font=("Segoe UI", 14, "bold"), text_color=BLANCO).pack(side="left", padx=14, pady=8)
        
        # Datos del cliente / saldo
        def lbl(r, t): ctk.CTkLabel(self.scroll_pagos, text=t, font=("Segoe UI", 13), text_color="#333", anchor="e").grid(row=r, column=0, sticky="e", padx=(12, 6), pady=4)
        def ent(r, ph="", w=None):
            e = ctk.CTkEntry(self.scroll_pagos, placeholder_text=ph, height=30, fg_color=BLANCO, border_color=V_OSC, text_color="#111", width=w or 200, font=("Segoe UI", 13))
            e.grid(row=r, column=1, sticky="ew", padx=(0, 12), pady=4)
            return e
            
        def sec(r, t):
            f = ctk.CTkFrame(self.scroll_pagos, fg_color=V_MED, corner_radius=4, height=30)
            f.grid(row=r, column=0, columnspan=2, sticky="ew", padx=6, pady=(12, 6))
            f.grid_propagate(False)
            ctk.CTkLabel(f, text=f"  {t}", font=("Segoe UI", 13, "bold"), text_color=BLANCO, anchor="w").pack(fill="both", expand=True, padx=8)

        # 1. Resumen de saldos
        sec(1, "1.  SITUACIÓN FINANCIERA DE LA FACTURA")
        
        lbl(2, "Factura seleccionada:")
        self.lbl_fact_sel = ctk.CTkLabel(self.scroll_pagos, text="Ninguna factura seleccionada", font=("Segoe UI", 13, "bold"), text_color=V_OSC, anchor="w")
        self.lbl_fact_sel.grid(row=2, column=1, sticky="w", padx=(0, 12))
        
        lbl(3, "Cliente:")
        self.lbl_cli_sel = ctk.CTkLabel(self.scroll_pagos, text="-", font=("Segoe UI", 13), text_color="#333", anchor="w")
        self.lbl_cli_sel.grid(row=3, column=1, sticky="w", padx=(0, 12))
        
        lbl(4, "Total Factura:")
        self.lbl_total_sel = ctk.CTkLabel(self.scroll_pagos, text="L. 0.00", font=("Segoe UI", 14, "bold"), text_color="#111", anchor="w")
        self.lbl_total_sel.grid(row=4, column=1, sticky="w", padx=(0, 12))
        
        lbl(5, "Total Cobrado:")
        self.lbl_cobrado_sel = ctk.CTkLabel(self.scroll_pagos, text="L. 0.00", font=("Segoe UI", 13, "bold"), text_color="#2E7D32", anchor="w")
        self.lbl_cobrado_sel.grid(row=5, column=1, sticky="w", padx=(0, 12))
        
        lbl(6, "Saldo Pendiente:")
        self.lbl_saldo_sel = ctk.CTkLabel(self.scroll_pagos, text="L. 0.00", font=("Segoe UI", 14, "bold"), text_color="#C0392B", anchor="w")
        self.lbl_saldo_sel.grid(row=6, column=1, sticky="w", padx=(0, 12))

        # 2. Registrar Abono
        sec(7, "2.  REGISTRAR NUEVO ABONO / PAGO")
        
        lbl(8, "Monto Abono (L.) *:")
        self.e_monto = ent(8, "Monto en Lempiras")
        
        lbl(9, "Fecha Pago *:")
        self.e_fecha = ent(9, "DD/MM/AAAA")
        self.e_fecha.insert(0, date.today().strftime("%d/%m/%Y"))
        
        lbl(10, "Método de Pago:")
        self.cb_metodo = ctk.CTkComboBox(self.scroll_pagos, values=METODOS_PAGO, height=30, fg_color=BLANCO, text_color="#111", border_color=V_OSC, button_color=V_OSC, font=("Segoe UI", 13), dropdown_font=("Segoe UI", 13))
        self.cb_metodo.set(METODOS_PAGO[0])
        self.cb_metodo.grid(row=10, column=1, sticky="ew", padx=(0, 12), pady=4)
        
        lbl(11, "No. Comprobante:")
        self.e_referencia = ent(11, "Ref/Transferencia/Cheque")
        
        self.btn_guardar_pago = ctk.CTkButton(self.scroll_pagos, text="💾  Registrar Abono", command=self._registrar_abono, fg_color=V_OSC, hover_color="#002171", text_color=BLANCO, font=("Segoe UI", 13, "bold"), height=36)
        self.btn_guardar_pago.grid(row=12, column=0, columnspan=2, pady=12, padx=12, sticky="ew")

        # 3. Historial de abonos registrados
        sec(13, "3.  HISTORIAL DE ABONOS RECIBIDOS")
        
        # Tabla de historial
        cols_h = ("Fecha", "Monto", "Método", "Comprobante")
        self.tree_abonos = ttk.Treeview(self.scroll_pagos, columns=cols_h, show="headings", height=4)
        for col, w in zip(cols_h, [90, 100, 120, 100]):
            self.tree_abonos.heading(col, text=col)
            self.tree_abonos.column(col, width=w, minwidth=40)
        self.tree_abonos.grid(row=14, column=0, columnspan=2, sticky="ew", padx=6, pady=4)
        
        self.btn_eliminar_abono = ctk.CTkButton(self.scroll_pagos, text="🗑 Quitar Abono Seleccionado", command=self._eliminar_abono_sel, fg_color="#8B2020", hover_color="#5C1515", text_color=BLANCO, font=("Segoe UI", 12), height=26)
        self.btn_eliminar_abono.grid(row=15, column=0, columnspan=2, sticky="e", padx=6, pady=2)

    # ── Cargar Facturas de la BD ────────────────────────────────────────────────
    def _cargar_facturas(self):
        self.tree_facturas.delete(*self.tree_facturas.get_children())
        self.selected_factura_id = None
        self._limpiar_detalles()
        
        filas = db.facturas_todos()
        for f in filas:
            # f: id, num_factura, fecha, cliente_nombre, total, ruta_pdf, estado
            fac_id, num, fec, cli, total, pdf_path, est = f
            
            # Obtener pagos para calcular saldos
            pagos = db.pagos_por_factura(fac_id)
            total_pagado = sum(float(p[2] or 0.0) for p in pagos)
            saldo = float(total or 0.0) - total_pagado
            
            # Formatear
            s_total = f"L. {float(total or 0.0):,.2f}"
            s_pagado = f"L. {total_pagado:,.2f}"
            s_saldo = f"L. {max(0.0, saldo):,.2f}"
            
            # Determinar estado de cobro
            if est == "ANULADA":
                est_cobro = "ANULADA"
                tag = "anulada"
            elif saldo <= 0.01:
                est_cobro = "Pagada"
                tag = "pagada"
            elif total_pagado > 0:
                est_cobro = "Parcial"
                tag = "parcial"
            else:
                est_cobro = "Pendiente"
                tag = "pendiente"
                
            self.tree_facturas.insert("", "end", iid=fac_id, values=(fac_id, num, fec, cli, s_total, s_pagado, s_saldo, est_cobro), tags=(tag,))

    # ── Evento factura seleccionada ─────────────────────────────────────────────
    def _on_factura_seleccionada(self, event):
        sel = self.tree_facturas.selection()
        if not sel:
            return
        self.selected_factura_id = int(sel[0])
        
        # Leer datos de la fila de la tabla
        item_vals = self.tree_facturas.item(self.selected_factura_id, "values")
        fac_num = item_vals[1]
        cli_nom = item_vals[3]
        total_str = item_vals[4]
        pagado_str = item_vals[5]
        saldo_str = item_vals[6]
        estado_fact = item_vals[7]
        
        # Mostrar en panel
        self.lbl_fact_sel.configure(text=fac_num)
        self.lbl_cli_sel.configure(text=cli_nom)
        self.lbl_total_sel.configure(text=total_str)
        self.lbl_cobrado_sel.configure(text=pagado_str)
        self.lbl_saldo_sel.configure(text=saldo_str)
        
        # Bloquear registro si la factura está anulada
        if estado_fact == "ANULADA":
            self.btn_guardar_pago.configure(state="disabled")
            self.e_monto.configure(state="disabled")
            self.e_fecha.configure(state="disabled")
            self.cb_metodo.configure(state="disabled")
            self.e_referencia.configure(state="disabled")
            self.btn_eliminar_abono.configure(state="disabled")
        else:
            self.btn_guardar_pago.configure(state="normal")
            self.e_monto.configure(state="normal")
            self.e_fecha.configure(state="normal")
            self.cb_metodo.configure(state="normal")
            self.e_referencia.configure(state="normal")
            self.btn_eliminar_abono.configure(state="normal")
            
        # Cargar abonos en la tabla
        self._cargar_abonos()

    def _cargar_abonos(self):
        self.tree_abonos.delete(*self.tree_abonos.get_children())
        if not self.selected_factura_id:
            return
            
        rows = db.pagos_por_factura(self.selected_factura_id)
        for r in rows:
            # r: id, factura_id, monto, fecha, metodo, comprobante, creado_en
            p_id, _, monto, fec, met, comp, _ = r
            s_monto = f"L. {float(monto or 0.0):,.2f}"
            self.tree_abonos.insert("", "end", iid=p_id, values=(fec, s_monto, met, comp or "-"))

    def _limpiar_detalles(self):
        self.lbl_fact_sel.configure(text="Ninguna factura seleccionada")
        self.lbl_cli_sel.configure(text="-")
        self.lbl_total_sel.configure(text="L. 0.00")
        self.lbl_cobrado_sel.configure(text="L. 0.00")
        self.lbl_saldo_sel.configure(text="L. 0.00")
        self.e_monto.delete(0, tk.END)
        self.e_referencia.delete(0, tk.END)
        self.tree_abonos.delete(*self.tree_abonos.get_children())

    # ── Registrar Abono ────────────────────────────────────────────────────────
    def _registrar_abono(self):
        if not self.selected_factura_id:
            messagebox.showwarning("Selección requerida", "Por favor seleccione primero una factura de la lista izquierda."); return
            
        monto_str = self.e_monto.get().strip().replace("L.", "").replace("L", "").replace(",", "").strip()
        fecha_str = self.e_fecha.get().strip()
        metodo = self.cb_metodo.get()
        referencia = self.e_referencia.get().strip()
        
        if not monto_str or not fecha_str:
            messagebox.showwarning("Campos obligatorios", "Por favor complete el monto y la fecha del abono."); return
            
        try:
            monto = float(monto_str)
            if monto <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Monto no válido", "Por favor introduzca un monto válido superior a cero."); return

        # Validar formato de fecha DD/MM/AAAA
        try:
            datetime.strptime(fecha_str, "%d/%m/%Y")
        except ValueError:
            messagebox.showerror("Fecha no válida", "La fecha de pago debe tener el formato DD/MM/AAAA (ejemplo: 15/06/2026)."); return
            
        # Comprobar que no exceda el saldo pendiente
        item_vals = self.tree_facturas.item(self.selected_factura_id, "values")
        saldo_pendiente = float(item_vals[6].replace("L. ", "").replace(",", "").strip())
        
        if monto > saldo_pendiente + 0.01: # margen para redondeos
            if not messagebox.askyesno("Confirmar Sobrepago", f"El monto del abono (L. {monto:,.2f}) excede el saldo pendiente (L. {saldo_pendiente:,.2f}).\n¿Desea registrar el cobro de todas formas?"):
                return
                
        # Guardar en BD
        try:
            db.pagos_agregar(self.selected_factura_id, monto, fecha_str, metodo, referencia)
            messagebox.showinfo("Abono Registrado", f"Se registró con éxito el abono por L. {monto:,.2f} a la factura.")
            self.e_monto.delete(0, tk.END)
            self.e_referencia.delete(0, tk.END)
            
            # Recargar y seleccionar de nuevo para actualizar saldos
            current_sel = self.selected_factura_id
            self._cargar_facturas()
            self.tree_facturas.selection_set(current_sel)
            
            self.app.set_status(f"Abono de L. {monto:,.2f} registrado en factura {item_vals[1]}")
        except Exception as ex:
            messagebox.showerror("Error al guardar", f"No se pudo registrar el pago en la base de datos:\n{str(ex)}")

    # ── Eliminar Abono Seleccionado ─────────────────────────────────────────────
    def _eliminar_abono_sel(self):
        sel_pago = self.tree_abonos.selection()
        if not sel_pago:
            messagebox.showinfo("Selección requerida", "Seleccione el abono que desea eliminar en la tabla de historial."); return
            
        pago_id = int(sel_pago[0])
        pago_vals = self.tree_abonos.item(pago_id, "values")
        monto_pago = pago_vals[1]
        
        if messagebox.askyesno("Confirmar Eliminación", f"¿Desea eliminar este abono de {monto_pago} del registro de la base de datos?\n\nEsta acción revertirá el saldo cobrado."):
            try:
                db.pagos_eliminar(pago_id)
                messagebox.showinfo("Abono Eliminado", "El abono fue eliminado físicamente del registro de finanzas.")
                
                # Recargar
                current_sel = self.selected_factura_id
                self._cargar_facturas()
                if current_sel:
                    self.tree_facturas.selection_set(current_sel)
            except Exception as ex:
                messagebox.showerror("Error al eliminar", f"No se pudo eliminar el abono:\n{str(ex)}")
