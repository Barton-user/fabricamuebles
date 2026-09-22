"""
Lector del  <ORDEN>-Mass production.json  de GuiGui  ->  modelo Panel.

Por que existe este modulo
--------------------------
GuiGui exporta .ban INCOMPLETOS (solo agujeros laterales; faltan los verticales
y las ranuras — ver CONTEXTO.md seccion 6). Pero el JSON de produccion contiene
TODA la geometria. Este modulo la lee y la normaliza.

Transformacion de coordenadas (derivada y verificada contra los archivos de
referencia de Bluen, mueble de muestra 试生产样品柜):

  El JSON usa un sistema Y-ABAJO (rect trae top=0 / bottom=height) y guarda la
  pieza en la orientacion de diseno. El .ban usa Y-ARRIBA y guarda la pieza
  siempre en formato "retrato" (lado largo sobre Y).

  Si oRect.width <= oRect.height  ->  solo se invierte Y:
        X_ban = x
        Y_ban = H - y
  Si oRect.width >  oRect.height  ->  ademas se rota 90 grados:
        X_ban = H - y
        Y_ban = W - x
        (y el ancho/alto del panel se intercambian)

  Ambas transformaciones tienen determinante -1 respecto de los numeros crudos
  del JSON, lo cual es correcto: el JSON es Y-abajo, asi que el resultado neto
  es una rotacion propia, NO un espejado.

Coordenadas usadas: `ocenter` / `opt1` / `opt2` / `realCurve`, que estan en el
sistema de la pieza TERMINADA (oRect). Los campos `center` / `pt1` / `pt2` estan
en el sistema de la placa nesteada y no sirven para el archivo de pieza.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional, Tuple

from panel import (EDGE_DOWN, EDGE_LEFT, EDGE_RIGHT, EDGE_UP, FACE_BACK,
                   FACE_FRONT, Hole, Panel, SideHole, Slot, Vertex,
                   polygon_area)

EDGE_TOL = 0.5   # mm de tolerancia para decidir sobre que canto cae un agujero


# --- helpers ------------------------------------------------------------------

def _f(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _parse_edge_info(s: str) -> Dict[str, float]:
    """'←1↓0.5→1↑0'  ->  {'left':1, 'down':0.5, 'right':1, 'up':0} (marco Y-abajo)."""
    out = {"left": 0.0, "down": 0.0, "right": 0.0, "up": 0.0}
    if not s:
        return out
    keys = {"←": "left", "↓": "down", "→": "right", "↑": "up"}
    for sym, name in keys.items():
        m = re.search(re.escape(sym) + r"\s*(-?\d+(?:\.\d+)?)", s)
        if m:
            out[name] = float(m.group(1))
    return out


def needs_rotation(width: float, height: float) -> bool:
    """El .ban orienta siempre la pieza en retrato (lado largo sobre Y)."""
    return width > height


class _Transform:
    """Transforma del marco del JSON (Y-abajo, W x H) al marco .ban (Y-arriba)."""

    def __init__(self, width: float, height: float, rotate: Optional[bool] = None):
        self.src_w = width
        self.src_h = height
        self.rotate = needs_rotation(width, height) if rotate is None else rotate
        self.width = height if self.rotate else width     # ancho del panel en el .ban
        self.height = width if self.rotate else height    # alto  del panel en el .ban

    def pt(self, x: float, y: float) -> Tuple[float, float]:
        if self.rotate:
            return (self.src_h - y, self.src_w - x)
        return (x, self.src_h - y)

    def edge(self, name: str) -> str:
        """Canto del marco JSON (left/right/up/down, Y-abajo) -> canto .ban."""
        if self.rotate:
            return {"left": EDGE_UP, "right": EDGE_DOWN,
                    "down": EDGE_RIGHT, "up": EDGE_LEFT}[name]
        return {"left": EDGE_LEFT, "right": EDGE_RIGHT,
                "down": EDGE_UP, "up": EDGE_DOWN}[name]


# --- lectura ------------------------------------------------------------------

def load_layout(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        doc = json.load(fh)
    lr = doc.get("layoutResult")
    if isinstance(lr, str):          # viene como string: hay que parsear dos veces
        lr = json.loads(lr)
    doc["_plates"] = lr or []
    return doc


def panels_from_layout(doc: Dict[str, Any], rotate_edges: bool = True) -> List[Panel]:
    out: List[Panel] = []
    for plate in doc.get("_plates", []):
        for raw in plate.get("parts", []):
            out.append(panel_from_part(raw, plate, rotate_edges=rotate_edges))
    return out


def panel_from_part(raw: Dict[str, Any], plate: Optional[Dict[str, Any]] = None,
                    rotate_edges: bool = True) -> Panel:
    orect = raw.get("oRect") or {}
    w = _f(orect.get("width"))
    h = _f(orect.get("height"))
    if not w or not h:
        fs = raw.get("fullSize") or {}
        w, h = _f(fs.get("width"), w), _f(fs.get("height"), h)

    t = _Transform(w, h)
    thickness = _f(raw.get("thick"), _f((plate or {}).get("thick"), 18.0))
    edges = _parse_edge_info(raw.get("edgeInfo", ""))

    # Cantos: del marco JSON al marco .ban (F = y0, B = yH, L = x0, R = xW).
    #
    # rotate_edges=True  -> los cantos siguen la rotacion de la pieza (geometricamente
    #                       correcto; validado contra la lista de corte de GuiGui en las
    #                       8 piezas NO rotadas de PRUEBA 1).
    # rotate_edges=False -> replica lo que hace GuiGui: rota las medidas pero NO rota los
    #                       flags de canto. Las 2 piezas rotadas de PRUEBA 1 salen asi.
    #
    # Para piezas no rotadas las dos opciones dan el mismo resultado.
    edge_t = t if rotate_edges else _Transform(w, h, rotate=False)
    ban_edges = {edge_t.edge(k): v for k, v in edges.items()}

    p = Panel(
        code=str(raw.get("plankNum") or raw.get("oriPlankNum") or "").strip(),
        name=raw.get("partName") or raw.get("name") or "",
        width=t.width,
        height=t.height,
        thickness=thickness,
        material=raw.get("matCode") or (plate or {}).get("matCode") or "",
        grain="2",
        quantity=1,
        edge_front=ban_edges.get(EDGE_DOWN, 0.0),
        edge_back=ban_edges.get(EDGE_UP, 0.0),
        edge_left=ban_edges.get(EDGE_LEFT, 0.0),
        edge_right=ban_edges.get(EDGE_RIGHT, 0.0),
        src_width=w,
        src_height=h,
        rotated=t.rotate,
        src_edge_left=edges["left"],
        src_edge_down=edges["down"],
        src_edge_right=edges["right"],
        src_edge_up=edges["up"],
        order_no=str(raw.get("orderNo") or ""),
        room=raw.get("roomName") or "",
        location=raw.get("loc") or "",
        short_name=raw.get("name") or "",
        texture=raw.get("texture") or (plate or {}).get("texture") or "",
        customer=raw.get("customer_name") or "",
        address=raw.get("address") or "",
        plank_id=str(raw.get("plankID") or ""),
        source="guigui-json",
    )

    p.outline = _outline(raw, t)
    p.holes = _holes(raw, t)
    p.side_holes = _side_holes(raw, t, thickness)
    p.slots = _slots(raw, t)
    return p


def _outline(raw: Dict[str, Any], t: _Transform) -> List[Vertex]:
    curve = raw.get("realCurve") or []
    if len(curve) < 3:
        return []
    verts: List[Vertex] = []
    for pt in curve:
        x, y = t.pt(_f(pt.get("x")), _f(pt.get("y")))
        # el bulge `b` viaja con el vertice; la transformacion invierte el sentido
        verts.append(Vertex(x, y, -_f(pt.get("b"))))

    if polygon_area([(v.x, v.y) for v in verts]) < 0:
        verts = _reverse_ring(verts)

    # arrancar por el vertice mas cercano al origen, como hace GuiGui
    k = min(range(len(verts)), key=lambda i: (round(verts[i].x, 3), round(verts[i].y, 3)))
    return verts[k:] + verts[:k]


def _reverse_ring(verts: List[Vertex]) -> List[Vertex]:
    """Invierte el sentido del anillo moviendo cada arco a su nuevo borde entrante."""
    n = len(verts)
    rev = []
    for i in range(n - 1, -1, -1):
        nxt = verts[(i + 1) % n]
        rev.append(Vertex(verts[i].x, verts[i].y, -nxt.arc))
    return rev


def _holes(raw: Dict[str, Any], t: _Transform) -> List[Hole]:
    out = []
    for h in (raw.get("oriHoles") or raw.get("holes") or []):
        c = h.get("ocenter") or h.get("center") or {}
        x, y = t.pt(_f(c.get("x")), _f(c.get("y")))
        out.append(Hole(x=x, y=y, diameter=_f(h.get("diameter")), depth=_f(h.get("deep")),
                        face=FACE_BACK if _f(h.get("side"), 1) < 0 else FACE_FRONT,
                        symbol=h.get("symbol") or "", uid=h.get("uniqueId")))
    return out


_SIDE_CODE = {"1": "left", "2": "up", "3": "right", "4": "down"}   # marco JSON, Y-abajo


def _side_holes(raw: Dict[str, Any], t: _Transform, thickness: float) -> List[SideHole]:
    out = []
    for h in (raw.get("oriSholes") or raw.get("sholes") or []):
        c = h.get("ocenter") or {}
        ox, oy = _f(c.get("x")), _f(c.get("y"))
        name = _edge_name(ox, oy, t.src_w, t.src_h)
        if name is None:
            name = _SIDE_CODE.get(str(h.get("side")).strip())
        if name is None:
            continue
        edge = t.edge(name)
        x, y = t.pt(ox, oy)
        # el z (altura dentro del espesor) vive en center['y']; por defecto, media placa
        z = _f((h.get("center") or {}).get("y"), thickness / 2.0)
        out.append(SideHole(x=x, y=y, z=z, diameter=_f(h.get("diameter")),
                            depth=_f(h.get("deep")), edge=edge,
                            symbol=h.get("symbol") or "", uid=h.get("uniqueId")))
    return out


def _edge_name(x: float, y: float, w: float, h: float) -> Optional[str]:
    if abs(x) <= EDGE_TOL:
        return "left"
    if abs(x - w) <= EDGE_TOL:
        return "right"
    if abs(y) <= EDGE_TOL:
        return "down"
    if abs(y - h) <= EDGE_TOL:
        return "up"
    return None


def _slots(raw: Dict[str, Any], t: _Transform) -> List[Slot]:
    out = []
    for s in (raw.get("oriSlots") or raw.get("slots") or []):
        a = s.get("opt1") or s.get("pt1") or {}
        b = s.get("opt2") or s.get("pt2") or {}
        x1, y1 = t.pt(_f(a.get("x")), _f(a.get("y")))
        x2, y2 = t.pt(_f(b.get("x")), _f(b.get("y")))
        out.append(Slot(x1=x1, y1=y1, x2=x2, y2=y2, width=_f(s.get("width")),
                        depth=_f(s.get("deep")),
                        face=FACE_BACK if _f(s.get("side"), 1) < 0 else FACE_FRONT,
                        symbol=s.get("symbol") or ""))
    # ranuras de canto (sslots): todavia sin muestra de referencia
    for s in (raw.get("oriSslots") or raw.get("sslots") or []):
        a = s.get("opt1") or s.get("pt1") or {}
        b = s.get("opt2") or s.get("pt2") or {}
        x1, y1 = t.pt(_f(a.get("x")), _f(a.get("y")))
        x2, y2 = t.pt(_f(b.get("x")), _f(b.get("y")))
        out.append(Slot(x1=x1, y1=y1, x2=x2, y2=y2, width=_f(s.get("width")),
                        depth=_f(s.get("deep")), face=FACE_FRONT,
                        symbol=s.get("symbol") or "sslot"))
    return out
