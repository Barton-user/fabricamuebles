# -*- coding: utf-8 -*-
"""
a_medida_corte — pasa un piezas.json de medida TERMINADA (con canto) a medida de
CORTE (sin canto), corriendo todos los mecanizados el espesor del canto.

Para perforar ANTES de pegar el canto: la placa que entra a la maquina mide lo
que salio de la sierra, y los agujeros quedan a la medida correcta cuando
despues se pega el canto.

    python3 a_medida_corte.py piezas.json -o piezas_corte.json
"""
import argparse, io, json


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("entrada"); ap.add_argument("-o", "--salida", required=True)
    a = ap.parse_args()
    d = json.load(io.open(a.entrada, encoding="utf-8"))
    for p in d["piezas"]:
        ci, cd, cb, ca = (float(p.get(k, 0) or 0) for k in ("canto_izq", "canto_der", "canto_abajo", "canto_arriba"))
        if not (ci or cd or cb or ca):
            continue
        W, H = p["ancho"] - ci - cd, p["alto"] - cb - ca
        cl = lambda v, m: round(min(max(v, 0.0), m), 3)
        for h in p.get("agujeros", []):
            h["x"], h["y"] = round(h["x"] - ci, 3), round(h["y"] - cb, 3)
        for r in p.get("ranuras", []):
            r["x1"], r["x2"] = cl(r["x1"] - ci, W), cl(r["x2"] - ci, W)
            r["y1"], r["y2"] = cl(r["y1"] - cb, H), cl(r["y2"] - cb, H)
        for h in p.get("agujeros_canto", []):
            h["x"], h["y"] = round(h["x"] - ci, 3), round(h["y"] - cb, 3)
            if h["canto"] == "L": h["x"] = 0.0
            if h["canto"] == "R": h["x"] = round(W, 3)
            if h["canto"] == "D": h["y"] = 0.0
            if h["canto"] == "U": h["y"] = round(H, 3)
        p["ancho"], p["alto"] = round(W, 3), round(H, 3)
        p["nombre"] = p["nombre"] + " (corte)"
    json.dump(d, io.open(a.salida, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    for p in d["piezas"]:
        print(p["codigo"], p["ancho"], "x", p["alto"])


if __name__ == "__main__":
    main()
