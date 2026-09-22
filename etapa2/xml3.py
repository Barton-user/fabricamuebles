"""
Escritor  Panel -> XML KDT (星辉 / 极东, formato XML3)

Un archivo por pieza, UTF-8, saltos LF. Es el mas simple de los cuatro:
una lista plana de operaciones tipificadas, sin contorno.

Tabla de TypeNo (verificada contra la referencia de Bluen):
     1  agujero vertical, cara frontal
     8  agujero vertical, cara trasera
     2  agujero horizontal  (Quadrant: 1 = x=L · 2 = x=0 · 3 = y=W · 4 = y=0)
     3  ranura, cara frontal
    13  ranura, cara trasera

Ojo: PanelLength es el ANCHO del panel y PanelWidth es el ALTO.
"""

from __future__ import annotations

from typing import List

from panel import (EDGE_DOWN, EDGE_LEFT, EDGE_RIGHT, EDGE_UP, FACE_BACK,
                   Panel)

QUADRANT = {EDGE_RIGHT: 1, EDGE_LEFT: 2, EDGE_UP: 3, EDGE_DOWN: 4}

TYPE_HOLE_FRONT = 1
TYPE_HOLE_BACK = 8
TYPE_HOLE_SIDE = 2
TYPE_SLOT_FRONT = 3
TYPE_SLOT_BACK = 13


def _n(v: float) -> str:
    r = round(float(v) + 0.0, 2)
    if r == 0:
        r = 0.0
    return f"{r:.2f}"


def _esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def panel_to_xml3(p: Panel) -> str:
    L: List[str] = ["<KDTPanelFormat>", "    <PANEL>"]
    L.append(f"        <PanelLength>{_n(p.width)}</PanelLength>")
    L.append(f"        <PanelWidth>{_n(p.height)}</PanelWidth>")
    L.append(f"        <PanelThickness>{_n(p.thickness)}</PanelThickness>")
    L.append(f"        <PanelName>{_esc(p.name)}</PanelName>")
    L.append("        <Params>")
    L.append(f'            <Param Key="L" Value="{_n(p.width)}" Comment="板长"/>')
    L.append(f'            <Param Key="W" Value="{_n(p.height)}" Comment="板宽"/>')
    L.append(f'            <Param Key="T" Value="{_n(p.thickness)}" Comment="板厚"/>')
    L.append("        </Params>")
    L.append("    </PANEL>")

    for h in p.holes:
        tn = TYPE_HOLE_BACK if h.face == FACE_BACK else TYPE_HOLE_FRONT
        L += ["    <CAD>",
              f"        <TypeNo>{tn}</TypeNo>",
              "        <TypeName>Vertical Hole</TypeName>",
              f"        <X1>{_n(h.x)}</X1>",
              f"        <Y1>{_n(h.y)}</Y1>",
              f"        <Depth>{_n(h.depth)}</Depth>",
              f"        <Diameter>{_n(h.diameter)}</Diameter>",
              "        <Enable>1</Enable>",
              "        <HoleNo>1</HoleNo>",
              "        <IntervalX>0.00</IntervalX>",
              "        <IntervalY>0.00</IntervalY>",
              "    </CAD>"]

    for s in p.side_holes:
        L += ["    <CAD>",
              f"        <TypeNo>{TYPE_HOLE_SIDE}</TypeNo>",
              "        <TypeName>Horizontal Hole</TypeName>",
              f"        <X1>{_n(s.x)}</X1>",
              f"        <Y1>{_n(s.y)}</Y1>",
              f"        <Z1>{_n(s.z)}</Z1>",
              f"        <Quadrant>{QUADRANT[s.edge]}</Quadrant>",
              f"        <Depth>{_n(s.depth)}</Depth>",
              f"        <Diameter>{_n(s.diameter)}</Diameter>",
              "        <Enable>1</Enable>",
              "        <HoleNo>1</HoleNo>",
              "        <IntervalX>0.00</IntervalX>",
              "        <IntervalY>0.00</IntervalY>",
              "        <IntervalZ>0.00</IntervalZ>",
              "    </CAD>"]

    for sl in p.slots:
        tn = TYPE_SLOT_BACK if sl.face == FACE_BACK else TYPE_SLOT_FRONT
        L += ["    <CAD>",
              f"        <TypeNo>{tn}</TypeNo>",
              "        <TypeName>Line</TypeName>",
              f"        <BeginX>{_n(sl.x1)}</BeginX>",
              f"        <BeginY>{_n(sl.y1)}</BeginY>",
              f"        <EndX>{_n(sl.x2)}</EndX>",
              f"        <EndY>{_n(sl.y2)}</EndY>",
              "        <Correction>0</Correction>",
              f"        <Width>{_n(sl.width)}</Width>",
              f"        <Depth>{_n(sl.depth)}</Depth>",
              "        <Enable>1</Enable>",
              "    </CAD>"]

    L.append("</KDTPanelFormat>")
    return "\n".join(L) + "\n"


def write_xml3(p: Panel, path: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(panel_to_xml3(p))
