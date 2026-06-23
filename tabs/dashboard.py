"""
tabs/dashboard.py – Tab de Dashboard Estadístico y Consolidado de Predios
SilvaDesk Pro · SEDCAF / ICF / FEMA Honduras
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
import os
import db
from datetime import datetime

# Matplotlib para gráficos dinámicos
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Paleta forestal y judicial integrada
V_OSC = "#1B5E20"     # Verde TFC
V_FEMA = "#005FB8"    # Azul FEMA
V_MED = "#2E7D32"
BLANCO = "#FFFFFF"
GRIS_F = "#F2F5F0"
ALERTA_COLOR = "#D32F2F" # Rojo para plagas
KPI_BG = "#E8F5E9"

class DashboardTab:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.selected_sitio = None
        
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(1, weight=1)
        
        self._build_toolbar()
        
        # Scrollable container for the dashboard content
        self.scroll = ctk.CTkScrollableFrame(self.parent, fg_color=GRIS_F)
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0,6))
        self.scroll.grid_columnconfigure(0, weight=1)
        
        self._build_kpi_cards()
        self._build_charts_frame()
        self._cargar_sitios()

    def _build_toolbar(self):
        tb = ctk.CTkFrame(self.parent, fg_color=V_MED, corner_radius=6, height=48)
        tb.grid(row=0, column=0, sticky="ew", padx=6, pady=(6,4))
        tb.grid_propagate(False)
        
        # Configurar columnas de la barra
        tb.grid_columnconfigure(0, weight=0)
        tb.grid_columnconfigure(1, weight=0)
        tb.grid_columnconfigure(2, weight=1)
        tb.grid_columnconfigure(3, weight=0)
        tb.grid_columnconfigure(4, weight=0)
        
        ctk.CTkLabel(tb, text=" Sitio / Predio:", text_color=BLANCO, font=("Segoe UI", 13, "bold")).grid(row=0, column=0, padx=(10, 4), pady=8)
        
        self.cb_sitios = ctk.CTkComboBox(tb, values=[], width=320, height=32,
            fg_color=BLANCO, text_color="#111", button_color=V_OSC, border_color=V_OSC,
            font=("Segoe UI", 13), dropdown_font=("Segoe UI", 13),
            command=self._on_sitio_cambiado)
        self.cb_sitios.grid(row=0, column=1, padx=4, pady=8)
        
        bc = dict(fg_color=V_OSC, hover_color="#0f3d14", text_color=BLANCO,
                  font=("Segoe UI", 12, "bold"), corner_radius=5, height=32)
        
        ctk.CTkButton(tb, text="🔄  Actualizar Datos", command=self.actualizar, width=130, **bc).grid(row=0, column=3, padx=4, pady=8)
        
        self.btn_export = ctk.CTkButton(tb, text="📄  Ficha Consolidada (PDF)", command=self._exportar_pdf, width=180, fg_color=V_FEMA, hover_color="#004687", text_color=BLANCO, font=("Segoe UI", 12, "bold"), corner_radius=5, height=32)
        self.btn_export.grid(row=0, column=4, padx=(4, 10), pady=8)

    def _build_kpi_cards(self):
        # Frame contenedor de KPIs
        self.kpis_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.kpis_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        self.kpis_frame.grid_columnconfigure(0, weight=1)
        self.kpis_frame.grid_columnconfigure(1, weight=1)
        self.kpis_frame.grid_columnconfigure(2, weight=1)
        
        # KPI 1: Volumen Cubicada
        self.card_vol = ctk.CTkFrame(self.kpis_frame, fg_color=BLANCO, corner_radius=8, border_width=1, border_color="#C8E6C9")
        self.card_vol.grid(row=0, column=0, padx=6, pady=4, sticky="nsew")
        ctk.CTkLabel(self.card_vol, text="🪵 VOLUMEN TOTAL CUBICADO", font=("Segoe UI", 11, "bold"), text_color=V_MED).pack(pady=(12, 2))
        self.lbl_vol_val = ctk.CTkLabel(self.card_vol, text="0.00 m³", font=("Segoe UI", 24, "bold"), text_color="#111")
        self.lbl_vol_val.pack(pady=(0, 6))
        ctk.CTkLabel(self.card_vol, text="Suma de registros asentados de campo", font=("Segoe UI", 11, "italic"), text_color="#666").pack(pady=(0, 12))
        
        # KPI 2: Salud Forestal / Alertas Plagas
        self.card_plagas = ctk.CTkFrame(self.kpis_frame, fg_color=BLANCO, corner_radius=8, border_width=1, border_color="#FFCDD2")
        self.card_plagas.grid(row=0, column=1, padx=6, pady=4, sticky="nsew")
        ctk.CTkLabel(self.card_plagas, text="🚨 ALERTAS DE SALUD FORESTAL", font=("Segoe UI", 11, "bold"), text_color=ALERTA_COLOR).pack(pady=(12, 2))
        self.lbl_plagas_val = ctk.CTkLabel(self.card_plagas, text="0", font=("Segoe UI", 24, "bold"), text_color="#111")
        self.lbl_plagas_val.pack(pady=(0, 6))
        self.lbl_plagas_desc = ctk.CTkLabel(self.card_plagas, text="Incidencias críticas reportadas (gorgojo)", font=("Segoe UI", 11, "italic"), text_color="#666")
        self.lbl_plagas_desc.pack(pady=(0, 12))
        
        # KPI 3: Actuaciones FEMA
        self.card_fema = ctk.CTkFrame(self.kpis_frame, fg_color=BLANCO, corner_radius=8, border_width=1, border_color="#BBDEFB")
        self.card_fema.grid(row=0, column=2, padx=6, pady=4, sticky="nsew")
        ctk.CTkLabel(self.card_fema, text="⚖️ INSPECCIONES / ACTAS FEMA", font=("Segoe UI", 11, "bold"), text_color=V_FEMA).pack(pady=(12, 2))
        self.lbl_fema_val = ctk.CTkLabel(self.card_fema, text="0", font=("Segoe UI", 24, "bold"), text_color="#111")
        self.lbl_fema_val.pack(pady=(0, 6))
        ctk.CTkLabel(self.card_fema, text="Actuaciones con carácter de peritaje", font=("Segoe UI", 11, "italic"), text_color="#666").pack(pady=(0, 12))

    def _build_charts_frame(self):
        # Frame contenedor para gráficos
        self.charts_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.charts_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.charts_frame.grid_columnconfigure(0, weight=1)
        self.charts_frame.grid_columnconfigure(1, weight=1)

    def _cargar_sitios(self):
        sitios = db.dashboard_sitios_todos()
        if sitios:
            self.cb_sitios.configure(values=sitios)
            self.cb_sitios.set(sitios[0])
            self.selected_sitio = sitios[0]
            self.actualizar()
        else:
            self.cb_sitios.configure(values=["Sin sitios registrados"])
            self.cb_sitios.set("Sin sitios registrados")
            self.selected_sitio = None
            self.lbl_vol_val.configure(text="0.00 m³")
            self.lbl_plagas_val.configure(text="0")
            self.lbl_fema_val.configure(text="0")
            self._limpiar_graficos()

    def _on_sitio_cambiado(self, val):
        if val != "Sin sitios registrados":
            self.selected_sitio = val
            self.actualizar()

    def actualizar(self):
        if not self.selected_sitio or self.selected_sitio == "Sin sitios registrados":
            return
            
        # 1. Cargar KPIs
        vol, ins, plagas = db.dashboard_kpis_por_sitio(self.selected_sitio)
        
        self.lbl_vol_val.configure(text=f"{vol:,.2f} m³")
        self.lbl_fema_val.configure(text=str(ins))
        self.lbl_plagas_val.configure(text=str(plagas))
        
        # Cambiar colores según riesgo de plagas
        if plagas > 0:
            self.card_plagas.configure(fg_color="#FFEBEE", border_color="#E57373")
            self.lbl_plagas_val.configure(text_color=ALERTA_COLOR)
            self.lbl_plagas_desc.configure(text="⚠️ Amenaza forestal detectada en campo")
        else:
            self.card_plagas.configure(fg_color=BLANCO, border_color="#FFCDD2")
            self.lbl_plagas_val.configure(text_color="#111")
            self.lbl_plagas_desc.configure(text="No se registran brotes de plagas")
            
        # 2. Re-generar gráficos
        self._limpiar_graficos()
        self._dibujar_graficos()
        self.app.set_status(f"Dashboard actualizado para el sitio: {self.selected_sitio}")

    def _limpiar_graficos(self):
        for widget in self.charts_frame.winfo_children():
            widget.destroy()

    def _dibujar_graficos(self):
        if not self.selected_sitio:
            return
            
        # Obtener datos estadísticos
        actividades = db.dashboard_actividades_por_sitio(self.selected_sitio)
        diligencias = db.dashboard_diligencias_por_sitio(self.selected_sitio)
        estados_actas = db.dashboard_estados_actas_por_sitio(self.selected_sitio)
        
        # Determinar diseño de grilla
        # Mostraremos actividades en el lado izquierdo y temas de FEMA en el lado derecho
        
        # 1. Gráfico de Actividades de Campo (Pie o Bar)
        f_left = ctk.CTkFrame(self.charts_frame, fg_color=BLANCO, corner_radius=8, border_width=1, border_color="#E0E0E0")
        f_left.grid(row=0, column=0, padx=6, pady=6, sticky="nsew")
        ctk.CTkLabel(f_left, text="Distribución de Actividades de Campo TFC", font=("Segoe UI", 12, "bold"), text_color=V_OSC).pack(pady=(8, 2))
        
        if actividades:
            fig1, ax1 = plt.subplots(figsize=(4.5, 3.5), dpi=100)
            fig1.patch.set_facecolor('#FFFFFF')
            ax1.set_facecolor('#FFFFFF')
            
            labels = [r[0][:20] + '..' if len(r[0]) > 20 else r[0] for r in actividades]
            sizes = [r[1] for r in actividades]
            
            # Paleta de verdes
            colors = ['#1B5E20', '#2E7D32', '#4CAF50', '#81C784', '#C8E6C9', '#E8F5E9']
            colors = colors[:len(sizes)]
            
            wedges, texts, autotexts = ax1.pie(sizes, labels=labels, autopct='%1.0f%%', startangle=90, colors=colors, textprops=dict(fontsize=8))
            plt.setp(autotexts, size=8, weight="bold", color="white")
            ax1.axis('equal')  
            
            canvas1 = FigureCanvasTkAgg(fig1, master=f_left)
            canvas1.draw()
            canvas1.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
            plt.close(fig1)
        else:
            ctk.CTkLabel(f_left, text="No hay anotaciones de campo registradas.", font=("Segoe UI", 11, "italic"), text_color="#666").pack(pady=40)
            
        # 2. Gráfico de Diligencias y Actas FEMA (Lado Derecho)
        f_right = ctk.CTkFrame(self.charts_frame, fg_color=BLANCO, corner_radius=8, border_width=1, border_color="#E0E0E0")
        f_right.grid(row=0, column=1, padx=6, pady=6, sticky="nsew")
        ctk.CTkLabel(f_right, text="Estado y Tipo de Diligencias FEMA", font=("Segoe UI", 12, "bold"), text_color=V_FEMA).pack(pady=(8, 2))
        
        if diligencias or estados_actas:
            # Gráfico de barras combinadas o subplots
            fig2, (ax2a, ax2b) = plt.subplots(2, 1, figsize=(4.5, 3.8), dpi=100)
            fig2.patch.set_facecolor('#FFFFFF')
            fig2.subplots_adjust(hspace=0.6, bottom=0.15)
            
            # ax2a: Estado de actas
            ax2a.set_facecolor('#FFFFFF')
            if estados_actas:
                est_labels = [r[0] for r in estados_actas]
                est_counts = [r[1] for r in estados_actas]
                # Colores para estados
                col_map = {"Activa": "#4CAF50", "En trámite": "#FFC107", "Elevada a proceso penal": "#FF5722", "Archivada": "#9E9E9E", "Anulada": "#E53935"}
                est_colors = [col_map.get(l, "#0078D4") for l in est_labels]
                
                bars = ax2a.bar(est_labels, est_counts, color=est_colors, width=0.4)
                ax2a.set_title("Estado de Actuaciones Periciales", fontsize=9, weight="bold", color="#333")
                ax2a.tick_params(axis='both', labelsize=8)
                ax2a.spines['top'].set_visible(False)
                ax2a.spines['right'].set_visible(False)
                ax2a.spines['left'].set_visible(False)
                ax2a.spines['bottom'].set_color('#DDD')
                ax2a.get_yaxis().set_visible(False) # ocultar eje Y para limpieza
                
                # Escribir valores encima de barras
                for bar in bars:
                    height = bar.get_height()
                    ax2a.annotate(f'{int(height)}',
                                xy=(bar.get_x() + bar.get_width() / 2, height),
                                xytext=(0, 2),  
                                textcoords="offset points",
                                ha='center', va='bottom', fontsize=8, weight="bold")
            else:
                ax2a.text(0.5, 0.5, 'Sin actas judiciales asentadas', ha='center', va='center', fontsize=8, color="#666")
                ax2a.axis('off')
                
            # ax2b: Tipo de Diligencias
            ax2b.set_facecolor('#FFFFFF')
            if diligencias:
                dil_labels = [r[0][:15] + '..' if len(r[0]) > 15 else r[0] for r in diligencias]
                dil_counts = [r[1] for r in diligencias]
                y_pos = range(len(dil_labels))
                
                bars2 = ax2b.barh(y_pos, dil_counts, color='#0078D4', height=0.5)
                ax2b.set_yticks(y_pos)
                ax2b.set_yticklabels(dil_labels, fontsize=8)
                ax2b.set_title("Tipos de Diligencia Judicial", fontsize=9, weight="bold", color="#333")
                ax2b.tick_params(axis='both', labelsize=8)
                ax2b.spines['top'].set_visible(False)
                ax2b.spines['right'].set_visible(False)
                ax2b.spines['left'].set_color('#DDD')
                ax2b.spines['bottom'].set_visible(False)
                ax2b.get_xaxis().set_visible(False)
                
                # Escribir valores en barras horizontales
                for bar in bars2:
                    width = bar.get_width()
                    ax2b.annotate(f' {int(width)}',
                                xy=(width, bar.get_y() + bar.get_height() / 2),
                                xytext=(2, 0),  
                                textcoords="offset points",
                                ha='left', va='center', fontsize=8, weight="bold")
            else:
                ax2b.text(0.5, 0.5, 'Sin diligencias registradas', ha='center', va='center', fontsize=8, color="#666")
                ax2b.axis('off')
                
            canvas2 = FigureCanvasTkAgg(fig2, master=f_right)
            canvas2.draw()
            canvas2.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
            plt.close(fig2)
        else:
            ctk.CTkLabel(f_right, text="No hay actas de la fiscalía registradas.", font=("Segoe UI", 11, "italic"), text_color="#666").pack(pady=40)

    def _exportar_pdf(self):
        if not self.selected_sitio or self.selected_sitio == "Sin sitios registrados":
            messagebox.showinfo("SilvaDesk", "No hay ningún predio válido seleccionado para exportar."); return
            
        # 1. Intentar buscar una carpeta configurada para este predio
        # Buscamos en bitacora_tfc primero
        conn = db.get_conn(); c = conn.cursor()
        c.execute("SELECT ruta_carpeta_caso FROM bitacora_tfc WHERE sitio_predio=? AND ruta_carpeta_caso IS NOT NULL AND ruta_carpeta_caso != '' LIMIT 1", (self.selected_sitio,))
        r = c.fetchone()
        carpeta_def = r[0] if r else ""
        
        # Si no la encuentra, busca en protocolo
        if not carpeta_def:
            c.execute("SELECT ruta_carpeta_caso FROM protocolo WHERE lugar=? AND ruta_carpeta_caso IS NOT NULL AND ruta_carpeta_caso != '' LIMIT 1", (self.selected_sitio,))
            r = c.fetchone()
            carpeta_def = r[0] if r else ""
        conn.close()
        
        # 2. Diálogo para guardar el PDF
        safe_name = "".join(c for c in f"Ficha_Consolidada_{self.selected_sitio}" if c.isalnum() or c in " _-").strip().replace(" ", "_")
        
        initial_dir = carpeta_def if carpeta_def and os.path.exists(carpeta_def) else os.getcwd()
        
        ruta_pdf = filedialog.asksaveasfilename(
            title="Guardar Ficha Técnica Consolidada",
            initialdir=initial_dir,
            initialfile=f"{safe_name}.pdf",
            filetypes=[("Documentos PDF", "*.pdf")],
            defaultextension=".pdf"
        )
        if not ruta_pdf:
            return
            
        # 3. Generar el PDF
        try:
            from utils.pdf_dashboard import generar_pdf_ficha_consolidada
            
            # Recolectar datos
            vol, ins, plagas = db.dashboard_kpis_por_sitio(self.selected_sitio)
            
            # Detalle de actividades
            conn = db.get_conn(); c = conn.cursor()
            c.execute("SELECT num_bitacora, fecha, actividad_tipo, volumen_m3, estado, tfc_nombre FROM bitacora_tfc WHERE sitio_predio=? ORDER BY fecha DESC", (self.selected_sitio,))
            lista_tfc = c.fetchall()
            
            # Detalle de actas FEMA
            c.execute("SELECT num_acta, fecha, tipo_diligencia, num_expediente_fema, estado FROM protocolo WHERE lugar=? ORDER BY fecha DESC", (self.selected_sitio,))
            lista_fema = c.fetchall()
            conn.close()
            
            conf = db.config_obtener()
            
            datos_consolidado = {
                "predio": self.selected_sitio,
                "volumen_total": vol,
                "inspecciones_total": ins,
                "plagas_total": plagas,
                "lista_tfc": lista_tfc,
                "lista_fema": lista_fema,
                "fecha_generacion": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "perito_nombre": conf[2],
                "empresa_nombre": conf[1]
            }
            
            generar_pdf_ficha_consolidada(ruta_pdf, datos_consolidado)
            
            # 4. Copiar automáticamente a la carpeta de caso si existe y es diferente a donde se guardó
            if carpeta_def and os.path.exists(carpeta_def):
                dest_copia = os.path.join(carpeta_def, f"{safe_name}.pdf")
                if os.path.abspath(ruta_pdf) != os.path.abspath(dest_copia):
                    import shutil
                    os.makedirs(carpeta_def, exist_ok=True)
                    shutil.copy2(ruta_pdf, dest_copia)
                    
            if messagebox.askyesno("SilvaDesk - Ficha Consolidada", f"Ficha Técnica Consolidada generada con éxito.\n¿Desea abrir el PDF ahora?\n{ruta_pdf}"):
                os.startfile(ruta_pdf)
                
            self.app.set_status(f"Ficha consolidada exportada a: {ruta_pdf}")
        except Exception as ex:
            messagebox.showerror("Error al generar PDF", f"Ocurrió un error inesperado al generar el PDF:\n{str(ex)}")
