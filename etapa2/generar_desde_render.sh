#!/bin/bash
# Paquete de produccion completo de un mueble de GuiGui, directo desde su render.json (sin Fusion).
#
#   ./generar_desde_render.sh <render.json> <carpeta PENDRIVE> <orden> <cliente> <guardado dd/mm/aaaa> [url-base]
#
# Escribe en <carpeta>:
#   maestra.json                 numeros, nombres y medidas (= etiqueta, web, planos, manual)
#   piezas/                      piezas.json (terminada) -> _corte -> _maquina, informes, modelo.json
#   XML3/<codigo>.xml            un programa por pieza (perforar ANTES de cantear: medida de corte)
#   XML3_2PASOS/99…xml           segundo paso de las piezas que no salen en uno (ver piezas/dos_pasos.txt)
#   XML3_PRUEBA_UN_PASO/         esas mismas piezas en un solo programa, para probar si MH2026 lo acepta
#   lista_corte.csv/.xlsx        para AutoCUT (columna 条码 = codigo)
#   HOJAS_VERIFICACION.html, HOJAS_2PASOS.html
#   etiquetas_qr_web/            etiquetas 60x39 y A4 con QR a <url-base>/p/<codigo>
#   manuales/manual_<mueble>.pdf manual de armado de 2 hojas por mueble
# y actualiza la web de piezas en curvado/public (pz/c/<codigo>.json, planos, ubicacion, manual).
set -e
cd "$(dirname "$0")"
R="$1"; P="$2"; ORDEN="$3"; CLIENTE="$4"; GUARDADO="$5"; URL="${6:-https://leiten.vercel.app}"
[ -f "$R" ] && [ -n "$P" ] || { sed -n 2,16p "$0"; exit 1; }
mkdir -p "$P/piezas" "$P/manuales"
python3 paquete.py "$R" -o "$P" | head -1
python3 render_piezas.py "$R" -o "$P/piezas/piezas.json" --orden "$ORDEN" --cliente "$CLIENTE" --herrajes-vigentes
python3 a_medida_corte.py "$P/piezas/piezas.json" -o "$P/piezas/piezas_corte.json" > /dev/null
python3 ajustar_maquina.py "$P/piezas/piezas_corte.json" -o "$P/piezas/piezas_maquina.json" > "$P/piezas/ajustes_maquina.txt"
TMP="$(mktemp -d)"
# Sin borrar nada en la carpeta (en la Mac borrar pide permiso): se genera en TMP y se copia encima.
python3 exportar.py "$P/piezas/piezas_maquina.json" -o "$TMP/uno" --formatos xml3 | tail -1
mkdir -p "$P/XML3" "$P/XML3_2PASOS" "$P/XML3_PRUEBA_UN_PASO"
cp -f "$TMP/uno/XML3/"*.xml "$P/XML3/"
python3 dos_pasos.py "$P/piezas/piezas_maquina.json" -o "$P/piezas/piezas_2pasos.json" > "$P/piezas/dos_pasos.txt"
tail -1 "$P/piezas/dos_pasos.txt"
python3 exportar.py "$P/piezas/piezas_2pasos.json" -o "$TMP" --formatos xml3 > /dev/null
python3 - "$P" "$TMP/XML3" <<'PY'
import json, os, shutil, sys
P, X2 = sys.argv[1], sys.argv[2]
os.makedirs(os.path.join(P, "XML3_2PASOS"), exist_ok=True)
os.makedirs(os.path.join(P, "XML3_PRUEBA_UN_PASO"), exist_ok=True)
conf = {l.split()[0] for l in open(os.path.join(P, "piezas", "ajustes_maquina.txt"), encoding="utf-8") if "CONFLICTO" in l}
for p in json.load(open(os.path.join(P, "piezas", "piezas_2pasos.json"), encoding="utf-8"))["piezas"]:
    c = p["codigo"]
    if p["nombre"].endswith("PASO 1"):
        if c not in conf:
            shutil.copy(os.path.join(P, "XML3", c + ".xml"), os.path.join(P, "XML3_PRUEBA_UN_PASO", c + ".xml"))
        shutil.copy(os.path.join(X2, c + ".xml"), os.path.join(P, "XML3", c + ".xml"))
    else:
        shutil.copy(os.path.join(X2, c + ".xml"), os.path.join(P, "XML3_2PASOS", c + ".xml"))
PY
python3 - "$P" <<'PY'
import json, os, sys
P = sys.argv[1]
d = json.load(open(os.path.join(P, "piezas", "piezas_2pasos.json"), encoding="utf-8"))["piezas"]
quedan = {"XML3": {p["codigo"] for p in json.load(open(os.path.join(P, "piezas", "piezas_maquina.json"), encoding="utf-8"))["piezas"]},
          "XML3_2PASOS": {p["codigo"] for p in d if p["nombre"].endswith("PASO 2")},
          "XML3_PRUEBA_UN_PASO": {p["codigo"] for p in d if p["nombre"].endswith("PASO 1")}}
for carpeta, codigos in quedan.items():
    viejos = [f for f in os.listdir(os.path.join(P, carpeta)) if f.endswith(".xml") and f[:-4] not in codigos]
    if viejos:
        print("ATENCION: en %s quedaron programas que ya no corresponden (borrarlos): %s" % (carpeta, ", ".join(sorted(viejos))))
PY
rm -rf "$TMP"
python3 listacorte.py "$P/piezas/piezas.json" -o "$P" | tail -1
python3 hojas.py "$P/piezas/piezas_maquina.json" -o "$P/HOJAS_VERIFICACION.html" --titulo "Perforadora: cara A arriba" | tail -1
python3 hojas.py "$P/piezas/piezas_2pasos.json" -o "$P/HOJAS_2PASOS.html" --titulo "Piezas en dos pasos" | tail -1
python3 etiquetas.py "$P/maestra.json" -o "$P/etiquetas_qr_web" --orden "$ORDEN" --cliente "$CLIENTE" --alto 39 --url-base "$URL" | tail -1
python3 render_modelo.py "$R" -o "$P/piezas/modelo.json" --orden "$ORDEN"
python3 manual_armado.py "$P/piezas/modelo.json" -o "$P/manuales/manual.pdf" | sed 's/ ->.*//'
python3 web_piezas.py "$R" --orden "$ORDEN" --guardado "$GUARDADO" -o ../curvado/public --manuales "$P/manuales" | tail -1
