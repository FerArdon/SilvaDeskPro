# utils/theme.py
# Sistema centralizado de estilos para SilvaDesk Pro

# ─── Paleta de Colores (Windows 11 Fluent) ──────────────────────────────────
COLOR_ACCENT       = "#0078D4"   # Windows 11 Blue
COLOR_ACCENT_DARK  = "#005FB8"   # Hover / pressed
COLOR_ACCENT_LIGHT = "#B4D6FA"   # Light accent
COLOR_HIGHLIGHT    = "#E8F4FD"   # Light blue input highlight / Active Row
COLOR_WARNING      = "#C42B1C"   # Rojo Win11 para botones eliminar/alertas
COLOR_WARNING_DARK = "#A21B14"   # Hover de alertas
COLOR_BG_MICA      = "#F3F3F3"   # Fondo general
COLOR_BG_PANEL     = "#FFFFFF"   # Blanco puro
COLOR_TEXT_DARK    = "#111111"
COLOR_TEXT_MUTED   = "#616161"
COLOR_TEXT_LIGHT   = "#FFFFFF"
COLOR_BORDER       = "#D1D1D1"

# ─── Tipografía Estandarizada ───────────────────────────────────────────────
# Basado en Segoe UI. Tamaño generoso sin requerir escalado forzado del widget.

FONT_FAMILY = "Segoe UI"

# Fuentes base de CustomTkinter  (+1.5 pts sobre base original)
FONT_SM    = (FONT_FAMILY, 14)          # Tooltips, notas, avisos       (era 12)
FONT_NORM  = (FONT_FAMILY, 16)          # Textos normales, inputs, tablas (era 14)
FONT_BOLD  = (FONT_FAMILY, 16, "bold")  # Cabeceras de tabla, botones   (era 14)
FONT_H3    = (FONT_FAMILY, 18, "bold")  # Totales, subtítulos           (era 16)
FONT_H2    = (FONT_FAMILY, 20, "bold")  # Títulos de sección            (era 18)
FONT_H1    = (FONT_FAMILY, 26, "bold")  # Títulos principales de la app (era 24)

# Alias para la compatibilidad con el refactor
V_OSC = COLOR_ACCENT_DARK
V_MED = COLOR_ACCENT
V_CLR = COLOR_ACCENT_LIGHT
BLANCO = COLOR_BG_PANEL
AMARILL = COLOR_HIGHLIGHT
GRIS_F = COLOR_BG_MICA
