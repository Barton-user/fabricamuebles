# -*- coding: utf-8 -*-
"""
ArmarDesdeRender — arma en Fusion un ambiente completo de GuiGui a partir de su
`render.json` (el modelo 3D abierto que devuelve `project_search_order`, ver
referencia/GUIGUI_MCP/LEEME.md). Es la version generica de ArmarPrueba1: no hay
tabla escrita a mano, todo sale del JSON.

Que hace por cada placa (Plank y puerta/SingleDoor):
  - un componente, con la placa ACOSTADA adentro: X = ancho (h), Y = alto (v),
    espesor en Z desde 0 hacia abajo. Cara A (Z=0) = la cara "side -1" de GuiGui.
  - contorno de `lastCurve` (escotaduras del unero, hueco del tacho)
  - agujeros de cara (`holes`), de canto (`sholes`), ranuras de cara (`slots`)
    y de canto (`sslots`), con las medidas reales del JSON
  - atributos FabricaMuebles (TIPO, CODIGO, MATERIAL, TEXTURA, cantos, MUEBLE)
  - color por textura
  - y la ubica en el mueble con la matriz de la ocurrencia.

Herrajes (componentes TIPO=HERRAJE, uno por tipo, reutilizados):
  - tres en uno: excentrica en cada O15, perno en cada O8 de canto, receptor en
    cada O10 (de cara o de canto). Formas de PonerHerrajes.
  - bisagra de cazoleta completa en cada O35 (HINGE), con la base sobre el
    lateral/techo que tiene los jlHoleEX.
  - correderas telescopicas en los agujeros `slideRail` (canal en el lateral,
    barra en el costado del cajon).
  - tira LED en cada `lightSlot`.

MARCO DE GUIGUI (deducido y verificado contra PRUEBA 1, ver CONTEXTO §17):
  hdvDir = "h_v_d", digitos 0..5 = +X +Y +Z -X -Y -Z del mundo de GuiGui.
  h = eje del ancho de la placa (x del archivo), v = eje del alto (y), d = normal.
  `holes[].side` = 1 cara con normal +d, -1 cara con normal -d. `ocenter` es la
  posicion en el marco (h, v) con origen en la esquina donde arrancan h y v.
  `sholes[].side`: 1 canto x=0, 2 canto y=H, 3 canto x=W, 4 canto y=0.
  `lastCurve.vertex` esta centrado y ESPEJADO en x: x = W/2 - vx, y = vy + H/2.
  `sslots[].pt1.y` = distancia desde la cara +d.
  GuiGui: X derecha, Y arriba, Z hacia atras (frente en -Z) -> Fusion (x, z, y).

USO desde el MCP de Fusion:
    mod.armar(ruta_json, modelos=None, nuevo=True)
"""

import io
import json
import math
import os
import traceback
import importlib.util

import adsk.core
import adsk.fusion

GRUPO = "FabricaMuebles"
MM = 0.1
AXES = {0: (1, 0, 0), 1: (0, 1, 0), 2: (0, 0, 1), 3: (-1, 0, 0), 4: (0, -1, 0), 5: (0, 0, -1)}

PH_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "PonerHerrajes", "PonerHerrajes.py")

BIBLIOTECA = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "herrajes", "biblioteca")

PALETA = [
    (u"玛雅灰", (146, 146, 148)),      # 13 gris maya
    (u"拉丝胡桃", "Walnut"),           # 04 nogal cepillado (apariencia de Fusion)
    (u"白麻面", (234, 231, 223)),      # d02 blanco lino
    (u"暖白", (246, 241, 229)),        # 01 blanco calido
    ("nogal", "Walnut"), ("roble", "Oak"), ("blanco", (240, 239, 235)),
    ("gris", (146, 146, 148)), ("negro", (38, 38, 40)),
]
POR_DEFECTO = (205, 192, 170)
BASE_COLOR = "Plastic - Matte (White)"

DIBUJAR_HERRAJES = True
_PH = None


# --------------------------------------------------------------------------- #
#  utilidades
# --------------------------------------------------------------------------- #

def _ph():
    global _PH
    if _PH is None:
        spec = importlib.util.spec_from_file_location("PonerHerrajes", PH_PATH)
        _PH = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_PH)
    return _PH


def p3(x, y, z):
    return adsk.core.Point3D.create(x * MM, y * MM, z * MM)


def v3(v):
    return adsk.core.Vector3D.create(v[0], v[1], v[2])


def cruz(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def suma(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def esc(a, k):
    return (a[0] * k, a[1] * k, a[2] * k)


def gg2f(v):
    """GuiGui (x, y arriba, z atras) -> Fusion (x, y=z_gg, z=y_gg)."""
    return (v[0], v[2], v[1])


def parse_vec(s):
    return tuple(float(t) for t in str(s).split(","))


def caja(tbm, x0, x1, y0, y1, z0, z1):
    c = p3((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0)
    obb = adsk.core.OrientedBoundingBox3D.create(
        c, adsk.core.Vector3D.create(1, 0, 0), adsk.core.Vector3D.create(0, 1, 0),
        abs(x1 - x0) * MM, abs(y1 - y0) * MM, abs(z1 - z0) * MM)
    return tbm.createBox(obb)


def cil(tbm, a, b, d):
    return tbm.createCylinderOrCone(p3(*a), d / 2.0 * MM, p3(*b), d / 2.0 * MM)


def resta(tbm, cuerpo, herramientas):
    n = 0
    for h in herramientas:
        try:
            tbm.booleanOperation(cuerpo, h, adsk.fusion.BooleanTypes.DifferenceBooleanType)
            n += 1
        except Exception:
            pass
    return n


def une(tbm, cuerpo, piezas):
    for pz in piezas:
        try:
            tbm.booleanOperation(cuerpo, pz, adsk.fusion.BooleanTypes.UnionBooleanType)
        except Exception:
            pass
    return cuerpo


def matriz(origen, ex, ey):
    ez = cruz(ex, ey)
    m = adsk.core.Matrix3D.create()
    m.setWithCoordinateSystem(p3(*origen), v3(ex), v3(ey), v3(ez))
    return m


def marco(origen_mm, ez, ex_pista=None):
    """Matrix3D (mm) con Z = ez y X = ex_pista proyectado."""
    z = v3(ez); z.normalize()
    if ex_pista is None or abs(v3(ex_pista).dotProduct(z)) > 0.9:
        ex_pista = (1, 0, 0) if abs(z.x) < 0.9 else (0, 1, 0)
    xp = v3(ex_pista)
    k = xp.dotProduct(z)
    x = adsk.core.Vector3D.create(xp.x - k * z.x, xp.y - k * z.y, xp.z - k * z.z)
    x.normalize()
    y = z.crossProduct(x)
    m = adsk.core.Matrix3D.create()
    m.setWithCoordinateSystem(p3(*origen_mm), x, y, z)
    return m


def transformar(m, p_mm):
    p = p3(*p_mm)
    p.transformBy(m)
    return (p.x / MM, p.y / MM, p.z / MM)


def girar(m, v):
    w = v3(v)
    w.transformBy(m)
    return (w.x, w.y, w.z)


# --------------------------------------------------------------------------- #
#  apariencias
# --------------------------------------------------------------------------- #

def _buscar(col, nombre):
    try:
        a = col.itemByName(nombre)
        if a is not None:
            return a
    except Exception:
        pass
    for i in range(col.count):
        if col.item(i).name == nombre:
            return col.item(i)
    return None


def _de_biblioteca(app, design, nombre):
    ya = _buscar(design.appearances, nombre)
    if ya is not None:
        return ya
    for i in range(app.materialLibraries.count):
        lib = app.materialLibraries.item(i)
        try:
            aps = lib.appearances
        except Exception:
            continue
        a = _buscar(aps, nombre)
        if a is not None:
            try:
                return design.appearances.addByCopy(a, nombre)
            except Exception:
                pass
    return None


def _color(app, design, rgb, etiqueta):
    nombre = "FM %s" % etiqueta
    ya = _buscar(design.appearances, nombre)
    if ya is not None:
        return ya
    base = _de_biblioteca(app, design, BASE_COLOR)
    if base is None:
        return None
    nueva = design.appearances.addByCopy(base, nombre)
    for k in range(nueva.appearanceProperties.count):
        p = nueva.appearanceProperties.item(k)
        if p.objectType.endswith("ColorProperty") and p.name == "Color":
            try:
                p.value = adsk.core.Color.create(rgb[0], rgb[1], rgb[2], 255)
            except Exception:
                pass
            break
    return nueva


_CACHE_AP = {}


def apariencia_textura(app, design, textura):
    clave = (textura or "").lower()
    for pedazo, valor in PALETA:
        if pedazo.lower() in clave:
            break
    else:
        pedazo, valor = "(sin textura)", POR_DEFECTO
    if pedazo in _CACHE_AP:
        return _CACHE_AP[pedazo]
    ap = _de_biblioteca(app, design, valor) if isinstance(valor, str) \
        else _color(app, design, valor, pedazo)
    if ap is None and isinstance(valor, str):
        ap = _color(app, design, (110, 78, 52), pedazo)
    _CACHE_AP[pedazo] = ap
    return ap


def apariencia_nombre(app, design, candidatos, rgb_fallback, etiqueta):
    for n in candidatos:
        ap = _de_biblioteca(app, design, n)
        if ap is not None:
            return ap
    return _color(app, design, rgb_fallback, etiqueta)


# --------------------------------------------------------------------------- #
#  lectura del render.json
# --------------------------------------------------------------------------- #

class Pieza(object):
    pass


def _cantos(edge):
    """'←0↓0→1↑0' -> (izq, abajo, der, arriba)"""
    out = {"IZQ": "0", "ABAJO": "0", "DER": "0", "ARRIBA": "0"}
    if not edge:
        return out
    s = str(edge)
    import re
    for flecha, k in ((u"←", "IZQ"), (u"↓", "ABAJO"), (u"→", "DER"), (u"↑", "ARRIBA")):
        m = re.search(flecha + r"([0-9.]+)", s)
        if m:
            out[k] = m.group(1)
    return out


def _pieza_de(nodo, datos, anchor_abs, hdv, mueble, ambiente):
    """nodo = el que tiene `vertices`; datos = el que tiene holes/spec (mismo o padre)."""
    vs = [parse_vec(v) for v in nodo["vertices"]]
    bmin = [min(v[i] for v in vs) * 1000.0 + anchor_abs[i] for i in range(3)]
    bmax = [max(v[i] for v in vs) * 1000.0 + anchor_abs[i] for i in range(3)]
    h, v, d = [AXES[int(t)] for t in str(hdv).split("_")]
    ext = [bmax[i] - bmin[i] for i in range(3)]
    ih = [i for i in range(3) if h[i]][0]
    iv = [i for i in range(3) if v[i]][0]
    idd = [i for i in range(3) if d[i]][0]
    pz = Pieza()
    pz.W, pz.H, pz.T = ext[ih], ext[iv], ext[idd]
    origen = [0.0, 0.0, 0.0]
    origen[ih] = bmin[ih] if h[ih] > 0 else bmax[ih]
    origen[iv] = bmin[iv] if v[iv] > 0 else bmax[iv]
    origen[idd] = bmin[idd] if d[idd] > 0 else bmax[idd]    # cara Z=0 local = cara -d
    pz.origen = gg2f(origen)
    pz.ex, pz.ey = gg2f(h), gg2f(v)
    pz.ez = cruz(pz.ex, pz.ey)
    pz.nombre = datos.get("name") or nodo.get("name") or "placa"
    pz.codigo = str(datos.get("plankNum") or "")
    pz.plankName = datos.get("plankName") or ("%s_%s" % (mueble, pz.nombre))
    pz.textura = datos.get("texImg") or ""
    pz.spec = datos.get("spec") or ""
    pz.material = datos.get("matCode") or ""
    pz.texDir = datos.get("texDir") or ""
    pz.mueble = mueble
    pz.ambiente = ambiente
    pz.es_puerta = datos.get("partName") == "SingleDoor"
    pz.rol = "PUERTA" if pz.es_puerta else ("FONDO" if pz.T < 8 else "")
    pz.cantos = _cantos(datos.get("edgeInfo2") or datos.get("lightEdgeInfo"))
    pz.holes = []
    for hh in datos.get("holes") or []:
        c = hh.get("ocenter") or hh.get("center")
        pz.holes.append(dict(x=float(c["x"]), y=float(c["y"]), side=int(hh.get("side", 1)),
                             d=float(hh["diameter"]), prof=float(hh["deep"]),
                             sym=hh.get("symbol") or ""))
    pz.sholes = []
    for hh in datos.get("sholes") or []:
        c = hh.get("ocenter") or hh.get("center")
        pz.sholes.append(dict(x=float(c["x"]), y=float(c["y"]), side=int(hh.get("side", 1)),
                              d=float(hh["diameter"]), prof=float(hh["deep"]),
                              sym=hh.get("symbol") or ""))
    pz.slots = []
    for s in datos.get("slots") or []:
        a, b = s.get("opt1") or s["pt1"], s.get("opt2") or s["pt2"]
        pz.slots.append(dict(x1=float(a["x"]), y1=float(a["y"]), x2=float(b["x"]), y2=float(b["y"]),
                             w=float(s["width"]), prof=float(s["deep"]), side=int(s.get("side", 1)),
                             sym=s.get("symbol") or ""))
    pz.sslots = []
    for s in datos.get("sslots") or []:
        a, b = s.get("opt1") or s["pt1"], s.get("opt2") or s["pt2"]
        pz.sslots.append(dict(x1=float(a["x"]), y1=float(a["y"]), x2=float(b["x"]), y2=float(b["y"]),
                              w=float(s["width"]), prof=float(s["deep"]), side=int(s.get("side", 4)),
                              zpos=float(s["pt1"].get("y", pz.T / 2.0)), sym=s.get("symbol") or ""))
    pz.contorno = None
    lc = datos.get("lastCurve") or nodo.get("lastCurve")
    if lc and lc.get("vertex"):
        pts = []
        for q in lc["vertex"]:
            p = (pz.W / 2.0 - float(q["x"]), float(q["y"]) + pz.H / 2.0)
            if not pts or (abs(p[0] - pts[-1][0]) > 1e-6 or abs(p[1] - pts[-1][1]) > 1e-6):
                pts.append(p)
        if len(pts) > 1 and abs(pts[0][0] - pts[-1][0]) < 1e-6 and abs(pts[0][1] - pts[-1][1]) < 1e-6:
            pts.pop()
        if len(pts) > 4:
            pz.contorno = pts
    return pz


def leer_render(ruta, modelos=None, log=None):
    with open(ruta, "r", encoding="utf-8") as f:
        d = json.load(f)
    ambiente = ""
    try:
        ambiente = d["models"][0].get("roomName", "")
    except Exception:
        pass
    muebles = []
    for i, m in enumerate(d["models"]):
        if modelos is not None and i not in modelos:
            continue
        piezas = []
        anchor = tuple(c * 1000.0 for c in parse_vec(m["anchor"]))

        def walk(n, anc, hdv, padre_datos):
            anc = suma(anc, tuple(c * 1000.0 for c in parse_vec(n.get("anchor") or "0,0,0")))
            hdv_n = n.get("hdvDir") or hdv
            pn = n.get("partName")
            if pn == "Plank" and n.get("vertices"):
                piezas.append(_pieza_de(n, n, anc, hdv_n, m["name"], ambiente))
            elif pn == u"外框" and padre_datos is not None and n.get("vertices"):
                piezas.append(_pieza_de(n, padre_datos, anc, hdv_n, m["name"], ambiente))
            for c in n.get("children") or []:
                walk(c, anc, hdv_n, n if pn == "SingleDoor" else padre_datos)

        for c in m.get("children") or []:
            walk(c, anchor, m.get("hdvDir"), None)
        muebles.append(dict(indice=i, nombre=m["name"], piezas=piezas))
    decidir_espejos([pz for mu in muebles for pz in mu["piezas"]], log)
    return muebles, d



# --------------------------------------------------------------------------- #
#  espejado de las piezas "especiales"
#
#  En algunas piezas (cajones, zocalos, tapas frontales, uneros) el marco de los
#  agujeros esta girado 180 grados alrededor de v respecto de lo que dice hdvDir:
#  x -> W - x y las caras cambiadas. No encontramos la regla en el JSON, asi que
#  se decide por consistencia geometrica: los pernos O8 tienen que caer en un
#  receptor O10, las ranuras tienen que contener un fondo de 5 mm y las
#  cazoletas tienen que quedar cerca de los jlHoleEX de la base de la bisagra.
# --------------------------------------------------------------------------- #

def _mundo(pz, x, y, z):
    o = pz.origen
    return tuple(o[i] + pz.ex[i] * x + pz.ey[i] * y + pz.ez[i] * z for i in range(3))


def _espejar(pz):
    """Aplica el giro de 180 grados alrededor de v al marco de los mecanizados."""
    W = pz.W
    for h in pz.holes:
        h["x"] = W - h["x"]
        h["side"] = -h["side"]
    for h in pz.sholes:
        h["x"] = W - h["x"]
        h["side"] = {1: 3, 3: 1}.get(h["side"], h["side"])
    for s in pz.slots:
        s["x1"], s["x2"] = W - s["x1"], W - s["x2"]
        s["side"] = -s["side"]
    for s in pz.sslots:
        s["x1"], s["x2"] = W - s["x1"], W - s["x2"]
        s["side"] = {1: 3, 3: 1}.get(s["side"], s["side"])
        s["zpos"] = pz.T - s["zpos"]
    if pz.contorno:
        pz.contorno = [(W - x, y) for (x, y) in pz.contorno]
    pz.espejada = not getattr(pz, "espejada", False)


def _puntos_clave(pz):
    """Puntos del mundo que tienen que coincidir con algo de otra pieza."""
    pines, recept, ranuras, cazoletas, bases = [], [], [], [], []
    for h in pz.sholes:
        bx, by = boca_canto(pz, h["x"], h["y"], h["side"])
        p = _mundo(pz, bx, by, -pz.T / 2.0)
        if abs(h["d"] - 8.0) < 0.5:
            pines.append(p)
        elif abs(h["d"] - 10.0) < 0.5:
            recept.append(p)
    for h in pz.holes:
        z0, sg = z_cara(pz, h["side"])
        p = _mundo(pz, h["x"], h["y"], z0)
        if abs(h["d"] - 10.0) < 0.5 and h["sym"] == "3in1Lock":
            recept.append(p)
        elif h["sym"] == "HINGE":
            cazoletas.append(p)
        elif h["sym"] == "jlHoleEX":
            bases.append(p)
    for s in pz.slots:
        if s["sym"] != "BP":
            continue
        z0, sg = z_cara(pz, s["side"])
        ranuras.append(_mundo(pz, (s["x1"] + s["x2"]) / 2.0, (s["y1"] + s["y2"]) / 2.0, z0 + sg * 3.0))
    for s in pz.sslots:
        dx, dy = dir_canto(s["side"])
        bx, by = boca_canto(pz, (s["x1"] + s["x2"]) / 2.0, (s["y1"] + s["y2"]) / 2.0, s["side"])
        ranuras.append(_mundo(pz, bx + dx * 3.0, by + dy * 3.0, -pz.T + s["zpos"]))
    return dict(pines=pines, recept=recept, ranuras=ranuras, cazoletas=cazoletas, bases=bases)


def _caja_mundo(pz, margen=1.0):
    pts = [_mundo(pz, x, y, z) for x in (0.0, pz.W) for y in (0.0, pz.H) for z in (0.0, -pz.T)]
    return ([min(p[i] for p in pts) - margen for i in range(3)],
            [max(p[i] for p in pts) + margen for i in range(3)])


def _en_caja(p, caja_):
    return all(caja_[0][i] <= p[i] <= caja_[1][i] for i in range(3))


def _dist(a, b):
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def decidir_espejos(todas, log=None):
    """todas = lista de Pieza (todas las del ambiente). Modifica las piezas en el lugar."""
    fondos = [_caja_mundo(pz, 6.0) for pz in todas if pz.T < 8.0]
    for pz in todas:
        pz.espejada = False
    claves = {id(pz): _puntos_clave(pz) for pz in todas}

    def puntaje(pz, k):
        otros_recept = [p for q in todas if q is not pz for p in claves[id(q)]["recept"]]
        otros_pines = [p for q in todas if q is not pz for p in claves[id(q)]["pines"]]
        otros_bases = [p for q in todas if q is not pz for p in claves[id(q)]["bases"]]
        otros_caz = [p for q in todas if q is not pz for p in claves[id(q)]["cazoletas"]]
        s = 0
        for p in k["pines"]:
            if otros_recept and min(_dist(p, r) for r in otros_recept) < 1.5:
                s += 1
        for p in k["recept"]:
            if otros_pines and min(_dist(p, r) for r in otros_pines) < 1.5:
                s += 1
        for p in k["ranuras"]:
            if any(_en_caja(p, c) for c in fondos):
                s += 1
        for p in k["cazoletas"]:
            if otros_bases and min(_dist(p, r) for r in otros_bases) < 70.0:
                s += 1
        for p in k["bases"]:
            if otros_caz and min(_dist(p, r) for r in otros_caz) < 70.0:
                s += 1
        return s

    def con_datos(pz):
        k = claves[id(pz)]
        return bool(k["pines"] or k["recept"] or k["ranuras"] or k["cazoletas"] or k["bases"])

    def total():
        return sum(puntaje(pz, claves[id(pz)]) for pz in todas if con_datos(pz))

    grupos = {}
    for pz in todas:
        grupos.setdefault(pz.mueble, []).append(pz)

    cambios = 1
    vueltas = 0
    while cambios and vueltas < 8:
        cambios = 0
        vueltas += 1
        # movimientos de a una pieza
        for pz in todas:
            if not con_datos(pz):
                continue
            s0 = puntaje(pz, claves[id(pz)])
            _espejar(pz)
            k1 = _puntos_clave(pz)
            s1 = puntaje(pz, k1)
            if s1 > s0:
                claves[id(pz)] = k1
                cambios += 1
                if log:
                    log("  espejada %s %s (%d -> %d)" % (pz.mueble, pz.nombre, s0, s1))
            else:
                _espejar(pz)                      # vuelve como estaba
        # movimientos de a un mueble entero (las piezas de un unero o de un cajon
        # solo cierran si se giran todas juntas)
        for nombre, piezas in grupos.items():
            piezas = [pz for pz in piezas if con_datos(pz)]
            if not piezas:
                continue
            t0 = total()
            viejas = {id(pz): claves[id(pz)] for pz in piezas}
            for pz in piezas:
                _espejar(pz)
                claves[id(pz)] = _puntos_clave(pz)
            t1 = total()
            if t1 > t0:
                cambios += 1
                if log:
                    log("  espejado el mueble entero %s (%d -> %d)" % (nombre, t0, t1))
            else:
                for pz in piezas:
                    _espejar(pz)
                    claves[id(pz)] = viejas[id(pz)]
    return todas


# --------------------------------------------------------------------------- #
#  contorno rectilineo: caja menos celdas fuera del poligono
# --------------------------------------------------------------------------- #

def _dentro(poly, x, y):
    n = len(poly)
    adentro = False
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi):
            adentro = not adentro
        j = i
    return adentro


def recortes_contorno(pz):
    if not pz.contorno:
        return []
    xs = sorted(set([0.0, pz.W] + [p[0] for p in pz.contorno]))
    ys = sorted(set([0.0, pz.H] + [p[1] for p in pz.contorno]))
    out = []
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            cx, cy = (xs[i] + xs[i + 1]) / 2.0, (ys[j] + ys[j + 1]) / 2.0
            if xs[i + 1] - xs[i] < 0.01 or ys[j + 1] - ys[j] < 0.01:
                continue
            if not _dentro(pz.contorno, cx, cy):
                x0 = xs[i] - (1.0 if i == 0 else 0.0)
                x1 = xs[i + 1] + (1.0 if i == len(xs) - 2 else 0.0)
                y0 = ys[j] - (1.0 if j == 0 else 0.0)
                y1 = ys[j + 1] + (1.0 if j == len(ys) - 2 else 0.0)
                out.append((x0, x1, y0, y1))
    return out


# --------------------------------------------------------------------------- #
#  geometria de la placa
# --------------------------------------------------------------------------- #

def z_cara(pz, side):
    """z local de la cara `side` y sentido hacia adentro."""
    return (-pz.T, +1.0) if side == 1 else (0.0, -1.0)


def dir_canto(side):
    """Direccion hacia adentro desde el canto `side` (1 x=0, 2 y=H, 3 x=W, 4 y=0)."""
    return {1: (1.0, 0.0), 2: (0.0, -1.0), 3: (-1.0, 0.0), 4: (0.0, 1.0)}[side]


def boca_canto(pz, x, y, side):
    """Boca del agujero de canto. `ocenter` ya viene sobre el canto (tambien en los
    cantos interiores de una escotadura), asi que se usa tal cual; `side` solo da
    la direccion. Si se sale del rectangulo, se lo trae al canto exterior."""
    x = min(max(x, 0.0), pz.W)
    y = min(max(y, 0.0), pz.H)
    return (x, y)


def cuerpo_placa(tbm, pz, log):
    cuerpo = caja(tbm, 0.0, pz.W, 0.0, pz.H, -pz.T, 0.0)
    herr = []
    for (x0, x1, y0, y1) in recortes_contorno(pz):
        herr.append(caja(tbm, x0, x1, y0, y1, -pz.T - 1.0, 1.0))
    for h in pz.holes:
        z0, s = z_cara(pz, h["side"])
        herr.append(cil(tbm, (h["x"], h["y"], z0 - s * 1.0), (h["x"], h["y"], z0 + s * h["prof"]), h["d"]))
    for h in pz.sholes:
        bx, by = boca_canto(pz, h["x"], h["y"], h["side"])
        dx, dy = dir_canto(h["side"])
        z = -pz.T / 2.0
        herr.append(cil(tbm, (bx - dx, by - dy, z), (bx + dx * h["prof"], by + dy * h["prof"], z), h["d"]))
    for s in pz.slots:
        z0, sg = z_cara(pz, s["side"])
        x1, x2 = sorted((s["x1"], s["x2"]))
        y1, y2 = sorted((s["y1"], s["y2"]))
        if abs(x2 - x1) < 1e-6:
            x1, x2 = x1 - s["w"] / 2.0, x2 + s["w"] / 2.0
        if abs(y2 - y1) < 1e-6:
            y1, y2 = y1 - s["w"] / 2.0, y2 + s["w"] / 2.0
        if x1 <= 0.01: x1 -= 1.0
        if y1 <= 0.01: y1 -= 1.0
        if x2 >= pz.W - 0.01: x2 += 1.0
        if y2 >= pz.H - 0.01: y2 += 1.0
        za, zb = sorted((z0 - sg * 1.0, z0 + sg * s["prof"]))
        herr.append(caja(tbm, x1, x2, y1, y2, za, zb))
    for s in pz.sslots:
        zc = -pz.T + s["zpos"]                     # medido desde la cara +d (z=-T)
        za, zb = zc - s["w"] / 2.0, zc + s["w"] / 2.0
        x1, x2 = sorted((s["x1"], s["x2"]))
        y1, y2 = sorted((s["y1"], s["y2"]))
        if s["side"] in (2, 4):
            if x1 <= 0.01: x1 -= 1.0
            if x2 >= pz.W - 0.01: x2 += 1.0
            if s["side"] == 4:
                y1, y2 = -1.0, s["prof"]
            else:
                y1, y2 = pz.H - s["prof"], pz.H + 1.0
        else:
            if y1 <= 0.01: y1 -= 1.0
            if y2 >= pz.H - 0.01: y2 += 1.0
            if s["side"] == 1:
                x1, x2 = -1.0, s["prof"]
            else:
                x1, x2 = pz.W - s["prof"], pz.W + 1.0
        herr.append(caja(tbm, x1, x2, y1, y2, za, zb))
    n = resta(tbm, cuerpo, herr)
    if n != len(herr):
        log("  aviso: %s: %d de %d mecanizados fallaron" % (pz.nombre, len(herr) - n, len(herr)))
    return cuerpo


def marcar(cuerpo, pz):
    datos = {"TIPO": "PLACA", "NOMBRE": pz.plankName, "CODIGO": pz.codigo,
             "MATERIAL": pz.material, "TEXTURA": pz.textura,
             "VETA": "VERTICAL" if pz.texDir in ("normal", "", None) else "HORIZONTAL",
             "MUEBLE": pz.mueble, "ROL": pz.rol,
             "CANTO_ABAJO": pz.cantos["ABAJO"], "CANTO_ARRIBA": pz.cantos["ARRIBA"],
             "CANTO_IZQ": pz.cantos["IZQ"], "CANTO_DER": pz.cantos["DER"]}
    for k, v in datos.items():
        cuerpo.attributes.add(GRUPO, k, str(v))


# --------------------------------------------------------------------------- #
#  herrajes
# --------------------------------------------------------------------------- #

def _construir(design, comp, nombre, solidos, ap):
    if design.designType == adsk.fusion.DesignTypes.DirectDesignType:
        for s in solidos:
            comp.bRepBodies.add(s)
    else:
        base = comp.features.baseFeatures.add()
        base.startEdit()
        for s in solidos:
            comp.bRepBodies.add(s, base)
        base.finishEdit()
    cuerpos = [comp.bRepBodies.item(i) for i in range(comp.bRepBodies.count)]
    if len(cuerpos) > 1 and design.designType == adsk.fusion.DesignTypes.DirectDesignType:
        ci = comp.features.combineFeatures.createInput(cuerpos[0], adsk.core.ObjectCollection.create())
        for b in cuerpos[1:]:
            ci.toolBodies.add(b)
        ci.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        ci.isKeepToolBodies = False
        try:
            comp.features.combineFeatures.add(ci)
        except Exception:
            pass
    for i in range(comp.bRepBodies.count):
        b = comp.bRepBodies.item(i)
        b.name = nombre
        b.attributes.add(GRUPO, "TIPO", "HERRAJE")
        if ap is not None:
            try:
                b.appearance = ap
            except Exception:
                pass
    comp.attributes.add(GRUPO, "TIPO", "HERRAJE")


_HERRAJES = {}


def _archivo_biblioteca(nombre):
    """Devuelve el .step de herrajes/biblioteca que corresponde a `nombre`, o None.

    El indice esta en herrajes/biblioteca/indice.json. Se busca por prefijo para
    que "Bisagra O35 base -6" caiga en la misma pieza que "Bisagra O35 base -4".
    """
    try:
        with io.open(os.path.join(BIBLIOTECA, "indice.json"), encoding="utf-8") as f:
            idx = json.load(f)
    except Exception:
        return None
    for pref, arch in sorted(idx.get("por_prefijo", {}).items(), key=lambda t: -len(t[0])):
        if nombre.startswith(pref):
            ruta = os.path.join(BIBLIOTECA, arch)
            return ruta if os.path.exists(ruta) else None
    return None


def _importar_step(design, comp, ruta, ap):
    """Mete el STEP de la biblioteca adentro de `comp`, en su propio origen."""
    app = adsk.core.Application.get()
    im = app.importManager
    opts = im.createSTEPImportOptions(ruta)
    im.importToTarget(opts, comp)
    if ap is not None:
        for i in range(comp.occurrences.count):
            c = comp.occurrences.item(i).component
            for j in range(c.bRepBodies.count):
                try:
                    c.bRepBodies.item(j).appearance = ap
                except Exception:
                    pass
    try:
        comp.attributes.add(GRUPO, "TIPO", "HERRAJE")
    except Exception:
        pass


def herraje(design, padre, nombre, m, forma, ap, *args):
    """Ocurrencia del herraje `nombre` bajo `padre` con matriz `m`; lo modela la primera vez."""
    comp = _HERRAJES.get(nombre)
    if comp is None:
        comp = design.allComponents.itemByName(nombre)
        if comp is not None and comp.bRepBodies.count == 0 and comp.occurrences.count == 0:
            comp = None
    if comp is None:
        # OJO: addExistingComponent compone la matriz pedida con la de la PRIMERA
        # ocurrencia del componente. Por eso el original de cada herraje vive en
        # la biblioteca, en el origen y apagado; las instancias van con su matriz.
        lib = _biblioteca(design)
        occ0 = lib.component.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        comp = occ0.component
        comp.name = nombre
        ruta = _archivo_biblioteca(nombre)
        if ruta:
            _importar_step(design, comp, ruta, ap)
        else:
            tbm = adsk.fusion.TemporaryBRepManager.get()
            _construir(design, comp, nombre, forma(tbm, *args), ap)
        _HERRAJES[nombre] = comp
    # addExistingComponent compone la matriz con la de otra ocurrencia del mismo
    # componente (comportamiento observado en Fusion, 24/09/2026). Se pone la
    # matriz a mano despues de crear la ocurrencia.
    # `padre` es la OCURRENCIA del mueble (de primer nivel); la matriz solo se
    # puede fijar sobre el proxy de la ocurrencia en el contexto del root.
    occ = padre.component.occurrences.addExistingComponent(comp, adsk.core.Matrix3D.create())
    proxy = occ.createForAssemblyContext(padre)
    try:
        proxy.isGroundToParent = False
    except Exception:
        pass
    proxy.transform2 = m
    return proxy


def _biblioteca(design):
    root = design.rootComponent
    for i in range(root.occurrences.count):
        o = root.occurrences.item(i)
        if o.component.name == "Herrajes (biblioteca)":
            return o
    o = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    o.component.name = "Herrajes (biblioteca)"
    o.component.attributes.add(GRUPO, "TIPO", "HERRAJE")
    o.isLightBulbOn = False
    return o


def forma_corredera_bolas(tbm, largo):
    """Corredera telescopica de bolas, tres tramos, 45 mm de alto.

    Es la que usa la fabrica (verificada contra foto, 29/09/2026). Antes esto
    eran dos piezas dibujadas mal (un canal y una barra); ahora es una sola.

    Marco: origen en el FRENTE del riel sobre la cara del lateral, X hacia atras
    (a lo largo), Y arriba, Z hacia el hueco del cajon.
    """
    e = 1.2
    H = 22.5            # media altura -> 45 mm
    Z = 12.7            # espesor cerrada
    # miembro fijo (va atornillado al lateral del mueble)
    fijo = caja(tbm, 0, largo, -H, H, 0, e)
    une(tbm, fijo, [caja(tbm, 0, largo, H - e, H, 0, Z),
                    caja(tbm, 0, largo, -H, -H + e, 0, Z),
                    caja(tbm, 0, largo, H - e - 3.2, H - e, Z - e, Z),
                    caja(tbm, 0, largo, -H + e, -H + e + 3.2, Z - e, Z)])
    ags = [cil(tbm, (x, 0, -1), (x, 0, e + 1), 4.5)
           for x in (32.0, largo / 2.0, largo - 32.0)]
    for x in (70.0, largo - 70.0):
        ags.append(cil(tbm, (x, -6.0, -1), (x, -6.0, e + 1), 4.2))
        ags.append(cil(tbm, (x, 6.0, -1), (x, 6.0, e + 1), 4.2))
    resta(tbm, fijo, ags)
    # miembro intermedio
    H2 = H - 3.4
    medio = caja(tbm, 6, largo - 6, -H2, H2, 3.0, 3.0 + e)
    une(tbm, medio, [caja(tbm, 6, largo - 6, H2 - e, H2, 3.0, Z - 1.4),
                     caja(tbm, 6, largo - 6, -H2, -H2 + e, 3.0, Z - 1.4)])
    # miembro movil (va atornillado al costado del cajon)
    H3 = H - 6.6
    movil = caja(tbm, 0, largo, -H3, H3, 6.3, 6.3 + e)
    une(tbm, movil, [caja(tbm, 0, largo, H3 - e, H3, 2.2, 6.3 + e),
                     caja(tbm, 0, largo, -H3, -H3 + e, 2.2, 6.3 + e)])
    resta(tbm, movil, [cil(tbm, (x, 0, 5.0), (x, 0, 8.5), 4.2)
                       for x in (24.0, 140.0, 300.0, largo - 24.0)])
    cuerpos = [fijo, medio, movil]
    # bolas
    x = 24.0
    while x < largo * 0.42:
        for y in (H - 4.6, -(H - 4.6)):
            try:
                cuerpos.append(tbm.createSphere(p3(x, y, 7.8), 2.2 * MM))
            except Exception:
                pass
        x += 15.0
    return cuerpos


def forma_led(tbm, largo):
    """Perfil de aluminio 9x9 con difusor: origen en un extremo, X a lo largo, Z hacia adentro
    de la ranura."""
    perfil = caja(tbm, 0, largo, -4.3, 4.3, 0.2, 8.6)
    resta(tbm, perfil, [caja(tbm, -1, largo + 1, -3.3, 3.3, -1, 6.0)])
    difusor = caja(tbm, 0, largo, -3.4, 3.4, 0.4, 2.2)
    return [perfil, difusor]


def _apariencia_led(app, design):
    return apariencia_nombre(app, design, ["Plastic - Translucent Matte (White)", "Plastic - Glossy (White)"],
                             (250, 250, 240), "led")


# --------------------------------------------------------------------------- #
#  armado
# --------------------------------------------------------------------------- #

def _placas_con(piezas_hechas, sym):
    return [(pz, occ, h) for (pz, occ) in piezas_hechas for h in pz.holes if h["sym"] == sym]


def poner_3en1(design, padre, pz, occ, ap_metal, log):
    PH = _ph()
    m = occ.transform2
    herr = PH.HERRAJES["3EN1-33"]
    n = 0
    # pernos en los O8 de canto
    ejes = []
    for h in pz.sholes:
        if abs(h["d"] - 8.0) > 0.5:
            continue
        bx, by = boca_canto(pz, h["x"], h["y"], h["side"])
        dx, dy = dir_canto(h["side"])
        boca = transformar(m, (bx, by, -pz.T / 2.0))
        adentro = girar(m, (dx, dy, 0))
        herraje(design, padre, "Perno O8 x 33", marco(boca, adentro), PH._forma_perno, ap_metal,
                herr["perno"], herr["recibe"])
        ejes.append(((bx, by), (dx, dy)))
        n += 1
    for h in pz.holes:
        if h["sym"] != "3in1Lock":
            continue
        z0, sg = z_cara(pz, h["side"])
        boca = transformar(m, (h["x"], h["y"], z0))
        adentro = girar(m, (0, 0, sg))
        if abs(h["d"] - 15.0) < 0.5:
            # X de la excentrica = de donde viene el perno (el canto)
            pista = None
            for (b, dd) in ejes:
                t = (h["x"] - b[0]) * dd[0] + (h["y"] - b[1]) * dd[1]
                perp = abs((h["x"] - b[0]) * dd[1] - (h["y"] - b[1]) * dd[0])
                if 5 < t < 60 and perp < 1.5:
                    pista = dd
                    break
            if pista is None:
                cands = [(h["x"], (1, 0)), (pz.W - h["x"], (-1, 0)), (h["y"], (0, 1)), (pz.H - h["y"], (0, -1))]
                pista = min(cands)[1]
            herraje(design, padre, "Excentrica O15", marco(boca, adentro, girar(m, (pista[0], pista[1], 0))),
                    PH._forma_excentrica, ap_metal, herr["cam"])
            n += 1
        elif abs(h["d"] - 10.0) < 0.5:
            herraje(design, padre, "Receptor O10", marco(boca, adentro), PH._forma_receptor, ap_metal,
                    herr["recibe"])
            n += 1
    for h in pz.sholes:
        if abs(h["d"] - 10.0) > 0.5:
            continue
        bx, by = boca_canto(pz, h["x"], h["y"], h["side"])
        dx, dy = dir_canto(h["side"])
        boca = transformar(m, (bx, by, -pz.T / 2.0))
        herraje(design, padre, "Receptor O10", marco(boca, girar(m, (dx, dy, 0))), PH._forma_receptor,
                ap_metal, herr["recibe"])
        n += 1
    return n


def poner_bisagras(design, padre, pz, occ, hechas, ap_metal, log):
    """pz es una puerta. La base va sobre la placa que tenga jlHoleEX cerca de la cazoleta."""
    PH = _ph()
    m = occ.transform2
    bases = []
    for (q, oq) in hechas:
        if q is pz:
            continue
        for h in q.holes:
            if h["sym"] == "jlHoleEX":
                z0, sg = z_cara(q, h["side"])
                bases.append((transformar(oq.transform2, (h["x"], h["y"], z0)), girar(oq.transform2, (0, 0, sg))))
    n = 0
    for h in pz.holes:
        if h["sym"] != "HINGE":
            continue
        z0, sg = z_cara(pz, h["side"])
        centro = transformar(m, (h["x"], h["y"], z0))
        adentro = girar(m, (0, 0, sg))
        cands = [(h["x"], (1, 0)), (pz.W - h["x"], (-1, 0)), (h["y"], (0, 1)), (pz.H - h["y"], (0, -1))]
        pista = min(cands)[1]
        x_h = girar(m, (pista[0], pista[1], 0))
        dx_lat = -5.0
        mejor = None
        for (pb, nb) in bases:
            dist = math.sqrt(sum((pb[i] - centro[i]) ** 2 for i in range(3)))
            if dist < 120 and (mejor is None or dist < mejor[0]):
                mejor = (dist, pb, nb)
        if mejor is not None:
            pb = mejor[1]
            dx_lat = sum((pb[i] - centro[i]) * x_h[i] for i in range(3))
            if dx_lat > -1.0:
                dx_lat = -5.0
        herraje(design, padre, "Bisagra O35 base %g" % round(dx_lat, 1), marco(centro, adentro, x_h),
                PH._forma_bisagra, ap_metal, dx_lat)
        n += 1
    return n


def poner_correderas(design, padre, pz, occ, ap_metal, log):
    m = occ.transform2
    hs = [h for h in pz.holes if h["sym"] == "slideRail"]
    if len(hs) < 2:
        return 0
    n = 0
    # la corredera corre a lo largo de la profundidad del mueble (Y del mundo):
    # el eje local que mas se alinea con Y es el del riel
    a_lo_largo_de_x = abs(girar(m, (1, 0, 0))[1]) >= abs(girar(m, (0, 1, 0))[1])
    lineas = {}
    for h in hs:
        k = (h["side"], round(h["y"], 1) if a_lo_largo_de_x else round(h["x"], 1))
        lineas.setdefault(k, []).append(h)
    es_cajon = pz.mueble is not None and pz.nombre.lower().find("drawer panel") >= 0
    if es_cajon:
        # la corredera de bolas es UNA sola pieza que incluye los tres tramos:
        # se dibuja del lado del lateral, no otra vez del lado del cajon.
        return 0
    for (side, c), grupo in lineas.items():
        coords = sorted(set((g["x"] if a_lo_largo_de_x else g["y"]) for g in grupo))
        L = pz.W if a_lo_largo_de_x else pz.H
        largo = 450.0
        ini = max(0.0, min(coords) - 40.0)
        if ini + largo > L:
            ini = max(0.0, L - largo - 3.0)
        z0, sg = z_cara(pz, side)
        if a_lo_largo_de_x:
            p0 = (ini + largo, c, z0)       # frente del riel = el extremo cercano al frente
            along = (-1.0, 0.0, 0.0)
            arriba_local = (0.0, 1.0, 0.0)
        else:
            p0 = (c, ini + largo, z0)
            along = (0.0, -1.0, 0.0)
            arriba_local = (1.0, 0.0, 0.0)
        # el "frente" del riel es donde esta el frente del cajon: elegimos el extremo cuya
        # coordenada mundo Y (Fusion, frente = -Y) sea menor
        pa = transformar(m, p0)
        pb = transformar(m, (p0[0] + along[0] * largo, p0[1] + along[1] * largo, p0[2]))
        if pb[1] < pa[1]:
            pa, along = pb, esc(along, -1.0)
        ex = girar(m, along)
        ez = girar(m, (0, 0, -sg))            # hacia afuera de la placa (hacia el hueco)
        forma = forma_corredera_bolas
        nombre = "Corredera bolas %d" % int(round(largo))
        mm_ = marco(pa, ez, ex)
        herraje(design, padre, nombre, mm_, forma, ap_metal, largo)
        n += 1
    return n


def poner_led(design, padre, pz, occ, ap_led, log):
    m = occ.transform2
    n = 0
    for s in pz.slots:
        if s["sym"] != "lightSlot":
            continue
        z0, sg = z_cara(pz, s["side"])
        x1, x2 = sorted((s["x1"], s["x2"]))
        y1, y2 = sorted((s["y1"], s["y2"]))
        if abs(x2 - x1) < 1e-6:
            x1 = x2 = s["x1"]
            y1, y2 = max(0.0, y1), min(pz.H, y2)
            p0, along, largo = (x1, y1, z0), (0, 1, 0), y2 - y1
        else:
            x1, x2 = max(0.0, x1), min(pz.W, x2)
            p0, along, largo = (x1, y1, z0), (1, 0, 0), x2 - x1
        if largo < 20:
            continue
        herraje(design, padre, "Tira LED %d" % int(round(largo)), marco(transformar(m, p0), girar(m, (0, 0, sg)),
                girar(m, along)), forma_led, ap_led, largo)
        n += 1
    return n


def armar(ruta_json, modelos=None, nuevo=False, herrajes=True, log_print=True):
    app = adsk.core.Application.get()
    log = []

    def L(s):
        log.append(s)

    if nuevo:
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.DirectDesignType
        try:
            design.unitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
        except Exception:
            pass
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent
    muebles, d = leer_render(ruta_json, None, L)
    if modelos is not None:
        muebles = [mu for mu in muebles if mu["indice"] in modelos]
    ambiente = muebles[0]["piezas"][0].ambiente if muebles and muebles[0]["piezas"] else ""
    tbm = adsk.fusion.TemporaryBRepManager.get()
    _ph()
    ap_metal = _ph()._apariencia_metal()
    ap_led = _apariencia_led(app, design)
    total = dict(placas=0, herrajes=0)
    for mu in muebles:
        occ_m = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        comp_m = occ_m.component
        comp_m.name = mu["nombre"]
        comp_m.attributes.add(GRUPO, "MUEBLE", mu["nombre"])
        hechas = []
        for pz in mu["piezas"]:
            try:
                occ = comp_m.occurrences.addNewComponent(matriz(pz.origen, pz.ex, pz.ey))
                comp = occ.component
                comp.name = "%s %s" % (pz.nombre, pz.codigo)
                cuerpo_t = cuerpo_placa(tbm, pz, L)
                if design.designType == adsk.fusion.DesignTypes.DirectDesignType:
                    cuerpo = comp.bRepBodies.add(cuerpo_t)
                else:
                    base = comp.features.baseFeatures.add()
                    base.startEdit()
                    cuerpo = comp.bRepBodies.add(cuerpo_t, base)
                    base.finishEdit()
                    cuerpo = comp.bRepBodies.item(comp.bRepBodies.count - 1)
                cuerpo.name = pz.codigo or pz.nombre
                marcar(cuerpo, pz)
                ap = apariencia_textura(app, design, pz.textura)
                if ap is not None:
                    try:
                        cuerpo.appearance = ap
                    except Exception:
                        pass
                hechas.append((pz, occ))
                total["placas"] += 1
            except Exception:
                L("  ERROR en %s %s:\n%s" % (pz.nombre, pz.codigo, traceback.format_exc()))
        nh = 0
        if herrajes and DIBUJAR_HERRAJES:
            for (pz, occ) in hechas:
                try:
                    nh += poner_3en1(design, occ_m, pz, occ, ap_metal, L)
                    nh += poner_correderas(design, occ_m, pz, occ, ap_metal, L)
                    nh += poner_led(design, occ_m, pz, occ, ap_led, L)
                    if pz.es_puerta:
                        nh += poner_bisagras(design, occ_m, pz, occ, hechas, ap_metal, L)
                except Exception:
                    L("  ERROR herrajes en %s: %s" % (pz.nombre, traceback.format_exc()))
        total["herrajes"] += nh
        L("%-40s %3d placas  %4d herrajes" % (mu["nombre"], len(hechas), nh))
    for k, v in {"ORDEN": str(d.get("orderId", "")), "AMBIENTE": ambiente,
                 "EJE_ARRIBA": "+Z", "EJE_FRENTE": "-Y"}.items():
        root.attributes.add(GRUPO, k, v)
    L("TOTAL: %d placas, %d herrajes" % (total["placas"], total["herrajes"]))
    if log_print:
        print("\n".join(log))
    return log


def run(context=None):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        dlg = ui.createFileDialog()
        dlg.title = "Elegir el render.json de GuiGui"
        dlg.filter = "JSON (*.json)"
        if dlg.showOpen() != adsk.core.DialogResults.DialogOK:
            return
        log = armar(dlg.filename, nuevo=False, log_print=False)
        ui.messageBox("\n".join(log[-20:]), "Armar desde render")
    except Exception:
        if ui:
            ui.messageBox("Fallo:\n%s" % traceback.format_exc(), "Armar desde render")


def rehacer_correderas(ruta_json, log_print=True):
    """Borra las correderas puestas y las vuelve a poner (para corregir sin rearmar)."""
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent
    log = []
    borradas = 0
    for i in range(root.allOccurrences.count - 1, -1, -1):
        o = root.allOccurrences.item(i)
        if o.component.name.startswith("Corredera") and not o.fullPathName.startswith("Herrajes"):
            o.deleteMe()
            borradas += 1
    muebles, d = leer_render(ruta_json, None, None)
    ap_metal = _ph()._apariencia_metal()
    n = 0
    for mu in muebles:
        occ_m = None
        for i in range(root.occurrences.count):
            if root.occurrences.item(i).component.name == mu["nombre"]:
                occ_m = root.occurrences.item(i)
        if occ_m is None:
            continue
        for pz in mu["piezas"]:
            nombre = "%s %s" % (pz.nombre, pz.codigo)
            for i in range(occ_m.childOccurrences.count):
                o = occ_m.childOccurrences.item(i)
                if o.component.name == nombre:
                    n += poner_correderas(design, occ_m, pz, o, ap_metal, log.append)
                    break
    log.append("correderas borradas %d, puestas %d" % (borradas, n))
    if log_print:
        print("\n".join(log))
    return log
