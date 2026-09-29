# -*- coding: utf-8 -*-
"""
explotar — vista explotada de un mueble del documento armado (COCINA MLV), desde Fusion.

Se corre por el MCP de Fusion con el documento abierto:

    mod.explotar(ruta_maestra_json, "00-Bandejero", carpeta_salida)

Que hace:
  1. aisla el mueble (apaga los demas),
  2. desplaza cada placa a lo largo de su normal, hacia afuera del mueble; los
     herrajes viajan con la placa que los lleva (la que tiene el agujero);
     puertas y frentes salen hacia adelante; la caja del cajon sale entera
     hacia adelante y se abre un poco,
  3. captura en isometrica a 3000 px y guarda <mueble>_explotada.png,
  4. proyecta el centro de cada placa a la imagen (viewport.modelToViewSpace)
     y escribe <mueble>_explotada.json con {globo, codigo, x, y} para dibujar
     los globos afuera de Fusion,
  5. vuelve todo a su lugar y prende los demas muebles. No guarda el documento.
"""

import json
import math
import os
import re

import adsk.core
import adsk.fusion

MM = 0.1


def _slug(s):
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")


def _tr(dx, dy, dz):
    m = adsk.core.Matrix3D.create()
    m.translation = adsk.core.Vector3D.create(dx * MM, dy * MM, dz * MM)
    return m


def _mult(m_orig, dx, dy, dz):
    m = m_orig.copy()
    t = _tr(dx, dy, dz)
    m.transformBy(t)
    return m


def _dentro(p, caja, margen):
    return all(caja[0][i] - margen <= p[i] <= caja[1][i] + margen for i in range(3))


def explotar(ruta_maestra, nombre_mueble, salida, escala=2, ancho_px=None, alto_px=None,
             separacion=320.0, frente=650.0, cajon=950.0):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent
    vp = app.activeViewport
    with open(ruta_maestra, "r", encoding="utf-8") as f:
        maestra = json.load(f)
    mu = [m for m in maestra["muebles"] if m["nombre"] == nombre_mueble][0]
    piezas = {p["codigo"]: p for p in mu["piezas"]}
    cc = [(mu["caja"][0][i] + mu["caja"][1][i]) / 2.0 for i in range(3)]

    # --- desplazamiento por pieza -------------------------------------------
    desplaz = {}
    caj = [p for p in mu["piezas"] if p["rol"] == "CAJON"]
    ccaj = None
    if caj:
        ccaj = [(min(p["caja"][0][i] for p in caj) + max(p["caja"][1][i] for p in caj)) / 2.0 for i in range(3)]
    for p in mu["piezas"]:
        c = [(p["caja"][0][i] + p["caja"][1][i]) / 2.0 for i in range(3)]
        n = p["normal"]
        rol = p["rol"]
        if rol in ("PUERTA", "FRENTE"):
            d = (0.0, -frente, 0.0)
        elif rol == "CAJON":
            # la caja sale entera hacia adelante y se abre a lo largo de su normal
            s = sum(n[i] * (c[i] - ccaj[i]) for i in range(3))
            s = 1.0 if s >= 0 else -1.0
            d = tuple(n[i] * s * 150.0 + (0.0, -cajon, 0.0)[i] for i in range(3))
        else:
            s = sum(n[i] * (c[i] - cc[i]) for i in range(3))
            if abs(s) < 5.0:                       # placa centrada (estante del medio): hacia arriba/atras
                s = 1.0 if (n[2] >= 0 and n[1] <= 0) else -1.0
            else:
                s = 1.0 if s > 0 else -1.0
            k = separacion * (1.0 + 0.5 * (abs(sum(n[i] * (c[i] - cc[i]) for i in range(3))) / max(1.0, max(mu["caja"][1][i] - mu["caja"][0][i] for i in range(3)))))
            d = tuple(n[i] * s * k for i in range(3))
            if rol == "FONDO":
                d = (0.0, separacion * 1.4, 0.0)
        desplaz[p["codigo"]] = d

    # --- ocurrencias -------------------------------------------------------
    occ_m = None
    for i in range(root.occurrences.count):
        o = root.occurrences.item(i)
        if o.component.name == nombre_mueble:
            occ_m = o
        if not o.fullPathName.startswith("Herrajes"):
            o.isLightBulbOn = (o.component.name == nombre_mueble)
    if occ_m is None:
        raise RuntimeError("no encuentro el mueble %s" % nombre_mueble)

    originales = []
    placas = []       # (codigo, proxy)
    herrajes = []     # proxies
    for k in range(occ_m.childOccurrences.count):
        o = occ_m.childOccurrences.item(k)
        codigo = o.component.name.rsplit(" ", 1)[-1]
        if codigo in piezas:
            placas.append((codigo, o))
        else:
            herrajes.append(o)
    movidos = 0
    for codigo, o in placas:
        d = desplaz[codigo]
        m0 = o.transform2.copy()
        originales.append((o, m0))
        o.transform2 = _mult(m0, *d)
        movidos += 1
    # herrajes: van con la placa que contiene su origen + 5 mm hacia adentro (eje Z del herraje)
    for o in herrajes:
        m0 = o.transform2.copy()
        t = m0.translation
        (_, xa, ya, za) = m0.getAsCoordinateSystem()
        p = [t.x / MM + za.x * 5.0, t.y / MM + za.y * 5.0, t.z / MM + za.z * 5.0]
        duenio = None
        for codigo, _o in placas:
            if _dentro(p, piezas[codigo]["caja"], 1.5):
                duenio = codigo
                break
        if duenio is None:
            for codigo, _o in placas:
                if _dentro([t.x / MM, t.y / MM, t.z / MM], piezas[codigo]["caja"], 6.0):
                    duenio = codigo
                    break
        if duenio is None:
            continue
        originales.append((o, m0))
        o.transform2 = _mult(m0, *desplaz[duenio])

    # --- captura -----------------------------------------------------------
    cam = vp.camera
    cam.viewOrientation = adsk.core.ViewOrientations.IsoTopLeftViewOrientation
    cam.isFitView = True
    cam.isPerspective = False
    vp.camera = cam
    vp.fit()
    vp.refresh()
    adsk.doEvents()
    # la imagen se renderiza con la MISMA proporcion que el viewport, si no la
    # proyeccion de modelToViewSpace no coincide con la captura
    if ancho_px is None:
        ancho_px, alto_px = int(vp.width * escala), int(vp.height * escala)
    os.makedirs(salida, exist_ok=True)
    base = os.path.join(salida, _slug(nombre_mueble) + "_explotada")
    vp.saveAsImageFile(base + ".png", ancho_px, alto_px)
    # el "view space" de Fusion esta en pixeles FISICOS (Retina: 2 por pixel logico),
    # origen arriba a la izquierda. El target de la camara cae en el centro.
    q0 = vp.modelToViewSpace(vp.camera.target)
    dpr = (2.0 * q0.x) / float(vp.width) if q0.x > 0 else 1.0
    dpr = round(dpr) or 1.0
    sx = ancho_px / (float(vp.width) * dpr)
    sy = alto_px / (float(vp.height) * dpr)
    puntos = []
    for codigo, o in placas:
        bb = o.bRepBodies.item(0).boundingBox
        c = adsk.core.Point3D.create((bb.minPoint.x + bb.maxPoint.x) / 2, (bb.minPoint.y + bb.maxPoint.y) / 2,
                                     (bb.minPoint.z + bb.maxPoint.z) / 2)
        v = vp.modelToViewSpace(c)
        esquinas = []
        for x in (bb.minPoint.x, bb.maxPoint.x):
            for y in (bb.minPoint.y, bb.maxPoint.y):
                for z in (bb.minPoint.z, bb.maxPoint.z):
                    q = vp.modelToViewSpace(adsk.core.Point3D.create(x, y, z))
                    esquinas.append([q.x * sx, q.y * sy])
        p = piezas[codigo]
        puntos.append(dict(globo=p["globo"], codigo=codigo, nombre=p["nombre"], x=v.x * sx, y=v.y * sy,
                           esquinas=esquinas))
    with open(base + ".json", "w", encoding="utf-8") as f:
        json.dump(dict(mueble=nombre_mueble, ancho=ancho_px, alto=alto_px, viewport=[vp.width, vp.height],
                       piezas=puntos), f, ensure_ascii=False, indent=1)

    # --- restaurar ---------------------------------------------------------
    for o, m0 in originales:
        o.transform2 = m0
    for i in range(root.occurrences.count):
        o = root.occurrences.item(i)
        o.isLightBulbOn = not o.fullPathName.startswith("Herrajes")
    vp.fit()
    vp.refresh()
    return dict(png=base + ".png", json=base + ".json", placas=movidos, herrajes=len(originales) - movidos)
