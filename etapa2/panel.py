"""
Modelo interno de pieza — el "esquema propio" de la Etapa 2.

Todo lo que entra al sistema (hoy: el JSON de GuiGui; mañana: Inventor/Fusion)
se convierte a este modelo. Todo lo que sale (.ban, .mpr, .xml, .xls) se genera
desde este modelo. El modelo es la unica fuente de verdad.

CONVENCIONES DEL MODELO (identicas a las del .ban, ver CONTEXTO.md seccion 3):
  - Origen en la esquina inferior izquierda, vista desde la cara frontal (A).
  - X a lo ancho (width), Y a lo largo (height).  Y CRECE HACIA ARRIBA.
  - Z = 0 en la superficie de la cara A; Z negativo hacia adentro.
  - Contorno en sentido antihorario, cerrando en el punto inicial.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

# --- caras y cantos -----------------------------------------------------------

FACE_FRONT = "A"   # cara frontal (正面)
FACE_BACK = "B"    # cara trasera (反面)

EDGE_UP = "U"      # canto superior   y = height
EDGE_DOWN = "D"    # canto inferior   y = 0
EDGE_LEFT = "L"    # canto izquierdo  x = 0
EDGE_RIGHT = "R"   # canto derecho    x = width


@dataclass
class Hole:
    """Agujero perpendicular a la cara (vertical en la maquina)."""
    x: float
    y: float
    diameter: float
    depth: float
    face: str = FACE_FRONT
    symbol: str = ""          # 3in1Lock, HINGE, HINGESCREW, jlHoleEX...
    uid: Optional[int] = None


@dataclass
class SideHole:
    """Agujero horizontal, entrando por un canto."""
    x: float                  # posicion del centro sobre la cara
    y: float
    z: float                  # altura dentro del espesor (positiva, p.ej. 9 en placa de 18)
    diameter: float
    depth: float
    edge: str                 # U / D / L / R
    symbol: str = ""
    uid: Optional[int] = None

    def start_end(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Punto sobre el canto y punto al fondo del agujero."""
        if self.edge == EDGE_UP:
            return (self.x, self.y), (self.x, self.y - self.depth)
        if self.edge == EDGE_DOWN:
            return (self.x, self.y), (self.x, self.y + self.depth)
        if self.edge == EDGE_RIGHT:
            return (self.x, self.y), (self.x - self.depth, self.y)
        if self.edge == EDGE_LEFT:
            return (self.x, self.y), (self.x + self.depth, self.y)
        raise ValueError(f"canto desconocido: {self.edge!r}")


@dataclass
class Slot:
    """Ranura recta de ancho constante, mecanizada desde una cara."""
    x1: float
    y1: float
    x2: float
    y2: float
    width: float
    depth: float
    face: str = FACE_FRONT
    symbol: str = ""          # BP (fondo), lightSlot...

    @property
    def length(self) -> float:
        return math.hypot(self.x2 - self.x1, self.y2 - self.y1)


@dataclass
class Vertex:
    """Vertice del contorno. `arc` = angulo incluido en grados del arco que
    LLEGA a este vertice desde el anterior (positivo = antihorario). 0 = recta."""
    x: float
    y: float
    arc: float = 0.0


@dataclass
class Panel:
    code: str                          # codigo de barras — es el nombre del archivo
    name: str = ""
    width: float = 0.0                 # X
    height: float = 0.0                # Y
    thickness: float = 18.0
    material: str = ""
    grain: str = "2"                   # 2 = veta vertical
    quantity: int = 1
    # cantos pegados, en el orden del atributo EdgeFBLR del .ban
    edge_front: float = 0.0            # canto y = 0
    edge_back: float = 0.0             # canto y = height
    edge_left: float = 0.0             # canto x = 0
    edge_right: float = 0.0            # canto x = width
    outline: List[Vertex] = field(default_factory=list)   # antihorario, sin repetir el cierre
    holes: List[Hole] = field(default_factory=list)
    side_holes: List[SideHole] = field(default_factory=list)
    slots: List[Slot] = field(default_factory=list)
    # Ranuras de CANTO (canal en el borde, no en la cara). El formato de maquina
    # todavia se desconoce: no hay ni una en los 82 archivos de referencia de
    # Bluen. Se llevan hasta aca para poder AVISAR, no para escribirlas.
    edge_slots: List[dict] = field(default_factory=list)
    # medidas en el marco ORIGINAL del diseno (antes de rotar a retrato).
    # La lista de corte de la sierra usa estas, no las del archivo de maquina.
    src_width: float = 0.0
    src_height: float = 0.0
    rotated: bool = False
    # cantos en el marco original: izquierda / abajo / derecha / arriba
    src_edge_left: float = 0.0
    src_edge_down: float = 0.0
    src_edge_right: float = 0.0
    src_edge_up: float = 0.0
    # trazabilidad
    order_no: str = ""
    room: str = ""
    location: str = ""
    short_name: str = ""
    texture: str = ""
    customer: str = ""
    address: str = ""
    plank_id: str = ""
    grain_text: str = ""               # vacio = se deduce de grain
    source: str = ""

    def veta(self) -> str:
        """Texto de veta para la lista de corte.

        竖纹 = la veta corre a lo largo de Y (largo);  横纹 = a lo largo de X.
        Si grain_text vino cargado desde el origen, ese gana.
        """
        if self.grain_text:
            return self.grain_text
        return "\u6a2a\u7eb9" if str(self.grain) == "1" else "\u7ad6\u7eb9"

    def rect_outline(self) -> List[Vertex]:
        return [Vertex(0.0, 0.0), Vertex(self.width, 0.0),
                Vertex(self.width, self.height), Vertex(0.0, self.height)]

    def ensure_outline(self) -> List[Vertex]:
        return self.outline or self.rect_outline()


# --- utilidades de geometria --------------------------------------------------

def polygon_area(points: Sequence[Tuple[float, float]]) -> float:
    """Area con signo. Positiva = antihorario."""
    a = 0.0
    n = len(points)
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        a += x1 * y2 - x2 * y1
    return a / 2.0


def arc_points(p0: Tuple[float, float], p1: Tuple[float, float],
               included_deg: float, step_mm: float = 1.12) -> List[Tuple[float, float]]:
    """Linealiza un arco que va de p0 a p1 con el angulo incluido dado.

    Devuelve los puntos INTERMEDIOS (sin p0 ni p1). Positivo = antihorario.
    GuiGui emite pasos de ~1.12 mm; el default replica ese aspecto.
    """
    theta = math.radians(included_deg)
    if abs(theta) < 1e-9:
        return []
    x0, y0 = p0
    x1, y1 = p1
    chord = math.hypot(x1 - x0, y1 - y0)
    if chord < 1e-9:
        return []
    radius = chord / (2.0 * math.sin(abs(theta) / 2.0))
    # distancia del centro al punto medio de la cuerda
    h = math.sqrt(max(radius * radius - (chord / 2.0) ** 2, 0.0))
    mx, my = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    # normal unitaria a la cuerda
    nx, ny = -(y1 - y0) / chord, (x1 - x0) / chord
    # el centro queda del lado que corresponde al sentido y a si el arco es mayor a 180
    sign = 1.0 if theta > 0 else -1.0
    if abs(included_deg) > 180.0:
        sign = -sign
    cx, cy = mx + sign * h * nx, my + sign * h * ny
    a0 = math.atan2(y0 - cy, x0 - cx)
    n = max(int(math.ceil(abs(theta) * radius / step_mm)), 2)
    out = []
    for i in range(1, n):
        a = a0 + theta * (i / n)
        out.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
    return out


def flatten_outline(vertices: Sequence[Vertex], step_mm: float = 1.12,
                    close: bool = True) -> List[Tuple[float, float]]:
    """Convierte el contorno (con arcos) en una polilinea de puntos."""
    pts: List[Tuple[float, float]] = []
    n = len(vertices)
    for i, v in enumerate(vertices):
        prev = vertices[i - 1]
        if i > 0 and abs(v.arc) > 1e-9:
            pts.extend(arc_points((prev.x, prev.y), (v.x, v.y), v.arc, step_mm))
        pts.append((v.x, v.y))
    if close and n:
        first = vertices[0]
        if abs(first.arc) > 1e-9:
            last = vertices[-1]
            pts.extend(arc_points((last.x, last.y), (first.x, first.y), first.arc, step_mm))
        pts.append((first.x, first.y))
    return pts
