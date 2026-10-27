# -*- coding: utf-8 -*-
"""
web_piezas — datos y planos por pieza para la pagina web que abre el QR de la etiqueta.

    python3 web_piezas.py <render.json> --orden 260625-20 --guardado 22/10/2026 \\
                          -o ../curvado/public [--modulos 0,3,5]

Escribe en <salida> (la carpeta `public/` del proyecto de Vercel `curvado`):
  pz/c/<codigo>.json            datos de la pieza + su modulo (lo que lee /p/<codigo>)
  pz/<orden>/m<NN>.pdf          planos completos del modulo (planos.py)
  pz/<orden>/<codigo>.png       lamina de la pieza (caras acotadas + mecanizados)
  pz/<orden>/<codigo>_ubic.svg  isometrica del modulo con la pieza resaltada

La pagina (`public/p/index.html`) es estatica: Vercel reescribe /p/<codigo> a ella y el
script lee el codigo de la URL. El QR de la etiqueta apunta a  <base>/p/<codigo>; el EAN-13
sigue siendo el codigo solo, para la perforadora.

No publica cliente ni direccion: sale el ambiente y la orden de GuiGui.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import planos as PL  # noqa: E402


def _n(v):
    return PL._n(v)


def slug(s):
    s = re.sub(r"[^A-Za-z0-9]+", "_", PL.re.sub(r"[^\x20-\x7e]", "", s or "")).strip("_")
    return s or "x"


def ubic_svg(piezas, sel, ruta):
    """Isometrica del modulo armado con la pieza `sel` resaltada (SVG liviano)."""
    polys = []
    for q in piezas:
        vs = PL.vertices(q)
        cpz = [sum(v[k] for v in vs) / 8.0 for k in range(3)]
        pr = [PL.proy_iso(v) for v in vs]
        es = q is sel
        for cara in PL.CARAS:
            a, b, c = vs[cara[0]], vs[cara[1]], vs[cara[2]]
            n = PL.norm(PL.cross(PL.sub(b, a), PL.sub(c, a)))
            cen = [sum(vs[i][k] for i in cara) / 4.0 for k in range(3)]
            if PL.dot(n, PL.sub(cen, cpz)) < 0:
                n = PL.mul(n, -1)
            if PL.dot(n, PL.V_ISO) <= 1e-6:
                continue
            eje = [abs(x) for x in n]
            k = PL.SOMBRA[eje.index(max(eje))]
            base = (239, 95, 39) if es else (226, 226, 222)
            rgb = tuple(int(min(255, ch * k)) for ch in base)
            polys.append((PL.dot(cen, PL.V_ISO) + (1e5 if es else 0),
                          [(pr[i][0], -pr[i][1]) for i in cara], rgb, es))
    xs = [p[0] for _, ps, _, _ in polys for p in ps]
    ys = [p[1] for _, ps, _, _ in polys for p in ps]
    mnx, mxx, mny, mxy = min(xs), max(xs), min(ys), max(ys)
    pad = 0.04 * max(mxx - mnx, mxy - mny)
    vb = "%.1f %.1f %.1f %.1f" % (mnx - pad, mny - pad, mxx - mnx + 2 * pad, mxy - mny + 2 * pad)
    sw = 0.0025 * max(mxx - mnx, mxy - mny)
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s">' % vb]
    for _, ps, rgb, es in sorted(polys, key=lambda t: t[0]):
        pts = " ".join("%.1f,%.1f" % p for p in ps)
        out.append('<polygon points="%s" fill="rgb(%d,%d,%d)" stroke="%s" stroke-width="%.2f" stroke-linejoin="round"/>'
                   % (pts, rgb[0], rgb[1], rgb[2], "#7a2a08" if es else "#8a8a86", sw * (1.6 if es else 1)))
    out.append("</svg>")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(out))


def lamina_png(pdf, pagina, ruta, dpi=130):
    base = ruta[:-4]
    subprocess.run(["pdftocairo", "-png", "-r", str(dpi), "-f", str(pagina), "-l", str(pagina),
                    "-singlefile", pdf, base], check=True)
    try:
        from PIL import Image
        im = Image.open(ruta).convert("RGB")
        im.quantize(colors=24, method=Image.Quantize.MEDIANCUT).save(ruta, optimize=True)
    except Exception:
        pass


def cantos_txt(c):
    nom = {"IZQ": "izquierdo", "DER": "derecho", "ABAJO": "abajo", "ARRIBA": "arriba"}
    lados = [nom[k] for k in ("ARRIBA", "ABAJO", "IZQ", "DER") if c.get(k)]
    return lados


def _manual(dir_manuales, mueble, dir_o, carpeta, idx):
    """Copia manuales/manual_<mueble>.pdf (salida de manual_armado.py) a la web; devuelve la URL."""
    if not dir_manuales:
        return None
    src = os.path.join(dir_manuales, "manual_%s.pdf" % mueble.replace(" ", "_").replace("/", "-"))
    if not os.path.exists(src):
        return None
    import shutil
    shutil.copyfile(src, os.path.join(dir_o, "m%02d_manual.pdf" % (idx + 1)))
    return "/pz/%s/m%02d_manual.pdf" % (carpeta, idx + 1)


def generar(render, salida, orden, guardado, modulos=None, manuales=None):
    ADR = PL.paquete._cargar_adr()
    muebles, d = ADR.leer_render(render, None, None)
    total = len(d["models"])
    idxs = modulos if modulos is not None else list(range(total))
    ambiente = ""
    try:
        ambiente = d["models"][0].get("roomName", "")
    except Exception:
        pass
    carpeta = "%s_%s" % (slug(orden), slug(ambiente))
    dir_o = os.path.join(salida, "pz", carpeta)
    dir_c = os.path.join(salida, "pz", "c")
    os.makedirs(dir_o, exist_ok=True)
    os.makedirs(dir_c, exist_ok=True)
    n_piezas = 0
    for idx in idxs:
        pdf = os.path.join(dir_o, "m%02d.pdf" % (idx + 1))
        piezas, info = PL.planos(render, pdf, idx, orden, guardado)
        url_manual = _manual(manuales, info["mueble"], dir_o, carpeta, idx)
        lista = [dict(n=p.num, nombre=p.nombre, codigo=p.codigo,
                      medida="%s x %s x %s" % tuple(_n(v) for v in (sorted([p.W, p.H], reverse=True) + [p.T])))
                 for p in piezas]
        for p in piezas:
            png = os.path.join(dir_o, "%s.png" % p.codigo)
            lamina_png(pdf, 3 + p.num, png)
            ubic_svg(piezas, p, os.path.join(dir_o, "%s_ubic.svg" % p.codigo))
            ops = PL.operaciones(p)
            mec = Counter(o["tipo"].split(" (")[0] for o in ops)
            a, b = sorted([p.corte_W, p.corte_H], reverse=True)
            ta, tb = sorted([p.W, p.H], reverse=True)
            datos = dict(
                version=1,
                codigo=p.codigo,
                orden=orden, ambiente=ambiente, guardado=guardado,
                modulo=dict(n=idx + 1, total=total, nombre=info["mueble"],
                            ancho=info["ancho"], alto=info["alto"], prof=info["prof"],
                            piezas=lista,
                            pdf="/pz/%s/m%02d.pdf" % (carpeta, idx + 1),
                            manual=url_manual),
                pieza=dict(n=p.num, nombre=p.nombre, nombre_guigui=p.nombre_guigui, tipo=p.tipo,
                           corte="%s x %s" % (_n(a), _n(b)), terminada="%s x %s" % (_n(ta), _n(tb)),
                           espesor=_n(p.T), material=PL.mat_es(p.material), color=PL.tex_es(p.textura),
                           veta=p.veta.lower(), rol=p.rol,
                           cantos=cantos_txt(p.cantos),
                           cantos_lados=dict(arriba=bool(p.cantos.get("ARRIBA")), abajo=bool(p.cantos.get("ABAJO")),
                                             izq=bool(p.cantos.get("IZQ")), der=bool(p.cantos.get("DER"))),
                           W=_n(p.W), H=_n(p.H),
                           mecanizados=[dict(tipo=t, n=c) for t, c in mec.items()],
                           aviso=p.aviso or ""),
                plano="/pz/%s/%s.png" % (carpeta, p.codigo),
                ubicacion="/pz/%s/%s_ubic.svg" % (carpeta, p.codigo),
            )
            with open(os.path.join(dir_c, "%s.json" % p.codigo), "w", encoding="utf-8") as f:
                json.dump(datos, f, ensure_ascii=False, separators=(",", ":"))
            n_piezas += 1
        print("  m%02d %-28s %2d piezas" % (idx + 1, info["mueble"], len(piezas)))
    print("%s: %d piezas en pz/%s y pz/c" % (salida, n_piezas, carpeta))
    return carpeta


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render")
    ap.add_argument("-o", "--salida", default=os.path.join(os.path.dirname(AQUI), "curvado", "public"))
    ap.add_argument("--orden", required=True)
    ap.add_argument("--guardado", default="")
    ap.add_argument("--modulos", default="", help="indices de models[] separados por coma (default: todos)")
    ap.add_argument("--manuales", default="", help="carpeta con manual_<mueble>.pdf (manual_armado.py)")
    a = ap.parse_args(argv)
    mods = [int(x) for x in a.modulos.split(",") if x.strip()] or None
    generar(a.render, a.salida, a.orden, a.guardado, mods, a.manuales or None)


if __name__ == "__main__":
    main()
