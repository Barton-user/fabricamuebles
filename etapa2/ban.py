"""
Escritor  Panel -> MicroDrawBan XML 3.0 (.ban)  para la perforadora SKH-612HS.

Un archivo por pieza; el nombre del archivo es el codigo de barras.
"""

from __future__ import annotations

import datetime as _dt
from typing import List, Optional

from panel import (EDGE_DOWN, EDGE_LEFT, EDGE_RIGHT, EDGE_UP, FACE_BACK,
                   Panel, flatten_outline)

BAN_HEADER = ('<MicroDrawBan_XML Version="3.0" Time="{time}" '
              'Source="{source}" SourceType="BAN">')


def _n(v: float, nd: int = 2) -> str:
    """Numero al formato del .ban: 2 decimales, sin cero negativo."""
    r = round(float(v) + 0.0, nd)
    if r == 0:
        r = 0.0
    return f"{r:.{nd}f}"


def _thick(v: float) -> str:
    return str(int(round(v))) if abs(v - round(v)) < 1e-6 else f"{v:g}"


def _edge(v: float) -> str:
    return str(int(v)) if abs(v - round(v)) < 1e-9 else f"{v:g}"


def _esc(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _timestamp(when: Optional[_dt.datetime] = None) -> str:
    when = when or _dt.datetime.now()
    ampm = "am" if when.hour < 12 else "pm"
    h12 = when.hour % 12 or 12
    return f"{when:%Y/%m/%d} {ampm} {h12}:{when:%M:%S}"


def panel_to_ban(p: Panel, *, arc_step: float = 1.12,
                 when: Optional[_dt.datetime] = None,
                 source: str = "fabrica-muebles",
                 back_slot_from_front: bool = False) -> str:
    """Serializa un Panel al XML del .ban.

    back_slot_from_front=True replica la variante BAN2, donde la ranura de la
    cara B se cota desde la cara A (Z = -(espesor - profundidad)).
    """
    L: List[str] = [BAN_HEADER.format(time=_timestamp(when), source=_esc(source))]
    L.append(
        f'<Plane Width="{_n(p.width)}" Height="{_n(p.height)}" '
        f'PlaneSize="{p.quantity}" Grain="{_esc(p.grain)}" Thickness="{_thick(p.thickness)}" '
        f'Material="{_esc(p.material)}" '
        f'EdgeFBLR="{_edge(p.edge_front)},{_edge(p.edge_back)},'
        f'{_edge(p.edge_left)},{_edge(p.edge_right)}" '
        f'Name="{_esc(p.name)}" Code="{_esc(p.code)}">'
    )

    L.append("    <Outline>")
    for x, y in flatten_outline(p.ensure_outline(), step_mm=arc_step, close=True):
        L.append(f'        <Point Value="{_n(x)} {_n(y)} 0"/>')
    L.append("    </Outline>")

    for h in p.holes:
        # El eje Z se mide SIEMPRE desde la cara A (Z=0 en A, -espesor en B).
        # Un agujero de cara B arranca en Z=-espesor y avanza hacia Z=0.
        if h.face == FACE_BACK:
            z0, z1 = -abs(p.thickness), -(abs(p.thickness) - abs(h.depth))
        else:
            z0, z1 = 0.0, -abs(h.depth)
        L.append(
            f'    <HoleV Name="" Diameter="{_n(h.diameter)}" IsCuted="0" Face="{h.face}" '
            f'Start="{_n(h.x)} {_n(h.y)} {"0" if z0 == 0 else _n(z0)}" '
            f'End="{_n(h.x)} {_n(h.y)} {_n(z1)}"/>'
        )

    for s in p.side_holes:
        (sx, sy), (ex, ey) = s.start_end()
        z = _n(-abs(s.z))
        L.append(
            f'    <HoleH Name="" Diameter="{_n(s.diameter)}" IsCuted="0" Face="{s.edge}" '
            f'Start="{_n(sx)} {_n(sy)} {z}" End="{_n(ex)} {_n(ey)} {z}"/>'
        )

    for sl in p.slots:
        depth = abs(sl.depth)
        if sl.face == FACE_BACK and back_slot_from_front:
            depth = abs(p.thickness) - depth
        z = _n(-depth)
        L.append(
            f'    <SlotL Name="" Face="{sl.face}" '
            f'Start="{_n(sl.x1)} {_n(sl.y1)} {z}" End="{_n(sl.x2)} {_n(sl.y2)} {z}" '
            f'Width="{_n(sl.width)}" IsCuted="0"/>'
        )

    L.append("</Plane>")
    L.append("</MicroDrawBan_XML>")
    return "\n".join(L)


def write_ban(p: Panel, path: str, *, bom: bool = False, **kw) -> None:
    text = panel_to_ban(p, **kw)
    enc = "utf-8-sig" if bom else "utf-8"
    with open(path, "w", encoding=enc, newline="\n") as fh:
        fh.write(text)
