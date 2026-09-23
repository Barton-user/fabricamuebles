# -*- coding: utf-8 -*-
"""
ArmarPrueba1 — modela PRUEBA 1 (orden 260625-20) como ENSAMBLE en Fusion.

Diferencia con PruebaCompleta: aca las placas van paradas y ubicadas en el
mueble, cada una en su componente, SIN agujeros de herraje. Los agujeros los
pone despues `PonerHerrajes`, y `ExportarPiezas` + `etapa2/validar.py` dicen si
el camino "disenar en Fusion -> maquina" reproduce lo que hacia GuiGui.

Las medidas y posiciones salen del modelo 3D de GuiGui
(referencia/GUIGUI_MCP/207960w11787944219301.render.json). GuiGui es mano
izquierda y Y-arriba; Fusion es mano derecha y Z-arriba. La tabla PIEZAS esta
escrita en un marco intermedio (x_f = -x_gg, Y arriba, frente en -Z) y la
funcion `mundo()` la pasa al mundo de Fusion: x = -x_f, y = z_f, z = y_f. Asi
el mueble queda PARADO, con el frente mirando a -Y (la vista "Front" de Fusion)
y el zocalo en el piso.

Marco de cada placa = marco del archivo de maquina: X ancho, Y alto, cara A en
Z=0 mirando a +Z local, espesor hacia -Z. Se elige por pieza cual cara fisica
es A (la que GuiGui mecaniza) y hacia donde corren X e Y, y el componente se
ubica con la matriz de la ocurrencia. Los nombres son los de PruebaCompleta.

USO: documento NUEVO Y VACIO en milimetros -> Ejecutar. Despues PonerHerrajes,
despues ExportarPiezas.
"""

import math
import traceback

import adsk.core
import adsk.fusion

GRUPO = "FabricaMuebles"
MM = 0.1
HOLGURA = 1.0

MUEBLE = u"00-Doble c/spar01"
DATOS_MUEBLE = {"ORDEN": "260625-20", "CLIENTE": "", "DIRECCION": "PRUEBA",
                "AMBIENTE": "PRUEBA 1",
                # orientacion del mueble en el mundo, la usa PonerHerrajes para
                # elegir la cara oculta de cada placa (GuiGui es Y arriba)
                "EJE_ARRIBA": "+Z", "EJE_FRENTE": "-Y"}
MULTI, DECO = u"多层实木", u"装饰板"
GRIS, NOGAL, BLANCO = u"13玛雅灰", u"04拉丝胡桃", u"d02白麻面"

# origen, ejes X e Y locales en mm / coordenadas Fusion (x_f = -x_guigui).
# ranuras: (x, y1, y2, ancho, prof, cara) en el marco de la placa.
# cantos: (abajo, arriba, izq, der) en mm.
PIEZAS = [
    dict(codigo="9441838670057", nombre=u"PRUEBA 1_00-Doble c/spar01_Roof plate01",
         comp="Techo", ancho=400, alto=600, esp=18, material=MULTI, textura=GRIS,
         cantos=(1, 1, 1, 0), origen=(0, 820.5, -400), ex=(0, 0, 1), ey=(-1, 0, 0),
         ranuras=[(372.5, 12.85, 587.15, 6, 6, "A"), (304.5, 0, 600, 9, 9, "B")]),   # LED a 95,5 del fondo, cara de arriba
    dict(codigo="9441838670064", nombre=u"PRUEBA 1_00-Doble c/spar01_Left board01",
         comp="Lateral izq", ancho=400, alto=741.83, esp=18, material=MULTI, textura=GRIS,
         cantos=(0, 0, 1, 0), origen=(-18, 78.67, -400), ex=(0, 0, 1), ey=(0, 1, 0),
         ranuras=[(372.5, 112.85, 741.83, 6, 6, "A")]),
    dict(codigo="9441838670071", nombre=u"PRUEBA 1_00-Doble c/spar01_Right board01",
         comp="Lateral der", ancho=400, alto=741.83, esp=18, material=MULTI, textura=GRIS,
         cantos=(0, 0, 1, 0), origen=(-582, 820.5, -400), ex=(0, 0, 1), ey=(0, -1, 0),
         ranuras=[(372.5, 0, 628.98, 6, 6, "A")]),
    dict(codigo="9441838670132", nombre=u"PRUEBA 1_00-Doble c/spar01_Partition01",
         comp="Piso", ancho=400, alto=564, esp=18, material=MULTI, textura=GRIS,
         cantos=(0, 0, 0, 1), origen=(-18, 196.67, 0), ex=(0, 0, -1), ey=(-1, 0, 0),
         ranuras=[(27.5, 0, 564, 6, 6, "A")]),
    dict(codigo="9441838670125", nombre=u"PRUEBA 1_00-Doble c/spar01_Partition02",
         comp="Estante", ancho=370, alto=564, esp=18, material=MULTI, textura=GRIS,
         cantos=(0, 0, 0, 1), origen=(-582, 499.585, -30), ex=(0, 0, -1), ey=(1, 0, 0),
         ranuras=[]),
    dict(codigo="9441838670149", nombre=u"PRUEBA 1_00-Doble c/spar01_Back panel01",
         comp="Fondo", rol="FONDO", ancho=574, alto=633.83, esp=5, material=DECO, textura=BLANCO,
         cantos=(0, 0, 0, 0), origen=(-13, 191.67, -30), ex=(-1, 0, 0), ey=(0, 1, 0),
         ranuras=[]),
    dict(codigo="9441838670156", nombre=u"PRUEBA 1_00-Doble c/spar01_Fascia board02_Vertical Partition01",
         comp="Zocalo frente", ancho=100, alto=564, esp=18, material=MULTI, textura=GRIS,
         # canto en el borde de abajo (X=100); GuiGui lo anota en F, ver README
         cantos=(0, 0, 0, 1), origen=(-582, 178.67, -382), ex=(0, -1, 0), ey=(1, 0, 0),
         ranuras=[]),
    dict(codigo="9441838670163", nombre=u"PRUEBA 1_00-Doble c/spar01_Fascia board01_Vertical Partition01",
         comp="Zocalo atras", ancho=100, alto=564, esp=18, material=MULTI, textura=GRIS,
         # canto en el borde de abajo (X=0); GuiGui lo anota en B, ver README
         cantos=(0, 0, 1, 0), origen=(-18, 78.67, 0), ex=(0, 1, 0), ey=(-1, 0, 0),
         ranuras=[]),
    dict(codigo="9441838670088", nombre=u"PRUEBA 1_00-Doble c/spar01_Cabinet door01_Double left01",
         comp="Puerta izq", rol="PUERTA", ancho=297, alto=681.83, esp=18, material=MULTI, textura=NOGAL,
         cantos=(1, 1, 1, 1), origen=(-1.5, 837, -400), ex=(-1, 0, 0), ey=(0, -1, 0),
         ranuras=[]),
    dict(codigo="9441838670101", nombre=u"PRUEBA 1_00-Doble c/spar01_Cabinet door01_Double open right01",
         comp="Puerta der", rol="PUERTA", ancho=297, alto=681.83, esp=18, material=MULTI, textura=NOGAL,
         cantos=(1, 1, 1, 1), origen=(-301.5, 837, -400), ex=(-1, 0, 0), ey=(0, -1, 0),
         ranuras=[]),
]


def cm(v):
    return v * MM


def val(v):
    return adsk.core.ValueInput.createByReal(v)


def pt(x, y, z):
    return adsk.core.Point3D.create(cm(x), cm(y), cm(z))


def cruz(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def mundo(v):
    """Marco de la tabla (Y arriba, frente -Z) -> mundo de Fusion (Z arriba, frente -Y)."""
    return (-v[0], v[2], v[1])


def matriz(origen, ex, ey):
    origen, ex, ey = mundo(origen), mundo(ex), mundo(ey)
    ez = cruz(ex, ey)
    m = adsk.core.Matrix3D.create()
    m.setWithCoordinateSystem(pt(*origen),
                              adsk.core.Vector3D.create(*ex),
                              adsk.core.Vector3D.create(*ey),
                              adsk.core.Vector3D.create(*ez))
    return m


def perfiles_por_area(sketch, area_mm2, tol=0.12):
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
    ext = comp.features.extrudeFeatures
    inp = ext.createInput(perfiles, adsk.fusion.FeatureOperations.CutFeatureOperation)
    if abs(desde_mm) > 1e-9:
        inp.startExtent = adsk.fusion.OffsetStartDefinition.create(val(cm(desde_mm)))
    inp.setDistanceExtent(False, val(cm(profundidad_mm)))
    inp.participantBodies = [cuerpo]
    return ext.add(inp)


def modelar(root, pieza):
    W, H, T = float(pieza["ancho"]), float(pieza["alto"]), float(pieza["esp"])
    occ = root.occurrences.addNewComponent(matriz(pieza["origen"], pieza["ex"], pieza["ey"]))
    comp = occ.component
    comp.name = pieza["comp"]

    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = "contorno"
    sk.sketchCurves.sketchLines.addTwoPointRectangle(pt(0, 0, 0), pt(W, H, 0))
    ext = comp.features.extrudeFeatures
    inp = ext.createInput(sk.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    inp.setDistanceExtent(False, val(-cm(T)))
    cuerpo = ext.add(inp).bodies.item(0)
    cuerpo.name = pieza["codigo"]

    for i, (x, y1, y2, ancho, prof, cara) in enumerate(pieza["ranuras"]):
        y1, y2 = float(min(y1, y2)), float(max(y1, y2))
        if y1 <= 0.01:
            y1 -= HOLGURA
        if y2 >= H - 0.01:
            y2 += HOLGURA
        s = comp.sketches.add(comp.xYConstructionPlane)
        s.name = "ranura %d" % (i + 1)
        s.sketchCurves.sketchLines.addTwoPointRectangle(pt(x - ancho / 2.0, y1, 0), pt(x + ancho / 2.0, y2, 0))
        perfiles = perfiles_por_area(s, ancho * (y2 - y1), tol=0.05)
        if perfiles.count != 1:
            perfiles = adsk.core.ObjectCollection.create()
            perfiles.add(s.profiles.item(0))
        if cara == "A":
            cortar(comp, cuerpo, perfiles, 0.0, -prof)
        else:
            cortar(comp, cuerpo, perfiles, -T, prof)

    ab, ar, iz, de = pieza["cantos"]
    datos = {"TIPO": "PLACA", "NOMBRE": pieza["nombre"], "CODIGO": pieza["codigo"],
             "MATERIAL": pieza["material"], "TEXTURA": pieza["textura"], "VETA": "VERTICAL",
             "MUEBLE": MUEBLE, "ROL": pieza.get("rol", ""),
             "CANTO_ABAJO": str(ab), "CANTO_ARRIBA": str(ar), "CANTO_IZQ": str(iz), "CANTO_DER": str(de)}
    for k, v in datos.items():
        cuerpo.attributes.add(GRUPO, k, v)
    return occ, cuerpo


def armar(design):
    root = design.rootComponent
    if root.bRepBodies.count or root.occurrences.count:
        return None, "El documento no esta vacio (%d cuerpos, %d componentes). Abri uno nuevo." % (
            root.bRepBodies.count, root.occurrences.count)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    lineas = []
    for pieza in PIEZAS:
        occ, cuerpo = modelar(root, pieza)
        bb = cuerpo.boundingBox  # en el espacio del ensamble
        lineas.append("%-14s %s  ensamble x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f]" % (
            pieza["comp"], pieza["codigo"],
            bb.minPoint.x / MM, bb.maxPoint.x / MM, bb.minPoint.y / MM, bb.maxPoint.y / MM,
            bb.minPoint.z / MM, bb.maxPoint.z / MM))
    for k, v in DATOS_MUEBLE.items():
        root.attributes.add(GRUPO, k, v)
    return lineas, None


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox("Abri un diseno de Fusion antes de correr el script.")
            return
        lineas, error = armar(design)
        if error:
            ui.messageBox(error, "Armar PRUEBA 1")
            return
        ui.messageBox("%d placas ubicadas.\n\n%s\n\nAhora: PonerHerrajes, despues ExportarPiezas."
                      % (len(lineas), "\n".join(lineas)), "Armar PRUEBA 1")
    except Exception:
        if ui:
            ui.messageBox("Fallo:\n%s" % traceback.format_exc(), "Armar PRUEBA 1")
