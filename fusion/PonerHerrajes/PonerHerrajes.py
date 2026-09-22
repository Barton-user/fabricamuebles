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
MARGEN = 50.0                 # mm del extremo al primer conector

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

        bb = body.boundingBox                     # en el marco del componente
        self.x0, self.y0 = bb.minPoint.x, bb.minPoint.y
        self.zA = bb.maxPoint.z                   # cara A = Z mayor
        self.ancho = mm(bb.maxPoint.x - bb.minPoint.x)
        self.alto = mm(bb.maxPoint.y - bb.minPoint.y)
        self.espesor = mm(bb.maxPoint.z - bb.minPoint.z)

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


def posiciones(largo, cuantos, margen=MARGEN):
    """Reparto de los conectores a lo largo de la union, en fracciones 0..1."""
    if cuantos <= 1:
        return [0.5]
    m = min(margen, largo / 3.0)
    a, b = m / largo, 1.0 - m / largo
    return [a + (b - a) * i / (cuantos - 1.0) for i in range(cuantos)]


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
#  poner un 3 en 1 en una union
# --------------------------------------------------------------------------- #

def herrajear(j, herraje, cuantos, log):
    a, b = j["apoya"], j["recibe"]
    cam, perno, recibe = herraje["cam"], herraje["perno"], herraje["recibe"]

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
        cara_a.append((cx, cy, cam["d"], cam["prof"], "A"))

        # --- la que recibe: O10 donde pega el perno ---
        bx, by, bz = b.a_local(pw)
        cara = "A" if abs(bz) < abs(bz + b.espesor) else "B"
        en_b.append((bx, by, recibe["d"], recibe["prof"], cara))

    # El O8 desemboca en el O15, asi que el B-Rep lo va a medir de menos.
    # Se deja escrito cuanto entra de verdad, para que ExportarPiezas no tenga
    # que adivinarlo con una tabla fija que no vale para todos los herrajes.
    a.body.attributes.add(GRUPO, "PROF_CANTO_%g" % round(perno["d"], 1),
                          str(perno["prof"]))

    n = 0
    n += agujero_cara(a, cara_a)
    n += agujero_canto(a, canto_a, log)
    n += agujero_cara(b, en_b)
    log("  %s -> %s (canto %s): %d conectores, %d agujeros"
        % (a.nombre, b.nombre, canto_a[0][5] if canto_a else "?",
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
            "    todas | 1,3 | 1-4   |   %s   |   cantidad\n\n"
            "BISAGRAS: escribi  BISAGRAS | n de la puerta | n del lateral | cuantas"
            % (len(js), "\n".join(lineas), catalogo),
            "Poner Herrajes", "todas | 3EN1-33 | 3")
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
            cuantos = int(partes[2] or "3")
        except ValueError:
            ui.messageBox("La cantidad tiene que ser un numero, vino '%s'."
                          % partes[2], "Poner Herrajes")
            return
        if cuantos < 1:
            ui.messageBox("La cantidad tiene que ser 1 o mas.", "Poner Herrajes")
            return

        registro = []
        total = 0
        for i in idx:
            try:
                total += herrajear(js[i], HERRAJES[clave], cuantos, registro.append)
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

def _cara_hacia(placa, objetivo_w):
    """De las dos caras de la placa, la que mira hacia objetivo_w."""
    t = placa.eje_esp
    return "A" if abs(placa.wmax[t] - objetivo_w) < abs(placa.wmin[t] - objetivo_w) \
        else "B"


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
    plano_lat = lateral.wmax[w] if cara_lat == "A" else lateral.wmin[w]

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
