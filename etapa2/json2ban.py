"""
json2ban — genera los .ban de la perforadora SKH-612HS a partir del
`<ORDEN>-Mass production.json` que exporta GuiGui.

Resuelve el problema de los drill files incompletos (CONTEXTO.md seccion 6):
GuiGui escribe .ban sin los agujeros verticales ni las ranuras, pero el JSON
de produccion los tiene todos.

Uso:
    python3 json2ban.py  "<ORDEN>-Mass production.json"  -o  salida/
    python3 json2ban.py  BluenNC/  -o salida/ --bom
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import List

from ban import write_ban
from guigui import load_layout, panels_from_layout


def find_jsons(path: str) -> List[str]:
    if os.path.isfile(path):
        return [path]
    out = []
    for root, _dirs, files in os.walk(path):
        for f in files:
            if f.endswith("Mass production.json"):
                out.append(os.path.join(root, f))
    return sorted(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada", help="el JSON de produccion, o una carpeta que lo contenga")
    ap.add_argument("-o", "--salida", default="BAN_generado", help="carpeta de salida")
    ap.add_argument("--bom", action="store_true",
                    help="escribir con BOM UTF-8 (variante BAN_SC)")
    ap.add_argument("--arc-step", type=float, default=1.12,
                    help="paso de linealizacion de arcos en mm (default 1.12)")
    ap.add_argument("--back-slot-from-front", action="store_true",
                    help="variante BAN2: ranura de cara B cotada desde la cara A")
    ap.add_argument("--source", default="fabrica-muebles",
                    help="valor del atributo Source del encabezado")
    ap.add_argument("--edges-like-guigui", action="store_true",
                    help="no rotar los flags de canto en piezas rotadas (replica a GuiGui)")
    ap.add_argument("-q", "--quiet", action="store_true")
    a = ap.parse_args(argv)

    jsons = find_jsons(a.entrada)
    if not jsons:
        print(f"No se encontro ningun '*Mass production.json' en {a.entrada}", file=sys.stderr)
        return 2

    os.makedirs(a.salida, exist_ok=True)
    total = 0
    problemas = 0
    for jp in jsons:
        doc = load_layout(jp)
        panels = panels_from_layout(doc, rotate_edges=not a.edges_like_guigui)
        if not a.quiet:
            print(f"{os.path.basename(jp)}: {len(panels)} piezas")
        for p in panels:
            if not p.code:
                print(f"  !! pieza sin codigo de barras ({p.name}) — se omite", file=sys.stderr)
                problemas += 1
                continue
            out = os.path.join(a.salida, f"{p.code}.ban")
            write_ban(p, out, bom=a.bom, arc_step=a.arc_step, source=a.source,
                      back_slot_from_front=a.back_slot_from_front)
            total += 1
            if not a.quiet:
                print(f"  {p.code}.ban  {p.width:g}x{p.height:g}x{p.thickness:g}  "
                      f"{len(p.holes)} AgV  {len(p.side_holes)} AgH  {len(p.slots)} ranuras  "
                      f"{p.name}")
    print(f"\n{total} archivos escritos en {a.salida}")
    return 1 if problemas else 0


if __name__ == "__main__":
    raise SystemExit(main())
