"""
listacorte — lista de corte para AutoCUT / sierra HP280, desde el modelo Panel.

Emite las MISMAS columnas, en el mismo orden, que el `开料清单.xls` que genera
GuiGui, para que el perfil de mapeo que ya esta cargado en AutoCUT siga sirviendo.

    python3 listacorte.py "<ORDEN>-Mass production.json" -o salida/

Escribe  lista_corte.csv  (UTF-8 con BOM) y, si hay openpyxl, lista_corte.xlsx

Medidas
-------
El archivo de la sierra usa el marco ORIGINAL del diseno, no el del archivo de
maquina (que rota la pieza a retrato). Por eso se usan `src_width` / `src_height`.

    长 (largo)  = src_height     宽 (ancho) = src_width
    开料长      = 长 menos los cantos de arriba y abajo
    开料宽      = 宽 menos los cantos de izquierda y derecha

El espesor del canto sale de `edgeInfo` (puede ser 1 o 0,5 mm), no de un valor fijo.

Cantos: 前 (delante) es el canto de ARRIBA del marco original y 后 (atras) el de
ABAJO — al reves de lo que sugiere el nombre. Verificado contra el 开料清单.xls
de GuiGui con las dos fascia boards, las unicas piezas de PRUEBA 1 que tienen
delante y atras distintos.

板件条码 (codigos de barras)
---------------------------
    sin mecanizado        ->  <codigo>
    con mecanizado        ->  <codigo>_<codigo>
    con cara trasera      ->  <codigo>_<codigo>_<codigo>K
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from typing import Any, Dict, List

from cargar import cargar
from mpr import has_back_ops, has_ops
from panel import Panel

COLUMNAS = [
    "序号", "打包二维码", "工件名称",
    "数量", "长", "宽", "成品面积", "厚",
    "材料", "开料长", "开料宽", "切割面积",
    "开料厚", "板件条码", "板号",
    "前封边", "后封边", "左封边", "右封边",
    "纹路", "订单号", "客户名称", "项目地址",
    "部件名称",
]

# traduccion, para el que tenga que mirar el archivo
ESPANOL = [
    "n", "QR empaque", "nombre pieza", "cant", "largo", "ancho", "area terminada",
    "espesor", "material", "largo corte", "ancho corte", "area corte", "espesor corte",
    "codigo de barras", "n placa", "canto delante", "canto atras", "canto izq",
    "canto der", "veta", "orden", "cliente", "proyecto", "componente",
]


def _n(v: float) -> Any:
    return int(round(v)) if abs(v - round(v)) < 1e-9 else round(v, 2)


def barcodes(p: Panel) -> str:
    if not has_ops(p):
        return p.code
    if has_back_ops(p):
        return f"{p.code}_{p.code}_{p.code}K"
    return f"{p.code}_{p.code}"


def fila(p: Panel, n: int) -> List[Any]:
    alto = p.src_height or p.height
    ancho_x = p.src_width or p.width
    corte_alto = alto - p.src_edge_up - p.src_edge_down
    corte_ancho_x = ancho_x - p.src_edge_left - p.src_edge_right
    # 长 (largo) es SIEMPRE la direccion de la veta: 竖纹 = a lo largo de Y,
    # 横纹 = a lo largo de X. La sierra usa este par para decidir si puede
    # girar la pieza al anidar, asi que no es solo una etiqueta.
    if str(p.grain) == "1":
        largo, ancho = ancho_x, alto
        corte_largo, corte_ancho = corte_ancho_x, corte_alto
        # los cantos se nombran respecto del par 长/宽, asi que giran con el
        c_frente, c_atras = p.src_edge_left, p.src_edge_right
        c_izq, c_der = p.src_edge_up, p.src_edge_down
    else:
        largo, ancho = alto, ancho_x
        corte_largo, corte_ancho = corte_alto, corte_ancho_x
        c_frente, c_atras = p.src_edge_up, p.src_edge_down
        c_izq, c_der = p.src_edge_left, p.src_edge_right
    etiqueta = "_".join(x for x in (p.room, p.location, p.short_name) if x) or p.name
    return [
        n, etiqueta, etiqueta, p.quantity,
        _n(largo), _n(ancho), round(largo * ancho / 1e6, 2), _n(p.thickness),
        "_".join(str(x) for x in (_n(p.thickness), p.material, p.texture) if str(x)),
        _n(corte_largo), _n(corte_ancho), round(corte_largo * corte_ancho / 1e6, 2),
        _n(p.thickness),
        barcodes(p), p.plank_id,
        _n(c_frente), _n(c_atras), _n(c_izq), _n(c_der),
        p.veta(), p.order_no, p.customer, p.address, p.name,
    ]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada")
    ap.add_argument("-o", "--salida", default=".")
    ap.add_argument("--espanol", action="store_true",
                    help="encabezados en espanol en vez de chino (rompe el mapeo de AutoCUT)")
    a = ap.parse_args(argv)

    panels = cargar(a.entrada)
    os.makedirs(a.salida, exist_ok=True)
    hdr = ESPANOL if a.espanol else COLUMNAS
    filas = [fila(p, i + 1) for i, p in enumerate(panels)]

    csv_path = os.path.join(a.salida, "lista_corte.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(hdr)
        wr.writerows(filas)
    print(f"{len(filas)} piezas → {csv_path}")

    try:
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "开料清单"
        ws.append(hdr)
        for f in filas:
            ws.append(f)
        for i, col in enumerate(ws.columns, 1):
            ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = \
                min(max(len(str(c.value or "")) for c in col) + 2, 40)
        xl = os.path.join(a.salida, "lista_corte.xlsx")
        wb.save(xl)
        print(f"{len(filas)} piezas → {xl}")
    except ImportError:
        print("(openpyxl no esta instalado; solo se escribio el CSV)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
