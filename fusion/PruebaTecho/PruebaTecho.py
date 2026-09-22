# -*- coding: utf-8 -*-
"""
Prueba Techo — script de Autodesk Fusion para FABRICA MUEBLES.

Modela solo la pieza de prueba: el techo de PRUEBA 1, codigo 9441838670057.
400 x 600 x 18, cuatro agujeros O10 prof 11, ranura de fondo 6x6 en la cara A
y ranura de luz 9x9 en la cara B. Deja el componente marcado y listo.

Existe para sacar el modelado de la ecuacion: si despues `ExportarPiezas` no da
lo esperado, el problema esta en el extractor y no en como se modelo.

USO: abrir un DOCUMENTO NUEVO Y VACIO en milimetros y ejecutarlo.
     Despues correr `ExportarPiezas` sobre ese documento.

Las medidas de aca salen de los archivos de referencia de Bluen, verificados
12 de 12. El .ban que produzca este camino tiene que dar identico al de
etapa2/salida/PRUEBA1/BAN/9441838670057.ban
"""

import math
import traceback

import adsk.core
import adsk.fusion

GRUPO = "FabricaMuebles"

# --- la pieza, en milimetros -------------------------------------------------
ANCHO, ALTO, ESPESOR = 400.0, 600.0, 18.0
AGUJEROS = [  # x, y, diametro, profundidad
    (40.0, 9.0, 10.0, 11.0),
    (360.0, 9.0, 10.0, 11.0),
    (40.0, 591.0, 10.0, 11.0),
    (360.0, 591.0, 10.0, 11.0),
]
# x_centro, y_desde, y_hasta, ancho, profundidad, cara
RANURAS = [
    (372.5, 12.85, 587.15, 6.0, 6.0, "A"),
    (304.5, -5.0, 605.0, 9.0, 9.0, "B"),   # se pasa de largo a proposito
]
DATOS = {
    "TIPO": "PLACA",
    "NOMBRE": "PRUEBA 1_00-Doble c/spar01_Roof plate01",
    "CODIGO": "9441838670057",
    "MATERIAL": u"多层实木",
    "TEXTURA": u"13玛雅灰",
    "VETA": "VERTICAL",
    "CANTO_ABAJO": "1", "CANTO_ARRIBA": "1", "CANTO_IZQ": "1", "CANTO_DER": "0",
}
DATOS_MUEBLE = {"ORDEN": "260625-20", "CLIENTE": "", "PROYECTO": "PRUEBA",
                "AMBIENTE": "PRUEBA 1"}

MM = 0.1      # la API de Fusion trabaja en centimetros


def cm(v):
    return v * MM


def val(v):
    return adsk.core.ValueInput.createByReal(v)


def perfiles_por_area(sketch, area_mm2, tol=0.15):
    """Elige los perfiles cuya area se parece a la esperada (evita agarrar de mas)."""
    objetivo = area_mm2 * MM * MM
    col = adsk.core.ObjectCollection.create()
    for i in range(sketch.profiles.count):
        p = sketch.profiles.item(i)
        try:
            a = p.areaProperties(adsk.fusion.CalculationAccuracy.LowCalculationAccuracy).area
        except Exception:
            continue
        if abs(a - objetivo) <= objetivo * tol:
            col.add(p)
    return col


def cortar(comp, cuerpo, perfiles, desde_mm, profundidad_mm):
    """Corte desde un plano paralelo a XY, con inicio desplazado."""
    ext = comp.features.extrudeFeatures
    inp = ext.createInput(perfiles, adsk.fusion.FeatureOperations.CutFeatureOperation)
    if abs(desde_mm) > 1e-9:
        inp.startExtent = adsk.fusion.OffsetStartDefinition.create(val(cm(desde_mm)))
    inp.setDistanceExtent(False, val(cm(profundidad_mm)))
    inp.participantBodies = [cuerpo]
    return ext.add(inp)


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
        # Un documento de tipo "Part Design" no admite sub-componentes; en ese
        # caso la placa va directo en el componente raiz.
        try:
            occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
            comp = occ.component
            comp.name = "Roof plate01"
            modo = "componente propio"
        except Exception:
            comp = root
            modo = "componente raiz (documento tipo Part)"
            try:
                comp.name = "Roof plate01"
            except Exception:
                pass

        # --- cuerpo ---------------------------------------------------------
        sk = comp.sketches.add(comp.xYConstructionPlane)
        sk.name = "contorno"
        sk.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(0, 0, 0),
            adsk.core.Point3D.create(cm(ANCHO), cm(ALTO), 0))
        ext = comp.features.extrudeFeatures
        inp = ext.createInput(sk.profiles.item(0),
                              adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        inp.setDistanceExtent(False, val(-cm(ESPESOR)))
        cuerpo = ext.add(inp).bodies.item(0)
        cuerpo.name = "Roof plate01"

        # --- agujeros (uno por diametro, agrupados) --------------------------
        por_diametro = {}
        for x, y, d, prof in AGUJEROS:
            por_diametro.setdefault((d, prof), []).append((x, y))
        for (d, prof), puntos in sorted(por_diametro.items()):
            s = comp.sketches.add(comp.xYConstructionPlane)
            s.name = "agujeros O%g" % d
            for x, y in puntos:
                s.sketchCurves.sketchCircles.addByCenterRadius(
                    adsk.core.Point3D.create(cm(x), cm(y), 0), cm(d / 2.0))
            perfiles = perfiles_por_area(s, math.pi * (d / 2.0) ** 2)
            if perfiles.count != len(puntos):
                raise RuntimeError("esperaba %d perfiles de O%g y encontre %d"
                                   % (len(puntos), d, perfiles.count))
            cortar(comp, cuerpo, perfiles, 0.0, -prof)

        # --- ranuras ---------------------------------------------------------
        for i, (xc, y0, y1, ancho, prof, cara) in enumerate(RANURAS):
            s = comp.sketches.add(comp.xYConstructionPlane)
            s.name = "ranura %g x %g cara %s" % (ancho, prof, cara)
            s.sketchCurves.sketchLines.addTwoPointRectangle(
                adsk.core.Point3D.create(cm(xc - ancho / 2.0), cm(y0), 0),
                adsk.core.Point3D.create(cm(xc + ancho / 2.0), cm(y1), 0))
            perfiles = perfiles_por_area(s, ancho * (y1 - y0), tol=0.02)
            if perfiles.count != 1:
                perfiles = adsk.core.ObjectCollection.create()
                perfiles.add(s.profiles.item(0))
            if cara == "A":
                cortar(comp, cuerpo, perfiles, 0.0, -prof)          # desde arriba
            else:
                cortar(comp, cuerpo, perfiles, -ESPESOR, prof)      # desde abajo

        # --- datos ------------------------------------------------------------
        for k, v in DATOS.items():
            comp.attributes.add(GRUPO, k, v)
        for k, v in DATOS_MUEBLE.items():
            root.attributes.add(GRUPO, k, v)

        bb = cuerpo.boundingBox
        medidas = "%.1f x %.1f x %.1f mm" % (
            (bb.maxPoint.x - bb.minPoint.x) / MM,
            (bb.maxPoint.y - bb.minPoint.y) / MM,
            (bb.maxPoint.z - bb.minPoint.z) / MM)

        ui.messageBox(
            "Techo de prueba creado.\n\n"
            "  medidas: %s   (esperado 400.0 x 600.0 x 18.0)\n"
            "  caras del solido: %d\n"
            "  4 agujeros O10 prof 11\n"
            "  ranura 6x6 cara A  ·  ranura 9x9 cara B\n"
            "  marcado como PLACA, codigo 9441838670057\n"
            "  modo: %s\n\n"
            "Ahora corre ExportarPiezas sobre este documento."
            % (medidas, cuerpo.faces.count, modo), "Prueba Techo")

    except Exception:
        if ui:
            ui.messageBox("Fallo:\n%s" % traceback.format_exc(), "Prueba Techo")
