"""db.py – Base de datos SQLite · SilvaDesk Pro"""
import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SilvaDesk.db")

def get_conn(): return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn(); c = conn.cursor()

    # ── Protocolo de actuaciones técnicas ─────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS protocolo (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        num_acta            TEXT NOT NULL,
        folio               INTEGER,
        anio                TEXT,
        fecha               TEXT NOT NULL,
        hora                TEXT,
        lugar               TEXT,
        municipio           TEXT,
        departamento        TEXT,
        num_expediente_fema TEXT,
        tipo_diligencia     TEXT,
        comparecientes      TEXT,
        hechos              TEXT,
        hallazgos           TEXT,
        fundamento_legal    TEXT,
        disposicion         TEXT,
        utm_zona            TEXT,
        utm_este            REAL,
        utm_norte           REAL,
        gps_latitud         REAL,
        gps_longitud        REAL,
        estado              TEXT DEFAULT 'Activa',
        observaciones       TEXT,
        ruta_carpeta_caso   TEXT,
        scan_expediente     TEXT,
        scan_otros          TEXT,
        perito_nombre       TEXT,
        perito_registro     TEXT,
        creado_en           TEXT DEFAULT (datetime('now','localtime'))
    )''')

    # ── Facturas ──────────────────────────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS facturas (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        num_factura     TEXT,
        fecha           TEXT NOT NULL,
        fecha_limite    TEXT,
        cai             TEXT,
        rango_inicio    TEXT,
        rango_fin       TEXT,
        cliente_nombre  TEXT,
        cliente_rtn     TEXT,
        cliente_dir     TEXT,
        servicios       TEXT,
        subtotal        REAL,
        isv             REAL,
        total           REAL,
        ruta_pdf        TEXT,
        estado          TEXT DEFAULT 'ACTIVA',
        motivo_anulacion TEXT,
        anulada_en      TEXT
    )''')

    # ── Tabla de Pagos Recibidos ──────────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS pagos_tfc (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        factura_id INTEGER,
        monto REAL NOT NULL,
        fecha TEXT NOT NULL,
        metodo TEXT,
        comprobante TEXT,
        creado_en TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (factura_id) REFERENCES facturas(id)
    )''')

    # ── Tabla de Contratos Forestales ──────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS contratos_tfc (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        predio_sitio TEXT NOT NULL,
        actividad_tipo TEXT NOT NULL,
        cliente_nombre TEXT NOT NULL,
        monto_total REAL NOT NULL,
        fecha_firma TEXT NOT NULL,
        ruta_pdf TEXT NOT NULL,
        consultor_nombre TEXT,
        consultor_registro TEXT,
        clausulas_adicionales TEXT,
        creado_en TEXT DEFAULT (datetime('now','localtime'))
    )''')

    # ── Configuración General (Empresa / Profesional) ─────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS configuracion (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        empresa_nombre      TEXT DEFAULT 'SEDCAF — Servicios de Consultoria y Asesoria Forestal',
        profesional_nombre  TEXT DEFAULT 'Ing. FERNANDO RAFAEL ARDON RODRIGUEZ',
        profesional_registro TEXT DEFAULT 'Ingeniero Forestal , COLPROFORH N.- 0226',
        empresa_rtn         TEXT DEFAULT '',
        empresa_direccion   TEXT DEFAULT 'Honduras',
        empresa_telefono    TEXT DEFAULT ''
    )''')

    c.execute("SELECT COUNT(*) FROM configuracion")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO configuracion (empresa_nombre, profesional_nombre, profesional_registro) VALUES (?, ?, ?)",
                  ('SEDCAF — Servicios de Consultoria y Asesoria Forestal', 'Ing. FERNANDO RAFAEL ARDON RODRIGUEZ', 'Ingeniero Forestal , COLPROFORH N.- 0226'))

    # ── Bitácora de Campo TFC ─────────────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS bitacora_tfc (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        num_bitacora        TEXT NOT NULL,
        folio               INTEGER,
        anio                TEXT,
        fecha               TEXT NOT NULL,
        hora                TEXT,
        sitio_predio        TEXT,
        poa_codigo          TEXT,
        tfc_nombre          TEXT,
        tfc_registro        TEXT,
        actividad_tipo      TEXT,
        detalles_tecnicos   TEXT,
        volumen_m3          REAL DEFAULT 0.0,
        plagas_observadas   TEXT,
        cumplimiento_ambiental TEXT,
        comentarios         TEXT,
        utm_zona            TEXT,
        utm_este            REAL,
        utm_norte           REAL,
        gps_latitud         REAL,
        gps_longitud        REAL,
        estado              TEXT DEFAULT 'Activo',
        ruta_carpeta_caso   TEXT,
        scan_plan_manejo    TEXT,
        scan_poa            TEXT,
        scan_resolucion     TEXT,
        creado_en           TEXT DEFAULT (datetime('now','localtime'))
    )''')

    # Migración: agregar columnas si la tabla ya existe sin ellas
    for col, definition in [
        ("fecha_limite",    "TEXT"),
        ("cai",             "TEXT"),
        ("rango_inicio",    "TEXT"),
        ("rango_fin",       "TEXT"),
        ("estado",          "TEXT DEFAULT 'ACTIVA'"),
        ("motivo_anulacion","TEXT"),
        ("anulada_en",      "TEXT"),
    ]:
        try:
            c.execute(f"ALTER TABLE facturas ADD COLUMN {col} {definition}")
        except sqlite3.OperationalError:
            pass  # columna ya existe

    # Migración de columnas UTM y GPS para protocolo y bitacora_tfc
    for tabla in ["protocolo", "bitacora_tfc"]:
        for col, definition in [
            ("utm_zona", "TEXT"),
            ("utm_este", "REAL"),
            ("utm_norte", "REAL"),
            ("gps_latitud", "REAL"),
            ("gps_longitud", "REAL"),
        ]:
            try:
                c.execute(f"ALTER TABLE {tabla} ADD COLUMN {col} {definition}")
            except sqlite3.OperationalError:
                pass

    # Migración de columnas de organización documental
    for col, definition in [
        ("ruta_carpeta_caso", "TEXT"),
        ("scan_plan_manejo", "TEXT"),
        ("scan_poa", "TEXT"),
        ("scan_resolucion", "TEXT"),
    ]:
        try:
            c.execute(f"ALTER TABLE bitacora_tfc ADD COLUMN {col} {definition}")
        except sqlite3.OperationalError:
            pass

    for col, definition in [
        ("ruta_carpeta_caso", "TEXT"),
        ("scan_expediente", "TEXT"),
        ("scan_otros", "TEXT"),
        ("perito_nombre", "TEXT"),
        ("perito_registro", "TEXT"),
    ]:
        try:
            c.execute(f"ALTER TABLE protocolo ADD COLUMN {col} {definition}")
        except sqlite3.OperationalError:
            pass

    for col, definition in [
        ("consultor_nombre",     "TEXT"),
        ("consultor_registro",   "TEXT"),
        ("clausulas_adicionales","TEXT"),
        ("cliente_rtn",          "TEXT DEFAULT ''"),
        ("municipio",            "TEXT DEFAULT ''"),
        ("departamento",         "TEXT DEFAULT ''"),
        ("forma_pago",           "TEXT DEFAULT ''"),
        ("plazo_ejecucion",      "TEXT DEFAULT ''"),
    ]:
        try:
            c.execute(f"ALTER TABLE contratos_tfc ADD COLUMN {col} {definition}")
        except sqlite3.OperationalError:
            pass

    # ── Tabla de Técnicos Asociados ───────────────────────────────────────────
    c.execute('''CREATE TABLE IF NOT EXISTS tecnicos_tfc (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        registro TEXT NOT NULL
    )''')

    # Sembrar técnico por defecto a partir de la configuración general y adicionales
    c.execute("SELECT COUNT(*) FROM tecnicos_tfc")
    if c.fetchone()[0] == 0:
        c.execute("SELECT profesional_nombre, profesional_registro FROM configuracion WHERE id=1")
        conf = c.fetchone()
        prof_nom = conf[0] if conf else "Ing. Fernando Rafael Ardon Rodriguez"
        prof_reg = conf[1] if conf else "COLPROFORH N.- 0226"
        c.execute("INSERT INTO tecnicos_tfc (nombre, registro) VALUES (?, ?)", (prof_nom, prof_reg))
        # Sembrar adicionales ficticios para pruebas de sociedad
        c.execute("INSERT INTO tecnicos_tfc (nombre, registro) VALUES (?, ?)", ("Ing. Juan Carlos Pérez", "COLPROFORH N.- 0450"))
        c.execute("INSERT INTO tecnicos_tfc (nombre, registro) VALUES (?, ?)", ("Ing. María Elena Mejía", "COLPROFORH N.- 0820"))

    conn.commit()
    
    # Insertar bitácora ficticia de demostración si no existe
    c.execute("SELECT COUNT(*) FROM bitacora_tfc WHERE num_bitacora='001-2026'")
    if c.fetchone()[0] == 0:
        c.execute("""INSERT INTO bitacora_tfc 
            (num_bitacora, folio, anio, fecha, hora, sitio_predio, poa_codigo, tfc_nombre, tfc_registro, actividad_tipo, detalles_tecnicos, volumen_m3, plagas_observadas, cumplimiento_ambiental, comentarios, utm_zona, utm_este, utm_norte, gps_latitud, gps_longitud, estado) 
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            ("001-2026", 1, "2026", "15/06/2026", "14:30", 
             "Finca El Pino, Sector Las Marías, Guaimaca", "POA-GUA-2026-04", 
             "Ing. Fernando Rafael Ardon Rodriguez", "COLPROFORH N.- 0226", 
             "Corte y Cubicacion de Madera", 
             "Aprovechamiento forestal de pino (Pinus oocarpa) en el rodal 2. Se cubicaron trozas de madera de calidad de aserrío con diámetros promedio de 35.0 cm y longitudes de 5.0 metros.", 
             48.50, 
             "Ninguna plaga activa detectada en el rodal de corte. Monitoreo constante sin brotes del gorgojo descortezador del pino (Dendroctonus frontalis).", 
             "Se respetó estrictamente la faja de protección del riachuelo Las Marías. Caminos de arrastre de trozas estabilizados con copas para mitigar la erosión.", 
             "Registro de ejemplo ficticio completo para pruebas. Este registro puede ser editado o eliminado físicamente desde el sistema mientras permanezca en estado 'Activo'. Una vez que el estado cambie a 'Archivada' o 'Anulada', se bloquearán todas las modificaciones.", 
             "16N", 525200.0, 1585600.0, 14.33923, -86.76632, "Activo"))
        conn.commit()

    # Insertar acta de protocolo ficticia de demostración asociada a otro técnico si no existe
    c.execute("SELECT COUNT(*) FROM protocolo WHERE num_acta='001-2026'")
    if c.fetchone()[0] == 0:
        c.execute("""INSERT INTO protocolo 
            (num_acta, folio, anio, fecha, hora, lugar, municipio, departamento, num_expediente_fema, tipo_diligencia, comparecientes, hechos, hallazgos, fundamento_legal, disposicion, utm_zona, utm_este, utm_norte, gps_latitud, gps_longitud, estado, observaciones, perito_nombre, perito_registro) 
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            ("001-2026", 1, "2026", "15/06/2026", "10:15",
             "Predio Santa Rosa, Kilómetro 45", "Talanga", "Francisco Morazán", "FEMA-1025-2026",
             "Acta de Peritaje Forestal", "Digna Estela Zelaya (Fiscal del MP)\nIng. Juan Carlos Pérez (Perito Forestal)",
             "Se constató la corta no autorizada de veinticinco (25) árboles de pino (Pinus oocarpa) en etapa juvenil.",
             "Corta realizada con motosierra. Volumen estimado de madera aprovechada de forma ilícita asciende a 14.80 m³.",
             "Art. 100 LFAPVS – Aprovechamiento ilegal",
             "Se recomienda el decomiso inmediato del producto forestal y la suspensión total de actividades en el área afectada.",
             "16N", 512400.0, 1573200.0, 14.22731, -86.88490, "Activa",
             "Se documentó fotográficamente el sitio. El peritaje fue suscrito por el perito asignado.",
             "Ing. Juan Carlos Pérez", "COLPROFORH N.- 0450"))
        conn.commit()

    # Insertar contrato ficticio de demostración asociado a otro técnico si no existe
    c.execute("SELECT COUNT(*) FROM contratos_tfc WHERE predio_sitio='Finca Vista Hermosa'")
    if c.fetchone()[0] == 0:
        c.execute("""INSERT INTO contratos_tfc 
            (predio_sitio, actividad_tipo, cliente_nombre, monto_total, fecha_firma, ruta_pdf, consultor_nombre, consultor_registro) 
            VALUES (?,?,?,?,?,?,?,?)""",
            ("Finca Vista Hermosa", "Elaboración de Plan Operativo Anual (POA)", "Inversiones Forestales de Honduras", 125000.00, "15/06/2026", "Contrato_Vista_Hermosa.pdf", "Ing. María Elena Mejía", "COLPROFORH N.- 0820"))
        conn.commit()
        
    conn.close()

# ─── PROTOCOLO ────────────────────────────────────────────────────────────────

def protocolo_siguiente_num(anio):
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM protocolo WHERE anio=?", (anio,))
    n = c.fetchone()[0] + 1; conn.close()
    return f"{n:03d}-{anio}"

def protocolo_siguiente_folio():
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT MAX(folio) FROM protocolo")
    r = c.fetchone()[0]; conn.close()
    return (r or 0) + 1

def protocolo_agregar(num_acta,folio,anio,fecha,hora,lugar,municipio,dept,num_exp,tipo,comparecientes,hechos,hallazgos,fundamento,disposicion,utm_zona,utm_este,utm_norte,gps_lat,gps_lon,estado,obs,ruta_carpeta="",scan_exp="",scan_ot="",perito_nombre="",perito_registro=""):
    conn = get_conn(); c = conn.cursor()
    c.execute("INSERT INTO protocolo (num_acta,folio,anio,fecha,hora,lugar,municipio,departamento,num_expediente_fema,tipo_diligencia,comparecientes,hechos,hallazgos,fundamento_legal,disposicion,utm_zona,utm_este,utm_norte,gps_latitud,gps_longitud,estado,observaciones,ruta_carpeta_caso,scan_expediente,scan_otros,perito_nombre,perito_registro) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (num_acta,folio,anio,fecha,hora,lugar,municipio,dept,num_exp,tipo,comparecientes,hechos,hallazgos,fundamento,disposicion,utm_zona,utm_este,utm_norte,gps_lat,gps_lon,estado,obs,ruta_carpeta,scan_exp,scan_ot,perito_nombre,perito_registro))
    conn.commit(); conn.close()

def protocolo_editar(id_,num_acta,folio,anio,fecha,hora,lugar,municipio,dept,num_exp,tipo,comparecientes,hechos,hallazgos,fundamento,disposicion,utm_zona,utm_este,utm_norte,gps_lat,gps_lon,estado,obs,ruta_carpeta="",scan_exp="",scan_ot="",perito_nombre="",perito_registro=""):
    conn = get_conn(); c = conn.cursor()
    c.execute("UPDATE protocolo SET num_acta=?,folio=?,anio=?,fecha=?,hora=?,lugar=?,municipio=?,departamento=?,num_expediente_fema=?,tipo_diligencia=?,comparecientes=?,hechos=?,hallazgos=?,fundamento_legal=?,disposicion=?,utm_zona=?,utm_este=?,utm_norte=?,gps_latitud=?,gps_longitud=?,estado=?,observaciones=?,ruta_carpeta_caso=?,scan_expediente=?,scan_otros=?,perito_nombre=?,perito_registro=? WHERE id=?",
        (num_acta,folio,anio,fecha,hora,lugar,municipio,dept,num_exp,tipo,comparecientes,hechos,hallazgos,fundamento,disposicion,utm_zona,utm_este,utm_norte,gps_lat,gps_lon,estado,obs,ruta_carpeta,scan_exp,scan_ot,perito_nombre,perito_registro,id_))
    conn.commit(); conn.close()

def protocolo_eliminar(id_):
    conn = get_conn(); c = conn.cursor()
    c.execute("DELETE FROM protocolo WHERE id=?", (id_,)); conn.commit(); conn.close()

def protocolo_todos():
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT id,num_acta,folio,fecha,hora,lugar,tipo_diligencia,num_expediente_fema,estado,gps_latitud,gps_longitud FROM protocolo ORDER BY folio DESC")
    rows = c.fetchall(); conn.close(); return rows

def protocolo_buscar(q):
    conn = get_conn(); c = conn.cursor(); p = f"%{q}%"
    c.execute("SELECT id,num_acta,folio,fecha,hora,lugar,tipo_diligencia,num_expediente_fema,estado,gps_latitud,gps_longitud FROM protocolo WHERE num_acta LIKE ? OR num_expediente_fema LIKE ? OR tipo_diligencia LIKE ? OR lugar LIKE ? OR comparecientes LIKE ? OR hechos LIKE ? ORDER BY folio DESC",(p,p,p,p,p,p))
    rows = c.fetchall(); conn.close(); return rows

def protocolo_por_estado(estado):
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT id,num_acta,folio,fecha,hora,lugar,tipo_diligencia,num_expediente_fema,estado,gps_latitud,gps_longitud FROM protocolo WHERE estado=? ORDER BY folio DESC",(estado,))
    rows = c.fetchall(); conn.close(); return rows

def protocolo_por_id(id_):
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT id, num_acta, folio, anio, fecha, hora, lugar, municipio, departamento, num_expediente_fema, tipo_diligencia, comparecientes, hechos, hallazgos, fundamento_legal, disposicion, estado, observaciones, utm_zona, utm_este, utm_norte, gps_latitud, gps_longitud, creado_en, ruta_carpeta_caso, scan_expediente, scan_otros, perito_nombre, perito_registro 
                 FROM protocolo WHERE id=?""",(id_,))
    row = c.fetchone(); conn.close(); return row

# ─── FACTURAS ─────────────────────────────────────────────────────────────────

def factura_agregar(num_fac,fecha,fecha_lim,cai,rng_ini,rng_fin,cli_nom,cli_rtn,cli_dir,servicios_json,subtotal,isv,total,ruta_pdf):
    conn = get_conn(); c = conn.cursor()
    c.execute("INSERT INTO facturas (num_factura,fecha,fecha_limite,cai,rango_inicio,rango_fin,cliente_nombre,cliente_rtn,cliente_dir,servicios,subtotal,isv,total,ruta_pdf) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (num_fac,fecha,fecha_lim,cai,rng_ini,rng_fin,cli_nom,cli_rtn,cli_dir,servicios_json,subtotal,isv,total,ruta_pdf))
    conn.commit(); conn.close()

def factura_anular(id_, motivo):
    """Marca la factura como ANULADA permanentemente. Nunca se elimina."""
    conn = get_conn(); c = conn.cursor()
    c.execute(
        "UPDATE facturas SET estado='ANULADA', motivo_anulacion=?, "
        "anulada_en=datetime('now','localtime') WHERE id=?",
        (motivo, id_)
    )
    conn.commit(); conn.close()

def factura_por_id(id_):
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT id, num_factura, fecha, fecha_limite, cai, rango_inicio, rango_fin,
                 cliente_nombre, cliente_rtn, cliente_dir, servicios,
                 subtotal, isv, total, ruta_pdf,
                 estado, motivo_anulacion, anulada_en, creado_en
                 FROM facturas WHERE id=?""", (id_,))
    row = c.fetchone(); conn.close(); return row

def factura_actualizar(id_,num_fac,fecha,fecha_lim,cai,rng_ini,rng_fin,cli_nom,cli_rtn,cli_dir,servicios_json,subtotal,isv,total,ruta_pdf):
    conn = get_conn(); c = conn.cursor()
    c.execute("""UPDATE facturas SET num_factura=?,fecha=?,fecha_limite=?,cai=?,rango_inicio=?,rango_fin=?,
        cliente_nombre=?,cliente_rtn=?,cliente_dir=?,servicios=?,subtotal=?,isv=?,total=?,ruta_pdf=?
        WHERE id=?""",
        (num_fac,fecha,fecha_lim,cai,rng_ini,rng_fin,cli_nom,cli_rtn,cli_dir,servicios_json,subtotal,isv,total,ruta_pdf,id_))
    conn.commit(); conn.close()

def factura_eliminar(id_):
    """SOLO para registros de prueba. Facturas reales deben anularse, no eliminarse."""
    conn = get_conn(); c = conn.cursor()
    c.execute("DELETE FROM facturas WHERE id=?", (id_,))
    conn.commit(); conn.close()

def facturas_todos():
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT id,num_factura,fecha,cliente_nombre,total,ruta_pdf,estado FROM facturas ORDER BY id DESC")
    rows = c.fetchall(); conn.close(); return rows

def siguiente_num_factura():
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM facturas"); n = c.fetchone()[0]+1; conn.close()
    return f"FAC-{n:04d}"

# ─── CONFIGURACIÓN GENERAL ────────────────────────────────────────────────────

def config_obtener():
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT * FROM configuracion ORDER BY id ASC LIMIT 1")
    row = c.fetchone()
    if not row:
        row = (1, 'SEDCAF — Servicios de Consultoria y Asesoria Forestal', 'Ing. FERNANDO RAFAEL ARDON RODRIGUEZ', 'Ingeniero Forestal , COLPROFORH N.- 0226', '', 'Honduras', '')
    conn.close()
    return row

def config_guardar(emp_nom, prof_nom, prof_reg, rtn, dir_, tel):
    conn = get_conn(); c = conn.cursor()
    c.execute("UPDATE configuracion SET empresa_nombre=?, profesional_nombre=?, profesional_registro=?, empresa_rtn=?, empresa_direccion=?, empresa_telefono=? WHERE id=1",
              (emp_nom, prof_nom, prof_reg, rtn, dir_, tel))
    conn.commit(); conn.close()

# ─── BITÁCORA DE CAMPO TFC ────────────────────────────────────────────────────

def bitacora_tfc_siguiente_num(anio):
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM bitacora_tfc WHERE anio=?", (anio,))
    n = c.fetchone()[0] + 1; conn.close()
    return f"{n:03d}-{anio}"

def bitacora_tfc_siguiente_folio():
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT MAX(folio) FROM bitacora_tfc")
    r = c.fetchone()[0]; conn.close()
    return (r or 0) + 1

def bitacora_tfc_agregar(num_bitacora, folio, anio, fecha, hora, sitio_predio, poa_codigo, tfc_nombre, tfc_registro, actividad_tipo, detalles_tecnicos, volumen_m3, plagas_observadas, cumplimiento_ambiental, comentarios, utm_zona, utm_este, utm_norte, gps_lat, gps_lon, estado, ruta_carpeta="", scan_pm="", scan_poa="", scan_res=""):
    conn = get_conn(); c = conn.cursor()
    c.execute("""INSERT INTO bitacora_tfc 
        (num_bitacora, folio, anio, fecha, hora, sitio_predio, poa_codigo, tfc_nombre, tfc_registro, actividad_tipo, detalles_tecnicos, volumen_m3, plagas_observadas, cumplimiento_ambiental, comentarios, utm_zona, utm_este, utm_norte, gps_latitud, gps_longitud, estado, ruta_carpeta_caso, scan_plan_manejo, scan_poa, scan_resolucion) 
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (num_bitacora, folio, anio, fecha, hora, sitio_predio, poa_codigo, tfc_nombre, tfc_registro, actividad_tipo, detalles_tecnicos, volumen_m3, plagas_observadas, cumplimiento_ambiental, comentarios, utm_zona, utm_este, utm_norte, gps_lat, gps_lon, estado, ruta_carpeta, scan_pm, scan_poa, scan_res))
    conn.commit(); conn.close()

def bitacora_tfc_editar(id_, num_bitacora, folio, anio, fecha, hora, sitio_predio, poa_codigo, tfc_nombre, tfc_registro, actividad_tipo, detalles_tecnicos, volumen_m3, plagas_observadas, cumplimiento_ambiental, comentarios, utm_zona, utm_este, utm_norte, gps_lat, gps_lon, estado, ruta_carpeta="", scan_pm="", scan_poa="", scan_res=""):
    conn = get_conn(); c = conn.cursor()
    c.execute("""UPDATE bitacora_tfc SET 
        num_bitacora=?, folio=?, anio=?, fecha=?, hora=?, sitio_predio=?, poa_codigo=?, tfc_nombre=?, tfc_registro=?, actividad_tipo=?, detalles_tecnicos=?, volumen_m3=?, plagas_observadas=?, cumplimiento_ambiental=?, comentarios=?, utm_zona=?, utm_este=?, utm_norte=?, gps_latitud=?, gps_longitud=?, estado=?, ruta_carpeta_caso=?, scan_plan_manejo=?, scan_poa=?, scan_resolucion=? 
        WHERE id=?""",
        (num_bitacora, folio, anio, fecha, hora, sitio_predio, poa_codigo, tfc_nombre, tfc_registro, actividad_tipo, detalles_tecnicos, volumen_m3, plagas_observadas, cumplimiento_ambiental, comentarios, utm_zona, utm_este, utm_norte, gps_lat, gps_lon, estado, ruta_carpeta, scan_pm, scan_poa, scan_res, id_))
    conn.commit(); conn.close()

def bitacora_tfc_anular(id_):
    conn = get_conn(); c = conn.cursor()
    c.execute("UPDATE bitacora_tfc SET estado='Anulada' WHERE id=?", (id_,))
    conn.commit(); conn.close()

def bitacora_tfc_todos():
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT id, num_bitacora, folio, fecha, sitio_predio, poa_codigo, actividad_tipo, volumen_m3, estado, gps_latitud, gps_longitud FROM bitacora_tfc ORDER BY folio DESC")
    rows = c.fetchall(); conn.close(); return rows

def bitacora_tfc_buscar(q):
    conn = get_conn(); c = conn.cursor(); p = f"%{q}%"
    c.execute("""SELECT id, num_bitacora, folio, fecha, sitio_predio, poa_codigo, actividad_tipo, volumen_m3, estado, gps_latitud, gps_longitud 
                 FROM bitacora_tfc 
                 WHERE num_bitacora LIKE ? OR poa_codigo LIKE ? OR sitio_predio LIKE ? OR actividad_tipo LIKE ? OR detalles_tecnicos LIKE ? OR plagas_observadas LIKE ? 
                 ORDER BY folio DESC""", (p, p, p, p, p, p))
    rows = c.fetchall(); conn.close(); return rows

def bitacora_tfc_por_estado(estado):
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT id, num_bitacora, folio, fecha, sitio_predio, poa_codigo, actividad_tipo, volumen_m3, estado, gps_latitud, gps_longitud FROM bitacora_tfc WHERE estado=? ORDER BY folio DESC", (estado,))
    rows = c.fetchall(); conn.close(); return rows

def bitacora_tfc_por_id(id_):
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT id, num_bitacora, folio, anio, fecha, hora, sitio_predio, poa_codigo, tfc_nombre, tfc_registro, actividad_tipo, detalles_tecnicos, volumen_m3, plagas_observadas, cumplimiento_ambiental, comentarios, utm_zona, utm_este, utm_norte, gps_latitud, gps_longitud, estado, creado_en, ruta_carpeta_caso, scan_plan_manejo, scan_poa, scan_resolucion 
                 FROM bitacora_tfc WHERE id=?""", (id_,))
    row = c.fetchone(); conn.close(); return row

def bitacora_tfc_eliminar(id_):
    conn = get_conn(); c = conn.cursor()
    c.execute("DELETE FROM bitacora_tfc WHERE id=?", (id_,))
    conn.commit(); conn.close()

def tecnicos_tfc_todos():
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT id, nombre, registro FROM tecnicos_tfc ORDER BY nombre ASC")
    rows = c.fetchall(); conn.close(); return rows

def tecnicos_tfc_agregar(nombre, registro):
    conn = get_conn(); c = conn.cursor()
    c.execute("INSERT INTO tecnicos_tfc (nombre, registro) VALUES (?, ?)", (nombre, registro))
    conn.commit(); conn.close()

def tecnicos_tfc_eliminar(id_):
    conn = get_conn(); c = conn.cursor()
    c.execute("DELETE FROM tecnicos_tfc WHERE id=?", (id_,))
    conn.commit(); conn.close()

def pagos_agregar(factura_id, monto, fecha, metodo, comprobante):
    conn = get_conn(); c = conn.cursor()
    c.execute("INSERT INTO pagos_tfc (factura_id, monto, fecha, metodo, comprobante) VALUES (?,?,?,?,?)",
              (factura_id, monto, fecha, metodo, comprobante))
    conn.commit(); conn.close()

def pagos_por_factura(factura_id):
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT id, factura_id, monto, fecha, metodo, comprobante, creado_en FROM pagos_tfc WHERE factura_id=? ORDER BY id DESC", (factura_id,))
    rows = c.fetchall(); conn.close(); return rows

def pagos_todos():
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT id, factura_id, monto, fecha, metodo, comprobante, creado_en FROM pagos_tfc ORDER BY id DESC")
    rows = c.fetchall(); conn.close(); return rows

def pagos_eliminar(id_):
    conn = get_conn(); c = conn.cursor()
    c.execute("DELETE FROM pagos_tfc WHERE id=?", (id_,))
    conn.commit(); conn.close()

def contratos_agregar(predio_sitio, actividad_tipo, cliente_nombre, monto_total,
                      fecha_firma, ruta_pdf, consultor_nombre="", consultor_registro="",
                      clausulas_adicionales="", cliente_rtn="", municipio="",
                      departamento="", forma_pago="", plazo_ejecucion=""):
    conn = get_conn(); c = conn.cursor()
    c.execute(
        "INSERT INTO contratos_tfc "
        "(predio_sitio, actividad_tipo, cliente_nombre, monto_total, fecha_firma, "
        "ruta_pdf, consultor_nombre, consultor_registro, clausulas_adicionales, "
        "cliente_rtn, municipio, departamento, forma_pago, plazo_ejecucion) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (predio_sitio, actividad_tipo, cliente_nombre, monto_total, fecha_firma,
         ruta_pdf, consultor_nombre, consultor_registro, clausulas_adicionales,
         cliente_rtn, municipio, departamento, forma_pago, plazo_ejecucion)
    )
    conn.commit(); conn.close()

def contratos_todos():
    conn = get_conn(); c = conn.cursor()
    c.execute(
        "SELECT id, predio_sitio, actividad_tipo, cliente_nombre, monto_total, "
        "fecha_firma, ruta_pdf, creado_en, consultor_nombre, consultor_registro, "
        "clausulas_adicionales, cliente_rtn, municipio, departamento, "
        "forma_pago, plazo_ejecucion FROM contratos_tfc ORDER BY id DESC"
    )
    rows = c.fetchall(); conn.close(); return rows

def contratos_editar(id_, predio_sitio, actividad_tipo, cliente_nombre, monto_total,
                     fecha_firma, ruta_pdf, consultor_nombre="", consultor_registro="",
                     clausulas_adicionales="", cliente_rtn="", municipio="",
                     departamento="", forma_pago="", plazo_ejecucion=""):
    conn = get_conn(); c = conn.cursor()
    c.execute(
        "UPDATE contratos_tfc SET predio_sitio=?, actividad_tipo=?, "
        "cliente_nombre=?, monto_total=?, fecha_firma=?, ruta_pdf=?, "
        "consultor_nombre=?, consultor_registro=?, clausulas_adicionales=?, "
        "cliente_rtn=?, municipio=?, departamento=?, forma_pago=?, plazo_ejecucion=? "
        "WHERE id=?",
        (predio_sitio, actividad_tipo, cliente_nombre, monto_total, fecha_firma,
         ruta_pdf, consultor_nombre, consultor_registro, clausulas_adicionales,
         cliente_rtn, municipio, departamento, forma_pago, plazo_ejecucion, id_)
    )
    conn.commit(); conn.close()

def contratos_eliminar(id_):
    conn = get_conn(); c = conn.cursor()
    c.execute("DELETE FROM contratos_tfc WHERE id=?", (id_,))
    conn.commit(); conn.close()

def dashboard_sitios_todos():
    conn = get_conn(); c = conn.cursor()
    c.execute("""
        SELECT DISTINCT sitio_predio AS sitio FROM bitacora_tfc WHERE sitio_predio IS NOT NULL AND sitio_predio != ''
        UNION
        SELECT DISTINCT lugar AS sitio FROM protocolo WHERE lugar IS NOT NULL AND lugar != ''
        ORDER BY sitio ASC
    """)
    rows = c.fetchall(); conn.close()
    return [r[0] for r in rows]

def dashboard_kpis_por_sitio(sitio):
    conn = get_conn(); c = conn.cursor()
    
    # 1. Volumen cubicado
    c.execute("SELECT SUM(volumen_m3) FROM bitacora_tfc WHERE sitio_predio = ?", (sitio,))
    vol = c.fetchone()[0] or 0.0
    
    # 2. Inspecciones/Actas
    c.execute("SELECT COUNT(*) FROM protocolo WHERE lugar = ?", (sitio,))
    inspecciones = c.fetchone()[0] or 0
    
    # 3. Plagas/Incidencias críticas
    c.execute("""
        SELECT COUNT(*) FROM bitacora_tfc 
        WHERE sitio_predio = ? 
          AND plagas_observadas IS NOT NULL 
          AND plagas_observadas != '' 
          AND (plagas_observadas LIKE '%plaga%' 
               OR plagas_observadas LIKE '%gorgojo%' 
               OR plagas_observadas LIKE '%brote%' 
               OR plagas_observadas LIKE '%incidencia%' 
               OR plagas_observadas LIKE '%daño%' 
               OR plagas_observadas LIKE '%alerta%'
               OR plagas_observadas LIKE '%dendroctonus%')
    """, (sitio,))
    plagas = c.fetchone()[0] or 0
    
    conn.close()
    return vol, inspecciones, plagas

def dashboard_actividades_por_sitio(sitio):
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT actividad_tipo, COUNT(*) FROM bitacora_tfc WHERE sitio_predio = ? GROUP BY actividad_tipo", (sitio,))
    rows = c.fetchall(); conn.close()
    return rows

def dashboard_diligencias_por_sitio(sitio):
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT tipo_diligencia, COUNT(*) FROM protocolo WHERE lugar = ? GROUP BY tipo_diligencia", (sitio,))
    rows = c.fetchall(); conn.close()
    return rows

def dashboard_estados_actas_por_sitio(sitio):
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT estado, COUNT(*) FROM protocolo WHERE lugar = ? GROUP BY estado", (sitio,))
    rows = c.fetchall(); conn.close()
    return rows


