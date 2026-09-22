"""
Escritor  Panel -> WoodWOP / Homag (.mpr)

Un archivo por pieza. Las piezas con mecanizado en la CARA TRASERA generan
ademas un segundo archivo con sufijo `K`.

Convenciones verificadas contra los archivos de referencia de Bluen:
  - Codificacion GBK, saltos de linea CRLF, sin salto final despues de `!`.
  - `<100 WerkStck>` lleva el rectangulo envolvente; los contornos irregulares
    NO se representan (el .mpr de referencia de la pieza con arco no trae contorno).
  - Solo van las operaciones de CARA A. La cara B va en el archivo `K`,
    con la X ESPEJADA (X' = LA - X) y la profundidad real desde esa cara.
  - `BM` del taladro horizontal:  XP = x0 (izq) · XM = xLA (der) · YP = y0 (abajo) · YM = yBR (arriba)
"""

from __future__ import annotations

from typing import List, Optional

from panel import (EDGE_DOWN, EDGE_LEFT, EDGE_RIGHT, EDGE_UP, FACE_BACK,
                   FACE_FRONT, Panel)

NL = "\r\n"
ENCODING = "gbk"

BM_EDGE = {EDGE_LEFT: "XP", EDGE_RIGHT: "XM", EDGE_DOWN: "YP", EDGE_UP: "YM"}

_DRILL_TAIL = [
    ('AN', '1'), ('MI', '0'), ('S_', '2'), ('AB', '32'), ('WI', '0'),
    ('HP', '0'), ('SP', '0'), ('YVE', '0'),
    ('WW', '60,61,62,88,90,91,92,150'), ('ASG', '2'),
    ('KAT', 'Bohren vertikal'), ('MNM', 'Vertical drilling'),
    ('MX', '0'), ('MY', '0'), ('MZ', '0'), ('MXF', '1'), ('MYF', '1'), ('MZF', '1'),
]

_BORING_TAIL = [
    ('AN', '1'), ('AB', '32'), ('HP', '0'), ('SP', '0'), ('YVE', '0'),
    ('WW', '50,51,52,53,93,94,95,56,153,151'), ('ASG', '2'),
    ('KAT', 'Horizontalbohren'), ('MNM', 'Horizontal drilling'),
    ('MX', '0'), ('MY', '0'), ('MZ', '0'), ('MXF', '1'), ('MYF', '1'), ('MZF', '1'),
]

_NUT_TAIL = [
    ('RK', 'NoWRK'), ('EM', 'MOD1'), ('AD', '0'), ('TV', '0'), ('MV', 'GL'),
]
_NUT_TAIL2 = [
    ('XY', '100'), ('MN', 'GL'), ('OP', '0'), ('AN', '0'), ('HP', '0'),
    ('SP', '0'), ('YVE', '0'), ('WW', '40,41,42,45,141,142,144,145'), ('ASG', '2'),
    ('KAT', 'Nuten'), ('MNM', 'Grooving'),
    ('MX', '0'), ('MY', '0'), ('MZ', '0'), ('MXF', '1'), ('MYF', '1'), ('MZF', '1'),
]


def _n(v: float) -> str:
    """Formato numerico del .mpr: hasta 2 decimales, sin ceros sobrantes."""
    s = f"{round(float(v) + 0.0, 2):.2f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


def _kv(pairs) -> List[str]:
    return [f'{k}="{v}"' for k, v in pairs]


def _header(p: Panel) -> List[str]:
    return [
        f'[H\\Left:{_n(p.edge_left)};Bottom:{_n(p.edge_front)};'
        f'Right:{_n(p.edge_right)};Top:{_n(p.edge_back)}',
        'VERSION="4.0 Alpha"', 'VIEW="NOMIRROR"', 'OP="1"', 'FM="1"', 'FW="800"',
        'HP="1"', 'UP="0"', 'GX="1"', 'DW="0"', 'ModusMirror="1"', '',
        '<100 \\WerkStck\\',
        f'LA="{_n(p.width)}"', f'BR="{_n(p.height)}"', f'DI="{_n(p.thickness)}"',
        'FNX="0"', 'FNY="0"', 'RNX="0"', 'RNY="0"', 'RNZ="0"', 'AX="0"', 'AY="0"', '',
    ]


def _v_drilling(x: float, y: float, depth: float, diameter: float) -> List[str]:
    return (['<102 \\V_DRILLING\\', f'XA="{_n(x)}"', f'YA="{_n(y)}"', 'BM="LS"',
             f'TI="{_n(depth)}"', f'DU="{_n(diameter)}"'] + _kv(_DRILL_TAIL) + [''])


def _end_boring(p: Panel, s) -> List[str]:
    return (['<103 \\End_Boring\\', 'MI="0"', f'XA="{_n(s.x)}"', f'YA="{_n(s.y)}"',
             f'ZA="{_n(s.z)}"', f'DU="{_n(s.diameter)}"', f'TI="{_n(s.depth)}"',
             'ANA="20"', f'BM="{BM_EDGE[s.edge]}"'] + _kv(_BORING_TAIL) + [''])


def _nuten(x1, y1, x2, y2, width, depth) -> List[str]:
    return (['<109 \\Nuten\\', f'XA="{_n(x1)}"', f'YA="{_n(y1)}"', 'WI="0"',
             f'XE="{_n(x2)}"', f'YE="{_n(y2)}"', f'NB="{_n(width)}"']
            + _kv(_NUT_TAIL) + [f'TI="{_n(depth)}"'] + _kv(_NUT_TAIL2) + [''])


def _body(p: Panel, back: bool) -> List[str]:
    """Operaciones de una cara. back=True espeja la X (segunda sujecion)."""
    mx = (lambda v: p.width - v) if back else (lambda v: v)
    face = FACE_BACK if back else FACE_FRONT
    out: List[str] = []
    for h in p.holes:
        if h.face == face:
            out += _v_drilling(mx(h.x), h.y, h.depth, h.diameter)
    if not back:
        for s in p.side_holes:
            out += _end_boring(p, s)
    for sl in p.slots:
        if sl.face == face:
            out += _nuten(mx(sl.x1), sl.y1, mx(sl.x2), sl.y2, sl.width, sl.depth)
    return out


def has_ops(p: Panel) -> bool:
    """GuiGui no emite .mpr para piezas sin ningun mecanizado (los fondos de 5 mm)."""
    return bool(p.holes or p.side_holes or p.slots)


def has_back_ops(p: Panel) -> bool:
    return any(h.face == FACE_BACK for h in p.holes) or \
           any(s.face == FACE_BACK for s in p.slots)


def panel_to_mpr(p: Panel, back: bool = False) -> str:
    lines = _header(p) + _body(p, back)
    lines += ['<101 \\Kommentar\\', f'KM="{p.name}"', '!']
    return NL.join(lines)


def write_mpr(p: Panel, path: str, back: bool = False) -> None:
    text = panel_to_mpr(p, back=back)
    with open(path, "wb") as fh:
        fh.write(text.encode(ENCODING, errors="replace"))
