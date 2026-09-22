"""
Escritor  Panel -> XML "Plate" (formato XML1)

Un archivo por pieza, UTF-8, saltos LF.

Ojo con la cabecera: `width` es el ALTO del panel y `depth` es el ANCHO
(invertidos respecto del .ban). Las coordenadas de agujeros y ranuras, en cambio,
son las mismas que en el .ban.

  direction     1 = vertical · 0 = horizontal
  positionSide  1 = cara frontal · 0 = cara trasera
  drillDirection  vector unitario de avance de la mecha
  El contorno va como segmentos, en sentido inverso al del .ban, y con los
  arcos ya linealizados (el formato no usa arcos).
"""

from __future__ import annotations

from typing import List

from panel import (EDGE_DOWN, EDGE_LEFT, EDGE_RIGHT, EDGE_UP, FACE_BACK,
                   Panel, flatten_outline)

DRILL_DIR = {EDGE_LEFT: "(1,0,0)", EDGE_RIGHT: "(-1,0,0)",
             EDGE_DOWN: "(0,1,0)", EDGE_UP: "(0,-1,0)"}


def _n(v: float, nd: int = 2) -> str:
    r = round(float(v) + 0.0, nd)
    if r == 0:
        r = 0.0
    return f"{r:.{nd}f}"


def _edge(v: float) -> str:
    return str(int(v)) if abs(v - round(v)) < 1e-9 else f"{v:g}"


def _esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _collection(tag: str, rows: List[str], indent: str = "    ") -> List[str]:
    if not rows:
        return [f"{indent}<{tag}/>"]
    return [f"{indent}<{tag}>"] + rows + [f"{indent}</{tag}>"]


def panel_to_xml1(p: Panel, *, arc_step: float = 1.12) -> str:
    t = _n(p.thickness)
    L: List[str] = ['<?xml version="1.0" encoding="UTF-8"?>']
    L.append(
        f'<Plate plateNumber="{_esc(p.code)}" plateNickName="{_esc(p.name)}" '
        f'width="{_n(p.height)}" depth="{_n(p.width)}" height="{t}" '
        f'barCode="{_esc(p.code)}" barCode1="">'
    )
    L.append("    <Bandings>")
    L.append(f'        <Banding bandingBack="{_edge(p.edge_back)}" '
             f'bandingRight="{_edge(p.edge_right)}" '
             f'bandingFront="{_edge(p.edge_front)}" '
             f'bandingLeft="{_edge(p.edge_left)}"/>')
    L.append("    </Bandings>")

    holes: List[str] = []
    for h in p.holes:
        back = h.face == FACE_BACK
        holes.append(
            f'        <Hole point="({_n(h.x)},{_n(h.y)},{t})" '
            f'diameter="{_n(h.diameter)}" depth="{_n(h.depth)}" direction="1" '
            f'positionSide="{0 if back else 1}" '
            f'drillDirection="{"(0,0,1)" if back else "(0,0,-1)"}"/>'
        )
    for s in p.side_holes:
        holes.append(
            f'        <Hole point="({_n(s.x)},{_n(s.y)},{_n(s.z)})" '
            f'diameter="{_n(s.diameter)}" depth="{_n(s.depth)}" direction="0" '
            f'positionSide="1" drillDirection="{DRILL_DIR[s.edge]}"/>'
        )
    L += _collection("Holes", holes)

    slots: List[str] = []
    for sl in p.slots:
        slots.append(
            f'        <Slotting positionSide="{0 if sl.face == FACE_BACK else 1}" '
            f'slottingStartX="{_n(sl.x1)}" slottingStartY="{_n(sl.y1)}" '
            f'slottingStartZ="0.000" slottingEndX="{_n(sl.x2)}" '
            f'slottingEndY="{_n(sl.y2)}" slottingEndZ="0.000" '
            f'slottingWidth="{_n(sl.width)}" slottingDepth="{_n(sl.depth)}"/>'
        )
    L += _collection("Slottings", slots)
    L.append("    <YXJSlottings/>")
    L.append("    <H_Slottings/>")

    pts = flatten_outline(p.ensure_outline(), step_mm=arc_step, close=True)
    pts = list(reversed(pts))                      # el XML1 recorre al reves que el .ban
    if len(pts) > 2:                               # ...y arranca un vertice mas adelante
        pts = pts[1:] + pts[1:2]
    segs: List[str] = []
    for i in range(len(pts) - 1):
        (x1, y1), (x2, y2) = pts[i], pts[i + 1]
        segs.append(
            f'        <Point startPoint="({_n(x1)},{_n(y1)},{t})" '
            f'endPoint="({_n(x2)},{_n(y2)},{t})" center="(0,0,0)" radius="" '
            f'arcDirection="0" millingIndex="0" cutHeight="" isLagestEdge="1" '
            f'cutPositionSide="正面"/>'
        )
    L += _collection("Points", segs)

    L.append("</Plate>")
    return "\n".join(L) + "\n"


def write_xml1(p: Panel, path: str, **kw) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(panel_to_xml1(p, **kw))
