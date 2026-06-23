"""
utils/license.py – Sistema de Licencias SilvaDesk Pro
SEDCAF · Honduras · 2026

Arquitectura:
  - Hardware ID único por PC (Windows MachineGuid vía registro)
  - HMAC-SHA256 con clave secreta para validar claves de activación
  - Trial de 15 días (fecha de primera ejecución en Windows Registry)
  - Límite de 5 registros en módulos protegidos tras vencer el trial
  - Estados: LICENSED | TRIAL_ACTIVE | TRIAL_EXPIRED
"""
import hmac
import hashlib
import base64
from datetime import date, timedelta

# ── Clave secreta (NO modificar nunca después de haber generado licencias) ─────
_SECRET = b"SEDCAF-SilvaDeskPro2026-HMAC-v1-XK9T-DO-NOT-SHARE"

# ── Parámetros configurables ───────────────────────────────────────────────────
TRIAL_DAYS  = 15   # días de prueba gratuita
FREE_LIMIT  = 5    # registros máximos en módulos protegidos (trial vencido)

# ── Claves del registro de Windows ─────────────────────────────────────────────
_REG_PATH    = r"Software\SEDCAF\SilvaDeskPro"
_KEY_INSTALL = "InstallDate"
_KEY_LICENSE = "LicenseKey"


# ══════════════════════════════════════════════════════════════════════════════
# HARDWARE ID
# ══════════════════════════════════════════════════════════════════════════════

def get_hardware_id() -> str:
    """
    Retorna el ID de hardware único de esta PC (16 chars, formato XXXX-XXXX-XXXX-XXXX).
    Basado en el MachineGuid de Windows; no cambia al reinstalar Windows si se
    restaura la misma clave de registro.
    """
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Cryptography"
        )
        guid, _ = winreg.QueryValueEx(key, "MachineGuid")
        winreg.CloseKey(key)
    except Exception:
        import socket
        guid = socket.gethostname() + "-fallback-2026"

    raw = hashlib.sha256(guid.encode("utf-8")).hexdigest()
    h   = raw[:16].upper()
    return f"{h[0:4]}-{h[4:8]}-{h[8:12]}-{h[12:16]}"


# ══════════════════════════════════════════════════════════════════════════════
# GENERACIÓN Y VERIFICACIÓN DE CLAVES
# ══════════════════════════════════════════════════════════════════════════════

def generate_activation_key(hardware_id: str) -> str:
    """
    Genera la clave de activación para un hardware_id dado.
    Esta función es usada tanto aquí (verificación) como en el
    script privado license_generator_PRIVADO.py.
    """
    hid     = hardware_id.replace("-", "").encode("utf-8")
    digest  = hmac.new(_SECRET, hid, hashlib.sha256).digest()
    b32     = base64.b32encode(digest).decode("ascii")[:20]
    return f"{b32[0:5]}-{b32[5:10]}-{b32[10:15]}-{b32[15:20]}"


def verify_key(key: str) -> bool:
    """
    Verifica si la clave ingresada es válida para el hardware de esta PC.
    Usa comparación de tiempo constante para evitar ataques de timing.
    """
    expected = generate_activation_key(get_hardware_id())
    k1 = key.strip().upper().replace("-", "").replace(" ", "")
    k2 = expected.replace("-", "")
    return hmac.compare_digest(k1, k2)


# ══════════════════════════════════════════════════════════════════════════════
# REGISTRO DE WINDOWS (persistencia)
# ══════════════════════════════════════════════════════════════════════════════

def _reg_read(name: str) -> str | None:
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, _REG_PATH)
        val, _ = winreg.QueryValueEx(key, name)
        winreg.CloseKey(key)
        return val
    except Exception:
        return None


def _reg_write(name: str, value: str) -> None:
    try:
        import winreg
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, _REG_PATH)
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
        winreg.CloseKey(key)
    except Exception:
        pass


def _ensure_install_date() -> None:
    """Registra la fecha de instalación la primera vez que se ejecuta la app."""
    if _reg_read(_KEY_INSTALL) is None:
        _reg_write(_KEY_INSTALL, date.today().isoformat())


# ══════════════════════════════════════════════════════════════════════════════
# ESTADO DEL TRIAL
# ══════════════════════════════════════════════════════════════════════════════

def get_trial_days_remaining() -> int:
    """
    Retorna cuántos días de trial quedan.
    Valor positivo = días restantes.
    Valor negativo = días desde que expiró.
    """
    _ensure_install_date()
    raw = _reg_read(_KEY_INSTALL)
    try:
        install_date = date.fromisoformat(raw)
    except Exception:
        install_date = date.today()
        _reg_write(_KEY_INSTALL, install_date.isoformat())
    expiry = install_date + timedelta(days=TRIAL_DAYS)
    return (expiry - date.today()).days


# ══════════════════════════════════════════════════════════════════════════════
# GESTIÓN DE LICENCIA GUARDADA
# ══════════════════════════════════════════════════════════════════════════════

def save_license(key: str) -> None:
    """Persiste la clave de licencia en el registro de Windows."""
    _reg_write(_KEY_LICENSE, key.strip().upper())


def get_saved_license() -> str | None:
    """Retorna la clave guardada, o None si no hay ninguna."""
    return _reg_read(_KEY_LICENSE)


def remove_license() -> None:
    """Elimina la licencia guardada (para pruebas o reset)."""
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, _REG_PATH,
                             access=winreg.KEY_WRITE)
        winreg.DeleteValue(key, _KEY_LICENSE)
        winreg.CloseKey(key)
    except Exception:
        pass


# ══════════════════════════════════════════════════════════════════════════════
# ESTADO GLOBAL DE LICENCIA
# ══════════════════════════════════════════════════════════════════════════════

def get_license_state() -> str:
    """
    Evalúa y retorna el estado actual de la licencia:

      'LICENSED'      → Clave válida activa. Sin restricciones.
      'TRIAL_ACTIVE'  → Trial vigente (< 15 días desde instalación). Sin restricciones.
      'TRIAL_EXPIRED' → Trial vencido y sin licencia válida.
                        Módulos protegidos limitados a FREE_LIMIT registros.
    """
    saved = get_saved_license()
    if saved and verify_key(saved):
        return "LICENSED"
    if get_trial_days_remaining() > 0:
        return "TRIAL_ACTIVE"
    return "TRIAL_EXPIRED"
