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
    repintar()                          -> cobre/vidrio a tiradores, perillas y vidrios
                                           (en otra corrida; ver la nota de la funcion)

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
    # escotaduras (esquinas recortadas, p. ej. por la viga): se restan como cajas. El contorno
    # resultante NO es convexo, asi que en ese caso no se usa el recorte por semiplanos de abajo.
    for e in pz.get("escotaduras", []):
        herr.append(A.caja(tbm, e["x1"] - 1.0 if e["x1"] <= 0.01 else e["x1"], e["x2"] + 1.0 if e["x2"] >= W - 0.01 else e["x2"],
                           e["y1"] - 1.0 if e["y1"] <= 0.01 else e["y1"], e["y2"] + 1.0 if e["y2"] >= H - 0.01 else e["y2"],
                           -T - 1.0, 1.0))
    # contorno: cada lado DIAGONAL se recorta con una caja grande (semiplano). Los lados paralelos a
    # los ejes que no caen sobre el rectangulo son de una escotadura y ya se restaron como caja.
    if pz.get("contorno"):
        pts = pz["contorno"]
        B = 3000.0
        for i in range(len(pts)):
            (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % len(pts)]
            if abs(x1 - x2) < 1e-6 or abs(y1 - y2) < 1e-6:
                continue                        # paralelo a un eje: borde o escotadura
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
    # router: ventanas pasantes y cajeados (vitrinas)
    for v in pz.get("ventanas", []):
        herr.append(A.caja(tbm, v["x1"], v["x2"], v["y1"], v["y2"], -T - 1.0, 1.0))
    for r in pz.get("rebajes", []):
        if r["cara"] == "A":
            za, zb = -r["prof"], 1.0
        else:
            za, zb = -T - 1.0, -T + r["prof"]
        herr.append(A.caja(tbm, r["x1"], r["x2"], r["y1"], r["y2"], za, zb))
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


def _forma_tirador(entre_centros):
    """Barral: dos postes O8 de 35 y una barra O12; marco: origen en el centro del
    barral sobre la cara vista, Z saliendo del frente, X a lo largo del barral."""
    e = entre_centros / 2.0

    def f(tbm):
        A = ADR()
        partes = [A.cil(tbm, (-e, 0, 0), (-e, 0, 35.0), 8.0), A.cil(tbm, (e, 0, 0), (e, 0, 35.0), 8.0),
                  A.cil(tbm, (-e - 16.0, 0, 41.0), (e + 16.0, 0, 41.0), 12.0)]
        return partes
    return f


def _forma_perilla(tbm):
    A = ADR()
    return [A.cil(tbm, (0, 0, 0), (0, 0, 22.0), 10.0), A.cil(tbm, (0, 0, 22.0), (0, 0, 38.0), 30.0)]


def _forma_vidrio(a):
    def f(tbm):
        A = ADR()
        return [A.caja(tbm, 0.0, a["ancho"], 0.0, a["alto"], 0.0, a["espesor"])]
    return f


def _forma_bacha(a):
    """Bacha sobre mesada: origen en el centro, sobre la cara de la mesada, Z arriba.
    Pestana apoyada sobre la mesada, cuba por el calado, agujero del desague."""
    def f(tbm):
        A = ADR()
        L, W, P = a["largo"], a["ancho"], a["prof"]
        cL, cW = a["corte"]
        e = a["pestana"]
        pest = A.caja(tbm, -L / 2, L / 2, -W / 2, W / 2, 0.0, e)
        cuba = A.caja(tbm, -cL / 2, cL / 2, -cW / 2, cW / 2, -P, 0.0)
        hueco = A.caja(tbm, -cL / 2 + 10, cL / 2 - 10, -cW / 2 + 10, cW / 2 - 10, -P + 10, e + 1)
        desague = A.cil(tbm, (0, 0, -P - 1), (0, 0, -P + 11), a["desague_d"])
        try:
            tbm.booleanOperation(cuba, pest, adsk.fusion.BooleanTypes.UnionBooleanType)
        except Exception:
            pass
        A.resta(tbm, cuba, [hueco, desague])
        return [cuba]
    return f


def _forma_escurreplatos(a):
    """Dos rejillas de alambre entre laterales. Origen: centro en planta, a la altura de la cara
    de abajo del estante fijo; Z hacia ABAJO. Rejilla = marco O8 + alambres O4 cada 40."""
    def f(tbm):
        A = ADR()
        w, p, h = a["ancho"], a["prof"], a["rejilla"]
        partes = []
        for zt in (a["z_platos"], a["z_vasos"]):
            zb = zt + h
            for (x0, x1, y0, y1) in ((-w / 2, w / 2, -p / 2, -p / 2 + 8), (-w / 2, w / 2, p / 2 - 8, p / 2),
                                     (-w / 2, -w / 2 + 8, -p / 2, p / 2), (w / 2 - 8, w / 2, -p / 2, p / 2)):
                partes.append(A.caja(tbm, x0, x1, y0, y1, zt, zb))
            n = int(w // 40)
            for i in range(1, n):
                x = -w / 2 + i * w / n
                partes.append(A.caja(tbm, x - 2, x + 2, -p / 2, p / 2, zb - 4, zb))
            # alambres verticales (apoyo de los platos) cada 40, 60 de alto
            if zt == a["z_platos"]:
                for i in range(1, n):
                    x = -w / 2 + i * w / n
                    partes.append(A.caja(tbm, x - 2, x + 2, -p / 2 + 60, -p / 2 + 64, zt - 60, zt))
                    partes.append(A.caja(tbm, x - 2, x + 2, p / 2 - 64, p / 2 - 60, zt - 60, zt))
        return partes
    return f


def _forma_cubiertero(a):
    """Canasto de cubiertos colgado de la rejilla de abajo: caja de malla (paredes de 2)."""
    def f(tbm):
        A = ADR()
        w, p, h, z0 = a["ancho"], a["prof"], a["alto"], a["z0"]
        caja = A.caja(tbm, -w / 2, w / 2, -p / 2, p / 2, z0, z0 + h)
        hueco = A.caja(tbm, -w / 2 + 2, w / 2 - 2, -p / 2 + 2, p / 2 - 2, z0 - 1, z0 + h - 2)
        A.resta(tbm, caja, [hueco])
        ganchos = [A.caja(tbm, -w / 2 + 10, -w / 2 + 14, -p / 2, p / 2, z0 - 8, z0 + 2),
                   A.caja(tbm, w / 2 - 14, w / 2 - 10, -p / 2, p / 2, z0 - 8, z0 + 2)]
        return [caja] + ganchos
    return f


def _forma_campana(a):
    """Campana extensible colgada bajo el piso: origen en el centro del mueble sobre la pared, a la
    altura del piso; Z arriba, Y hacia el frente. Cuerpo + visor extensible (cerrado) + filtros."""
    def f(tbm):
        A = ADR()
        w, h, p, fr = a["ancho"], a["alto"], a["prof"], a["frente"]
        cuerpo = A.caja(tbm, -w / 2, w / 2, fr - p, fr, -h, 0.0)
        hueco = A.caja(tbm, -w / 2 + 15, w / 2 - 15, fr - p + 15, fr - 60, -h - 1, -8.0)   # rejilla de filtros
        A.resta(tbm, cuerpo, [hueco])
        filtros = A.caja(tbm, -w / 2 + 20, w / 2 - 20, fr - p + 20, fr - 65, -h + 2, -h + 10)
        visor = A.caja(tbm, -w / 2, w / 2, fr - 60, fr, -h, -h + 40)
        return [cuerpo, filtros, visor]
    return f


def _forma_ducto(a):
    """Ducto O150: vertical desde la salida de la campana (y = prof de la pared) hasta `alto`, y codo
    horizontal hasta la pared (y = -30, dentro de la salida de aire)."""
    def f(tbm):
        A = ADR()
        d, yp, h = a["d"], a["prof"], a["alto"]
        return [A.cil(tbm, (0, yp, 0), (0, yp, h), d), A.cil(tbm, (0, yp, h), (0, -30.0, h), d)]
    return f


def _forma_salida_aire(a):
    def f(tbm):
        A = ADR()
        return [A.cil(tbm, (0, 0, -60.0), (0, 0, 2.0), a["d"] + 20), A.cil(tbm, (0, 0, -61.0), (0, 0, 3.0), a["d"])]
    return f


def _forma_parrilla(a):
    """Cruz de listones pegada al frente del vidrio: origen en la esquina del hueco,
    Z hacia el frente; cols-1 listones verticales y filas-1 horizontales."""
    def f(tbm):
        A = ADR()
        w, h, L, e = a["ancho"], a["alto"], a["liston"], a["esp"]
        partes = []
        # el marco (ez hacia el frente, ex a lo ancho) tiene ey hacia ABAJO: origen en la
        # esquina de arriba del hueco y se dibuja en +y
        for i in range(1, a["cols"]):
            x = w * i / a["cols"]
            partes.append(A.caja(tbm, x - L / 2.0, x + L / 2.0, 0.0, h, 0.0, e))
        for j in range(1, a["filas"]):
            y = h * j / a["filas"]
            partes.append(A.caja(tbm, 0.0, w, y - L / 2.0, y + L / 2.0, 0.0, e))
        return partes
    return f


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
    if f == "tirador":
        return _forma_tirador(a["entre_centros"])
    if f == "perilla":
        return _forma_perilla
    if f == "vidrio":
        return _forma_vidrio(a)
    if f == "parrilla":
        return _forma_parrilla(a)
    if f == "bacha":
        return _forma_bacha(a)
    if f == "campana":
        return _forma_campana(a)
    if f == "ducto":
        return _forma_ducto(a)
    if f == "salida_aire":
        return _forma_salida_aire(a)
    if f == "escurreplatos":
        return _forma_escurreplatos(a)
    if f == "cubiertero":
        return _forma_cubiertero(a)
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
    for item in cajas:
        nombre, (x0, x1, y0, y1, z0, z1), rgb = item[0], item[1], item[2]
        cuerpo_t = A.caja(tbm, x0, x1, y0, y1, z0, z1)
        restas = [A.caja(tbm, *r) for r in (item[3] if len(item) > 3 else [])]   # p. ej. el calado de la bacha
        if restas:
            A.resta(tbm, cuerpo_t, restas)
        b = comp.bRepBodies.add(cuerpo_t)
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
    # tiradores, perillas y vidrios: dentro de armar() la apariencia no prende (ver repintar());
    # se intenta igual y despues hay que llamar a repintar() en otra corrida.
    ap_cobre = A._de_biblioteca(app, design, "Copper - Polished") or ap_metal
    ap_vidrio = A._de_biblioteca(app, design, "Glass (Clear)") or ap_metal
    if herrajes:
        for h in modelo["herrajes"]:
            try:
                ap = {"led": ap_led, "tirador": ap_cobre, "perilla": ap_cobre,
                      "vidrio": ap_vidrio, "parrilla": _apariencia(app, design, "VERDE")}.get(h["forma"], ap_metal)
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


def repintar():
    """Cobre a tiradores y perillas, vidrio a los vidrios. Hay que correrlo en una corrida
    APARTE despues de armar(): dentro de armar() `cuerpo.appearance = ap` no da error pero
    el cuerpo queda "Steel - Satin" (18/10/2026, no se entendio por que; en una corrida
    nueva anda). Igual para las placas no hace falta."""
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    A = ADR()
    cobre = A._de_biblioteca(app, design, "Copper - Polished")
    vidrio = A._de_biblioteca(app, design, "Glass (Clear)")
    n = 0
    for comp in design.allComponents:
        ap = {"Tirador": cobre, "Perilla": cobre, "Vidrio": vidrio,
              "Parrilla": _apariencia(app, design, "VERDE")}.get(comp.name.split()[0])
        if ap is None:
            continue
        for b in comp.bRepBodies:
            b.appearance = ap
            n += 1
    return n


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
