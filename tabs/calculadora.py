"""tabs/calculadora.py – Calculadora Arancel COLPROFORH 2024 · SilvaDesk Pro"""
import tkinter as tk
import customtkinter as ctk
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

V_OSC="#005FB8"; V_MED="#0078D4"; V_CLR="#DDEEFF"; BLANCO="#FFFFFF"
AMARILL="#FFF2CC"; GRIS_F="#F2F5F0"; AZL_C="#DCE6F1"; ROJO_C="#FCE4D6"; VERDE_R="#E8F0FB"; MORADO="#7D3C98"

def _rr(p,r,lbl,var,bg=VERDE_R,fc=V_OSC,bold=False):
    fn=("Segoe UI",13,"bold") if bold else ("Segoe UI",13)
    ctk.CTkLabel(p,text=lbl,font=("Segoe UI",13),text_color="#444",anchor="e").grid(row=r,column=0,sticky="e",padx=(10,6),pady=2)
    ctk.CTkLabel(p,textvariable=var,font=fn,text_color=fc,anchor="center",fg_color=bg,corner_radius=4,width=200,height=26).grid(row=r,column=1,sticky="w",padx=(0,10),pady=2)

class CalculadoraTab:
    def __init__(self,parent,app):
        self.parent=parent; self.app=app
        self.parent.grid_columnconfigure(0,weight=1); self.parent.grid_columnconfigure(1,weight=1); self.parent.grid_rowconfigure(0,weight=1)
        left=ctk.CTkScrollableFrame(parent,fg_color=GRIS_F,corner_radius=6); left.grid(row=0,column=0,sticky="nsew",padx=(6,3),pady=6); left.grid_columnconfigure(0,weight=1)
        right=ctk.CTkScrollableFrame(parent,fg_color=GRIS_F,corner_radius=6); right.grid(row=0,column=1,sticky="nsew",padx=(3,6),pady=6); right.grid_columnconfigure(0,weight=1)
        r=[0]
        def nrow(): v=r[0]; r[0]+=1; return v
        self._sec1(left,nrow); self._sec2(left,nrow); self._sec3(left,nrow); self._sec4(left,nrow)
        r[0]=0
        self._sec5(right,nrow); self._sec6(right,nrow); self._sec7(right,nrow); self._sec8(right,nrow); self._nota(right,nrow)

    def _hdr(self,p,r,t,col=V_MED):
        f=ctk.CTkFrame(p,fg_color=col,corner_radius=5,height=32); f.grid(row=r,column=0,sticky="ew",padx=4,pady=(10,4)); f.grid_propagate(False)
        ctk.CTkLabel(f,text=f"  {t}",font=("Segoe UI",14,"bold"),text_color=BLANCO,anchor="w").pack(side="left",padx=10)

    def _card(self,p,r):
        f=ctk.CTkFrame(p,fg_color=BLANCO,corner_radius=6,border_width=1,border_color="#C0D4EC")
        f.grid(row=r,column=0,sticky="ew",padx=4,pady=(0,4)); f.grid_columnconfigure(1,weight=1); return f

    def _inp(self,f,r,lbl,var,nota="",w=160):
        ctk.CTkLabel(f,text=lbl,font=("Segoe UI",13),text_color="#333",anchor="e",width=200).grid(row=r,column=0,sticky="e",padx=(10,6),pady=4)
        ctk.CTkEntry(f,textvariable=var,width=w,height=30,fg_color=AMARILL,border_color=V_OSC,text_color="#7F6000",font=("Segoe UI",13,"bold")).grid(row=r,column=1,sticky="w",padx=(0,6),pady=4)
        if nota: ctk.CTkLabel(f,text=nota,font=("Segoe UI",12,"italic"),text_color=V_MED,anchor="w").grid(row=r,column=2,sticky="w",padx=4)

    def _combo(self,f,r,lbl,var,vals,nota=""):
        ctk.CTkLabel(f,text=lbl,font=("Segoe UI",13),text_color="#333",anchor="e",width=200).grid(row=r,column=0,sticky="e",padx=(10,6),pady=4)
        cb=ctk.CTkComboBox(f,variable=var,values=vals,width=200,height=30,fg_color=AMARILL,text_color="#7F6000",border_color=V_OSC,button_color=V_OSC,font=("Segoe UI",13),dropdown_font=("Segoe UI", 13)); cb.grid(row=r,column=1,sticky="w",padx=(0,6),pady=4)
        if nota: ctk.CTkLabel(f,text=nota,font=("Segoe UI",12,"italic"),text_color=V_MED,anchor="w").grid(row=r,column=2,sticky="w",padx=4)
        return cb

    def _blq(self,f,r,v_b,v_i,v_t,v_r,v_n):
        ctk.CTkFrame(f,fg_color=V_CLR,height=1).grid(row=r,column=0,columnspan=3,sticky="ew",padx=10,pady=(6,2))
        _rr(f,r+1,"→ Honorario base:",v_b,VERDE_R,V_OSC)
        _rr(f,r+2,"→ + ISV 15% (al cliente):",v_i,AZL_C,"#1F4E79")
        _rr(f,r+3,"→ TOTAL A FACTURAR:",v_t,"#B8D4E8","#1F4E79",bold=True)
        _rr(f,r+4,"→ – ISR 12.5% (cliente retiene):",v_r,ROJO_C,"#C0504D")
        _rr(f,r+5,"→ NETO A RECIBIR:",v_n,VERDE_R,V_OSC,bold=True)

    def _set(self,base,vb,vi,vt,vr,vn):
        i=base*0.15; t=base+i; r=base*0.125; n=t-r
        vb.set(f"L. {base:>14,.2f}"); vi.set(f"L. {i:>14,.2f}"); vt.set(f"L. {t:>14,.2f}"); vr.set(f"(L. {r:>12,.2f})"); vn.set(f"L. {n:>14,.2f}")

    def _sec1(self,p,nrow):
        self._hdr(p,nrow(),"1. CONSULTORÍA POR HORA (Ing. Universitario – Cat. C)")
        f=self._card(p,nrow())
        self.h_tar=tk.DoubleVar(value=722.66); self.h_hor=tk.DoubleVar(value=8.0); self.h_mov=tk.DoubleVar(value=500.0)
        self.h_b,self.h_i,self.h_t,self.h_r,self.h_n=[tk.StringVar() for _ in range(5)]
        self._inp(f,0,"Tarifa base / hora (L.):",self.h_tar,"Cat.C=L.722.66"); self._inp(f,1,"Número de horas:",self.h_hor,"Mín. 2 (Art.9)"); self._inp(f,2,"Movilización (L.):",self.h_mov)
        for v in [self.h_tar,self.h_hor,self.h_mov]: v.trace_add("write",lambda *_:self._c1())
        self._blq(f,3,self.h_b,self.h_i,self.h_t,self.h_r,self.h_n); self._c1()
    def _c1(self):
        try: self._set(self.h_tar.get()*self.h_hor.get()+self.h_mov.get(),self.h_b,self.h_i,self.h_t,self.h_r,self.h_n)
        except: pass

    def _sec2(self,p,nrow):
        self._hdr(p,nrow(),"2. PLAN DE MANEJO FORESTAL (PMF)")
        f=self._card(p,nrow())
        self.p_vol=tk.DoubleVar(value=500.0); self.p_may=tk.StringVar(value="No (< 100 ha)")
        self.p_b,self.p_i,self.p_t,self.p_r,self.p_n=[tk.StringVar() for _ in range(5)]
        self._inp(f,0,"Volumen del plan (m³):",self.p_vol); self._combo(f,1,"¿Propiedad > 100 ha?:",self.p_may,["No (< 100 ha)","Sí (> 100 ha)"],"No→L.120/m³  |  Sí→L.80/m³")
        self.p_vol.trace_add("write",lambda *_:self._c2()); self.p_may.trace_add("write",lambda *_:self._c2())
        self._blq(f,2,self.p_b,self.p_i,self.p_t,self.p_r,self.p_n); self._c2()
    def _c2(self):
        try: self._set(self.p_vol.get()*(80.0 if "Sí" in self.p_may.get() else 120.0),self.p_b,self.p_i,self.p_t,self.p_r,self.p_n)
        except: pass

    def _sec3(self,p,nrow):
        self._hdr(p,nrow(),"3. PLAN OPERATIVO ANUAL (POA)")
        f=self._card(p,nrow())
        self.poa_v=tk.DoubleVar(value=250.0); self.poa_s=tk.StringVar(value="3 – AMBOS (L.270/m³)")
        self.poa_b,self.poa_i,self.poa_t,self.poa_r,self.poa_n=[tk.StringVar() for _ in range(5)]
        self._inp(f,0,"Volumen del POA (m³):",self.poa_v)
        self._combo(f,1,"Servicio:",self.poa_s,["1 – Elaboración (L.150/m³)","2 – Administración (L.120/m³)","3 – AMBOS (L.270/m³)"])
        self.poa_v.trace_add("write",lambda *_:self._c3()); self.poa_s.trace_add("write",lambda *_:self._c3())
        self._blq(f,2,self.poa_b,self.poa_i,self.poa_t,self.poa_r,self.poa_n); self._c3()
    def _c3(self):
        try:
            s=self.poa_s.get(); t=150.0 if "1" in s else (120.0 if "2" in s else 270.0)
            self._set(self.poa_v.get()*t,self.poa_b,self.poa_i,self.poa_t,self.poa_r,self.poa_n)
        except: pass

    def _sec4(self,p,nrow):
        self._hdr(p,nrow(),"4. PERITAJE JUDICIAL / CIVIL O ADMINISTRATIVO")
        f=self._card(p,nrow())
        self.pc_d=tk.DoubleVar(value=200000.0)
        self.pc_b,self.pc_i,self.pc_t,self.pc_r,self.pc_n=[tk.StringVar() for _ in range(5)]
        self._inp(f,0,"Valor total de la demanda (L.):",self.pc_d,"15% s/demanda (Art.12)")
        self.pc_d.trace_add("write",lambda *_:self._c4())
        self._blq(f,1,self.pc_b,self.pc_i,self.pc_t,self.pc_r,self.pc_n)
        ctk.CTkLabel(f,text="⚠  Solo en casos CIVILES o ADMINISTRATIVOS. NO aplica en proceso penal.",font=("Segoe UI",12,"italic"),text_color="#C0504D",anchor="w",wraplength=380).grid(row=7,column=0,columnspan=3,padx=10,pady=(4,8),sticky="w")
        self._c4()
    def _c4(self):
        try: self._set(self.pc_d.get()*0.15,self.pc_b,self.pc_i,self.pc_t,self.pc_r,self.pc_n)
        except: pass

    def _sec5(self,p,nrow):
        self._hdr(p,nrow(),"5. FINIQUITO – REGLA 3×1 (PCM-002-2006)")
        f=self._card(p,nrow())
        self.fin_ha=tk.DoubleVar(value=80.0)
        self.fin_b,self.fin_i,self.fin_t,self.fin_r,self.fin_n=[tk.StringVar() for _ in range(5)]
        self._inp(f,0,"Superficie de la propiedad (ha):",self.fin_ha,"<100ha→L.30,000  |  ≥100→L.50,000")
        self.fin_ha.trace_add("write",lambda *_:self._c5())
        self._blq(f,1,self.fin_b,self.fin_i,self.fin_t,self.fin_r,self.fin_n); self._c5()
    def _c5(self):
        try: self._set(30000.0 if self.fin_ha.get()<100 else 50000.0,self.fin_b,self.fin_i,self.fin_t,self.fin_r,self.fin_n)
        except: pass

    def _sec6(self,p,nrow):
        self._hdr(p,nrow(),"6. ESTABLECIMIENTO / CERTIFICACIÓN DE PLANTACIONES")
        f=self._card(p,nrow())
        self.pl_ha=tk.DoubleVar(value=15.0); self.pl_s=tk.StringVar(value="1 – Establecimiento (L.10,000/ha)")
        self.pl_b,self.pl_i,self.pl_t,self.pl_r,self.pl_n=[tk.StringVar() for _ in range(5)]
        self._inp(f,0,"Hectáreas:",self.pl_ha)
        self._combo(f,1,"Servicio:",self.pl_s,["1 – Establecimiento (L.10,000/ha)","2 – Certificación (1-10ha: L.5,000 | adicional: L.2,000)"])
        self.pl_ha.trace_add("write",lambda *_:self._c6()); self.pl_s.trace_add("write",lambda *_:self._c6())
        self._blq(f,2,self.pl_b,self.pl_i,self.pl_t,self.pl_r,self.pl_n); self._c6()
    def _c6(self):
        try:
            ha=self.pl_ha.get(); b=ha*10000.0 if "1" in self.pl_s.get() else (min(ha,10)*5000+max(0,ha-10)*2000)
            self._set(b,self.pl_b,self.pl_i,self.pl_t,self.pl_r,self.pl_n)
        except: pass

    def _sec7(self,p,nrow):
        self._hdr(p,nrow(),"7. PERITAJE EN PROCESO PENAL  (no aplica 15% s/demanda)",col=MORADO)
        f=self._card(p,nrow())
        ctk.CTkLabel(f,text="⚠  CPP Art.124: cobrar horas + avalúo de volumen ilegal. NO existe 'valor de demanda'.",font=("Segoe UI",12,"italic"),text_color="#7D3C98",anchor="w",wraplength=400).grid(row=0,column=0,columnspan=3,padx=10,pady=(8,4),sticky="w")
        self.pen_h=tk.DoubleVar(value=16.0); self.pen_t=tk.DoubleVar(value=722.66); self.pen_v=tk.DoubleVar(value=50.0); self.pen_tv=tk.DoubleVar(value=300.0); self.pen_m=tk.DoubleVar(value=1500.0)
        self.pen_b,self.pen_i,self.pen_tt,self.pen_r,self.pen_n=[tk.StringVar() for _ in range(5)]
        self._inp(f,1,"Horas invertidas:",self.pen_h,"Campo + análisis + dictamen")
        self._inp(f,2,"Tarifa horaria Cat. C (L.):",self.pen_t)
        self._inp(f,3,"Volumen ilegal (m³):",self.pen_v,"0 si no aplica")
        self._inp(f,4,"Tarifa avalúo (L./m³):",self.pen_tv,"L.300/m³ Arancel")
        self._inp(f,5,"Movilización / viáticos (L.):",self.pen_m)
        for v in [self.pen_h,self.pen_t,self.pen_v,self.pen_tv,self.pen_m]: v.trace_add("write",lambda *_:self._c7())
        self._blq(f,6,self.pen_b,self.pen_i,self.pen_tt,self.pen_r,self.pen_n); self._c7()
    def _c7(self):
        try: self._set(self.pen_h.get()*self.pen_t.get()+self.pen_v.get()*self.pen_tv.get()+self.pen_m.get(),self.pen_b,self.pen_i,self.pen_tt,self.pen_r,self.pen_n)
        except: pass


    def _sec8(self,p,nrow):
        AZUL_S="#005FB8"; AZUL_C2="#DCE6F1"; AZUL_R="#EEF3FB"
        self._hdr(p,nrow(),"8. SOFTWARE FORESTAL / AMBIENTAL ESPECIALIZADO",col=AZUL_S)
        f=self._card(p,nrow()); f.grid_columnconfigure(2,weight=0)
        ctk.CTkLabel(f,text=(
            "💻  Honorarios por desarrollo, licencia y mantenimiento de software forestal/ambiental.\n"
            "    Ejemplos: SilvaDesk Pro, Lex Viridis, sistemas SIG, apps de gestión forestal."
        ),font=("Segoe UI",14,"italic"),text_color=AZUL_S,anchor="w",wraplength=420,justify="left"
        ).grid(row=0,column=0,columnspan=3,padx=10,pady=(8,4),sticky="w")

        self.sw_tar  = tk.DoubleVar(value=1500.0)   # tarifa/hora desarrollo
        self.sw_hor  = tk.DoubleVar(value=80.0)     # horas desarrollo
        self.sw_mod  = tk.DoubleVar(value=3.0)      # módulos adicionales
        self.sw_pmod = tk.DoubleVar(value=8000.0)   # precio/módulo
        self.sw_lic  = tk.DoubleVar(value=20000.0)  # licencia perpetua (0 si no aplica)
        self.sw_mant = tk.DoubleVar(value=15.0)     # % mantenimiento anual s/base
        self.sw_mov  = tk.DoubleVar(value=2000.0)   # movilización/viáticos
        self.sw_b,self.sw_i,self.sw_t,self.sw_r,self.sw_n=[tk.StringVar() for _ in range(5)]
        self.sw_mant_v = tk.StringVar()

        self._inp(f,1,"Tarifa hora desarrollo (L.):",  self.sw_tar, "Ingeniería de software forestal")
        self._inp(f,2,"Horas de desarrollo:",          self.sw_hor, "Diseño + codificación + pruebas")
        self._inp(f,3,"Módulos adicionales (cant.):",  self.sw_mod, "Módulos extra al sistema base")
        self._inp(f,4,"Precio por módulo (L.):",       self.sw_pmod,"Por módulo funcional")
        self._inp(f,5,"Licencia perpetua (L.):",       self.sw_lic, "0 si va incluida en desarrollo")
        self._inp(f,6,"Movilización / viáticos (L.):", self.sw_mov)

        ctk.CTkFrame(f,fg_color="#B8CCE4",height=1).grid(row=7,column=0,columnspan=3,sticky="ew",padx=10,pady=(6,2))
        ctk.CTkLabel(f,text="% Mantenimiento anual s/honorario base:",
            font=("Segoe UI",13),text_color="#333",anchor="e",width=200).grid(row=8,column=0,sticky="e",padx=(10,6),pady=4)
        ctk.CTkEntry(f,textvariable=self.sw_mant,width=80,height=30,
            fg_color=AMARILL,border_color=AZUL_S,text_color="#7F6000",font=("Segoe UI",13,"bold")
        ).grid(row=8,column=1,sticky="w",padx=(0,6),pady=4)
        ctk.CTkLabel(f,text="(15-20% anual habitual en software)",
            font=("Segoe UI",12,"italic"),text_color=AZUL_S,anchor="w"
        ).grid(row=8,column=2,sticky="w",padx=4)

        ctk.CTkLabel(f,text="→ Mantenimiento anual (referencial):",
            font=("Segoe UI",13),text_color="#444",anchor="e",width=200
        ).grid(row=9,column=0,sticky="e",padx=(10,6),pady=2)
        ctk.CTkLabel(f,textvariable=self.sw_mant_v,
            font=("Segoe UI",13,"bold"),text_color=AZUL_S,anchor="center",
            fg_color=AZUL_C2,corner_radius=4,width=200,height=26
        ).grid(row=9,column=1,sticky="w",padx=(0,10),pady=2)

        self._blq(f,10,self.sw_b,self.sw_i,self.sw_t,self.sw_r,self.sw_n)
        ctk.CTkLabel(f,
            text="⚑  El total facturado corresponde al desarrollo + módulos + licencia + movilización.\n"
                 "   El mantenimiento anual se factura por separado en años subsiguientes.",
            font=("Segoe UI",12,"italic"),text_color="#555",anchor="w",wraplength=400,justify="left"
        ).grid(row=16,column=0,columnspan=3,padx=10,pady=(4,10),sticky="w")

        for v in [self.sw_tar,self.sw_hor,self.sw_mod,self.sw_pmod,self.sw_lic,self.sw_mant,self.sw_mov]:
            v.trace_add("write",lambda *_:self._c8())
        self._c8()

    def _c8(self):
        try:
            base = (self.sw_tar.get() * self.sw_hor.get()
                    + self.sw_mod.get() * self.sw_pmod.get()
                    + self.sw_lic.get()
                    + self.sw_mov.get())
            mant = base * (self.sw_mant.get() / 100.0)
            self.sw_mant_v.set(f"L. {mant:>12,.2f} / año")
            self._set(base,self.sw_b,self.sw_i,self.sw_t,self.sw_r,self.sw_n)
        except: pass

    def _nota(self,p,nrow):
        f=ctk.CTkFrame(p,fg_color=V_CLR,corner_radius=6,border_width=1,border_color=V_MED); f.grid(row=nrow(),column=0,sticky="ew",padx=4,pady=(10,4))
        ctk.CTkLabel(f,text=("📌  COLPROFORH – La Gaceta No. 36,609 (10/08/2024)\n"
            "ISV 15%: cobrar al cliente, declarar al SAR mensualmente.\n"
            "ISR 12.5%: el cliente retiene – no aparece en factura.\n"
            "Zona especial (Gracias a Dios / Islas Bahía / Iriona): +50% s/base.\n"
            "Reajuste anual enero – IGPC/BCH."),
            font=("Segoe UI",13),text_color=V_OSC,anchor="w",justify="left",wraplength=420).pack(padx=12,pady=8)


    # ─── Sección 8: Software Especializado ────────────────────────────────────
    # (llamar desde __init__ después de _sec7)
