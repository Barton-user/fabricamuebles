"""
Diff SEMANTICO de archivos de maquina, para los cuatro formatos.

Compara la geometria, no el texto: agujeros y ranuras como multiconjuntos con
tolerancia, y el contorno por distancia maxima entre polilineas (asi un arco
linealizado con otro paso no cuenta como diferencia).

    python3 validar.py ban   GENERADOS/  REFERENCIA/
    python3 validar.py mpr   GENERADOS/  REFERENCIA/
    python3 validar.py xml1  GENERADOS/  REFERENCIA/
    python3 validar.py xml3  GENERADOS/  REFERENCIA/
"""

from __future__ import annotations

import math
import os
import re
import sys
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Sequence, Tuple

TOL = 0.02
OUTLINE_TOL = 0.6
EXT = {"ban": ".ban", "mpr": ".mpr", "xml1": ".xml", "xml3": ".xml"}


# ---------- helpers ----------

def _t(s: str) -> Tuple[float, ...]:
    return tuple(float(v) for v in s.split())


def _p3(s: str) -> Tuple[float, float, float]:
    a = list(_t(s)) + [0.0, 0.0, 0.0]
    return (a[0], a[1], a[2])


def _tup(s: str) -> Tuple[float, ...]:
    return tuple(float(v) for v in s.strip("()").split(","))


def _r(v: float) -> float:
    return round(float(v), 2) + 0.0


def _seg_dist(p, a, b) -> float:
    (ax, ay), (bx, by), (px, py) = a, b, p
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return math.dist(p, a)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.dist(p, (ax + t * dx, ay + t * dy))


def _poly_dev(A, B) -> float:
    if not A:
        return 0.0
    if len(B) < 2:
        return float("inf")
    return max(min(_seg_dist(p, B[i], B[i + 1]) for i in range(len(B) - 1)) for p in A)


# ---------- parsers: cada uno devuelve una estructura canonica ----------

def parse_ban(path: str) -> Dict[str, Any]:
    with open(path, encoding="utf-8-sig") as fh:
        plane = ET.fromstring(fh.read()).find("Plane")
    a = plane.attrib
    th = float(a.get("Thickness", 0) or 0)
    d: Dict[str, Any] = {
        "size": (_r(float(a.get("Width", 0) or 0)), _r(float(a.get("Height", 0) or 0)), _r(th)),
        "name": a.get("Name", ""), "code": a.get("Code", ""),
        "edges": a.get("EdgeFBLR", "").replace(" ", ""),
    }
    ol = plane.find("Outline")
    d["outline"] = [_p3(p.get("Value", "0 0 0"))[:2]
                    for p in (ol.findall("Point") if ol is not None else [])]
    hv = []
    for h in plane.findall("HoleV"):
        s, e = _p3(h.get("Start", "0 0 0")), _p3(h.get("End", "0 0 0"))
        face = h.get("Face", "")
        depth = abs(e[2] - s[2])
        hv.append((_r(float(h.get("Diameter", 0))), face, _r(s[0]), _r(s[1]), _r(depth)))
    d["holev"] = sorted(hv)
    hh = []
    for h in plane.findall("HoleH"):
        s, e = _p3(h.get("Start", "0 0 0")), _p3(h.get("End", "0 0 0"))
        hh.append((_r(float(h.get("Diameter", 0))), h.get("Face", ""), _r(s[0]), _r(s[1]),
                   _r(abs(s[2])), _r(math.dist(s[:2], e[:2]))))
    d["holeh"] = sorted(hh)
    sl = []
    for s in plane.findall("SlotL"):
        p1, p2 = _p3(s.get("Start", "0 0 0")), _p3(s.get("End", "0 0 0"))
        face = s.get("Face", "")
        depth = abs(p1[2]) if face != "B" else min(abs(p1[2]), _r(th) - abs(p1[2]))
        sl.append((face, _r(float(s.get("Width", 0))), _r(depth),
                   tuple(sorted([(_r(p1[0]), _r(p1[1])), (_r(p2[0]), _r(p2[1]))]))))
    d["slots"] = sorted(sl)
    return d


def parse_mpr(path: str) -> Dict[str, Any]:
    raw = open(path, "rb").read().decode("gbk", errors="replace")
    lines = raw.replace("\r\n", "\n").split("\n")
    blocks: List[Tuple[str, Dict[str, str]]] = []
    header: Dict[str, str] = {}
    cur = None
    for ln in lines:
        ln = ln.strip()
        if ln.startswith("[H\\"):
            for part in ln[3:].split(";"):
                if ":" in part:
                    k, v = part.split(":", 1)
                    header[k.strip()] = v.strip()
            continue
        m = re.match(r"^<(\d+)\s+\\(.+?)\\", ln)
        if m:
            cur = (m.group(1), {})
            blocks.append(cur)
            continue
        m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)="(.*)"$', ln)
        if m and cur is not None:
            cur[1][m.group(1)] = m.group(2)
    by = lambda n: [b[1] for b in blocks if b[0] == n]
    w = by("100")[0] if by("100") else {}
    d: Dict[str, Any] = {
        "size": (_r(float(w.get("LA", 0))), _r(float(w.get("BR", 0))), _r(float(w.get("DI", 0)))),
        "edges": ",".join(header.get(k, "") for k in ("Left", "Bottom", "Right", "Top")),
        "name": (by("101")[0].get("KM", "") if by("101") else ""),
        "holev": sorted((_r(float(b["DU"])), _r(float(b["XA"])), _r(float(b["YA"])),
                         _r(float(b["TI"]))) for b in by("102")),
        "holeh": sorted((_r(float(b["DU"])), b.get("BM", ""), _r(float(b["XA"])),
                         _r(float(b["YA"])), _r(float(b["ZA"])), _r(float(b["TI"])))
                        for b in by("103")),
        "slots": sorted((_r(float(b["NB"])), _r(float(b["TI"])),
                         tuple(sorted([(_r(float(b["XA"])), _r(float(b["YA"]))),
                                       (_r(float(b["XE"])), _r(float(b["YE"])))])))
                        for b in by("109")),
        "outline": [],
    }
    return d


def parse_xml1(path: str) -> Dict[str, Any]:
    root = ET.parse(path).getroot()
    a = root.attrib
    d: Dict[str, Any] = {
        "size": (_r(float(a.get("depth", 0))), _r(float(a.get("width", 0))),
                 _r(float(a.get("height", 0)))),
        "code": a.get("plateNumber", ""), "name": a.get("plateNickName", ""),
    }
    b = root.find("./Bandings/Banding")
    d["edges"] = ",".join((b.get(k, "") if b is not None else "")
                          for k in ("bandingFront", "bandingBack", "bandingLeft", "bandingRight"))
    hv, hh = [], []
    for h in root.findall("./Holes/Hole"):
        pt = _tup(h.get("point", "(0,0,0)"))
        rec = (_r(float(h.get("diameter", 0))), _r(pt[0]), _r(pt[1]),
               _r(float(h.get("depth", 0))), h.get("positionSide", ""),
               h.get("drillDirection", ""))
        (hv if h.get("direction") == "1" else hh).append(rec + ((_r(pt[2]),) if h.get("direction") != "1" else ()))
    d["holev"], d["holeh"] = sorted(hv), sorted(hh)
    d["slots"] = sorted(
        (s.get("positionSide", ""), _r(float(s.get("slottingWidth", 0))),
         _r(float(s.get("slottingDepth", 0))),
         tuple(sorted([(_r(float(s.get("slottingStartX", 0))), _r(float(s.get("slottingStartY", 0)))),
                       (_r(float(s.get("slottingEndX", 0))), _r(float(s.get("slottingEndY", 0))))])))
        for s in root.findall("./Slottings/Slotting"))
    pts = []
    for p in root.findall("./Points/Point"):
        sp = _tup(p.get("startPoint", "(0,0,0)"))
        pts.append((sp[0], sp[1]))
    if pts:
        ep = _tup(root.findall("./Points/Point")[-1].get("endPoint", "(0,0,0)"))
        pts.append((ep[0], ep[1]))
    d["outline"] = pts
    return d


def parse_xml3(path: str) -> Dict[str, Any]:
    root = ET.parse(path).getroot()
    p = root.find("PANEL")
    g = lambda e, t: float(e.findtext(t, "0") or 0)
    d: Dict[str, Any] = {
        "size": (_r(g(p, "PanelLength")), _r(g(p, "PanelWidth")), _r(g(p, "PanelThickness"))),
        "name": p.findtext("PanelName", ""), "edges": "", "outline": [],
    }
    hv, hh, sl = [], [], []
    for c in root.findall("CAD"):
        tn = int(c.findtext("TypeNo", "0"))
        if tn in (1, 8):
            hv.append((tn, _r(g(c, "Diameter")), _r(g(c, "X1")), _r(g(c, "Y1")), _r(g(c, "Depth"))))
        elif tn == 2:
            hh.append((_r(g(c, "Diameter")), int(c.findtext("Quadrant", "0")), _r(g(c, "X1")),
                       _r(g(c, "Y1")), _r(g(c, "Z1")), _r(g(c, "Depth"))))
        elif tn in (3, 13):
            sl.append((tn, _r(g(c, "Width")), _r(g(c, "Depth")),
                       tuple(sorted([(_r(g(c, "BeginX")), _r(g(c, "BeginY"))),
                                     (_r(g(c, "EndX")), _r(g(c, "EndY")))]))))
    d["holev"], d["holeh"], d["slots"] = sorted(hv), sorted(hh), sorted(sl)
    return d


PARSERS = {"ban": parse_ban, "mpr": parse_mpr, "xml1": parse_xml1, "xml3": parse_xml3}


# ---------- comparacion ----------

def _eq(x, y) -> bool:
    if isinstance(x, (int, float)) and isinstance(y, (int, float)):
        return abs(x - y) <= TOL
    if isinstance(x, tuple) and isinstance(y, tuple):
        return len(x) == len(y) and all(_eq(u, v) for u, v in zip(x, y))
    return x == y


def compare(fmt: str, gen: str, ref: str) -> List[str]:
    a, b = PARSERS[fmt](gen), PARSERS[fmt](ref)
    msgs: List[str] = []
    if not _eq(a["size"], b["size"]):
        msgs.append(f"medidas: {a['size']} != {b['size']}")
    for k in ("name", "code", "edges"):
        if k in a and k in b and a[k] != b[k]:
            msgs.append(f"{k}: {a[k]!r} != {b[k]!r}")
    for key, label in (("holev", "agujeros verticales"), ("holeh", "agujeros horizontales"),
                       ("slots", "ranuras")):
        ga, gb = a.get(key, []), b.get(key, [])
        if len(ga) != len(gb):
            msgs.append(f"{label}: cantidad {len(ga)} != {len(gb)}")
            msgs.append(f"    generado  : {ga}")
            msgs.append(f"    referencia: {gb}")
            continue
        for x, y in zip(ga, gb):
            if not _eq(x, y):
                msgs.append(f"{label}: {x} != {y}")
    if a.get("outline") or b.get("outline"):
        dev = max(_poly_dev(a["outline"], b["outline"]), _poly_dev(b["outline"], a["outline"]))
        if dev > OUTLINE_TOL:
            msgs.append(f"contorno: desviacion maxima {dev:.3f} mm "
                        f"({len(a['outline'])} vs {len(b['outline'])} puntos)")
    return msgs


def main(argv: List[str]) -> int:
    if len(argv) != 4 or argv[1] not in PARSERS:
        print(__doc__)
        return 2
    fmt, gen, ref = argv[1], argv[2], argv[3]
    ext = EXT[fmt]
    names = sorted(f for f in os.listdir(ref) if f.lower().endswith(ext))
    ok = bad = missing = extra = 0
    for n in names:
        g = os.path.join(gen, n)
        if not os.path.exists(g):
            print(f"[FALTA]  {n}")
            missing += 1
            continue
        msgs = compare(fmt, g, os.path.join(ref, n))
        if msgs:
            bad += 1
            print(f"[DIFF]   {n}")
            for m in msgs:
                print(f"         {m}")
        else:
            ok += 1
            print(f"[OK]     {n}")
    for f in sorted(os.listdir(gen)):
        if f.lower().endswith(ext) and f not in names:
            print(f"[SOBRA]  {f}  — no existe en la referencia")
            extra += 1
    print(f"\n{ok} iguales, {bad} con diferencias, {missing} faltantes, "
          f"{extra} de mas, sobre {len(names)} de referencia")
    return 0 if (bad or missing or extra) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
