# -*- coding: utf-8 -*-
"""
etiquetas — etiquetas de pieza 60 x 40 mm con EAN-13 y QR, desde maestra.json.

    python3 etiquetas.py maestra.json -o <carpeta> [--mueble "00-Bandejero"]
                         [--orden 260625-20] [--cliente PRUEBA] [--ancho 60 --alto 40]

Escribe:
  etiquetas_60x40.pdf   una etiqueta por pagina, tamano de pagina = etiqueta (para la AIBAO)
  etiquetas_A4.pdf      12 por hoja A4, para probar en cualquier impresora

El codigo de barras y el QR llevan el MISMO valor: el codigo de 13 digitos de
GuiGui (EAN-13 valido), que es el que la perforadora busca para cargar el
programa. El numero grande es el globo de la explotada y de la lista.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

from reportlab.graphics.barcode import eanbc, qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

TEXTURAS = {u"白麻面": "blanco lino", u"暖白": "blanco cálido", u"玛雅灰": "gris maya", u"拉丝胡桃": "nogal"}
MATERIALES = {u"多层实木": "multilaminado", u"装饰板": "fondo 5 mm"}
CJK = "STSong-Light"


FUENTES_CJK = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    "C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/simhei.ttf",
]


def _reg():
    """La fuente china se dibuja como imagen con PIL (las Noto CJK son CFF y
    reportlab no las incrusta). Devuelve la ruta de la fuente o None."""
    for f in FUENTES_CJK:
        if os.path.exists(f):
            try:
                from PIL import ImageFont
                ImageFont.truetype(f, 20)
                return f
            except Exception:
                continue
    return None


def _cjk_imagen(c, texto, x, y, alto_pt, fuente):
    """Escribe `texto` con la fuente CJK como imagen, base en (x, y), alto en puntos."""
    from PIL import Image, ImageDraw, ImageFont
    from reportlab.lib.utils import ImageReader
    px = int(alto_pt * 8)                      # ~576 dpi
    ft = ImageFont.truetype(fuente, px)
    bb = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), texto, font=ft)
    im = Image.new("RGBA", (bb[2] - bb[0] + 4, bb[3] - bb[1] + 4), (255, 255, 255, 0))
    ImageDraw.Draw(im).text((2 - bb[0], 2 - bb[1]), texto, font=ft, fill=(0, 0, 0, 255))
    w = im.size[0] / 8.0
    h = im.size[1] / 8.0
    c.drawImage(ImageReader(im), x, y - h * 0.22, w, h, mask="auto")
    return w


def _tex(t):
    """'d02白麻面' -> 'blanco lino (d02)'"""
    cod = re.match(r"[A-Za-z]*\d+", t or "")
    cod = cod.group(0) if cod else ""
    for k, v in TEXTURAS.items():
        if k in (t or ""):
            return "%s (%s)" % (v, cod) if cod else v
    return t


def _mat(mt):
    return MATERIALES.get(mt, mt)


def _n(v):
    return str(int(v)) if abs(v - round(v)) < 1e-9 else ("%.1f" % v)


def dibujar_etiqueta(c, x0, y0, W, H, mu, p, orden, cliente, cjk):
    """Dibuja una etiqueta con la esquina inferior izquierda en (x0, y0), en puntos."""
    c.saveState()
    c.translate(x0, y0)
    m = 2.2 * mm
    c.setLineWidth(0.4)
    c.rect(0, 0, W, H)
    # --- cabecera: orden y cliente
    c.setFont("Helvetica-Bold", 7)
    c.drawString(m, H - m - 6, "%s · %s" % (orden, cliente))
    c.setFont("Helvetica", 6)
    c.drawRightString(W - m, H - m - 6, mu["nombre"][:34])
    # --- globo grande
    r = 5.2 * mm
    cx, cy = m + r, H - m - 8 - r - 1.5 * mm
    c.setLineWidth(0.8)
    c.circle(cx, cy, r)
    c.setFont("Helvetica-Bold", 15 if p["globo"] < 100 else 12)
    c.drawCentredString(cx, cy - 5, str(p["globo"]))
    # --- nombre de pieza y medidas
    tx = m + 2 * r + 2 * mm
    c.setFont("Helvetica-Bold", 8)
    c.drawString(tx, H - m - 8 - 7, p["nombre"][:26])
    c.setFont("Helvetica-Bold", 10)
    a, b = sorted((p["corte_H"], p["corte_W"]), reverse=True)
    ta, tb = sorted((p["H"], p["W"]), reverse=True)
    c.drawString(tx, H - m - 8 - 19, "%s x %s x %s" % (_n(a), _n(b), _n(p["T"])))
    c.setFont("Helvetica", 5.5)
    c.drawString(tx, H - m - 8 - 26, "corte  ·  terminada %s x %s" % (_n(ta), _n(tb)))
    # --- material y textura (espanol + chino), debajo del globo
    y = H - m - 8 - 2 * r - 1.5 * mm - 9
    c.setFont("Helvetica-Bold", 7)
    c.drawString(m, y, "%s  ·  %s" % (_mat(p["material"]), _tex(p["textura"])))
    # --- cantos: rectangulo con los lados marcados
    cw, ch = 9 * mm, 6.5 * mm
    ex, ey = W - m - cw, m + 1.5 * mm
    c.setLineWidth(0.3)
    c.rect(ex, ey, cw, ch)
    c.setLineWidth(1.4)
    k = p["cantos"]
    if k["abajo"]:
        c.line(ex, ey, ex + cw, ey)
    if k["arriba"]:
        c.line(ex, ey + ch, ex + cw, ey + ch)
    if k["izq"]:
        c.line(ex, ey, ex, ey + ch)
    if k["der"]:
        c.line(ex + cw, ey, ex + cw, ey + ch)
    c.setFont("Helvetica", 4.5)
    c.drawCentredString(ex + cw / 2, ey + ch + 1.2 * mm, "cantos")
    # --- QR (derecha, arriba de los cantos)
    qw = 12 * mm
    qd = qr.QrCodeWidget(p["codigo"])
    b = qd.getBounds()
    d = Drawing(qw, qw, transform=[qw / (b[2] - b[0]), 0, 0, qw / (b[3] - b[1]), 0, 0])
    d.add(qd)
    d.drawOn(c, W - m - qw - 0.5 * mm, ey + ch + 3.5 * mm)
    # --- EAN-13 (abajo a la izquierda)
    bw = W - 2 * m - qw - 3 * mm
    ean = eanbc.Ean13BarcodeWidget(p["codigo"])
    ean.barHeight = 8.5 * mm
    ean.fontSize = 6
    ean.humanReadable = True
    bb = ean.getBounds()
    sx = bw / (bb[2] - bb[0])
    d2 = Drawing(bw, 12 * mm, transform=[sx, 0, 0, 1, -bb[0] * sx, 0])
    d2.add(ean)
    d2.drawOn(c, m, m)
    c.restoreState()


def escribir(m, salida, solo=None, orden="", cliente="", ancho=60.0, alto=40.0):
    os.makedirs(salida, exist_ok=True)
    cjk = _reg()
    W, H = ancho * mm, alto * mm
    piezas = [(mu, p) for mu in m["muebles"] if not solo or mu["nombre"] in solo for p in mu["piezas"]]
    # --- una por pagina
    r1 = os.path.join(salida, "etiquetas_%dx%d.pdf" % (int(ancho), int(alto)))
    c = canvas.Canvas(r1, pagesize=(W, H))
    c.setTitle("Etiquetas %s" % m.get("ambiente", ""))
    for mu, p in piezas:
        dibujar_etiqueta(c, 0, 0, W, H, mu, p, orden, cliente, cjk)
        c.showPage()
    c.save()
    # --- A4, 3 x 4 por hoja
    from reportlab.lib.pagesizes import A4
    r2 = os.path.join(salida, "etiquetas_A4.pdf")
    c = canvas.Canvas(r2, pagesize=A4)
    pw, ph = A4
    cols, filas = 3, 4
    gx = (pw - cols * W) / (cols + 1)
    gy = (ph - filas * H) / (filas + 1)
    i = 0
    for mu, p in piezas:
        col, fila = i % cols, (i // cols) % filas
        x = gx + col * (W + gx)
        y = ph - gy - (fila + 1) * H - fila * gy
        dibujar_etiqueta(c, x, y, W, H, mu, p, orden, cliente, cjk)
        i += 1
        if i % (cols * filas) == 0:
            c.showPage()
    if i % (cols * filas) != 0:
        c.showPage()
    c.save()
    print("%s y %s: %d etiquetas" % (r1, r2, len(piezas)))
    return r1, r2


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("maestra")
    ap.add_argument("-o", "--salida", default=".")
    ap.add_argument("--mueble", action="append")
    ap.add_argument("--orden", default="")
    ap.add_argument("--cliente", default="")
    ap.add_argument("--ancho", type=float, default=60.0)
    ap.add_argument("--alto", type=float, default=40.0)
    a = ap.parse_args(argv)
    with open(a.maestra, "r", encoding="utf-8") as f:
        m = json.load(f)
    escribir(m, a.salida, a.mueble, a.orden, a.cliente, a.ancho, a.alto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
