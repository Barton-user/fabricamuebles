# -*- coding: utf-8 -*-
"""
MoverPuertas — juntas de Fusion para abrir puertas y cajones de un ambiente
armado con ArmarReceta (o ArmarDesdeRender).

    preparar(ruta_modelo)   -> pasa el diseno a parametrico, fija el cuerpo de
                               los muebles y crea:
                                 * una junta de REVOLUCION por puerta, sobre el
                                   canto de bisagras (cara de afuera), 0..90 grados,
                                   con sus bisagras pegadas a la puerta
                                 * una junta DESLIZANTE por cajon (frente + caja
                                   en un grupo rigido), 0..400 mm
    mover(abierto)          -> 0..1: lleva todas las juntas a esa fraccion
    animar(carpeta, ...)    -> cuadros PNG abriendo y cerrando, para armar un GIF

Despues en Fusion: ENSAMBLAR -> "Accionar juntas" (Drive Joints) o "Estudio de
movimiento" (Motion Study) para verlo en vivo; clic derecho sobre una junta en el
navegador -> "Editar limites".

OJO: correr sobre una COPIA del documento de produccion. Las juntas no tocan la
geometria de las placas (ExportarPiezas lee cada placa en su componente), pero el
documento pasa a parametrico.

Notas de la API que costaron (29/09/2026):
  * las juntas "as-built" solo existen en diseno parametrico
  * con geometria de punto (vertice), CustomJointDirection + arista se ignora y
    gira sobre el Z local del componente; hay que usar el eje LOCAL: las puertas
    y frentes de la receta tienen Y local = vertical -> YAxisJointDirection para
    girar, ZAxisJointDirection (espesor) para deslizar
  * la junta queda en el componente del mueble, no en el raiz
"""

import io
import json
import math
import os
import traceback

import adsk.core
import adsk.fusion

MM = 0.1
ABRE_PUERTA = 90.0          # grados (a 95 dos puertas vecinas con bisagra en el mismo encuentro se tocan)
ABRE_CAJON = 400.0          # mm (corredera 450 de extension total)


def _occs(root):
    return [root.allOccurrences.item(i) for i in range(root.allOccurrences.count)]


def _codigo(occ):
    n = occ.component.name
    return n.rsplit(" ", 1)[-1] if " " in n else ""


def _mundo(occ, p_mm):
    p = adsk.core.Point3D.create(p_mm[0] * MM, p_mm[1] * MM, p_mm[2] * MM)
    p.transformBy(occ.transform2)
    return p


def _vertice(occ, p_mm):
    """Vertice del cuerpo de la placa mas cercano al punto local p (mm)."""
    obj = _mundo(occ, p_mm)
    mejor = None
    for v in occ.bRepBodies.item(0).vertices:
        dd = v.geometry.distanceTo(obj)
        if mejor is None or dd < mejor[0]:
            mejor = (dd, v)
    return mejor[1]


def _centro(occ):
    b = occ.bRepBodies.item(0).boundingBox
    return adsk.core.Point3D.create((b.minPoint.x + b.maxPoint.x) / 2, (b.minPoint.y + b.maxPoint.y) / 2,
                                    (b.minPoint.z + b.maxPoint.z) / 2)


def _frente(occ):
    """Hacia afuera del mueble = -Z local de la puerta/frente (la cara A mira adentro)."""
    m = occ.transform2
    z = adsk.core.Vector3D.create(0, 0, -1)
    z.transformBy(m)
    return z


def _avance(occ, antes):
    c = _centro(occ)
    d = adsk.core.Vector3D.create(c.x - antes.x, c.y - antes.y, c.z - antes.z)
    return d.dotProduct(_frente(occ))


def preparar(ruta_modelo, log_print=True):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent
    log = []
    L = log.append
    with io.open(ruta_modelo, encoding="utf-8") as fh:
        modelo = json.load(fh)
    piezas = {p["codigo"]: p for p in modelo["piezas"]}

    if design.designType != adsk.fusion.DesignTypes.ParametricDesignType:
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        L("diseno pasado a parametrico")
    # borrar juntas y grupos de una corrida anterior
    for c in design.allComponents:
        for j in [c.asBuiltJoints.item(i) for i in range(c.asBuiltJoints.count)]:
            j.deleteMe()
        for g in [c.rigidGroups.item(i) for i in range(c.rigidGroups.count)]:
            g.deleteMe()

    occs = _occs(root)
    por_codigo = {}
    for o in occs:
        c = _codigo(o)
        if c in piezas and o.bRepBodies.count:
            por_codigo[c] = o

    moviles = set()
    puertas, cajones = [], {}
    for c, o in por_codigo.items():
        pz = piezas[c]
        if pz["pieza"].startswith("Puerta"):
            puertas.append((pz, o))
        elif pz["pieza"].startswith("Frente cajon") or pz["pieza"].startswith("Cajon "):
            num = pz["pieza"].split()[2] if pz["pieza"].startswith("Frente") else pz["pieza"].split()[1]
            cajones.setdefault((pz["mueble"], num), []).append((pz, o))

    # bisagras: herraje cuyo origen cae a menos de 30 mm de una cazoleta de la puerta
    bisagras = [o for o in occs if o.component.name.startswith("Bisagra") and
                not o.fullPathName.startswith("Herrajes")]

    # fijar todo lo que no se mueve
    for pz, o in puertas:
        moviles.add(o.fullPathName)
    for grupo in cajones.values():
        for pz, o in grupo:
            moviles.add(o.fullPathName)

    # ANCLAR todo lo que no se mueve. Sin esto, al arrastrar una puerta con el mouse
    # (o con Accionar juntas) Fusion resuelve la junta moviendo el LATERAL en vez de
    # la puerta y el mueble se desarma (visto el 29/09: laterales girados 20 grados).
    for i in range(root.occurrences.count):
        try:
            root.occurrences.item(i).isGrounded = True
        except Exception:
            pass
    anclados = 0
    for c, o in por_codigo.items():
        if o.fullPathName not in moviles:
            try:
                o.isGrounded = True
                anclados += 1
            except Exception:
                pass
    L("placas fijas ancladas: %d" % anclados)

    n_p = n_c = 0
    for pz, o in puertas:
        try:
            cazoletas = [h for h in pz["agujeros"] if h.get("sym") == "HINGE"]
            if not cazoletas:
                L("  %s / %s: sin cazoletas, no se mueve" % (pz["mueble"], pz["pieza"]))
                continue
            x_c = cazoletas[0]["x"]
            x_eje = 0.0 if x_c < pz["W"] / 2 else pz["W"]
            # soporte = cualquier placa del mismo mueble que no se mueve (el lateral de las bisagras)
            soporte = None
            for c2, o2 in por_codigo.items():
                p2 = piezas[c2]
                if p2["mueble"] == pz["mueble"] and o2.fullPathName not in moviles and \
                        any(h.get("sym") == "jlHoleEX" for h in p2["agujeros"]):
                    w = _mundo(o, (x_eje, 0, 0))
                    cc = _centro(o2)
                    dd = w.distanceTo(cc)
                    if soporte is None or dd < soporte[0]:
                        soporte = (dd, o2)
            soporte = soporte[1]
            # bisagras de esta puerta
            centros = [_mundo(o, (h["x"], h["y"], 0.0)) for h in cazoletas]
            mias = []
            for b in bisagras:
                t = b.transform2.translation
                p = adsk.core.Point3D.create(t.x, t.y, t.z)
                if any(p.distanceTo(cc) < 3.0 for cc in centros):
                    mias.append(b)
            if mias:
                col = adsk.core.ObjectCollection.create()
                col.add(o)
                for b in mias:
                    col.add(b)
                g = root.rigidGroups.add(col, True)
                g.name = "%s %s (con bisagras)" % (pz["mueble"][:2], pz["pieza"])
            geo = adsk.fusion.JointGeometry.createByPoint(_vertice(o, (x_eje, 0.0, -pz["T"])))
            inp = root.asBuiltJoints.createInput(o, soporte, geo)
            inp.setAsRevoluteJointMotion(adsk.fusion.JointDirections.YAxisJointDirection)
            j = root.asBuiltJoints.add(inp)
            j.name = "%s %s" % (pz["mueble"][:2], pz["pieza"])
            jm = j.jointMotion
            antes = _centro(o)
            jm.rotationValue = math.radians(45)
            signo = 1.0 if _avance(o, antes) > 0 else -1.0
            jm.rotationValue = 0.0
            lim = jm.rotationLimits
            if signo > 0:
                lim.isMinimumValueEnabled, lim.minimumValue = True, 0.0
                lim.isMaximumValueEnabled, lim.maximumValue = True, math.radians(ABRE_PUERTA)
            else:
                lim.isMinimumValueEnabled, lim.minimumValue = True, -math.radians(ABRE_PUERTA)
                lim.isMaximumValueEnabled, lim.maximumValue = True, 0.0
            lim.isRestValueEnabled, lim.restValue = True, 0.0
            j.attributes.add("FabricaMuebles", "ABRE", "%g" % signo)
            n_p += 1
        except Exception:
            L("  ERROR puerta %s / %s: %s" % (pz["mueble"], pz["pieza"], traceback.format_exc()))

    for (mueble, num), grupo in sorted(cajones.items()):
        try:
            frente = [o for pz, o in grupo if pz["pieza"].startswith("Frente")][0]
            pzf = [pz for pz, o in grupo if pz["pieza"].startswith("Frente")][0]
            col = adsk.core.ObjectCollection.create()
            for pz, o in grupo:
                col.add(o)
            g = root.rigidGroups.add(col, True)
            g.name = "%s cajon %s" % (mueble[:2], num)
            soporte = None
            for c2, o2 in por_codigo.items():
                p2 = piezas[c2]
                if p2["mueble"] == mueble and any(h.get("sym") == "slideRail" for h in p2["agujeros"]) and \
                        o2.fullPathName not in moviles:
                    soporte = o2
                    break
            geo = adsk.fusion.JointGeometry.createByPoint(_vertice(frente, (0.0, 0.0, -pzf["T"])))
            inp = root.asBuiltJoints.createInput(frente, soporte, geo)
            inp.setAsSliderJointMotion(adsk.fusion.JointDirections.ZAxisJointDirection)
            j = root.asBuiltJoints.add(inp)
            j.name = "%s cajon %s" % (mueble[:2], num)
            jm = j.jointMotion
            antes = _centro(frente)
            jm.slideValue = 10.0
            signo = 1.0 if _avance(frente, antes) > 0 else -1.0
            jm.slideValue = 0.0
            lim = jm.slideLimits
            if signo > 0:
                lim.isMinimumValueEnabled, lim.minimumValue = True, 0.0
                lim.isMaximumValueEnabled, lim.maximumValue = True, ABRE_CAJON * MM
            else:
                lim.isMinimumValueEnabled, lim.minimumValue = True, -ABRE_CAJON * MM
                lim.isMaximumValueEnabled, lim.maximumValue = True, 0.0
            lim.isRestValueEnabled, lim.restValue = True, 0.0
            j.attributes.add("FabricaMuebles", "ABRE", "%g" % signo)
            n_c += 1
        except Exception:
            L("  ERROR cajon %s %s: %s" % (mueble, num, traceback.format_exc()))

    L("juntas: %d puertas, %d cajones" % (n_p, n_c))
    if log_print:
        print("\n".join(log))
    return log


def juntas(design):
    out = []
    for c in design.allComponents:
        for i in range(c.asBuiltJoints.count):
            j = c.asBuiltJoints.item(i)
            a = j.attributes.itemByName("FabricaMuebles", "ABRE")
            if a is not None:
                out.append((j, float(a.value)))
    return out


def mover(abierto, solo=None, design=None):
    """abierto 0..1 (o un dict nombre -> fraccion). solo = prefijo del nombre."""
    design = design or adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    for j, signo in juntas(design):
        if solo and not j.name.startswith(solo):
            continue
        f = abierto.get(j.name, 0.0) if isinstance(abierto, dict) else abierto
        jm = j.jointMotion
        if jm.objectType.endswith("RevoluteJointMotion"):
            jm.rotationValue = signo * math.radians(ABRE_PUERTA) * f
        else:
            jm.slideValue = signo * ABRE_CAJON * MM * f


# Las puertas de los esquineros y la de al lado no se pueden abrir a fondo las dos a
# la vez (con la vecina abierta, la del esquinero llega a 45 grados sin tocar):
# en la animacion van hasta la mitad.
TOPE_ANIMACION = {"B1 Puerta": 0.5, "A1 Puerta": 0.5}


def animar(carpeta, cuadros=24, ancho=1280, alto=960, cuadros_quieto=4, tope=None):
    """Abre todo y lo vuelve a cerrar; escribe cuadro_000.png ... en `carpeta`.

    Las puertas arrancan un poco antes que los cajones (desfasado), con aceleracion
    suave (coseno). Oculta los iconos de las juntas mientras saca los cuadros."""
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    vp = app.activeViewport
    tope = TOPE_ANIMACION if tope is None else tope
    for c in design.allComponents:
        try:
            c.isJointsFolderLightBulbOn = False
        except Exception:
            pass
    os.makedirs(carpeta, exist_ok=True)
    js = juntas(design)
    n = 0
    secuencia = [0.0] * cuadros_quieto + [i / float(cuadros) for i in range(cuadros + 1)] + \
                [1.0] * cuadros_quieto + [1.0 - i / float(cuadros) for i in range(cuadros + 1)]
    for k, t in enumerate(secuencia):
        f = {}
        for j, _ in js:
            retraso = 0.0 if "Puerta" in j.name else 0.25
            u = min(1.0, max(0.0, (t - retraso) / (1.0 - retraso))) if t > 0 else 0.0
            f[j.name] = (0.5 - 0.5 * math.cos(math.pi * u)) * tope.get(j.name, 1.0)
        mover(f, design=design)
        adsk.doEvents()
        vp.refresh()
        vp.saveAsImageFile(os.path.join(carpeta, "cuadro_%03d.png" % n), ancho, alto)
        n += 1
    mover(0.0, design=design)
    return n


# --------------------------------------------------------------------------- #
#  todas juntas: vinculos de movimiento (Motion Link) a una junta maestra
# --------------------------------------------------------------------------- #

MAESTRA = "B2 Puerta der"
PREFIJO_VINCULO = "Todo con "


def _proxy(root, j):
    for i in range(root.occurrences.count):
        o = root.occurrences.item(i)
        if o.component == j.parentComponent:
            return j.createForAssemblyContext(o)
    return j


def desvincular(design=None):
    design = design or adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    n = 0
    for c in design.allComponents:
        for ml in [c.motionLinks.item(i) for i in range(c.motionLinks.count)]:
            ml.deleteMe()
            n += 1
    return n


def vincular(maestra=MAESTRA, tope=None, design=None):
    """Vincula todas las juntas a la maestra: la maestra de 0 a 90 grados lleva
    las puertas de 0 a 90 (los esquineros de 0 a 45) y los cajones de 0 a 400 mm.

    Despues alcanza con mover la maestra: ENSAMBLAR -> Accionar juntas, o el boton
    'Animar' del Vinculo de movimiento, o un Estudio de movimiento con esa sola junta."""
    design = design or adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    root = design.rootComponent
    tope = TOPE_ANIMACION if tope is None else tope
    desvincular(design)
    js = {j.name: (j, s) for j, s in juntas(design)}
    jm_, sm = js[maestra]
    R = adsk.fusion.JointMotionTypes.RevoluteJointRotateMotionType
    S = adsk.fusion.JointMotionTypes.SliderJointSlideMotionType
    log = []
    for nombre, (j, s) in sorted(js.items()):
        if nombre == maestra:
            continue
        es_puerta = j.jointMotion.objectType.endswith("RevoluteJointMotion")
        f = tope.get(nombre, 1.0)
        inp = root.motionLinks.createInput(_proxy(root, jm_), _proxy(root, j))
        inp.motionOne = R
        inp.valueOne = adsk.core.ValueInput.createByString("%g deg" % ABRE_PUERTA)
        inp.motionTwo = R if es_puerta else S
        inp.valueTwo = adsk.core.ValueInput.createByString(
            ("%g deg" % (ABRE_PUERTA * f)) if es_puerta else ("%g mm" % (ABRE_CAJON * f)))
        inp.isReversed = (sm * s) < 0
        ml = root.motionLinks.add(inp)
        ml.name = PREFIJO_VINCULO + nombre
        log.append(ml.name)
    # comprobar: con la maestra abierta, cada junta tiene que abrir (valor * signo > 0)
    jm_.jointMotion.rotationValue = sm * math.radians(ABRE_PUERTA)
    for nombre, (j, s) in sorted(js.items()):
        jm = j.jointMotion
        v = jm.rotationValue if jm.objectType.endswith("RevoluteJointMotion") else jm.slideValue
        if nombre != maestra and v * s <= 0:
            # sentido al reves: se invierte el vinculo
            for ml in [root.motionLinks.item(i) for i in range(root.motionLinks.count)]:
                if ml.name == PREFIJO_VINCULO + nombre:
                    ml.isReversed = not ml.isReversed
                    log.append("  invertido: " + nombre)
    jm_.jointMotion.rotationValue = 0.0
    return log


def en_vivo(vueltas=1, pasos=40, pausa=0.02, maestra=MAESTRA):
    """Abre y cierra todo en la pantalla moviendo la maestra (con los vinculos puestos)."""
    import time
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    js = {j.name: (j, s) for j, s in juntas(design)}
    j, s = js[maestra]
    vp = app.activeViewport
    for _ in range(vueltas):
        for t in [i / float(pasos) for i in range(pasos + 1)] + [1 - i / float(pasos) for i in range(pasos + 1)]:
            u = 0.5 - 0.5 * math.cos(math.pi * t)
            j.jointMotion.rotationValue = s * math.radians(ABRE_PUERTA) * u
            vp.refresh()
            adsk.doEvents()
            time.sleep(pausa)
    j.jointMotion.rotationValue = 0.0


def run(context):
    """Desde Utilidades -> Scripts y complementos: abre y cierra todo dos veces."""
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not juntas(design):
            ui.messageBox("Este documento no tiene las juntas de MoverPuertas.\n"
                          "Abri 'COCINA-01 movimiento'.", "Mover puertas")
            return
        tiene = any(c.motionLinks.count for c in design.allComponents)
        if not tiene:
            vincular(design=design)
        en_vivo(vueltas=2)
    except Exception:
        if ui:
            ui.messageBox("Fallo:\n%s" % traceback.format_exc(), "Mover puertas")
