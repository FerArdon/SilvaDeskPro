"""
utils/geo_conv.py – Conversión geodésica offline de UTM WGS84 a Lat/Lon decimales.
SilvaDesk Pro · SEDCAF / ICF Honduras
"""
import math

def utm_to_latlon(este: float, norte: float, zona: str) -> tuple:
    """
    Convierte coordenadas UTM WGS84 (Zonas 16N o 17N) a Latitud/Longitud en grados decimales.
    
    Parámetros:
        este: Coordenada X en metros (ej. 375000.0)
        norte: Coordenada Y en metros (ej. 1550000.0)
        zona: '16N' o '17N'
        
    Retorna:
        (latitud, longitud) en grados decimales. En caso de error, retorna (None, None).
    """
    try:
        # Validar entradas básicas
        if not (100000.0 <= este <= 900000.0) or not (0.0 <= norte <= 10000000.0):
            return None, None
        
        # Determinar meridiano central según la zona
        if zona == '16N':
            lon_origin = -87.0
        elif zona == '17N':
            lon_origin = -81.0
        else:
            return None, None
        
        # Constantes WGS84
        a = 6378137.0         # Semieje mayor (m)
        f = 1.0 / 298.257223563 # Achatamiento
        b = a * (1.0 - f)     # Semieje menor (m)
        
        # Constantes de cálculo
        e2 = (a**2 - b**2) / (a**2)
        ep2 = (a**2 - b**2) / (b**2)
        k0 = 0.9996
        
        x = este - 500000.0   # Quitar falso Este
        y = norte
        
        # Cálculo de la latitud huella (footprint latitude)
        M = y / k0
        mu = M / (a * (1.0 - e2 / 4.0 - 3.0 * e2**2 / 64.0 - 5.0 * e2**3 / 256.0))
        
        e1 = (1.0 - math.sqrt(1.0 - e2)) / (1.0 + math.sqrt(1.0 - e2))
        
        phi1_rad = (mu + (3.0 * e1 / 2.0 - 27.0 * e1**3 / 32.0) * math.sin(2.0 * mu)
                    + (21.0 * e1**2 / 16.0 - 55.0 * e1**4 / 32.0) * math.sin(4.0 * mu)
                    + (151.0 * e1**3 / 96.0) * math.sin(6.0 * mu))
        
        # Radios de curvatura
        sin_phi1 = math.sin(phi1_rad)
        cos_phi1 = math.cos(phi1_rad)
        tan_phi1 = math.tan(phi1_rad)
        
        n1 = a / math.sqrt(1.0 - e2 * sin_phi1**2)
        r1 = a * (1.0 - e2) / (1.0 - e2 * sin_phi1**2)**1.5
        t1 = tan_phi1**2
        c1 = ep2 * cos_phi1**2
        d = x / (n1 * k0)
        
        # Cálculo de Latitud
        lat_rad = (phi1_rad - (n1 * tan_phi1 / r1) * (d**2 / 2.0 
                   - (5.0 + 3.0 * t1 + 10.0 * c1 - 4.0 * c1**2 - 9.0 * ep2) * d**4 / 24.0
                   + (61.0 + 90.0 * t1 + 298.0 * c1 + 45.0 * t1**2 - 252.0 * ep2 - 3.0 * c1**2) * d**6 / 720.0))
        
        # Cálculo de Longitud
        lon_rad = ((d - (1.0 + 2.0 * t1 + c1) * d**3 / 6.0
                    + (5.0 - 2.0 * c1 + 28.0 * t1 - 3.0 * c1**2 + 8.0 * ep2 + 24.0 * t1**2) * d**5 / 120.0) / cos_phi1)
        
        lat = math.degrees(lat_rad)
        lon = lon_origin + math.degrees(lon_rad)
        
        return round(lat, 6), round(lon, 6)
    
    except Exception:
        return None, None
