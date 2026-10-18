# -*- coding: utf-8 -*-
"""
cocina01 — receta de la cocina COCINA-01 (pedido de prueba), toda en codigo.

    python3 recetas/cocina01.py            -> recetas/salida/COCINA-01/

Escribe:
    modelo.json          placas (marco, contorno, agujeros, ranuras, atributos)
                         + herrajes a dibujar. Lo lee fusion/ArmarReceta.
    piezas_receta.json   las mismas placas en el esquema de ExportarPiezas, para
                         comparar contra lo que Fusion lee del solido (oraculo).
    resumen.txt          lista de muebles y placas, herrajes y avisos.

Sale del modelo de render "COCINA" (Fusion, proyecto cocina) — solo medidas —
con las decisiones de Pato del 29/09/2026, REVISADAS el 18/10/2026 para que la
cocina quede como el render de referencia (verde, vitrinas, tiradores de cobre):

  * frentes de melamina 18 (VERDE 18), cuerpos BLANCO 18
  * esquineros diagonales (bajo y alacena): la sierra corta el rectangulo y el
    chanfle a 45 se hace a mano; la puerta cuelga de un MONTANTE a 45 con la
    bisagra de cazoleta de siempre
  * pared larga, desde el esquinero: bajo pileta 600 (frente fijo + 2 puertas),
    cajonera 320 (4 cajones), BAJO PUERTA 452 (una puerta ancha, donde iba el
    lavavajillas: 18/10 se saco el lavavajillas) y panel terminal
  * pared corta: esquinero, cocina 550 x 650 y panel terminal
  * cajonera: corredera de bolillas 450 Grupo Euro (agujeros 37/413 como
    GuiGui); caja de melamina 18 con 3 en 1, fondo 5 en ranura
  * zocalo clip sobre patas regulables (el cuerpo arranca a 100)
  * alacenas de 1450 a 2490, SIN cenefa ni cornisa (18/10: quedaban feas); LED
    embutido con perfil de aluminio en la ranura 10x10 del piso; estantes
    regulables O5 sistema 32; se cuelgan por un TRAVESANO TRASERO 18 x 80 bajo el
    techo (dos en el esquinero), atornillado a la pared a mano
  * VITRINAS (A3 2 puertas, A4 1 puerta de 567, esquinero): MARCO DE 4 PIEZAS
    DE MADERA MACIZA de 18 (montantes 60, travesanos 70) unido con Minifix +
    tarugo O8, vidrio de 4 en ranura 12 x 5 por atras, cruz de listones 25 x 8
    pegada al vidrio. Todo lo perfora la SKH-612 (la ranura con la T11); la
    madera va en lista de corte aparte de la melamina (no es para AutoCUT).
  * A2 (sobre la pileta): DOS hojas rebatibles hacia arriba, con pistones: la
    de arriba (1/3) colgada del techo, la de abajo del estante fijo (18/10)
  * tiradores: barral de cobre 128 entre centros en los bajos (vertical en
    puertas, horizontal en cajones y en la rebatible) y perilla en alacenas.
    Agujeros O5 PASANTES.
  * 3 en 1 con perno de rosca para madera: receptor O5 x 12 (medidas.json)
  * placa base de bisagra: 2 x O5 a 37 del frente, +-16 (probada 16/10)
  * fondos de 5 en ranura 6x6
  * mesada de otro proveedor, cocina (horno) 650 de fondo x 550

Mundo (mm): X a lo largo de la pared larga, Y saliendo de la pared larga, Z
arriba. Pared larga en Y=0, pared corta en X=0. Los muebles de la pared larga
miran a +Y; los de la pared corta, a +X.

Marco de cada placa = marco del archivo de maquina: X ancho, Y alto, cara A en
z=0 con normal +ez, espesor hacia -ez. Punto del mundo = O + x*ex + y*ey + z*ez.

Los herrajes y sus medidas salen de lo ya verificado (CONTEXTO §15.5, §24,
herrajes/biblioteca/CATALOGO.md, y los agujeros reales de COCINA MLV).
"""

from __future__ import annotations

import json
import math
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, "salida", "COCINA-01")

ORDEN = "COCINA-01"
CLIENTE = "PRUEBA"
AMBIENTE = "COCINA-01"
PREFIJO_CODIGO = "999260929"          # 999 = codigo propio + fecha; 3 digitos de serie

MEL, FIB = "Melamina", "Melamina"
VERDE, BLANCO, FONDO5 = "VERDE 18", "BLANCO 18", "BLANCO 5"
CANTO = 1.0                           # mm — SIN VERIFICAR contra el canto real

# ---------------------------------------------------------------- herrajes --
# las medidas de herrajes salen de herrajes/medidas.json (cambiar ALLA, no aca)
def _medidas():
    with open(os.path.join(os.path.dirname(AQUI), "herrajes", "medidas.json"), encoding="utf-8") as fh:
        return json.load(fh)
_M = _medidas()
_B, _U = _M["bisagra"], _M["tres_en_uno"]
# 3 en 1 con perno de rosca para madera: excentrica O15, perno O8 x 33 en el canto,
# receptor O5 x 12 (sin taco: el perno rosca directo en la placa, probado 06/10)
CAM = {"d": _U["excentrica_d"], "prof": _U["excentrica_prof"], "desde_canto": 33.0}
PERNO = {"d": _U["perno_canto_d"], "prof": _U["perno_canto_prof"]}
RECIBE = {"d": _U["receptor_d"], "prof": _U["receptor_prof"]}
MARGEN_MIN, PASO, LARGO_UN_CONECTOR = 40.0, 32.0, 200.0
# bisagra de cazoleta Grupo Euro (48/6)
CAZ = {"d": _B["cazoleta_d"], "prof": _B["cazoleta_prof"], "desde_canto": _B["cazoleta_desde_canto"]}
TOR = {"d": _B["tornillo_d"], "prof": _B["tornillo_prof"],
       "adentro": _B["tornillos_desde_cazoleta"], "a_lo_largo": _B["tornillos_a_lo_largo"]}
# placa base (en el lateral / montante): 2 agujeros a `frente` del canto de adelante,
# uno arriba del otro a +-`a_lo_largo` del centro de la cazoleta (probada 16/10/2026)
BASE = {"d": _B["base_d"], "prof": _B["base_prof"], "frente": _B["base_frente"],
        "a_lo_largo": _B["base_a_lo_largo"]}
MARGEN_BISAGRA = 100.0
# tiradores (18/10): barral 128 entre centros, perilla; tornillo M4 -> O5 pasante
TIRADOR = {"d": 5.0, "entre_centros": 128.0, "del_canto": 45.0, "del_borde": 150.0}
PERILLA = {"d": 5.0, "del_canto": 40.0, "del_borde": 50.0}
# vitrina (18/10, decision de Pato): MARCO DE 4 PIEZAS DE MADERA MACIZA de 18 unido con
# Minifix (el 3 en 1 de siempre: excentrica O15 en la cara de atras del travesano, perno O8 x 33
# en su punta, O5 x 12 en el canto interior del montante) + un tarugo O8 por esquina para que no
# gire. Vidrio de 4 en una ranura-rebaje de 12 x 5 por la cara de atras (T11 O10), sujeto con
# junquillos. La cruz que imita los 6 vidrios es una parrilla de listones 25 x 8 pegada al vidrio.
MADERA = "Madera maciza"
MACIZA = "MADERA VERDE 18"                       # textura: 'VERDE' -> se pinta verde en Fusion
VIT = {"montante": 60.0, "travesano": 70.0, "parante": 25.0, "parante_esp": 8.0,
       "rebaje_ancho": 12.0, "rebaje_prof": 5.0, "vidrio": 4.0}
TARUGO = {"d": 8.0, "prof": 15.0, "del_borde": 12.0}
# corredera de bolillas 450 (COCINA MLV): O3 x 10 a 37 y 413 del frente
CORR = {"d": 3.0, "prof": 10.0, "a": (37.0, 413.0), "largo": 450.0, "juego": 13.0}
# estante regulable
PIN = {"d": 5.0, "prof": 12.0, "banda": (-64, -32, 0, 32, 64)}
# ranuras
BP = {"ancho": 6.0, "prof": 6.0, "desde_atras": 27.5}          # fondo de 5
BP_CAJON = {"ancho": 6.0, "prof": 5.5, "desde_abajo": 17.5}
LED = {"ancho": 10.0, "prof": 10.0, "desde_frente": 45.0, "margen": 20.0}

# ---------------------------------------------------------------- medidas --
T = 18.0
Z_BAJO = 100.0                        # arranque del cuerpo (patas + zocalo)
H_BAJO = 760.0                        # hasta 860; mesada 40 -> 900
F_BAJO = 580.0                        # fondo del cuerpo bajo
Z_ALTO0, Z_ALTO1 = 1450.0, 2490.0     # cuerpo de las alacenas, de punta a punta (18/10: sin cenefa ni cornisa)
Z_CUERPO0, Z_CUERPO1 = Z_ALTO0, Z_ALTO1
TRAV_ALTO = 80.0                      # travesano trasero de las alacenas (para colgarlas)
TRAV_TORNILLOS = 2                    # tornillos a la pared por travesano (a mano, en obra)
F_ALTO = 332.0
X_FIN = 2190.0                        # largo de la pared larga (mesada)
Y_FIN = 1368.0                        # hasta donde llega el panel de la cocina en la pared corta
LUZ = 1.5                             # retiro de la puerta respecto del cuerpo
JUNTA = 3.0                           # luz entre puertas / frentes

S2 = math.sqrt(2.0)


# ================================================================ vectores ==
def add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def mul(a, k): return (a[0] * k, a[1] * k, a[2] * k)
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def norm(a):
    n = math.sqrt(dot(a, a))
    return (a[0] / n, a[1] / n, a[2] / n)


AX = {"+X": (1, 0, 0), "-X": (-1, 0, 0), "+Y": (0, 1, 0), "-Y": (0, -1, 0), "+Z": (0, 0, 1), "-Z": (0, 0, -1)}
DIRECCION = {"IZQ": (1, 0), "DER": (-1, 0), "ABAJO": (0, 1), "ARRIBA": (0, -1)}   # hacia adentro
LETRA = {"IZQ": "L", "DER": "R", "ABAJO": "D", "ARRIBA": "U"}


# ================================================================== placa ==
class Placa(object):
    def __init__(self, mueble, nombre, W, H, esp, O, ex, ey, textura, rol="", cantos=(),
                 contorno=None, material=MEL, veta="VERTICAL"):
        self.mueble, self.nombre = mueble, nombre
        self.W, self.H, self.T = float(W), float(H), float(esp)
        self.O, self.ex, self.ey = tuple(O), norm(ex), norm(ey)
        self.ez = cross(self.ex, self.ey)
        self.textura, self.material, self.rol, self.veta = textura, material, rol, veta
        self.contorno = contorno            # lista de (x, y) CCW, o None = rectangulo
        self.agujeros, self.canto, self.ranuras = [], [], []
        self.ventanas, self.rebajes = [], []         # router: huecos pasantes y cajeados (vitrinas)
        self.cantos = {"IZQ": 0.0, "DER": 0.0, "ABAJO": 0.0, "ARRIBA": 0.0}
        self._cantos_mundo = [AX[c] if isinstance(c, str) else c for c in cantos]
        self.codigo = ""
        self._marcar_cantos()

    # --- marcos
    def mundo(self, x, y, z=0.0):
        return add(self.O, add(mul(self.ex, x), add(mul(self.ey, y), mul(self.ez, z))))

    def local(self, p):
        d = sub(p, self.O)
        return (dot(d, self.ex), dot(d, self.ey), dot(d, self.ez))

    def vec(self, x, y, z):
        return add(mul(self.ex, x), add(mul(self.ey, y), mul(self.ez, z)))

    def normal_canto(self, canto):
        dx, dy = DIRECCION[canto]
        return self.vec(-dx, -dy, 0)       # hacia afuera

    def _marcar_cantos(self):
        for c in self.cantos:
            n = self.normal_canto(c)
            for w in self._cantos_mundo:
                if dot(n, norm(w)) > 0.99:
                    self.cantos[c] = CANTO

    def poligono(self):
        return self.contorno or [(0, 0), (self.W, 0), (self.W, self.H), (0, self.H)]

    def dentro(self, x, y, tol=0.5):
        """Punto (x, y) dentro del contorno (convexo, CCW) con tolerancia."""
        pts = self.poligono()
        for i in range(len(pts)):
            (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % len(pts)]
            # normal hacia afuera de un CCW: (dy, -dx)
            nx, ny = (y2 - y1), -(x2 - x1)
            L = math.hypot(nx, ny)
            if ((x - x1) * nx + (y - y1) * ny) / L > tol:
                return False
        return True

    # --- mecanizados
    def agujero(self, x, y, d, prof, cara, sym):
        self.agujeros.append(dict(x=round(x, 2), y=round(y, 2), d=d, prof=prof, cara=cara, sym=sym))

    def agujero_canto(self, x, y, d, prof, canto, sym):
        self.canto.append(dict(x=round(x, 2), y=round(y, 2), z=self.T / 2.0, d=d, prof=prof,
                               canto=canto, sym=sym))

    def ranura(self, x1, y1, x2, y2, ancho, prof, cara, sym):
        self.ranuras.append(dict(x1=round(x1, 2), y1=round(y1, 2), x2=round(x2, 2), y2=round(y2, 2),
                                 ancho=ancho, prof=prof, cara=cara, sym=sym))

    def ventana(self, x1, y1, x2, y2):
        """Hueco rectangular PASANTE (lo hace el router, no la perforadora)."""
        self.ventanas.append(dict(x1=round(x1, 2), y1=round(y1, 2), x2=round(x2, 2), y2=round(y2, 2)))

    def rebaje(self, x1, y1, x2, y2, prof, cara):
        """Cajeado rectangular de profundidad `prof` en la cara (router)."""
        self.rebajes.append(dict(x1=round(x1, 2), y1=round(y1, 2), x2=round(x2, 2), y2=round(y2, 2),
                                 prof=prof, cara=cara))

    def cara_hacia(self, p):
        """'A' si el punto del mundo p queda del lado de la cara A."""
        return "A" if self.local(p)[2] > -self.T / 2.0 else "B"


def placa_caja(mueble, nombre, x0, x1, y0, y1, z0, z1, A, X, textura, **kw):
    """Placa alineada a los ejes, dada por su caja en el mundo.

    A = direccion del mundo hacia donde mira la cara A ('+Y', ...): el espesor va
    sobre ese eje. X = direccion del mundo del eje X local.
    """
    lo, hi = (x0, y0, z0), (x1, y1, z1)
    ez, ex = AX[A], AX[X]
    ey = cross(ez, ex)
    O = [0.0, 0.0, 0.0]
    ext = [hi[i] - lo[i] for i in range(3)]
    for v in (ex, ey):
        i = [abs(c) for c in v].index(1)
        O[i] = lo[i] if v[i] > 0 else hi[i]
    i = [abs(c) for c in ez].index(1)
    O[i] = hi[i] if ez[i] > 0 else lo[i]
    W = ext[[abs(c) for c in ex].index(1)]
    H = ext[[abs(c) for c in ey].index(1)]
    esp = ext[i]
    return Placa(mueble, nombre, W, H, esp, O, ex, ey, textura, **kw)


# ============================================================== herrajeria ==
HERRAJES = []        # lo que dibuja ArmarReceta
AVISOS = []


def herraje(mueble, nombre, origen, ez, ex, forma, **args):
    if ex is None:
        ex = (1, 0, 0) if abs(ez[0]) < 0.9 else (0, 1, 0)
    HERRAJES.append(dict(mueble=mueble, nombre=nombre, origen=[round(c, 3) for c in origen],
                         ez=[round(c, 6) for c in ez], ex=[round(c, 6) for c in ex],
                         forma=forma, args=args))


def posiciones(largo, cuantos):
    """Reparto medido sobre PRUEBA 1 (ver PonerHerrajes.posiciones)."""
    if cuantos <= 1:
        return [largo / 2.0]
    libre = largo - 2.0 * MARGEN_MIN
    if libre <= 0:
        return [largo / 2.0]
    tramo = PASO * math.floor(libre / PASO + 1e-9)
    m = (largo - tramo) / 2.0
    return [m + tramo * i / (cuantos - 1.0) for i in range(cuantos)]


def _canto_de(p, x, y):
    if abs(x) < 0.5: return "IZQ"
    if abs(x - p.W) < 0.5: return "DER"
    if abs(y) < 0.5: return "ABAJO"
    if abs(y - p.H) < 0.5: return "ARRIBA"
    return None


def tres_en_uno(apoya, recibe, cara_cam, cuantos=None, en=None):
    """3 en 1 entre una placa que APOYA su canto y la CARA de otra.

    Busca el canto recto de `apoya` (a media placa) que cae sobre una cara de
    `recibe`, recorta el tramo de contacto con el contorno de `recibe` y reparte
    los conectores con la regla de PRUEBA 1. Excentrica en la cara `cara_cam`
    de `apoya`, perno por el canto, receptor en la cara de `recibe`.

    en = lista de coordenadas locales de `apoya` a lo largo del canto (y para un
    canto vertical, x para uno horizontal) para forzar donde van los conectores.
    """
    mejor = None
    pts = apoya.poligono()
    zm = -apoya.T / 2.0
    for i in range(len(pts)):
        (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % len(pts)]
        canto = None
        if abs(x1) < 0.5 and abs(x2) < 0.5: canto = "IZQ"
        elif abs(x1 - apoya.W) < 0.5 and abs(x2 - apoya.W) < 0.5: canto = "DER"
        elif abs(y1) < 0.5 and abs(y2) < 0.5: canto = "ABAJO"
        elif abs(y1 - apoya.H) < 0.5 and abs(y2 - apoya.H) < 0.5: canto = "ARRIBA"
        if canto is None:
            continue                         # canto diagonal: no lleva agujero de canto
        a, b = apoya.mundo(x1, y1, zm), apoya.mundo(x2, y2, zm)
        la, lb = recibe.local(a), recibe.local(b)
        for zf, cara in ((0.0, "A"), (-recibe.T, "B")):
            if abs(la[2] - zf) > 0.3 or abs(lb[2] - zf) > 0.3:
                continue
            # tramo del canto dentro del contorno de recibe
            L = math.hypot(x2 - x1, y2 - y1)
            ts = [k / 400.0 for k in range(401)]
            dentro = [t for t in ts if recibe.dentro(la[0] + (lb[0] - la[0]) * t, la[1] + (lb[1] - la[1]) * t)]
            if not dentro:
                continue
            t0, t1 = min(dentro), max(dentro)
            largo = (t1 - t0) * L
            if largo < 20:
                continue
            if mejor is None or largo > mejor[0]:
                mejor = (largo, canto, (x1, y1), (x2, y2), t0, t1, L, cara)
    if mejor is None:
        raise ValueError("sin union entre %s y %s" % (apoya.nombre, recibe.nombre))
    largo, canto, (x1, y1), (x2, y2), t0, t1, L, cara_r = mejor
    n = cuantos or (1 if largo <= LARGO_UN_CONECTOR else 2)
    dx, dy = DIRECCION[canto]
    adentro = apoya.vec(dx, dy, 0)
    if en is not None:
        vertical = canto in ("IZQ", "DER")
        c1, c2 = (y1, y2) if vertical else (x1, x2)
        ts = [(c - c1) / (c2 - c1) for c in en]
    else:
        ts = [t0 + s / L for s in posiciones(largo, n)]
    for t in ts:
        x, y = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
        # la que apoya
        apoya.agujero_canto(x, y, PERNO["d"], PERNO["prof"], canto, "3in1")
        cx, cy = x + dx * CAM["desde_canto"], y + dy * CAM["desde_canto"]
        apoya.agujero(cx, cy, CAM["d"], CAM["prof"], cara_cam, "3in1")
        # la que recibe
        pw = apoya.mundo(x, y, zm)
        rx, ry, _ = recibe.local(pw)
        recibe.agujero(rx, ry, RECIBE["d"], RECIBE["prof"], cara_r, "3in1")
        # herrajes (marco de la biblioteca: origen sobre el agujero, Z hacia adentro)
        zc = 0.0 if cara_cam == "A" else -apoya.T
        haciaz = apoya.vec(0, 0, -1) if cara_cam == "A" else apoya.vec(0, 0, 1)
        herraje(apoya.mueble, "Excentrica O15", apoya.mundo(cx, cy, zc), haciaz, adentro,
                "excentrica", cam=CAM)
        herraje(apoya.mueble, "Perno O8 x 33", pw, adentro, (0, 0, 1) if abs(adentro[2]) < 0.9 else (1, 0, 0),
                "perno", perno=PERNO, recibe=RECIBE)
        # receptor: solo si es de taco (O10). Con rosca para madera (O5) el perno
        # entra directo en la placa y no hay pieza que dibujar.
        if RECIBE["d"] > 6.0:
            zr = 0.0 if cara_r == "A" else -recibe.T
            hz = recibe.vec(0, 0, -1) if cara_r == "A" else recibe.vec(0, 0, 1)
            herraje(recibe.mueble, "Receptor O%g" % RECIBE["d"], recibe.mundo(rx, ry, zr), hz, None,
                    "receptor", recibe=RECIBE)
    return n


def bisagras(puerta, soporte, canto_puerta, canto_frente_soporte, cara_soporte, cuantas=None):
    """Bisagra de cazoleta. Puerta: cara A = interior, Y local a lo largo del canto
    de bisagras. Soporte (lateral o montante): Y local = arriba, y se da su canto
    de adelante y la cara que mira a la puerta."""
    largo = puerta.H
    n = cuantas or (3 if largo > 900 else 2)
    m = min(MARGEN_BISAGRA, largo / 3.0)
    alturas = [m + (largo - 2 * m) * i / (n - 1.0) for i in range(n)]
    dx, dy = DIRECCION[canto_puerta]
    x_edge = 0.0 if canto_puerta == "IZQ" else puerta.W
    fdx, _ = DIRECCION[canto_frente_soporte]
    x_frente = 0.0 if canto_frente_soporte == "IZQ" else soporte.W
    for yh in alturas:
        cx = x_edge + dx * CAZ["desde_canto"]
        puerta.agujero(cx, yh, CAZ["d"], CAZ["prof"], "A", "HINGE")
        tx = x_edge + dx * (CAZ["desde_canto"] + TOR["adentro"])
        for sg in (-1, 1):
            puerta.agujero(tx, yh + sg * TOR["a_lo_largo"], TOR["d"], TOR["prof"], "A", "HINGESCREW")
        centro = puerta.mundo(cx, yh, 0.0)
        _, ys, _ = soporte.local(centro)
        # placa base: 2 agujeros a 37 del frente, uno arriba del otro (+-16 de la cazoleta)
        xb = x_frente + fdx * BASE["frente"]
        for sg in (-1, 1):
            soporte.agujero(xb, ys + sg * BASE["a_lo_largo"], BASE["d"], BASE["prof"], cara_soporte, "jlHoleEX")
        # herraje: X de la bisagra hacia el centro de la puerta, Z hacia adentro de la puerta
        x_h = puerta.vec(dx, dy, 0)
        pb = soporte.mundo(x_frente + fdx * 36.0, ys, 0.0 if cara_soporte == "A" else -soporte.T)
        dx_lat = dot(sub(pb, centro), x_h)
        herraje(puerta.mueble, "Bisagra O35 base %g" % round(dx_lat, 1), centro, puerta.vec(0, 0, -1), x_h,
                "bisagra", dx_lat=dx_lat)
    return n


def correderas(lateral, cara, canto_frente, alturas_y):
    """O3 x 10 del riel en el lateral (cara interior) a 37 y 413 del frente."""
    fdx, _ = DIRECCION[canto_frente]
    x0 = 0.0 if canto_frente == "IZQ" else lateral.W
    for y in alturas_y:
        for a in CORR["a"]:
            lateral.agujero(x0 + fdx * a, y, CORR["d"], CORR["prof"], cara, "slideRail")
        zc = 0.0 if cara == "A" else -lateral.T
        hacia_hueco = lateral.vec(0, 0, 1) if cara == "A" else lateral.vec(0, 0, -1)
        herraje(lateral.mueble, "Corredera bolas 450", lateral.mundo(x0, y, zc), hacia_hueco,
                lateral.vec(fdx, 0, 0), "corredera", largo=CORR["largo"])


def pines(lateral, cara, xs, y_centros):
    for yc in y_centros:
        for dy in PIN["banda"]:
            for x in xs:
                lateral.agujero(x, yc + dy, PIN["d"], PIN["prof"], cara, "shelfPin")


# ------------------------------------------------------------- tiradores --
def _afuera(frente):
    """Vector del mundo que sale del frente por la cara vista (cara B)."""
    return frente.vec(0, 0, -1)


def tirador(frente, cx, cy, sentido):
    """Barral de 128 entre centros. (cx, cy) = centro del barral en el marco del
    frente; sentido = vector local (1, 0) horizontal o (0, 1) vertical. Dos
    agujeros O5 PASANTES (tornillo M4), perforados desde la cara A."""
    ux, uy = sentido
    e = TIRADOR["entre_centros"] / 2.0
    for sg in (-1, 1):
        frente.agujero(cx + sg * ux * e, cy + sg * uy * e, TIRADOR["d"], frente.T, "A", "handle")
    herraje(frente.mueble, "Tirador barral 128", frente.mundo(cx, cy, -frente.T), _afuera(frente),
            frente.vec(ux, uy, 0), "tirador", entre_centros=TIRADOR["entre_centros"])


def tirador_puerta(puerta, canto_libre):
    """Barral vertical en una puerta de bajo mesada: a 45 del canto que abre y
    centrado a 150 del borde de arriba."""
    x = TIRADOR["del_canto"] if canto_libre == "IZQ" else puerta.W - TIRADOR["del_canto"]
    tirador(puerta, x, puerta.H - TIRADOR["del_borde"], (0, 1))


def perilla(frente, x, y):
    frente.agujero(x, y, PERILLA["d"], frente.T, "A", "handle")
    herraje(frente.mueble, "Perilla", frente.mundo(x, y, -frente.T), _afuera(frente), frente.vec(1, 0, 0),
            "perilla")


def perilla_puerta(puerta, canto_libre):
    """Perilla de alacena: a 40 del canto que abre y 50 del borde de abajo."""
    x = PERILLA["del_canto"] if canto_libre == "IZQ" else puerta.W - PERILLA["del_canto"]
    perilla(puerta, x, PERILLA["del_borde"])


# --------------------------------------------------------------- vitrina --
def minifix_marco(trav, lado, mont, canto_mont, y_cam, y_tarugo):
    """Union de la punta `lado` ('IZQ'/'DER') del travesano con el canto interior
    `canto_mont` del montante: Minifix (perno en la punta del travesano, excentrica
    en su cara A = atras, O5 x 12 en el canto del montante) + tarugo O8."""
    dx = 1 if lado == "IZQ" else -1
    xe = 0.0 if lado == "IZQ" else trav.W
    # perno + excentrica en el travesano
    trav.agujero_canto(xe, y_cam, PERNO["d"], PERNO["prof"], lado, "3in1")
    cx = xe + dx * CAM["desde_canto"]
    trav.agujero(cx, y_cam, CAM["d"], CAM["prof"], "A", "3in1")
    # tarugo en la punta del travesano
    trav.agujero_canto(xe, y_tarugo, TARUGO["d"], TARUGO["prof"], lado, "dowel")
    # en el canto del montante: receptor O5 y tarugo, donde caen los del travesano
    for y, d, prof, sym in ((y_cam, RECIBE["d"], RECIBE["prof"], "3in1"),
                            (y_tarugo, TARUGO["d"], TARUGO["prof"], "dowel")):
        pw = trav.mundo(xe, y, -trav.T / 2.0)
        mx, my, _ = mont.local(pw)
        xm = 0.0 if canto_mont == "IZQ" else mont.W
        if abs(mx - xm) > 0.5:
            raise RuntimeError("marco: la punta del travesano no cae en el canto del montante (%s)" % trav.nombre)
        mont.agujero_canto(xm, my, d, prof, canto_mont, sym)
    # herrajes (como en tres_en_uno)
    adentro = trav.vec(dx, 0, 0)
    herraje(trav.mueble, "Excentrica O15", trav.mundo(cx, y_cam, 0.0), trav.vec(0, 0, -1), adentro, "excentrica", cam=CAM)
    pw = trav.mundo(xe, y_cam, -trav.T / 2.0)
    herraje(trav.mueble, "Perno O8 x 33", pw, adentro, (0, 0, 1) if abs(adentro[2]) < 0.9 else (1, 0, 0),
            "perno", perno=PERNO, recibe=RECIBE)


def vitrina_marco(puerta, cols=2, filas=3):
    """Puerta vitrina como MARCO de 4 piezas de madera maciza en el lugar de `puerta`
    (que se usa solo como marco de referencia y NO se agrega al mueble). Devuelve
    {'IZQ': montante, 'DER': montante, 'ABAJO': travesano, 'ARRIBA': travesano}.
    El que llama cuelga las bisagras del montante que corresponda y pone la perilla."""
    m, t = VIT["montante"], VIT["travesano"]
    W, H, mu = puerta.W, puerta.H, puerta.mueble
    nm = puerta.nombre

    def pieza(sufijo, x0, y0, w, h):
        return Placa(mu, "%s montante %s" % (nm, sufijo) if w == m else "%s travesano %s" % (nm, sufijo),
                     w, h, T, puerta.mundo(x0, y0, 0.0), puerta.ex, puerta.ey, MACIZA, rol="PUERTA",
                     material=MADERA, veta="VERTICAL" if w == m else "HORIZONTAL")

    mi = pieza("izq", 0.0, 0.0, m, H)
    md = pieza("der", W - m, 0.0, m, H)
    ta = pieza("abajo", m, 0.0, W - 2 * m, t)
    tr = pieza("arriba", m, H - t, W - 2 * m, t)
    r, prof = VIT["rebaje_ancho"], VIT["rebaje_prof"]
    # rebaje del vidrio = ranura de 12 x 5 por la cara A (atras) sobre el canto interior.
    # En los montantes va solo entre los travesanos (hasta donde llega el vidrio).
    mi.ranura(m - r / 2.0, t - r, m - r / 2.0, H - t + r, r, prof, "A", "glassSlot")
    md.ranura(r / 2.0, t - r, r / 2.0, H - t + r, r, prof, "A", "glassSlot")
    ta.ranura(0.0, t - r / 2.0, ta.W, t - r / 2.0, r, prof, "A", "glassSlot")
    tr.ranura(0.0, r / 2.0, tr.W, r / 2.0, r, prof, "A", "glassSlot")
    # uniones: Minifix al centro del travesano, tarugo a 12 del borde de afuera
    yc = t / 2.0
    minifix_marco(ta, "IZQ", mi, "DER", yc, TARUGO["del_borde"])
    minifix_marco(ta, "DER", md, "IZQ", yc, TARUGO["del_borde"])
    minifix_marco(tr, "IZQ", mi, "DER", yc, t - TARUGO["del_borde"])
    minifix_marco(tr, "DER", md, "IZQ", yc, t - TARUGO["del_borde"])
    # vidrio: una hoja de 4 que entra 11 en cada ranura (1 de juego)
    gw, gh = W - 2 * m + 2 * r - 2.0, H - 2 * t + 2 * r - 2.0
    herraje(mu, "Vidrio %dx%d" % (int(round(gw)), int(round(gh))),
            puerta.mundo(m - r + 1.0, t - r + 1.0, -prof), puerta.vec(0, 0, 1), puerta.vec(1, 0, 0),
            "vidrio", ancho=gw, alto=gh, espesor=VIT["vidrio"])
    # cruz de listones 25 x 8 pegada al frente del vidrio, dentro del hueco
    aw, ah = W - 2 * m, H - 2 * t
    herraje(mu, "Parrilla %dx%d %dx%d" % (int(round(aw)), int(round(ah)), cols, filas),
            puerta.mundo(m, t + ah, -prof), puerta.vec(0, 0, -1), puerta.vec(1, 0, 0),   # esquina de ARRIBA: ey local queda hacia abajo
            "parrilla", ancho=aw, alto=ah, cols=cols, filas=filas, liston=VIT["parante"], esp=VIT["parante_esp"])
    piezas = {"IZQ": mi, "DER": md, "ABAJO": ta, "ARRIBA": tr}
    for p in piezas.values():
        p.vitrina = dict(cols=cols, filas=filas, vidrio=(gw, gh))
    AVISOS.append("%s / %s: marco de madera maciza de 4 piezas con Minifix + tarugo O8; vidrio de 4 de %.0f x %.0f "
                  "en ranura 12 x 5 (junquillos a mano); cruz de listones %gx%g (%dx%d) a mano. Piezas de madera: "
                  "NO van a AutoCUT (lista aparte)." % (mu, nm, gw, gh, VIT["parante"], VIT["parante_esp"], cols, filas))
    return piezas


def puerta_vitrina(P, puerta, canto_bisagra, soporte, canto_frente_soporte, cara_soporte, cols=2, filas=3):
    """Arma el marco en el lugar de `puerta`, lo agrega a P, cuelga las bisagras del
    montante del lado `canto_bisagra` y pone la perilla en el otro."""
    mk = vitrina_marco(puerta, cols, filas)
    P += [mk["IZQ"], mk["DER"], mk["ABAJO"], mk["ARRIBA"]]
    libre = "DER" if canto_bisagra == "IZQ" else "IZQ"
    bisagras(mk[canto_bisagra], soporte, canto_bisagra, canto_frente_soporte, cara_soporte)
    perilla_puerta(mk[libre], libre)
    return mk


# ================================================================ muebles ==
MUEBLES = []          # (nombre, [placas])


def mueble(nombre):
    lista = []
    MUEBLES.append((nombre, lista))
    return lista


def fondo_bajo_normal(mu, nombre, x0, x1, P):
    """Fondo de 5 en las ranuras de los laterales y del piso (arriba lo tapa el
    travesano trasero, al que se atornilla)."""
    y0, y1 = BP["desde_atras"] - 2.5, BP["desde_atras"] + 2.5
    f = placa_caja(nombre, "Fondo", x0 + T - 5, x1 - T + 5, y0, y1,
                   Z_BAJO + T - 5, Z_BAJO + H_BAJO - 1, "+Y", "-X", FONDO5, rol="FONDO",
                   material=FIB)
    f.T = 5.0
    P.append(f)
    return f


def bajo_normal(nombre, x0, ancho, tipo):
    """Bajo mesada de la pared larga. tipo: 'pileta' | 'cajonera' | 'puerta'
    (una sola puerta a todo el alto, bisagras en el lateral de la izquierda
    de quien mira = el del extremo de la pared)."""
    P = mueble(nombre)
    x1 = x0 + ancho
    z0, z1 = Z_BAJO, Z_BAJO + H_BAJO
    Y1 = F_BAJO
    frente = ("+Y",)
    # u menor = derecha de quien mira de frente (pared larga: el que mira va hacia -Y)
    li = placa_caja(nombre, "Lateral der", x0, x0 + T, 0, Y1, z0, z1, "+X", "+Y", BLANCO, cantos=frente)
    ld = placa_caja(nombre, "Lateral izq", x1 - T, x1, 0, Y1, z0, z1, "-X", "-Y", BLANCO, cantos=frente)
    piso = placa_caja(nombre, "Piso", x0 + T, x1 - T, 0, Y1, z0, z0 + T, "+Z", "+X", BLANCO, cantos=frente)
    P += [li, ld, piso]
    if tipo == "pileta":
        tf = placa_caja(nombre, "Travesano delantero", x0 + T, x1 - T, Y1 - T, Y1, z1 - 100, z1, "-Y", "+X",
                        BLANCO, cantos=("+Z",))
    else:
        tf = placa_caja(nombre, "Travesano delantero", x0 + T, x1 - T, Y1 - 100, Y1, z1 - T, z1, "-Z", "+X",
                        BLANCO, cantos=frente)
    tb = placa_caja(nombre, "Travesano trasero", x0 + T, x1 - T, 0, T, z1 - 100, z1, "-Y", "+X", BLANCO)
    P += [tf, tb]
    fondo = fondo_bajo_normal(P, nombre, x0, x1, P)
    # ranuras del fondo: laterales (cara A = interior; li: x desde atras, ld: x desde el frente)
    li.ranura(BP["desde_atras"], 0, BP["desde_atras"], li.H, BP["ancho"], BP["prof"], "A", "BP")
    ld.ranura(ld.W - BP["desde_atras"], 0, ld.W - BP["desde_atras"], ld.H, BP["ancho"], BP["prof"], "A", "BP")
    piso.ranura(0, BP["desde_atras"], piso.W, BP["desde_atras"], BP["ancho"], BP["prof"], "A", "BP")
    # uniones
    tres_en_uno(piso, li, "B"); tres_en_uno(piso, ld, "B")
    cam_tf = "A"
    tres_en_uno(tf, li, cam_tf); tres_en_uno(tf, ld, cam_tf)
    tres_en_uno(tb, li, "A"); tres_en_uno(tb, ld, "A")
    # frentes
    xa, xb = x0 + LUZ, x1 - LUZ
    za, zb = z0 + LUZ, z1 - LUZ
    if tipo == "pileta":
        hf = 185.0
        ff = placa_caja(nombre, "Frente fijo", xa, xb, Y1, Y1 + T, zb - hf, zb, "-Y", "+X", VERDE,
                        rol="PUERTA", cantos=("+X", "-X", "+Z", "-Z"))
        zp1 = zb - hf - JUNTA
        xm = (xa + xb) / 2.0
        pi = placa_caja(nombre, "Puerta der", xa, xm - JUNTA / 2, Y1, Y1 + T, za, zp1, "-Y", "+X", VERDE,
                        rol="PUERTA", cantos=("+X", "-X", "+Z", "-Z"))
        pd = placa_caja(nombre, "Puerta izq", xm + JUNTA / 2, xb, Y1, Y1 + T, za, zp1, "-Y", "+X", VERDE,
                        rol="PUERTA", cantos=("+X", "-X", "+Z", "-Z"))
        P += [ff, pi, pd]
        # pi cuelga de li (X mundo menor = su canto IZQ); li tiene el frente en x = W (DER)
        bisagras(pi, li, "IZQ", "DER", "A")
        bisagras(pd, ld, "DER", "IZQ", "A")
        tirador_puerta(pi, "DER"); tirador_puerta(pd, "IZQ")
    elif tipo == "puerta":
        pu = placa_caja(nombre, "Puerta", xa, xb, Y1, Y1 + T, za, zb, "-Y", "+X", VERDE,
                        rol="PUERTA", cantos=("+X", "-X", "+Z", "-Z"))
        P.append(pu)
        # cuelga de ld (X mundo mayor = canto DER = izquierda de quien mira); abre por el canto IZQ
        bisagras(pu, ld, "DER", "IZQ", "A")
        tirador_puerta(pu, "IZQ")
    else:
        n = 4
        hf = (zb - za - (n - 1) * JUNTA) / n
        inner0, inner1 = x0 + T, x1 - T
        bx0, bx1 = inner0 + CORR["juego"], inner1 - CORR["juego"]
        hc = 120.0
        alt_li, alt_ld = [], []
        for i in range(n):
            fz0 = za + i * (hf + JUNTA)
            fr = placa_caja(nombre, "Frente cajon %d" % (i + 1), xa, xb, Y1, Y1 + T, fz0, fz0 + hf, "-Y", "+X",
                            VERDE, rol="PUERTA", cantos=("+X", "-X", "+Z", "-Z"))
            P.append(fr)
            tirador(fr, fr.W / 2.0, fr.H / 2.0, (1, 0))      # barral horizontal centrado
            cz0 = fz0 + 23.5
            cz1 = cz0 + hc
            yb0, yb1 = Y1 - CORR["largo"], Y1
            cn = "Cajon %d " % (i + 1)
            # frente y contrafrente van por fuera; los costados entre ellos (piezas >= 250)
            cf = placa_caja(nombre, cn + "frente", bx0, bx1, yb1 - T, yb1, cz0, cz1, "-Y", "+X", BLANCO,
                            cantos=("+Z",))
            cc = placa_caja(nombre, cn + "contrafrente", bx0, bx1, yb0, yb0 + T, cz0, cz1, "+Y", "-X", BLANCO,
                            cantos=("+Z",))
            ci = placa_caja(nombre, cn + "costado der", bx0, bx0 + T, yb0 + T, yb1 - T, cz0, cz1, "+X", "+Y",
                            BLANCO, cantos=("+Z",))
            cd = placa_caja(nombre, cn + "costado izq", bx1 - T, bx1, yb0 + T, yb1 - T, cz0, cz1, "-X", "-Y",
                            BLANCO, cantos=("+Z",))
            ya = BP_CAJON["desde_abajo"]
            fb = placa_caja(nombre, cn + "fondo", bx0 + T - 4.5, bx1 - T + 4.5, yb0 + T - 4.5, yb1 - T + 4.5,
                            cz0 + ya - 2.5, cz0 + ya + 2.5, "+Z", "+X", FONDO5, rol="FONDO", material=FIB)
            P += [cf, cc, ci, cd, fb]
            for c in (ci, cd):
                c.ranura(0, ya, c.W, ya, BP_CAJON["ancho"], BP_CAJON["prof"], "A", "BP")
            for c in (cf, cc):
                c.ranura(13.0, ya, c.W - 13.0, ya, BP_CAJON["ancho"], BP_CAJON["prof"], "A", "BP")
            # el conector va ARRIBA de la corredera (que atornilla a media altura por
            # afuera): a media altura el O3 del riel se mete en el O8 del perno.
            for c in (ci, cd):
                tres_en_uno(c, cf, "A", en=[hc - 30.0]); tres_en_uno(c, cc, "A", en=[hc - 30.0])
            # correderas: costados (cara B = exterior) a media altura, 37/413 del frente del cajon
            ymid = hc / 2.0
            # ci: x desde atras, el frente del cajon queda en x = W + T; cd: x desde el frente (-T)
            for a in CORR["a"]:
                ci.agujero(ci.W + T - a, ymid, CORR["d"], CORR["prof"], "B", "slideRail")
                cd.agujero(a - T, ymid, CORR["d"], CORR["prof"], "B", "slideRail")
            alt = (cz0 + cz1) / 2.0 - z0
            alt_li.append(alt); alt_ld.append(alt)
        correderas(li, "A", "DER", alt_li)
        correderas(ld, "A", "IZQ", alt_ld)
    # patas
    for (px, py) in ((x0 + 60, 60), (x1 - 60, 60), (x0 + 60, Y1 - 80), (x1 - 60, Y1 - 80)):
        herraje(nombre, "Pata regulable", (px, py, Z_BAJO), (0, 0, -1), (1, 0, 0), "pata")
    return P


def diagonal(PA, PB):
    """Ejes de la diagonal: t de PA a PB, n hacia afuera (frente)."""
    t = norm(sub(PB, PA))
    n = norm(cross(t, (0, 0, 1)))
    if n[0] + n[1] < 0:
        n = mul(n, -1)
    return t, n


def esquinero(nombre, alto, prof, z0, z1, estantes, techo=True, cenefa=False):
    """Esquinero diagonal 800 x 800. Laterales por fuera (en las puntas de las dos
    alas), piso y techo pentagonales entre ellos, dos fondos, dos montantes a 45
    y una puerta sobre la diagonal colgada del montante de la punta A."""
    P = mueble(nombre)
    E = 800.0
    li = E - T                       # cara interior de los laterales (782)
    # lateral A: pared larga, en X = 782..800, Y 0..prof ; lateral B: pared corta
    # la: x = 0 en el frente (Y = prof); lb: x = 0 atras (X = 0)
    la = placa_caja(nombre, "Lateral A", li, E, 0, prof, z0, z1, "-X", "-Y", BLANCO, cantos=("+Y",))
    lb = placa_caja(nombre, "Lateral B", 0, prof, li, E, z0, z1, "-Y", "+X", BLANCO, cantos=("+X",))
    P += [la, lb]
    PA, PB = (li, prof, 0.0), (prof, li, 0.0)
    t, n = diagonal(PA, PB)
    L = math.hypot(PB[0] - PA[0], PB[1] - PA[1])
    # pentagono en el plano (X local = +X mundo, Y local = +Y mundo)
    penta = [(0, 0), (li, 0), (li, prof), (prof, li), (0, li)]

    def horizontal(nm, zb, A, poli, rol="", cantos_diag=True, tex=BLANCO):
        # A = '+Z' (cara A arriba) o '-Z'
        if A == "+Z":
            p = Placa(nombre, nm, li, li, T, (0, 0, zb + T), (1, 0, 0), (0, 1, 0), tex, rol=rol,
                      contorno=poli)
        else:
            # cara A abajo: X local = +X, Y local = -Y -> O en (0, li, zb)
            p = Placa(nombre, nm, li, li, T, (0, li, zb), (1, 0, 0), (0, -1, 0), tex, rol=rol,
                      contorno=[(x, li - y) for (x, y) in reversed(poli)])
        if cantos_diag:
            p.cantos_diagonal = CANTO
        return p

    piso = horizontal("Piso", z0 + (0 if not cenefa else 0), "+Z", penta)
    P.append(piso)
    if techo:
        tec = horizontal("Techo", z1 - T, "-Z", penta)
        P.append(tec)
    # ranuras de fondo en L (cara A = interior): piso arriba, techo abajo
    d = BP["desde_atras"]
    # Las dos ranuras NO se tocan: en L forman un solo fondo de ranura que ExportarPiezas
    # no reconoce (se probo el 29/09). La del fondo B va desde atras (y = d-3) hasta el
    # lateral; la del fondo A arranca 1 mm despues de la otra (x = d+4).
    xa0 = d + 3.0 + 1.0
    for p in [piso] + ([tec] if techo else []):
        if p is piso:
            p.ranura(xa0, d, li, d, BP["ancho"], BP["prof"], "A", "BP")            # a lo largo de X
            p.ranura(d, d - 3.0, d, li, BP["ancho"], BP["prof"], "A", "BP")        # a lo largo de Y
        else:
            p.ranura(xa0, li - d, li, li - d, BP["ancho"], BP["prof"], "A", "BP")
            p.ranura(d, li - d + 3.0, d, 0, BP["ancho"], BP["prof"], "A", "BP")
    la.ranura(la.W - d, 0, la.W - d, la.H, BP["ancho"], BP["prof"], "A", "BP")
    lb.ranura(d, 0, d, lb.H, BP["ancho"], BP["prof"], "A", "BP")
    # fondos
    zf0 = z0 + T - 5
    zf1 = (z1 - T + 5) if techo else (z1 - 1)
    fa = placa_caja(nombre, "Fondo A", xa0 + 0.5, li + 5, d - 2.5, d + 2.5, zf0, zf1, "+Y", "-X", FONDO5,
                    rol="FONDO", material=FIB)
    fb = placa_caja(nombre, "Fondo B", d - 2.5, d + 2.5, d - 2.5, li + 5, zf0, zf1, "+X", "+Y", FONDO5,
                    rol="FONDO", material=FIB)
    P += [fa, fb]
    # montantes a 45: 80 de ancho hacia adentro, 18 a lo largo de la diagonal
    W_M = 80.0
    zm0, zm1 = z0 + T, (z1 - T) if techo else z1
    adentro = mul(n, -1)

    def montante(nm, s0, punta_a):
        """Cara A = la que mira al centro de la puerta. Montante A (s 0..18): X hacia
        adentro desde el frente (frente = IZQ). Montante B (s L-18..L): X desde adentro
        hacia el frente (frente = DER)."""
        ey = (0, 0, 1)
        if punta_a:
            ex = adentro                                  # ez = +t
            O = add(PA, mul(t, s0 + T))
        else:
            ex = n                                        # ez = -t
            O = add(add(PA, mul(t, s0)), mul(n, -W_M))
        return Placa(nombre, nm, W_M, zm1 - zm0, T, (O[0], O[1], zm0), ex, ey, BLANCO, cantos=(n,))

    m1 = montante("Montante A", 0.0, True)
    m2 = montante("Montante B", L - T, False)
    for m in (m1, m2):
        if m.cara_hacia(add(add(PA, mul(t, L / 2)), (0, 0, zm0 + 10))) != "A":
            raise RuntimeError("montante con la cara A al reves")
    P += [m1, m2]
    # uniones
    tres_en_uno(piso, la, "B"); tres_en_uno(piso, lb, "B")
    if techo:
        tres_en_uno(tec, la, "A"); tres_en_uno(tec, lb, "A")
    for m in (m1, m2):
        tres_en_uno(m, piso, "A", cuantos=1)
        if techo:
            tres_en_uno(m, tec, "A", cuantos=1)
    # puerta sobre la diagonal
    zd0, zd1 = (z0 + LUZ, z1 - LUZ)
    if cenefa:
        zd0 = z0 + LUZ
    s_a, s_b = LUZ, L - LUZ
    ex_p = mul(t, -1)                         # X local de la puerta: de B hacia A (mirando de frente, izq->der)
    ey_p = (0, 0, 1)
    ez_p = cross(ex_p, ey_p)                  # tiene que mirar hacia adentro (cara A interior)
    Op = add(add(PA, mul(t, s_b)), (0, 0, zd0))
    if dot(ez_p, n) > 0:
        raise RuntimeError("marco de la puerta al reves")
    Op = add(Op, mul(n, 0.0))
    pu = Placa(nombre, "Puerta", s_b - s_a, zd1 - zd0, T, Op, ex_p, ey_p, VERDE, rol="PUERTA",
               cantos=(t, mul(t, -1), (0, 0, 1), (0, 0, -1)))
    # la puerta: su canto DER (x=W) es el de la punta A
    cara_m1 = m1.cara_hacia(add(PA, mul(t, L / 2)))
    if cenefa:                                # alacena: vitrina de madera (marco de 4), perilla
        puerta_vitrina(P, pu, "DER", m1, "IZQ", cara_m1, cols=2, filas=3)
    else:                                     # bajo: puerta lisa con barral vertical
        P.append(pu)
        bisagras(pu, m1, "DER", "IZQ", cara_m1)
        tirador_puerta(pu, "IZQ")
    # estantes regulables: pentagono retirado 82 de la diagonal, 1 del lateral, 31 del fondo
    off = W_M + 2.0
    k = (li + prof) - off * S2               # x + y <= k
    lim = li - 1.0
    base_f = d + 3.5
    poli = [(base_f, base_f), (lim, base_f), (lim, k - lim), (k - lim, lim), (base_f, lim)]
    poli = [(x - base_f, y - base_f) for (x, y) in poli]
    interior0 = z0 + T
    interior1 = (z1 - T) if techo else z1
    alt_int = interior1 - interior0
    ycs = [alt_int * (i + 1) / (estantes + 1.0) for i in range(estantes)]
    # pines en los dos laterales: fila de atras a 68 del fondo, fila de adelante a +32*k
    y_max = k - lim - base_f                 # hasta donde llega el estante sobre el lateral
    fila_atras = 68.0
    fila_adel = fila_atras + PASO * math.floor((k - lim - 25.0 - fila_atras) / PASO)
    for i, yc in enumerate(ycs):
        zs = interior0 + yc
        es = Placa(nombre, "Estante %d" % (i + 1), lim - base_f, lim - base_f, T,
                   (base_f, base_f, zs + T), (1, 0, 0), (0, 1, 0), BLANCO, contorno=poli)
        es.cantos_diagonal = CANTO
        P.append(es)
        for (lat, xs) in ((la, (la.W - fila_atras, la.W - fila_adel)), (lb, (fila_atras, fila_adel))):
            yl = zs - z0 - 6.0                 # el pin queda 6 abajo del estante... centro del agujero
            pines(lat, "A", xs, [zs - z0 - 8.0])
            for x in xs:
                herraje(nombre, "Soporte estante O5", lat.mundo(x, zs - z0 - 8.0, 0.0), lat.vec(0, 0, -1),
                        (0, 0, 1), "pin")
    return P, piso, pu, (PA, PB, t, n, L), la, lb


def bajo_esquinero():
    nombre = "B1 Esquinero bajo"
    P, piso, pu, geo, la, lb = esquinero(nombre, H_BAJO, F_BAJO, Z_BAJO, Z_BAJO + H_BAJO, estantes=1)
    for (px, py) in ((60, 60), (740, 60), (60, 740), (740, 500), (500, 740)):
        herraje(nombre, "Pata regulable", (px, py, Z_BAJO), (0, 0, -1), (1, 0, 0), "pata")
    return P


def alacena_esquinero():
    nombre = "A1 Esquinero alacena"
    z0, z1 = Z_CUERPO0, Z_CUERPO1
    P, piso, pu, (PA, PB, t, n, L), la, lb = esquinero(nombre, z1 - z0, F_ALTO, z0, z1,
                                                       estantes=2, cenefa=True)
    tec = [p for p in P if p.nombre == "Techo"][0]
    # dos travesanos traseros bajo el techo, uno por pared, detras de los fondos (que van a 25..30):
    # 3 en 1 al lateral de su punta y al techo; por ellos se cuelga el mueble.
    li_ = 800.0 - T
    zt0, zt1 = z1 - T - TRAV_ALTO, z1 - T
    ta = placa_caja(nombre, "Travesano A", 31.0, li_, 0, T, zt0, zt1, "-Y", "+X", BLANCO)
    tb = placa_caja(nombre, "Travesano B", 0, T, 31.0, li_, zt0, zt1, "-X", "-Y", BLANCO)
    P += [ta, tb]
    tres_en_uno(ta, la, "A", cuantos=1); tres_en_uno(tb, lb, "A", cuantos=1)
    tres_en_uno(ta, tec, "A", cuantos=2); tres_en_uno(tb, tec, "A", cuantos=2)
    AVISOS.append("%s: se cuelga por los dos travesanos traseros (18 x %g) con %d tornillos a la pared "
                  "cada uno, a mano." % (nombre, TRAV_ALTO, TRAV_TORNILLOS))
    led_piso(piso, nombre, diagonal_geo=(PA, PB, t, n, L))
    return P


def led_piso(piso, nombre, diagonal_geo=None, frente_y=None):
    """Ranura 10x10 en la cara B (abajo) del piso de la alacena, a 45 del frente."""
    if diagonal_geo is None:
        # piso normal: cara A arriba, X local a lo ancho, Y local hacia el frente
        y = piso.H - LED["desde_frente"]
        x1, x2 = LED["margen"] + T, piso.W - LED["margen"] - T
        piso.ranura(x1, y, x2, y, LED["ancho"], LED["prof"], "B", "lightSlot")
        herraje(nombre, "Tira LED %d" % int(round(x2 - x1)), piso.mundo(x1, y, -piso.T),
                piso.vec(0, 0, 1), piso.ex, "led", largo=x2 - x1)
    else:
        # esquinero: la diagonal no es paralela a X ni a Y -> ranura diagonal NO se puede
        # en la perforadora (solo X/Y). Se pone la tira sin ranura, pegada, detras de la cenefa.
        PA, PB, t, n, L = diagonal_geo
        p0 = add(add(PA, mul(t, 60.0)), mul(n, -LED["desde_frente"]))
        herraje(nombre, "Tira LED %d" % int(round(L - 120)), (p0[0], p0[1], piso.O[2] - piso.T),
                (0, 0, 1), t, "led", largo=L - 120.0)
        AVISOS.append("A1 Esquinero alacena: la tira LED va PEGADA bajo el piso, sin ranura "
                      "(la diagonal no es paralela a X/Y y la perforadora no ranura en diagonal).")


def alacena(nombre, x0, ancho, eje="X", tipo="vitrina", cols=2, puertas=2):
    """Alacena normal, estilo COCINA MLV: piso y techo por fuera (a todo el ancho),
    laterales entre ellos, cenefa abajo y cornisa arriba (las dos retiradas 18).

    tipo 'vitrina': `puertas` (1 o 2) puertas vitrina de madera maciza (marco de 4
    piezas con Minifix, vidrio, cruz cols x 3) con perilla.
    tipo 'rebatible': dos hojas rebatibles hacia arriba, la de arriba (un tercio)
    colgada del techo y la de abajo del estante fijo que separa las dos.

    Se trabaja en (u, v, w): u a lo ancho, v hacia el frente, w arriba, siempre
    mano derecha. eje 'X' = pared larga: u = +X, v = +Y. eje 'Y' = pared corta:
    v = +X y u = -Y (u crece hacia la pared larga). x0 = coordenada del mundo
    donde arranca el mueble sobre la pared (X o Y menor)."""
    P = mueble(nombre)
    z0, z1 = Z_CUERPO0, Z_CUERPO1
    D = F_ALTO
    if eje == "X":
        U, mU, V, mV = "+X", "-X", "+Y", "-Y"
        u0, u1 = x0, x0 + ancho

        def caja(a0, a1, b0, b1, c0, c1):
            return (a0, a1, b0, b1, c0, c1)
    else:
        U, mU, V, mV = "-Y", "+Y", "+X", "-X"
        u0, u1 = -(x0 + ancho), -x0

        def caja(a0, a1, b0, b1, c0, c1):
            return (b0, b1, -a1, -a0, c0, c1)

    def pc(nm, a0, a1, b0, b1, c0, c1, A, X, tex, **kw):
        b = caja(a0, a1, b0, b1, c0, c1)
        return placa_caja(nombre, nm, b[0], b[1], b[2], b[3], b[4], b[5], A, X, tex, **kw)

    piso = pc("Piso", u0, u1, 0, D, z0, z0 + T, "+Z", U, BLANCO, cantos=(V,))          # y hacia el frente
    tec = pc("Techo", u0, u1, 0, D, z1 - T, z1, "-Z", U, BLANCO, cantos=(V,))          # y hacia atras
    # lateral en u0 = derecha de quien mira; x desde atras. En u1 = izquierda; x desde el frente.
    ld = pc("Lateral der", u0, u0 + T, 0, D, z0 + T, z1 - T, U, V, BLANCO, cantos=(V,))
    li = pc("Lateral izq", u1 - T, u1, 0, D, z0 + T, z1 - T, mU, mV, BLANCO, cantos=(V,))
    d = BP["desde_atras"]
    fo = pc("Fondo", u0 + T - 5, u1 - T + 5, d - 2.5, d + 2.5, z0 + T - 5, z1 - T + 5, V, mU, FONDO5,
            rol="FONDO", material=FIB)
    # travesano trasero bajo el techo, contra la pared, detras del fondo: por ahi se cuelga
    # (tornillos a la pared a mano). Cara A = la que mira a la pared (excentricas ocultas).
    tt = pc("Travesano trasero", u0 + T, u1 - T, 0, T, z1 - T - TRAV_ALTO, z1 - T, mV, U, BLANCO)
    P += [piso, tec, ld, li, fo, tt]
    # ranuras de fondo (cara A = interior), cortadas a 12,85 de las puntas como MLV
    piso.ranura(12.85, d, piso.W - 12.85, d, BP["ancho"], BP["prof"], "A", "BP")
    tec.ranura(12.85, tec.H - d, tec.W - 12.85, tec.H - d, BP["ancho"], BP["prof"], "A", "BP")
    ld.ranura(d, 0, d, ld.H, BP["ancho"], BP["prof"], "A", "BP")
    li.ranura(li.W - d, 0, li.W - d, li.H, BP["ancho"], BP["prof"], "A", "BP")
    # uniones: los laterales apoyan en piso y techo (excentrica en la cara interior)
    for l in (ld, li):
        tres_en_uno(l, piso, "A")
        if tipo != "rebatible":
            tres_en_uno(l, tec, "A")           # el rebatible rehace el techo mas abajo y lo une ahi
    tres_en_uno(tt, ld, "A"); tres_en_uno(tt, li, "A")
    AVISOS.append("%s: se cuelga por el travesano trasero (18 x %g, bajo el techo) con %d tornillos a la "
                  "pared, a mano." % (nombre, TRAV_ALTO, TRAV_TORNILLOS))
    led_piso(piso, nombre)
    ua, ub = u0 + LUZ, u1 - LUZ
    wa, wb = z0 + LUZ, z1 - LUZ
    cant = (U, mU, "+Z", "-Z")
    inner0, inner1 = z0 + T, z1 - T
    if tipo == "rebatible":
        # como la Alacena Spar: hoja REBATIBLE arriba (un tercio), colgada del techo con 2 bisagras
        # en su canto de arriba + pistones a gas; abajo 2 puertas comunes. Estante fijo en la junta.
        HF = round((wb - wa) * 0.45)                    # proporcion del render: ~45 % arriba, 55 % abajo
        zj = wb - HF - JUNTA / 2.0                      # centro de la junta
        # el techo se rehace con X local = profundidad (frente en x = W) para que bisagras() pueda
        # usarlo de soporte; misma ranura de fondo, en coordenadas giradas
        P.remove(tec)
        tec = pc("Techo", u0, u1, 0, D, z1 - T, z1, "-Z", V, BLANCO, cantos=(V,))
        tec.ranura(d, 12.85, d, tec.H - 12.85, BP["ancho"], BP["prof"], "A", "BP")
        P.insert(1, tec)
        for l in (ld, li):
            tres_en_uno(l, tec, "A")
        # estante fijo: cara A abajo (mira a la hoja de abajo), X local = profundidad (frente en
        # x = W); su cara de abajo queda 16,5 arriba del canto de la hoja de abajo, como un techo
        # sobre una puerta, asi la bisagra es la de siempre (base -6)
        es = pc("Estante fijo", u0 + T, u1 - T, d + 3.5, D, zj - T, zj, "-Z", V, BLANCO, cantos=(V,))
        # dos hojas REBATIBLES hacia arriba (X local hacia abajo: x = 0 = canto de arriba, el de
        # bisagras; Y local a lo ancho): la de arriba cuelga del techo, la de abajo del estante fijo
        pa_ = pc("Puerta rebatible arriba", ua, ub, D, D + T, zj + JUNTA / 2.0, wb, mV, "-Z", VERDE,
                 rol="PUERTA", cantos=cant)
        pb_ = pc("Puerta rebatible abajo", ua, ub, D, D + T, wa, zj - JUNTA / 2.0, mV, "-Z", VERDE,
                 rol="PUERTA", cantos=cant)
        P += [es, pa_, pb_]
        tres_en_uno(es, ld, "B"); tres_en_uno(es, li, "B")      # excentrica arriba
        bisagras(pa_, tec, "IZQ", "DER", "A")
        bisagras(pb_, es, "IZQ", "DER", "A")
        for h in (pa_, pb_):
            tirador(h, h.W - 50.0, h.H / 2.0, (0, 1))          # barral horizontal, 50 del borde de abajo
        AVISOS.append("%s: las dos hojas rebatibles (%g x %g arriba, %g x %g abajo) llevan 2 pistones a gas "
                      "cada una, atornillados a mano (sin CNC, sin dibujar)." % (nombre, pa_.H, pa_.W, pb_.H, pb_.W))
        # un estante regulable en el compartimiento de abajo
        zs = inner0 + (zj - T / 2.0 - inner0) / 2.0
        estantes = [zs]
    elif puertas == 1:
        # una sola puerta vitrina, bisagras en el lateral derecho de quien mira (u0)
        pu = pc("Puerta", ua, ub, D, D + T, wa, wb, mV, U, VERDE, rol="PUERTA", cantos=cant)
        puerta_vitrina(P, pu, "IZQ", ld, "DER", "A", cols=cols)
        estantes = [inner0 + (inner1 - inner0) * (i + 1) / 3.0 for i in range(2)]
    else:
        um = (ua + ub) / 2.0
        pdr = pc("Puerta der", ua, um - JUNTA / 2, D, D + T, wa, wb, mV, U, VERDE, rol="PUERTA", cantos=cant)
        piz = pc("Puerta izq", um + JUNTA / 2, ub, D, D + T, wa, wb, mV, U, VERDE, rol="PUERTA", cantos=cant)
        puerta_vitrina(P, pdr, "IZQ", ld, "DER", "A", cols=cols)
        puerta_vitrina(P, piz, "DER", li, "IZQ", "A", cols=cols)
        estantes = [inner0 + (inner1 - inner0) * (i + 1) / 3.0 for i in range(2)]
    # estantes regulables
    for i, zs in enumerate(estantes):
        es = pc("Estante %d" % (i + 1), u0 + T + 1, u1 - T - 1, d + 3.5, D - 20, zs, zs + T, "+Z", U, BLANCO,
                cantos=(V,))
        P.append(es)
        yl = zs - inner0 - 8.0
        for (lat, xs) in ((ld, (68.0, ld.W - 37.0)), (li, (li.W - 68.0, 37.0))):
            pines(lat, "A", xs, [yl])
            for x in xs:
                herraje(nombre, "Soporte estante O5", lat.mundo(x, yl, 0.0), lat.vec(0, 0, -1), (0, 0, 1), "pin")
    return P


def panel_terminal(nombre, caja_, A, X):
    P = mueble(nombre)
    p = placa_caja(nombre, "Panel terminal", *caja_, A, X, VERDE, rol="PUERTA",
                   cantos=("+X", "-X", "+Y", "-Y", "+Z", "-Z"))
    P.append(p)
    return P


def zocalos():
    P = mueble("Z Zocalos")
    # pared larga: frente del zocalo a 40 del frente del cuerpo
    yf = F_BAJO - 40.0
    x_ini = 765.0
    z = placa_caja("Z Zocalos", "Zocalo largo", x_ini, X_FIN - T, yf - T, yf, 0.5, 99.5, "+Y", "-X", VERDE,
                   rol="PUERTA", cantos=("-Z",))
    P.append(z)
    # diagonal del esquinero bajo, retirada 40
    PA, PB = (782.0, F_BAJO, 0.0), (F_BAJO, 782.0, 0.0)
    t, n = diagonal(PA, PB)
    k = (PA[0] + PA[1]) - 40.0 * S2          # linea del frente del zocalo: x + y = k
    a = (k - yf, yf, 0.0)                    # encuentro con el zocalo largo
    b = (k - 800.0, 800.0, 0.0)              # termina contra la cocina (Y = 800)
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    ex = mul(t, -1)
    O = add(b, mul(n, -T))                   # cara A = la de atras, 18 detras del frente
    O = (O[0], O[1], 0.5)
    zd = Placa("Z Zocalos", "Zocalo diagonal", L, 99.0, T, O, ex, (0, 0, 1), VERDE, rol="PUERTA",
               cantos=((0, 0, -1),))
    P.append(zd)
    AVISOS.append("Zocalos: las puntas se ajustan en obra (encuentro a 45 entre el largo y el diagonal).")
    return P


# ================================================================ armado ==
def armar():
    bajo_esquinero()
    bajo_normal("B2 Bajo pileta 600", 800.0, 600.0, "pileta")
    bajo_normal("B3 Cajonera 320", 1400.0, 320.0, "cajonera")
    bajo_normal("B4 Bajo puerta 452", 1720.0, X_FIN - T - 1720.0, "puerta")        # donde iba el lavavajillas
    panel_terminal("P1 Panel terminal", (X_FIN - T, X_FIN, 0.0, F_BAJO + T, 0.0, Z_BAJO + H_BAJO), "+X", "+Y")
    panel_terminal("P2 Panel cocina", (0.0, F_BAJO + T, Y_FIN - T, Y_FIN, 0.0, Z_BAJO + H_BAJO), "+Y", "-X")
    alacena_esquinero()
    alacena("A2 Alacena 600 rebatible", 800.0, 600.0, "X", tipo="rebatible")
    alacena("A3 Vitrina 800", 1400.0, 800.0, "X", cols=2)
    alacena("A4 Vitrina 570", 800.0, 570.0, "Y", cols=2, puertas=1)   # una puerta de 567 (con 2 los travesanos quedan < 250)
    zocalos()


# cuerpos de referencia (no se fabrican): mesada, cocina, bacha. Sin lavavajillas desde el 18/10.
REFERENCIA = [
    ("Mesada pared larga", (0, X_FIN, 0, 620, 860, 900)),
    ("Mesada pared corta", (0, 620, 620, 800, 860, 900)),
    ("Cocina 550x650", (0, 650, 800, 1350, 0, 900)),
    ("Bacha (hueco)", (850, 1350, 110, 510, 660, 861)),
]
REF_RGB = {"Mesada": (214, 220, 222), "Cocina": (190, 180, 176), "Bacha": (200, 185, 180)}


def ean13(doce):
    s = sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(doce))
    return doce + str((10 - s % 10) % 10)


def chequeos():
    """Controles de coherencia que no dependen de Fusion."""
    malos = []
    for nombre, placas in MUEBLES:
        for p in placas:
            for h in p.agujeros:
                if not (0 <= h["x"] <= p.W and 0 <= h["y"] <= p.H) or not p.dentro(h["x"], h["y"], tol=0.01):
                    malos.append("%s / %s: agujero O%g fuera de la placa en (%.1f, %.1f)"
                                 % (nombre, p.nombre, h["d"], h["x"], h["y"]))
                if h["prof"] >= p.T and h["sym"] != "handle":
                    malos.append("%s / %s: agujero O%g pasante" % (nombre, p.nombre, h["d"]))
                if h["prof"] > p.T:
                    malos.append("%s / %s: agujero O%g mas profundo que la placa" % (nombre, p.nombre, h["d"]))
            # agujeros que caen en una ventana o en el rebaje de la vitrina
            for h in p.agujeros:
                for v in p.ventanas:
                    if v["x1"] - h["d"] / 2 < h["x"] < v["x2"] + h["d"] / 2 and v["y1"] - h["d"] / 2 < h["y"] < v["y2"] + h["d"] / 2:
                        malos.append("%s / %s: O%g (%s) cae en una ventana" % (nombre, p.nombre, h["d"], h["sym"]))
                for r in p.rebajes:
                    if r["cara"] == h["cara"] and \
                            r["x1"] - h["d"] / 2 < h["x"] < r["x2"] + h["d"] / 2 and r["y1"] - h["d"] / 2 < h["y"] < r["y2"] + h["d"] / 2:
                        malos.append("%s / %s: O%g (%s) cae en el rebaje del vidrio" % (nombre, p.nombre, h["d"], h["sym"]))
            for s in p.ranuras:
                if s["cara"] == "B" and s["ancho"] < 10:
                    malos.append("%s / %s: ranura de %g en cara B (minimo 10)" % (nombre, p.nombre, s["ancho"]))
            # agujeros de caras opuestas que se cruzan
            for a in p.agujeros:
                for b in p.agujeros:
                    if a is b or a["cara"] == b["cara"]:
                        continue
                    if math.hypot(a["x"] - b["x"], a["y"] - b["y"]) < (a["d"] + b["d"]) / 2.0 and \
                            a["prof"] + b["prof"] > p.T - 1.0:
                        malos.append("%s / %s: O%g (cara %s) y O%g (cara %s) se cruzan en (%.0f, %.0f)"
                                     % (nombre, p.nombre, a["d"], a["cara"], b["d"], b["cara"], a["x"], a["y"]))
            # agujero de cara que se mete en un agujero de canto (salvo la excentrica de su perno)
            for c in p.canto:
                dx, dy = DIRECCION[c["canto"]]
                for h in p.agujeros:
                    # distancia del centro del agujero al eje del de canto
                    ux, uy = h["x"] - c["x"], h["y"] - c["y"]
                    a_lo_largo = ux * dx + uy * dy
                    perp = abs(ux * dy - uy * dx)
                    if not (-h["d"] / 2 < a_lo_largo < c["prof"] + h["d"] / 2):
                        continue
                    if perp >= (h["d"] + c["d"]) / 2.0:
                        continue
                    z0, z1 = (-h["prof"], 0.0) if h["cara"] == "A" else (-p.T, -p.T + h["prof"])
                    zc = -c["z"]
                    if z1 < zc - c["d"] / 2 or z0 > zc + c["d"] / 2:
                        continue
                    if h["sym"] == "3in1" and abs(h["d"] - CAM["d"]) < 0.1 and perp < 0.5 and \
                            abs(a_lo_largo - CAM["desde_canto"]) < 0.5:
                        continue
                    malos.append("%s / %s: O%g (%s, cara %s) en (%.1f, %.1f) choca con el O%g del canto %s"
                                 % (nombre, p.nombre, h["d"], h["sym"], h["cara"], h["x"], h["y"], c["d"],
                                    c["canto"]))
            # agujeros de la misma cara que se pisan
            for i, a1 in enumerate(p.agujeros):
                for a2 in p.agujeros[i + 1:]:
                    if a1["cara"] == a2["cara"] and \
                            math.hypot(a1["x"] - a2["x"], a1["y"] - a2["y"]) < (a1["d"] + a2["d"]) / 2.0 + 1.0:
                        malos.append("%s / %s: O%g (%s) y O%g (%s) se pisan en (%.0f, %.0f)"
                                     % (nombre, p.nombre, a1["d"], a1["sym"], a2["d"], a2["sym"], a1["x"], a1["y"]))
            # agujero que cae en una ranura de la misma cara
            for h in p.agujeros:
                for r in p.ranuras:
                    x1, x2 = sorted((r["x1"], r["x2"])); y1, y2 = sorted((r["y1"], r["y2"]))
                    w = r["ancho"] / 2.0 + h["d"] / 2.0
                    if x1 - w < h["x"] < x2 + w and y1 - w < h["y"] < y2 + w:
                        if abs(x2 - x1) < 1e-6 and abs(h["x"] - x1) >= w: continue
                        if abs(y2 - y1) < 1e-6 and abs(h["y"] - y1) >= w: continue
                        zh = (-h["prof"], 0.0) if h["cara"] == "A" else (-p.T, -p.T + h["prof"])
                        zr = (-r["prof"], 0.0) if r["cara"] == "A" else (-p.T, -p.T + r["prof"])
                        if zh[1] > zr[0] and zr[1] > zh[0]:
                            malos.append("%s / %s: O%g (%s) cae en la ranura %s"
                                         % (nombre, p.nombre, h["d"], h["sym"], r["sym"]))
            # limites de la SKH-612H (manual): 250-5000 x 50-1200, 10-48 de espesor
            if p.rol != "FONDO" and (p.agujeros or p.canto or p.ranuras):
                lado_l, lado_c = max(p.W, p.H), min(p.W, p.H)
                if lado_l < 250 or lado_c < 50 or lado_c > 1200:
                    malos.append("%s / %s: %g x %g fuera del rango de la perforadora (250-5000 x 50-1200)"
                                 % (nombre, p.nombre, p.W, p.H))
    return malos


def a_json():
    n = 0
    piezas_modelo, piezas_exp = [], []
    for nombre, placas in MUEBLES:
        for p in placas:
            n += 1
            p.codigo = ean13("%s%03d" % (PREFIJO_CODIGO, n))
            p.nombre_largo = "%s_%s_%s" % (AMBIENTE, nombre, p.nombre)
            cantos = dict(p.cantos)
            piezas_modelo.append(dict(
                mueble=nombre, nombre=p.nombre_largo, pieza=p.nombre, codigo=p.codigo, rol=p.rol,
                W=round(p.W, 3), H=round(p.H, 3), T=p.T, O=[round(c, 4) for c in p.O],
                ex=[round(c, 7) for c in p.ex], ey=[round(c, 7) for c in p.ey],
                contorno=[[round(x, 3), round(y, 3)] for (x, y) in p.contorno] if p.contorno else None,
                material=p.material, textura=p.textura, veta=p.veta, cantos=cantos,
                agujeros=p.agujeros, agujeros_canto=p.canto, ranuras=p.ranuras,
                ventanas=p.ventanas, rebajes=p.rebajes))
            piezas_exp.append({
                "codigo": p.codigo, "nombre": p.nombre_largo, "ancho": round(p.W, 2), "alto": round(p.H, 2),
                "espesor": p.T, "material": p.material, "mueble": nombre, "textura": p.textura,
                "veta": p.veta, "cantidad": 1,
                "canto_abajo": cantos["ABAJO"], "canto_arriba": cantos["ARRIBA"],
                "canto_izq": cantos["IZQ"], "canto_der": cantos["DER"],
                "agujeros": [dict(x=h["x"], y=h["y"], diametro=h["d"], profundidad=h["prof"], cara=h["cara"])
                             for h in p.agujeros],
                "agujeros_canto": [dict(x=h["x"], y=h["y"], z=h["z"], diametro=h["d"], profundidad=h["prof"],
                                        canto=LETRA[h["canto"]]) for h in p.canto],
                "ranuras": [dict(x1=s["x1"], y1=s["y1"], x2=s["x2"], y2=s["y2"], ancho=s["ancho"],
                                 profundidad=s["prof"], cara=s["cara"]) for s in p.ranuras],
                "ranuras_canto": [],
                "contorno": [dict(x=round(x, 2), y=round(y, 2), arco=0.0) for (x, y) in p.contorno]
                if p.contorno else None,
                # ROUTER (no lo lee ExportarPiezas ni etapa2 todavia): ventanas pasantes y cajeados
                "ventanas": p.ventanas, "rebajes": p.rebajes,
            })
    cab = dict(version=1, origen="receta", documento=AMBIENTE, orden=ORDEN, cliente=CLIENTE,
               direccion="", ambiente=AMBIENTE)
    ref = [(nm, caja, REF_RGB[nm.split()[0]]) for nm, caja in REFERENCIA]
    return (dict(cab, piezas=piezas_modelo, herrajes=HERRAJES, avisos=AVISOS, referencia=ref),
            dict(cab, piezas=piezas_exp))


def main():
    armar()
    malos = chequeos()
    for nombre, placas in MUEBLES:
        for p in placas:
            if p.contorno:
                AVISOS.append("%s / %s: contorno con chanfle a 45 — la sierra corta el rectangulo %g x %g, "
                              "el chanfle se hace a mano y el canto del lado diagonal se pega despues "
                              "(no figura en la lista de corte)." % (nombre, p.nombre, p.W, p.H))
    for nombre, placas in MUEBLES:
        for p in placas:
            if p.ventanas:
                v = p.vitrina
                AVISOS.append("%s / %s: VITRINA %dx%d — las %d ventanas y el rebaje del vidrio (%g prof.) los hace "
                              "el ROUTER; el .nc no se genera todavia (estan en modelo.json). Vidrio de %g: "
                              "%.0f x %.0f." % (nombre, p.nombre, v["cols"], v["filas"], len(p.ventanas),
                                                VIT["rebaje_prof"], VIT["vidrio"], v["vidrio"][0], v["vidrio"][1]))
    AVISOS.append("Alacenas sin cenefa ni cornisa (18/10): la tira LED va EMBUTIDA en la ranura 10x10 del piso "
                  "con perfil de aluminio y difusor a ras.")
    if any(h["sym"] == "handle" for _, pl in MUEBLES for p in pl for h in p.agujeros):
        AVISOS.append("Tiradores: agujeros O5 PASANTES desde la cara A (interior). Si el frente astilla a la "
                      "salida, perforarlos desde la cara B.")
    modelo, exp = a_json()
    os.makedirs(SALIDA, exist_ok=True)
    with open(os.path.join(SALIDA, "modelo.json"), "w", encoding="utf-8") as fh:
        json.dump(modelo, fh, ensure_ascii=False, indent=1)
    with open(os.path.join(SALIDA, "piezas_receta.json"), "w", encoding="utf-8") as fh:
        json.dump(exp, fh, ensure_ascii=False, indent=1)
    from collections import Counter
    cuenta = Counter(h["nombre"].split(" base")[0] if h["nombre"].startswith("Bisagra") else
                     (h["nombre"] if not h["nombre"].startswith(("Tira LED", "Vidrio")) else h["nombre"].split()[0])
                     for h in HERRAJES)
    lin = ["COCINA-01 — receta", ""]
    for nombre, placas in MUEBLES:
        lin.append("%-26s %3d placas" % (nombre, len(placas)))
        for p in placas:
            lin.append("    %-13s %-26s %7.1f x %7.1f x %4.1f  %-9s  ag %3d  canto %2d  ran %d%s"
                       % (p.codigo, p.nombre, p.W, p.H, p.T, p.textura, len(p.agujeros), len(p.canto),
                          len(p.ranuras), ("  (contorno)" if p.contorno else "") +
                          ("  (vitrina %d ventanas)" % len(p.ventanas) if p.ventanas else "")))
    lin.append("")
    lin.append("TOTAL %d placas" % sum(len(pl) for _, pl in MUEBLES))
    lin.append("HERRAJES:")
    for k, v in sorted(cuenta.items()):
        lin.append("    %-28s %4d" % (k, v))
    lin.append("")
    lin += ["AVISO: " + a for a in AVISOS]
    lin += ["ERROR: " + m for m in malos]
    with open(os.path.join(SALIDA, "resumen.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lin) + "\n")
    print("\n".join(lin))
    return 1 if malos else 0


if __name__ == "__main__":
    sys.exit(main())
