# -*- coding: utf-8 -*-
"""
dos_pasos — parte en DOS programas las piezas que MH2026 no convierte en uno.

    python3 dos_pasos.py piezas_maquina.json -o piezas_2pasos.json

Caso que fallo el 19-20/10 (cajon del Bandejero): todos los agujeros verticales en la cara
de abajo (TypeNo 8) y la ranura arriba -> "diametro de herramienta demasiado grande".
Tambien el caso sin solucion en un programa: ranuras de menos de 10 en las dos caras.

Para cada pieza asi (salida de ajustar_maquina, cara A = arriba):
  paso 1  codigo ORIGINAL : la cara con los agujeros verticales ARRIBA + agujeros de canto
                            (+ las ranuras de esa misma cara)
  paso 2  codigo 99…      : solo lo de la otra cara, dada vuelta para que quede ARRIBA
El codigo del paso 2 = "99" + digitos 3 a 12 del original + verificador EAN-13.
"""
from __future__ import annotations

import argparse
import copy
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ajustar_maquina import voltear  # noqa: E402
from fusion_json import digito_ean13  # noqa: E402


def codigo_paso2(c):
    doce = "99" + c[2:12]
    return doce + digito_ean13(doce)


def caras(p, cara):
    v = [h for h in p.get("agujeros", []) if h["cara"] == cara]
    r = [x for x in p.get("ranuras", []) if x["cara"] == cara]
    return v, r


def necesita(p):
    va, ra = caras(p, "A")
    vb, rb = caras(p, "B")
    angosta = lambda rs: any(x["ancho"] < 10 - 1e-6 for x in rs)
    if angosta(ra) and angosta(rb):
        return "ranuras de menos de 10 en las dos caras"
    if vb and not va and ra:
        return "verticales solo abajo y ranura arriba"
    return ""


def partir(p):
    vb = caras(p, "B")[0]
    uno = copy.deepcopy(p)
    if vb:                      # la cara con verticales tiene que quedar arriba
        voltear(uno)
    uno["agujeros"] = [h for h in uno["agujeros"] if h["cara"] == "A"]
    uno["ranuras"] = [x for x in uno["ranuras"] if x["cara"] == "A"]
    dos = copy.deepcopy(uno)
    voltear(dos)               # lo que quedo abajo pasa arriba
    otro = copy.deepcopy(p)
    if vb:
        voltear(otro)
    voltear(otro)
    dos["agujeros"] = [h for h in otro["agujeros"] if h["cara"] == "A"]
    dos["ranuras"] = [x for x in otro["ranuras"] if x["cara"] == "A"]
    dos["agujeros_canto"] = []
    dos["codigo"] = codigo_paso2(p["codigo"])
    dos["nombre"] = p["nombre"] + " PASO 2"
    uno["nombre"] = p["nombre"] + " PASO 1"
    return uno, dos


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada")
    ap.add_argument("-o", "--salida", required=True)
    a = ap.parse_args(argv)
    d = json.load(io.open(a.entrada, encoding="utf-8"))
    out, inf = [], []
    for p in d["piezas"]:
        por = necesita(p)
        if not por:
            continue
        uno, dos = partir(p)
        out += [uno, dos]
        d1 = ", ".join(sorted({"O%g" % h["diametro"] for h in uno["agujeros"]} |
                              {"ranura %gx%g" % (x["ancho"], x["profundidad"]) for x in uno["ranuras"]})) or "-"
        d2 = ", ".join(sorted({"O%g" % h["diametro"] for h in dos["agujeros"]} |
                              {"ranura %gx%g" % (x["ancho"], x["profundidad"]) for x in dos["ranuras"]})) or "-"
        inf.append("%s %-44s (%s)\n    paso 1 %s: %s + %d de canto\n    paso 2 %s: %s  (dar vuelta la pieza)"
                   % (p["codigo"], p["nombre"][:44], por, uno["codigo"], d1, len(uno["agujeros_canto"]), dos["codigo"], d2))
    d["piezas"] = out
    json.dump(d, io.open(a.salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n".join(inf))
    print("%d piezas en dos pasos" % (len(out) // 2))


if __name__ == "__main__":
    main()
