# -*- coding: utf-8 -*-
"""
etiquetas_tspl — las mismas etiquetas de etiquetas.py pero en TSPL (lenguaje de la TSC / AIBAO),
en MODO CONTINUO con el paso exacto de la etiqueta, para cuando el sensor de gap no anda.

    python3 etiquetas_tspl.py maestra.json -o <carpeta> --orden 260625-20 --cliente MALVINAS
                              [--paso 42] [--alto 39] [--ancho 60] [--cabezal 12] [--direction 1]

Escribe en <carpeta>:
  00_ALINEAR.txt         imprime una regla para verificar la alineacion (y medir --cabezal)
  NN_<mueble>.txt        una tanda por mueble
  TODAS.txt              las 125 seguidas
  LEEME.txt              como se imprime (copy /b archivo \\\\localhost\\TSC)

Protocolo de alineacion: entre tanda y tanda el papel queda con el GAP en la cuchilla de corte
(se corta ahi). Cada archivo arranca con FEED (paso - cabezal - gap) para llevar el borde de la
etiqueta siguiente al cabezal (una etiqueta queda en blanco), imprime las etiquetas de a 42 mm
exactos, y termina con FEED (cabezal + gap) para dejar otra vez el gap en la cuchilla. --cabezal es la distancia cabezal -
cuchilla (TTP-245C: ~12 mm); se verifica con 00_ALINEAR.txt.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import unicodedata

MM = 8  # dots por mm a 203 dpi

TEXTURAS = {u"白麻面": "blanco lino", u"暖白": "blanco calido", u"玛雅灰": "gris maya", u"拉丝胡桃": "nogal"}
MATERIALES = {u"多层实木": "multilaminado", u"装饰板": "fondo 5 mm",
              "NEstructura": "estructura 18", "STRUCTURE": "estructura 18",
              "NPetfrente": "PET frente 18", "PETFRONT": "PET frente 18", "18PETFRONT": "PET frente 18 (?)",
              "NFondo": "fondo 5", "BACKGROUND": "fondo 5"}


def ascii_(s):
    """Sin acentes ni chino: las fuentes bitmap de la impresora son ASCII."""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.replace(u"·", "-").replace(u"×", "x").replace(u"Ø", "O")
    return "".join(c if 32 <= ord(c) < 127 else "" for c in s).strip()


def _tex(t):
    cod = re.match(r"[A-Za-z]*\d+", t or "")
    cod = cod.group(0) if cod else ""
    for k, v in TEXTURAS.items():
        if k in (t or ""):
            return "%s (%s)" % (v, cod) if cod else v
    return ascii_(t)


def _mat(m):
    return MATERIALES.get(m, ascii_(m))


def _n(v):
    return str(int(v)) if abs(v - round(v)) < 1e-9 else ("%.1f" % v)


def q(s):
    return '"' + ascii_(s).replace('"', "'") + '"'


def cabecera(ancho, paso, direction, density=8, speed=3):
    return ["SIZE %g mm,%g mm" % (ancho, paso), "GAP 0 mm,0 mm", "DIRECTION %d,0" % direction,
            "REFERENCE 0,0", "SHIFT 0", "OFFSET 0 mm", "SET TEAR OFF", "SET PEEL OFF",
            "DENSITY %d" % density, "SPEED %d" % speed, "CODEPAGE 437"]


def etiqueta(mu, p, orden, cliente, ancho, alto):
    """Comandos TSPL de una etiqueta (origen arriba a la izquierda, en dots)."""
    W, H = ancho * MM, alto * MM
    m = 2 * MM
    L = ["CLS"]
    # cabecera: orden - cliente (izq) y mueble (der)
    L.append("TEXT %d,%d,\"2\",0,1,1,%s" % (m, 10, q("%s - %s" % (orden, cliente))))
    mueble = ascii_(mu["nombre"])[:22]
    L.append("TEXT %d,%d,\"1\",0,1,1,%s" % (W - m - 8 * len(mueble), 14, q(mueble)))
    # globo
    d = 64
    gx, gy = m, 36
    L.append("CIRCLE %d,%d,%d,3" % (gx, gy, d))
    num = str(p["globo"])
    fnt, fw, fh = ("5", 32, 48) if len(num) < 3 else ("4", 24, 32)
    L.append("TEXT %d,%d,\"%s\",0,1,1,%s" % (gx + d // 2 - fw * len(num) // 2, gy + d // 2 - fh // 2, fnt, q(num)))
    # nombre, medida de corte, terminada
    tx = gx + d + 10
    L.append("TEXT %d,%d,\"3\",0,1,1,%s" % (tx, 34, q(ascii_(p["nombre"])[:23])))
    a, b = sorted((p["corte_H"], p["corte_W"]), reverse=True)
    ta, tb = sorted((p["H"], p["W"]), reverse=True)
    L.append("TEXT %d,%d,\"4\",0,1,1,%s" % (tx, 62, q("%s x %s x %s" % (_n(a), _n(b), _n(p["T"])))))
    L.append("TEXT %d,%d,\"1\",0,1,1,%s" % (tx, 98, q("corte - terminada %s x %s" % (_n(ta), _n(tb)))))
    # material - textura
    L.append("TEXT %d,%d,\"2\",0,1,1,%s" % (m, 122, q("%s - %s" % (_mat(p["material"]), _tex(p["textura"])))))
    # QR (derecha)
    qx, qy = W - m - 84, 112
    L.append("QRCODE %d,%d,M,3,A,0,%s" % (qx, qy, q(p["codigo"])))
    # cantos (abajo a la derecha)
    cw, ch = 52, 34
    ex, ey = W - m - cw, H - m - ch
    L.append("TEXT %d,%d,\"1\",0,1,1,\"cantos\"" % (ex + 2, ey - 14))
    L.append("BOX %d,%d,%d,%d,1" % (ex, ey, ex + cw, ey + ch))
    k = p["cantos"]
    t = 4
    if k["abajo"]:
        L.append("BAR %d,%d,%d,%d" % (ex, ey + ch - t, cw, t))
    if k["arriba"]:
        L.append("BAR %d,%d,%d,%d" % (ex, ey, cw, t))
    if k["izq"]:
        L.append("BAR %d,%d,%d,%d" % (ex, ey, t, ch))
    if k["der"]:
        L.append("BAR %d,%d,%d,%d" % (ex + cw - t, ey, t, ch))
    # EAN-13 (abajo a la izquierda): 12 digitos, la impresora calcula el digito de control
    cod = p["codigo"]
    L.append("BARCODE %d,%d,\"EAN13\",%d,1,0,3,3,%s" % (m, 164, 80, q(cod[:12])))
    L.append("PRINT 1,1")
    return L


def regla(ancho, alto):
    """Etiqueta con una regla en mm desde el borde de arriba, para medir --cabezal."""
    W = ancho * MM
    alto = int(round(alto))
    L = ["CLS", "TEXT 200,40,\"3\",0,1,1,\"ARRIBA\"", "TEXT 200,%d,\"3\",0,1,1,\"ABAJO\"" % (alto * MM - 60)]
    for k in range(0, alto + 1):
        y = k * MM
        ln = 60 if k % 5 == 0 else (36 if k % 1 == 0 else 20)
        L.append("BAR 0,%d,%d,2" % (min(y, alto * MM - 2), ln))
        if k % 5 == 0:
            L.append("TEXT %d,%d,\"1\",0,1,1,\"%d\"" % (ln + 6, max(y - 5, 0), k))
    L.append("PRINT 1,1")
    return L


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("maestra")
    ap.add_argument("-o", "--salida", default="etiquetas_tspl")
    ap.add_argument("--orden", default="")
    ap.add_argument("--cliente", default="")
    ap.add_argument("--ancho", type=float, default=60.0)
    ap.add_argument("--alto", type=float, default=39.0, help="alto de la etiqueta (sin gap)")
    ap.add_argument("--paso", type=float, default=42.0, help="etiqueta + gap, medido")
    ap.add_argument("--cabezal", type=float, default=12.0, help="distancia cabezal-cuchilla en mm")
    ap.add_argument("--direction", type=int, default=1)
    a = ap.parse_args(argv)
    m = json.load(open(a.maestra, encoding="utf-8"))
    os.makedirs(a.salida, exist_ok=True)
    gap = a.paso - a.alto
    back = int(round((a.cabezal + gap) * MM))
    cab = cabecera(a.ancho, a.paso, a.direction)
    # El BACKFEED de la AIBAO es impreciso (y limitado): en vez de retroceder (cabezal + gap) se
    # AVANZA hasta el borde de la etiqueta siguiente (paso - cabezal - gap), sacrificando una
    # etiqueta en blanco por tanda. Al final se avanza (cabezal + gap) para dejar el gap en la
    # cuchilla; el total por tanda es multiplo del paso, asi que la fase se conserva.
    adelante = int(round(a.paso * MM)) - back
    pre = cab + ["FEED %d" % adelante]
    post = ["FEED %d" % back]
    archivos = []
    todas = []
    for i, mu in enumerate(m["muebles"], 1):
        L = []
        for p in mu["piezas"]:
            L += etiqueta(mu, p, a.orden, a.cliente, a.ancho, a.alto)
        nombre = "%02d_%s.txt" % (i, re.sub(r"[^A-Za-z0-9]+", "_", ascii_(mu["nombre"])).strip("_"))
        with open(os.path.join(a.salida, nombre), "w", encoding="ascii", newline="\r\n") as f:
            f.write("\r\n".join(pre + L + post) + "\r\n")
        archivos.append((nombre, len(mu["piezas"])))
        todas += L
    with open(os.path.join(a.salida, "TODAS.txt"), "w", encoding="ascii", newline="\r\n") as f:
        f.write("\r\n".join(pre + todas + post) + "\r\n")
    with open(os.path.join(a.salida, "00_ALINEAR.txt"), "w", encoding="ascii", newline="\r\n") as f:
        f.write("\r\n".join(pre + regla(a.ancho, a.alto) + post) + "\r\n")
    with open(os.path.join(a.salida, "00_PRUEBA5.txt"), "w", encoding="ascii", newline="\r\n") as f:
        f.write("\r\n".join(pre + regla(a.ancho, a.alto) * 5 + post) + "\r\n")
    with open(os.path.join(a.salida, "LEEME.txt"), "w", encoding="utf-8", newline="\r\n") as f:
        f.write(u"""ETIQUETAS EN TSPL - MODO CONTINUO (sin sensor de gap)
Etiqueta %g x %g mm, paso %g mm, cabezal-cuchilla %g mm, DIRECTION %d.

Copiar esta carpeta a C:\\tsc\\mlv en la PC de la sierra. La impresora tiene que estar compartida como TSC
(ya esta). Cada archivo se manda desde cmd con:

    copy /b C:\\tsc\\mlv\\<archivo> \\\\localhost\\TSC

ALINEACION (una sola vez, y cada vez que se abre la tapa o se mueve el papel):
  con la tapa cerrada, girar el rollo hasta que el GAP (la separacion entre dos etiquetas)
  quede justo en la cuchilla de corte. Nada mas. Cada archivo avanza solo hasta la etiqueta siguiente
  (la primera etiqueta de cada tanda sale en blanco: es el precio de no usar el sensor).

PRUEBA: mandar 00_ALINEAR.txt. Imprime una regla: el "0" tiene que caer en el borde de arriba de la
  etiqueta. Si cae a N mm del borde, regenerar con --cabezal corregido (+N si la regla empieza
  tarde, -N si empieza antes). Al terminar deja de nuevo el gap en la cuchilla: cortar ahi.

TANDAS: un archivo por mueble (NN_<mueble>.txt) o TODAS.txt. Al final de cada archivo el papel
  queda con el gap en la cuchilla: cortar y seguir con el siguiente sin tocar nada.
  Si en el medio de una tanda se ve corrida mas de 1 mm, cancelar, realinear a mano y repetir
  desde ese mueble.

Archivos:
%s
""" % (a.ancho, a.alto, a.paso, a.cabezal, a.direction,
       "\n".join("  %-40s %3d etiquetas" % (n, c) for n, c in archivos)))
    print("%s: %d archivos, %d etiquetas, paso %g, BACKFEED/FEED %d dots" % (a.salida, len(archivos), sum(c for _, c in archivos), a.paso, back))


if __name__ == "__main__":
    main()
