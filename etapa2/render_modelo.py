# -*- coding: utf-8 -*-
"""
render_modelo — render.json de GuiGui  ->  modelo.json para manual_armado.py (camino GuiGui)

    python3 render_modelo.py <render.json> -o modelo.json [--orden 260625-20]
    python3 manual_armado.py modelo.json -o manuales/manual.pdf      (un PDF por mueble)

Las piezas salen de ArmarDesdeRender.leer_render (marco h/v, placa en z in [-T, 0] sobre ez,
igual que el modelo de las recetas) y los nombres de paquete.maestra. El mundo de
ArmarDesdeRender (X derecha, Y hacia atras) se gira 180 grados alrededor de Z para pasar al de
las recetas (X desde la derecha de quien mira, Y desde la pared hacia el frente).

Herrajes que se pasan: pernos (agujeros O8 de canto), excentricas (O15), bisagras (cazoletas),
correderas (un par por cajon) y tiras LED (lightSlot). Los receptores O5 no son una pieza.
Las piezas de cada cajon (nodo Drawer del render) se llaman "Cajón N ..." / "Frente cajón N"
para que manual_armado las arme como sub-armado.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import paquete  # noqa: E402

TOL = 0.6


def R(v):
    return [-float(v[0]), -float(v[1]), float(v[2])]


def cruz(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def mundo(pz, x, y, z):
    return [pz.origen[i] + pz.ex[i] * x + pz.ey[i] * y + pz.ez[i] * z for i in range(3)]


def lado(pz, h):
    x, y = h["x"], h["y"]
    if abs(x) <= TOL:
        return 1
    if abs(y - pz.H) <= TOL:
        return 2
    if abs(x - pz.W) <= TOL:
        return 3
    if abs(y) <= TOL:
        return 4
    return int(h.get("side") or 1)


ADENTRO = {1: (1.0, 0.0), 2: (0.0, -1.0), 3: (-1.0, 0.0), 4: (0.0, 1.0)}


def cajones_del_render(d):
    """{plankNum: n de cajon dentro de su mueble}."""
    out = {}
    for m in d["models"]:
        k = 0

        def junta(n, acc):
            if isinstance(n, dict):
                if n.get("plankNum"):
                    acc.append(str(n["plankNum"]))
                for c in n.get("children") or []:
                    junta(c, acc)
            return acc

        def walk(n):
            nonlocal k
            if n.get("partName") == "Drawer":
                k += 1
                for c in junta(n, []):
                    out[c] = k
                return
            for c in n.get("children") or []:
                walk(c)
        walk(m)
    return out


def corto(mp):
    """'Lateral 840.5x400x18 A' -> 'Lateral A' (la medida va en otra columna del manual)."""
    partes = mp["nombre"].split()
    letra = partes[-1] if len(partes) > 2 and len(partes[-1]) == 1 and partes[-1].isalpha() else ""
    return (mp.get("tipo") or partes[0]) + (" " + letra if letra else "")


def _largo(s):
    import re
    m = re.search(r"\d+(?:\.\d+)?", str(s or ""))
    return float(m.group(0)) if m else 450.0


def convertir(ruta, orden=""):
    ADR = paquete._cargar_adr()
    muebles, d = ADR.leer_render(ruta, None, None)
    m = paquete.maestra(ruta)
    MP = {p["codigo"]: p for mu in m["muebles"] for p in mu["piezas"]}
    caj = cajones_del_render(d)
    piezas, herrajes = [], []
    for mu in muebles:
        for pz in mu["piezas"]:
            mp = MP.get(pz.codigo)
            if not mp:
                continue
            nombre = corto(mp)
            n = mp.get("cajon") or caj.get(pz.codigo)
            if n:
                nombre = ("Frente cajón %d" % n) if mp["rol"] == "FRENTE" else ("Cajón %d %s" % (n, nombre.lower()))
            piezas.append(dict(mueble=mu["nombre"], nombre="%s_%s" % (mu["nombre"], mp["nombre"]), pieza=nombre,
                               codigo=pz.codigo, rol=mp["rol"] if mp["rol"] in ("PUERTA", "FONDO") else "",
                               W=pz.W, H=pz.H, T=pz.T, O=R(pz.origen), ex=R(pz.ex), ey=R(pz.ey),
                               material=mp.get("material", ""), textura=mp.get("textura", ""),
                               veta=mp.get("veta", ""), globo=mp.get("globo")))
            ez_cara = lambda side: (-pz.T, 1.0) if side == 1 else (0.0, -1.0)
            for h in pz.sholes:
                if abs(h["d"] - 8.0) > 0.5:
                    continue
                s = lado(pz, h)
                dx, dy = ADENTRO[s]
                bx, by = min(max(h["x"], 0.0), pz.W), min(max(h["y"], 0.0), pz.H)
                o = mundo(pz, bx, by, -pz.T / 2.0)
                ez = [pz.ex[i] * dx + pz.ey[i] * dy for i in range(3)]
                herrajes.append(dict(mueble=mu["nombre"], nombre="Perno", forma="perno", origen=R(o), ez=R(ez)))
            for h in pz.holes:
                z0, sg = ez_cara(h["side"])
                o = mundo(pz, h["x"], h["y"], z0)
                ez = [pz.ez[i] * sg for i in range(3)]
                if h["sym"] == "3in1Lock" and abs(h["d"] - 15.0) < 0.5:
                    herrajes.append(dict(mueble=mu["nombre"], nombre="Excentrica O15", forma="excentrica",
                                         origen=R(o), ez=R(ez)))
                elif h["sym"] == "HINGE":
                    herrajes.append(dict(mueble=mu["nombre"], nombre="Bisagra", forma="bisagra",
                                         origen=R(o), ez=R(ez)))
            for s in pz.slots:
                if s["sym"] != "lightSlot":
                    continue
                largo = max(abs(s["x2"] - s["x1"]), abs(s["y2"] - s["y1"]))
                largo = min(largo, max(pz.W, pz.H))
                o = mundo(pz, (s["x1"] + s["x2"]) / 2, (s["y1"] + s["y2"]) / 2, 0.0)
                herrajes.append(dict(mueble=mu["nombre"], nombre="Tira LED %d" % round(largo), forma="led",
                                     origen=R(o), ez=R(pz.ez), args=dict(largo=round(largo))))
        tot = next((x for x in m["muebles"] if x["nombre"] == mu["nombre"]), {}).get("herrajes", {})
        for k in range(int(tot.get("correderas_pares") or 0)):
            herrajes.append(dict(mueble=mu["nombre"], nombre="Corredera", forma="corredera", origen=[0, 0, 0],
                                 ez=[0, 0, 1], args=dict(largo=_largo(tot.get("correderas_largo")))))
    avisos = []
    for mu in m["muebles"]:
        h = mu["herrajes"]
        if h.get("correderas_pares"):
            avisos.append("%s: correderas %s; los agujeros de la corredera no vienen de la máquina: "
                          "atornillarlas con la plantilla." % (mu["nombre"], h.get("correderas_largo") or ""))
    return dict(version=1, origen="guigui-render", documento=os.path.basename(ruta), orden=orden,
                cliente="", direccion="", ambiente=m["ambiente"], piezas=piezas, herrajes=herrajes,
                avisos=avisos, referencia=[])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render")
    ap.add_argument("-o", "--salida", required=True)
    ap.add_argument("--orden", default="")
    a = ap.parse_args(argv)
    doc = convertir(a.render, a.orden)
    with io.open(a.salida, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    print("%s: %d piezas, %d herrajes" % (a.salida, len(doc["piezas"]), len(doc["herrajes"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
