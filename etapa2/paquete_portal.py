# -*- coding: utf-8 -*-
"""
paquete_portal — arma el paquete de un ambiente para el portal de ingenieria (ingenieria.leiten.com.ar)

    python3 paquete_portal.py <render.json> <carpeta PENDRIVE> --proyecto MLV-COCINA \
        --nombre "Malvinas · Cocina" --obra Malvinas --orden 260625-20 --guardado 22/10/2026 \
        [--idee planos_IDEE.pdf] [--empresa hemma] -o paquete_MLV-COCINA.zip

Formato: `docs/PORTAL_INGENIERIA.md` (formato "fabrica-muebles/paquete@1"). Un ZIP con
`manifest.json` + archivos. El portal lo recibe por API y lo carga en su modelo; aca no se
habla con el portal (eso lo hace `subir_portal.py` cuando exista el endpoint).

Necesita que la carpeta ya este generada con `generar_desde_render.sh` (maestra, piezas/,
XML3, lista de corte, manuales). Los planos de mecanizado y las ubicaciones se regeneran aca
con `web_piezas.py` en una carpeta temporal (mismos numeros y nombres).
"""
from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import web_piezas  # noqa: E402

FORMATO = "fabrica-muebles/paquete@1"
CODIGO_RE = re.compile(r"^[A-Z0-9][A-Z0-9._\-/]{1,39}$")   # = esCodigoValido del portal


def _num(s):
    try:
        f = float(str(s).replace(",", "."))
        return int(f) if f == int(f) else round(f, 2)
    except ValueError:
        return s


def _par(s):
    return [_num(x) for x in str(s).replace("×", "x").split("x")]


def _pagina(pdf, n, salida):
    from pypdf import PdfReader, PdfWriter
    r = PdfReader(pdf)
    w = PdfWriter()
    w.add_page(r.pages[n - 1])
    with open(salida, "wb") as fh:
        w.write(fh)


def partir_idee(pdf, dir_out):
    """Hoja 1 = conjunto; hojas con 'ID nnnn · <EAN13>' = piezas; 'Módulo N ·' = modulos."""
    from pypdf import PdfReader, PdfWriter
    r = PdfReader(pdf)
    piezas, modulos, conjunto = {}, {}, None
    for i, pg in enumerate(r.pages, 1):
        t = pg.extract_text() or ""
        m = re.search(r"ID (\d+) · (\d{13})", t)
        dest = None
        if m:
            dest = os.path.join(dir_out, "idee_%s.pdf" % m.group(2)); piezas[m.group(2)] = (dest, int(m.group(1)))
        else:
            mm = re.search(r"Módulo (\d+) ·", t)
            if mm:
                dest = os.path.join(dir_out, "idee_m%02d.pdf" % int(mm.group(1))); modulos[int(mm.group(1))] = dest
            elif i == 1:
                dest = os.path.join(dir_out, "idee_conjunto.pdf"); conjunto = dest
        if dest:
            w = PdfWriter(); w.add_page(pg)
            with open(dest, "wb") as fh:
                w.write(fh)
    return conjunto, modulos, piezas


def armar(a):
    P = a.carpeta
    maestra = json.load(io.open(os.path.join(P, "maestra.json"), encoding="utf-8"))
    pm = {p["codigo"]: p for p in json.load(io.open(os.path.join(P, "piezas", "piezas_maquina.json"),
                                                    encoding="utf-8"))["piezas"]}
    dos = {}
    ruta2 = os.path.join(P, "piezas", "piezas_2pasos.json")
    if os.path.exists(ruta2):
        for p in json.load(io.open(ruta2, encoding="utf-8"))["piezas"]:
            if p["nombre"].endswith("PASO 2"):
                orig = next(c for c in pm if c[2:12] == p["codigo"][2:12])
                dos[orig] = p["codigo"]
    aviso_inf = {}
    for linea in io.open(os.path.join(P, "piezas", "piezas_informe.txt"), encoding="utf-8"):
        m = re.match(r"\s*\d+ (\d{13}) .{30} (.*)$", linea.rstrip("\n"))
        if m:
            aviso_inf[m.group(1)] = [x.strip()[2:] for x in m.group(2).split(";") if x.strip().startswith("⚠")]

    tmp = tempfile.mkdtemp(prefix="paq_")
    web = os.path.join(tmp, "web")
    carpeta_web = web_piezas.generar(a.render, web, a.orden, a.guardado, None, os.path.join(P, "manuales"))
    dir_w = os.path.join(web, "pz", carpeta_web)
    idee_c, idee_m, idee_p = (None, {}, {})
    if a.idee:
        os.makedirs(os.path.join(tmp, "idee"))
        idee_c, idee_m, idee_p = partir_idee(a.idee, os.path.join(tmp, "idee"))

    z = zipfile.ZipFile(a.salida, "w", zipfile.ZIP_DEFLATED)
    def poner(src, ruta):
        z.write(src, ruta); return ruta

    proy = a.proyecto.upper()
    assert CODIGO_RE.match(proy), "codigo de proyecto invalido para el portal: %s" % proy
    manifest = dict(
        formato=FORMATO,
        generado=dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        origen=dict(programa="FABRICA MUEBLES · etapa2/paquete_portal.py", commit=_commit(),
                    guigui=dict(orden=a.orden, ambiente=maestra["ambiente"], guardado=a.guardado,
                                render=os.path.basename(a.render))),
        empresa=a.empresa,
        proyecto=dict(codigo=proy, nombre=a.nombre, obra=a.obra, ambiente=maestra["ambiente"], orden=a.orden),
        conjunto=dict(codigo=proy, descripcion=a.nombre, tipo="conjunto", archivos=[]),
        modulos=[], archivos_proyecto=[], avisos=[])
    if idee_c:
        manifest["conjunto"]["archivos"].append(dict(rol="plano_idee", ruta=poner(idee_c, "conjunto/plano_idee.pdf")))
    if a.idee:
        manifest["archivos_proyecto"].append(dict(rol="planos_idee_completo", ruta=poner(a.idee, "proyecto/planos_idee.pdf")))
    for nombre, rol, maq in (("lista_corte.xlsx", "lista_corte", "corte_hp280"),
                             ("lista_corte.csv", "lista_corte", "corte_hp280"),
                             ("HOJAS_VERIFICACION.html", "hojas_verificacion", "perforadora_6caras"),
                             ("HOJAS_2PASOS.html", "hojas_verificacion", "perforadora_6caras"),
                             ("LEEME.md", "leeme", None),
                             (os.path.join("piezas", "piezas_informe.txt"), "informe_generacion", None)):
        src = os.path.join(P, nombre)
        if os.path.exists(src):
            d = dict(rol=rol, ruta=poner(src, "proyecto/" + os.path.basename(nombre)))
            if maq:
                d["maquina"] = maq
            manifest["archivos_proyecto"].append(d)

    vistos = set()
    for mu in maestra["muebles"]:
        k = int(mu["indice"]) + 1
        cod_m = "%s-M%02d" % (proy, k)
        mod = dict(n=k, codigo=cod_m, nombre=mu["nombre"], tipo="subconjunto", cantidad=1,
                   ancho=mu["ancho"], alto=mu["alto"], prof=mu["prof"], archivos=[], piezas=[])
        pdf_m = os.path.join(dir_w, "m%02d.pdf" % k)
        mod["archivos"].append(dict(rol="planos_mecanizado", ruta=poner(pdf_m, "modulos/M%02d/planos_mecanizado.pdf" % k)))
        man = os.path.join(dir_w, "m%02d_manual.pdf" % k)
        if os.path.exists(man):
            mod["archivos"].append(dict(rol="manual_armado", publico=True, ruta=poner(man, "modulos/M%02d/manual_armado.pdf" % k)))
        if k in idee_m:
            mod["archivos"].append(dict(rol="plano_idee", ruta=poner(idee_m[k], "modulos/M%02d/plano_idee.pdf" % k)))
        for p in sorted(mu["piezas"], key=lambda q: q["globo"]):
            c = p["codigo"]
            vistos.add(c)
            w = json.load(io.open(os.path.join(web, "pz", "c", c + ".json"), encoding="utf-8"))["pieza"]
            base = "piezas/%s/" % c
            pdf_p = os.path.join(tmp, "mec_%s.pdf" % c)
            _pagina(pdf_m, 3 + int(w["n"]), pdf_p)
            arch = []
            if c in idee_p:
                arch.append(dict(rol="plano_idee", principal=True, ruta=poner(idee_p[c][0], base + "plano_idee.pdf")))
            arch.append(dict(rol="plano_mecanizado", principal=c not in idee_p, ruta=poner(pdf_p, base + "plano_mecanizado.pdf")))
            arch.append(dict(rol="plano_mecanizado_png", ruta=poner(os.path.join(dir_w, c + ".png"), base + "plano_mecanizado.png")))
            arch.append(dict(rol="ubicacion", publico=True, ruta=poner(os.path.join(dir_w, c + "_ubic.svg"), base + "ubicacion.svg")))
            x1 = os.path.join(P, "XML3", c + ".xml")
            if os.path.exists(x1):
                arch.append(dict(rol="programa", maquina="perforadora_6caras", paso=1 if c in dos else None,
                                 ruta=poner(x1, "programas/perforadora/%s.xml" % c)))
            if c in dos:
                arch.append(dict(rol="programa", maquina="perforadora_6caras", paso=2, codigo_programa=dos[c],
                                 ruta=poner(os.path.join(P, "XML3_2PASOS", dos[c] + ".xml"),
                                            "programas/perforadora/%s.xml" % dos[c])))
                un = os.path.join(P, "XML3_PRUEBA_UN_PASO", c + ".xml")
                if os.path.exists(un):
                    arch.append(dict(rol="programa_alternativo", maquina="perforadora_6caras", nota="un solo paso, a probar",
                                     ruta=poner(un, "programas/perforadora_un_paso/%s.xml" % c)))
            q = pm.get(c, {})
            mod["piezas"].append(dict(
                item=p["globo"], codigo=c, id_etiqueta=p.get("id_etiqueta"), cantidad=1,
                nombre=p["nombre"], nombre_guigui=p["nombre_guigui"], tipo=p["tipo"], rol=p["rol"],
                cajon=p.get("cajon") or 0,
                medida=dict(terminada=[_num(p["W"]), _num(p["H"])], corte=_par(w["corte"]), espesor=_num(p["T"])),
                material=w["material"], material_codigo=p["material"], color=w["color"], veta=w["veta"],
                cantos=dict(izq=p["cantos"]["izq"], der=p["cantos"]["der"], abajo=p["cantos"]["abajo"],
                            arriba=p["cantos"]["arriba"]),
                mecanizados=w["mecanizados"],
                dos_pasos=dict(paso2=dos[c]) if c in dos else None,
                avisos=aviso_inf.get(c, []) + ([w["aviso"]] if w.get("aviso") else []),
                archivos=arch))
        manifest["modulos"].append(mod)
    if a.idee:
        sobran = sorted(set(idee_p) - vistos)
        faltan = sorted(vistos - set(idee_p))
        if sobran:
            manifest["avisos"].append("planos de IDEE de piezas que no estan en GuiGui: %s" % ", ".join(sobran))
        if faltan:
            manifest["avisos"].append("piezas sin plano de IDEE: %s" % ", ".join(faltan))
        for c, (_, idv) in idee_p.items():
            mp = next((p for mu in maestra["muebles"] for p in mu["piezas"] if p["codigo"] == c), None)
            if mp and mp.get("id_etiqueta") and int(mp["id_etiqueta"]) != idv:
                manifest["avisos"].append("ID etiqueta distinto en IDEE (%s) y GuiGui (%s) para %s" % (idv, mp["id_etiqueta"], c))
    z.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=1))
    z.close()
    shutil.rmtree(tmp, ignore_errors=True)
    n = sum(len(m["piezas"]) for m in manifest["modulos"])
    print("%s: %d modulos, %d piezas, %d archivos, %.1f MB" % (
        a.salida, len(manifest["modulos"]), n, len(zipfile.ZipFile(a.salida).namelist()) - 1,
        os.path.getsize(a.salida) / 1e6))
    for av in manifest["avisos"]:
        print("  aviso:", av)


def _commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=AQUI,
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return ""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("render"); ap.add_argument("carpeta")
    ap.add_argument("--proyecto", required=True, help="codigo del proyecto en el portal, ej. MLV-COCINA")
    ap.add_argument("--nombre", required=True); ap.add_argument("--obra", default="")
    ap.add_argument("--orden", required=True); ap.add_argument("--guardado", default="")
    ap.add_argument("--empresa", default="hemma"); ap.add_argument("--idee", default="")
    ap.add_argument("-o", "--salida", required=True)
    armar(ap.parse_args(argv))


if __name__ == "__main__":
    main()
