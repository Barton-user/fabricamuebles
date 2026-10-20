# -*- coding: utf-8 -*-
"""
a_medida_real — adapta un piezas.json a la MEDIDA REAL que salio de la sierra.

La HP280 suele dejar 1-2 mm de mas. Si la perforadora recibe un programa con el ancho
nominal y la pieza es mas ancha, el carro del eje A empuja contra la placa y salta
202h AEje (CONTEXTO §4). En vez de recortar, se genera el programa con la medida real:
el material de mas queda en UN borde y todos los mecanizados se corren para quedar
referidos al borde opuesto.

    python3 a_medida_real.py piezas_maquina.json -o piezas_real.json \
        --pieza 2115070657455=300x450 --pieza 2115070657431=300.5x203 [--extra canto|izq|der|abajo|arriba]

  --pieza CODIGO=ANCHOxALTO   medida real con calibre (ancho = X del programa, alto = Y).
                              Se puede repetir. Las piezas no nombradas quedan igual.
  --extra                     en que borde queda el sobrante (default: canto = el borde
                              que lleva canto; si no tiene, 'der' en X y 'arriba' en Y).
                              Los mecanizados se corren para quedar fijos respecto del
                              borde opuesto.

Reglas: si el sobrante va a la IZQ, todo X se corre +dx; si va a la DER, X no cambia.
Si va ABAJO, todo Y se corre +dy; si va ARRIBA, Y no cambia. Los agujeros de canto del
borde que crece se mueven al borde nuevo. El nombre lleva " (real AxB)".
"""
import argparse, io, json, sys

def lado_extra(p, pedido, eje):
    if pedido and pedido != "canto":
        return pedido
    if eje == "x":
        if p.get("canto_izq") and not p.get("canto_der"): return "izq"
        return "der"
    else:
        if p.get("canto_abajo") and not p.get("canto_arriba"): return "abajo"
        return "arriba"

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada"); ap.add_argument("-o", "--salida", required=True)
    ap.add_argument("--pieza", action="append", default=[], help="CODIGO=ANCHOxALTO")
    ap.add_argument("--extra", default="canto", choices=["canto", "izq", "der", "abajo", "arriba"])
    a = ap.parse_args()
    reales = {}
    for s in a.pieza:
        cod, med = s.split("="); w, h = med.lower().replace(",", ".").split("x")
        reales[cod.strip()] = (float(w), float(h))
    d = json.load(io.open(a.entrada, encoding="utf-8"))
    informe = []
    for p in d["piezas"]:
        if p["codigo"] not in reales:
            continue
        W0, H0 = float(p["ancho"]), float(p["alto"])
        W1, H1 = reales[p["codigo"]]
        dx, dy = round(W1 - W0, 3), round(H1 - H0, 3)
        if dx < -0.01 or dy < -0.01:
            informe.append("%s: la pieza real es MAS CHICA (%gx%g vs %gx%g): recortar el programa no es seguro, revisar" % (p["codigo"], W1, H1, W0, H0))
        ex = lado_extra(p, a.extra if a.extra in ("izq", "der", "canto") else "canto", "x")
        ey = lado_extra(p, a.extra if a.extra in ("abajo", "arriba", "canto") else "canto", "y")
        sx = dx if ex == "izq" else 0.0
        sy = dy if ey == "abajo" else 0.0
        for h in p.get("agujeros", []):
            h["x"] = round(h["x"] + sx, 3); h["y"] = round(h["y"] + sy, 3)
        for r in p.get("ranuras", []):
            for k in ("x1", "x2"): r[k] = round(r[k] + sx, 3)
            for k in ("y1", "y2"): r[k] = round(r[k] + sy, 3)
            # ranuras de borde a borde siguen de borde a borde
            if abs(r["y1"] - sy) < 0.01 and abs(r["y2"] - (H0 + sy)) < 0.01: r["y1"], r["y2"] = 0.0, round(H1, 3)
            if abs(r["x1"] - sx) < 0.01 and abs(r["x2"] - (W0 + sx)) < 0.01: r["x1"], r["x2"] = 0.0, round(W1, 3)
        for h in p.get("agujeros_canto", []):
            h["x"] = round(h["x"] + sx, 3); h["y"] = round(h["y"] + sy, 3)
            if h["canto"] == "L": h["x"] = 0.0
            if h["canto"] == "R": h["x"] = round(W1, 3)
            if h["canto"] == "D": h["y"] = 0.0
            if h["canto"] == "U": h["y"] = round(H1, 3)
        for r in p.get("ranuras_canto", []) or []:
            for k in ("x1", "x2"):
                if k in r: r[k] = round(r[k] + sx, 3)
            for k in ("y1", "y2"):
                if k in r: r[k] = round(r[k] + sy, 3)
        cantos_y = {h["canto"] for h in p.get("agujeros_canto", [])} & {"U", "D"}
        cantos_x = {h["canto"] for h in p.get("agujeros_canto", [])} & {"L", "R"}
        if abs(dy) > 0.01 and cantos_y:
            informe.append("  AVISO %s: tiene pernos en los cantos de arriba/abajo. El sobrante en Y (%+g) deja la excentrica a %g del canto en vez de 34: esa medida tiene que ser EXACTA (define el ancho interior del cajon). Mejor recortar el largo en la sierra." % (p["codigo"], dy, 34 + abs(dy)))
        if abs(dx) > 0.01 and cantos_x:
            informe.append("  AVISO %s: idem en X (pernos en los cantos izq/der): recortar en vez de absorber." % p["codigo"])
        if p.get("contorno"):
            informe.append("%s: tiene contorno; NO se escala, revisar a mano" % p["codigo"])
        p["ancho"], p["alto"] = round(W1, 3), round(H1, 3)
        p["nombre"] = "%s (real %gx%g)" % (p["nombre"], W1, H1)
        informe.append("%s %-40s %gx%g -> %gx%g  sobrante X en %s (%+g), Y en %s (%+g)" % (
            p["codigo"], p["nombre"][:40], W0, H0, W1, H1, ex.upper(), dx, ey.upper(), dy))
    json.dump(d, io.open(a.salida, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("\n".join(informe) if informe else "ninguna pieza coincide con --pieza")

if __name__ == "__main__":
    main()
