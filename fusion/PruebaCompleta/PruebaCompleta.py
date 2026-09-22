# -*- coding: utf-8 -*-
"""
Prueba Completa — script de Autodesk Fusion para FABRICA MUEBLES.

Modela las DIEZ piezas de PRUEBA 1 (orden 260625-20) para validar el extractor
contra todos los casos, no solo el facil:

  · agujeros de cara, ciegos, de 5 diametros distintos
  · agujeros de canto en los cuatro cantos
  · ranuras en cara A y en cara B
  · piezas rotadas a retrato (las dos fascia boards)
  · una pieza sin ningun mecanizado (el fondo de 5 mm)

Las medidas salen de los .ban ya verificados 12/12 contra los archivos de
referencia de Bluen. El .ban que produzca este camino tiene que dar identico a
etapa2/salida/PRUEBA1/BAN/.

USO: abrir un DOCUMENTO NUEVO Y VACIO en milimetros y ejecutarlo.
     Despues correr `ExportarPiezas` sobre ese documento.

Las piezas se acuestan una al lado de la otra sobre el plano XY. Cada una es un
CUERPO del componente raiz con sus datos en atributos propios, asi que funciona
igual en un documento tipo Part que en uno tipo Assembly.
"""

import math
import traceback

import adsk.core
import adsk.fusion

GRUPO = "FabricaMuebles"
MM = 0.1          # la API de Fusion trabaja en centimetros
SEPARACION = 60.0  # mm entre piezas
HOLGURA = 1.0      # mm que se pasan los cortes para que rompan la superficie

DATOS_MUEBLE = {"ORDEN": "260625-20", "CLIENTE": "", "DIRECCION": "PRUEBA",
                "AMBIENTE": "PRUEBA 1"}
TEXTURA = u"13玛雅灰"

PIEZAS = [
    {
        "codigo": "9441838670057",
        "nombre": u"PRUEBA 1_00-Doble c/spar01_Roof plate01",
        "ancho": 400, "alto": 600, "espesor": 18,
        "material": u"多层实木",
        "cantos": (1, 1, 1, 0),
        "agujeros": [(360, 9, 10, 11, 'A'), (40, 9, 10, 11, 'A'), (360, 591, 10, 11, 'A'), (40, 591, 10, 11, 'A')],
        "canto_agujeros": [],
        "ranuras": [(372.5, 587.15, 372.5, 12.85, 6, 6, 'A'), (304.5, 600, 304.5, 0, 9, 9, 'B')],
    },
    {
        "codigo": "9441838670064",
        "nombre": u"PRUEBA 1_00-Doble c/spar01_Left board01",
        "ancho": 400, "alto": 741.83, "espesor": 18,
        "material": u"多层实木",
        "cantos": (0, 0, 1, 0),
        "agujeros": [(360, 708.83, 15, 13.5, 'A'), (40, 708.83, 15, 13.5, 'A'), (20, 176.5, 6, 3, 'A'), (52, 176.5, 6, 3, 'A'), (20, 658.33, 6, 3, 'A'), (52, 658.33, 6, 3, 'A'), (329, 429.91, 10, 11, 'A'), (41, 429.91, 10, 11, 'A'), (360, 109, 10, 11, 'A'), (40, 109, 10, 11, 'A'), (9, 50, 10, 11, 'A'), (391, 50, 10, 11, 'A')],
        "canto_agujeros": [(360, 741.83, 9, 8, 33, 'U'), (40, 741.83, 9, 8, 33, 'U')],
        "ranuras": [(372.5, 741.83, 372.5, 112.85, 6, 6, 'A')],
    },
    {
        "codigo": "9441838670071",
        "nombre": u"PRUEBA 1_00-Doble c/spar01_Right board01",
        "ancho": 400, "alto": 741.83, "espesor": 18,
        "material": u"多层实木",
        "cantos": (0, 0, 1, 0),
        "agujeros": [(360, 33, 15, 13.5, 'A'), (40, 33, 15, 13.5, 'A'), (20, 565.33, 6, 3, 'A'), (52, 565.33, 6, 3, 'A'), (20, 83.5, 6, 3, 'A'), (52, 83.5, 6, 3, 'A'), (329, 311.92, 10, 11, 'A'), (41, 311.92, 10, 11, 'A'), (360, 632.83, 10, 11, 'A'), (40, 632.83, 10, 11, 'A'), (9, 691.83, 10, 11, 'A'), (391, 691.83, 10, 11, 'A')],
        "canto_agujeros": [(360, 0, 9, 8, 33, 'D'), (40, 0, 9, 8, 33, 'D')],
        "ranuras": [(372.5, 0, 372.5, 628.98, 6, 6, 'A')],
    },
    {
        "codigo": "9441838670088",
        "nombre": u"PRUEBA 1_00-Doble c/spar01_Cabinet door01_Double left01",
        "ancho": 297, "alto": 681.83, "espesor": 18,
        "material": u"多层实木",
        "cantos": (1, 1, 1, 1),
        "agujeros": [(22.5, 581.83, 35, 13, 'A'), (37, 557.83, 6, 3, 'A'), (37, 605.83, 6, 3, 'A'), (22.5, 100, 35, 13, 'A'), (37, 76, 6, 3, 'A'), (37, 124, 6, 3, 'A')],
        "canto_agujeros": [],
        "ranuras": [],
    },
    {
        "codigo": "9441838670101",
        "nombre": u"PRUEBA 1_00-Doble c/spar01_Cabinet door01_Double open right01",
        "ancho": 297, "alto": 681.83, "espesor": 18,
        "material": u"多层实木",
        "cantos": (1, 1, 1, 1),
        "agujeros": [(274.5, 581.83, 35, 13, 'A'), (260, 557.83, 6, 3, 'A'), (260, 605.83, 6, 3, 'A'), (274.5, 100, 35, 13, 'A'), (260, 76, 6, 3, 'A'), (260, 124, 6, 3, 'A')],
        "canto_agujeros": [],
        "ranuras": [],
    },
    {
        "codigo": "9441838670125",
        "nombre": u"PRUEBA 1_00-Doble c/spar01_Partition02",
        "ancho": 370, "alto": 564, "espesor": 18,
        "material": u"多层实木",
        "cantos": (0, 0, 0, 1),
        "agujeros": [(41, 33, 15, 13.5, 'A'), (329, 33, 15, 13.5, 'A'), (41, 531, 15, 13.5, 'A'), (329, 531, 15, 13.5, 'A')],
        "canto_agujeros": [(41, 0, 9, 8, 33, 'D'), (329, 0, 9, 8, 33, 'D'), (41, 564, 9, 8, 33, 'U'), (329, 564, 9, 8, 33, 'U')],
        "ranuras": [],
    },
    {
        "codigo": "9441838670132",
        "nombre": u"PRUEBA 1_00-Doble c/spar01_Partition01",
        "ancho": 400, "alto": 564, "espesor": 18,
        "material": u"多层实木",
        "cantos": (0, 0, 0, 1),
        "agujeros": [(40, 531, 15, 13.5, 'B'), (360, 531, 15, 13.5, 'B'), (40, 33, 15, 13.5, 'B'), (360, 33, 15, 13.5, 'B'), (391, 42, 10, 11, 'B'), (391, 522, 10, 11, 'B'), (9, 42, 10, 11, 'B'), (9, 522, 10, 11, 'B')],
        "canto_agujeros": [(40, 564, 9, 8, 33, 'U'), (360, 564, 9, 8, 33, 'U'), (40, 0, 9, 8, 33, 'D'), (360, 0, 9, 8, 33, 'D')],
        "ranuras": [(27.5, 564, 27.5, 0, 6, 6, 'A')],
    },
    {
        "codigo": "9441838670149",
        "nombre": u"PRUEBA 1_00-Doble c/spar01_Back panel01",
        "ancho": 574, "alto": 633.83, "espesor": 5,
        "material": u"装饰板",
        "cantos": (0, 0, 0, 0),
        "agujeros": [],
        "canto_agujeros": [],
        "ranuras": [],
    },
    {
        "codigo": "9441838670156",
        "nombre": u"PRUEBA 1_00-Doble c/spar01_Fascia board02_Vertical Partition01",
        "ancho": 100, "alto": 564, "espesor": 18,
        "material": u"多层实木",
        "cantos": (0, 0, 1, 0),
        "agujeros": [(50, 531, 15, 13.5, 'A'), (50, 33, 15, 13.5, 'A'), (33, 522, 15, 13.5, 'A'), (33, 42, 15, 13.5, 'A')],
        "canto_agujeros": [(50, 564, 9, 8, 33, 'U'), (50, 0, 9, 8, 33, 'D'), (0, 522, 9, 8, 33, 'L'), (0, 42, 9, 8, 33, 'L')],
        "ranuras": [],
    },
    {
        "codigo": "9441838670163",
        "nombre": u"PRUEBA 1_00-Doble c/spar01_Fascia board01_Vertical Partition01",
        "ancho": 100, "alto": 564, "espesor": 18,
        "material": u"多层实木",
        "cantos": (0, 0, 0, 1),
        "agujeros": [(50, 33, 15, 13.5, 'A'), (50, 531, 15, 13.5, 'A'), (67, 522, 15, 13.5, 'A'), (67, 42, 15, 13.5, 'A')],
        "canto_agujeros": [(50, 0, 9, 8, 33, 'D'), (50, 564, 9, 8, 33, 'U'), (100, 522, 9, 8, 33, 'R'), (100, 42, 9, 8, 33, 'R')],
        "ranuras": [],
    },
]



def cm(v):
    return v * MM


def val(v):
    return adsk.core.ValueInput.createByReal(v)


def pt(x, y, z):
    return adsk.core.Point3D.create(cm(x), cm(y), cm(z))


def perfiles_por_area(sketch, area_mm2, tol=0.12):
    objetivo = area_mm2 * MM * MM
    col = adsk.core.ObjectCollection.create()
    for i in range(sketch.profiles.count):
        p = sketch.profiles.item(i)
        try:
            a = p.areaProperties(
                adsk.fusion.CalculationAccuracy.LowCalculationAccuracy).area
        except Exception:
            continue
        if abs(a - objetivo) <= objetivo * tol:
            col.add(p)
    return col


def cortar(comp, cuerpo, perfiles, desde_mm, profundidad_mm):
    ext = comp.features.extrudeFeatures
    inp = ext.createInput(perfiles, adsk.fusion.FeatureOperations.CutFeatureOperation)
    if abs(desde_mm) > 1e-9:
        inp.startExtent = adsk.fusion.OffsetStartDefinition.create(val(cm(desde_mm)))
    inp.setDistanceExtent(False, val(cm(profundidad_mm)))
    inp.participantBodies = [cuerpo]
    return ext.add(inp)


def _cuerpo_por_nombre(comp, nombre):
    for i in range(comp.bRepBodies.count):
        b = comp.bRepBodies.item(i)
        if b.name == nombre:
            return b
    return None


def cortar_cantos(comp, nombre_cuerpo, cilindros):
    """Agujeros horizontales: cilindros temporales + una sola booleana de resta.

    Se hace asi y no con un boceto sobre un plano lateral porque los ejes de
    esos planos cambian de orientacion segun cual sea, y aca los dos extremos
    del eje se dan en coordenadas globales: no hay nada que interpretar.

    OJO: al cerrar el BaseFeature, Fusion invalida las referencias que se
    tomaron adentro (ALL_TOOL_BODY_REFERENCE_LOST). Por eso los cuerpos se
    vuelven a buscar DESPUES del finishEdit, comparando contra los que habia
    antes. Todos los cilindros de la pieza van en un solo BaseFeature y una
    sola combinacion.
    """
    if not cilindros:
        return _cuerpo_por_nombre(comp, nombre_cuerpo)

    antes = set()
    for i in range(comp.bRepBodies.count):
        antes.add(comp.bRepBodies.item(i).entityToken)

    tbm = adsk.fusion.TemporaryBRepManager.get()
    base = comp.features.baseFeatures.add()
    base.startEdit()
    for p0, p1, radio_mm in cilindros:
        comp.bRepBodies.add(tbm.createCylinderOrCone(p0, cm(radio_mm),
                                                     p1, cm(radio_mm)), base)
    base.finishEdit()

    tools = adsk.core.ObjectCollection.create()
    for i in range(comp.bRepBodies.count):
        b = comp.bRepBodies.item(i)
        if b.entityToken not in antes:
            tools.add(b)
    if tools.count != len(cilindros):
        raise RuntimeError("esperaba %d cilindros y aparecieron %d"
                           % (len(cilindros), tools.count))

    objetivo = _cuerpo_por_nombre(comp, nombre_cuerpo)
    if objetivo is None:
        raise RuntimeError("se perdio el cuerpo %s" % nombre_cuerpo)

    ci = comp.features.combineFeatures.createInput(objetivo, tools)
    ci.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
    ci.isKeepToolBodies = False
    comp.features.combineFeatures.add(ci)
    return _cuerpo_por_nombre(comp, nombre_cuerpo)


def modelar(comp, pieza, dx, indice=0):
    W = float(pieza["ancho"])
    H = float(pieza["alto"])
    T = float(pieza["espesor"])

    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "%s contorno" % pieza["codigo"]
    sk.sketchCurves.sketchLines.addTwoPointRectangle(pt(dx, 0, 0), pt(dx + W, H, 0))
    ext = comp.features.extrudeFeatures
    inp = ext.createInput(sk.profiles.item(0),
                          adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    inp.setDistanceExtent(False, val(-cm(T)))
    cuerpo = ext.add(inp).bodies.item(0)
    # nombre temporal unico: si el documento ya tiene un cuerpo con este codigo,
    # buscar por nombre agarraria el viejo
    temporal = "__pieza_%d__" % indice
    cuerpo.name = temporal

    # --- agujeros de cara, agrupados por diametro/profundidad/cara ----------
    grupos = {}
    for x, y, d, prof, cara in pieza["agujeros"]:
        grupos.setdefault((float(d), float(prof), cara), []).append((float(x), float(y)))
    for (d, prof, cara), puntos in sorted(grupos.items(), key=lambda k: (k[0][0], k[0][1], k[0][2])):
        s = comp.sketches.add(comp.xYConstructionPlane)
        s.name = "%s O%g %s" % (pieza["codigo"], d, cara)
        for x, y in puntos:
            s.sketchCurves.sketchCircles.addByCenterRadius(pt(dx + x, y, 0), cm(d / 2.0))
        perfiles = perfiles_por_area(s, math.pi * (d / 2.0) ** 2)
        if perfiles.count != len(puntos):
            raise RuntimeError("%s: esperaba %d perfiles de O%g y hay %d"
                               % (pieza["codigo"], len(puntos), d, perfiles.count))
        pasante = prof >= T - 0.01
        largo = (T + HOLGURA) if pasante else prof
        if cara == "A":
            cortar(comp, cuerpo, perfiles, 0.0, -largo)
        else:
            cortar(comp, cuerpo, perfiles, -T, largo)

    # --- ranuras ------------------------------------------------------------
    for i, (x1, y1, x2, y2, ancho, prof, cara) in enumerate(pieza["ranuras"]):
        x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)
        ancho, prof = float(ancho), float(prof)
        # si un extremo toca el borde de la pieza, pasarse para que corte limpio
        def estirar(a, b, lim):
            if abs(min(a, b)) <= 0.01:
                a, b = (a - HOLGURA, b) if a < b else (a, b - HOLGURA)
            if abs(max(a, b) - lim) <= 0.01:
                a, b = (a, b + HOLGURA) if b > a else (a + HOLGURA, b)
            return a, b
        if abs(x1 - x2) < 0.01:                      # ranura a lo largo de Y
            y1, y2 = estirar(y1, y2, H)
            a = pt(dx + x1 - ancho / 2.0, min(y1, y2), 0)
            b = pt(dx + x1 + ancho / 2.0, max(y1, y2), 0)
            area = ancho * abs(y2 - y1)
        else:                                        # ranura a lo largo de X
            x1, x2 = estirar(x1, x2, W)
            a = pt(dx + min(x1, x2), y1 - ancho / 2.0, 0)
            b = pt(dx + max(x1, x2), y1 + ancho / 2.0, 0)
            area = ancho * abs(x2 - x1)
        s = comp.sketches.add(comp.xYConstructionPlane)
        s.name = "%s ranura %d" % (pieza["codigo"], i + 1)
        s.sketchCurves.sketchLines.addTwoPointRectangle(a, b)
        perfiles = perfiles_por_area(s, area, tol=0.05)
        if perfiles.count != 1:
            perfiles = adsk.core.ObjectCollection.create()
            perfiles.add(s.profiles.item(0))
        if cara == "A":
            cortar(comp, cuerpo, perfiles, 0.0, -prof)
        else:
            cortar(comp, cuerpo, perfiles, -T, prof)

    # --- agujeros de canto --------------------------------------------------
    cilindros = []
    for x, y, z, d, prof, canto in pieza["canto_agujeros"]:
        x, y, z, d, prof = float(x), float(y), float(z), float(d), float(prof)
        gz = -z                                   # cara A en z=0, hacia adentro negativo
        if canto == "L":
            p0, p1 = pt(dx - HOLGURA, y, gz), pt(dx + prof, y, gz)
        elif canto == "R":
            p0, p1 = pt(dx + W + HOLGURA, y, gz), pt(dx + W - prof, y, gz)
        elif canto == "D":
            p0, p1 = pt(dx + x, -HOLGURA, gz), pt(dx + x, prof, gz)
        elif canto == "U":
            p0, p1 = pt(dx + x, H + HOLGURA, gz), pt(dx + x, H - prof, gz)
        else:
            raise RuntimeError("%s: canto desconocido %r" % (pieza["codigo"], canto))
        cilindros.append((p0, p1, d / 2.0))
    cuerpo = cortar_cantos(comp, temporal, cilindros) or cuerpo
    cuerpo.name = pieza["codigo"]

    # --- datos, en atributos del CUERPO -------------------------------------
    ab, ar, iz, de = pieza["cantos"]
    datos = {
        "TIPO": "PLACA", "NOMBRE": pieza["nombre"], "CODIGO": pieza["codigo"],
        "MATERIAL": pieza["material"], "TEXTURA": TEXTURA, "VETA": "VERTICAL",
        "CANTO_ABAJO": str(ab), "CANTO_ARRIBA": str(ar),
        "CANTO_IZQ": str(iz), "CANTO_DER": str(de),
    }
    for k, v in datos.items():
        cuerpo.attributes.add(GRUPO, k, v)
    return cuerpo


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox("Abri un diseno de Fusion antes de correr el script.")
            return
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        root = design.rootComponent

        if root.bRepBodies.count:
            ui.messageBox(
                "Este documento ya tiene %d cuerpo(s).\n\nCorre el script en un "
                "documento NUEVO Y VACIO: si no, se mezclan las piezas de las "
                "corridas anteriores y el export sale con codigos repetidos."
                % root.bRepBodies.count, "Prueba Completa")
            return

        dx = 0.0
        hechas, fallos = [], []
        for i, pieza in enumerate(PIEZAS):
            try:
                cuerpo = modelar(root, pieza, dx, i)
                bb = cuerpo.boundingBox
                hechas.append("  %s  %.1f x %.1f x %.1f   %d caras" % (
                    pieza["codigo"],
                    (bb.maxPoint.x - bb.minPoint.x) / MM,
                    (bb.maxPoint.y - bb.minPoint.y) / MM,
                    (bb.maxPoint.z - bb.minPoint.z) / MM,
                    cuerpo.faces.count))
            except Exception as e:
                fallos.append("  %s: %s" % (pieza["codigo"], e))
            dx += float(pieza["ancho"]) + SEPARACION

        for k, v in DATOS_MUEBLE.items():
            root.attributes.add(GRUPO, k, v)

        msg = "%d de %d piezas modeladas.\n\n%s" % (
            len(hechas), len(PIEZAS), "\n".join(hechas))
        if fallos:
            msg += "\n\nFALLARON:\n" + "\n".join(fallos)
        msg += "\n\nAhora corre ExportarPiezas sobre este documento."
        ui.messageBox(msg, "Prueba Completa")

    except Exception:
        if ui:
            ui.messageBox("Fallo:\n%s" % traceback.format_exc(), "Prueba Completa")
