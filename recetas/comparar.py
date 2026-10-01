# -*- coding: utf-8 -*-
"""comparar — receta (piezas_receta.json) contra lo que Fusion leyo del solido (piezas.json).

    python3 recetas/comparar.py <piezas_receta.json> <piezas.json>
"""
import json, sys, math

def key_h(h): return (round(h["x"], 1), round(h["y"], 1), round(h["diametro"], 1), round(h["profundidad"], 1), h["cara"])
def key_c(h): return (round(h["x"], 1), round(h["y"], 1), round(h["z"], 1), round(h["diametro"], 1), round(h["profundidad"], 1), h["canto"])
def key_s(s):
    a = (round(s["x1"], 1), round(s["y1"], 1)); b = (round(s["x2"], 1), round(s["y2"], 1))
    a, b = sorted([a, b])
    return (a, b, round(s["ancho"], 1), round(s["profundidad"], 1), s["cara"])

def casar(ra, fa, tol):
    """empareja listas de tuplas con tolerancia en los numeros"""
    fa = list(fa); falt = []
    for r in ra:
        hit = None
        for i, f in enumerate(fa):
            ok = True
            for x, y in zip(r, f):
                if isinstance(x, tuple):
                    ok = ok and all(abs(p - q) <= tol for p, q in zip(x, y))
                elif isinstance(x, (int, float)):
                    ok = ok and abs(x - y) <= tol
                else:
                    ok = ok and x == y
            if ok:
                hit = i; break
        if hit is None: falt.append(r)
        else: fa.pop(hit)
    return falt, fa

def area(c):
    if not c: return None
    s = 0
    for i in range(len(c)):
        a, b = c[i], c[(i + 1) % len(c)]
        s += a["x"] * b["y"] - b["x"] * a["y"]
    return abs(s) / 2

R = {p["codigo"]: p for p in json.load(open(sys.argv[1]))["piezas"]}
F = {p["codigo"]: p for p in json.load(open(sys.argv[2]))["piezas"]}
malas = 0
print("receta %d piezas, fusion %d piezas" % (len(R), len(F)))
for c in sorted(set(R) | set(F)):
    r, f = R.get(c), F.get(c)
    if r is None or f is None:
        print("FALTA", c, "en", "receta" if r is None else "fusion"); malas += 1; continue
    prob = []
    for k in ("ancho", "alto", "espesor"):
        if abs(r[k] - f[k]) > 0.05: prob.append("%s %g vs %g" % (k, r[k], f[k]))
    for k in ("canto_abajo", "canto_arriba", "canto_izq", "canto_der", "material", "textura", "mueble"):
        if str(r[k]) != str(f[k]) and not (isinstance(r[k], float) and float(f[k]) == r[k]):
            prob.append("%s %s vs %s" % (k, r[k], f[k]))
    ar_, af = area(r.get("contorno")), area(f.get("contorno"))
    if r.get("contorno") or (f.get("contorno") and len(f["contorno"]) != 4):
        rr = ar_ if ar_ is not None else r["ancho"] * r["alto"]
        ff = af if af is not None else f["ancho"] * f["alto"]
        if abs(rr - ff) > 1.0: prob.append("area contorno %.1f vs %.1f" % (rr, ff))
    for nombre, kk, lr, lf in (("agujeros", key_h, r["agujeros"], f["agujeros"]),
                               ("canto", key_c, r["agujeros_canto"], f["agujeros_canto"]),
                               ("ranuras", key_s, r["ranuras"], f["ranuras"])):
        fr, sf = casar([kk(x) for x in lr], [kk(x) for x in lf], 0.06)
        if fr: prob.append("%s solo en receta: %s" % (nombre, fr[:4]))
        if sf: prob.append("%s solo en fusion: %s" % (nombre, sf[:4]))
    if f.get("ranuras_canto"): prob.append("ranuras de canto: %s" % f["ranuras_canto"])
    if prob:
        malas += 1
        print("%s %s" % (c, r["nombre"]))
        for p in prob: print("    " + p)
print("piezas con diferencias: %d de %d" % (malas, len(R)))
