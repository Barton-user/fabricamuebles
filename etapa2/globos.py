# -*- coding: utf-8 -*-
"""
globos — dibuja los globos numerados sobre la explotada que capturo Fusion.

    python3 globos.py <mueble>_explotada.png   (busca el .json al lado)

Escribe <mueble>_explotada_globos.png. El numero es el globo de maestra.json,
que es el mismo de la lista de materiales y de la etiqueta.
"""

from __future__ import annotations

import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont


def _fuente(px):
    for f in ("/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if os.path.exists(f):
            try:
                return ImageFont.truetype(f, px)
            except Exception:
                pass
    return ImageFont.load_default()


def _contenido(im):
    """Caja del dibujo (lo que no es fondo ni grilla ni sombra). Fusion deja el
    fondo con un degrade y una grilla tenue: se toma como dibujo lo que se
    aparta bastante del color del fondo local."""
    W, H = im.size
    peq = im.resize((W // 4, H // 4))
    px = peq.load()
    w, h = peq.size
    xs, ys = [], []
    for y in range(h):
        bg = px[2, y]
        for x in range(w):
            p = px[x, y]
            if sum(abs(p[i] - bg[i]) for i in range(3)) > 90:
                xs.append(x); ys.append(y)
    if not xs:
        return im, (0, 0), (W, H)
    return im, (min(xs) * 4, min(ys) * 4), (max(xs) * 4 + 3, max(ys) * 4 + 3)


def recortar(im, margen=60):
    """Recorta el aire alrededor del dibujo."""
    W, H = im.size
    _, (x0, y0), (x1, y1) = _contenido(im)
    return im.crop((max(0, x0 - margen), max(0, y0 - margen), min(W, x1 + margen), min(H, y1 + margen))), (x0, y0)


def poner_globos(ruta_png, radio=44):
    base = ruta_png[:-4]
    with open(base + ".json", "r", encoding="utf-8") as f:
        meta = json.load(f)
    im = Image.open(ruta_png).convert("RGB")
    W, H = im.size
    piezas = meta["piezas"]
    _, (x0, y0), (x1, y1) = _contenido(im)
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    # posicion inicial del globo: desde el centro de la pieza, alejandose del centro de la imagen
    globos = []
    for p in piezas:
        dx, dy = p["x"] - cx, p["y"] - cy
        n = math.hypot(dx, dy) or 1.0
        ex = [e for e in p["esquinas"]]
        # radio aparente de la pieza en la imagen
        r_ap = max(math.hypot(e[0] - p["x"], e[1] - p["y"]) for e in ex)
        d = r_ap * 0.55 + radio * 2.2
        globos.append([p["x"] + dx / n * d, p["y"] + dy / n * d])
    # separar globos que se pisan
    for _ in range(200):
        movido = False
        for i in range(len(globos)):
            for j in range(i + 1, len(globos)):
                ax, ay = globos[i]; bx, by = globos[j]
                dd = math.hypot(ax - bx, ay - by)
                if dd < radio * 2.4:
                    ux, uy = ((ax - bx) / dd, (ay - by) / dd) if dd > 1e-6 else (1.0, 0.0)
                    push = (radio * 2.4 - dd) / 2.0 + 1
                    globos[i] = [ax + ux * push, ay + uy * push]
                    globos[j] = [bx - ux * push, by - uy * push]
                    movido = True
        if not movido:
            break
    # que no se salgan de la imagen
    for g in globos:
        g[0] = min(max(g[0], radio + 4), W - radio - 4)
        g[1] = min(max(g[1], radio + 4), H - radio - 4)

    dr = ImageDraw.Draw(im)
    f = _fuente(int(radio * 1.15))
    for p, g in zip(piezas, globos):
        # linea de referencia hasta el borde del globo
        dx, dy = p["x"] - g[0], p["y"] - g[1]
        n = math.hypot(dx, dy) or 1.0
        x1, y1 = g[0] + dx / n * radio, g[1] + dy / n * radio
        dr.line([(x1, y1), (p["x"], p["y"])], fill=(20, 20, 20), width=4)
        dr.ellipse([p["x"] - 7, p["y"] - 7, p["x"] + 7, p["y"] + 7], fill=(20, 20, 20))
        dr.ellipse([g[0] - radio, g[1] - radio, g[0] + radio, g[1] + radio], fill=(255, 255, 255),
                   outline=(20, 20, 20), width=4)
        t = str(p["globo"])
        bb = dr.textbbox((0, 0), t, font=f)
        dr.text((g[0] - (bb[2] - bb[0]) / 2 - bb[0], g[1] - (bb[3] - bb[1]) / 2 - bb[1]), t, fill=(20, 20, 20), font=f)
    im2, _ = recortar(im)
    out = base + "_globos.png"
    im2.save(out)
    return out


if __name__ == "__main__":
    for r in sys.argv[1:]:
        print(poner_globos(r))
