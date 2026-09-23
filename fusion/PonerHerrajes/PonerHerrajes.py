# -*- coding: utf-8 -*-
"""
Poner Herrajes — script de Autodesk Fusion para FABRICA MUEBLES.

Busca solo las uniones del mueble y hace los agujeros de los herrajes en las
DOS piezas de cada union.

COMO SE MODELA PARA QUE FUNCIONE
--------------------------------
Cada placa, un COMPONENTE, con la placa ACOSTADA adentro (boceto en XY, extruir
en Z). Despues se para y se ubica moviendo la ocurrencia. Es como modela
cualquiera un mueble, y es lo que ya necesita ExportarPiezas.

Una union es una placa que APOYA su canto contra la CARA de otra.

COMO SE USA
-----------
Correr el script. No hace falta seleccionar nada: Fusion borra la seleccion al
abrir el dialogo de Scripts, asi que el script lista las uniones que encontro y
pregunta cuales herrajear.

    1  Estante       -> Lateral izq    canto DER, 564 mm de contacto
    2  Estante       -> Lateral der    canto IZQ, 564 mm de contacto

    Cuales?  todas | 1,3 | 1-4        herraje: 3EN1-33      cantidad: 3

LAS MEDIDAS NO SON INVENTADAS
-----------------------------
Salen de medir los 72 conectores de los archivos reales de Bluen. Los dos
pedidos que tenemos usan herrajes DISTINTOS, por eso hay dos entradas en la
tabla y hay que elegir cual.
"""

import math
import traceback

import adsk.core
import adsk.fusion

GRUPO = "FabricaMuebles"
MM = 0.1                      # 1 mm en cm, que es la unidad interna de Fusion
TOL = 0.05                    # cm — 0,5 mm
SOLAPE_MIN = 20.0             # mm de contacto para considerar que hay union
MARGEN_MIN = 40.0             # mm minimos del extremo al primer conector
PASO = 32.0                   # mm: los conectores caen en una grilla de 32 (System 32)
LARGO_UN_CONECTOR = 200.0     # mm: uniones mas cortas llevan un solo conector

# --------------------------------------------------------------------------- #
#  tabla de herrajes — medida sobre los archivos reales de Bluen
# --------------------------------------------------------------------------- #
#
#   3EN1-33 : 20 conectores del pedido PRUEBA 1
#   3EN1-34 : 52 conectores del pedido de muestra
#
#   En los 72 el O15 va a 33 mm del canto, con 13,5 de profundidad, y el O8
#   entra por el canto a 9 mm (media placa de 18). Lo unico que cambia entre
#   pedidos es cuanto entran el perno y el receptor.

HERRAJES = {
    "3EN1-33": {
        "nombre": "3 en 1 — perno 33 (PRUEBA 1)",
        "cam":    {"d": 15.0, "prof": 13.5, "desde_canto": 33.0},
        "perno":  {"d": 8.0,  "prof": 33.0},
        "recibe": {"d": 10.0, "prof": 11.0},
    },
    "3EN1-34": {
        "nombre": "3 en 1 — perno 34 (pedido de muestra)",
        "cam":    {"d": 15.0, "prof": 13.5, "desde_canto": 33.0},
        "perno":  {"d": 8.0,  "prof": 34.0},
        "recibe": {"d": 10.0, "prof": 12.0},
    },
}

# Bisagra de cazoleta, medida sobre las 4 bisagras de PRUEBA 1: las dos puertas
# y los dos laterales. Lleva agujeros en las DOS piezas.
#
#   en la PUERTA : cazoleta O35x13 a 22,5 del canto
#                  2 tornillos O6x3 a 37 del canto (14,5 mas adentro), +-24
#   en el LATERAL: 2 tornillos O6x3 del herraje de la base, a 20 y 52 del
#                  canto DE ADELANTE, los dos a la altura de la bisagra
BISAGRA = {
    "nombre": "bisagra cazoleta 35",
    "cazoleta": {"d": 35.0, "prof": 13.0, "desde_canto": 22.5},
    "tornillo": {"d": 6.0, "prof": 3.0, "adentro": 14.5, "a_lo_largo": 24.0},
    "base": {"d": 6.0, "prof": 3.0, "desde_frente": (20.0, 52.0)},
}

MARGEN_BISAGRA = 100.0        # mm del extremo de la puerta a la primera bisagra


# --------------------------------------------------------------------------- #
#  utilidades
# --------------------------------------------------------------------------- #

def mm(v):
    return v * 10.0


def leer(obj, nombre, defecto=""):
    a = obj.attributes.itemByName(GRUPO, nombre)
    return a.value if a is not None and a.value is not None else defecto


def pedir(ui, prompt, titulo, defecto):
    r = ui.inputBox(prompt, titulo, defecto)
    if not isinstance(r, (tuple, list)):
        r = (r,)
    texto, cancelado = None, False
    for v in r:
        if isinstance(v, bool):
            cancelado = v
        elif isinstance(v, str):
            texto = v
    return None if (cancelado or texto is None) else texto


def parsear_indices(texto, total):
    t = texto.strip().lower()
    if t in ("todas", "todos", "all", "*"):
        return list(range(total))
    idx = []
    for trozo in t.replace(" ", "").split(","):
        if not trozo:
            continue
        if "-" in trozo:
            a, _, b = trozo.partition("-")
            if not (a.isdigit() and b.isdigit()):
                return None
            idx.extend(range(int(a), int(b) + 1))
        elif trozo.isdigit():
            idx.append(int(trozo))
        else:
            return None
    if not idx or any(not 1 <= n <= total for n in idx):
        return None
    vistos, limpio = set(), []
    for n in idx:
        if n not in vistos:
            vistos.add(n)
            limpio.append(n - 1)
    return limpio


# --------------------------------------------------------------------------- #
#  las placas y su marco
# --------------------------------------------------------------------------- #

class Placa(object):
    """Una placa: su cuerpo acostado en el componente, y donde quedo en el mueble."""

    def __init__(self, occ, body):
        self.occ = occ
        self.body = body
        self.comp = occ.component
        self.codigo = leer(body, "CODIGO") or body.name
        self.nombre = leer(body, "NOMBRE") or occ.component.name
        # ROL: PUERTA / FONDO / (vacio = estructura). Las puertas y los fondos no
        # llevan tres en uno aunque toquen otra placa. Un fondo se reconoce solo
        # por el espesor si no esta marcado.
        self.rol = str(leer(body, "ROL", "")).strip().upper()

        bb = body.boundingBox                     # en el marco del componente
        self.x0, self.y0 = bb.minPoint.x, bb.minPoint.y
        self.zA = bb.maxPoint.z                   # cara A = Z mayor
        self.ancho = mm(bb.maxPoint.x - bb.minPoint.x)
        self.alto = mm(bb.maxPoint.y - bb.minPoint.y)
        self.espesor = mm(bb.maxPoint.z - bb.minPoint.z)
        if not self.rol and self.espesor < 8.0:
            self.rol = "FONDO"

        self.m = occ.transform2.copy()
        self.mi = occ.transform2.copy()
        self.mi.invert()

        mb = occ.bRepBodies.item(0).boundingBox if occ.bRepBodies.count else bb
        self.wmin = [mb.minPoint.x, mb.minPoint.y, mb.minPoint.z]
        self.wmax = [mb.maxPoint.x, mb.maxPoint.y, mb.maxPoint.z]
        ext = [self.wmax[i] - self.wmin[i] for i in range(3)]
        self.eje_esp = ext.index(min(ext))        # eje del mundo donde va el espesor

    def a_local(self, pw):
        """Punto del mundo -> (x, y, z) en mm del marco de la placa acostada.

        z se mide desde la cara A, hacia adentro negativo, igual que en el .ban.
        """
        p = adsk.core.Point3D.create(pw[0], pw[1], pw[2])
        p.transformBy(self.mi)
        return (mm(p.x - self.x0), mm(p.y - self.y0), mm(p.z - self.zA))

    def canto_de(self, x, y):
        if abs(x) <= 1.0:
            return "IZQ"
        if abs(x - self.ancho) <= 1.0:
            return "DER"
        if abs(y) <= 1.0:
            return "ABAJO"
        if abs(y - self.alto) <= 1.0:
            return "ARRIBA"
        return None


def placas_del_diseno(design):
    root = design.rootComponent
    out = []
    for i in range(root.allOccurrences.count):
        occ = root.allOccurrences.item(i)
        if not occ.isLightBulbOn:
            continue
        for j in range(occ.component.bRepBodies.count):
            b = occ.component.bRepBodies.item(j)
            if not b.isSolid or not b.isVisible:
                continue
            if str(leer(b, "TIPO", "")).strip().upper() not in ("", "PLACA"):
                continue
            try:
                out.append(Placa(occ, b))
            except Exception:
                pass
    return out


# --------------------------------------------------------------------------- #
#  deteccion de uniones
# --------------------------------------------------------------------------- #

def uniones(placas):
    """Toda placa que APOYA su canto contra la CARA de otra.

    Se trabaja con las cajas en el mundo. Un mueble esta a escuadra, asi que el
    canto de una y la cara de la otra caen sobre el mismo plano perpendicular a
    un eje: eso es lo que se busca.
    """
    out = []
    for a in placas:
        for b in placas:
            if a is b:
                continue
            if a.rol in ("PUERTA", "FONDO") or b.rol in ("PUERTA", "FONDO"):
                continue                      # puertas y fondos no se herrajean
            u = b.eje_esp                     # el canto de A apoya sobre la cara de B
            if u == a.eje_esp:
                continue                      # A esta en el mismo plano que B, no apoya
            v = 3 - a.eje_esp - u             # el tercer eje: por ahi corre la union
            for cara_b in (b.wmin[u], b.wmax[u]):
                for canto_a in (a.wmin[u], a.wmax[u]):
                    if abs(canto_a - cara_b) > TOL:
                        continue
                    lo = max(a.wmin[v], b.wmin[v])
                    hi = min(a.wmax[v], b.wmax[v])
                    if mm(hi - lo) < SOLAPE_MIN:
                        continue
                    # y tienen que compartir tambien el rango del espesor de A
                    ta = a.eje_esp
                    if not (b.wmin[ta] - TOL <= a.wmin[ta] and
                            a.wmax[ta] <= b.wmax[ta] + TOL):
                        continue
                    out.append({
                        "apoya": a, "recibe": b,
                        "eje_union": v, "lo": lo, "hi": hi,
                        "plano": cara_b, "eje_plano": u,
                        "centro_esp": (a.wmin[ta] + a.wmax[ta]) / 2.0,
                        "eje_esp_a": ta,
                        "largo": mm(hi - lo)})
    return out


def punto_union(j, t):
    """Punto del mundo sobre la linea de union, a la fraccion t (0..1)."""
    p = [0.0, 0.0, 0.0]
    p[j["eje_union"]] = j["lo"] + t * (j["hi"] - j["lo"])
    p[j["eje_plano"]] = j["plano"]
    p[j["eje_esp_a"]] = j["centro_esp"]
    return p


def posiciones(largo, cuantos, margen_min=MARGEN_MIN, paso=PASO):
    """Reparto de los conectores a lo largo de la union, en fracciones 0..1.

    Regla medida sobre PRUEBA 1 (uniones de 370, 400 y 564 mm, 2 conectores):
    GuiGui deja como minimo 40 mm en cada extremo y separa los conectores un
    multiplo de 32 mm, el mayor que entre, centrado en la union.

        400 -> 40 / 360   (tramo 320 = 10 x 32)
        370 -> 41 / 329   (tramo 288 =  9 x 32)
        564 -> 42 / 522   (tramo 480 = 15 x 32)
    """
    if cuantos <= 1:
        return [0.5]
    libre = largo - 2.0 * margen_min
    if libre <= 0:
        return [0.5]
    tramo = paso * math.floor(libre / paso + 1e-9)
    if tramo <= 0:
        tramo = libre
    m = (largo - tramo) / 2.0
    return [(m + tramo * i / (cuantos - 1.0)) / largo for i in range(cuantos)]


def cuantos_auto(largo):
    """Cuantos conectores lleva una union, segun su largo (PRUEBA 1: 100 -> 1, 370..564 -> 2)."""
    return 1 if largo <= LARGO_UN_CONECTOR else 2


def orientacion(design):
    """(eje_arriba, eje_frente) del mueble en el mundo: indice 0/1/2 y signo.

    Se leen de los atributos EJE_ARRIBA / EJE_FRENTE del componente raiz
    ("+Y", "-Z", ...). Sin atributos se asume la orientacion por defecto de
    Fusion: Z arriba, el frente mirando a -Y.
    """
    def eje(txt, defecto):
        txt = (txt or defecto).strip().upper()
        signo = -1 if txt.startswith("-") else 1
        letra = txt.lstrip("+-")[:1]
        return ("XYZ".index(letra) if letra in "XYZ" else defecto_idx(defecto)), signo
    def defecto_idx(d):
        return "XYZ".index(d.lstrip("+-")[:1])
    root = design.rootComponent
    return (eje(leer(root, "EJE_ARRIBA"), "+Z"), eje(leer(root, "EJE_FRENTE"), "-Y"))


def cara_oculta(placa, orient, centro):
    """Cara de la placa donde va la excentrica: la menos visible.

    Regla deducida de PRUEBA 1:
      placa horizontal      -> la cara de ABAJO
      placa de frente/atras -> la cara que mira hacia ATRAS
      lateral / divisor     -> la cara que mira al CENTRO del mueble
    """
    (i_up, s_up), (i_fr, s_fr) = orient
    t = placa.eje_esp
    if t == i_up:
        objetivo = placa.wmin[t] - 10.0 if s_up > 0 else placa.wmax[t] + 10.0
    elif t == i_fr:
        objetivo = placa.wmax[t] + 10.0 if s_fr < 0 else placa.wmin[t] - 10.0
    else:
        objetivo = centro[t]
    return _cara_hacia(placa, objetivo)


def centro_mueble(placas):
    lo = [min(p.wmin[i] for p in placas) for i in range(3)]
    hi = [max(p.wmax[i] for p in placas) for i in range(3)]
    return [(lo[i] + hi[i]) / 2.0 for i in range(3)]


# --------------------------------------------------------------------------- #
#  hacer los agujeros
# --------------------------------------------------------------------------- #

def agujero_cara(placa, pedidos):
    """Agujeros perpendiculares a la cara. pedidos = [(x, y, diam, prof, cara)].

    cara "A" = la de Z mayor del componente; "B" = la de Z menor.

    OJO: se agrupa por cara Y POR PROFUNDIDAD. Agrupar solo por cara hace que
    todos los agujeros de esa cara salgan con la profundidad del mas hondo: en
    una puerta con cazoleta de 13 y tornillos de 3, los tornillos salian de 13.
    """
    if not pedidos:
        return 0
    comp = placa.comp
    hechos = 0
    grupos = {}
    for pe in pedidos:
        grupos.setdefault((pe[4], round(pe[3], 3)), []).append(pe)

    for (cara, prof), grupo in sorted(grupos.items()):
        sk = comp.sketches.add(comp.xYConstructionPlane)
        sk.name = "herrajes cara %s prof %g" % (cara, prof)
        z0 = placa.zA / MM - placa.espesor        # cara B, en mm del marco local
        for x, y, d, _, _ in grupo:
            sk.sketchCurves.sketchCircles.addByCenterRadius(
                adsk.core.Point3D.create((placa.x0 / MM + x) * MM,
                                         (placa.y0 / MM + y) * MM, 0),
                d / 2.0 * MM)
        if cara == "A":
            desde = z0 + placa.espesor - prof
        else:
            desde = z0 - 1.0
        largo = prof + 1.0
        ext = comp.features.extrudeFeatures
        col = adsk.core.ObjectCollection.create()
        for i in range(sk.profiles.count):
            col.add(sk.profiles.item(i))
        inp = ext.createInput(col, adsk.fusion.FeatureOperations.CutFeatureOperation)
        inp.startExtent = adsk.fusion.OffsetStartDefinition.create(
            adsk.core.ValueInput.createByReal(desde * MM))
        inp.setDistanceExtent(False, adsk.core.ValueInput.createByReal(largo * MM))
        inp.participantBodies = [placa.body]
        ext.add(inp)
        hechos += len(grupo)
    return hechos


DIRECCION = {"IZQ": (1, 0), "DER": (-1, 0), "ABAJO": (0, 1), "ARRIBA": (0, -1)}


def agujero_canto(placa, pedidos, log):
    """Agujeros que entran por el canto. pedidos = [(x, y, z, diam, prof, canto)].

    Se hacen con cilindros temporales y un Combine, que es lo unico que sabe
    taladrar de costado sin depender de un plano de boceto nuevo por agujero.
    """
    if not pedidos:
        return 0
    comp = placa.comp
    tbm = adsk.fusion.TemporaryBRepManager.get()
    herramientas = []
    for x, y, z, d, prof, canto in pedidos:
        dx, dy = DIRECCION[canto]
        # arranca 1 mm afuera para que corte limpio el canto
        bx = placa.x0 / MM + x - dx * 1.0
        by = placa.y0 / MM + y - dy * 1.0
        bz = placa.zA / MM + z
        base = adsk.core.Point3D.create(bx * MM, by * MM, bz * MM)
        tope = adsk.core.Point3D.create((bx + dx * (prof + 1.0)) * MM,
                                        (by + dy * (prof + 1.0)) * MM, bz * MM)
        herramientas.append(tbm.createCylinderOrCone(base, d / 2.0 * MM,
                                                     tope, d / 2.0 * MM))

    antes = set()
    for j in range(comp.bRepBodies.count):
        antes.add(comp.bRepBodies.item(j).entityToken)

    base_feat = comp.features.baseFeatures.add()
    base_feat.startEdit()
    for t in herramientas:
        comp.bRepBodies.add(t, base_feat)
    base_feat.finishEdit()

    # OJO: al cerrar el BaseFeature, Fusion invalida las referencias tomadas
    # adentro. Hay que volver a buscar los cuerpos comparando con los de antes.
    nuevos = []
    for j in range(comp.bRepBodies.count):
        b = comp.bRepBodies.item(j)
        if b.entityToken not in antes:
            nuevos.append(b)
    if len(nuevos) != len(herramientas):
        log("  aviso: esperaba %d herramientas y encontre %d"
            % (len(herramientas), len(nuevos)))
    if not nuevos:
        return 0

    destino = None
    for j in range(comp.bRepBodies.count):
        b = comp.bRepBodies.item(j)
        if b.entityToken not in [n.entityToken for n in nuevos]:
            if leer(b, "CODIGO") == placa.codigo or b.name == placa.body.name:
                destino = b
    if destino is None:
        destino = placa.body

    comb = comp.features.combineFeatures
    ci = comb.createInput(destino, adsk.core.ObjectCollection.create())
    for b in nuevos:
        ci.toolBodies.add(b)
    ci.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
    ci.isKeepToolBodies = False
    comb.add(ci)
    return len(pedidos)



# --------------------------------------------------------------------------- #
#  cuerpos de herraje
# --------------------------------------------------------------------------- #
#
#  Ademas de los agujeros, se pone el herraje como componente: excentrica,
#  perno y receptor del 3 en 1, y la bisagra completa (cazoleta, brazo, base y
#  tornillos). Son para la documentacion (explotada, manual de armado) y para
#  el visor: la maquina no los necesita. Van marcados TIPO = HERRAJE en el
#  cuerpo y en el componente, asi ExportarPiezas y este mismo script los
#  ignoran. Un componente por tipo de herraje, reutilizado en cada posicion.
#
#  Marco local de cada herraje: origen en la boca del agujero, Z hacia adentro
#  de la placa. Las formas son simplificadas pero con las medidas reales de
#  diametro y profundidad; el detalle fino se cambia en las funciones _forma_*.

DIBUJAR_HERRAJES = True


def _vec(placa, x, y, z):
    """Vector del marco local de la placa -> mundo (sin traslacion), unitario."""
    v = adsk.core.Vector3D.create(x, y, z)
    v.transformBy(placa.m)
    v.normalize()
    return v


def _p3(p):
    return adsk.core.Point3D.create(p[0], p[1], p[2])


def _mas(p, v, k):
    return [p[0] + v.x * k, p[1] + v.y * k, p[2] + v.z * k]


def _marco(origen, ez, ex_pista=None):
    """Matrix3D con Z = ez y X = ex_pista proyectado (o cualquiera perpendicular)."""
    z = ez.copy()
    z.normalize()
    if ex_pista is None or abs(ex_pista.dotProduct(z)) > 0.9:
        ex_pista = adsk.core.Vector3D.create(1, 0, 0) if abs(z.x) < 0.9 \
            else adsk.core.Vector3D.create(0, 1, 0)
    k = ex_pista.dotProduct(z)
    x = adsk.core.Vector3D.create(ex_pista.x - k * z.x, ex_pista.y - k * z.y,
                                  ex_pista.z - k * z.z)
    x.normalize()
    y = z.crossProduct(x)
    m = adsk.core.Matrix3D.create()
    m.setWithCoordinateSystem(_p3(origen), x, y, z)
    return m


def _cil(tbm, p0, p1, d):
    """Cilindro entre dos puntos (mm, marco local) de diametro d."""
    return tbm.createCylinderOrCone(_p3([c * MM for c in p0]), d / 2.0 * MM,
                                    _p3([c * MM for c in p1]), d / 2.0 * MM)


def _caja(tbm, x0, x1, y0, y1, z0, z1):
    c = adsk.core.Point3D.create((x0 + x1) / 2.0 * MM, (y0 + y1) / 2.0 * MM,
                                 (z0 + z1) / 2.0 * MM)
    obb = adsk.core.OrientedBoundingBox3D.create(
        c, adsk.core.Vector3D.create(1, 0, 0), adsk.core.Vector3D.create(0, 1, 0),
        abs(x1 - x0) * MM, abs(y1 - y0) * MM, abs(z1 - z0) * MM)
    return tbm.createBox(obb)


def _construir(comp, nombre_cuerpo, solidos):
    """Mete los solidos temporales en el componente (un BaseFeature) y los une."""
    base = comp.features.baseFeatures.add()
    base.startEdit()
    for sol in solidos:
        comp.bRepBodies.add(sol, base)
    base.finishEdit()
    cuerpos = [comp.bRepBodies.item(i) for i in range(comp.bRepBodies.count)]
    if len(cuerpos) > 1:
        ci = comp.features.combineFeatures.createInput(
            cuerpos[0], adsk.core.ObjectCollection.create())
        for b in cuerpos[1:]:
            ci.toolBodies.add(b)
        ci.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        ci.isKeepToolBodies = False
        comp.features.combineFeatures.add(ci)
    metal = _apariencia_metal()
    for i in range(comp.bRepBodies.count):
        b = comp.bRepBodies.item(i)
        b.name = nombre_cuerpo
        b.attributes.add(GRUPO, "TIPO", "HERRAJE")
        if metal is not None:
            try:
                b.appearance = metal
            except Exception:
                pass
    comp.attributes.add(GRUPO, "TIPO", "HERRAJE")


def _apariencia_metal():
    """Una apariencia metalica de la biblioteca de Fusion, copiada al diseno. Si no hay, None."""
    try:
        app = adsk.core.Application.get()
        design = adsk.fusion.Design.cast(app.activeProduct)
        for j in range(design.appearances.count):
            if design.appearances.item(j).name in ("Aluminum - Satin", "Steel - Satin"):
                return design.appearances.item(j)
        for i in range(app.materialLibraries.count):
            lib = app.materialLibraries.item(i)
            try:
                aps = lib.appearances
            except Exception:
                continue
            for j in range(aps.count):
                a = aps.item(j)
                if a.name in ("Aluminum - Satin", "Steel - Satin"):
                    return design.appearances.addByCopy(a, a.name)
    except Exception:
        pass
    return None


def _forma_excentrica(tbm, cam):
    d, prof = cam["d"] - 0.4, cam["prof"] - 0.5
    return [_cil(tbm, (0, 0, 0), (0, 0, prof), d),
            _cil(tbm, (0, 0, -0.8), (0, 0, 0), d)]          # borde que asoma


def _forma_receptor(tbm, recibe):
    return [_cil(tbm, (0, 0, 0), (0, 0, recibe["prof"] - 0.5), recibe["d"] - 0.4)]


def _forma_perno(tbm, perno, recibe):
    return [_cil(tbm, (0, 0, 0), (0, 0, perno["prof"] - 1.0), perno["d"] - 0.4),
            _cil(tbm, (0, 0, -(recibe["prof"] - 2.0)), (0, 0, 0), 6.0)]


def _forma_bisagra(tbm, dx_lat):
    """Marco: origen en el centro de la cazoleta sobre la cara interior de la
    puerta, X hacia el centro de la puerta, Z hacia adentro de la puerta.
    dx_lat = donde queda la cara interior del lateral sobre X (negativo)."""
    caz, tor, base = BISAGRA["cazoleta"], BISAGRA["tornillo"], BISAGRA["base"]
    e = 2.0                                                   # chapa
    z_brazo = -13.0                                           # altura del brazo sobre la puerta
    solidos = [
        _cil(tbm, (0, 0, 0), (0, 0, caz["prof"] - 0.5), caz["d"] - 0.4),   # cazoleta
        _caja(tbm, -caz["d"] / 2.0, caz["d"] / 2.0, -9, 9, -e, 0),          # tapa de la cazoleta
        _caja(tbm, dx_lat, 8, -7, 7, z_brazo, z_brazo + e * 2),             # brazo
        _caja(tbm, dx_lat, dx_lat + e, -7, 7, z_brazo, -e),                 # bajada a la placa
        _caja(tbm, dx_lat, dx_lat + e, -9, 9, -(base["desde_frente"][1] + 10),
              z_brazo),                                                     # base sobre el lateral
    ]
    for dist in base["desde_frente"]:
        solidos.append(_cil(tbm, (dx_lat - tor["prof"], 0, -dist),
                            (dx_lat + e, 0, -dist), tor["d"] - 0.4))       # tornillos
    return solidos


def _herraje(nombre, matriz, forma, *args):
    """Pone una ocurrencia del herraje `nombre` en `matriz`; lo modela la primera vez."""
    design = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    root = design.rootComponent
    comp = design.allComponents.itemByName(nombre)
    if comp is not None and comp.bRepBodies.count:
        return root.occurrences.addExistingComponent(comp, matriz)
    occ = root.occurrences.addNewComponent(matriz)
    comp = occ.component
    comp.name = nombre
    tbm = adsk.fusion.TemporaryBRepManager.get()
    _construir(comp, nombre, forma(tbm, *args))
    return occ


def dibujar_3en1(a, b, pw, dir_in_a, cara_cam, herraje):
    """Excentrica + perno en la placa que apoya, receptor en la que recibe."""
    cam, perno, recibe = herraje["cam"], herraje["perno"], herraje["recibe"]
    n_a = _vec(a, 0, 0, 1)                       # normal de la cara A de la que apoya
    if cara_cam == "A":
        sup = _mas(pw, n_a, a.espesor / 2.0 * MM)
        z_cam = n_a.copy(); z_cam.scaleBy(-1.0)
    else:
        sup = _mas(pw, n_a, -a.espesor / 2.0 * MM)
        z_cam = n_a
    centro_cam = _mas(sup, dir_in_a, cam["desde_canto"] * MM)
    _herraje("Excentrica O%g" % cam["d"], _marco(centro_cam, z_cam, dir_in_a),
             _forma_excentrica, cam)
    _herraje("Perno O%g x %g" % (perno["d"], perno["prof"]), _marco(pw, dir_in_a),
             _forma_perno, perno, recibe)
    hacia_b = dir_in_a.copy(); hacia_b.scaleBy(-1.0)
    _herraje("Receptor O%g" % recibe["d"], _marco(pw, hacia_b), _forma_receptor, recibe)


def dibujar_bisagra(puerta, lateral, pw, x_h, plano_lat, w):
    """Bisagra completa: pw = punto del canto de la puerta a la altura de la bisagra."""
    caz = BISAGRA["cazoleta"]
    n_p = _vec(puerta, 0, 0, 1)                  # cara A de la puerta = la interior
    sup = _mas(pw, n_p, puerta.espesor / 2.0 * MM)
    centro = _mas(sup, x_h, caz["desde_canto"] * MM)
    z_h = n_p.copy(); z_h.scaleBy(-1.0)
    comp_w = [x_h.x, x_h.y, x_h.z][w]
    dx_lat = mm((plano_lat - centro[w]) * (1.0 if comp_w > 0 else -1.0))
    _herraje("Bisagra O%g base %g" % (caz["d"], round(dx_lat, 1)),
             _marco(centro, z_h, x_h), _forma_bisagra, dx_lat)

# --------------------------------------------------------------------------- #
#  poner un 3 en 1 en una union
# --------------------------------------------------------------------------- #

def herrajear(j, herraje, cuantos, log, cara_cam="A"):
    a, b = j["apoya"], j["recibe"]
    cam, perno, recibe = herraje["cam"], herraje["perno"], herraje["recibe"]
    if cuantos is None or cuantos <= 0:
        cuantos = cuantos_auto(j["largo"])

    cara_a, canto_a, en_b = [], [], []
    for t in posiciones(j["largo"], cuantos):
        pw = punto_union(j, t)

        # --- la que apoya: O8 por el canto + O15 en la cara ---
        x, y, z = a.a_local(pw)
        canto = a.canto_de(x, y)
        if canto is None:
            log("  union %s -> %s: el punto (%.1f, %.1f) no cae en ningun canto, "
                "se saltea" % (a.nombre, b.nombre, x, y))
            continue
        dx, dy = DIRECCION[canto]
        canto_a.append((x, y, -a.espesor / 2.0, perno["d"], perno["prof"], canto))
        cx = x + dx * cam["desde_canto"]
        cy = y + dy * cam["desde_canto"]
        cara_a.append((cx, cy, cam["d"], cam["prof"], cara_cam))

        # --- la que recibe: O10 donde pega el perno ---
        bx, by, bz = b.a_local(pw)
        cara = "A" if abs(bz) < abs(bz + b.espesor) else "B"
        en_b.append((bx, by, recibe["d"], recibe["prof"], cara))

        if DIBUJAR_HERRAJES:
            try:
                dibujar_3en1(a, b, pw, _vec(a, dx, dy, 0), cara_cam, herraje)
            except Exception as e:
                log("  aviso: no pude dibujar el herraje en (%.0f, %.0f): %s" % (x, y, e))

    # El O8 desemboca en el O15, asi que el B-Rep lo va a medir de menos.
    # Se deja escrito cuanto entra de verdad, para que ExportarPiezas no tenga
    # que adivinarlo con una tabla fija que no vale para todos los herrajes.
    a.body.attributes.add(GRUPO, "PROF_CANTO_%g" % round(perno["d"], 1),
                          str(perno["prof"]))

    n = 0
    n += agujero_cara(a, cara_a)
    n += agujero_canto(a, canto_a, log)
    n += agujero_cara(b, en_b)
    log("  %s -> %s (canto %s, excentrica en cara %s): %d conectores, %d agujeros"
        % (a.nombre, b.nombre, canto_a[0][5] if canto_a else "?", cara_cam,
           len(canto_a), n))
    return len(canto_a)


def poner_bisagras(placa, canto, posiciones_mm, log):
    """Cazoleta O35 + los dos O6, sobre un canto de la puerta."""
    caz, tor = BISAGRA["cazoleta"], BISAGRA["tornillo"]
    dx, dy = DIRECCION[canto]
    pedidos = []
    for s in posiciones_mm:
        if canto in ("IZQ", "DER"):
            bx = (0.0 if canto == "IZQ" else placa.ancho) + dx * caz["desde_canto"]
            by = s
            tx = (0.0 if canto == "IZQ" else placa.ancho) + dx * (
                caz["desde_canto"] + tor["adentro"])
            ty1, ty2 = s - tor["a_lo_largo"], s + tor["a_lo_largo"]
            pedidos.append((bx, by, caz["d"], caz["prof"], "A"))
            pedidos.append((tx, ty1, tor["d"], tor["prof"], "A"))
            pedidos.append((tx, ty2, tor["d"], tor["prof"], "A"))
        else:
            by = (0.0 if canto == "ABAJO" else placa.alto) + dy * caz["desde_canto"]
            bx = s
            ty = (0.0 if canto == "ABAJO" else placa.alto) + dy * (
                caz["desde_canto"] + tor["adentro"])
            tx1, tx2 = s - tor["a_lo_largo"], s + tor["a_lo_largo"]
            pedidos.append((bx, by, caz["d"], caz["prof"], "A"))
            pedidos.append((tx1, ty, tor["d"], tor["prof"], "A"))
            pedidos.append((tx2, ty, tor["d"], tor["prof"], "A"))
    n = agujero_cara(placa, pedidos)
    log("  %s: %d bisagras en el canto %s (%d agujeros)"
        % (placa.nombre, len(posiciones_mm), canto, n))
    return n


# --------------------------------------------------------------------------- #

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox("Abri un diseno de Fusion antes de correr el script.",
                          "Poner Herrajes")
            return

        placas = placas_del_diseno(design)
        if len(placas) < 2:
            ui.messageBox(
                "Encontre %d placa(s) en componentes.\n\n"
                "Para que el script pueda buscar las uniones, cada placa tiene "
                "que ser un COMPONENTE, con la placa acostada adentro, y puesta "
                "en su lugar moviendo la ocurrencia." % len(placas),
                "Poner Herrajes")
            return

        js = uniones(placas)
        if not js:
            ui.messageBox(
                "Encontre %d placas pero ninguna union.\n\n"
                "Una union es una placa que APOYA su canto contra la CARA de "
                "otra. Si las placas estan sueltas o acostadas una al lado de "
                "la otra, no hay uniones que herrajear." % len(placas),
                "Poner Herrajes")
            return

        lineas = []
        for n, j in enumerate(js, 1):
            lineas.append("%2d  %-18s -> %-18s  %.0f mm de contacto"
                          % (n, j["apoya"].nombre[:18], j["recibe"].nombre[:18],
                             j["largo"]))
        catalogo = "   ".join(sorted(HERRAJES))
        texto = pedir(
            ui,
            "%d uniones:\n\n%s\n\n"
            "Cuales herrajeo, que herraje y cuantos por union:\n"
            "    todas | 1,3 | 1-4   |   %s   |   auto o cantidad\n\n"
            "BISAGRAS: escribi  BISAGRAS | n de la puerta | n del lateral | cuantas"
            % (len(js), "\n".join(lineas), catalogo),
            "Poner Herrajes", "todas | 3EN1-33 | auto")
        if texto is None:
            return

        partes = [p.strip() for p in texto.split("|")]
        while len(partes) < 3:
            partes.append("")

        if partes[0].strip().upper().startswith("BISAGRA"):
            # BISAGRAS | <n puerta> | <n lateral> | <cuantas>
            while len(partes) < 4:
                partes.append("")
            lista = "\n".join("%2d  %s" % (n, p.nombre)
                              for n, p in enumerate(placas, 1))
            try:
                ip = int(partes[1]); il = int(partes[2])
                cuantas = int(partes[3] or "2")
            except ValueError:
                ui.messageBox(
                    "Para bisagras hace falta:\n\n"
                    "    BISAGRAS | numero de la PUERTA | numero del LATERAL | "
                    "cuantas\n\nLas placas son:\n\n%s" % lista,
                    "Poner Herrajes")
                return
            if not (1 <= ip <= len(placas) and 1 <= il <= len(placas)) or ip == il:
                ui.messageBox("Los numeros tienen que ser dos placas distintas "
                              "de esta lista:\n\n%s" % lista, "Poner Herrajes")
                return
            registro = []
            try:
                n = herrajear_bisagras(placas[ip - 1], placas[il - 1],
                                       cuantas, registro.append)
            except Exception as e:
                ui.messageBox("No pude poner las bisagras:\n\n%s" % e,
                              "Poner Herrajes")
                return
            ui.messageBox("%s\n\n%d bisagras puestas.\n\n%s\n\n"
                          "Ahora corre ExportarPiezas."
                          % (BISAGRA["nombre"], n, "\n".join(registro)),
                          "Poner Herrajes")
            return

        idx = parsear_indices(partes[0], len(js))
        if idx is None:
            ui.messageBox("No entiendo '%s'.\n\nUsa: todas | 1,3 | 1-4"
                          % partes[0], "Poner Herrajes")
            return
        clave = (partes[1] or "3EN1-33").strip().upper()
        if clave not in HERRAJES:
            ui.messageBox("No conozco el herraje '%s'.\n\nHay: %s"
                          % (clave, catalogo), "Poner Herrajes")
            return
        try:
            cuantos = 0 if (partes[2] or "auto").strip().lower() in ("auto", "") else int(partes[2])
        except ValueError:
            ui.messageBox("La cantidad tiene que ser un numero, vino '%s'."
                          % partes[2], "Poner Herrajes")
            return
        if cuantos < 0:
            ui.messageBox("La cantidad tiene que ser 'auto' o 1 o mas.", "Poner Herrajes")
            return

        registro = []
        total = 0
        orient = orientacion(design)
        centro = centro_mueble(placas)
        for i in idx:
            try:
                total += herrajear(js[i], HERRAJES[clave], cuantos, registro.append,
                                   cara_cam=cara_oculta(js[i]["apoya"], orient, centro))
            except Exception as e:
                registro.append("  FALLO en la union %d: %s" % (i + 1, e))

        ui.messageBox(
            "%s\n\n%d conectores puestos en %d uniones.\n\n%s\n\n"
            "Ahora corre ExportarPiezas."
            % (HERRAJES[clave]["nombre"], total, len(idx), "\n".join(registro)),
            "Poner Herrajes")

    except Exception:
        if ui:
            ui.messageBox("Fallo:\n%s" % traceback.format_exc(), "Poner Herrajes")


# --------------------------------------------------------------------------- #
#  bisagras
# --------------------------------------------------------------------------- #

def _plano_cara(placa, cara):
    """Coordenada del mundo (sobre el eje del espesor) donde queda la cara A o B."""
    t = placa.eje_esp
    pa = adsk.core.Point3D.create(placa.x0, placa.y0, placa.zA)
    pa.transformBy(placa.m)
    wa = [pa.x, pa.y, pa.z][t]
    wb = placa.wmin[t] if abs(wa - placa.wmax[t]) < abs(wa - placa.wmin[t]) else placa.wmax[t]
    return wa if cara == "A" else wb


def _cara_hacia(placa, objetivo_w):
    """De las dos caras de la placa, la que mira hacia objetivo_w.

    Se calcula donde quedo la cara A en el mundo con la matriz de la ocurrencia.
    Suponer que A es siempre la de coordenada mayor es falso en cuanto el Z
    local del componente apunta al negativo de un eje del mundo.
    """
    wa, wb = _plano_cara(placa, "A"), _plano_cara(placa, "B")
    return "A" if abs(wa - objetivo_w) < abs(wb - objetivo_w) else "B"


def herrajear_bisagras(puerta, lateral, cuantas, log):
    """Cazoleta y tornillos en la puerta, y los de la base en el lateral.

    La puerta y el lateral los elige el usuario; todo lo demas sale de donde
    quedaron las dos piezas en el mueble.
    """
    caz, tor, base = BISAGRA["cazoleta"], BISAGRA["tornillo"], BISAGRA["base"]

    w = lateral.eje_esp                    # el ancho del mueble
    d = puerta.eje_esp                     # la profundidad: por ahi tiene espesor la puerta
    if w == d:
        raise ValueError("la puerta y el lateral estan en el mismo plano; "
                         "revisa cual elegiste")
    v = 3 - w - d                          # el alto: por ahi corre la linea de bisagras

    # cara interna del lateral = la que mira al centro de la puerta
    centro_puerta_w = (puerta.wmin[w] + puerta.wmax[w]) / 2.0
    cara_lat = _cara_hacia(lateral, centro_puerta_w)
    plano_lat = _plano_cara(lateral, cara_lat)

    # canto de la puerta donde van las bisagras = el mas cercano al lateral
    canto_w = min((puerta.wmin[w], puerta.wmax[w]),
                  key=lambda c: abs(c - plano_lat))

    # canto de ADELANTE del lateral = el mas cercano al plano de la puerta
    centro_puerta_d = (puerta.wmin[d] + puerta.wmax[d]) / 2.0
    frente_d = min((lateral.wmin[d], lateral.wmax[d]),
                   key=lambda c: abs(c - centro_puerta_d))

    largo = mm(puerta.wmax[v] - puerta.wmin[v])
    m = min(MARGEN_BISAGRA, largo / 3.0)
    if cuantas <= 1:
        fracs = [0.5]
    else:
        a, b = m / largo, 1.0 - m / largo
        fracs = [a + (b - a) * i / (cuantas - 1.0) for i in range(cuantas)]

    en_puerta, en_lateral = [], []
    for t in fracs:
        alto = puerta.wmin[v] + t * (puerta.wmax[v] - puerta.wmin[v])

        # --- puerta ---
        pw = [0.0, 0.0, 0.0]
        pw[v] = alto
        pw[w] = canto_w
        pw[d] = (puerta.wmin[d] + puerta.wmax[d]) / 2.0
        x, y, z = puerta.a_local(pw)
        canto = puerta.canto_de(x, y)
        if canto is None:
            log("  la bisagra a la altura %.0f no cae en un canto de la puerta, "
                "se saltea" % mm(alto))
            continue
        dx, dy = DIRECCION[canto]
        # a lo largo del canto: el eje perpendicular al que entra
        lx, ly = (0.0, 1.0) if canto in ("IZQ", "DER") else (1.0, 0.0)
        cx, cy = x + dx * caz["desde_canto"], y + dy * caz["desde_canto"]
        en_puerta.append((cx, cy, caz["d"], caz["prof"], "A"))
        tx = x + dx * (caz["desde_canto"] + tor["adentro"])
        ty = y + dy * (caz["desde_canto"] + tor["adentro"])
        for signo in (-1.0, 1.0):
            en_puerta.append((tx + lx * signo * tor["a_lo_largo"],
                              ty + ly * signo * tor["a_lo_largo"],
                              tor["d"], tor["prof"], "A"))
        if DIBUJAR_HERRAJES:
            try:
                dibujar_bisagra(puerta, lateral, pw, _vec(puerta, dx, dy, 0), plano_lat, w)
            except Exception as e:
                log("  aviso: no pude dibujar la bisagra a %.0f: %s" % (mm(alto), e))

        # --- lateral: los dos tornillos de la base ---
        lw = [0.0, 0.0, 0.0]
        lw[v] = alto
        lw[w] = plano_lat
        lw[d] = frente_d
        bx, by, bz = lateral.a_local(lw)
        canto_f = lateral.canto_de(bx, by)
        if canto_f is None:
            log("  no encuentro el canto de adelante del lateral, se saltea")
            continue
        fdx, fdy = DIRECCION[canto_f]
        for dist in base["desde_frente"]:
            en_lateral.append((bx + fdx * dist, by + fdy * dist,
                               base["d"], base["prof"], cara_lat))

    n = agujero_cara(puerta, en_puerta) + agujero_cara(lateral, en_lateral)
    log("  %s + %s: %d bisagras, %d agujeros (cazoleta en la cara A de la "
        "puerta, base en la cara %s del lateral)"
        % (puerta.nombre, lateral.nombre, len(fracs), n, cara_lat))
    return len(fracs)
