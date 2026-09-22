"""
hojas — hojas de verificacion imprimibles, una por pieza.

Dibuja cada pieza acotada a partir del modelo Panel, para:
  · comparar contra el dibujo que muestra HHcnc antes de mecanizar
  · medir con calibre despues

    python3 hojas.py "<ORDEN>-Mass production.json" -o hojas.html

Salida: un HTML autocontenido, una pieza por hoja al imprimir.
"""

from __future__ import annotations

import argparse
import html
import os
import sys
from typing import Dict, List, Tuple

from cargar import cargar
from panel import (EDGE_DOWN, EDGE_LEFT, EDGE_RIGHT, EDGE_UP, FACE_BACK,
                   Panel, flatten_outline)

W_PX = 600.0          # ancho util del dibujo
MARGIN = 84.0         # margen para las cotas


def _g(v: float) -> str:
    return f"{v:g}" if abs(v - round(v)) > 1e-9 else str(int(round(v)))


def _svg(p: Panel, back: bool = False) -> str:
    """Vista de una cara. back=True dibuja la cara B (espejada en X, como se ve dada vuelta)."""
    import math

    sc = min(W_PX / p.width, 460.0 / p.height)
    w, h = p.width * sc, p.height * sc
    W, H = w + 2 * MARGIN, h + 2 * MARGIN

    def X(v: float) -> float:
        return MARGIN + (p.width - v if back else v) * sc

    def Y(v: float) -> float:
        return MARGIN + (p.height - v) * sc      # SVG tiene la Y al reves

    o: List[str] = [f'<svg viewBox="0 0 {W:.1f} {H:.1f}" class="pz">']
    o.append('<rect x="0" y="0" width="%.1f" height="%.1f" fill="var(--paper)"/>' % (W, H))

    # --- colocacion de etiquetas sin superposicion -------------------------
    cajas: List[Tuple[float, float, float, float]] = []

    def libre(x0, y0, x1, y1) -> bool:
        return all(x1 < b[0] or x0 > b[2] or y1 < b[1] or y0 > b[3] for b in cajas)

    def etiqueta(cx: float, cy: float, txt: str, cls: str, r: float = 0.0) -> None:
        """Coloca el texto en el primer hueco libre alrededor del punto."""
        an, al = len(txt) * 4.5, 10.0
        for dx, dy in ((0, -r - 4), (0, r + 10), (an / 2 + r + 5, 3), (-an / 2 - r - 5, 3),
                       (0, -r - 15), (0, r + 21), (an / 2 + r + 5, -8), (-an / 2 - r - 5, -8)):
            x, y = cx + dx, cy + dy
            x0, y0, x1, y1 = x - an / 2, y - al + 2, x + an / 2, y + 2
            if libre(x0, y0, x1, y1):
                cajas.append((x0, y0, x1, y1))
                o.append(f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}">{txt}</text>')
                return

    pts = flatten_outline(p.ensure_outline(), step_mm=1.5, close=True)
    d = " ".join(f'{"M" if i == 0 else "L"}{X(x):.2f},{Y(y):.2f}' for i, (x, y) in enumerate(pts))
    o.append(f'<path d="{d}" fill="var(--panel)" stroke="var(--ink)" stroke-width="1.4"/>')

    face = FACE_BACK if back else "A"
    xs: Dict[float, None] = {}
    ys: Dict[float, None] = {}

    for sl in p.slots:
        if sl.face != face:
            continue
        ang = math.atan2(sl.y2 - sl.y1, sl.x2 - sl.x1)
        nx, ny = -math.sin(ang) * sl.width / 2, math.cos(ang) * sl.width / 2
        c = [(sl.x1 + nx, sl.y1 + ny), (sl.x2 + nx, sl.y2 + ny),
             (sl.x2 - nx, sl.y2 - ny), (sl.x1 - nx, sl.y1 - ny)]
        pd = " ".join(f'{"M" if i == 0 else "L"}{X(x):.2f},{Y(y):.2f}'
                      for i, (x, y) in enumerate(c)) + " Z"
        o.append(f'<path d="{pd}" fill="var(--slot)" stroke="var(--slotline)" stroke-width="1"/>')
        for v in (sl.x1, sl.x2):
            xs[round(v, 2)] = None
        for v in (sl.y1, sl.y2):
            ys[round(v, 2)] = None

    for hl in p.holes:
        if hl.face != face:
            continue
        r = max(hl.diameter * sc / 2, 2.2)
        o.append(f'<circle cx="{X(hl.x):.2f}" cy="{Y(hl.y):.2f}" r="{r:.2f}" '
                 f'fill="var(--hole)" stroke="var(--ink)" stroke-width="1"/>')
        xs[round(hl.x, 2)] = None
        ys[round(hl.y, 2)] = None

    if not back:
        for s in p.side_holes:
            (sx, sy), (ex, ey) = s.start_end()
            o.append(f'<line x1="{X(sx):.2f}" y1="{Y(sy):.2f}" x2="{X(ex):.2f}" '
                     f'y2="{Y(ey):.2f}" stroke="var(--side)" stroke-width="3" '
                     f'stroke-linecap="round"/>')
            if s.edge in (EDGE_LEFT, EDGE_RIGHT):
                ys[round(sy, 2)] = None
            else:
                xs[round(sx, 2)] = None

    # etiquetas de las operaciones, despues de dibujarlas todas
    for sl in p.slots:
        if sl.face == face:
            etiqueta(X((sl.x1 + sl.x2) / 2), Y((sl.y1 + sl.y2) / 2),
                     f'{_g(sl.width)}&#215;{_g(sl.depth)}', 'lbl', 4)
    for hl in p.holes:
        if hl.face == face:
            etiqueta(X(hl.x), Y(hl.y), f'&#216;{_g(hl.diameter)}&#8239;·&#8239;{_g(hl.depth)}',
                     'lbl', max(hl.diameter * sc / 2, 2.2))
    if not back:
        # el rotulo va cerca de la BOCA del agujero, no del centro: a media
        # profundidad se solapa con la excentrica Ø15 del mismo tres-en-uno
        for s in p.side_holes:
            (sx, sy), (ex, ey) = s.start_end()
            ax, ay = sx + (ex - sx) * 0.22, sy + (ey - sy) * 0.22
            etiqueta(X(ax), Y(ay), f'&#216;{_g(s.diameter)}&#8239;·&#8239;{_g(s.depth)}',
                     'lbl side', 3)

    # --- cotas, escalonadas para que no se pisen ---------------------------
    fil: List[float] = []
    for v in sorted(xs):
        an = len(_g(v)) * 6.0
        px = X(v)
        k = 0
        while k < len(fil) and abs(px - fil[k]) < an:
            k += 1
        if k == len(fil):
            fil.append(px)
        else:
            fil[k] = px
        y0 = MARGIN + h
        y1 = y0 + 8 + k * 13
        o.append(f'<line x1="{px:.2f}" y1="{y0:.1f}" x2="{px:.2f}" y2="{y1:.1f}" class="cot"/>')
        o.append(f'<text x="{px:.1f}" y="{y1 + 10:.1f}" class="cota">{_g(v)}</text>')
    filx = len(fil)

    fil = []
    for v in sorted(ys):
        py = Y(v)
        k = 0
        while k < len(fil) and abs(py - fil[k]) < 12:
            k += 1
        if k == len(fil):
            fil.append(py)
        else:
            fil[k] = py
        x0 = MARGIN
        x1 = x0 - 8 - k * 30
        o.append(f'<line x1="{x0:.1f}" y1="{py:.2f}" x2="{x1:.1f}" y2="{py:.2f}" class="cot"/>')
        o.append(f'<text x="{x1 - 3:.1f}" y="{py + 3.5:.1f}" class="cota ar">{_g(v)}</text>')

    yb = MARGIN + h + 8 + filx * 13 + 24
    o.append(f'<text x="{MARGIN + w / 2:.1f}" y="{yb:.1f}" class="med">{_g(p.width)} mm</text>')
    o.append(f'<text x="{MARGIN - 46:.1f}" y="{MARGIN + h / 2:.1f}" class="med" '
             f'transform="rotate(-90 {MARGIN - 46:.1f} {MARGIN + h / 2:.1f})">'
             f'{_g(p.height)} mm</text>')
    o.append(f'<text x="{MARGIN + 6:.1f}" y="{MARGIN - 12:.1f}" class="cara">'
             f'{"CARA B (pieza dada vuelta)" if back else "CARA A (frontal)"}</text>')
    o.append("</svg>")
    return "".join(o)


def _tools(panels: List[Panel]) -> List[Tuple[str, float, float, int]]:
    acc: Dict[Tuple[str, float, float], int] = {}
    for p in panels:
        for h in p.holes:
            acc[("Vertical", h.diameter, h.depth)] = acc.get(("Vertical", h.diameter, h.depth), 0) + 1
        for s in p.side_holes:
            acc[("Horizontal", s.diameter, s.depth)] = acc.get(("Horizontal", s.diameter, s.depth), 0) + 1
        for sl in p.slots:
            acc[("Fresa", sl.width, sl.depth)] = acc.get(("Fresa", sl.width, sl.depth), 0) + 1
    return [(k[0], k[1], k[2], v) for k, v in sorted(acc.items())]


CSS = """
:root{--paper:#fff;--ink:#1c1b19;--muted:#6b6862;--rule:#d9d5cc;--panel:#f4f1ea;
--hole:#c8d9e8;--slot:#e6dcc8;--slotline:#a08d63;--side:#b5543f;--accent:#7a3c2c}
@media screen and (prefers-color-scheme:dark){:root:not([data-theme=light]){
--paper:#12110f;--ink:#eceae5;--muted:#9a958c;--rule:#33312c;--panel:#1e1c19;
--hole:#2c455c;--slot:#3a3226;--slotline:#a08d63;--side:#d4735c;--accent:#e0a18c}}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);
font:14px/1.5 ui-sans-serif,-apple-system,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:760px;margin:0 auto;padding:24px 16px 60px}
h1{font-size:22px;margin:0 0 2px}
.sub{color:var(--muted);font-size:13px;margin-bottom:22px}
.hoja{border-top:2px solid var(--ink);padding-top:14px;margin-top:34px}
.hoja:first-of-type{margin-top:18px}
.cod{font:600 19px ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.02em}
.nom{color:var(--muted);font-size:13px;margin:2px 0 4px}
.dim{font-size:13px;margin-bottom:10px}
.dim b{font-weight:600}
svg.pz{width:100%;height:auto;display:block;margin:6px 0 4px;
border:1px solid var(--rule);border-radius:6px;background:var(--paper)}
text{font:10px ui-sans-serif,sans-serif;fill:var(--ink);text-anchor:middle}
.lbl{font-size:9.5px;fill:var(--muted)}
.lbl.side{fill:var(--side)}
.cota{font-size:10px;fill:var(--accent);font-weight:600}
.cota.ar{text-anchor:end}
.med{font-size:11px;fill:var(--muted)}
.cara{font-size:10px;fill:var(--muted);text-anchor:start;letter-spacing:.06em}
.cot{stroke:var(--accent);stroke-width:1}
table{border-collapse:collapse;width:100%;font-size:13px;margin:8px 0 26px}
th,td{text-align:left;padding:5px 8px;border-bottom:1px solid var(--rule)}
th{font-weight:600;color:var(--muted);font-size:12px}
td.n{text-align:right;font-variant-numeric:tabular-nums}
.nota{background:var(--panel);border-left:3px solid var(--accent);
padding:10px 14px;border-radius:0 6px 6px 0;font-size:13px;margin:16px 0}
@media print{.hoja{page-break-before:always;border-top:none}
.hoja:first-of-type{page-break-before:avoid}.wrap{max-width:none;padding:0}
:root{--paper:#fff;--ink:#000;--muted:#555;--rule:#bbb;--panel:#f2f2f2}}
"""


def build(panels: List[Panel], titulo: str) -> str:
    o: List[str] = ['<!doctype html><html lang="es"><meta charset="utf-8">',
                    '<meta name="viewport" content="width=device-width,initial-scale=1">',
                    f"<title>Hojas de verificacion</title><style>{CSS}</style>",
                    '<div class="wrap">',
                    f"<h1>Hojas de verificación — {html.escape(titulo)}</h1>",
                    f'<div class="sub">{len(panels)} piezas · cotas en mm desde el borde · '
                    'medir con calibre contra estos valores</div>']

    o.append("<h2 style='font-size:15px;margin:0 0 6px'>Herramientas necesarias</h2>")
    o.append("<table><tr><th>Tipo</th><th>Ø / ancho</th><th>Profundidad</th>"
             "<th style='text-align:right'>Cantidad</th></tr>")
    for tipo, dia, prof, n in _tools(panels):
        o.append(f"<tr><td>{tipo}</td><td>{_g(dia)} mm</td><td>{_g(prof)} mm</td>"
                 f"<td class='n'>{n}</td></tr>")
    o.append("</table>")
    o.append('<div class="nota"><b>Antes de mecanizar:</b> cargar el programa y comparar '
             'el dibujo de la pantalla contra esta hoja. Si no coincide, parar.</div>')

    for p in panels:
        back = any(h.face == FACE_BACK for h in p.holes) or \
               any(s.face == FACE_BACK for s in p.slots)
        o.append('<div class="hoja">')
        o.append(f'<div class="cod">{html.escape(p.code)}</div>')
        o.append(f'<div class="nom">{html.escape(p.name)}</div>')
        o.append(f'<div class="dim"><b>{_g(p.width)} × {_g(p.height)} × {_g(p.thickness)} mm</b>'
                 f' · {html.escape(p.material)} · cantos F{_g(p.edge_front)} B{_g(p.edge_back)} '
                 f'L{_g(p.edge_left)} R{_g(p.edge_right)}</div>')
        o.append(_svg(p, back=False))
        if back:
            o.append(_svg(p, back=True))
        o.append("</div>")

    o.append("</div></html>")
    return "\n".join(o)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada")
    ap.add_argument("-o", "--salida", default="hojas.html")
    ap.add_argument("--titulo", default="")
    a = ap.parse_args(argv)

    panels = cargar(a.entrada)
    panels = [p for p in panels if p.holes or p.side_holes or p.slots]
    titulo = a.titulo or os.path.basename(os.path.dirname(os.path.abspath(a.entrada))) \
        if os.path.basename(a.entrada) == "piezas.json" \
        else a.titulo or os.path.basename(a.entrada).replace("-Mass production.json", "")
    with open(a.salida, "w", encoding="utf-8") as fh:
        fh.write(build(panels, titulo))
    print(f"{len(panels)} piezas → {a.salida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
