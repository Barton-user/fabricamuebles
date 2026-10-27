# -*- coding: utf-8 -*-
"""
render_piezas — render.json de GuiGui  ->  piezas.json (mismo esquema que exporta Fusion)

    python3 render_piezas.py <render.json> -o piezas.json [--orden 260625-20] [--cliente X]
                             [--herrajes-vigentes] [--modulos 0,3]

Camino directo, SIN pasar por Fusion (ArmarDesdeRender + ExportarPiezas). Validado el
27/10/2026 contra el export de Fusion de la Alacena spar (render 05/10, 11 piezas, la que
se perforo): mismos agujeros, agujeros de canto y ranuras pieza por pieza con esta regla:

  * marco de la pieza = el marco h/v de ArmarDesdeRender (W x H de paquete.maestra);
    los `ocenter` / `opt1` / `opt2` del render se usan TAL CUAL (x, y).
  * side -1 -> cara A ; side 1 -> cara B.   (ajustar_maquina despues elige que cara va arriba)
  * agujero de canto: el canto sale de la coordenada (x=0 L, x=W R, y=0 D, y=H U); z = center.y
  * cantos: edgeInfo2  ← izq (x=0)  → der (x=W)  ↑ abajo (y=0)  ↓ arriba (y=H)
  * nombre, mueble, medida y codigo: los de paquete.maestra (= etiqueta, web y planos)
  * piezas `espejada` de la maestra (cajones): se espejan igual que en ArmarDesdeRender
    (x -> W - x, caras y cantos izq/der cambiados) para usar el mismo marco que los planos

--herrajes-vigentes reemplaza lo que GuiGui todavia trae viejo por herrajes/medidas.json:
  tornillos de bisagra O3 x 0,5 -> O5 x 3 ; cazoleta -> prof. vigente ;
  placa base (O3 a 37 y 69 del frente) -> 2 x O5 x 3 a 37 del frente, +-16 a lo largo ;
  receptor del 3 en 1 O5 x 11 -> O5 x 12 ; perno de canto -> prof. vigente ;
  tornillos de corredera O3 x 2 -> se sacan (no hay mecha O3; se atornilla con plantilla).
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import paquete  # noqa: E402

TOL = 0.6


def _planks(nodo, out):
    if isinstance(nodo, dict):
        if nodo.get("plankNum"):
            out.append(nodo)
        for v in nodo.values():
            _planks(v, out)
    elif isinstance(nodo, list):
        for v in nodo:
            _planks(v, out)
    return out


def cantos_e2(s):
    o = {"canto_izq": 0.0, "canto_der": 0.0, "canto_abajo": 0.0, "canto_arriba": 0.0}
    for sym, k in ((u"←", "canto_izq"), (u"→", "canto_der"), (u"↑", "canto_abajo"), (u"↓", "canto_arriba")):
        m = re.search(re.escape(sym) + r"\s*(-?\d+(?:\.\d+)?)", s or "")
        if m:
            o[k] = float(m.group(1))
    return o


def _cara(side):
    try:
        return "A" if float(side) < 0 else "B"
    except (TypeError, ValueError):
        return "A"


def _r(v):
    return round(float(v), 3)


def _canto_de(x, y, W, H, code):
    if abs(x) <= TOL:
        return "L"
    if abs(x - W) <= TOL:
        return "R"
    if abs(y) <= TOL:
        return "D"
    if abs(y - H) <= TOL:
        return "U"
    return {"1": "L", "2": "U", "3": "R", "4": "D"}.get(str(code).strip())


# Materiales que la diseñadora dejo con el material de muestra de GuiGui. Se cortan como la placa
# vigente equivalente (mismo criterio que la INF01 de la Alacena spar, 05/10). Avisar a la diseñadora.
MATERIAL_VIGENTE = {
    (u"多层实木", u"13玛雅灰"): ("NEstructura", "Gris"),
    (u"装饰板", u"d02白麻面"): ("NFondo", "Blanco"),
    (u"装饰板", u"01暖白"): ("NFondo", "Blanco"),
    (u"PETFRONT", u"PET Gris"): ("NPetfrente", "PET Gris"),
}


def pieza(raw, mp, mueble):
    W, H, T = float(mp["W"]), float(mp["H"]), float(mp["T"])
    p = dict(codigo=mp["codigo"], nombre="%s_%s" % (mueble, mp["nombre"]), globo=mp.get("globo"),
             ancho=W, alto=H, espesor=T, material=mp.get("material") or "", mueble=mueble,
             textura=mp.get("textura") or "", veta=mp.get("veta") or "VERTICAL", cantidad=1,
             agujeros=[], agujeros_canto=[], ranuras=[], ranuras_canto=[], contorno=[], avisos=[])
    p.update(cantos_e2(raw.get("edgeInfo2") or raw.get("lightEdgeInfo")))
    fix = MATERIAL_VIGENTE.get((p["material"], p["textura"]))
    if fix:
        p["avisos"].append("material de GuiGui %s %s -> se corta en %s %s" % (p["material"], p["textura"], fix[0], fix[1]))
        p["material"], p["textura"] = fix
    for h in raw.get("holes") or []:
        c = h.get("ocenter") or h.get("center") or {}
        p["agujeros"].append(dict(x=_r(c["x"]), y=_r(c["y"]), diametro=float(h["diameter"]),
                                  profundidad=float(h["deep"]), cara=_cara(h.get("side")),
                                  herraje=h.get("symbol") or "", tipo=h.get("holeType") or ""))
    for h in raw.get("sholes") or []:
        c = h.get("ocenter") or {}
        x, y = float(c["x"]), float(c["y"])
        canto = _canto_de(x, y, W, H, h.get("side"))
        if canto is None:
            p["avisos"].append("agujero de canto fuera de los bordes en (%g, %g): no se usa" % (x, y))
            continue
        z = float((h.get("center") or {}).get("y", T / 2))
        p["agujeros_canto"].append(dict(x=_r(x), y=_r(y), z=_r(z), diametro=float(h["diameter"]),
                                        profundidad=float(h["deep"]), canto=canto,
                                        herraje=h.get("symbol") or "", tipo=h.get("holeType") or ""))
    for s in raw.get("slots") or []:
        a, b = s.get("opt1") or s.get("pt1"), s.get("opt2") or s.get("pt2")
        x1, y1, x2, y2 = (min(max(float(v), 0.0), lim) for v, lim in
                          ((a["x"], W), (a["y"], H), (b["x"], W), (b["y"], H)))
        p["ranuras"].append(dict(x1=_r(x1), y1=_r(y1), x2=_r(x2), y2=_r(y2), ancho=float(s["width"]),
                                 profundidad=float(s["deep"]), cara=_cara(s.get("side")),
                                 herraje=s.get("symbol") or ""))
    for s in raw.get("sslots") or []:
        # va en `ranuras_canto_aparte` y no en `ranuras_canto`: exportar.py descarta la pieza entera
        # si tiene ranura de canto (formato sin verificar); asi sale el programa con lo demas.
        p.setdefault("ranuras_canto_aparte", []).append(dict(x1=_r(s["opt1"]["x"]), y1=_r(s["opt1"]["y"]), x2=_r(s["opt2"]["x"]),
                                       y2=_r(s["opt2"]["y"]), ancho=float(s["width"]),
                                       profundidad=float(s["deep"]), herraje=s.get("symbol") or ""))
        p["avisos"].append("ranura de canto %gx%g (largo %g): NO esta en el programa; hacerla aparte (tupi/router de mano)"
                           % (s["width"], s["deep"], s.get("length") or 0))
    # piezas que ArmarDesdeRender espeja (cajones): mismo giro de 180 grados alrededor de v,
    # para que el programa use el mismo marco que los planos, la web y la etiqueta.
    # Es la misma placa dada vuelta: no cambia nada fisico.
    if mp.get("espejada"):
        for h in p["agujeros"]:
            h["x"] = _r(W - h["x"]); h["cara"] = {"A": "B", "B": "A"}[h["cara"]]
        for h in p["agujeros_canto"]:
            h["x"] = _r(W - h["x"]); h["z"] = _r(T - h["z"])
            h["canto"] = {"L": "R", "R": "L"}.get(h["canto"], h["canto"])
        for r in p["ranuras"]:
            r["x1"], r["x2"] = _r(W - r["x1"]), _r(W - r["x2"]); r["cara"] = {"A": "B", "B": "A"}[r["cara"]]
        for r in p.get("ranuras_canto_aparte", []):
            r["x1"], r["x2"] = _r(W - r["x1"]), _r(W - r["x2"])
        p["canto_izq"], p["canto_der"] = p["canto_der"], p["canto_izq"]
    # control: todo dentro de la pieza
    pts = [(h["x"], h["y"]) for h in p["agujeros"] + p["agujeros_canto"]] + \
          [(r["x1"], r["y1"]) for r in p["ranuras"]] + [(r["x2"], r["y2"]) for r in p["ranuras"]]
    fuera = [q for q in pts if q[0] < -TOL or q[0] > W + TOL or q[1] < -TOL or q[1] > H + TOL]
    if fuera:
        p["avisos"].append("%d mecanizados fuera de %gx%g, p. ej. %s" % (len(fuera), W, H, fuera[0]))
    if raw.get("lastCurve") and len((raw["lastCurve"] or {}).get("vertex") or []) > 4:
        p["avisos"].append("pieza con recorte (no es rectangular): el programa es el rectangulo; "
                           "el recorte va a mano o en el router")
    if mp.get("aviso"):
        p["avisos"].append(mp["aviso"])
    return p


# ---------------------------------------------------------------- herrajes vigentes

def _medidas():
    with io.open(os.path.join(os.path.dirname(AQUI), "herrajes", "medidas.json"), encoding="utf-8") as fh:
        return json.load(fh)


def herrajes_vigentes(p, med):
    b, t = med["bisagra"], med["tres_en_uno"]
    cambios = []
    hs = p["agujeros"]
    n = 0
    for h in hs:
        if h["herraje"] == "HINGESCREW" and (h["diametro"], h["profundidad"]) != (b["tornillo_d"], b["tornillo_prof"]):
            h["diametro"], h["profundidad"] = b["tornillo_d"], b["tornillo_prof"]; n += 1
    if n:
        cambios.append("%d tornillos de bisagra -> O%g x %g" % (n, b["tornillo_d"], b["tornillo_prof"]))
    n = 0
    for h in hs:
        if h["herraje"] == "HINGE" and abs(h["diametro"] - b["cazoleta_d"]) < 0.01 and h["profundidad"] != b["cazoleta_prof"]:
            h["profundidad"] = b["cazoleta_prof"]; n += 1
    if n:
        cambios.append("%d cazoletas -> prof %g" % (n, b["cazoleta_prof"]))
    # placa base: pares de jlHoleEX alineados perpendiculares a un canto, uno a ~37 de ese canto
    base = [h for h in hs if h["herraje"] == "jlHoleEX"]
    usados, nuevos = set(), []
    W, H = p["ancho"], p["alto"]
    for i, a in enumerate(base):
        if i in usados:
            continue
        for j, c in enumerate(base):
            if j <= i or j in usados or c["cara"] != a["cara"]:
                continue
            if abs(a["y"] - c["y"]) < 0.01 and abs(abs(a["x"] - c["x"]) - 32) < 1.01:
                eje = "x"
            elif abs(a["x"] - c["x"]) < 0.01 and abs(abs(a["y"] - c["y"]) - 32) < 1.01:
                eje = "y"
            else:
                continue
            lim = W if eje == "x" else H
            otro = "y" if eje == "x" else "x"
            # el canto del frente es el mas cercano al par
            cerca = min((a, c), key=lambda h: min(h[eje], lim - h[eje]))
            if cerca[eje] <= lim - cerca[eje]:
                pos = b["base_frente"]
            else:
                pos = lim - b["base_frente"]
            for sg in (-1, 1):
                q = dict(a); q[eje] = _r(pos); q[otro] = _r(a[otro] + sg * b["base_a_lo_largo"])
                q["diametro"], q["profundidad"] = b["base_d"], b["base_prof"]
                nuevos.append(q)
            usados.update((i, j))
            break
    if base:
        sueltos = [h for k, h in enumerate(base) if k not in usados]
        p["agujeros"] = [h for h in hs if h["herraje"] != "jlHoleEX"] + nuevos + sueltos
        hs = p["agujeros"]
        cambios.append("%d placas base -> 2 x O%g x %g a %g del frente, +-%g"
                       % (len(nuevos) // 2, b["base_d"], b["base_prof"], b["base_frente"], b["base_a_lo_largo"]))
        if sueltos:
            p["avisos"].append("%d agujeros de placa base sin par: quedaron como vienen" % len(sueltos))
    n = 0
    for h in hs + p["agujeros_canto"]:
        if h["herraje"] == "3in1Lock" and h["tipo"] == "preHole" and abs(h["diametro"] - t["receptor_d"]) < 0.01 \
                and h["profundidad"] != t["receptor_prof"]:
            h["profundidad"] = t["receptor_prof"]; n += 1
    if n:
        cambios.append("%d receptores 3 en 1 -> O%g x %g" % (n, t["receptor_d"], t["receptor_prof"]))
    n = 0
    for h in p["agujeros_canto"]:
        if h["herraje"] == "3in1Lock" and abs(h["diametro"] - t["perno_canto_d"]) < 0.01 \
                and h["profundidad"] != t["perno_canto_prof"]:
            h["profundidad"] = t["perno_canto_prof"]; n += 1
    if n:
        cambios.append("%d pernos de canto -> prof %g" % (n, t["perno_canto_prof"]))
    n = len([h for h in hs if h["herraje"] == "slideRail"])
    if n:
        p["agujeros"] = [h for h in hs if h["herraje"] != "slideRail"]
        cambios.append("%d tornillos de corredera O3 sacados (atornillar con plantilla)" % n)
    return cambios


def convertir(ruta_render, orden="", cliente="", vigentes=False, modulos=None):
    m = paquete.maestra(ruta_render, modulos)
    with io.open(ruta_render, encoding="utf-8") as fh:
        d = json.load(fh)
    R = {str(r["plankNum"]): r for r in _planks(d, [])}
    med = _medidas() if vigentes else None
    piezas, informe = [], []
    for mu in m["muebles"]:
        for mp in sorted(mu["piezas"], key=lambda q: q["globo"]):
            p = pieza(R[mp["codigo"]], mp, mu["nombre"])
            p["modulo"] = len({q["mueble"] for q in piezas} | {mu["nombre"]})
            cambios = herrajes_vigentes(p, med) if vigentes else []
            piezas.append(p)
            informe.append((p, cambios))
    sin = [r for c, r in R.items() if c not in {p["codigo"] for p in piezas}]
    doc = dict(version=1, origen="guigui-render", documento=os.path.basename(ruta_render), orden=orden,
               cliente=cliente, direccion="", ambiente=m["ambiente"], piezas=piezas)
    return doc, informe, sin


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render")
    ap.add_argument("-o", "--salida", required=True)
    ap.add_argument("--orden", default="")
    ap.add_argument("--cliente", default="")
    ap.add_argument("--herrajes-vigentes", action="store_true")
    ap.add_argument("--modulos", default="", help="indices de models[] separados por coma")
    a = ap.parse_args(argv)
    mods = [int(x) for x in a.modulos.split(",") if x.strip()] or None
    doc, informe, sin = convertir(a.render, a.orden, a.cliente, a.herrajes_vigentes, mods)
    with io.open(a.salida, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
    lineas = []
    mueble = None
    for p, cambios in informe:
        if p["mueble"] != mueble:
            mueble = p["mueble"]; lineas.append("\n## %s" % mueble)
        txt = "; ".join(cambios + ["⚠ " + x for x in p["avisos"]]) or "sin cambios"
        lineas.append("%2s %s %-30s %s" % (p["globo"], p["codigo"], p["nombre"].split("_", 1)[-1][:30], txt))
    for r in sin:
        lineas.append("\n⚠ %s %s: esta en el render sin geometria -> NO tiene programa ni etiqueta"
                      % (r.get("plankNum"), r.get("name")))
    inf = os.path.splitext(a.salida)[0] + "_informe.txt"
    with io.open(inf, "w", encoding="utf-8") as fh:
        fh.write("render_piezas %s\n" % os.path.basename(a.render) + "\n".join(lineas) + "\n")
    print("%s: %d piezas; informe en %s" % (a.salida, len(doc["piezas"]), inf))
    return 0


if __name__ == "__main__":
    sys.exit(main())
