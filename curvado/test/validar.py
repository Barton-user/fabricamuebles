"""Compara los escritores JS contra etapa2 (Python), byte a byte.
   uso:  python3 test/validar.py <carpeta etapa2>"""
import csv, io, json, sys, glob, os
sys.path.insert(0, sys.argv[1])
from panel import Panel, Slot
import xml3, mpr, listacorte

ok = fail = 0
def cmp(nombre, a, b):
    global ok, fail
    if a == b: ok += 1; print("  OK  ", nombre)
    else:
        fail += 1; print("  FALLA", nombre)
        for i, (x, y) in enumerate(zip(a.splitlines(), b.splitlines())):
            if x != y: print("     py:", x, "\n     js:", y); break

paneles = []
for f in sorted(glob.glob("test/out/*.json")):
    d = json.load(open(f, encoding="utf-8"))
    e = d["edges"]
    p = Panel(code=d["code"], name=d["name"], width=d["width"], height=d["height"], thickness=d["thickness"],
              material=d["material"], texture=d["texture"], grain=d["grain"], quantity=d["quantity"],
              edge_front=e.get("down", 0), edge_back=e.get("up", 0), edge_left=e.get("left", 0), edge_right=e.get("right", 0),
              src_width=d["width"], src_height=d["height"],
              src_edge_left=e.get("left", 0), src_edge_right=e.get("right", 0), src_edge_up=e.get("up", 0), src_edge_down=e.get("down", 0),
              order_no=d["order_no"], customer=d["customer"], address=d["address"], location=d["location"],
              short_name=d["short_name"], plank_id=d["plank_id"])
    p.slots = [Slot(s["x1"], s["y1"], s["x2"], s["y2"], s["width"], s["depth"], s["face"]) for s in d["slots"]]
    paneles.append(p)
    base = f[:-5]
    cmp(os.path.basename(base) + ".xml", xml3.panel_to_xml3(p), open(base + ".xml", encoding="utf-8", newline="").read())
    cmp(os.path.basename(base) + ".mpr", mpr.panel_to_mpr(p), open(base + ".mpr", encoding="gbk", newline="").read())
    if mpr.has_back_ops(p):
        cmp(os.path.basename(base) + "K.mpr", mpr.panel_to_mpr(p, back=True), open(base + "K.mpr", encoding="gbk", newline="").read())

buf = io.StringIO()
w = csv.writer(buf); w.writerow(listacorte.COLUMNAS); w.writerows(listacorte.fila(p, i + 1) for i, p in enumerate(paneles))
cmp("lista_corte.csv", "﻿" + buf.getvalue(), open("test/out/lista_corte.csv", encoding="utf-8", newline="").read())
print(f"\n{ok} iguales, {fail} distintos")
sys.exit(1 if fail else 0)
