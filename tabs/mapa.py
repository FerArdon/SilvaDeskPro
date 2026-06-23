"""
tabs/mapa.py – Visualización Geoespacial de Predios (Mapa de Honduras Offline)
SilvaDesk Pro · SEDCAF / ICF Honduras
"""
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

V_OSC="#005FB8"; V_MED="#0078D4"; V_CLR="#DDEEFF"; BLANCO="#FFFFFF"
GRIS_F="#F2F5F0"; GRIS_B="#DDDDDD"; ROJO_M="#D84315"; VERDE_M="#2E7D32"; VERDE_OSC="#1B5E20"

# Coordenadas extremas geográficas de la imagen del mapa de Honduras
LON_MIN = -89.3797
LON_MAX = -83.1292
LAT_MIN = 12.9814
LAT_MAX = 16.5197

class MapaTab:
    def __init__(self, parent, app):
        self.parent = parent; self.app = app
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)

        self.puntos = []            # Lista unificada de todos los puntos de coordenadas
        self.punto_seleccionado = None
        self.img_mapa_original = None
        self.map_image_id = None
        
        # Cargar mapa original
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.mapa_path = os.path.join(base, "assets", "honduras_map.png")
        if os.path.exists(self.mapa_path):
            try:
                self.img_mapa_original = Image.open(self.mapa_path)
            except Exception:
                pass

        # PanedWindow para dividir el mapa (izquierda) y el panel lateral (derecha)
        self.paned = tk.PanedWindow(
            parent,
            orient=tk.HORIZONTAL,
            sashwidth=6,
            sashrelief="flat",
            bg="#C0D4EC",
            handlesize=0
        )
        self.paned.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        self._build_panel_mapa()
        self._build_panel_lateral()

        # Vincular evento de redimensión del canvas
        self.canvas.bind("<Configure>", self._on_canvas_resize)
        
        # Cargar puntos inicialmente
        self.actualizar_puntos()

    def _build_panel_mapa(self):
        # Frame del Canvas del mapa
        self.map_pane = tk.Frame(self.paned, bg=GRIS_F)
        self.map_pane.rowconfigure(0, weight=1)
        self.map_pane.columnconfigure(0, weight=1)
        self.paned.add(self.map_pane, minsize=500, stretch="always")

        # Canvas para dibujar el mapa y los marcadores
        self.canvas = tk.Canvas(self.map_pane, bg=BLANCO, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

    def _build_panel_lateral(self):
        # Panel lateral derecho
        self.side_pane = tk.Frame(self.paned, bg=GRIS_F)
        self.side_pane.rowconfigure(2, weight=1)
        self.side_pane.columnconfigure(0, weight=1)
        self.paned.add(self.side_pane, minsize=340, stretch="never")

        # Header del panel
        hdr = ctk.CTkFrame(self.side_pane, fg_color=V_OSC, corner_radius=6, height=40)
        hdr.grid(row=0, column=0, sticky="ew", padx=6, pady=(6,4)); hdr.grid_propagate(False)
        ctk.CTkLabel(hdr, text="📍 Ubicación de Predios Forestales", font=("Segoe UI",13,"bold"), text_color=BLANCO).pack(side="left", padx=12, pady=8)
        
        btn_refresh = ctk.CTkButton(hdr, text="🔄 Actualizar", font=("Segoe UI", 11), text_color=BLANCO, fg_color=V_MED, hover_color="#006CC4", width=80, height=24, command=self.actualizar_puntos)
        btn_refresh.pack(side="right", padx=10)

        # Resumen de totales
        self.lbl_resumen = ctk.CTkLabel(self.side_pane, text="Cargando ubicaciones...", font=("Segoe UI", 12, "bold"), text_color="#555", anchor="w")
        self.lbl_resumen.grid(row=1, column=0, sticky="ew", padx=12, pady=2)

        # Lista scrollable de predios
        self.list_frame = ctk.CTkScrollableFrame(self.side_pane, fg_color=BLANCO, corner_radius=6, border_width=1, border_color="#C0D4EC")
        self.list_frame.grid(row=2, column=0, sticky="nsew", padx=6, pady=4)
        self.list_frame.grid_columnconfigure(0, weight=1)

        # Ficha de detalle del punto seleccionado
        self.detail_frame = ctk.CTkFrame(self.side_pane, fg_color=V_CLR, corner_radius=6, border_width=1, border_color=V_MED)
        self.detail_frame.grid(row=3, column=0, sticky="ew", padx=6, pady=(4,6))
        self.detail_frame.grid_columnconfigure(0, weight=1)

        self.lbl_detalle = ctk.CTkLabel(self.detail_frame, 
            text="💡 Seleccioná un predio de la lista o un punto en el mapa para ver sus detalles geográficos y técnicos.",
            font=("Segoe UI", 12, "italic"), text_color=V_OSC, justify="left", anchor="w", wraplength=310)
        self.lbl_detalle.grid(row=0, column=0, padx=12, pady=12)

    def actualizar_puntos(self):
        self.puntos.clear()
        
        # 1. Cargar actas del protocolo que tengan coordenadas GPS
        actas = db.protocolo_todos()
        for a in actas:
            # a: id, num_acta, folio, fecha, hora, lugar, tipo_diligencia, num_expediente_fema, estado, gps_lat, gps_lon
            # Los indices despues del estado son: lat (9), lon (10)
            if len(a) > 10 and a[9] is not None and a[10] is not None:
                row_full = db.protocolo_por_id(a[0])
                # row_full[18]=utm_zona, row_full[19]=utm_este, row_full[20]=utm_norte
                self.puntos.append({
                    "id": a[0],
                    "tipo": "FEMA",
                    "registro": a[1],
                    "folio": a[2],
                    "fecha": a[3],
                    "predio": a[5],
                    "actividad": a[6],
                    "expediente": a[7],
                    "estado": a[8],
                    "lat": a[9],
                    "lon": a[10],
                    "utm_z": row_full[18] if len(row_full) > 18 else "",
                    "utm_e": row_full[19] if len(row_full) > 19 else None,
                    "utm_n": row_full[20] if len(row_full) > 20 else None,
                })

        # 2. Cargar bitácoras de campo TFC que tengan coordenadas GPS
        tfc_rows = db.bitacora_tfc_todos()
        for t in tfc_rows:
            # t: id, num_bitacora, folio, fecha, sitio_predio, poa_codigo, actividad_tipo, volumen_m3, estado, gps_lat, gps_lon
            # Los indices despues del estado son: lat (9), lon (10)
            if len(t) > 10 and t[9] is not None and t[10] is not None:
                row_full = db.bitacora_tfc_por_id(t[0])
                # row_full[16]=utm_zona, row_full[17]=utm_este, row_full[18]=utm_norte
                self.puntos.append({
                    "id": t[0],
                    "tipo": "TFC",
                    "registro": t[1],
                    "folio": t[2],
                    "fecha": t[3],
                    "predio": t[4],
                    "actividad": t[6],
                    "poa": t[5],
                    "volumen": t[7],
                    "estado": t[8],
                    "lat": t[9],
                    "lon": t[10],
                    "utm_z": row_full[16] if len(row_full) > 16 else "",
                    "utm_e": row_full[17] if len(row_full) > 17 else None,
                    "utm_n": row_full[18] if len(row_full) > 18 else None,
                })

        # Actualizar totales
        c_fema = sum(1 for p in self.puntos if p["tipo"] == "FEMA")
        c_tfc = sum(1 for p in self.puntos if p["tipo"] == "TFC")
        self.lbl_resumen.configure(text=f"Total: {len(self.puntos)} predios (🔴 {c_fema} FEMA · 🟢 {c_tfc} TFC)")

        # Redibujar la lista y los marcadores
        self._refrescar_lista_lateral()
        self._dibujar_mapa_y_marcadores()

    def _refrescar_lista_lateral(self):
        # Limpiar lista lateral
        for w in self.list_frame.winfo_children():
            w.destroy()

        if not self.puntos:
            ctk.CTkLabel(self.list_frame, text="No hay áreas georreferenciadas.", font=("Segoe UI", 12, "italic"), text_color="#777").pack(pady=20)
            return

        for p in self.puntos:
            color_b = ROJO_M if p["tipo"] == "FEMA" else VERDE_M
            lbl_pref = "FEMA" if p["tipo"] == "FEMA" else "TFC"
            
            btn = ctk.CTkButton(
                self.list_frame,
                text=f"{lbl_pref} | Folio {p['folio']} · {p['predio'][:22]}{'...' if len(p['predio']) > 22 else ''}",
                font=("Segoe UI", 12),
                anchor="w",
                fg_color=BLANCO,
                text_color="#333",
                hover_color="#F2F5F0",
                border_width=1,
                border_color=color_b,
                height=32,
                corner_radius=4,
                command=lambda pt=p: self.seleccionar_punto(pt)
            )
            btn.pack(fill="x", padx=4, pady=3)

    def _on_canvas_resize(self, event):
        # El canvas cambió de tamaño, redibujar todo
        self._dibujar_mapa_y_marcadores()

    def _dibujar_mapa_y_marcadores(self):
        self.canvas.delete("all")
        
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw < 50 or ch < 50:
            return  # Canvas demasiado pequeño para dibujar

        new_w, new_h = cw, ch
        offset_x, offset_y = 0, 0

        # 1. Dibujar el mapa de fondo redimensionado
        if self.img_mapa_original:
            try:
                w_orig, h_orig = self.img_mapa_original.size
                aspect = w_orig / h_orig
                
                if cw / ch > aspect:
                    new_h = ch
                    new_w = int(ch * aspect)
                else:
                    new_w = cw
                    new_h = int(cw / aspect)
                
                offset_x = (cw - new_w) / 2
                offset_y = (ch - new_h) / 2

                img_resized = self.img_mapa_original.resize((new_w, new_h), Image.Resampling.LANCZOS)
                self.photo_mapa = ImageTk.PhotoImage(img_resized)
                self.map_image_id = self.canvas.create_image(offset_x, offset_y, anchor="nw", image=self.photo_mapa)
            except Exception:
                self.canvas.create_text(cw/2, ch/2, text="[Error cargando el mapa offline]", font=("Segoe UI", 13, "bold"), fill="#C0392B")

        # 2. Dibujar los marcadores de predios
        for p in self.puntos:
            lat, lon = p["lat"], p["lon"]
            
            # Proyección lineal ajustada al tamaño escalado y offset
            x = offset_x + (((lon - LON_MIN) / (LON_MAX - LON_MIN)) * new_w)
            y = offset_y + (new_h - (((lat - LAT_MIN) / (LAT_MAX - LAT_MIN)) * new_h))

            # Validar límites físicos del lienzo
            if 0 <= x <= cw and 0 <= y <= ch:
                color_fill = ROJO_M if p["tipo"] == "FEMA" else VERDE_M
                
                # Resaltar si está seleccionado
                r = 7 if (self.punto_seleccionado and self.punto_seleccionado["tipo"] == p["tipo"] and self.punto_seleccionado["id"] == p["id"]) else 5
                outline_color = "#000000" if r == 7 else BLANCO
                outline_w = 2 if r == 7 else 1
                
                marker = self.canvas.create_oval(
                    x - r, y - r, x + r, y + r,
                    fill=color_fill, outline=outline_color, width=outline_w,
                    tags=("marker", f"marker_{p['tipo']}_{p['id']}")
                )
                
                # Asociar clic en el marcador
                self.canvas.tag_bind(marker, "<Button-1>", lambda e, pt=p: self.seleccionar_punto(pt))
                # Tooltip al pasar el mouse
                self.canvas.tag_bind(marker, "<Enter>", lambda e, pt=p, mx=x, my=y: self._mostrar_tooltip(pt, mx, my))
                self.canvas.tag_bind(marker, "<Leave>", lambda e: self.canvas.delete("tooltip"))

    def seleccionar_punto(self, p):
        self.punto_seleccionado = p
        self._dibujar_mapa_y_marcadores()
        self._mostrar_detalle_lateral(p)
        
        # Efecto visual: parpadear marcador en el canvas
        tag = f"marker_{p['tipo']}_{p['id']}"
        self.canvas.itemconfig(tag, fill=BLANCO)
        self.parent.after(150, lambda: self.canvas.itemconfig(tag, fill=(ROJO_M if p["tipo"] == "FEMA" else VERDE_M)))
        self.parent.after(300, lambda: self.canvas.itemconfig(tag, fill=BLANCO))
        self.parent.after(450, lambda: self.canvas.itemconfig(tag, fill=(ROJO_M if p["tipo"] == "FEMA" else VERDE_M)))

    def _mostrar_detalle_lateral(self, p):
        for w in self.detail_frame.winfo_children():
            w.destroy()

        self.detail_frame.configure(border_color=(ROJO_M if p["tipo"] == "FEMA" else VERDE_M))
        
        # Construir ficha técnica en el panel lateral
        title_t = "Diligencia FEMA (Acta)" if p["tipo"] == "FEMA" else "Bitácora Campo TFC"
        ctk.CTkLabel(self.detail_frame, text=title_t, font=("Segoe UI", 12, "bold"), text_color=(ROJO_M if p["tipo"] == "FEMA" else VERDE_OSC)).grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(10,4))
        
        def add_row(r, lbl, val):
            ctk.CTkLabel(self.detail_frame, text=lbl, font=("Segoe UI", 11, "bold"), text_color="#555", anchor="e").grid(row=r, column=0, sticky="e", padx=(12,6), pady=2)
            ctk.CTkLabel(self.detail_frame, text=val, font=("Segoe UI", 11), text_color="#111", anchor="w", justify="left", wraplength=200).grid(row=r, column=1, sticky="w", padx=(0,12), pady=2)

        add_row(1, "Registro No.:", p["registro"])
        add_row(2, "Folio:", str(p["folio"]))
        add_row(3, "Fecha:", p["fecha"])
        add_row(4, "Predio / Sitio:", p["predio"])
        add_row(5, "Actividad:", p["actividad"])
        
        if p["tipo"] == "FEMA":
            add_row(6, "Exp. FEMA No.:", p["expediente"] or "—")
        else:
            add_row(6, "Código POA:", p["poa"] or "—")
            vol_m3 = f"{float(p['volumen'] or 0.0):,.2f} m³"
            add_row(7, "Vol. Cubicada:", vol_m3)
        
        # Coordenadas UTM
        e_str = f"{p['utm_e']:,.1f} m" if p["utm_e"] is not None else "—"
        n_str = f"{p['utm_n']:,.1f} m" if p["utm_n"] is not None else "—"
        add_row(8, "Zona UTM WGS84:", p["utm_z"] or "16N")
        add_row(9, "UTM Este (X):", e_str)
        add_row(10, "UTM Norte (Y):", n_str)
        
        # Coordenadas Lat/Lon decimales
        gps_str = f"{p['lat']:.5f} N, {p['lon']:.5f} O"
        add_row(11, "Grados Decimales:", gps_str)

        add_row(12, "Estado actual:", p["estado"])

        # Botón para abrir el documento
        def abrir_doc():
            if p["tipo"] == "FEMA":
                from tabs.bitacora import BitacoraTab
                # Generar PDF de forma temporal
                row_full = db.protocolo_por_id(p["id"])
                # Importar generador de PDF
                from utils.pdf_acta import generar_acta
                conf = db.config_obtener()
                base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Actas")
                os.makedirs(base, exist_ok=True)
                ruta = os.path.join(base, f"Acta_{row_full[1]}.pdf")
                datos_acta = {
                    "num_acta": row_full[1], "folio": row_full[2], "anio": row_full[3], "fecha": row_full[4], "hora": row_full[5],
                    "lugar": row_full[6], "municipio": row_full[7], "departamento": row_full[8], "num_expediente_fema": row_full[9],
                    "tipo_diligencia": row_full[10], "comparecientes": row_full[11], "hechos": row_full[12], "hallazgos": row_full[13],
                    "fundamento_legal": row_full[14], "disposicion": row_full[15], "estado": row_full[16], "observaciones": row_full[17],
                    "perito_nombre": row_full[27] if len(row_full) > 27 and row_full[27] else conf[2],
                    "perito_registro": row_full[28] if len(row_full) > 28 and row_full[28] else conf[3],
                    "seccion": conf[1]
                }
                generar_acta(ruta, datos_acta)
                if os.path.exists(ruta): os.startfile(ruta)
            else:
                row_full = db.bitacora_tfc_por_id(p["id"])
                from utils.pdf_bitacora_tfc import generar_pdf_bitacora
                base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "BitacorasTFC")
                os.makedirs(base, exist_ok=True)
                ruta = os.path.join(base, f"Bitacora_{row_full[1]}.pdf")
                datos_tfc = {
                    "num_bitacora":            row_full[1],
                    "folio":                  row_full[2],
                    "anio":                   row_full[3],
                    "fecha":                  row_full[4],
                    "hora":                   row_full[5],
                    "sitio_predio":           row_full[6],
                    "poa_codigo":             row_full[7],
                    "tfc_nombre":             row_full[8],
                    "tfc_registro":           row_full[9],
                    "actividad_tipo":        row_full[10],
                    "detalles_tecnicos":      row_full[11],
                    "volumen_m3":             row_full[12],
                    "plagas_observadas":      row_full[13],
                    "cumplimiento_ambiental": row_full[14],
                    "comentarios":            row_full[15],
                    "scan_plan_manejo":       row_full[24] if len(row_full) > 24 else "",
                    "scan_poa":               row_full[25] if len(row_full) > 25 else "",
                    "scan_resolucion":        row_full[26] if len(row_full) > 26 else "",
                    "estado":                 row_full[21],
                }
                generar_pdf_bitacora(ruta, datos_tfc)
                if os.path.exists(ruta): os.startfile(ruta)

        btn_fg = V_MED if p["tipo"] == "FEMA" else VERDE_M
        btn_hover = V_OSC if p["tipo"] == "FEMA" else VERDE_OSC
        ctk.CTkButton(self.detail_frame, text="📄 Abrir PDF Oficial", font=("Segoe UI", 11, "bold"), height=26, fg_color=btn_fg, hover_color=btn_hover, text_color=BLANCO, command=abrir_doc).grid(row=13, column=0, columnspan=2, pady=(10,12))

    def _mostrar_tooltip(self, p, x, y):
        self.canvas.delete("tooltip")
        
        # Texto del tooltip
        lbl_pref = "Acta FEMA" if p["tipo"] == "FEMA" else "Bitácora TFC"
        text = f"{lbl_pref} No. {p['registro']}\nPredio: {p['predio'][:30]}\nActividad: {p['actividad'][:30]}"
        if p["tipo"] == "TFC" and p["volumen"] > 0:
            text += f"\nVolumen: {float(p['volumen']):,.2f} m³"
            
        # Evitar excepciones si las coordenadas UTM son None
        utm_z = p['utm_z'] or "16N"
        e_val = f"{p['utm_e']:,.1f}" if p['utm_e'] is not None else "—"
        n_val = f"{p['utm_n']:,.1f}" if p['utm_n'] is not None else "—"
        text += f"\nUTM: {utm_z} - E:{e_val}, N:{n_val}"

        # Dibujar tooltip flotante
        tw = 220
        th = 85
        
        # Ajustar coordenadas si se sale del canvas
        cw = self.canvas.winfo_width()
        tx = x + 12
        if tx + tw > cw:
            tx = x - tw - 12
        ty = y - th / 2

        # Rectángulo de fondo
        self.canvas.create_rectangle(
            tx, ty, tx + tw, ty + th,
            fill="#1E293B", outline=V_CLR, width=1,
            tags="tooltip"
        )
        # Texto
        self.canvas.create_text(
            tx + 10, ty + 8,
            text=text, font=("Segoe UI", 9), fill="white", anchor="nw",
            justify=tk.LEFT, tags="tooltip"
        )
