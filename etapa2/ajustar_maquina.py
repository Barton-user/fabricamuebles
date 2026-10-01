# -*- coding: utf-8 -*-
"""
ajustar_maquina — adapta un piezas.json a lo que la SKH-612HS puede hacer HOY.

    python3 ajustar_maquina.py piezas.json -o piezas_maquina.json [--o6-a-o5] [--led10] [--bisagra] [--sin-voltear]

1. VOLTEO AUTOMATICO (por defecto): elige como cara A (la que queda ARRIBA en la
   maquina) la cara que tiene lo que solo se hace desde arriba:
     - ranuras de menos de 10 de ancho (abajo solo esta la T11, O10)
     - cazoletas / agujeros de O20 o mas (se fresan con la T184, arriba)
   Si ninguna cara lo exige, queda arriba la cara con mas trabajo.
   Dar vuelta = espejar en X: x -> W - x, cara A <-> B, canto izq <-> der.
2. --o6-a-o5: agujeros verticales O6 -> O5 (no hay O6 montada; con O6 el
   software crashea, CONTEXTO §15).
3. --led10: ranuras de 9 x 9 -> 10 x 10 (minimo de la cara dorso = T11).
4. --bisagra: corrige los tornillos de bisagra que vienen de GuiGui (a 14,5 del
   centro de la cazoleta) a la medida real de herrajes/medidas.json (48/6 ->
   a 6). Busca cada cazoleta O35 y los dos agujeros chicos (O5/O6, prof. ~3)
   de la misma cara a +-24 a lo largo y 14,5 hacia adentro, y los corre.

Escribe un informe de que cambio en cada pieza.
"""
from __future__ import annotations

import argparse
import io
import os
import json

SOLO_ARRIBA_RANURA = 10.0
SOLO_ARRIBA_AGUJERO = 20.0


def exige_arriba(p, cara):
    for r in p.get("ranuras", []):
        if r["cara"] == cara and r["ancho"] < SOLO_ARRIBA_RANURA - 1e-6:
            return True
    for h in p.get("agujeros", []):
        if h["cara"] == cara and h["diametro"] >= SOLO_ARRIBA_AGUJERO - 1e-6:
            return True
    return False


def trabajo(p, cara):
    return sum(1 for h in p.get("agujeros", []) if h["cara"] == cara) + \
        sum(1 for r in p.get("ranuras", []) if r["cara"] == cara)


def _medidas_bisagra():
    ruta = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "herrajes", "medidas.json")
    with io.open(ruta, encoding="utf-8") as fh:
        return json.load(fh)["bisagra"]


def corregir_bisagra(p, b, guigui=14.5, tol=0.6):
    """Corre los tornillos de cada bisagra de `guigui` a b['tornillos_desde_cazoleta'].
    Devuelve cuantos agujeros movio."""
    nuevo, largo = b["tornillos_desde_cazoleta"], b["tornillos_a_lo_largo"]
    hs = p.get("agujeros", [])
    cazs = [h for h in hs if abs(h["diametro"] - b["cazoleta_d"]) < 0.01]
    movidos = 0
    for c in cazs:
        chicos = [h for h in hs if h is not c and h["cara"] == c["cara"] and h["diametro"] <= 6.01
                  and abs(h["profundidad"] - b["tornillo_prof"]) < 1.01]
        for h in chicos:
            dx, dy = h["x"] - c["x"], h["y"] - c["y"]
            for eje, perp, a_lo in (("x", dx, dy), ("y", dy, dx)):
                if abs(abs(perp) - guigui) < tol and abs(abs(a_lo) - largo) < tol:
                    sg = 1.0 if perp > 0 else -1.0
                    h[eje] = round(c[eje] + sg * nuevo, 3)
                    movidos += 1
                    break
    return movidos


def voltear(p):
    W, T = p["ancho"], p["espesor"]
    otra = {"A": "B", "B": "A"}
    for h in p.get("agujeros", []):
        h["x"] = round(W - h["x"], 3); h["cara"] = otra[h["cara"]]
    for r in p.get("ranuras", []):
        r["x1"] = round(W - r["x1"], 3); r["x2"] = round(W - r["x2"], 3); r["cara"] = otra[r["cara"]]
    for h in p.get("agujeros_canto", []):
        h["x"] = round(W - h["x"], 3)
        h["z"] = round(T - h["z"], 3)
        h["canto"] = {"L": "R", "R": "L"}.get(h["canto"], h["canto"])
    for r in p.get("ranuras_canto", []) or []:
        for k in ("x", "x1", "x2"):
            if k in r:
                r[k] = round(W - r[k], 3)
    if p.get("contorno"):
        p["contorno"] = [dict(c, x=round(W - c["x"], 3)) for c in reversed(p["contorno"])]
    p["canto_izq"], p["canto_der"] = p["canto_der"], p["canto_izq"]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada")
    ap.add_argument("-o", "--salida", required=True)
    ap.add_argument("--o6-a-o5", action="store_true")
    ap.add_argument("--led10", action="store_true")
    ap.add_argument("--bisagra", action="store_true",
                    help="tornillos de bisagra de GuiGui (14,5) -> medida de herrajes/medidas.json")
    ap.add_argument("--sin-voltear", action="store_true")
    a = ap.parse_args()
    with io.open(a.entrada, encoding="utf-8") as fh:
        d = json.load(fh)
    inf = []
    for p in d["piezas"]:
        nom = "%s %s" % (p["codigo"], p["nombre"].split("_")[-1])
        cambios = []
        if a.led10:
            for r in p.get("ranuras", []):
                if abs(r["ancho"] - 9) < 0.01 and abs(r["profundidad"] - 9) < 0.01:
                    r["ancho"], r["profundidad"] = 10.0, 10.0
                    cambios.append("ranura 9x9 -> 10x10")
        if a.bisagra:
            n = corregir_bisagra(p, _medidas_bisagra())
            if n:
                cambios.append("%d tornillos de bisagra 14,5 -> %g" % (n, _medidas_bisagra()["tornillos_desde_cazoleta"]))
        if a.o6_a_o5:
            n = 0
            for h in p.get("agujeros", []):
                if abs(h["diametro"] - 6) < 0.01:
                    h["diametro"] = 5.0; n += 1
            if n:
                cambios.append("%d x O6 -> O5" % n)
        if not a.sin_voltear:
            ea, eb = exige_arriba(p, "A"), exige_arriba(p, "B")
            if ea and eb:
                cambios.append("CONFLICTO: las dos caras necesitan ir arriba")
            elif eb or (not ea and trabajo(p, "B") > trabajo(p, "A")):
                voltear(p)
                cambios.append("VOLTEADA (cara de trabajo arriba)")
        abajo = [("O%g" % h["diametro"]) for h in p.get("agujeros", []) if h["cara"] == "B"] + \
                [("ranura %gx%g" % (r["ancho"], r["profundidad"])) for r in p.get("ranuras", []) if r["cara"] == "B"]
        if abajo:
            cambios.append("queda ABAJO: " + ", ".join(sorted(set(abajo))))
        inf.append("%-34s %s" % (nom, "; ".join(cambios) or "sin cambios"))
    with io.open(a.salida, "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=2)
    print("\n".join(inf))


if __name__ == "__main__":
    main()
