"""
exportar — genera los archivos de maquina a partir del `Mass production.json`
de GuiGui, en los cuatro formatos que puede leer una perforadora de seis caras.

    python3 exportar.py "<ORDEN>-Mass production.json" -o salida/

Escribe:
    salida/BAN/<codigo>.ban        MicroDrawBan XML 3.0
    salida/MPR/<codigo>.mpr        WoodWOP / Homag  (+ <codigo>K.mpr si hay cara trasera)
    salida/XML1/<codigo>.xml       formato "Plate"
    salida/XML3/<codigo>.xml       formato KDT

Con --formatos se elige un subconjunto:  --formatos ban,mpr
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import List

from ban import write_ban
from cargar import buscar, cargar
from mpr import has_back_ops, has_ops, write_mpr
from xml1 import write_xml1
from xml3 import write_xml3

FORMATOS = ("ban", "mpr", "xml1", "xml3")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada",
                    help="'<ORDEN>-Mass production.json' (GuiGui) o 'piezas.json' (Fusion), "
                         "o una carpeta que los contenga")
    ap.add_argument("-o", "--salida", default="salida", help="carpeta de salida")
    ap.add_argument("--formatos", default=",".join(FORMATOS),
                    help="subconjunto a generar, separado por comas (%s)" % ",".join(FORMATOS))
    ap.add_argument("--bom", action="store_true", help="BAN con BOM UTF-8 (variante BAN_SC)")
    ap.add_argument("--arc-step", type=float, default=1.12,
                    help="paso de linealizacion de arcos en mm")
    ap.add_argument("--back-slot-from-front", action="store_true",
                    help="BAN variante BAN2: ranura de cara B cotada desde la cara A")
    ap.add_argument("--edges-like-guigui", action="store_true",
                    help="no rotar los flags de canto en piezas rotadas (replica a GuiGui)")
    ap.add_argument("-q", "--quiet", action="store_true")
    a = ap.parse_args(argv)

    fmts = [f.strip().lower() for f in a.formatos.split(",") if f.strip()]
    malos = [f for f in fmts if f not in FORMATOS]
    if malos:
        print(f"Formato desconocido: {', '.join(malos)}", file=sys.stderr)
        return 2

    jsons = buscar(a.entrada)
    if not jsons:
        print(f"No se encontro ninguna entrada en {a.entrada}", file=sys.stderr)
        return 2

    dirs = {f: os.path.join(a.salida, f.upper()) for f in fmts}
    for d in dirs.values():
        os.makedirs(d, exist_ok=True)

    cuenta = {f: 0 for f in fmts}
    problemas = 0

    for jp in jsons:
        panels = cargar(jp, rotate_edges=not a.edges_like_guigui)
        if not a.quiet:
            print(f"\n{os.path.basename(jp)}: {len(panels)} piezas")
        for p in panels:
            if not p.code:
                print(f"  !! pieza sin codigo de barras ({p.name}) — se omite", file=sys.stderr)
                problemas += 1
                continue
            # Una ranura de CANTO no se sabe escribir: no hay ni una en los 82
            # archivos de referencia de Bluen, asi que el elemento de maquina es
            # desconocido. Escribir cualquier cosa manda un programa equivocado a
            # la perforadora, que es peor que no mandar nada.
            if getattr(p, "edge_slots", None):
                det = "; ".join(
                    "canto %s, %.1f ancho x %.1f prof" %
                    (r.get("canto", "?"), float(r.get("ancho", 0)),
                     float(r.get("profundidad", 0))) for r in p.edge_slots)
                print(f"  !! {p.code} ({p.name}) tiene RANURA DE CANTO — se omite",
                      file=sys.stderr)
                print(f"     {det}", file=sys.stderr)
                print("     El formato de maquina para ranuras de canto todavia no "
                      "esta verificado.", file=sys.stderr)
                print("     Esa ranura hay que hacerla aparte, o confirmar el formato "
                      "con HUAHUA antes.", file=sys.stderr)
                problemas += 1
                continue
            extra = ""
            if "ban" in fmts:
                write_ban(p, os.path.join(dirs["ban"], f"{p.code}.ban"), bom=a.bom,
                          arc_step=a.arc_step,
                          back_slot_from_front=a.back_slot_from_front)
                cuenta["ban"] += 1
            if "mpr" in fmts and has_ops(p):
                write_mpr(p, os.path.join(dirs["mpr"], f"{p.code}.mpr"))
                cuenta["mpr"] += 1
                if has_back_ops(p):
                    write_mpr(p, os.path.join(dirs["mpr"], f"{p.code}K.mpr"), back=True)
                    cuenta["mpr"] += 1
                    extra = "  +K"
            if "xml1" in fmts:
                write_xml1(p, os.path.join(dirs["xml1"], f"{p.code}.xml"), arc_step=a.arc_step)
                cuenta["xml1"] += 1
            if "xml3" in fmts:
                write_xml3(p, os.path.join(dirs["xml3"], f"{p.code}.xml"))
                cuenta["xml3"] += 1
            if not a.quiet:
                print(f"  {p.code}  {p.width:g}x{p.height:g}x{p.thickness:g}  "
                      f"{len(p.holes)} AgV  {len(p.side_holes)} AgH  "
                      f"{len(p.slots)} ranuras{extra}  {p.name}")

    print("\n" + "  ".join(f"{f.upper()}: {n}" for f, n in cuenta.items())
          + f"   →  {a.salida}")
    return 1 if problemas else 0


if __name__ == "__main__":
    raise SystemExit(main())
