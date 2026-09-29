# -*- coding: utf-8 -*-
"""
paquete — la lista maestra del paquete de produccion, desde el render.json de GuiGui.

    python3 paquete.py <render.json> -o <carpeta>            -> maestra.json
    python3 paquete.py <render.json> -o <carpeta> --mueble 0  (solo ese mueble)

Todo lo demas del paquete (explotada, plano, lista de materiales, etiquetas) lee
maestra.json: asi el numero de globo, la fila de la lista y la etiqueta apuntan
siempre al mismo codigo.

Por pieza: globo (1..N dentro del mueble, en orden de armado), codigo de 13
digitos (EAN-13 de GuiGui), nombre, mueble, W x H x T (marco h/v de GuiGui),
medidas de corte (menos cantos), material, textura, cantos, veta, rol y la
caja en el mundo de Fusion (para la explotada).

Orden de armado (= orden de globos): laterales y parantes -> horizontales de
abajo hacia arriba -> travesaños y fondos -> puertas y frentes -> cajas de cajon.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import types

AQUI = os.path.dirname(os.path.abspath(__file__))
ADR_PATH = os.path.join(os.path.dirname(AQUI), "fusion", "ArmarDesdeRender", "ArmarDesdeRender.py")


def _cargar_adr():
    """ArmarDesdeRender importa adsk; fuera de Fusion se le da un adsk vacio."""
    if "adsk" not in sys.modules:
        class _Any(object):
            def __getattr__(self, k):
                return _Any()

            def __call__(self, *a, **k):
                return _Any()
        adsk = types.ModuleType("adsk")
        core = types.ModuleType("adsk.core")
        fusion = types.ModuleType("adsk.fusion")
        core.__getattr__ = lambda k: _Any()
        fusion.__getattr__ = lambda k: _Any()
        adsk.core, adsk.fusion = core, fusion
        sys.modules["adsk"], sys.modules["adsk.core"], sys.modules["adsk.fusion"] = adsk, core, fusion
    spec = importlib.util.spec_from_file_location("ArmarDesdeRender", ADR_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ean13_ok(s):
    if len(s) != 13 or not s.isdigit():
        return False
    t = sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(s[:12]))
    return (10 - t % 10) % 10 == int(s[12])


def _n(v):
    return int(round(v)) if abs(v - round(v)) < 1e-6 else round(v, 2)


def _caja_mundo(ADR, pz):
    pts = [ADR._mundo(pz, x, y, z) for x in (0.0, pz.W) for y in (0.0, pz.H) for z in (0.0, -pz.T)]
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]


def _categoria(pz, es_cajon):
    """Orden de armado. Menor = antes."""
    nz = [abs(c) for c in pz.ez]           # normal en Fusion: x, y(=profundidad), z(=altura)
    eje = nz.index(max(nz))
    if pz.es_puerta or "drawer panels" in pz.nombre.lower():
        return 40
    if es_cajon:
        return 50
    if pz.T < 8:
        return 35                          # fondos
    if eje == 0:
        return 10                          # laterales, parantes
    if eje == 2:
        return 20                          # piso, techo, estantes
    return 30                              # travesaños, zocalos, frentes fijos


def _es_cajon(pz):
    n = pz.nombre.lower()
    return ("draw box" in n or "drawer back" in n or "drawer base" in n
            or "drawer panel01" in n and "drawer panels" not in n
            or ("drawer panel" in n and "panels" not in n))


def _herrajes(pz):
    h = dict(excentricas=0, pernos=0, receptores=0, bisagras=0, tornillos_bisagra=0,
             correderas=0, tornillos_corredera=0, led=[])
    for a in pz.holes:
        if a["sym"] == "3in1Lock" and abs(a["d"] - 15) < 0.5:
            h["excentricas"] += 1
        elif a["sym"] == "3in1Lock" and abs(a["d"] - 10) < 0.5:
            h["receptores"] += 1
        elif a["sym"] == "HINGE":
            h["bisagras"] += 1
        elif a["sym"] in ("HINGESCREW", "jlHoleEX"):
            h["tornillos_bisagra"] += 1
    for a in pz.sholes:
        if abs(a["d"] - 8) < 0.5:
            h["pernos"] += 1
        elif abs(a["d"] - 10) < 0.5:
            h["receptores"] += 1
    for s in pz.slots:
        if s["sym"] == "lightSlot":
            largo = max(abs(s["x2"] - s["x1"]), abs(s["y2"] - s["y1"]))
            h["led"].append(_n(min(largo, max(pz.W, pz.H))))
    return h



# --------------------------------------------------------------------------- #
#  nombres propios de las piezas
#
#  "<Tipo> <largo>x<ancho>x<esp>" y una letra (A, B, C...) cuando en el mismo
#  mueble hay mas de una del mismo tipo y medida. El tipo sale de la geometria
#  (normal y posicion en el mueble) y del rol, no del nombre de GuiGui.
# --------------------------------------------------------------------------- #

def _tipo(pz, es_cajon, caja_m, bmin, bmax):
    n = pz.nombre.lower()
    nz = [abs(c) for c in pz.ez]
    eje = nz.index(max(nz))                 # 0 = normal X (vertical lateral), 1 = normal Y (frente/fondo), 2 = normal Z (horizontal)
    alto = bmax[2] - bmin[2]
    if pz.es_puerta:
        return "Puerta"
    if "drawer panels" in n:
        return "Frente cajón"
    if es_cajon:
        if "base" in n:
            return "Fondo caja"
        if "front" in n:
            return "Frente caja"
        if "back" in n:
            return "Trasera caja"
        return "Lateral caja"
    if pz.mueble.lower().find("uñero") >= 0 or pz.mueble.lower().find("unero") >= 0:
        return "Uñero"
    if pz.T < 8:
        return "Fondo"
    if "skirting" in n or "kick" in n:
        return "Zócalo"
    abajo = abs(bmin[2] - caja_m[0][2]) < 2.0
    arriba = abs(bmax[2] - caja_m[1][2]) < 2.0
    if eje == 0:
        en_borde = (abs(bmin[0] - caja_m[0][0]) < 2.0) or (abs(bmax[0] - caja_m[1][0]) < 2.0)
        if alto <= 120 and abajo:
            return "Zócalo"
        if alto < 200:
            return "Travesaño"
        return "Lateral" if en_borde else "Parante"
    if eje == 2:
        prof = bmax[1] - bmin[1]
        if prof < 200:
            return "Travesaño"
        if abajo:
            return "Piso"
        if arriba:
            return "Techo"
        return "Estante"
    # normal Y: zocalos, travesanos, tapas de ajuste
    if alto <= 120 and abajo:
        return "Zócalo"
    if alto < 200:
        return "Travesaño"
    return "Tapa"


def nombrar(piezas):
    """Asigna nombre propio consistente a las piezas de UN mueble (in place)."""
    grupos = {}
    for p in piezas:
        L, A = sorted((p["H"], p["W"]), reverse=True)
        base = "%s %sx%sx%s" % (p["tipo"], _n(L), _n(A), _n(p["T"]))
        grupos.setdefault(base, []).append(p)
    for base, lista in grupos.items():
        lista.sort(key=lambda p: (p["caja"][0][0], p["caja"][0][2], p["caja"][0][1]))
        for i, p in enumerate(lista):
            p["nombre"] = base + (" %s" % chr(65 + i) if len(lista) > 1 else "")


def maestra(ruta_render, modelos=None):
    ADR = _cargar_adr()
    muebles, d = ADR.leer_render(ruta_render, None, None)
    ambiente = ""
    try:
        ambiente = d["models"][0].get("roomName", "")
    except Exception:
        pass
    salida = dict(ambiente=ambiente, orden=str(d.get("orderId", "")), version=d.get("version", ""),
                  muebles=[])
    # cajones: partsChildren del Drawer (correderas y tornillos) — se leen del JSON crudo
    cajones_por_mueble = {}
    for m in d["models"]:
        n = 0
        tornillos = 0
        largo_corr = ""

        def walk(nodo):
            nonlocal n, tornillos, largo_corr
            if nodo.get("partName") == "Drawer":
                n += 1
                for p in nodo.get("partsChildren") or []:
                    if p.get("symbol") == "drawerScrew":
                        tornillos += int(p.get("amount") or 0)
                    if p.get("symbol") == "slideRail":
                        largo_corr = p.get("matSpec") or largo_corr
            for c in nodo.get("children") or []:
                walk(c)
        walk(m)
        cajones_por_mueble[m["name"]] = (n, tornillos, largo_corr)

    for mu in muebles:
        if modelos is not None and mu["indice"] not in modelos:
            continue
        piezas = []
        cajas = [_caja_mundo(ADR, pz) for pz in mu["piezas"]]
        estr = [c for pz, c in zip(mu["piezas"], cajas)
                if not (pz.es_puerta or _es_cajon(pz) or "drawer panels" in pz.nombre.lower())] or cajas
        caja_m = ([min(c[0][i] for c in estr) for i in range(3)],
                  [max(c[1][i] for c in estr) for i in range(3)]) if cajas else ([0, 0, 0], [0, 0, 0])
        for pz, (bmin, bmax) in zip(mu["piezas"], cajas):
            es_cajon = _es_cajon(pz)
            c = pz.cantos
            izq, ab, der, ar = (float(c["IZQ"]), float(c["ABAJO"]), float(c["DER"]), float(c["ARRIBA"]))
            # Medida de corte: la de `spec` de GuiGui. En los fondos de 5 mm es la
            # caja + 10 (5 mm dentro de cada ranura) y en algun estante GuiGui
            # dibuja una profundidad y corta otra; se avisa cuando difieren.
            W, H, aviso = pz.W, pz.H, ""
            try:
                sw, sh = [float(t) for t in str(pz.spec).split("*")[:2]]
                if abs(sw - W) + abs(sh - H) > 0.05 and abs(sw - H) + abs(sh - W) > 0.05:
                    if abs(sw - W) + abs(sh - H) <= abs(sw - H) + abs(sh - W):
                        W, H = sw, sh
                    else:
                        W, H = sh, sw
                    if pz.T >= 8:
                        aviso = "GuiGui dibuja %gx%g pero corta %gx%g (spec)" % (pz.W, pz.H, W, H)
            except Exception:
                pass
            piezas.append(dict(
                codigo=pz.codigo, nombre=pz.nombre, nombre_guigui=pz.nombre, nombre_largo=pz.plankName,
                tipo=_tipo(pz, es_cajon, caja_m, bmin, bmax),
                W=_n(W), H=_n(H), T=_n(pz.T), dibujo_W=_n(pz.W), dibujo_H=_n(pz.H), aviso=aviso,
                corte_W=_n(W - izq - der), corte_H=_n(H - ab - ar),
                material=pz.material, textura=pz.textura,
                cantos=dict(izq=izq, abajo=ab, der=der, arriba=ar),
                veta="VERTICAL" if pz.texDir in ("normal", "", None) else "HORIZONTAL",
                rol=("PUERTA" if pz.es_puerta else "FRENTE" if "drawer panels" in pz.nombre.lower()
                     else "CAJON" if es_cajon else "FONDO" if pz.T < 8 else "PLACA"),
                categoria=_categoria(pz, es_cajon),
                caja=[[_n(v) for v in bmin], [_n(v) for v in bmax]],
                normal=[_n(v) for v in pz.ez],
                espejada=bool(getattr(pz, "espejada", False)),
                herrajes=_herrajes(pz),
                ean_ok=ean13_ok(pz.codigo),
            ))
        # orden de armado: categoria, despues de abajo hacia arriba, de izquierda a derecha
        piezas.sort(key=lambda p: (p["categoria"], round(p["caja"][0][2] / 50.0), p["caja"][0][0], p["caja"][0][1]))
        for i, p in enumerate(piezas, 1):
            p["globo"] = i
        nombrar(piezas)
        tot = dict(excentricas=0, pernos=0, receptores=0, bisagras=0, tornillos_bisagra=0, led=[])
        for p in piezas:
            for k in ("excentricas", "pernos", "receptores", "bisagras", "tornillos_bisagra"):
                tot[k] += p["herrajes"][k]
            tot["led"] += p["herrajes"]["led"]
        nc, torn, largo = cajones_por_mueble.get(mu["nombre"], (0, 0, ""))
        tot["correderas_pares"] = nc
        tot["correderas_largo"] = largo
        tot["tornillos_corredera"] = torn
        caja_t = ([min(c[0][i] for c in cajas) for i in range(3)],
                  [max(c[1][i] for c in cajas) for i in range(3)]) if cajas else caja_m
        caja_m = caja_t
        salida["muebles"].append(dict(indice=mu["indice"], nombre=mu["nombre"], piezas=piezas,
                                      herrajes=tot, caja=caja_m,
                                      ancho=_n(caja_m[1][0] - caja_m[0][0]),
                                      alto=_n(caja_m[1][2] - caja_m[0][2]),
                                      prof=_n(caja_m[1][1] - caja_m[0][1])))
    return salida


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render")
    ap.add_argument("-o", "--salida", default=".")
    ap.add_argument("--mueble", type=int, action="append", help="indice de models[] (repetible)")
    a = ap.parse_args(argv)
    m = maestra(a.render, a.mueble)
    os.makedirs(a.salida, exist_ok=True)
    ruta = os.path.join(a.salida, "maestra.json")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=1)
    codigos = [p["codigo"] for mu in m["muebles"] for p in mu["piezas"]]
    print("%s: %d muebles, %d piezas, %d codigos distintos, EAN-13 validos %d"
          % (ruta, len(m["muebles"]), len(codigos), len(set(codigos)),
             sum(1 for mu in m["muebles"] for p in mu["piezas"] if p["ean_ok"])))
    for mu in m["muebles"]:
        h = mu["herrajes"]
        print("  %-36s %3d piezas  %dx%dx%d  3en1 %d/%d/%d  bis %d  corr %d  led %d"
              % (mu["nombre"], len(mu["piezas"]), mu["ancho"], mu["alto"], mu["prof"],
                 h["excentricas"], h["pernos"], h["receptores"], h["bisagras"], h["correderas_pares"], len(h["led"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
