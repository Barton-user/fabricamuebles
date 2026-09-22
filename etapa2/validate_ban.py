"""
Diff SEMANTICO entre dos .ban.

Compara la geometria, no el texto: los agujeros y ranuras se comparan como
multiconjuntos con tolerancia, y el contorno por distancia maxima entre
polilineas (asi un arco linealizado con otro paso no cuenta como diferencia).

Uso:
    python3 validate_ban.py  GENERADOS/  REFERENCIA/
    python3 validate_ban.py  a.ban  b.ban
"""

from __future__ import annotations

import math
import os
import sys
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Tuple

TOL = 0.02        # mm — tolerancia para agujeros, ranuras y medidas
OUTLINE_TOL = 0.6  # mm — tolerancia para el contorno (arcos linealizados distinto)


def _pt(s: str) -> Tuple[float, float, float]:
    a = [float(v) for v in s.split()]
    while len(a) < 3:
        a.append(0.0)
    return (a[0], a[1], a[2])


def parse(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8-sig") as fh:
        root = ET.fromstring(fh.read())
    plane = root.find("Plane")
    if plane is None:
        raise ValueError(f"{path}: no tiene <Plane>")
    a = plane.attrib
    d: Dict[str, Any] = {
        "width": float(a.get("Width", a.get("Wight", 0)) or 0),
        "height": float(a.get("Height", a.get("Hight", 0)) or 0),
        "thickness": float(a.get("Thickness", 0) or 0),
        "material": a.get("Material", ""),
        "name": a.get("Name", ""),
        "code": a.get("Code", ""),
        "grain": a.get("Grain", ""),
        "edges": a.get("EdgeFBLR", ""),
        "qty": a.get("PlaneSize", ""),
    }
    ol = plane.find("Outline")
    d["outline"] = [_pt(p.get("Value", "0 0 0"))[:2]
                    for p in (ol.findall("Point") if ol is not None else [])]
    d["holev"] = sorted(
        (round(float(h.get("Diameter", 0)), 2), h.get("Face", ""),
         round(_pt(h.get("Start", "0 0 0"))[0], 2), round(_pt(h.get("Start", "0 0 0"))[1], 2),
         round(abs(_pt(h.get("End", "0 0 0"))[2]), 2))
        for h in plane.findall("HoleV"))
    d["holeh"] = sorted(
        (round(float(h.get("Diameter", 0)), 2), h.get("Face", ""),
         round(_pt(h.get("Start", "0 0 0"))[0], 2), round(_pt(h.get("Start", "0 0 0"))[1], 2),
         round(abs(_pt(h.get("Start", "0 0 0"))[2]), 2),
         round(math.dist(_pt(h.get("Start", "0 0 0"))[:2], _pt(h.get("End", "0 0 0"))[:2]), 2))
        for h in plane.findall("HoleH"))
    slots = []
    for s in plane.findall("SlotL"):
        p1 = _pt(s.get("Start", "0 0 0"))
        p2 = _pt(s.get("End", "0 0 0"))
        ends = tuple(sorted([(round(p1[0], 2), round(p1[1], 2)), (round(p2[0], 2), round(p2[1], 2))]))
        slots.append((s.get("Face", ""), round(float(s.get("Width", 0)), 2),
                      round(abs(p1[2]), 2), ends))
    d["slots"] = sorted(slots)
    return d


def _seg_dist(p, a, b) -> float:
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return math.dist(p, a)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.dist(p, (ax + t * dx, ay + t * dy))


def _poly_dev(A: List[Tuple[float, float]], B: List[Tuple[float, float]]) -> float:
    if not A or len(B) < 2:
        return float("inf")
    return max(min(_seg_dist(p, B[i], B[i + 1]) for i in range(len(B) - 1)) for p in A)


def compare(gen: str, ref: str) -> List[str]:
    a, b = parse(gen), parse(ref)
    msgs: List[str] = []

    for k, label in (("width", "Width"), ("height", "Height"), ("thickness", "Thickness")):
        if abs(a[k] - b[k]) > TOL:
            msgs.append(f"{label}: {a[k]} != {b[k]}")
    for k, label in (("code", "Code"), ("material", "Material"), ("grain", "Grain")):
        if a[k] != b[k]:
            msgs.append(f"{label}: {a[k]!r} != {b[k]!r}")
    if a["name"] != b["name"]:
        msgs.append(f"Name: {a['name']!r} != {b['name']!r}")
    if a["edges"].replace(" ", "") != b["edges"].replace(" ", ""):
        msgs.append(f"EdgeFBLR: {a['edges']} != {b['edges']}")

    for key, label in (("holev", "HoleV"), ("holeh", "HoleH"), ("slots", "SlotL")):
        ga, gb = list(a[key]), list(b[key])
        if len(ga) != len(gb):
            msgs.append(f"{label}: cantidad {len(ga)} != {len(gb)}")
            msgs.append(f"    generado : {ga}")
            msgs.append(f"    referencia: {gb}")
            continue
        for x, y in zip(ga, gb):
            if not _tuple_eq(x, y):
                msgs.append(f"{label}: {x} != {y}")

    dev = max(_poly_dev(a["outline"], b["outline"]), _poly_dev(b["outline"], a["outline"]))
    if dev > OUTLINE_TOL:
        msgs.append(f"Outline: desviacion maxima {dev:.3f} mm "
                    f"({len(a['outline'])} vs {len(b['outline'])} puntos)")
    return msgs


def _tuple_eq(x, y) -> bool:
    if len(x) != len(y):
        return False
    for u, v in zip(x, y):
        if isinstance(u, (int, float)) and isinstance(v, (int, float)):
            if abs(u - v) > TOL:
                return False
        elif isinstance(u, tuple) and isinstance(v, tuple):
            if not _tuple_eq(u, v):
                return False
        elif u != v:
            return False
    return True


def main(argv: List[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    gen, ref = argv[1], argv[2]
    if os.path.isfile(gen) and os.path.isfile(ref):
        pairs = [(os.path.basename(gen), gen, ref)]
    else:
        names = sorted(f for f in os.listdir(ref) if f.lower().endswith(".ban"))
        pairs = [(n, os.path.join(gen, n), os.path.join(ref, n)) for n in names]

    ok = bad = missing = 0
    for name, g, r in pairs:
        if not os.path.exists(g):
            print(f"[FALTA]  {name}  — no se genero")
            missing += 1
            continue
        msgs = compare(g, r)
        if msgs:
            bad += 1
            print(f"[DIFF]   {name}")
            for m in msgs:
                print(f"         {m}")
        else:
            ok += 1
            print(f"[OK]     {name}")
    print(f"\n{ok} iguales, {bad} con diferencias, {missing} faltantes, de {len(pairs)}")
    return 0 if bad == 0 and missing == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
