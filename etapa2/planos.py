# -*- coding: utf-8 -*-
"""
planos — planos de fabricacion en PDF (A4 apaisado) desde el render.json de GuiGui.

    python3 planos.py <render.json> -o planos.pdf [--mueble N] [--orden 260625-20] [--guardado 15/10/2026]

Laminas:
  1   Vistas generales acotadas: frente, frente sin puertas, corte lateral (sin el lateral
      izquierdo) y planta sin techo.
  2   Explotada con globos + lista de piezas (el globo es el mismo de maestra.json / etiqueta).
  3   Lista de corte, herrajes y notas: lo que GuiGui trae distinto de lo vigente en CONTEXTO.md.
  4+  Una lamina por pieza: cara A y cara B acotadas (cotas acumuladas desde la esquina de
      origen del marco h/v de GuiGui), agujeros de canto, ranuras, cantos, veta y tabla de
      mecanizados numerada.

Mundo (el de ArmarDesdeRender): X a la derecha, Y hacia atras (el frente esta en -Y), Z arriba.
Marco de cada pieza: h = ex, v = ey (como GuiGui). Cara A = side 1 (normal -ez), cara B = side -1.
El numero de globo, el orden de la lista de corte y la lamina de cada pieza son el mismo
(sale de paquete.maestra).
"""
from __future__ import annotations

import argparse
import datetime
import math
import os
import re
import sys
from collections import Counter

from reportlab.lib.colors import Color, black, white
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import paquete  # noqa: E402

PW, PH = landscape(A4)
M = 26.0                      # margen
PIE = 34.0                    # alto del rotulo de abajo
GRIS = Color(0.45, 0.45, 0.45)
GRIS_CLARO = Color(0.80, 0.80, 0.80)
AZUL = Color(0.10, 0.30, 0.70)
ROJO = Color(0.75, 0.10, 0.10)
VERDE = Color(0.05, 0.50, 0.25)
NARANJA = Color(0.85, 0.45, 0.05)

TEXTURAS = [(u"玛雅灰", "Gris Maya (13)"), (u"拉丝胡桃", "Nogal cepillado (04)"),
            (u"白麻面", "Blanco lino (d02)"), (u"暖白", "Blanco calido (01)")]
MATERIALES = {"STRUCTURE": "Estructura 18", "PETFRONT": "PET frente 18", "BACKGROUND": "Fondo 5",
              "NEstructura": "Estructura (N) 18", u"多层实木": "Multilaminado 18"}
COLORES = [("胡桃", (0.56, 0.43, 0.33)), ("nogal", (0.56, 0.43, 0.33)), ("玛雅灰", (0.72, 0.72, 0.73)),
           ("gris", (0.72, 0.72, 0.73)), ("白麻", (0.92, 0.91, 0.87)), ("blanco", (0.93, 0.93, 0.90))]


# ------------------------------------------------------------------ utilidades
def _n(v):
    v = float(v)
    return str(int(round(v))) if abs(v - round(v)) < 0.005 else ("%.2f" % v).rstrip("0").rstrip(".")


def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def sub(a, b): return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
def add(a, b): return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]
def mul(a, k): return [a[0] * k, a[1] * k, a[2] * k]
def cross(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def norm(a):
    n = math.sqrt(dot(a, a)) or 1.0
    return [a[0] / n, a[1] / n, a[2] / n]


def tex_es(s):
    s = s or ""
    for k, v in TEXTURAS:
        if k in s:
            return v
    t = re.sub(r"[^\x20-\x7e]+", "", s).strip()
    return t or s


def mat_es(s):
    return MATERIALES.get(s or "", re.sub(r"[^\x20-\x7e]+", "", s or "").strip() or (s or ""))


def color_de(p):
    t = (p.textura or "") + " " + (p.material or "")
    for k, rgb in COLORES:
        if k.lower() in t.lower():
            return Color(*rgb)
    if p.rol == "FONDO":
        return Color(0.92, 0.91, 0.87)
    return Color(0.78, 0.78, 0.78)


def dir_es(v):
    """Nombre en el mueble de una direccion del mundo."""
    ax = [abs(c) for c in v]
    i = ax.index(max(ax))
    s = v[i] > 0
    return {0: ("derecha", "izquierda"), 1: ("atras (pared)", "frente"), 2: ("arriba", "abajo")}[i][0 if s else 1]


# ------------------------------------------------------------------ piezas
class Pz(object):
    pass


def cargar(ruta, idx=0):
    ADR = paquete._cargar_adr()
    muebles, d = ADR.leer_render(ruta, None, None)
    mu_adr = [m for m in muebles if m["indice"] == idx][0]
    m = paquete.maestra(ruta, [idx])
    mu = m["muebles"][0]
    por_codigo = {pz.codigo: pz for pz in mu_adr["piezas"]}
    piezas = []
    for row in mu["piezas"]:
        a = por_codigo[row["codigo"]]
        p = Pz()
        p.num = row["globo"]
        p.nombre = row["nombre"]
        p.nombre_guigui = row["nombre_guigui"]
        p.tipo = row["tipo"]
        p.codigo = row["codigo"]
        p.W, p.H, p.T = float(a.W), float(a.H), float(a.T)
        p.corte_W, p.corte_H = row["corte_W"], row["corte_H"]
        p.spec = a.spec
        p.aviso = row["aviso"]
        p.origen, p.ex, p.ey, p.ez = list(a.origen), list(a.ex), list(a.ey), list(a.ez)
        p.bmin, p.bmax = paquete._caja_mundo(ADR, a)
        p.holes, p.sholes, p.slots, p.sslots = a.holes, a.sholes, a.slots, a.sslots
        p.cantos = {k: float(v) for k, v in a.cantos.items()}
        p.material, p.textura = a.material, a.textura
        p.veta = row["veta"]
        p.rol = row["rol"]
        p.es_puerta = a.es_puerta
        piezas.append(p)
    # nombres mas fieles a una alacena colgada: los "zocalos" son listones, el estante de
    # abajo es el piso
    zmin = min(p.bmin[2] for p in piezas)
    for p in piezas:
        if p.tipo == u"Zócalo" and zmin > 300:
            p.nombre = p.nombre.replace(u"Zócalo", u"Listón"); p.tipo = u"Listón"
    horiz = [p for p in piezas if p.tipo == "Estante"]
    if horiz:
        piso = min(horiz, key=lambda p: p.bmin[2])
        if abs(piso.bmin[2] - min(q.bmin[2] for q in piezas if q.rol == "PLACA" and q.tipo != u"Listón")) < 1.0 \
                or piso.bmin[2] - zmin < 150:
            piso.nombre = piso.nombre.replace("Estante", "Piso"); piso.tipo = "Piso"
    info = dict(ambiente=m["ambiente"], orden=m["orden"], mueble=mu["nombre"],
                ancho=mu["ancho"], alto=mu["alto"], prof=mu["prof"], caja=mu["caja"],
                herrajes=mu["herrajes"])
    return piezas, info


def vertices(p, extra=(0, 0, 0)):
    o = add(p.origen, list(extra))
    vs = []
    for a in (0, p.W):
        for b in (0, p.H):
            for c in (0, -p.T):
                vs.append(add(add(add(o, mul(p.ex, a)), mul(p.ey, b)), mul(p.ez, c)))
    return vs


CARAS = [(0, 2, 6, 4), (1, 3, 7, 5), (0, 1, 5, 4), (2, 3, 7, 6), (0, 1, 3, 2), (4, 5, 7, 6)]


def centro(p):
    return [(p.bmin[i] + p.bmax[i]) / 2.0 for i in range(3)]


def eje_normal(p):
    n = [abs(x) for x in p.ez]
    return n.index(max(n))


# ------------------------------------------------------------------ cotas
def cota_h(cv, xs, y, vals, arriba=True, fs=6.5):
    """Cadena de cotas horizontal: xs en puntos (ordenados), vals textos por tramo."""
    cv.setLineWidth(0.4); cv.setStrokeColor(black); cv.setFillColor(black)
    cv.line(xs[0], y, xs[-1], y)
    for x in xs:
        cv.line(x, y - 2.5, x, y + 2.5)
    cv.setFont("Helvetica", fs)
    nivel = 0
    for i in range(len(xs) - 1):
        t = vals[i]
        tw = cv.stringWidth(t, "Helvetica", fs)
        cx = (xs[i] + xs[i + 1]) / 2.0
        if tw + 2 > xs[i + 1] - xs[i]:
            nivel = (nivel + 1) % 3
            dy = 2 + nivel * (fs + 1)
        else:
            nivel = 0
            dy = 2
        cv.drawCentredString(cx, y + dy if arriba else y - dy - fs + 1, t)


def cota_v(cv, ys, x, vals, izq=True, fs=6.5):
    cv.setLineWidth(0.4); cv.setStrokeColor(black); cv.setFillColor(black)
    cv.line(x, ys[0], x, ys[-1])
    for y in ys:
        cv.line(x - 2.5, y, x + 2.5, y)
    cv.setFont("Helvetica", fs)
    nivel = 0
    for i in range(len(ys) - 1):
        t = vals[i]
        cy = (ys[i] + ys[i + 1]) / 2.0
        if fs + 1 > ys[i + 1] - ys[i]:
            nivel = (nivel + 1) % 3
        else:
            nivel = 0
        tw = cv.stringWidth(t, "Helvetica", fs)
        dx = 3 + nivel * (tw + 3)
        if izq:
            cv.drawRightString(x - dx, cy - fs / 2 + 1, t)
        else:
            cv.drawString(x + dx, cy - fs / 2 + 1, t)


def _breaks(vals, tol=0.6):
    out = []
    for v in sorted(vals):
        if not out or v - out[-1] > tol:
            out.append(v)
    return out


# ------------------------------------------------------------------ vistas ortogonales
def vista(cv, piezas, x0, y0, w, h, proy, titulo, excluir=lambda p: False, swing=False,
          cotas_de=None, subtitulo=""):
    """proy(p3) -> (u, v, prof). Dibuja las piezas como cajas, con cadenas de cotas.
    cotas_de: filtro de las piezas cuyas aristas entran en las cadenas de cotas (default: todas)."""
    items = []
    for p in piezas:
        if excluir(p):
            continue
        pts = [proy(v) for v in vertices(p)]
        us = [q[0] for q in pts]; vs = [q[1] for q in pts]; ds = [q[2] for q in pts]
        items.append((p, min(us), max(us), min(vs), max(vs), sum(ds) / 8.0))
    if not items:
        return
    umin = min(i[1] for i in items); umax = max(i[2] for i in items)
    vmin = min(i[3] for i in items); vmax = max(i[4] for i in items)
    ML, MB, MT, MR = 44.0, 34.0, 46.0, 36.0          # lugar para cotas
    sc = min((w - ML - MR) / (umax - umin), (h - MB - MT) / (vmax - vmin))
    ox = x0 + ML
    oy = y0 + MB
    X = lambda u: ox + (u - umin) * sc
    Y = lambda v: oy + (v - vmin) * sc
    top = Y(vmax); right = X(umax)
    cv.setFont("Helvetica-Bold", 8.5); cv.setFillColor(black)
    cv.drawString(x0, y0 + h - 9, titulo)
    if subtitulo:
        cv.setFont("Helvetica", 6.5); cv.setFillColor(GRIS); cv.drawString(x0, y0 + h - 18, subtitulo)
    cv.setLineWidth(0.5)
    for p, a, b, c, d, prof in sorted(items, key=lambda i: i[5]):
        cv.setFillColor(color_de(p)); cv.setStrokeColor(Color(0.2, 0.2, 0.2))
        cv.rect(X(a), Y(c), (b - a) * sc, (d - c) * sc, fill=1, stroke=1)
        if swing and p.es_puerta:
            _swing(cv, p, X(a), Y(c), (b - a) * sc, (d - c) * sc)
    # cotas: cadenas abajo y a la izquierda, totales arriba y a la derecha
    sel = [i for i in items if (cotas_de is None or cotas_de(i[0]))] or items
    bu = _breaks([i[1] for i in sel] + [i[2] for i in sel])
    bv = _breaks([i[3] for i in sel] + [i[4] for i in sel])
    cv.setStrokeColor(GRIS_CLARO); cv.setLineWidth(0.3)
    for u in bu:
        cv.line(X(u), oy - 2, X(u), oy - 14)
    for v in bv:
        cv.line(ox - 2, Y(v), ox - 14, Y(v))
    cota_h(cv, [X(u) for u in bu], oy - 14, [_n(bu[i + 1] - bu[i]) for i in range(len(bu) - 1)], arriba=False)
    cv.setStrokeColor(GRIS_CLARO); cv.setLineWidth(0.3)
    cv.line(X(umin), top + 2, X(umin), top + 12); cv.line(X(umax), top + 2, X(umax), top + 12)
    cota_h(cv, [X(umin), X(umax)], top + 12, [_n(umax - umin)], arriba=True, fs=7.5)
    cota_v(cv, [Y(v) for v in bv], ox - 14, [_n(bv[i + 1] - bv[i]) for i in range(len(bv) - 1)], izq=True)
    cv.setStrokeColor(GRIS_CLARO); cv.setLineWidth(0.3)
    cv.line(right + 2, Y(vmin), right + 12, Y(vmin)); cv.line(right + 2, Y(vmax), right + 12, Y(vmax))
    cota_v(cv, [Y(vmin), Y(vmax)], right + 12, [_n(vmax - vmin)], izq=False, fs=7.5)


def lado_bisagra(p):
    cups = [h for h in p.holes if h["sym"] == "HINGE"]
    if not cups:
        return None
    xs = [h["x"] for h in cups]; ys = [h["y"] for h in cups]
    if max(xs) < p.W * 0.3:
        return "h0"
    if min(xs) > p.W * 0.7:
        return "hW"
    if min(ys) > p.H * 0.7:
        return "vH"
    if max(ys) < p.H * 0.3:
        return "v0"
    return None


def _swing(cv, p, x, y, w, h):
    """Simbolo de apertura: dos lineas desde el canto de bisagra al medio del canto opuesto."""
    lado = lado_bisagra(p)
    if not lado:
        return
    # el frente de la puerta mira a -Y; en la vista de frente h=ex va a +X (derecha) y v a +Z
    sx = 1 if p.ex[0] >= 0 else -1
    if lado in ("h0", "hW"):
        izq = (lado == "h0") == (sx > 0)
        a, b = ((x, y), (x, y + h)) if izq else ((x + w, y), (x + w, y + h))
        c = (x + w, y + h / 2) if izq else (x, y + h / 2)
    else:
        arriba = (lado == "vH")
        a, b = ((x, y + h), (x + w, y + h)) if arriba else ((x, y), (x + w, y))
        c = (x + w / 2, y) if arriba else (x + w / 2, y + h)
    cv.setStrokeColor(Color(0.15, 0.15, 0.15)); cv.setLineWidth(0.4); cv.setDash(3, 2)
    cv.line(a[0], a[1], c[0], c[1]); cv.line(b[0], b[1], c[0], c[1])
    cv.setDash()


# ------------------------------------------------------------------ isometrica / explotada
U_ISO = [0.866, 0.866, 0.0]
W_ISO = [-0.5, 0.5, 1.0]
V_ISO = norm(cross(U_ISO, W_ISO))            # hacia el observador: +x, -y, +z
SOMBRA = {0: 0.86, 1: 1.0, 2: 0.72}          # normal X / Y / Z


def _tono(c, k):
    return Color(min(1, c.red * k), min(1, c.green * k), min(1, c.blue * k))


def proy_iso(p3):
    return dot(p3, U_ISO), dot(p3, W_ISO), dot(p3, V_ISO)


def explotar(piezas):
    lo = [min(p.bmin[i] for p in piezas) for i in range(3)]
    hi = [max(p.bmax[i] for p in piezas) for i in range(3)]
    cen = [(lo[i] + hi[i]) / 2 for i in range(3)]
    tam = max(hi[i] - lo[i] for i in range(3))
    for p in piezas:
        e = eje_normal(p); c = centro(p)
        v = [0.0, 0.0, 0.0]
        if p.rol == "PUERTA":
            v[1] = -0.95 * tam
            v[2] = 0.08 * tam * (1 if c[2] > cen[2] else -1)
        elif p.rol == "FONDO":
            v[1] = 0.55 * tam
        elif e == 1:                          # listones / travesanos: bien abajo, y hacia su lado
            lado = c[e] - cen[e]
            v[2] = -0.85 * tam
            v[1] = math.copysign(0.15 * tam, lado) if abs(lado) > 0.15 * (hi[e] - lo[e]) else 0.0
        elif e == 0:                          # laterales: a los costados
            lado = c[e] - cen[e]
            if abs(lado) > 0.15 * (hi[e] - lo[e]):
                v[e] = math.copysign(0.55 * tam, lado)
        else:                                 # horizontales: proporcional a su altura en el mueble
            v[2] = 0.9 * (c[2] - cen[2])
        p.desplazo = v
    return cen


def dibujar_iso(cv, piezas, x0, y0, w, h, globos=True):
    polys = []
    for p in piezas:
        vs = vertices(p, p.desplazo)
        cpz = [sum(v[k] for v in vs) / 8.0 for k in range(3)]
        pr = [proy_iso(v) for v in vs]
        col = color_de(p)
        for cara in CARAS:
            a, b, c = vs[cara[0]], vs[cara[1]], vs[cara[2]]
            n = norm(cross(sub(b, a), sub(c, a)))
            cen = [sum(vs[i][k] for i in cara) / 4.0 for k in range(3)]
            if dot(n, sub(cen, cpz)) < 0:
                n = mul(n, -1)
            if dot(n, V_ISO) <= 1e-6:
                continue
            eje = [abs(x) for x in n]
            polys.append((dot(cen, V_ISO), [(pr[i][0], pr[i][1]) for i in cara], _tono(col, SOMBRA[eje.index(max(eje))])))
    xs = [q[0] for _, ps, _ in polys for q in ps]; ys = [q[1] for _, ps, _ in polys for q in ps]
    mnx, mxx, mny, mxy = min(xs), max(xs), min(ys), max(ys)
    # globos (en unidades del dibujo): afuera de la caja proyectada de cada pieza, en la
    # direccion que va del centro del conjunto al centro de la pieza
    glob = []
    if globos:
        cx, cy = (mnx + mxx) / 2, (mny + mxy) / 2
        esc0 = min(w / ((mxx - mnx) or 1), h / ((mxy - mny) or 1))
        for p in piezas:
            pr = [proy_iso(v) for v in vertices(p, p.desplazo)]
            pu = [q[0] for q in pr]; pv = [q[1] for q in pr]
            cu, cvv = (min(pu) + max(pu)) / 2, (min(pv) + max(pv)) / 2
            dx, dy = cu - cx, cvv - cy
            L = math.hypot(dx, dy) or 1.0
            dx, dy = dx / L, dy / L
            # salir de la caja de la pieza a lo largo de (dx, dy)
            t = min((((max(pu) if dx > 0 else min(pu)) - cu) / dx) if abs(dx) > 1e-6 else 1e9,
                    (((max(pv) if dy > 0 else min(pv)) - cvv) / dy) if abs(dy) > 1e-6 else 1e9)
            t = min(t, 0.6 * max(max(pu) - min(pu), max(pv) - min(pv)))
            g = (cu + dx * (t + 22 / esc0), cvv + dy * (t + 22 / esc0))
            glob.append((p.num, g, (cu, cvv)))
        xs += [g[1][0] for g in glob]; ys += [g[1][1] for g in glob]
        mnx, mxx, mny, mxy = min(xs), max(xs), min(ys), max(ys)
    pad = 12 if globos else 4
    sc = min((w - 2 * pad) / ((mxx - mnx) or 1), (h - 2 * pad) / ((mxy - mny) or 1))
    ox = x0 + (w - (mxx - mnx) * sc) / 2 - mnx * sc
    oy = y0 + (h - (mxy - mny) * sc) / 2 - mny * sc
    T = lambda q: (ox + q[0] * sc, oy + q[1] * sc)
    cv.setLineWidth(0.5)
    for _, ps, col in sorted(polys, key=lambda t: t[0]):
        cv.setFillColor(col); cv.setStrokeColor(Color(0.25, 0.25, 0.25))
        path = cv.beginPath(); q = T(ps[0]); path.moveTo(*q)
        for pt in ps[1:]:
            path.lineTo(*T(pt))
        path.close(); cv.drawPath(path, fill=1, stroke=1)
    for num, g, a in glob:
        gx, gy = T(g); ax, ay = T(a)
        cv.setStrokeColor(black); cv.setLineWidth(0.5); cv.line(ax, ay, gx, gy)
        cv.setFillColor(white); cv.circle(gx, gy, 7.5, fill=1, stroke=1)
        cv.setFillColor(black); cv.setFont("Helvetica-Bold", 8)
        cv.drawCentredString(gx, gy - 2.8, str(num))


# ------------------------------------------------------------------ mecanizados de una pieza
def tipo_agujero(h, canto=False):
    s, d = h["sym"], h["d"]
    if canto:
        return "Perno 3 en 1 (canto)" if s == "3in1Lock" else ("Agujero de canto " + s)
    if s == "3in1Lock":
        return u"Excéntrica 3 en 1" if abs(d - 15) < 0.6 else "Receptor del perno"
    if s == "HINGE":
        return "Cazoleta bisagra"
    if s == "HINGESCREW":
        return "Tornillo bisagra (puerta)"
    if s == "jlHoleEX":
        return "Placa base bisagra"
    if s == "slideRail":
        return "Corredera"
    return s or "Agujero"


def tipo_ranura(s):
    return {"BP": "Ranura fondo", "lightSlot": "Ranura tira LED"}.get(s["sym"], "Ranura " + (s["sym"] or ""))


def operaciones(p):
    """Lista numerada de mecanizados: (n, cara, tipo, x, y, Ø/ancho, prof, obj, clase)."""
    ops = []
    orden_cara = {1: 0, -1: 1}
    hs = sorted(p.holes, key=lambda h: (orden_cara.get(h["side"], 2), -h["d"], h["y"], h["x"]))
    for h in hs:
        ops.append(dict(cara="A" if h["side"] == 1 else "B", tipo=tipo_agujero(h), x=h["x"], y=h["y"],
                        d=h["d"], prof=h["prof"], obj=h, clase="hole"))
    for s in sorted(p.slots, key=lambda s: (orden_cara.get(s["side"], 2), s["x1"])):
        ops.append(dict(cara="A" if s["side"] == 1 else "B", tipo=tipo_ranura(s),
                        x=(s["x1"], s["x2"]), y=(s["y1"], s["y2"]), d=s["w"], prof=s["prof"], obj=s, clase="slot"))
    canto_nombre = {1: "canto izq (x=0)", 2: "canto arriba (y=H)", 3: "canto der (x=W)", 4: "canto abajo (y=0)"}
    for h in sorted(p.sholes, key=lambda h: (h["side"], h["x"], h["y"])):
        ops.append(dict(cara=canto_nombre.get(h["side"], "canto"), tipo=tipo_agujero(h, True),
                        x=h["x"], y=h["y"], d=h["d"], prof=h["prof"], obj=h, clase="shole"))
    for s in p.sslots:
        ops.append(dict(cara=canto_nombre.get(s["side"], "canto"), tipo="Ranura de canto",
                        x=(s["x1"], s["x2"]), y=(s["y1"], s["y2"]), d=s["w"], prof=s["prof"], obj=s, clase="sslot"))
    for i, o in enumerate(ops, 1):
        o["n"] = i
    return ops


def color_op(o):
    t = o["tipo"]
    if "centrica" in t:
        return ROJO
    if "Receptor" in t or "Perno" in t:
        return AZUL
    if "Cazoleta" in t:
        return VERDE
    if "bisagra" in t:
        return NARANJA
    if "Ranura" in t:
        return Color(0.5, 0.3, 0.6)
    return GRIS


def dibujo_cara(cv, p, cara, ops, x0, y0, wmax, hmax):
    """Una cara de la pieza acotada. cara 'B' se dibuja espejada (como se ve dada vuelta)."""
    sc = min((wmax - 48) / p.W, (hmax - 86) / p.H)
    w, h = p.W * sc, p.H * sc
    ox = x0 + 44 + ((wmax - 48) - w) / 2.0
    oy = y0 + 60
    X = (lambda x: ox + x * sc) if cara == "A" else (lambda x: ox + (p.W - x) * sc)
    Y = lambda y: oy + y * sc
    # placa
    cv.setFillColor(Color(0.97, 0.96, 0.93)); cv.setStrokeColor(black); cv.setLineWidth(0.8)
    cv.rect(ox, oy, w, h, fill=1, stroke=1)
    # cantos (gruesos)
    cv.setStrokeColor(Color(0.1, 0.1, 0.1)); cv.setLineWidth(2.6)
    if p.cantos["IZQ"] > 0: cv.line(X(0), oy, X(0), oy + h)
    if p.cantos["DER"] > 0: cv.line(X(p.W), oy, X(p.W), oy + h)
    if p.cantos["ABAJO"] > 0: cv.line(ox, Y(0), ox + w, Y(0))
    if p.cantos["ARRIBA"] > 0: cv.line(ox, Y(p.H), ox + w, Y(p.H))
    # veta
    cv.setStrokeColor(GRIS_CLARO); cv.setLineWidth(0.3)
    if p.veta == "VERTICAL":
        for k in range(1, 6):
            cv.line(ox + w * k / 6.0, oy + 3, ox + w * k / 6.0, oy + h - 3)
    else:
        for k in range(1, 6):
            cv.line(ox + 3, oy + h * k / 6.0, ox + w - 3, oy + h * k / 6.0)
    # ranuras y agujeros de esta cara
    xs_cota, ys_cota = [0.0, p.W], [0.0, p.H]
    for o in ops:
        if o["clase"] == "slot" and o["cara"] == cara:
            s = o["obj"]; hw = s["w"] / 2.0
            x1, x2 = sorted((s["x1"], s["x2"])); y1, y2 = sorted((s["y1"], s["y2"]))
            if abs(x2 - x1) < 1e-6:
                rx, ry, rw, rh = x1 - hw, y1, 2 * hw, y2 - y1
                xs_cota += [x1 - hw, x1 + hw]
            else:
                rx, ry, rw, rh = x1, y1 - hw, x2 - x1, 2 * hw
                ys_cota += [y1 - hw, y1 + hw]
            cv.setFillColor(Color(0.85, 0.78, 0.9)); cv.setStrokeColor(color_op(o)); cv.setLineWidth(0.6)
            xa, xb = sorted((X(rx), X(rx + rw)))
            cv.rect(xa, Y(ry), xb - xa, rh * sc, fill=1, stroke=1)
            cv.setFillColor(color_op(o)); cv.setFont("Helvetica-Bold", 6)
            cv.drawString(xb + 2, Y(ry + rh / 2.0), str(o["n"]))
        if o["clase"] == "hole" and o["cara"] == cara:
            hh = o["obj"]; r = max(hh["d"] / 2.0 * sc, 1.6)
            cv.setStrokeColor(color_op(o)); cv.setLineWidth(0.7)
            cv.setFillColor(white if hh["d"] >= 10 else color_op(o))
            cv.circle(X(hh["x"]), Y(hh["y"]), r, fill=1, stroke=1)
            if hh["d"] >= 10:
                cv.line(X(hh["x"]) - r, Y(hh["y"]), X(hh["x"]) + r, Y(hh["y"]))
                cv.line(X(hh["x"]), Y(hh["y"]) - r, X(hh["x"]), Y(hh["y"]) + r)
            cv.setFillColor(color_op(o)); cv.setFont("Helvetica-Bold", 6)
            cv.drawString(X(hh["x"]) + r + 1.5, Y(hh["y"]) + r * 0.3, str(o["n"]))
            xs_cota.append(hh["x"]); ys_cota.append(hh["y"])
    # agujeros de canto (en las dos caras, espejados en B)
    for o in ops:
        if o["clase"] != "shole":
            continue
        hh = o["obj"]; side = hh["side"]; d = hh["d"] * sc; L = hh["prof"] * sc
        cv.setStrokeColor(AZUL); cv.setLineWidth(0.7); cv.setFillColor(AZUL)
        if side in (1, 3):
            xe = X(0) if side == 1 else X(p.W)
            dirx = 1 if (xe < ox + w / 2) else -1
            y = Y(hh["y"])
            cv.rect(xe - 1.5, y - max(d / 2, 1.5), 3, 2 * max(d / 2, 1.5), fill=1, stroke=0)
            cv.setDash(2, 1.5); cv.line(xe, y, xe + dirx * L, y); cv.setDash()
            cv.setFont("Helvetica-Bold", 6)
            if dirx > 0:
                cv.drawRightString(xe - 3, y - 2, str(o["n"]))
            else:
                cv.drawString(xe + 3, y - 2, str(o["n"]))
            ys_cota.append(hh["y"])
        else:
            ye = Y(0) if side == 4 else Y(p.H)
            diry = 1 if side == 4 else -1
            x = X(hh["x"])
            cv.rect(x - max(d / 2, 1.5), ye - 1.5, 2 * max(d / 2, 1.5), 3, fill=1, stroke=0)
            cv.setDash(2, 1.5); cv.line(x, ye, x, ye + diry * L); cv.setDash()
            cv.setFont("Helvetica-Bold", 6)
            cv.drawCentredString(x, ye - 8 if diry > 0 else ye + 3.5, str(o["n"]))
            xs_cota.append(hh["x"])
    # origen
    cv.setStrokeColor(black); cv.setLineWidth(0.6); cv.setFillColor(white)
    cv.circle(X(0), Y(0), 3.2, fill=1, stroke=1); cv.circle(X(0), Y(0), 1.0, fill=1, stroke=1)
    # cotas acumuladas: abajo (x) y a la izquierda (y)
    xs_u = _breaks(xs_cota, 0.3); ys_u = _breaks(ys_cota, 0.3)
    cv.setFont("Helvetica", 5.5); cv.setFillColor(black)
    ybase = oy - 12
    cv.setStrokeColor(GRIS); cv.setLineWidth(0.3); cv.line(ox, ybase, ox + w, ybase)
    cv.setStrokeColor(GRIS_CLARO)
    for xv in xs_u:
        cv.line(X(xv), oy - 1, X(xv), ybase)
    cv.setStrokeColor(GRIS)
    ult = [-1e9, -1e9, -1e9]
    for xv in sorted(xs_u, key=lambda v: X(v)):
        px = X(xv)
        cv.line(px, ybase - 2, px, ybase + 2)
        nivel = next((k for k in range(3) if px - ult[k] >= 7.0), 2)
        ult[nivel] = px
        cv.saveState(); cv.translate(px + 2.0, ybase - 4 - nivel * 15); cv.rotate(90)
        cv.drawRightString(0, 0, _n(xv)); cv.restoreState()
    xbase = ox - 12
    cv.line(xbase, oy, xbase, oy + h)
    cv.setStrokeColor(GRIS_CLARO)
    for yv in ys_u:
        cv.line(ox - 1, Y(yv), xbase, Y(yv))
    cv.setStrokeColor(GRIS)
    ult = [-1e9, -1e9, -1e9]
    for yv in ys_u:
        py = Y(yv)
        cv.line(xbase - 2, py, xbase + 2, py)
        nivel = next((k for k in range(3) if py - ult[k] >= 7.0), 2)
        ult[nivel] = py
        cv.drawRightString(xbase - 3 - nivel * 17, py - 2, _n(yv))
    # titulo de la cara
    cv.setFont("Helvetica-Bold", 8); cv.setFillColor(black)
    cv.drawString(x0 + 44, y0 + hmax - 8, "Cara %s" % cara + ("  (espejada: pieza dada vuelta)" if cara == "B" else ""))
    cv.setFont("Helvetica", 6.5); cv.setFillColor(GRIS)
    cv.drawString(x0 + 44, y0 + hmax - 17, "%s x %s  ·  cotas en mm desde el origen (esquina marcada)" % (_n(p.W), _n(p.H)))


# ------------------------------------------------------------------ rotulo y texto
def rotulo(cv, info, lamina, total, titulo):
    cv.setStrokeColor(black); cv.setLineWidth(0.8)
    cv.rect(M, M, PW - 2 * M, PH - 2 * M)
    cv.line(M, M + PIE, PW - M, M + PIE)
    y = M + PIE
    cols = [M, M + 120, M + 450, M + 615, PW - M - 64]
    for x in cols[1:]:
        cv.line(x, M, x, y)
    cv.setFillColor(black)
    cv.setFont("Helvetica-Bold", 9); cv.drawString(cols[0] + 5, y - 12, "LEITEN COM")
    cv.setFont("Helvetica", 7); cv.drawString(cols[0] + 5, y - 22, u"Fábrica de muebles · planos")
    cv.setFont("Helvetica-Bold", 10); cv.drawString(cols[1] + 5, y - 13, info["mueble"])
    cv.setFont("Helvetica", 7)
    cv.drawString(cols[1] + 5, y - 24, "%s x %s x %s mm (ancho x alto x prof., con puertas)  ·  %s" % (
        _n(info["ancho"]), _n(info["alto"]), _n(info["prof"]), titulo))
    cv.drawString(cols[2] + 5, y - 12, "Ambiente: %s   Orden: %s" % (info["ambiente"], info.get("orden_codigo") or info["orden"]))
    cv.drawString(cols[2] + 5, y - 24, "Origen: GuiGui (render.json), guardado %s" % info.get("guardado", "?"))
    cv.drawString(cols[3] + 5, y - 12, "Plano: %s" % datetime.date.today().strftime("%d/%m/%Y"))
    cv.drawString(cols[3] + 5, y - 24, "mm, medidas terminadas")
    cv.setFont("Helvetica-Bold", 12); cv.drawCentredString(cols[4] + 32, y - 20, u"%d / %d" % (lamina, total))


def texto(cv, x, y, lineas, fs=7, lh=None, bold_first=False, color=black):
    lh = lh or fs + 2.2
    for i, l in enumerate(lineas):
        cv.setFont("Helvetica-Bold" if (bold_first and i == 0) else "Helvetica", fs)
        cv.setFillColor(color)
        cv.drawString(x, y - i * lh, l)
    return y - len(lineas) * lh


# ------------------------------------------------------------------ notas (GuiGui vs vigente)
def notas(piezas):
    out = []
    marcas = sorted({(h["d"], h["prof"]) for p in piezas for h in p.holes if h["sym"] in ("HINGESCREW", "jlHoleEX") and h["d"] < 4.5})
    if marcas:
        out.append(u"Tornillos de bisagra y de placa base: GuiGui trae %s (marcas). Vigente (16/10): Ø5 x 3. "
                   u"Se corrige con etapa2/ajustar_maquina.py --bisagra." % ", ".join(u"Ø%s x %s" % (_n(d), _n(pr)) for d, pr in marcas))
    # placa base: pares de jlHoleEX a la misma y, separados 32 en x -> horizontal (20/52 del frente)
    horiz = False
    for p in piezas:
        js = [h for h in p.holes if h["sym"] == "jlHoleEX"]
        for a in js:
            for b in js:
                if a is not b and abs(a["y"] - b["y"]) < 0.5 and 30 < abs(a["x"] - b["x"]) < 34:
                    horiz = True
    if horiz:
        out.append(u"Placa base de bisagra: GuiGui la pone con los dos tornillos en línea, a 20 y 52 del frente. "
                   u"Vigente (Häfele 311.04.003 probada el 16/10): a 37 del frente, uno arriba del otro a ±16 de la cazoleta.")
    pernos = sorted({(h["d"], h["prof"]) for p in piezas for h in p.sholes if h["sym"] == "3in1Lock"})
    if pernos and any(abs(d - 8) > 0.5 for d, _ in pernos):
        out.append(u"Perno del 3 en 1 (agujero de canto): GuiGui trae %s. Vigente: Ø8 x 33 (confirmar 33 o 34 con el herraje Grupo Euro)." %
                   ", ".join(u"Ø%s x %s" % (_n(d), _n(pr)) for d, pr in pernos))
    rec = sorted({(h["d"], h["prof"]) for p in piezas for h in p.holes if h["sym"] == "3in1Lock" and abs(h["d"] - 15) > 0.5})
    if rec:
        out.append(u"Receptor del perno (cara): GuiGui trae %s. Vigente (06/10): Ø5 x 12, rosca para madera sin taco." %
                   ", ".join(u"Ø%s x %s" % (_n(d), _n(pr)) for d, pr in rec))
    finas = sorted({s["w"] for p in piezas for s in p.slots if s["w"] < 10})
    if finas:
        out.append(u"Ranuras de %s mm: la perforadora sólo ranura de 10 (T11 abajo, T187 arriba). ajustar_maquina.py las pasa a 10; "
                   u"las de cara B de menos de 10 se dan vuelta." % ", ".join(_n(w) for w in finas))
    cups = sorted({(h["d"], h["prof"]) for p in piezas for h in p.holes if h["sym"] == "HINGE"})
    if cups and all(abs(pr - 13) < 0.1 for _, pr in cups):
        out.append(u"Cazoleta Ø35 x 13 a 22,5 del canto y tornillos a 6 / ±24 de la cazoleta: coincide con lo vigente (T184, tabla 34,8/34,8/Z 24).")
    for p in piezas:
        for sl in p.slots:
            if sl["sym"] == "lightSlot" and p.tipo == "Techo" and dir_es(p.ez if sl["side"] == -1 else mul(p.ez, -1.0)) == "arriba":
                out.append(u"Tira LED: GuiGui la pone en una ranura sobre la cara de ARRIBA del techo (queda a la vista). "
                           u"La receta alacena_spar.py la lleva a la cara de abajo del piso, ranura 10 x 10 a 60 del frente.")
    for p in piezas:
        if p.aviso:
            out.append(u"%s: %s." % (p.nombre, p.aviso))
    out.append(u"La HP280 corta 1-2 mm de más: medir cada pieza con calibre antes de perforar (alarma 202h si el ancho no coincide).")
    return out


# ------------------------------------------------------------------ laminas
def lamina_vistas(cv, piezas, info, lam, total):
    rotulo(cv, info, lam, total, "Vistas generales")
    x0, y0 = M + 6, M + PIE + 6
    W = PW - 2 * M - 12; H = PH - 2 * M - PIE - 12
    lat_izq = min((p for p in piezas if p.tipo == "Lateral"), key=lambda p: p.bmin[0], default=None)
    techo = max((p for p in piezas if p.tipo == "Techo"), key=lambda p: p.bmax[2], default=None)
    frente = lambda v: (v[0], v[2], -v[1])
    lateral = lambda v: (-v[1], v[2], -v[0])
    planta = lambda v: (v[0], v[1], v[2])
    ancho, alto, prof = float(info["ancho"]), float(info["alto"]), float(info["prof"])
    # dos filas: arriba frente / frente sin puertas / corte lateral; abajo planta + isometrica.
    # Escala comun, la mayor que entra.
    MX, MY = 80.0, 68.0                      # margenes para cotas (vista() los reserva)
    s = min((H - 2 * MY - 10) / (alto + prof), (W - 3 * MX - 12) / (2 * ancho + prof))
    h1 = alto * s + MY; h2 = prof * s + MY
    wf, wl, wp = ancho * s + MX, prof * s + MX, ancho * s + MX
    ytop = y0 + H - h1
    vista(cv, piezas, x0, ytop, wf, h1, frente, "FRENTE", swing=True, cotas_de=lambda p: p.es_puerta,
          subtitulo="con puertas: cotas de las puertas y sus luces; el simbolo marca el lado de bisagra")
    vista(cv, piezas, x0 + wf + 6, ytop, wf, h1, frente, "FRENTE sin puertas", excluir=lambda p: p.es_puerta,
          subtitulo="cotas del cuerpo")
    vista(cv, piezas, x0 + 2 * (wf + 6), ytop, wl, h1, lateral, "CORTE lateral", excluir=lambda p: p is lat_izq,
          cotas_de=lambda p: not p.es_puerta, subtitulo="desde la izquierda, sin el lateral izq.; el frente a la derecha")
    vista(cv, piezas, x0, y0, wp, h2, planta, "PLANTA sin techo", excluir=lambda p: p is techo,
          cotas_de=lambda p: not p.es_puerta, subtitulo="desde arriba; el frente abajo")
    for p in piezas:
        p.desplazo = [0.0, 0.0, 0.0]
    xi = x0 + wp + 20
    cv.setFont("Helvetica-Bold", 8.5); cv.setFillColor(black)
    cv.drawString(xi, y0 + h2 - 9, u"ISOMÉTRICA")
    dibujar_iso(cv, piezas, xi, y0, W - wp - 26, h2 - 14, globos=False)
    cv.setFont("Helvetica", 6.5); cv.setFillColor(GRIS)
    cv.drawString(xi + (W - wp - 26) * 0.55, y0 + h2 - 9,
                  u"%s ancho x %s alto x %s prof. (con puertas) · %d piezas" % (_n(ancho), _n(alto), _n(prof), len(piezas)))


def lamina_explotada(cv, piezas, info, lam, total):
    rotulo(cv, info, lam, total, "Explotada y lista de piezas")
    x0, y0 = M + 6, M + PIE + 6
    W = PW - 2 * M - 12; H = PH - 2 * M - PIE - 12
    explotar(piezas)
    dibujar_iso(cv, piezas, x0, y0, W * 0.52, H - 14, globos=True)
    cv.setFont("Helvetica-Bold", 8.5); cv.setFillColor(black)
    cv.drawString(x0, y0 + H - 9, u"EXPLOTADA · el número es el globo de la lista, de la etiqueta y de la lámina de cada pieza")
    # lista
    tx = x0 + W * 0.54; ty = y0 + H - 9
    cv.drawString(tx, ty, "LISTA DE PIEZAS")
    cols = [tx, tx + 18, tx + 128, tx + 196, tx + 262, tx + 330]
    heads = [u"N°", "Pieza", u"Medida (L x A x E)", u"Código", "Material", u"Lámina"]
    y = ty - 14
    cv.setFont("Helvetica-Bold", 7)
    for c, h in zip(cols, heads):
        cv.drawString(c, y, h)
    cv.setLineWidth(0.4); cv.line(tx, y - 3, x0 + W, y - 3)
    y -= 12
    cv.setFont("Helvetica", 7)
    for p in piezas:
        a, b = sorted([p.W, p.H], reverse=True)
        vals = [str(p.num), p.nombre, "%s x %s x %s" % (_n(a), _n(b), _n(p.T)), p.codigo, mat_es(p.material), str(3 + p.num)]
        for c, v in zip(cols, vals):
            cv.drawString(c, y, v)
        y -= 10.5
    cv.line(tx, y + 7, x0 + W, y + 7)
    y -= 6
    y = texto(cv, tx, y, [u"Orden de armado (globos): laterales → horizontales de abajo hacia arriba → listones",
                          u"→ fondo por las ranuras → puertas con bisagras. Detalle en el manual de armado."], fs=6.8, color=GRIS)


def lamina_corte(cv, piezas, info, lam, total):
    rotulo(cv, info, lam, total, "Lista de corte, herrajes y notas")
    x0, y0 = M + 6, M + PIE + 6
    W = PW - 2 * M - 12; H = PH - 2 * M - PIE - 12
    cv.setFont("Helvetica-Bold", 8.5); cv.setFillColor(black)
    cv.drawString(x0, y0 + H - 9, "LISTA DE CORTE  (medidas terminadas y de corte = terminada menos cantos)")
    cols = [x0, x0 + 16, x0 + 118, x0 + 180, x0 + 238, x0 + 282, x0 + 306, x0 + 386, x0 + 466, x0 + 500, x0 + 586]
    heads = [u"N°", "Pieza", u"Código", "Terminada", "Corte", "Esp.", "Material", "Textura", "Veta", "Cantos (I / D / Ab / Ar)", "Mecanizados"]
    y = y0 + H - 24
    cv.setFont("Helvetica-Bold", 6.8)
    for c, h in zip(cols, heads):
        cv.drawString(c, y, h)
    cv.setLineWidth(0.4); cv.line(x0, y - 3, x0 + W, y - 3)
    y -= 11
    cv.setFont("Helvetica", 6.8)
    for p in piezas:
        c = p.cantos
        cant = "%s / %s / %s / %s" % tuple(_n(c[k]) if c[k] else "-" for k in ("IZQ", "DER", "ABAJO", "ARRIBA"))
        cnt = Counter()
        for o in operaciones(p):
            cnt[o["tipo"].split(" (")[0]] += 1
        mec = ", ".join("%d %s" % (n, t) for t, n in cnt.items()) or "-"
        vals = [str(p.num), p.nombre, p.codigo, "%s x %s" % (_n(p.W), _n(p.H)), "%s x %s" % (_n(p.corte_W), _n(p.corte_H)),
                _n(p.T), mat_es(p.material), tex_es(p.textura), p.veta.lower(), cant]
        cv.setFont("Helvetica", 6.8)
        for cx, v in zip(cols, vals):
            cv.drawString(cx, y, v)
        cv.setFont("Helvetica", 5.8)
        for j, l in enumerate(_partir(mec, 62)[:2]):
            cv.drawString(cols[-1], y + 3 - j * 7, l)
        y -= 14
    cv.line(x0, y + 7, x0 + W, y + 7)
    # materiales por placa
    y -= 8
    cv.setFont("Helvetica-Bold", 8.5); cv.drawString(x0, y, "RESUMEN POR MATERIAL")
    y -= 12
    porm = {}
    for p in piezas:
        k = (mat_es(p.material), tex_es(p.textura), _n(p.T))
        d = porm.setdefault(k, [0, 0.0])
        d[0] += 1; d[1] += p.corte_W * p.corte_H / 1e6
    for (ma, te, es), (n, area) in sorted(porm.items()):
        cv.setFont("Helvetica", 7)
        cv.drawString(x0, y, u"%s · %s · %s mm: %d piezas, %.2f m² netos" % (ma, te, es, n, area))
        y -= 9.5
    # herrajes
    hy = y0 + H - 24
    hx = x0 + W * 0.60
    y -= 4
    cv.setFont("Helvetica-Bold", 8.5); cv.drawString(x0, y, "HERRAJES")
    y -= 12
    tot = Counter()
    for p in piezas:
        for o in operaciones(p):
            tot[o["tipo"].split(" (")[0]] += 1
    exc = tot.get(u"Excéntrica 3 en 1", 0); per = tot.get("Perno 3 en 1", 0); rec = tot.get("Receptor del perno", 0)
    bis = tot.get("Cazoleta bisagra", 0)
    led = [s for p in piezas for s in p.slots if s["sym"] == "lightSlot"]
    lineas = [u"3 en 1 (Grupo Euro): %d excéntricas Ø15, %d pernos, %d receptores" % (exc, per, rec),
              u"Bisagras de cazoleta Ø35 codo 0 (cubre total): %d, con %d placas base · tornillos Ø5 x 3: %d" % (
                  bis, bis, tot.get("Tornillo bisagra", 0) + tot.get("Placa base bisagra", 0))]
    for p in piezas:
        for s in p.slots:
            if s["sym"] != "lightSlot":
                continue
            L = max(abs(s["x2"] - s["x1"]), abs(s["y2"] - s["y1"]))
            nA = mul(p.ez, -1.0)
            cara = dir_es(nA if s["side"] == 1 else p.ez)
            lineas.append(u"Tira LED de %s mm en ranura %s x %s de la pieza %d (%s), cara %s que mira hacia %s + fuente y salida de cable" % (
                _n(min(L, max(p.W, p.H))), _n(s["w"]), _n(s["prof"]), p.num, p.nombre, "A" if s["side"] == 1 else "B", cara))
    puertas = [p for p in piezas if p.es_puerta]
    for p in puertas:
        lado = {"h0": "bisagras a la izquierda", "hW": "bisagras a la derecha", "vH": "bisagras arriba (rebatible hacia arriba, lleva pistones)",
                "v0": "bisagras abajo"}.get(lado_bisagra(p), "")
        lineas.append(u"%s (N° %d): %s" % (p.nombre, p.num, lado))
    for l in lineas:
        cv.setFont("Helvetica", 7); cv.drawString(x0, y, l); y -= 9.5
    # notas
    y -= 6
    cv.setFont("Helvetica-Bold", 8.5); cv.drawString(x0, y, "NOTAS  (lo que GuiGui trae distinto de lo vigente en CONTEXTO.md)")
    y -= 12
    cv.setFont("Helvetica", 6.8)
    for i, n in enumerate(notas(piezas), 1):
        for j, l in enumerate(_partir(u"%d. %s" % (i, n), 185)):
            cv.drawString(x0 + (0 if j == 0 else 9), y, l); y -= 8.6
            if y < y0 + 4:
                break


def _partir(t, n):
    out, cur = [], ""
    for w in t.split(" "):
        if len(cur) + len(w) + 1 > n:
            out.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        out.append(cur)
    return out


def lamina_pieza(cv, p, piezas, info, lam, total):
    rotulo(cv, info, lam, total, u"Pieza %d · %s" % (p.num, p.nombre))
    x0, y0 = M + 6, M + PIE + 6
    W = PW - 2 * M - 12; H = PH - 2 * M - PIE - 12
    ops = operaciones(p)
    tiene_B = any(o["cara"] == "B" for o in ops)
    # columna izquierda: dibujos
    dw = W * 0.58
    if tiene_B:
        dibujo_cara(cv, p, "A", ops, x0, y0, dw / 2 - 4, H - 74)
        dibujo_cara(cv, p, "B", ops, x0 + dw / 2 + 4, y0, dw / 2 - 4, H - 74)
    else:
        dibujo_cara(cv, p, "A", ops, x0, y0, dw, H - 74)
    # cabecera de la pieza
    cv.setFillColor(black); cv.setFont("Helvetica-Bold", 13)
    cv.drawString(x0, y0 + H - 14, u"%d · %s" % (p.num, p.nombre))
    cv.setFont("Helvetica", 7.5); cv.setFillColor(GRIS)
    cv.drawString(x0, y0 + H - 25, u"GuiGui: %s  ·  código %s  ·  %s x %s x %s terminada  ·  corte %s x %s  ·  %s · %s · veta %s" % (
        p.nombre_guigui, p.codigo, _n(p.W), _n(p.H), _n(p.T), _n(p.corte_W), _n(p.corte_H),
        mat_es(p.material), tex_es(p.textura), p.veta.lower()))
    centro_m = [(info["caja"][0][i] + info["caja"][1][i]) / 2.0 for i in range(3)]
    nA = mul(p.ez, -1.0)
    adentro = dot(nA, sub(centro_m, centro(p))) > 0
    cv.drawString(x0, y0 + H - 35, u"En el mueble: +x (h) va hacia %s, +y (v) va hacia %s. Cara A mira hacia %s%s; cara B es la opuesta." % (
        dir_es(p.ex), dir_es(p.ey), dir_es(nA), " (adentro del mueble)" if adentro and eje_normal(p) != 2 else ""))
    cv.setFillColor(black)
    extras = []
    c = p.cantos
    cs = [k for k, nm in (("IZQ", "izquierdo (x=0)"), ("DER", "derecho (x=W)"), ("ABAJO", "de abajo (y=0)"), ("ARRIBA", "de arriba (y=H)")) if c[k] > 0]
    extras.append(u"Cantos (línea gruesa): %s" % (", ".join({"IZQ": "izq (x=0)", "DER": "der (x=W)", "ABAJO": "abajo (y=0)", "ARRIBA": "arriba (y=H)"}[k] + " %s mm" % _n(c[k]) for k in cs) if cs else "sin canto"))
    if p.W > p.H:
        extras.append(u"En la perforadora la pieza entra girada 90° (%s x %s, lado largo sobre Y): el archivo XML3 ya lo rota." % (_n(p.H), _n(p.W)))
    if p.rol == "FONDO":
        extras.append(u"Fondo de 5 mm: entra 5 mm en cada ranura (spec de corte %s)." % p.spec)
    cv.setFont("Helvetica", 7); cv.setFillColor(GRIS)
    for i, e in enumerate(extras[:3]):
        cv.drawString(x0, y0 + H - 45 - i * 9, e)
    # tabla de mecanizados
    tx = x0 + dw + 10; ty = y0 + H - 48
    cv.setFillColor(black); cv.setFont("Helvetica-Bold", 8.5)
    cv.drawString(tx, ty, "MECANIZADOS  (%d)" % len(ops))
    cols = [tx, tx + 14, tx + 70, tx + 166, tx + 212, tx + 266, tx + 300]
    heads = [u"N°", "Cara / canto", "Tipo", "x", "y", u"Ø / ancho", "Prof."]
    y = ty - 13
    cv.setFont("Helvetica-Bold", 6.8)
    for cx, h in zip(cols, heads):
        cv.drawString(cx, y, h)
    cv.setLineWidth(0.4); cv.line(tx, y - 3, x0 + W, y - 3)
    y -= 10.5
    for o in ops:
        if isinstance(o["x"], tuple):
            xs = u"%s → %s" % (_n(o["x"][0]), _n(o["x"][1])) if abs(o["x"][0] - o["x"][1]) > 0.01 else _n(o["x"][0])
            ys = u"%s → %s" % (_n(o["y"][0]), _n(o["y"][1])) if abs(o["y"][0] - o["y"][1]) > 0.01 else _n(o["y"][0])
        else:
            xs, ys = _n(o["x"]), _n(o["y"])
        cv.setFillColor(color_op(o)); cv.setFont("Helvetica-Bold", 6.8); cv.drawString(cols[0], y, str(o["n"]))
        cv.setFillColor(black); cv.setFont("Helvetica", 6.5)
        vals = [None, o["cara"], o["tipo"], xs, ys, (u"Ø" if o["clase"] in ("hole", "shole") else "") + _n(o["d"]), _n(o["prof"])]
        for cx, v in zip(cols[1:], vals[1:]):
            cv.drawString(cx, y, v)
        y -= 9.2
        if y < y0 + 40:
            cv.drawString(cols[1], y, u"(sigue en la tabla de la lista de corte)"); break
    # resumen de la pieza
    cnt = Counter(o["tipo"].split(" (")[0] for o in ops)
    y -= 6
    cv.setFont("Helvetica-Bold", 7)
    for l in _partir("Resumen: " + (", ".join("%d %s" % (n, t) for t, n in cnt.items()) or "sin mecanizados"), 78):
        cv.drawString(tx, y, l); y -= 9
    y -= 3
    leyenda = [(ROJO, u"excéntrica Ø15 x 13,5"), (AZUL, u"perno / receptor"), (VERDE, u"cazoleta Ø35"),
               (NARANJA, u"tornillos de bisagra"), (Color(0.5, 0.3, 0.6), "ranura")]
    cv.setFont("Helvetica", 6.5)
    for i, (col, t) in enumerate(leyenda):
        cv.setFillColor(col); cv.circle(tx + 4 + i * 66, y + 2, 2.5, fill=1, stroke=0)
        cv.setFillColor(black); cv.drawString(tx + 9 + i * 66, y, t)
    # mini-iso con la pieza resaltada
    for q in piezas:
        q.desplazo = [0.0, 0.0, 0.0]
    _mini_iso(cv, piezas, p, tx, y0 + 4, W - dw - 14, max(60.0, y - y0 - 20))


def _mini_iso(cv, piezas, p, x0, y0, w, h):
    polys = []
    for q in piezas:
        vs = vertices(q)
        cpz = [sum(v[k] for v in vs) / 8.0 for k in range(3)]
        pr = [proy_iso(v) for v in vs]
        col = Color(0.95, 0.35, 0.15) if q is p else Color(0.88, 0.88, 0.88)
        for cara in CARAS:
            a, b, c = vs[cara[0]], vs[cara[1]], vs[cara[2]]
            n = norm(cross(sub(b, a), sub(c, a)))
            cen = [sum(vs[i][k] for i in cara) / 4.0 for k in range(3)]
            if dot(n, sub(cen, cpz)) < 0:
                n = mul(n, -1)
            if dot(n, V_ISO) <= 1e-6:
                continue
            eje = [abs(x) for x in n]
            polys.append((dot(cen, V_ISO) + (5000 if q is p else 0), [(pr[i][0], pr[i][1]) for i in cara],
                          _tono(col, SOMBRA[eje.index(max(eje))]), q is p))
    xs = [q[0] for _, ps, _, _ in polys for q in ps]; ys = [q[1] for _, ps, _, _ in polys for q in ps]
    mnx, mxx, mny, mxy = min(xs), max(xs), min(ys), max(ys)
    sc = min((w - 8) / ((mxx - mnx) or 1), (h - 8) / ((mxy - mny) or 1))
    ox = x0 + (w - (mxx - mnx) * sc) / 2 - mnx * sc
    oy = y0 + (h - (mxy - mny) * sc) / 2 - mny * sc
    T = lambda q: (ox + q[0] * sc, oy + q[1] * sc)
    cv.setLineWidth(0.3)
    for _, ps, col, es in sorted(polys, key=lambda t: t[0]):
        cv.setFillColor(col); cv.setStrokeColor(Color(0.3, 0.3, 0.3) if es else Color(0.7, 0.7, 0.7))
        path = cv.beginPath(); q = T(ps[0]); path.moveTo(*q)
        for pt in ps[1:]:
            path.lineTo(*T(pt))
        path.close(); cv.drawPath(path, fill=1, stroke=1)
    cv.setFont("Helvetica", 6.5); cv.setFillColor(GRIS)
    cv.drawString(x0, y0 + h - 6, u"Dónde va en el mueble")


# ------------------------------------------------------------------ main
def planos(ruta, salida, idx=0, orden_codigo="", guardado=""):
    piezas, info = cargar(ruta, idx)
    info["orden_codigo"] = orden_codigo
    info["guardado"] = guardado or "?"
    total = 3 + len(piezas)
    cv = canvas.Canvas(salida, pagesize=landscape(A4))
    cv.setTitle(u"Planos %s" % info["mueble"]); cv.setAuthor("Leiten Com")
    lamina_vistas(cv, piezas, info, 1, total); cv.showPage()
    lamina_explotada(cv, piezas, info, 2, total); cv.showPage()
    lamina_corte(cv, piezas, info, 3, total); cv.showPage()
    for p in piezas:
        lamina_pieza(cv, p, piezas, info, 3 + p.num, total); cv.showPage()
    cv.save()
    return piezas, info


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render")
    ap.add_argument("-o", "--salida", default="planos.pdf")
    ap.add_argument("--mueble", type=int, default=0, help="indice de models[] del render")
    ap.add_argument("--orden", default="", help="codigo de orden de GuiGui, p. ej. 260625-20")
    ap.add_argument("--guardado", default="", help="fecha en que se guardo en GuiGui")
    a = ap.parse_args(argv)
    piezas, info = planos(a.render, a.salida, a.mueble, a.orden, a.guardado)
    print("%s: %s, %d piezas, %d laminas" % (a.salida, info["mueble"], len(piezas), 3 + len(piezas)))


if __name__ == "__main__":
    main()
