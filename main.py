"""
SilvaDesk Pro
Sistema de Gestión Forestal Profesional
SEDCAF · Sección Técnica Ambiental · Fiscalía de Medio Ambiente · Honduras
COLPROFORH Arancel 2024 – La Gaceta No. 36,609
"""
import sys, os
BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from PIL import Image
import db
db.init_db()
from utils import license as lic

ctk.set_appearance_mode("light")
V_OSC="#005FB8"; V_MED="#0078D4"; V_CLR="#DDEEFF"; BLANCO="#FFFFFF"; GRIS_F="#F2F5F0"

class SilvaDeskApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SilvaDesk Pro – Sistema de Gestión Forestal")
        self.geometry("1300x760"); self.minsize(1100,650)
        self.configure(fg_color=GRIS_F)

        # ── Estado de licencia ──────────────────────────────────────────────────
        self.license_state = lic.get_license_state()
        self.trial_days    = lic.get_trial_days_remaining()

        # Ícono de la ventana y la barra de tareas de Windows
        ico_path = os.path.join(BASE, "assets", "icon.ico")
        if os.path.exists(ico_path):
            self.iconbitmap(ico_path)

        self.grid_columnconfigure(0,weight=1); self.grid_rowconfigure(1,weight=1)
        self._build_header(); self._build_statusbar(); self._build_tabs()

        # Abrir maximizado en la pantalla activa (Windows)
        self.after(10, lambda: self.state("zoomed"))


    def _build_header(self):
        hdr=ctk.CTkFrame(self,fg_color=V_OSC,corner_radius=0,height=70)
        hdr.grid(row=0,column=0,sticky="ew"); hdr.grid_propagate(False)
        hdr.grid_columnconfigure(1,weight=1)

        # Logo (árbol forestal blanco) en el header
        logo_path = os.path.join(BASE, "assets", "icon_header.png")
        try:
            pil_img = Image.open(logo_path).convert("RGBA")
            self.ctk_logo = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(48, 48))
            ctk.CTkLabel(hdr, image=self.ctk_logo, text="", width=60).grid(row=0, column=0, rowspan=2, padx=(14,4), pady=10)
        except Exception:
            # Fallback al emoji si falla la imagen
            ctk.CTkLabel(hdr, text="🌿", font=("Segoe UI Emoji", 30), text_color=BLANCO, width=60).grid(row=0, column=0, rowspan=2, padx=(18,6), pady=10)

        ctk.CTkLabel(hdr,text="SilvaDesk Pro",font=("Segoe UI",22,"bold"),text_color=BLANCO,anchor="w").grid(row=0,column=1,sticky="sw",padx=4,pady=(12,0))
        ctk.CTkLabel(hdr,text="Sistema de Gestión Forestal Profesional  ·  SEDCAF  ·  COLPROFORH N.° 0226",font=("Segoe UI",10),text_color="#E0EEFA",anchor="w").grid(row=1,column=1,sticky="nw",padx=4,pady=(0,10))
        ctk.CTkLabel(hdr,text="v1.0.0",font=("Segoe UI",9),text_color="#B4D6FA",anchor="e").grid(row=0,column=2,rowspan=2,padx=(4,4),sticky="e")

        # ── Badge de estado de licencia ─────────────────────────────────────────
        if self.license_state == "LICENSED":
            badge_txt = "✓ LICENCIADO"
            badge_fg  = "#1a6b2e"
            badge_bg  = "#c8f0d0"
        elif self.license_state == "TRIAL_ACTIVE":
            badge_txt = f"🕐 PRUEBA · {self.trial_days}d"
            badge_fg  = "#7a4b00"
            badge_bg  = "#fff0c0"
        else:
            badge_txt = "⚠ PRUEBA VENCIDA"
            badge_fg  = "#7a0000"
            badge_bg  = "#ffe0e0"

        self.lbl_badge = ctk.CTkLabel(
            hdr, text=badge_txt,
            font=("Segoe UI", 9, "bold"),
            text_color=badge_fg,
            fg_color=badge_bg,
            corner_radius=6,
            padx=8, pady=2
        )
        self.lbl_badge.grid(row=1, column=2, padx=(4, 14), pady=(0, 8), sticky="e")

    # ══════════════════════════════════════════════════════════════════════════
    # SISTEMA DE LICENCIAS
    # ══════════════════════════════════════════════════════════════════════════

    def refresh_license(self):
        """Re-evalúa el estado de licencia y actualiza el badge del header."""
        self.license_state = lic.get_license_state()
        self.trial_days    = lic.get_trial_days_remaining()
        if self.license_state == "LICENSED":
            self.lbl_badge.configure(text="✓ LICENCIADO",
                                     text_color="#1a6b2e", fg_color="#c8f0d0")
        elif self.license_state == "TRIAL_ACTIVE":
            self.lbl_badge.configure(text=f"🕐 PRUEBA · {self.trial_days}d",
                                     text_color="#7a4b00", fg_color="#fff0c0")
        else:
            self.lbl_badge.configure(text="⚠ PRUEBA VENCIDA",
                                     text_color="#7a0000", fg_color="#ffe0e0")

    def check_record_limit(self, current_count: int, module_name: str = "este módulo") -> bool:
        """
        Verifica si se puede crear un nuevo registro.
        Retorna True si está permitido, False si se alcanzó el límite.
        En modo LICENSED o TRIAL_ACTIVE no hay restricción.
        En modo TRIAL_EXPIRED bloquea al superar FREE_LIMIT registros.
        """
        if self.license_state != "TRIAL_EXPIRED":
            return True
        if current_count < lic.FREE_LIMIT:
            return True
        # Mostrar diálogo de activación
        self._dialogo_activacion(
            f"Has alcanzado el límite de {lic.FREE_LIMIT} registros en {module_name}.\n"
            f"Activa tu licencia para uso ilimitado."
        )
        return False

    def _dialogo_activacion(self, mensaje: str = ""):
        """Diálogo de activación de licencia."""
        dlg = ctk.CTkToplevel(self)
        dlg.title("🔑 Activar SilvaDesk Pro")
        dlg.geometry("520x420")
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.configure(fg_color=GRIS_F)

        # Header
        hdr = ctk.CTkFrame(dlg, fg_color="#8B1A1A", corner_radius=0, height=52)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="🔑  Activar Licencia – SilvaDesk Pro",
                     font=("Segoe UI", 14, "bold"), text_color=BLANCO).pack(pady=14)

        body = ctk.CTkFrame(dlg, fg_color=GRIS_F)
        body.pack(fill="both", expand=True, padx=24, pady=16)

        if mensaje:
            ctk.CTkLabel(body, text=mensaje,
                         font=("Segoe UI", 12), text_color="#8B1A1A",
                         wraplength=440, justify="left").pack(anchor="w", pady=(0, 12))

        # Hardware ID
        hid = lic.get_hardware_id()
        ctk.CTkLabel(body, text="Tu ID de Hardware (envíalo a SEDCAF para obtener tu clave):",
                     font=("Segoe UI", 11, "bold"), text_color="#333").pack(anchor="w")

        frm_hid = ctk.CTkFrame(body, fg_color=BLANCO, border_color="#C0D4EC",
                                border_width=1, corner_radius=6)
        frm_hid.pack(fill="x", pady=(4, 14))
        frm_hid.columnconfigure(0, weight=1)

        lbl_hid = ctk.CTkLabel(frm_hid, text=hid,
                                font=("Courier New", 16, "bold"), text_color=V_OSC)
        lbl_hid.grid(row=0, column=0, padx=16, pady=10, sticky="w")

        def _copiar_hid():
            self.clipboard_clear(); self.clipboard_append(hid)
            btn_copy.configure(text="✓ Copiado")
            dlg.after(1800, lambda: btn_copy.configure(text="📋 Copiar ID"))

        btn_copy = ctk.CTkButton(frm_hid, text="📋 Copiar ID", command=_copiar_hid,
                                  fg_color=V_MED, hover_color=V_OSC, text_color=BLANCO,
                                  font=("Segoe UI", 11, "bold"), width=110, height=28,
                                  corner_radius=5)
        btn_copy.grid(row=0, column=1, padx=10, pady=6)

        # Campo para ingresar clave
        ctk.CTkLabel(body, text="Clave de Activación:",
                     font=("Segoe UI", 11, "bold"), text_color="#333").pack(anchor="w")
        e_key = ctk.CTkEntry(body, height=34, font=("Courier New", 14),
                              fg_color=BLANCO, border_color=V_MED,
                              placeholder_text="XXXXX-XXXXX-XXXXX-XXXXX",
                              text_color="#111")
        e_key.pack(fill="x", pady=(4, 16))

        # Botones
        frm_btns = ctk.CTkFrame(body, fg_color=GRIS_F)
        frm_btns.pack(fill="x")

        def _activar():
            key = e_key.get().strip()
            if not key:
                messagebox.showwarning("SilvaDesk Pro", "Ingresa la clave de activación."); return
            if lic.verify_key(key):
                lic.save_license(key)
                self.refresh_license()
                messagebox.showinfo("SilvaDesk Pro",
                                    "✓ ¡Licencia activada correctamente!\n"
                                    "SilvaDesk Pro está ahora desbloqueado sin restricciones.")
                dlg.destroy()
            else:
                messagebox.showerror("SilvaDesk Pro",
                                     "Clave incorrecta. Verifica que el ID de Hardware\n"
                                     "enviado a SEDCAF sea exactamente el que aparece arriba.")

        ctk.CTkButton(frm_btns, text="🔑  Activar Ahora", command=_activar,
                      fg_color=V_OSC, hover_color="#004490", text_color=BLANCO,
                      font=("Segoe UI", 13, "bold"), height=34, corner_radius=6
                      ).pack(side="left")
        ctk.CTkButton(frm_btns, text="Cancelar", command=dlg.destroy,
                      fg_color="#888", hover_color="#666", text_color=BLANCO,
                      font=("Segoe UI", 12), height=34, width=90, corner_radius=6
                      ).pack(side="left", padx=10)

    def _build_tabs(self):
        self.tabview=ctk.CTkTabview(self,fg_color=BLANCO,
            segmented_button_fg_color=V_MED,segmented_button_selected_color=V_OSC,
            segmented_button_selected_hover_color=V_OSC,segmented_button_unselected_color=V_MED,
            segmented_button_unselected_hover_color="#006CC4",text_color=BLANCO,
            corner_radius=8,border_width=1,border_color="#C0D4EC")
        self.tabview._segmented_button.configure(font=("Segoe UI", 13, "bold"))
        self.tabview.grid(row=1,column=0,sticky="nsew",padx=12,pady=(8,4))
        for lbl in [
            "⚖️  Protocolo Judicial (FEMA)", 
            "🌲  Bitácora de Campo (TFC)", 
            "📊  Dashboard Dinámico",
            "🗺️  Mapa de Predios", 
            "✍️  Biblioteca de Contratos",
            "🧾  Facturador", 
            "💵  Finanzas y Pagos",
            "🌿  Calculadora Arancel",
            "❓  Ayuda TFC", 
            "ℹ️  Acerca de"
        ]:
            self.tabview.add(lbl)
            
        from tabs.bitacora import BitacoraTab
        from tabs.bitacora_tfc import BitacoraTFCTab
        from tabs.dashboard import DashboardTab
        from tabs.mapa import MapaTab
        from tabs.contratos import ContratosTab
        from tabs.facturador import FacturadorTab
        from tabs.finanzas import FinanzasTab
        from tabs.calculadora import CalculadoraTab
        from tabs.ayuda_tfc import AyudaTFCTab
        
        BitacoraTab(self.tabview.tab("⚖️  Protocolo Judicial (FEMA)"), self)
        BitacoraTFCTab(self.tabview.tab("🌲  Bitácora de Campo (TFC)"), self)
        DashboardTab(self.tabview.tab("📊  Dashboard Dinámico"), self)
        MapaTab(self.tabview.tab("🗺️  Mapa de Predios"), self)
        ContratosTab(self.tabview.tab("✍️  Biblioteca de Contratos"), self)
        FacturadorTab(self.tabview.tab("🧾  Facturador"), self)
        FinanzasTab(self.tabview.tab("💵  Finanzas y Pagos"), self)
        CalculadoraTab(self.tabview.tab("🌿  Calculadora Arancel"), self)
        AyudaTFCTab(self.tabview.tab("❓  Ayuda TFC"), self)
        self._build_about(self.tabview.tab("ℹ️  Acerca de"))

    def _build_statusbar(self):
        bar=ctk.CTkFrame(self,fg_color=V_OSC,corner_radius=0,height=22)
        bar.grid(row=2,column=0,sticky="ew"); bar.grid_propagate(False); bar.grid_columnconfigure(0,weight=1)
        self.status_var=tk.StringVar(value="Listo  ·  SilvaDesk Pro")
        ctk.CTkLabel(bar,textvariable=self.status_var,font=("Segoe UI",9),text_color="#E0EEFA",anchor="w").grid(row=0,column=0,padx=10,sticky="w")

    def set_status(self,msg): self.status_var.set(msg)

    def _build_about(self,parent):
        parent.grid_columnconfigure(0,weight=1); parent.grid_rowconfigure(0,weight=1)
        self.frm_about=ctk.CTkScrollableFrame(parent,fg_color=GRIS_F)
        self.frm_about.grid(row=0,column=0,sticky="nsew",padx=20,pady=20)
        self.frm_about.grid_columnconfigure(0,weight=1)

        # Logo circular en Acerca de
        logo_path = os.path.join(BASE, "assets", "icon_blue.png")
        try:
            pil_logo = Image.open(logo_path).convert("RGBA")
            self.ctk_about_logo = ctk.CTkImage(light_image=pil_logo, dark_image=pil_logo, size=(100, 100))
            ctk.CTkLabel(self.frm_about, image=self.ctk_about_logo, text="").grid(pady=(10,6))
        except Exception:
            pass

        ctk.CTkLabel(self.frm_about, text="SilvaDesk Pro", font=("Segoe UI", 26, "bold"), text_color=V_OSC, anchor="w").grid(sticky="w", padx=20, pady=1)
        ctk.CTkLabel(self.frm_about, text="Sistema de Gestión Forestal Profesional", font=("Segoe UI", 13), text_color=V_MED, anchor="w").grid(sticky="w", padx=20, pady=1)
        ctk.CTkLabel(self.frm_about, text="", height=8).grid(sticky="w")
        ctk.CTkLabel(self.frm_about, text="Versión 1.0.0", font=("Segoe UI", 11), text_color="#555555", anchor="w").grid(sticky="w", padx=20, pady=1)

        self.lbl_empresa = ctk.CTkLabel(self.frm_about, text="", font=("Segoe UI", 11), text_color="#333", anchor="w")
        self.lbl_empresa.grid(sticky="w", padx=20, pady=1)

        ctk.CTkLabel(self.frm_about, text="Arancel COLPROFORH - La Gaceta No. 36,609 (10/08/2024)", font=("Segoe UI", 11), text_color="#333", anchor="w").grid(sticky="w", padx=20, pady=1)
        ctk.CTkLabel(self.frm_about, text="", height=8).grid(sticky="w")

        self.lbl_profesional = ctk.CTkLabel(self.frm_about, text="", font=("Segoe UI", 12, "bold"), text_color=V_OSC, anchor="w")
        self.lbl_profesional.grid(sticky="w", padx=20, pady=1)

        self.lbl_registro = ctk.CTkLabel(self.frm_about, text="", font=("Segoe UI", 11), text_color="#555", anchor="w")
        self.lbl_registro.grid(sticky="w", padx=20, pady=1)

        self._actualizar_about()

        ctk.CTkLabel(self.frm_about, text="", height=15).grid(sticky="w")
        ctk.CTkButton(self.frm_about, text="⚙️  Configurar Empresa / Licencia",
                      command=self._dialogo_configuracion,
                      fg_color=V_MED, hover_color=V_OSC, text_color=BLANCO,
                      font=("Segoe UI", 13, "bold"), height=32, corner_radius=5
        ).grid(sticky="w", padx=20, pady=(10, 4))

        # ── Sección de licencia ─────────────────────────────────────────────────
        ctk.CTkLabel(self.frm_about, text="", height=6).grid(sticky="w")
        ctk.CTkLabel(self.frm_about, text="Estado de Licencia",
                     font=("Segoe UI", 12, "bold"), text_color=V_OSC,
                     anchor="w").grid(sticky="w", padx=20, pady=(4, 2))

        # Badge de estado
        if self.license_state == "LICENSED":
            lic_txt, lic_col = "✓ Licencia Activa – Uso ilimitado", "#1a6b2e"
        elif self.license_state == "TRIAL_ACTIVE":
            lic_txt = f"🕐 Versión de Prueba – {self.trial_days} días restantes de {lic.TRIAL_DAYS}"
            lic_col = "#7a4b00"
        else:
            lic_txt, lic_col = "⚠ Período de Prueba Vencido – Módulos limitados a 5 registros", "#8B1A1A"

        self.lbl_lic_estado = ctk.CTkLabel(
            self.frm_about, text=lic_txt,
            font=("Segoe UI", 11), text_color=lic_col, anchor="w")
        self.lbl_lic_estado.grid(sticky="w", padx=20, pady=1)

        # Hardware ID
        ctk.CTkLabel(self.frm_about, text=f"ID de Hardware:  {lic.get_hardware_id()}",
                     font=("Courier New", 11), text_color="#444", anchor="w"
                     ).grid(sticky="w", padx=20, pady=4)

        # Botón activar (siempre visible para ingresar o cambiar clave)
        ctk.CTkButton(self.frm_about, text="🔑  Activar Licencia",
                      command=self._dialogo_activacion,
                      fg_color="#8B1A1A" if self.license_state == "TRIAL_EXPIRED" else V_OSC,
                      hover_color="#6a0000" if self.license_state == "TRIAL_EXPIRED" else "#004490",
                      text_color=BLANCO,
                      font=("Segoe UI", 13, "bold"), height=32, corner_radius=5
        ).grid(sticky="w", padx=20, pady=8)

    def _actualizar_about(self):
        conf = db.config_obtener()
        self.lbl_empresa.configure(text=conf[1])
        self.lbl_profesional.configure(text=conf[2])
        self.lbl_registro.configure(text=conf[3])

    def _dialogo_configuracion(self):
        conf = db.config_obtener()

        dlg = ctk.CTkToplevel(self)
        dlg.title("Configuración de Datos de Licencia / Empresa")
        dlg.geometry("560x680")
        dlg.minsize(520, 640)
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.configure(fg_color=GRIS_F)

        # Header
        hdr = ctk.CTkFrame(dlg, fg_color=V_OSC, corner_radius=0, height=50)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="⚙️  Configuración General del Sistema", font=("Segoe UI", 14, "bold"), text_color=BLANCO).pack(pady=12)

        # Área scrollable para todo el contenido
        scroll = ctk.CTkScrollableFrame(dlg, fg_color=GRIS_F)
        scroll.pack(fill="both", expand=True, padx=0, pady=0)
        scroll.columnconfigure(1, weight=1)

        # ── Sección datos de empresa ───────────────────────────────────────────
        ctk.CTkLabel(scroll, text="Datos de la Empresa / Profesional",
                     font=("Segoe UI", 12, "bold"), text_color=V_OSC,
                     anchor="w").grid(row=0, column=0, columnspan=2,
                                      sticky="w", padx=16, pady=(14, 4))

        def lbl(r, t):
            ctk.CTkLabel(scroll, text=t, font=("Segoe UI", 12, "bold"),
                         text_color="#333", anchor="e"
                         ).grid(row=r, column=0, sticky="e", padx=(10, 8), pady=5)

        def ent(r, val):
            e = ctk.CTkEntry(scroll, height=28, fg_color=BLANCO,
                              border_color=V_OSC, text_color="#111",
                              font=("Segoe UI", 12))
            e.insert(0, val or "")
            e.grid(row=r, column=1, sticky="ew", padx=(0, 16), pady=5)
            return e

        lbl(1, "Nombre de Empresa:")
        e_emp = ent(1, conf[1])
        lbl(2, "Nombre Profesional:")
        e_prof = ent(2, conf[2])
        lbl(3, "Registro Profesional:")
        e_reg = ent(3, conf[3])
        lbl(4, "RTN Emisor:")
        e_rtn = ent(4, conf[4])
        lbl(5, "Dirección Emisor:")
        e_dir = ent(5, conf[5])
        lbl(6, "Teléfono Emisor:")
        e_tel = ent(6, conf[6])

        # Botón técnicos
        ctk.CTkButton(scroll, text="👥  Administrar Técnicos Asociados",
                      command=self._administrar_tecnicos_global,
                      fg_color=V_MED, hover_color=V_OSC, text_color=BLANCO,
                      font=("Segoe UI", 12, "bold"), height=32, corner_radius=5
                      ).grid(row=7, column=0, columnspan=2,
                             pady=(14, 4), padx=16, sticky="ew")

        # ── Separador ──────────────────────────────────────────────────────────
        sep = ctk.CTkFrame(scroll, fg_color="#C0D4EC", height=2)
        sep.grid(row=8, column=0, columnspan=2, sticky="ew", padx=16, pady=(18, 10))

        # ── Sección de licencia ────────────────────────────────────────────────
        ctk.CTkLabel(scroll, text="🔑  Activación de Licencia",
                     font=("Segoe UI", 12, "bold"), text_color=V_OSC,
                     anchor="w").grid(row=9, column=0, columnspan=2,
                                      sticky="w", padx=16, pady=(0, 4))

        # Estado actual
        if self.license_state == "LICENSED":
            est_txt, est_col = "✓ Licencia Activa – Uso ilimitado", "#107C10"
        elif self.license_state == "TRIAL_ACTIVE":
            est_txt = f"🕐 Versión de Prueba – {self.trial_days} días restantes"
            est_col = "#7a4b00"
        else:
            est_txt, est_col = "⚠ Prueba Vencida – Módulos limitados a 5 registros", "#8B1A1A"

        ctk.CTkLabel(scroll, text=est_txt, font=("Segoe UI", 11),
                     text_color=est_col, anchor="w"
                     ).grid(row=10, column=0, columnspan=2,
                            sticky="w", padx=16, pady=(0, 8))

        # Hardware ID
        hid = lic.get_hardware_id()
        ctk.CTkLabel(scroll, text="ID de Hardware:",
                     font=("Segoe UI", 12, "bold"), text_color="#333",
                     anchor="e").grid(row=11, column=0, sticky="e",
                                      padx=(10, 8), pady=4)

        frm_hid = ctk.CTkFrame(scroll, fg_color=BLANCO,
                                border_color="#C0D4EC", border_width=1,
                                corner_radius=6)
        frm_hid.grid(row=11, column=1, sticky="ew", padx=(0, 16), pady=4)
        frm_hid.columnconfigure(0, weight=1)

        ctk.CTkLabel(frm_hid, text=hid, font=("Courier New", 13, "bold"),
                     text_color=V_OSC, anchor="w"
                     ).grid(row=0, column=0, padx=10, pady=6, sticky="w")

        def _copiar_hid():
            self.clipboard_clear(); self.clipboard_append(hid)
            btn_chid.configure(text="✓")
            dlg.after(1800, lambda: btn_chid.configure(text="📋"))

        btn_chid = ctk.CTkButton(frm_hid, text="📋", width=32, height=24,
                                  command=_copiar_hid,
                                  fg_color=V_MED, hover_color=V_OSC,
                                  text_color=BLANCO, corner_radius=4,
                                  font=("Segoe UI", 11))
        btn_chid.grid(row=0, column=1, padx=(4, 8), pady=4)

        # Campo clave de activación
        ctk.CTkLabel(scroll, text="Clave de Activación:",
                     font=("Segoe UI", 12, "bold"), text_color="#333",
                     anchor="e").grid(row=12, column=0, sticky="e",
                                      padx=(10, 8), pady=4)

        e_key = ctk.CTkEntry(scroll, height=30,
                              font=("Courier New", 13),
                              fg_color=BLANCO, border_color=V_MED,
                              placeholder_text="XXXXX-XXXXX-XXXXX-XXXXX",
                              text_color="#111")
        e_key.grid(row=12, column=1, sticky="ew", padx=(0, 16), pady=4)

        lbl_key_err = ctk.CTkLabel(scroll, text="",
                                    font=("Segoe UI", 10),
                                    text_color="#8B1A1A", anchor="w")
        lbl_key_err.grid(row=13, column=1, sticky="w", padx=(0, 16))

        def _activar():
            key = e_key.get().strip()
            if not key:
                lbl_key_err.configure(text="⚠  Ingresa la clave de activación.")
                return
            if lic.verify_key(key):
                lic.save_license(key)
                self.refresh_license()
                messagebox.showinfo("SilvaDesk Pro",
                                    "✓ ¡Licencia activada correctamente!\n"
                                    "SilvaDesk Pro está ahora desbloqueado.")
                dlg.destroy()
            else:
                lbl_key_err.configure(
                    text="⚠  Clave incorrecta. Verifica el ID enviado a SEDCAF.")

        ctk.CTkButton(scroll, text="🔑  Activar Licencia",
                      command=_activar,
                      fg_color="#8B1A1A" if self.license_state == "TRIAL_EXPIRED" else V_OSC,
                      hover_color="#6a0000" if self.license_state == "TRIAL_EXPIRED" else "#004490",
                      text_color=BLANCO,
                      font=("Segoe UI", 12, "bold"), height=32, corner_radius=5
                      ).grid(row=14, column=0, columnspan=2,
                             sticky="w", padx=16, pady=(10, 18))

        # ── Botones inferiores ─────────────────────────────────────────────────
        btn_frame = ctk.CTkFrame(dlg, fg_color="#E8ECF0", height=50, corner_radius=0)
        btn_frame.pack(fill="x", side="bottom")

        def guardar():
            db.config_guardar(
                e_emp.get().strip(),
                e_prof.get().strip(),
                e_reg.get().strip(),
                e_rtn.get().strip(),
                e_dir.get().strip(),
                e_tel.get().strip()
            )
            self._actualizar_about()
            messagebox.showinfo("SilvaDesk Pro",
                                "Configuración guardada correctamente.")
            dlg.destroy()

        ctk.CTkButton(btn_frame, text="💾  Guardar", command=guardar,
                      fg_color=V_OSC, hover_color="#00488F", text_color=BLANCO,
                      font=("Segoe UI", 13, "bold"), width=120, height=32,
                      corner_radius=5).pack(side="left", padx=(140, 6), pady=9)

        ctk.CTkButton(btn_frame, text="Cancelar", command=dlg.destroy,
                      fg_color="#888", hover_color="#666", text_color=BLANCO,
                      font=("Segoe UI", 13), width=100, height=32,
                      corner_radius=5).pack(side="left", padx=6, pady=9)

    def _administrar_tecnicos_global(self):
        dlg = ctk.CTkToplevel(self)
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

if __name__=="__main__":
    app=SilvaDeskApp(); app.mainloop()
