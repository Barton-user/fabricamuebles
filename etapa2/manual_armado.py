# -*- coding: utf-8 -*-
"""
manual_armado — manual de armado de 2 hojas A4 para el cliente, desde la receta.

    python3 manual_armado.py ../recetas/salida/ALACENA-SPAR/modelo.json -o manual.pdf
    python3 manual_armado.py modelo.json -o manual.pdf --mueble "Alacena Spar"

Lee el `modelo.json` que escriben las recetas (`recetas/*.py`): cada placa con su
posicion en el mundo (O, ex, ey, W, H, T) y cada herraje con su lugar. No hace
falta Fusion: los dibujos son isometricas de las placas, hechas aca.

Hoja 1: vista explotada con un numero por pieza + lista de piezas (numero, nombre,
        medida, codigo de la etiqueta) + lista de herrajes con cantidades.
Hoja 2: pasos de armado dibujados (lo ya armado en gris, lo nuevo en color) y
        las notas de la receta (lo que se hace a mano).

Orden de armado (el mismo criterio que etapa2/paquete.py):
    preparar herrajes -> primer lateral -> horizontales de abajo hacia arriba
    (y listones / parantes) -> fondo por las ranuras -> otro lateral (cierra)
    -> puertas con bisagras -> accesorios.

Mundo de las recetas: X a lo ancho (0 = derecha de quien mira), Y desde la pared
hacia el frente, Z hacia arriba.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
from collections import Counter, defaultdict

from reportlab.lib.colors import Color, black, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ------------------------------------------------------------------ vectores
def add(a, b): return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]
def sub(a, b): return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
def mul(a, k): return [a[0] * k, a[1] * k, a[2] * k]
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def cross(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
def norm(a):
    n = math.sqrt(dot(a, a)) or 1.0
    return [a[0] / n, a[1] / n, a[2] / n]


# ------------------------------------------------------------------ piezas
class Pieza:
    def __init__(self, d):
        self.d = d
        self.nombre = d["pieza"]
        self.codigo = d["codigo"]
        self.rol = (d.get("rol") or "").upper()
        self.W, self.H, self.T = d["W"], d["H"], d["T"]
        self.O, self.ex, self.ey = d["O"], norm(d["ex"]), norm(d["ey"])
        self.ez = cross(self.ex, self.ey)
        self.material = d.get("material", "")
        self.textura = d.get("textura", "")
        self.num = 0
        self.desplazo = [0.0, 0.0, 0.0]
        m = re.match(r"(?i)^(?:frente )?caj[oó]n (\d+)", self.nombre)
        self.cajon = int(m.group(1)) if m else 0          # 0 = no es de un cajon
        self.frente_cajon = bool(re.match(r"(?i)^frente caj[oó]n", self.nombre))

    def a_45(self):
        return any(0.05 < abs(x) < 0.95 for x in self.ex + self.ey)

    def vertices(self, extra=(0, 0, 0)):
        o = add(self.O, extra)
        vs = []
        for a in (0, self.W):
            for b in (0, self.H):
                for c in (0, -self.T):        # la placa crece hacia -ez (cara A en z=0)
                    vs.append(add(add(add(o, mul(self.ex, a)), mul(self.ey, b)), mul(self.ez, c)))
        return vs

    def centro(self):
        vs = self.vertices()
        return [sum(v[i] for v in vs) / 8.0 for i in range(3)]

    def caja(self):
        vs = self.vertices()
        return [min(v[i] for v in vs) for i in range(3)], [max(v[i] for v in vs) for i in range(3)]

    def contiene(self, p, tol=0.6):
        lo, hi = self.caja()
        return all(lo[i] - tol <= p[i] <= hi[i] + tol for i in range(3))

    def eje_normal(self):
        n = [abs(x) for x in self.ez]
        return n.index(max(n))          # 0 = X (lateral), 1 = Y (frente/fondo), 2 = Z (horizontal)

    def medida(self):
        a, b = sorted([self.W, self.H], reverse=True)
        return "%g × %g × %g" % (a, b, self.T)


def caras(vs):
    """Las 6 caras de la caja (indices de vertices() en orden de recorrido)."""
    # indice = a*4 + b*2 + c
    return [(0, 2, 6, 4), (1, 3, 7, 5), (0, 1, 5, 4), (2, 3, 7, 6), (0, 1, 3, 2), (4, 5, 7, 6)]


# ------------------------------------------------------------------ uniones
def uniones(piezas, herrajes):
    """(pieza con el perno, pieza con la excentrica) por cada 3 en 1."""
    res = []
    for h in herrajes:
        if h.get("forma") != "perno":
            continue
        # la boca del perno esta en el limite entre las dos placas; ez apunta hacia la
        # placa que recibe (la de la excentrica)
        o, ez = h["origen"], norm(h["ez"])
        a = [p for p in piezas if p.contiene(add(o, mul(ez, -5.0)), tol=0.0)]
        b = [p for p in piezas if p.contiene(add(o, mul(ez, 10.0)), tol=0.0) and p not in a]
        if a and b:
            res.append((a[0], b[0]))
    return res


def bisagras_por_puerta(piezas, herrajes):
    c = Counter()
    for h in herrajes:
        if h.get("forma") == "bisagra":
            for p in piezas:
                if p.rol == "PUERTA" and p.contiene(h["origen"], tol=2.0):
                    c[p.codigo] += 1
                    break
    return c


# ------------------------------------------------------------------ orden de armado
def pasos(piezas, herrajes):
    cajones = defaultdict(list)
    for p in piezas:
        if p.cajon:
            cajones[p.cajon].append(p)
    cuerpo = [p for p in piezas if not p.cajon]
    laterales = sorted([p for p in cuerpo if p.eje_normal() == 0 and p.rol not in ("PUERTA", "FONDO")],
                       key=lambda p: p.centro()[0])
    puertas = [p for p in cuerpo if p.rol == "PUERTA"]
    fondos = [p for p in cuerpo if p.rol == "FONDO"]
    resto = [p for p in cuerpo if p not in laterales and p not in puertas and p not in fondos]
    primero = laterales[0] if laterales else None
    ultimo = laterales[-1] if len(laterales) > 1 else None
    medio = [p for p in laterales if p not in (primero, ultimo)]
    horiz = sorted(resto + medio, key=lambda p: (p.caja()[0][2], p.eje_normal() != 2))
    uni = uniones(piezas, herrajes)
    bis = bisagras_por_puerta(piezas, herrajes)

    def n_uniones(nuevas, puestas):
        s = set(id(p) for p in nuevas); t = s | set(id(p) for p in puestas)
        return sum(1 for a, b in uni if (id(a) in s or id(b) in s) and id(a) in t and id(b) in t)

    out, puestas = [], []
    cnt = Counter(h.get("forma") for h in herrajes)
    out.append(dict(titulo="Preparar los herrajes", nuevas=[], ya=[],
                    texto="Atornillar los %d pernos en sus agujeros de canto y colocar las %d "
                          "excéntricas en sus agujeros de cara, con la flecha mirando al canto. "
                          "Todavía no ajustar." % (cnt.get("perno", 0), cnt.get("excentrica", 0)),
                    dibujo="herrajes"))
    if primero:
        out.append(dict(titulo="Primer lateral", nuevas=[primero], ya=[],
                        texto="Apoyar el %s acostado sobre una superficie limpia, con la cara de "
                              "adentro (la de los agujeros) hacia arriba." % primero.nombre.lower()))
        puestas.append(primero)
    if horiz:
        n = n_uniones(horiz, puestas)
        nombres = [p.nombre.lower() for p in horiz]
        que = _enumerar(nombres) if len(set(nombres)) <= 5 else "las %d piezas de abajo hacia arriba" % len(horiz)
        out.append(dict(titulo="Piezas horizontales", nuevas=list(horiz), ya=list(puestas),
                        texto="Encastrar %s en el lateral, de abajo hacia arriba. Cada perno entra en "
                              "su excéntrica: girar la excéntrica media vuelta con destornillador para "
                              "trabar (%d uniones)." % (que, n)))
        puestas += horiz
    if fondos:
        f = fondos[0]
        sale = [0.0, 0.0, 0.0]
        if ultimo:                         # asoma por el lado que todavia esta abierto
            d = 1.0 if ultimo.centro()[0] > f.centro()[0] else -1.0
            sale[0] = d * 0.55 * max(f.W, f.H)
        out.append(dict(titulo="Fondo" if len(fondos) == 1 else "Fondos", nuevas=list(fondos),
                        ya=list(puestas), desliza=sale,
                        texto="Deslizar %s por las ranuras desde el lado abierto, con la cara "
                              "vista hacia adentro del mueble, hasta el tope."
                              % ("el fondo" if len(fondos) == 1 else "los %d fondos" % len(fondos))))
        puestas += fondos
    if ultimo:
        n = n_uniones([ultimo], puestas)
        out.append(dict(titulo="Cerrar con el otro lateral", nuevas=[ultimo], ya=list(puestas),
                        texto="Presentar el %s sobre los pernos y trabar las %d excéntricas. "
                              "Parar el mueble y verificar que esté a escuadra (diagonales iguales)."
                              % (ultimo.nombre.lower(), n)))
        puestas.append(ultimo)
    npatas = sum(1 for h in herrajes if h.get("forma") == "pata")
    if npatas:
        out.append(dict(titulo="Patas", nuevas=[], ya=list(puestas),
                        texto="Con el mueble acostado, atornillar las %d patas regulables abajo, en sus "
                              "lugares. Pararlo y nivelarlo girando las patas. El zócalo se engancha al "
                              "final, cuando el mueble está en su lugar." % npatas))
    if cajones:
        uno = cajones[min(cajones)]
        caja = [p for p in uno if not p.frente_cajon]
        nc = len(cajones)
        out.append(dict(titulo="Armar los cajones" if nc > 1 else "Armar el cajón", nuevas=caja, ya=[],
                        solo=True,
                        texto="Para cada cajón (%d): unir frente y contrafrente con los costados, deslizar el "
                              "fondo por las ranuras y cerrar. Atornillar el frente exterior desde adentro, "
                              "centrado. (En el dibujo, el cajón 1.)" % nc))
        corr = sum(1 for h in herrajes if h.get("forma") == "corredera")
        todas = [p for c in cajones.values() for p in c]
        out.append(dict(titulo="Correderas y cajones", nuevas=todas, ya=list(puestas),
                        texto="Atornillar las correderas (%d) en los laterales, a la altura de sus agujeros, y "
                              "la otra mitad en los costados de cada cajón. Enganchar cada cajón y "
                              "regular el frente para que la luz quede pareja." % corr))
        puestas += todas
    if puertas:
        nb = sum(bis.values())
        out.append(dict(titulo="Puertas", nuevas=list(puertas), ya=list(puestas),
                        texto="Atornillar las bisagras en las cazoletas de cada puerta (%d en total) y "
                              "las placas base en el mueble. Enganchar cada puerta en su base y regular "
                              "con los tornillos de la bisagra hasta que la luz quede pareja." % nb))
        puestas += puertas
    return out


def _rangos(ns):
    out, i = [], 0
    while i < len(ns):
        j = i
        while j + 1 < len(ns) and ns[j + 1] == ns[j] + 1:
            j += 1
        out.append(str(ns[i]) if j == i else ("%d y %d" % (ns[i], ns[j]) if j == i + 1 else "%d a %d" % (ns[i], ns[j])))
        i = j + 1
    return ", ".join(out)


def _enumerar(xs):
    xs = list(dict.fromkeys(xs))
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " y " + xs[-1]


# ------------------------------------------------------------------ dibujo
VISTA = norm([-0.85, 1.0, 0.75])          # desde adelante, a la derecha del que mira y arriba
DER = norm(cross([0, 0, 1], VISTA))
ARR = cross(VISTA, DER)

COL = {
    "nuevo": Color(0.96, 0.62, 0.20), "ya": Color(0.86, 0.86, 0.86),
    "PET": Color(0.55, 0.62, 0.70), "FONDO": Color(0.93, 0.90, 0.82), "placa": Color(0.82, 0.82, 0.80),
}
SOMBRA = {0: 0.80, 1: 1.0, 2: 0.92}      # aclarar/oscurecer cada cara por su orientacion


def _tono(c, k):
    return Color(min(1, c.red * k), min(1, c.green * k), min(1, c.blue * k))


def proy(p):
    return dot(p, DER), dot(p, ARR), dot(p, VISTA)


def dibujar(cv, items, x0, y0, w, h, globos=None):
    """items: lista de (pieza, color, desplazamiento). Encaja el dibujo en la caja."""
    polys = []
    for pz, color, extra in items:
        vs = pz.vertices(extra)
        centro_pz = [sum(v[k] for v in vs) / 8.0 for k in range(3)]
        pr = [proy(v) for v in vs]
        for cara in caras(vs):
            pts = [pr[i] for i in cara]
            a, b, c = (vs[cara[0]], vs[cara[1]], vs[cara[2]])
            n = norm(cross(sub(b, a), sub(c, a)))
            cen = [sum(vs[i][k] for i in cara) / 4.0 for k in range(3)]
            if dot(n, sub(cen, centro_pz)) < 0:
                n = mul(n, -1)
            if dot(n, VISTA) <= 1e-6:
                continue
            eje = [abs(x) for x in n]
            k = SOMBRA[eje.index(max(eje))]
            polys.append((dot(cen, VISTA), [(p[0], p[1]) for p in pts], _tono(color, k)))
    if not polys:
        return None
    xs = [p[0] for _, ps, _ in polys for p in ps]; ys = [p[1] for _, ps, _ in polys for p in ps]
    gx = [g[1][0] for g in (globos or [])]; gy = [g[1][1] for g in (globos or [])]
    mnx, mxx = min(xs + gx), max(xs + gx); mny, mxy = min(ys + gy), max(ys + gy)
    esc = min(w / ((mxx - mnx) or 1), h / ((mxy - mny) or 1))
    ox = x0 + (w - (mxx - mnx) * esc) / 2 - mnx * esc
    oy = y0 + (h - (mxy - mny) * esc) / 2 - mny * esc
    T = lambda p: (ox + p[0] * esc, oy + p[1] * esc)
    cv.setLineWidth(0.5)
    for _, ps, col in sorted(polys, key=lambda t: t[0]):
        cv.setFillColor(col); cv.setStrokeColor(Color(0.25, 0.25, 0.25))
        path = cv.beginPath(); q = T(ps[0]); path.moveTo(*q)
        for p in ps[1:]:
            path.lineTo(*T(p))
        path.close(); cv.drawPath(path, fill=1, stroke=1)
    for num, pos, ancla in (globos or []):
        a, b = T(ancla), T(pos)
        cv.setStrokeColor(black); cv.setLineWidth(0.6); cv.line(a[0], a[1], b[0], b[1])
        cv.setFillColor(white); cv.circle(b[0], b[1], 7.5, fill=1, stroke=1)
        cv.setFillColor(black); cv.setFont("Helvetica-Bold", 8.5)
        cv.drawCentredString(b[0], b[1] - 3, str(num))
    return T


def explotar(piezas):
    lo = [min(p.caja()[0][i] for p in piezas) for i in range(3)]
    hi = [max(p.caja()[1][i] for p in piezas) for i in range(3)]
    cen = [(lo[i] + hi[i]) / 2 for i in range(3)]
    tam = max(hi[i] - lo[i] for i in range(3))
    for p in piezas:
        e = p.eje_normal(); c = p.centro()
        v = [0.0, 0.0, 0.0]
        if p.rol == "PUERTA":
            v[1] = 0.75 * tam
            v[2] = 0.10 * tam * (1 if c[2] > cen[2] else -1)
        elif p.rol == "FONDO":
            v[1] = -0.45 * tam
        else:
            lado = c[e] - cen[e]
            if abs(lado) > 0.15 * (hi[e] - lo[e]):
                v[e] = math.copysign((0.55 if e == 0 else 0.35) * tam, lado)
        p.desplazo = v
    # que las puertas no tapen ningun lateral: alejarlas hasta que no se pisen en el dibujo
    puertas = [p for p in piezas if p.rol == "PUERTA"]
    otras = [p for p in piezas if p.rol != "PUERTA"]
    def caja2d(ps):
        pts = [proy(v) for p in ps for v in p.vertices(p.desplazo)]
        return min(q[0] for q in pts), max(q[0] for q in pts), min(q[1] for q in pts), max(q[1] for q in pts)
    def pisa(a, b):
        return not (a[1] < b[0] or b[1] < a[0] or a[3] < b[2] or b[3] < a[2])
    k = 0.75
    while puertas and k < 2.5 and any(pisa(caja2d([d]), caja2d([o])) for d in puertas for o in otras
                                      if o.eje_normal() == 0):
        k += 0.1
        for d in puertas:
            d.desplazo[1] = k * tam
    return cen


# ------------------------------------------------------------------ PDF
def manual(modelo, salida, mueble=None):
    piezas = [Pieza(d) for d in modelo["piezas"] if not mueble or d["mueble"] == mueble]
    herrajes = [h for h in modelo.get("herrajes", []) if not mueble or h.get("mueble") == mueble]
    nombre = mueble or (piezas[0].d["mueble"] if piezas else modelo.get("documento", ""))
    ps = pasos(piezas, herrajes)
    n = 0
    for st in ps:                                    # numeros en orden de armado
        for p in st["nuevas"]:
            if not p.num:
                n += 1; p.num = n
    for p in piezas:
        if not p.num:
            n += 1; p.num = n
    lo = [min(p.caja()[0][i] for p in piezas) for i in range(3)]
    hi = [max(p.caja()[1][i] for p in piezas) for i in range(3)]
    ancho, fondo, alto = hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]

    W, H = A4
    cv = canvas.Canvas(salida, pagesize=A4)
    cv.setTitle("Manual de armado — %s" % nombre)
    m = 36

    def encabezado(sub):
        cv.setFillColor(black); cv.setFont("Helvetica-Bold", 17)
        cv.drawString(m, H - m - 6, nombre)
        cv.setFont("Helvetica", 10)
        cv.drawString(m, H - m - 22, "Manual de armado · %s · %g × %g × %g mm (ancho × profundidad × alto)"
                      % (sub, round(ancho), round(fondo), round(alto)))
        orden = modelo.get("orden") or ""
        if orden:
            cv.drawRightString(W - m, H - m - 6, "Orden %s" % orden)
        cv.setStrokeColor(Color(0.6, 0.6, 0.6)); cv.line(m, H - m - 30, W - m, H - m - 30)

    # ---------------- hoja 1
    encabezado("hoja 1 de 2 · qué hay en la caja")
    explotar(piezas)
    items, glob = [], []
    for p in piezas:
        col = COL["FONDO"] if p.rol == "FONDO" else (COL["PET"] if "PET" in (p.material + p.textura).upper() else COL["placa"])
        items.append((p, col, p.desplazo))
        c = add(p.centro(), p.desplazo)
        cp = proy(c)
        glob.append((p.num, (cp[0] + 0.0, cp[1] + 0.0), (cp[0], cp[1])))
    # globos: corridos un poco hacia afuera del centro del dibujo
    cx = sum(g[2][0] for g in glob) / len(glob); cy = sum(g[2][1] for g in glob) / len(glob)
    tam = max(ancho, fondo, alto)
    glob = [(nu, (a[0] + (a[0] - cx) * 0.18 + 0.06 * tam, a[1] + (a[1] - cy) * 0.18 + 0.05 * tam), a)
            for nu, _, a in glob]
    dibujar(cv, items, m, H * 0.47, W - 2 * m, H * 0.40, globos=glob)

    y = H * 0.47 - 8
    cv.setFont("Helvetica-Bold", 11); cv.setFillColor(black); cv.drawString(m, y, "Piezas")
    y -= 14
    orden = sorted(piezas, key=lambda p: p.num)
    dos = len(orden) > 16
    mitades = [orden[:(len(orden) + 1) // 2], orden[(len(orden) + 1) // 2:]] if dos else [orden]
    ancho_col = (W - 2 * m - 12) / len(mitades)
    paso = 9.2 if dos else 11
    y0 = y
    for k, grupo in enumerate(mitades):
        x0 = m + k * (ancho_col + 12)
        rel = [0, 18, 0.40, 0.62, 0.79] if dos else [0, 26, 190, 300, 400]
        cols = [x0 + (c * ancho_col if isinstance(c, float) else c) for c in rel]
        yy = y0
        cv.setFont("Helvetica-Bold", 7.5 if dos else 8)
        for x, t in zip(cols, ["N°", "Pieza", "Medida (mm)", "Material", "Código" if dos else "Código de la etiqueta"]):
            cv.drawString(x, yy, t)
        yy -= 4; cv.line(x0, yy, x0 + ancho_col, yy); yy -= 9
        cv.setFont("Helvetica", 7 if dos else 8)
        for p in grupo:
            t = (p.textura or p.material or "").strip()
            mat = t if any(ch.isdigit() for ch in t) else ("%s %g" % (t, p.T)).strip()
            for x, t in zip(cols, [str(p.num), p.nombre, p.medida(), mat, p.codigo]):
                cv.drawString(x, yy, t)
            yy -= paso
        y = min(y, yy)
    # herrajes
    cnt = Counter()
    for h in herrajes:
        f = h.get("forma")
        if f == "excentrica": cnt["Excéntrica Ø15 (traba del 3 en 1)"] += 1
        elif f == "perno": cnt["Perno del 3 en 1"] += 1
        elif f == "receptor": cnt["Receptor Ø10 (taco)"] += 1
        elif f == "bisagra": cnt["Bisagra de cazoleta Ø35 con placa base"] += 1
        elif f == "led": cnt["Tira LED %g mm" % h.get("args", {}).get("largo", 0)] += 1
        elif f == "corredera": cnt["Corredera de bolas %g mm (media)" % h.get("args", {}).get("largo", 0)] += 1
        elif f == "pata": cnt["Pata regulable"] += 1
        else: cnt[h.get("nombre", f)] += 1
    nb = sum(1 for h in herrajes if h.get("forma") == "bisagra")
    if nb:
        cnt["Tornillos para bisagra y placa base"] = nb * 4
    xh = m
    yh = y - 12
    cv.setFont("Helvetica-Bold", 11); cv.drawString(xh, yh, "Herrajes"); yh -= 16
    cv.setFont("Helvetica", 8.5)
    for k, v in cnt.items():
        cv.drawRightString(xh + 18, yh, str(v)); cv.drawString(xh + 24, yh, "×  " + k)
        yh -= 12
    xh, yh = W / 2 + 60, y - 12
    cv.setFont("Helvetica-Bold", 11); cv.drawString(xh, yh, "Herramientas"); yh -= 16
    cv.setFont("Helvetica", 8.5)
    for t in ("Destornillador Phillips", "Destornillador plano (excéntricas)", "Metro"):
        cv.drawString(xh, yh, "· " + t); yh -= 11
    cv.setFont("Helvetica-Oblique", 7.5); cv.setFillColor(Color(0.35, 0.35, 0.35))
    cv.drawString(m, m - 12, "El número de cada pieza es el orden en que se arma. El código coincide con la etiqueta pegada en la pieza.")
    cv.showPage()

    # ---------------- hoja 2
    encabezado("hoja 2 de 2 · paso a paso")
    cols_n, filas_n = 2, math.ceil(len(ps) / 2.0)
    top = H - m - 40
    alto_celda = (top - m - (110 if modelo.get("avisos") else 20)) / filas_n
    ancho_celda = (W - 2 * m - 14) / cols_n
    for i, st in enumerate(ps):
        col, fil = i % cols_n, i // cols_n
        x = m + col * (ancho_celda + 14); y = top - (fil + 1) * alto_celda
        cv.setStrokeColor(Color(0.75, 0.75, 0.75)); cv.setLineWidth(0.6)
        cv.roundRect(x, y + 4, ancho_celda, alto_celda - 8, 6, stroke=1, fill=0)
        cv.setFillColor(COL["nuevo"]); cv.circle(x + 16, y + alto_celda - 20, 10, fill=1, stroke=0)
        cv.setFillColor(white); cv.setFont("Helvetica-Bold", 11); cv.drawCentredString(x + 16, y + alto_celda - 24, str(i + 1))
        cv.setFillColor(black); cv.setFont("Helvetica-Bold", 10.5); cv.drawString(x + 32, y + alto_celda - 24, st["titulo"])
        # texto
        tx = st["texto"]
        if st["nuevas"]:
            tx += "  (Piezas %s.)" % _rangos(sorted(p.num for p in st["nuevas"]))
        lineas = _partir(tx, 62)
        cv.setFont("Helvetica", 8.2)
        yy = y + 14 + 10 * (len(lineas) - 1)
        for ln in lineas:
            cv.drawString(x + 10, yy, ln); yy -= 10
        hd = alto_celda - 50 - 10 * len(lineas)
        if st.get("dibujo") == "herrajes":
            _dibujo_herrajes(cv, x + 10, y + 20 + 10 * len(lineas), ancho_celda - 20, hd)
            continue
        items = [] if st.get("solo") else [(p, COL["ya"], [0, 0, 0]) for p in st["ya"]]
        for p in st["nuevas"]:
            ex = [0, 0, 0]
            if p.rol == "PUERTA": ex = [0, 120, 0]
            elif p.rol == "FONDO": ex = st.get("desliza", [0, 0, 0])
            items.append((p, COL["nuevo"], ex))
        dibujar(cv, items, x + 10, y + 20 + 10 * len(lineas), ancho_celda - 20, hd)
    avisos = avisos_del_mueble(modelo, nombre)
    if any(p.a_45() for p in piezas):
        avisos = ["Este mueble tiene piezas a 45° (esquinero): el orden de armado automático puede no "
                  "servir; revisar los pasos a mano antes de entregar."] + avisos
    if avisos:
        yy = m + 86
        cv.setFillColor(Color(0.7, 0.2, 0.1)); cv.setFont("Helvetica-Bold", 10)
        cv.drawString(m, yy, "Pendiente de definir en fábrica (sacar antes de entregar al cliente)")
        cv.setFillColor(black)
        yy -= 13; cv.setFont("Helvetica", 8)
        for a in avisos:
            for k, ln in enumerate(_partir(a, 120)):
                cv.drawString(m + (0 if k == 0 else 8), yy, ("· " if k == 0 else "") + ln); yy -= 10
            if yy < m: break
    cv.save()
    return ps, piezas


def avisos_del_mueble(modelo, nombre):
    """Las notas de la receta que son de este mueble (las que empiezan con su nombre)."""
    todos = list(dict.fromkeys(p["mueble"] for p in modelo["piezas"]))
    def corto(n):
        partes = n.split(" ", 1)
        return partes[1] if len(partes) == 2 and re.match(r"^[A-Z]\d*$", partes[0]) else n
    res = []
    for a in modelo.get("avisos") or []:
        de = [n for n in todos if a.startswith(n) or a.startswith(corto(n))]
        if (de and nombre in de) or (not de and len(todos) == 1):
            res.append(a)
    return res


def _dibujo_herrajes(cv, x, y, w, h):
    """Esquema del 3 en 1: perno en el canto, excentrica en la cara."""
    cxm = x + w / 2; cym = y + h / 2
    s = min(w / 220.0, h / 120.0)
    gr = Color(0.82, 0.82, 0.80)
    cv.setStrokeColor(Color(0.25, 0.25, 0.25)); cv.setLineWidth(0.6)
    cv.setFillColor(gr); cv.rect(cxm - 100 * s, cym - 9 * s, 90 * s, 18 * s, fill=1)          # placa con perno (canto)
    cv.setFillColor(gr); cv.rect(cxm + 10 * s, cym - 50 * s, 18 * s, 100 * s, fill=1)        # placa con excentrica
    cv.setFillColor(COL["nuevo"]); cv.rect(cxm - 10 * s, cym - 3 * s, 34 * s, 6 * s, fill=1)  # perno
    cv.circle(cxm + 19 * s, cym, 7.5 * s, fill=1)                                             # excentrica
    cv.setFillColor(black); cv.setFont("Helvetica", 7.5)
    cv.drawString(cxm - 100 * s, cym - 9 * s - 11, "perno: se atornilla en el canto")
    cv.drawString(cxm + 32 * s, cym + 8, "excéntrica: en la cara,")
    cv.drawString(cxm + 32 * s, cym - 2, "se traba girándola")


def _partir(t, n):
    out, ln = [], ""
    for w in t.split():
        if len(ln) + len(w) + 1 > n:
            out.append(ln); ln = w
        else:
            ln = (ln + " " + w).strip()
    if ln: out.append(ln)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("modelo", help="modelo.json de una receta")
    ap.add_argument("-o", "--salida", default="manual_armado.pdf")
    ap.add_argument("--mueble", help="si el modelo tiene varios muebles, cual")
    a = ap.parse_args(argv)
    with open(a.modelo, encoding="utf-8") as fh:
        modelo = json.load(fh)
    muebles = list(dict.fromkeys(p["mueble"] for p in modelo["piezas"]))
    if a.mueble or len(muebles) == 1:
        ps, piezas = manual(modelo, a.salida, a.mueble or muebles[0])
        print("%s: %d piezas, %d pasos -> %s" % (a.mueble or muebles[0], len(piezas), len(ps), a.salida))
    else:
        base, ext = os.path.splitext(a.salida)
        for mb in muebles:
            out = "%s_%s%s" % (base, mb.replace(" ", "_").replace("/", "-"), ext)
            ps, piezas = manual(modelo, out, mb)
            print("%s: %d piezas, %d pasos -> %s" % (mb, len(piezas), len(ps), out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
