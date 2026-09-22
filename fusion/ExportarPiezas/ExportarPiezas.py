# -*- coding: utf-8 -*-
"""
Exportar Piezas — script de Autodesk Fusion para FABRICA MUEBLES.

Recorre el diseno abierto, reconoce las placas y exporta `piezas.json`, el
esquema neutro que despues consume el generador de `etapa2/` para producir
.ban / .mpr / XML1 / XML3 / lista de corte.

COMO LEE LA GEOMETRIA
---------------------
No lee el arbol de operaciones: lee el SOLIDO. Busca caras cilindricas
(agujeros) y caras planas intermedias (ranuras). Por eso no importa como
modelaste el agujero — con la herramienta Agujero, con un corte extruido o
con lo que sea.

    cilindro completo, eje en Z         ->  agujero vertical
    cilindro completo, eje en el plano  ->  agujero horizontal (por el canto)
    cilindro parcial                    ->  redondeo del contorno, se ignora
    cara plana entre las dos caras      ->  fondo de ranura

MARCO DE COORDENADAS
--------------------
El marco de la PIEZA (no el del ensamble). Se toma la caja envolvente del
cuerpo: el espesor es la dimension menor, la cara A es la de Z mayor, y el
origen queda en la esquina inferior izquierda. Eso coincide exactamente con el
marco del archivo de maquina, asi que no hay ninguna conversion que pueda
salir espejada.

Si algo no sale como esperabas, mira `diagnostico.txt`: registra cada cara que
examino y por que la clasifico asi.
"""

import json
import math
import os
import traceback

import adsk.core
import adsk.fusion

GRUPO_ATTR = "FabricaMuebles"
CM_A_MM = 10.0

# Carpeta del generador. Se puede pisar con el atributo RUTA_ETAPA2 del mueble.
RUTA_ETAPA2 = os.path.expanduser(
    "~/Documents/Claude/Projects/FABRICA MUEBLES/etapa2")

TOL = 0.05          # mm — tolerancia general
R_MAX_AGUJERO = 40.0  # mm — radio por encima del cual no se considera agujero
COMPLETITUD_MIN = 0.55  # fraccion de cilindro completo para contar como agujero
RANURA_ASPECTO_MIN = 2.0   # largo / ancho minimo de una ranura
RANURA_LARGO_MIN = 20.0    # mm

# Profundidad real del agujero de canto segun diametro.
#
# POR QUE HACE FALTA: cuando la varilla de un tres-en-uno desemboca en la
# excentrica O15, el solido terminado YA NO GUARDA la profundidad con la que se
# taladro — la cara cilindrica queda cortada por el otro agujero. La geometria
# sola no puede recuperar ese dato. Como el vocabulario de herrajes es fijo, se
# resuelve con esta tabla: si lo medido es MENOR que lo de tabla, se usa tabla y
# queda anotado en el diagnostico. Si es mayor o no hay entrada, manda lo medido.
# Cuando el O8 desemboca en el O15, el B-Rep solo ve el pedazo de cilindro que
# quedo, y mide de menos. Hay que completarlo con el dato del herraje.
#
# OJO: NO es un numero universal. Los dos pedidos de referencia usan herrajes
# distintos — PRUEBA 1 lleva perno de 33 y el de muestra de 34. Por eso lo
# primero que se mira es el atributo PROF_CANTO_<diametro> que deja
# PonerHerrajes en la pieza; la tabla es solo el ultimo recurso.
PROFUNDIDAD_CANTO = {8.0: 33.0}
TOL_DIAMETRO = 0.3

_log = []


def log(msg):
    _log.append(str(msg))


# --------------------------------------------------------------------------- #
#  utilidades de geometria
# --------------------------------------------------------------------------- #

def mm(v):
    return v * CM_A_MM


def attr(objeto, nombre, defecto=""):
    try:
        a = objeto.attributes.itemByName(GRUPO_ATTR, nombre)
        return a.value if a and a.value not in (None, "") else defecto
    except Exception:
        return defecto


def attr2(body, comp, nombre, defecto=""):
    """Los datos pueden estar en el CUERPO o en el COMPONENTE; gana el cuerpo.

    Asi un documento con varias placas como cuerpos sueltos funciona igual que
    uno con un componente por placa."""
    v = attr(body, nombre, "")
    return v if v not in (None, "") else attr(comp, nombre, defecto)


def num(v, defecto=0.0):
    try:
        return float(str(v).replace(",", "."))
    except (TypeError, ValueError):
        return defecto


class Marco(object):
    """Convierte del espacio del componente al marco de la pieza."""

    def __init__(self, bbox):
        p0, p1 = bbox.minPoint, bbox.maxPoint
        dx, dy, dz = mm(p1.x - p0.x), mm(p1.y - p0.y), mm(p1.z - p0.z)
        self.espesor = min(dx, dy, dz)
        if self.espesor != dz:
            raise ValueError(
                "el espesor no esta sobre Z (medidas %.1f x %.1f x %.1f). "
                "La placa tiene que estar acostada: boceto en XY, extruir en Z."
                % (dx, dy, dz))
        self.ancho, self.alto = dx, dy
        self.x0, self.y0 = mm(p0.x), mm(p0.y)
        self.z_cara_a = mm(p1.z)          # cara A = Z mayor

    def x(self, vx):
        return mm(vx) - self.x0

    def y(self, vy):
        return mm(vy) - self.y0

    def z(self, vz):
        """0 en la cara A, negativo hacia adentro."""
        return mm(vz) - self.z_cara_a

    def canto_de(self, x, y):
        if abs(x) <= 0.6:
            return "L"
        if abs(x - self.ancho) <= 0.6:
            return "R"
        if abs(y) <= 0.6:
            return "D"
        if abs(y - self.alto) <= 0.6:
            return "U"
        return None


def eje_principal(v):
    """Devuelve 'Z' si el vector es paralelo a Z, 'XY' si esta en el plano, si no None."""
    n = math.sqrt(v.x ** 2 + v.y ** 2 + v.z ** 2)
    if n == 0:
        return None
    x, y, z = abs(v.x) / n, abs(v.y) / n, abs(v.z) / n
    if z > 0.999:
        return "Z"
    if z < 0.001:
        return "XY"
    return None


# --------------------------------------------------------------------------- #
#  reconocimiento de operaciones
# --------------------------------------------------------------------------- #

def leer_agujeros(body, marco):
    verticales, horizontales = [], []
    for i in range(body.faces.count):
        face = body.faces.item(i)
        geo = face.geometry
        if geo.surfaceType != adsk.core.SurfaceTypes.CylinderSurfaceType:
            continue
        cyl = adsk.core.Cylinder.cast(geo)
        if cyl is None:
            continue
        radio = mm(cyl.radius)
        bb = face.boundingBox
        eje = eje_principal(cyl.axis)

        if radio > R_MAX_AGUJERO:
            log("  cilindro R=%.1f ignorado: radio mayor a %.0f" % (radio, R_MAX_AGUJERO))
            continue
        if eje is None:
            log("  cilindro R=%.1f ignorado: eje oblicuo" % radio)
            continue

        # alto del cilindro sobre su eje
        if eje == "Z":
            alto = mm(bb.maxPoint.z - bb.minPoint.z)
        else:
            ax, ay = abs(cyl.axis.x), abs(cyl.axis.y)
            alto = (mm(bb.maxPoint.x - bb.minPoint.x) if ax > ay
                    else mm(bb.maxPoint.y - bb.minPoint.y))
        if alto <= TOL:
            continue

        # un agujero es un cilindro (casi) completo; un redondeo de esquina no
        area_completa = 2 * math.pi * radio * alto
        completitud = (mm(mm(face.area)) / area_completa) if area_completa > 0 else 0.0
        if completitud < COMPLETITUD_MIN:
            log("  cilindro R=%.1f alto=%.1f ignorado: %.0f%% de cilindro (redondeo)"
                % (radio, alto, completitud * 100))
            continue

        if eje == "Z":
            x, y = marco.x(cyl.origin.x), marco.y(cyl.origin.y)
            z_sup, z_inf = marco.z(bb.maxPoint.z), marco.z(bb.minPoint.z)
            # cara A si el agujero arranca arriba; cara B si arranca abajo
            if abs(z_sup) <= TOL:
                cara, prof = "A", abs(z_inf)
            elif abs(z_inf + marco.espesor) <= TOL:
                cara, prof = "B", abs(z_sup + marco.espesor)
            else:
                log("  cilindro vertical R=%.1f en z=[%.2f,%.2f] ignorado: "
                    "no arranca en ninguna cara" % (radio, z_inf, z_sup))
                continue
            verticales.append({"x": round(x, 2), "y": round(y, 2),
                               "diametro": round(radio * 2, 2),
                               "profundidad": round(prof, 2), "cara": cara})
            log("  agujero vertical  O%.1f prof %.1f  cara %s  en (%.1f, %.1f)"
                % (radio * 2, prof, cara, x, y))
        else:
            # extremos del eje dentro de la caja de la cara
            if abs(cyl.axis.x) > abs(cyl.axis.y):
                p_a = (marco.x(bb.minPoint.x), marco.y(cyl.origin.y))
                p_b = (marco.x(bb.maxPoint.x), marco.y(cyl.origin.y))
            else:
                p_a = (marco.x(cyl.origin.x), marco.y(bb.minPoint.y))
                p_b = (marco.x(cyl.origin.x), marco.y(bb.maxPoint.y))
            canto_a = marco.canto_de(*p_a)
            canto_b = marco.canto_de(*p_b)
            if canto_a and not canto_b:
                entrada, canto = p_a, canto_a
            elif canto_b and not canto_a:
                entrada, canto = p_b, canto_b
            elif canto_a and canto_b:
                log("  cilindro horizontal R=%.1f ignorado: pasante de canto a canto "
                    "(no soportado todavia)" % radio)
                continue
            else:
                log("  cilindro horizontal R=%.1f ignorado: no toca ningun canto" % radio)
                continue
            z = -marco.z(cyl.origin.z)
            diam = radio * 2
            prof = alto
            marcada = num(attr(body, "PROF_CANTO_%g" % round(diam, 1), 0))
            if marcada and alto < marcada - 0.1:
                log("  (O%.1f: medido %.1f, se usa %.1f del herraje puesto en "
                    "esta pieza — el agujero desemboca en otro)"
                    % (diam, alto, marcada))
                prof = marcada
            else:
                for d_tabla, p_tabla in PROFUNDIDAD_CANTO.items():
                    if abs(diam - d_tabla) <= TOL_DIAMETRO and alto < p_tabla - 0.1:
                        prof = p_tabla
                    log("  (O%.1f: medido %.1f, se usa %.1f de tabla — el agujero "
                        "desemboca en otro)" % (diam, alto, p_tabla))
                    break
            horizontales.append({"x": round(entrada[0], 2), "y": round(entrada[1], 2),
                                 "z": round(z, 2), "diametro": round(diam, 2),
                                 "profundidad": round(prof, 2), "canto": canto})
            log("  agujero de canto  O%.1f prof %.1f  canto %s  en (%.1f, %.1f) z=%.1f"
                % (diam, prof, canto, entrada[0], entrada[1], z))
    return verticales, horizontales


# --------------------------------------------------------------------------- #
#  contorno de la pieza
# --------------------------------------------------------------------------- #

def _cara_horizontal_en(face, marco, z_obj):
    """True si la cara es plana y horizontal a la altura z_obj del marco."""
    if face.geometry.surfaceType != adsk.core.SurfaceTypes.PlaneSurfaceType:
        return False
    bb = face.boundingBox
    return (abs(marco.z(bb.maxPoint.z) - z_obj) <= TOL and
            abs(marco.z(bb.minPoint.z) - z_obj) <= TOL)


def _norm_ang(d):
    while d > math.pi:
        d -= 2 * math.pi
    while d <= -math.pi:
        d += 2 * math.pi
    return d


def _barrido(edge, centro, pa, pb):
    """Angulo barrido por el arco, con signo (+ = antihorario), en grados.

    Se pasa por el punto MEDIO del arco para no confundir un arco de mas de
    media vuelta con el complementario.
    """
    def ang(p):
        return math.atan2(p.y - centro.y, p.x - centro.x)
    ev = edge.evaluator
    ok, t0, t1 = ev.getParameterExtents()
    if not ok:
        return 0.0
    ok, pm = ev.getPointAtParameter((t0 + t1) / 2.0)
    if not ok:
        return 0.0
    a0, am, a1 = ang(pa), ang(pm), ang(pb)
    return math.degrees(_norm_ang(am - a0) + _norm_ang(a1 - am))


def _area_con_signo(verts):
    a = 0.0
    for i in range(len(verts)):
        x1, y1 = verts[i]["x"], verts[i]["y"]
        x2, y2 = verts[(i + 1) % len(verts)]["x"], verts[(i + 1) % len(verts)]["y"]
        a += x1 * y2 - x2 * y1
    return a / 2.0


def _es_rectangulo(verts, marco):
    """True si el contorno es el rectangulo completo del bounding box."""
    if len(verts) != 4 or any(abs(v["arco"]) > 0.01 for v in verts):
        return False
    esperados = [(0.0, 0.0), (marco.ancho, 0.0),
                 (marco.ancho, marco.alto), (0.0, marco.alto)]
    for ex, ey in esperados:
        if not any(abs(v["x"] - ex) <= TOL and abs(v["y"] - ey) <= TOL for v in verts):
            return False
    return True


def _loop_de_cara(body, marco, z_obj):
    """Contorno del borde exterior de la cara horizontal que esta en z_obj."""
    cara, area = None, -1.0
    for i in range(body.faces.count):
        f = body.faces.item(i)
        if _cara_horizontal_en(f, marco, z_obj) and f.area > area:
            cara, area = f, f.area
    if cara is None:
        return None

    loop = None
    for i in range(cara.loops.count):
        if cara.loops.item(i).isOuter:
            loop = cara.loops.item(i)
    if loop is None:
        return None

    verts = []
    for i in range(loop.coEdges.count):
        ce = loop.coEdges.item(i)
        e = ce.edge
        pa, pb = e.startVertex.geometry, e.endVertex.geometry
        if ce.isOpposedToEdge:
            pa, pb = pb, pa
        g = e.geometry
        tipo = g.objectType
        if pa.distanceTo(pb) < 0.0005 and tipo == adsk.core.Line3D.classType():
            continue                                  # arista degenerada
        arco = 0.0
        if tipo in (adsk.core.Arc3D.classType(), adsk.core.Circle3D.classType()):
            arco = _barrido(e, g.center, pa, pb)
        elif tipo != adsk.core.Line3D.classType():
            log("  contorno: arista de tipo %s aproximada por una recta" % tipo)
        verts.append({"x": round(marco.x(pb.x), 2), "y": round(marco.y(pb.y), 2),
                      "arco": round(arco, 3)})

    if len(verts) < 3:
        return None
    # el generador espera el contorno en sentido ANTIHORARIO
    if _area_con_signo(verts) < 0:
        verts = list(reversed(verts))
        arcos = [v["arco"] for v in verts]
        for i, v in enumerate(verts):
            v["arco"] = -arcos[(i + 1) % len(verts)]
    return verts


def leer_contorno(body, marco):
    """Contorno de la pieza: la SILUETA, no el borde de una cara.

    No alcanza con mirar la cara A. Una ranura que llega hasta el borde le abre
    un golfo al contorno de esa cara, y si la cruza entera se lo parte en dos.
    En una placa ya validada eso daba un contorno 30 mm mas angosto que la
    pieza. Por eso se leen LAS DOS caras y gana la de mayor area, que es la que
    no esta comida por la ranura.

    Devuelve [] si la pieza es un rectangulo liso: en ese caso el generador usa
    el rectangulo del bounding box y el archivo sale igual que siempre.
    """
    cand = [v for v in (_loop_de_cara(body, marco, 0.0),
                        _loop_de_cara(body, marco, -marco.espesor)) if v]
    if not cand:
        log("  sin cara plana horizontal: no se puede leer el contorno")
        return []
    if len(cand) == 2:
        aa, ab = abs(_area_con_signo(cand[0])), abs(_area_con_signo(cand[1]))
        if abs(aa - ab) > 1.0:
            log("  contorno: las dos caras difieren (%.1f vs %.1f mm2); "
                "se usa la mayor" % (aa, ab))
    verts = max(cand, key=lambda v: abs(_area_con_signo(v)))

    # Red de seguridad: la silueta tiene que ocupar todo el bounding box. Si no,
    # las dos caras estan comidas y el contorno leido seria mas chico que la
    # pieza. Antes de mandar eso a la sierra, se avisa y se deja el rectangulo.
    xs = [v["x"] for v in verts]
    ys = [v["y"] for v in verts]
    if (abs(min(xs)) > TOL or abs(max(xs) - marco.ancho) > TOL or
            abs(min(ys)) > TOL or abs(max(ys) - marco.alto) > TOL):
        log("  !! CONTORNO SOSPECHOSO: ocupa x %.1f..%.1f  y %.1f..%.1f "
            "pero la pieza mide %.1f x %.1f. No se exporta el contorno."
            % (min(xs), max(xs), min(ys), max(ys), marco.ancho, marco.alto))
        return []

    if _es_rectangulo(verts, marco):
        return []

    rectas = sum(1 for v in verts if abs(v["arco"]) <= 0.01)
    log("  contorno irregular: %d vertices (%d rectas, %d arcos)"
        % (len(verts), rectas, len(verts) - rectas))
    for v in verts:
        log("    (%.2f, %.2f)%s" % (v["x"], v["y"],
                                    "  arco %.2f grados" % v["arco"] if v["arco"] else ""))
    return verts


def _material_arriba(body, punto_cm, eps_cm=0.02):
    """True si hay material justo por encima del punto (o None si no se puede saber)."""
    try:
        p = adsk.core.Point3D.create(punto_cm.x, punto_cm.y, punto_cm.z + eps_cm)
        cont = body.pointContainment(p)
        return cont == adsk.fusion.PointContainment.PointInsidePointContainment
    except Exception:
        return None


def _solapan(a, b):
    """Fraccion de solape en XY entre dos bounding boxes, respecto de la menor."""
    ix = min(a[2], b[2]) - max(a[0], b[0])
    iy = min(a[3], b[3]) - max(a[1], b[1])
    if ix <= 0 or iy <= 0:
        return 0.0
    inter = ix * iy
    aa = (a[2] - a[0]) * (a[3] - a[1])
    ab = (b[2] - b[0]) * (b[3] - b[1])
    menor = min(aa, ab)
    return inter / menor if menor > 0 else 0.0


def leer_ranuras(body, marco):
    """Ranuras de CARA y ranuras de CANTO.

    Una ranura de cara deja UNA cara plana horizontal intermedia (su fondo).
    Una ranura de canto deja DOS, enfrentadas: el piso y el techo del canal.
    Si no se distinguen, un canal de 6 mm en el canto se lee como dos ranuras
    de 12 mm, una por cara — y la maquina fresa las dos caras. Por eso se
    emparejan antes de decidir.
    """
    candidatas, ranuras_canto_out = [], []
    for i in range(body.faces.count):
        face = body.faces.item(i)
        if face.geometry.surfaceType != adsk.core.SurfaceTypes.PlaneSurfaceType:
            continue
        bb = face.boundingBox
        zt, zb = marco.z(bb.maxPoint.z), marco.z(bb.minPoint.z)
        if abs(zt - zb) > TOL:
            continue                      # no es horizontal
        z = zt
        if abs(z) <= TOL or abs(z + marco.espesor) <= TOL:
            continue                      # es la cara A o la cara B de la placa
        dx = mm(bb.maxPoint.x - bb.minPoint.x)
        dy = mm(bb.maxPoint.y - bb.minPoint.y)
        largo, ancho = max(dx, dy), min(dx, dy)
        if ancho <= TOL or largo < RANURA_LARGO_MIN or largo / ancho < RANURA_ASPECTO_MIN:
            log("  cara plana en z=%.2f de %.1f x %.1f ignorada: no parece ranura"
                % (z, dx, dy))
            continue
        candidatas.append({
            "z": z, "dx": dx, "dy": dy, "largo": largo, "ancho": ancho,
            "caja": (marco.x(bb.minPoint.x), marco.y(bb.minPoint.y),
                     marco.x(bb.maxPoint.x), marco.y(bb.maxPoint.y)),
            "arriba": _material_arriba(body, face.pointOnFace)})

    # --- emparejar piso y techo de un mismo canal de canto ---
    ranuras, cantos, usadas = [], [], set()
    for i in range(len(candidatas)):
        if i in usadas:
            continue
        a = candidatas[i]
        for j in range(i + 1, len(candidatas)):
            if j in usadas:
                continue
            b = candidatas[j]
            bajo, alto = (a, b) if a["z"] < b["z"] else (b, a)
            # el piso tiene material abajo (hueco arriba) y el techo al reves
            if bajo["arriba"] is not False or alto["arriba"] is not True:
                continue
            if _solapan(a["caja"], b["caja"]) < 0.8:
                continue
            cantos.append((bajo, alto))
            usadas.add(i)
            usadas.add(j)
            break

    for bajo, alto in cantos:
        x0, y0, x1, y1 = bajo["caja"]
        ancho_canal = round(alto["z"] - bajo["z"], 2)     # espesor del canal, en Z
        # sobre que canto desemboca
        canto = None
        if abs(x0) <= 0.6:
            canto, prof = "L", x1 - x0
        elif abs(x1 - marco.ancho) <= 0.6:
            canto, prof = "R", x1 - x0
        elif abs(y0) <= 0.6:
            canto, prof = "D", y1 - y0
        elif abs(y1 - marco.alto) <= 0.6:
            canto, prof = "U", y1 - y0
        if canto is None:
            log("  CANAL INTERNO en z=%.2f..%.2f: no desemboca en ningun canto. "
                "No se exporta." % (bajo["z"], alto["z"]))
            continue
        if canto in ("L", "R"):
            eje = (y0 + y1) / 2.0
            p1, p2 = (x0 if canto == "L" else x1, y0), (x0 if canto == "L" else x1, y1)
            recorrido = y1 - y0
            p1, p2 = (p1[0], y0), (p2[0], y1)
        else:
            p1, p2 = (x0, y0 if canto == "D" else y1), (x1, y0 if canto == "D" else y1)
            recorrido = x1 - x0
        cantos_datos = {
            "canto": canto,
            "x1": round(p1[0], 2), "y1": round(p1[1], 2),
            "x2": round(p2[0], 2), "y2": round(p2[1], 2),
            "ancho": ancho_canal,
            "profundidad": round(prof, 2),
            "z_desde_b": round(marco.espesor + bajo["z"], 2),
            "largo": round(recorrido, 2)}
        ranuras_canto_out.append(cantos_datos)
        log("  RANURA DE CANTO en %s: %.1f de ancho x %.1f de profundidad, "
            "a %.1f de la cara B, corre %.1f mm"
            % (canto, ancho_canal, prof, cantos_datos["z_desde_b"], recorrido))

    # --- lo que queda son ranuras de cara ---
    for i, c in enumerate(candidatas):
        if i in usadas:
            continue
        z = c["z"]
        if c["arriba"] is None:
            cara = "A" if (marco.espesor + z) > abs(z) else "B"
            log("  (sin test de contencion; cara deducida por profundidad)")
        else:
            cara = "B" if c["arriba"] else "A"
        prof = abs(z) if cara == "A" else abs(marco.espesor + z)
        x0, y0, x1, y1 = c["caja"]
        if c["dx"] >= c["dy"]:
            ejey = (y0 + y1) / 2.0
            p1, p2 = (x0, ejey), (x1, ejey)
        else:
            ejex = (x0 + x1) / 2.0
            p1, p2 = (ejex, y0), (ejex, y1)
        ranuras.append({"x1": round(p1[0], 2), "y1": round(p1[1], 2),
                        "x2": round(p2[0], 2), "y2": round(p2[1], 2),
                        "ancho": round(c["ancho"], 2), "profundidad": round(prof, 2),
                        "cara": cara})
        log("  ranura %.1f x %.1f  cara %s  de (%.1f, %.1f) a (%.1f, %.1f)"
            % (c["ancho"], prof, cara, p1[0], p1[1], p2[0], p2[1]))
    return ranuras, ranuras_canto_out


# --------------------------------------------------------------------------- #
#  recorrido del diseno
# --------------------------------------------------------------------------- #

def es_placa(objeto):
    t = str(attr(objeto, "TIPO", "")).strip().upper()
    if t:
        return t == "PLACA"
    return None      # sin marcar: se decide por la geometria


def pieza_de(body, comp, cantidad, solo_del_cuerpo=False):
    marco = Marco(body.boundingBox)
    verticales, horizontales = leer_agujeros(body, marco)
    ranuras, ranuras_canto = leer_ranuras(body, marco)
    contorno = leer_contorno(body, marco)
    # Con varios cuerpos en el mismo componente, el codigo y el nombre TIENEN que
    # salir del cuerpo: heredarlos del componente daria el mismo codigo a todos.
    ident = (lambda n, d="": str(attr(body, n, d))) if solo_del_cuerpo else \
            (lambda n, d="": str(attr2(body, comp, n, d)))
    return {
        "codigo": ident("CODIGO"),
        "nombre": ident("NOMBRE") or body.name,
        "ancho": round(marco.ancho, 2),
        "alto": round(marco.alto, 2),
        "espesor": round(marco.espesor, 2),
        "material": str(attr2(body, comp, "MATERIAL", "")),
        "mueble": str(attr2(body, comp, "MUEBLE", "")),
        "textura": str(attr2(body, comp, "TEXTURA", "")),
        "veta": str(attr2(body, comp, "VETA", "VERTICAL")).upper(),
        "cantidad": cantidad,
        "canto_abajo": num(attr2(body, comp, "CANTO_ABAJO", 0)),
        "canto_arriba": num(attr2(body, comp, "CANTO_ARRIBA", 0)),
        "canto_izq": num(attr2(body, comp, "CANTO_IZQ", 0)),
        "canto_der": num(attr2(body, comp, "CANTO_DER", 0)),
        "agujeros": verticales,
        "agujeros_canto": horizontales,
        "ranuras": ranuras,
        "ranuras_canto": ranuras_canto,
        "contorno": contorno,
    }


def hay_marcados(design):
    """True si algun cuerpo del diseno esta marcado TIPO=PLACA."""
    root = design.rootComponent
    comps = [root] + [root.allOccurrences.item(i).component
                      for i in range(root.allOccurrences.count)]
    for comp in comps:
        for j in range(comp.bRepBodies.count):
            if str(attr(comp.bRepBodies.item(j), "TIPO", "")).strip().upper() == "PLACA":
                return True
    return False


def recolectar(design):
    root = design.rootComponent
    piezas, saltadas = [], []
    # Si hay cuerpos marcados a proposito, se ignora todo lo demas. Evita que
    # cuerpos sueltos (herramientas de corte, restos) entren como placas.
    solo_marcados = hay_marcados(design)

    cantidades = {}
    for i in range(root.allOccurrences.count):
        occ = root.allOccurrences.item(i)
        if occ.isLightBulbOn:
            cantidades[occ.component.id] = cantidades.get(occ.component.id, 0) + 1

    vistos = set()
    componentes = [(root, 1)]
    for i in range(root.allOccurrences.count):
        c = root.allOccurrences.item(i).component
        if c.id not in vistos:
            vistos.add(c.id)
            componentes.append((c, cantidades.get(c.id, 1)))

    for comp, cantidad in componentes:
        marcado = es_placa(comp)
        if marcado is False:
            saltadas.append("%s — marcada TIPO distinto de PLACA" % comp.name)
            continue
        for j in range(comp.bRepBodies.count):
            body = comp.bRepBodies.item(j)
            if not body.isSolid or not body.isVisible:
                continue
            marca = es_placa(body)
            if marca is False or (solo_marcados and marca is not True):
                saltadas.append("%s / %s — no esta marcado como PLACA"
                                % (comp.name, body.name))
                continue
            log("")
            log("=== %s / %s ===" % (comp.name, body.name))
            try:
                piezas.append(pieza_de(body, comp, cantidad,
                                       solo_del_cuerpo=comp.bRepBodies.count > 1))
            except ValueError as e:
                saltadas.append("%s / %s — %s" % (comp.name, body.name, e))
                log("  SALTADA: %s" % e)
            except Exception as e:
                saltadas.append("%s / %s — error: %s" % (comp.name, body.name, e))
                log("  ERROR: %s" % traceback.format_exc())
    return piezas, saltadas


def escribir_lanzador(carpeta, etapa2):
    """Deja un .command para doble clic, con las rutas ya resueltas."""
    guion = """#!/bin/bash
# Generado por ExportarPiezas. Doble clic para producir los archivos de maquina.
cd "%s" || { echo "No encuentro el generador en %s"; read -n1; exit 1; }
SALIDA="%s/salida"
python3 exportar.py "%s/piezas.json" -o "$SALIDA" || { read -n1; exit 1; }
python3 listacorte.py "%s/piezas.json" -o "$SALIDA"
python3 hojas.py "%s/piezas.json" -o "$SALIDA/HOJAS_VERIFICACION.html"
echo
echo "Listo. Todo en: $SALIDA"
open "$SALIDA"
echo "Apreta una tecla para cerrar."
read -n1
""" % (etapa2, etapa2, carpeta, carpeta, carpeta, carpeta)
    ruta = os.path.join(carpeta, "GENERAR ARCHIVOS.command")
    with open(ruta, "w") as fh:
        fh.write(guion)
    try:
        os.chmod(ruta, 0o755)
    except Exception:
        pass
    log("lanzador escrito: %s  (generador en %s)" % (ruta, etapa2))


# --------------------------------------------------------------------------- #

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox("Abri un diseno de Fusion antes de correr el script.")
            return

        dlg = ui.createFolderDialog()
        dlg.title = "Donde guardo piezas.json"
        if dlg.showDialog() != adsk.core.DialogResults.DialogOK:
            return
        carpeta = dlg.folder

        del _log[:]
        log("Exportar Piezas — %s" % design.parentDocument.name)
        piezas, saltadas = recolectar(design)

        # Red de seguridad: dos placas con el mismo codigo de barras mandarian
        # el programa equivocado a la maquina. Se avisa fuerte y no se exporta.
        vistos = {}
        duplicados = []
        for p in piezas:
            c = p["codigo"]
            if not c:
                continue
            if c in vistos:
                duplicados.append("%s  (%s  y  %s)" % (c, vistos[c], p["nombre"]))
            else:
                vistos[c] = p["nombre"]
        if duplicados:
            log("")
            log("CODIGOS DE BARRAS REPETIDOS:")
            for d in duplicados:
                log("  " + d)
            with open(os.path.join(carpeta, "diagnostico.txt"), "w") as fh:
                fh.write("\n".join(_log))
            ui.messageBox(
                "No exporto: hay codigos de barras repetidos.\n\n  %s\n\n"
                "Dos placas con el mismo codigo hacen que la perforadora tome el "
                "programa equivocado.\n\nLo mas probable es que el documento tenga "
                "cuerpos de una corrida anterior. Proba en un documento nuevo y "
                "vacio.\n\nEl detalle esta en diagnostico.txt"
                % "\n  ".join(duplicados), "Exportar Piezas")
            return

        datos = {
            "version": 1,
            "origen": "fusion",
            "documento": design.parentDocument.name,
            "orden": str(attr(design.rootComponent, "ORDEN", "")),
            "cliente": str(attr(design.rootComponent, "CLIENTE", "")),
            "direccion": str(attr(design.rootComponent, "DIRECCION", "")
                             or attr(design.rootComponent, "PROYECTO", "")),
            "ambiente": str(attr(design.rootComponent, "AMBIENTE", "")),
            "piezas": piezas,
        }
        ruta = os.path.join(carpeta, "piezas.json")
        with open(ruta, "w") as fh:
            json.dump(datos, fh, ensure_ascii=False, indent=2)

        etapa2 = str(attr(design.rootComponent, "RUTA_ETAPA2", "")) or RUTA_ETAPA2
        escribir_lanzador(carpeta, etapa2)

        log("")
        log("%d piezas exportadas" % len(piezas))
        for s in saltadas:
            log("SALTADA: %s" % s)
        with open(os.path.join(carpeta, "diagnostico.txt"), "w") as fh:
            fh.write("\n".join(_log))

        resumen = "\n".join(
            "  %s   %g x %g x %g   %d agujeros, %d de canto, %d ranuras"
            % (p["nombre"], p["ancho"], p["alto"], p["espesor"],
               len(p["agujeros"]), len(p["agujeros_canto"]), len(p["ranuras"]))
            for p in piezas) or "  (ninguna)"
        aviso = ("\n\nSALTADAS:\n  " + "\n  ".join(saltadas)) if saltadas else ""
        # Trampa clasica: apenas UNA pieza queda marcada TIPO=PLACA, el resto se
        # ignora. Conviene decirlo con todas las letras y no solo listarlas.
        if any("no esta marcado como PLACA" in s_ for s_ in saltadas):
            aviso += ("\n\nOJO: hay piezas marcadas y piezas sin marcar. Cuando "
                      "hay al menos una marcada, las que NO lo estan se ignoran.\n"
                      "Marca TODAS las placas con MarcarPlaca, o ninguna.")
        ui.messageBox("%d piezas → piezas.json\n\n%s%s\n\n"
                      "Ahora doble clic en GENERAR ARCHIVOS.command, en la misma "
                      "carpeta, y quedan los cuatro formatos, la lista de corte y "
                      "las hojas de verificacion.\n\n"
                      "El detalle de cada cara examinada esta en diagnostico.txt"
                      % (len(piezas), resumen, aviso), "Exportar Piezas")

    except Exception:
        if ui:
            ui.messageBox("Fallo:\n%s" % traceback.format_exc(), "Exportar Piezas")
