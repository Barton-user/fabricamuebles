# -*- coding: utf-8 -*-
"""
ArmarReceta — arma en Fusion un ambiente que viene de una RECETA en codigo
(recetas/<receta>.py -> salida/<ORDEN>/modelo.json), con todos los agujeros ya
hechos y los herrajes de la biblioteca puestos.

Es el gemelo de ArmarDesdeRender: aquel lee el render.json de GuiGui, este lee
el modelo.json de una receta propia. Las formas de herraje y la biblioteca de
STEP son las mismas (se importan de ArmarDesdeRender / PonerHerrajes).

    armar(ruta_modelo, nuevo=True)      -> documento nuevo, modo directo
    exportar(carpeta)                   -> piezas.json + GENERAR ARCHIVOS.command
                                           (lo mismo que ExportarPiezas, sin dialogos)

Cada placa: un componente con la placa ACOSTADA adentro (X ancho, Y alto, cara
A en z=0, espesor hacia -Z), ubicado con la matriz de la ocurrencia. Es la
convencion de ExportarPiezas, que despues LEE EL SOLIDO: los archivos de
maquina salen de la geometria, no de la receta. Por eso la receta tambien
escribe piezas_receta.json, para comparar las dos cosas.

Los cuerpos de referencia (mesada, cocina, lavavajillas, bacha) van marcados
TIPO=REFERENCIA y no se exportan.
"""

import importlib.util
import io
import json
import math
import os
import traceback

import adsk.core
import adsk.fusion

GRUPO = "FabricaMuebles"
MM = 0.1
AQUI = os.path.dirname(os.path.abspath(__file__))
FUSION = os.path.dirname(AQUI)
ADR_PATH = os.path.join(FUSION, "ArmarDesdeRender", "ArmarDesdeRender.py")
EP_PATH = os.path.join(FUSION, "ExportarPiezas", "ExportarPiezas.py")
ETAPA2 = os.path.join(os.path.dirname(FUSION), "etapa2")

COLORES = {"VERDE": (79, 97, 66), "BLANCO": (240, 239, 235), "PET GRIS": (72, 73, 76), "GRIS": (150, 151, 147)}

_MOD = {}


def _cargar(nombre, ruta):
    if nombre not in _MOD:
        spec = importlib.util.spec_from_file_location(nombre, ruta)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        _MOD[nombre] = m
    return _MOD[nombre]


def ADR():
    return _cargar("ArmarDesdeRender", ADR_PATH)


# --------------------------------------------------------------- placas --
def cuerpo_placa(tbm, pz):
    A = ADR()
    W, H, T = pz["W"], pz["H"], pz["T"]
    cuerpo = A.caja(tbm, 0.0, W, 0.0, H, -T, 0.0)
    herr = []
    # contorno: cada lado que no cae sobre el rectangulo se recorta con una caja grande
    if pz.get("contorno"):
        pts = pz["contorno"]
        B = 3000.0
        for i in range(len(pts)):
            (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % len(pts)]
            sobre = (abs(x1 - x2) < 1e-6 and (abs(x1) < 1e-6 or abs(x1 - W) < 1e-6)) or \
                    (abs(y1 - y2) < 1e-6 and (abs(y1) < 1e-6 or abs(y1 - H) < 1e-6))
            if sobre:
                continue
            L = math.hypot(x2 - x1, y2 - y1)
            ux, uy = (x2 - x1) / L, (y2 - y1) / L
            nx, ny = uy, -ux                     # hacia afuera (contorno CCW)
            cx, cy = (x1 + x2) / 2.0 + nx * B / 2.0, (y1 + y2) / 2.0 + ny * B / 2.0
            obb = adsk.core.OrientedBoundingBox3D.create(
                A.p3(cx, cy, -T / 2.0), adsk.core.Vector3D.create(ux, uy, 0),
                adsk.core.Vector3D.create(nx, ny, 0), (L + 2 * B) * MM, B * MM, (T + 4.0) * MM)
            herr.append(tbm.createBox(obb))
    for h in pz["agujeros"]:
        if h["cara"] == "A":
            a, b = (h["x"], h["y"], 1.0), (h["x"], h["y"], -h["prof"])
        else:
            a, b = (h["x"], h["y"], -T - 1.0), (h["x"], h["y"], -T + h["prof"])
        herr.append(A.cil(tbm, a, b, h["d"]))
    for h in pz["agujeros_canto"]:
        dx, dy = {"IZQ": (1, 0), "DER": (-1, 0), "ABAJO": (0, 1), "ARRIBA": (0, -1)}[h["canto"]]
        z = -h["z"]
        a = (h["x"] - dx * 1.0, h["y"] - dy * 1.0, z)
        b = (h["x"] + dx * h["prof"], h["y"] + dy * h["prof"], z)
        herr.append(A.cil(tbm, a, b, h["d"]))
    for s in pz["ranuras"]:
        x1, x2 = sorted((s["x1"], s["x2"]))
        y1, y2 = sorted((s["y1"], s["y2"]))
        w = s["ancho"]
        if abs(x2 - x1) < 1e-6:
            x1, x2 = x1 - w / 2.0, x2 + w / 2.0
        else:
            y1, y2 = y1 - w / 2.0, y2 + w / 2.0
        if x1 <= 0.01: x1 -= 1.0
        if y1 <= 0.01: y1 -= 1.0
        if x2 >= W - 0.01: x2 += 1.0
        if y2 >= H - 0.01: y2 += 1.0
        if s["cara"] == "A":
            za, zb = -s["prof"], 1.0
        else:
            za, zb = -T - 1.0, -T + s["prof"]
        herr.append(A.caja(tbm, x1, x2, y1, y2, za, zb))
    n = A.resta(tbm, cuerpo, herr)
    return cuerpo, len(herr) - n


def marcar(cuerpo, pz):
    c = pz["cantos"]
    datos = {"TIPO": "PLACA", "NOMBRE": pz["nombre"], "CODIGO": pz["codigo"],
             "MATERIAL": pz["material"], "TEXTURA": pz["textura"], "VETA": pz["veta"],
             "MUEBLE": pz["mueble"], "ROL": pz["rol"],
             "CANTO_ABAJO": c["ABAJO"], "CANTO_ARRIBA": c["ARRIBA"],
             "CANTO_IZQ": c["IZQ"], "CANTO_DER": c["DER"]}
    for k, v in datos.items():
        cuerpo.attributes.add(GRUPO, k, str(v))
    # el O8 del 3 en 1 desemboca en el O15: el solido lo mide corto. Se deja escrito.
    profs = [h["prof"] for h in pz["agujeros_canto"] if abs(h["d"] - 8.0) < 0.5]
    if profs:
        cuerpo.attributes.add(GRUPO, "PROF_CANTO_8", "%g" % max(profs))


def _apariencia(app, design, textura):
    for k, rgb in COLORES.items():
        if k in (textura or "").upper():
            return ADR()._color(app, design, rgb, k.lower())
    return ADR().apariencia_textura(app, design, textura)


# ------------------------------------------------------------- herrajes --
def _forma_pin(tbm):
    A = ADR()
    return [A.cil(tbm, (0, 0, -1.0), (0, 0, 9.0), 4.8), A.caja(tbm, -3.5, 3.5, -2.0, 8.0, -3.0, -1.0)]


def _forma_pata(tbm):
    A = ADR()
    # marco: origen bajo el piso del mueble, Z hacia abajo
    return [A.cil(tbm, (0, 0, 0), (0, 0, 4.0), 60.0), A.cil(tbm, (0, 0, 4.0), (0, 0, 92.0), 28.0),
            A.cil(tbm, (0, 0, 92.0), (0, 0, 99.5), 50.0)]


def forma(h):
    A = ADR()
    PH = A._ph()
    a = h["args"]
    f = h["forma"]
    if f == "excentrica":
        return lambda tbm: PH._forma_excentrica(tbm, a["cam"])
    if f == "perno":
        return lambda tbm: PH._forma_perno(tbm, a["perno"], a["recibe"])
    if f == "receptor":
        return lambda tbm: PH._forma_receptor(tbm, a["recibe"])
    if f == "bisagra":
        return lambda tbm: PH._forma_bisagra(tbm, a["dx_lat"])
    if f == "corredera":
        return lambda tbm: A.forma_corredera_bolas(tbm, a["largo"])
    if f == "led":
        return lambda tbm: A.forma_led(tbm, a["largo"])
    if f == "pin":
        return _forma_pin
    if f == "pata":
        return _forma_pata
    raise ValueError("forma desconocida: %s" % f)


# ----------------------------------------------------------- referencia --
def referencia(design, root, app, cajas):
    """Mesada, electrodomesticos y bacha como cajas grises marcadas TIPO=REFERENCIA."""
    A = ADR()
    tbm = adsk.fusion.TemporaryBRepManager.get()
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "Referencia (no se fabrica)"
    comp.attributes.add(GRUPO, "TIPO", "REFERENCIA")
    for nombre, (x0, x1, y0, y1, z0, z1), rgb in cajas:
        b = comp.bRepBodies.add(A.caja(tbm, x0, x1, y0, y1, z0, z1))
        b.name = nombre
        b.attributes.add(GRUPO, "TIPO", "REFERENCIA")
        ap = A._color(app, design, rgb, "ref " + nombre)
        if ap is not None:
            try:
                b.appearance = ap
            except Exception:
                pass
    return occ


REFERENCIA = [
    ("Mesada pared larga", (0, 2190, 0, 620, 860, 900), (214, 220, 222)),
    ("Mesada pared corta", (0, 620, 620, 800, 860, 900), (214, 220, 222)),
    ("Cocina 550x650", (0, 650, 800, 1350, 0, 900), (190, 180, 176)),
    ("Lavavajillas 450", (1720, 2170, 0, 590, 40, 850), (225, 225, 225)),
    ("Bacha (hueco)", (850, 1350, 110, 510, 660, 861), (200, 185, 180)),
]


def matriz_orto(O, ex, ey):
    """Matriz con ex, ey re-ortonormalizados: el JSON trae 7 decimales y Fusion
    rechaza ejes que no son exactamente perpendiculares (diagonales a 45)."""
    x = adsk.core.Vector3D.create(*ex); x.normalize()
    y = adsk.core.Vector3D.create(*ey)
    k = y.dotProduct(x)
    y = adsk.core.Vector3D.create(y.x - k * x.x, y.y - k * x.y, y.z - k * x.z); y.normalize()
    z = x.crossProduct(y)
    m = adsk.core.Matrix3D.create()
    m.setWithCoordinateSystem(ADR().p3(*O), x, y, z)
    return m


# ---------------------------------------------------------------- armar --
def armar(ruta_modelo, nuevo=True, herrajes=True, log_print=True):
    app = adsk.core.Application.get()
    log = []
    L = log.append
    with io.open(ruta_modelo, encoding="utf-8") as fh:
        modelo = json.load(fh)
    if nuevo:
        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        design.designType = adsk.fusion.DesignTypes.DirectDesignType
        try:
            design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
        except Exception:
            pass
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent
    A = ADR()
    tbm = adsk.fusion.TemporaryBRepManager.get()
    PH = A._ph()
    ap_metal = PH._apariencia_metal()
    ap_led = A._apariencia_led(app, design)

    occs = {}
    for pz in modelo["piezas"]:
        mu = pz["mueble"]
        if mu not in occs:
            o = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
            o.component.name = mu
            o.component.attributes.add(GRUPO, "MUEBLE", mu)
            occs[mu] = o
    n_placas = n_fallas = 0
    for pz in modelo["piezas"]:
        try:
            padre = occs[pz["mueble"]]
            occ = padre.component.occurrences.addNewComponent(matriz_orto(pz["O"], pz["ex"], pz["ey"]))
            comp = occ.component
            comp.name = "%s %s" % (pz["pieza"], pz["codigo"])
            cuerpo_t, fallas = cuerpo_placa(tbm, pz)
            if fallas:
                L("  aviso: %s: %d mecanizados no se pudieron restar" % (pz["nombre"], fallas))
                n_fallas += fallas
            cuerpo = comp.bRepBodies.add(cuerpo_t)
            cuerpo.name = pz["codigo"]
            marcar(cuerpo, pz)
            ap = _apariencia(app, design, pz["textura"])
            if ap is not None:
                try:
                    cuerpo.appearance = ap
                except Exception:
                    pass
            n_placas += 1
        except Exception:
            L("  ERROR en %s:\n%s" % (pz["nombre"], traceback.format_exc()))
    n_h = 0
    if herrajes:
        for h in modelo["herrajes"]:
            try:
                ap = ap_led if h["forma"] == "led" else ap_metal
                m = A.marco(h["origen"], h["ez"], h["ex"])
                A.herraje(design, occs[h["mueble"]] if h["mueble"] in occs else _occ_extra(root, occs, h["mueble"]),
                          h["nombre"], m, forma(h), ap)
                n_h += 1
            except Exception:
                L("  ERROR herraje %s en %s: %s" % (h["nombre"], h["mueble"], traceback.format_exc()))
    referencia(design, root, app, modelo.get("referencia", REFERENCIA))
    for k, v in {"ORDEN": modelo.get("orden", ""), "CLIENTE": modelo.get("cliente", ""),
                 "AMBIENTE": modelo.get("ambiente", ""), "EJE_ARRIBA": "+Z", "EJE_FRENTE": "+Y",
                 "RUTA_ETAPA2": ETAPA2}.items():
        root.attributes.add(GRUPO, k, str(v))
    L("TOTAL: %d placas (%d mecanizados fallidos), %d herrajes" % (n_placas, n_fallas, n_h))
    if log_print:
        print("\n".join(log))
    return log


def _occ_extra(root, occs, nombre):
    o = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    o.component.name = nombre
    occs[nombre] = o
    return o


# ------------------------------------------------------------- exportar --
def exportar(carpeta):
    """ExportarPiezas sin dialogo: piezas.json + diagnostico.txt + lanzador."""
    EP = _cargar("ExportarPiezas", EP_PATH)
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    os.makedirs(carpeta, exist_ok=True)
    del EP._log[:]
    EP.log("Exportar Piezas — %s" % design.parentDocument.name)
    piezas, saltadas = EP.recolectar(design)
    vistos, dup = {}, []
    for p in piezas:
        if p["codigo"] in vistos:
            dup.append(p["codigo"])
        vistos[p["codigo"]] = 1
    raiz = design.rootComponent
    datos = {"version": 1, "origen": "fusion", "documento": design.parentDocument.name,
             "orden": str(EP.attr(raiz, "ORDEN", "")), "cliente": str(EP.attr(raiz, "CLIENTE", "")),
             "direccion": "", "ambiente": str(EP.attr(raiz, "AMBIENTE", "")), "piezas": piezas}
    with io.open(os.path.join(carpeta, "piezas.json"), "w", encoding="utf-8") as fh:
        json.dump(datos, fh, ensure_ascii=False, indent=2)
    EP.escribir_lanzador(carpeta, ETAPA2)
    for s in saltadas:
        EP.log("SALTADA: %s" % s)
    with io.open(os.path.join(carpeta, "diagnostico.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(EP._log))
    return len(piezas), saltadas, dup


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        dlg = ui.createFileDialog()
        dlg.title = "Elegir el modelo.json de la receta"
        dlg.filter = "JSON (*.json)"
        if dlg.showOpen() != adsk.core.DialogResults.DialogOK:
            return
        log = armar(dlg.filename, nuevo=True, log_print=False)
        ui.messageBox("\n".join(log[-20:]), "Armar receta")
    except Exception:
        if ui:
            ui.messageBox("Fallo:\n%s" % traceback.format_exc(), "Armar receta")
