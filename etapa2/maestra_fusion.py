# -*- coding: utf-8 -*-
"""
maestra_fusion — maestra.json (globos, etiquetas, lista de materiales) desde el
piezas.json que ExportarPiezas lee del SOLIDO de Fusion.

    python3 maestra_fusion.py <piezas.json> -o <carpeta> [--modelo modelo.json] [--orden-armado "Lateral,Liston,..."]

Es el gemelo de paquete.py (que lee el render.json de GuiGui): con esto el
camino Fusion tambien saca etiquetas (etiquetas.py) y lista de materiales
(materiales.py) sin pasar por GuiGui. Las medidas y los cantos salen del
piezas.json, igual que los programas de maquina, asi que la etiqueta y el
programa siempre hablan de la misma pieza.

--modelo (opcional): el modelo.json de una receta, para contar los herrajes.
"""
from __future__ import annotations

import argparse
import io
import json
import os
from collections import Counter, OrderedDict

ORDEN_DEF = ["Lateral", "Liston", "Zocalo", "Tapa inferior", "Piso", "Estante", "Techo", "Tapa superior",
             "Travesano", "Cenefa", "Fondo", "Puerta", "Frente", "Cajon"]


def _rango(nombre, orden):
    for i, k in enumerate(orden):
        if k.lower() in nombre.lower():
            return i
    return len(orden)


def herrajes_de(modelo, mueble):
    c = Counter()
    led = []
    for h in modelo.get("herrajes", []):
        if h["mueble"] != mueble:
            continue
        n = h["nombre"]
        if n.startswith("Excentrica"): c["excentricas"] += 1
        elif n.startswith("Perno"): c["pernos"] += 1
        elif n.startswith("Receptor"): c["receptores"] += 1
        elif n.startswith("Bisagra"): c["bisagras"] += 1
        elif n.startswith("Corredera"): c["correderas"] += 1
        elif n.startswith("Tira LED"): led.append(int(round(h["args"].get("largo", 0))))
    return {"excentricas": c["excentricas"], "pernos": c["pernos"], "receptores": c["receptores"],
            "bisagras": c["bisagras"], "tornillos_bisagra": 4 * c["bisagras"],
            "led": led, "correderas_pares": c["correderas"] // 2 if c["correderas"] else 0,
            "correderas_largo": "", "tornillos_corredera": 0}


def maestra(ruta_piezas, ruta_modelo=None, orden=None):
    with io.open(ruta_piezas, encoding="utf-8") as fh:
        d = json.load(fh)
    modelo = {}
    if ruta_modelo:
        with io.open(ruta_modelo, encoding="utf-8") as fh:
            modelo = json.load(fh)
    orden = orden or ORDEN_DEF
    muebles = OrderedDict()
    for p in d["piezas"]:
        muebles.setdefault(p.get("mueble") or "Mueble", []).append(p)
    out = []
    for i, (mu, ps) in enumerate(muebles.items()):
        ps = sorted(ps, key=lambda p: (_rango(p["nombre"].split("_")[-1], orden), p["nombre"]))
        piezas = []
        for g, p in enumerate(ps, 1):
            corto = p["nombre"].split("_")[-1]
            ca = {"izq": float(p.get("canto_izq", 0)), "der": float(p.get("canto_der", 0)),
                  "abajo": float(p.get("canto_abajo", 0)), "arriba": float(p.get("canto_arriba", 0))}
            W, H, T = p["ancho"], p["alto"], p["espesor"]
            rol = "FONDO" if T < 8 else ("PUERTA" if "puerta" in corto.lower() or "frente" in corto.lower()
                                          else "PLACA")
            piezas.append({
                "codigo": p["codigo"], "nombre": corto, "nombre_guigui": "", "nombre_largo": p["nombre"],
                "tipo": corto.split(" ")[0], "W": W, "H": H, "T": T, "dibujo_W": W, "dibujo_H": H,
                "aviso": "", "corte_W": round(W - ca["izq"] - ca["der"], 2),
                "corte_H": round(H - ca["abajo"] - ca["arriba"], 2),
                "material": p.get("material", ""), "textura": p.get("textura", ""), "cantos": ca,
                "veta": p.get("veta", "VERTICAL"), "rol": rol, "globo": g, "ean_ok": True,
                "herrajes": {}})
        out.append({"indice": i, "nombre": mu, "herrajes": herrajes_de(modelo, mu), "piezas": piezas})
    return {"ambiente": d.get("ambiente", ""), "orden": d.get("orden", ""), "cliente": d.get("cliente", ""),
            "version": "fusion", "muebles": out}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("piezas")
    ap.add_argument("-o", "--salida", default=".")
    ap.add_argument("--modelo")
    a = ap.parse_args()
    m = maestra(a.piezas, a.modelo)
    os.makedirs(a.salida, exist_ok=True)
    ruta = os.path.join(a.salida, "maestra.json")
    with io.open(ruta, "w", encoding="utf-8") as fh:
        json.dump(m, fh, ensure_ascii=False, indent=1)
    for mu in m["muebles"]:
        print("%s: %d piezas" % (mu["nombre"], len(mu["piezas"])))
        for p in mu["piezas"]:
            print("  %2d  %s  %-17s %g x %g x %g  corte %g x %g" % (p["globo"], p["codigo"], p["nombre"], p["H"],
                                                                   p["W"], p["T"], p["corte_H"], p["corte_W"]))
    print(ruta)


if __name__ == "__main__":
    main()
