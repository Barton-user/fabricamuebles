"""
Lector del `piezas.json` que exporta el script de Fusion  ->  modelo Panel.

Es el gemelo de `guigui.py`: misma salida, otra fuente. El resto del sistema
—los cuatro generadores, la lista de corte, las hojas— no se entera de cual de
los dos produjo los paneles.

El JSON ya viene en el marco del archivo de maquina (origen abajo a la
izquierda, Y hacia arriba, cara A en Z=0), asi que aca no hay ninguna
transformacion de coordenadas: el script de Fusion la hizo al leer el solido.

CODIGOS DE BARRAS
-----------------
Si una pieza viene sin `codigo`, se le asigna uno de 13 digitos con verificador
EAN-13, y el mapeo se guarda en `codigos.json` al lado del archivo de entrada
para que el mismo mueble de siempre los mismos codigos.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional

from panel import (EDGE_DOWN, EDGE_LEFT, EDGE_RIGHT, EDGE_UP, FACE_BACK,
                   FACE_FRONT, Hole, Panel, SideHole, Slot, Vertex)

CANTOS = {"D": EDGE_DOWN, "U": EDGE_UP, "L": EDGE_LEFT, "R": EDGE_RIGHT}


def _f(v: Any, d: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return d


def _cara(v: Any) -> str:
    return FACE_BACK if str(v).strip().upper() == "B" else FACE_FRONT


def digito_ean13(doce: str) -> str:
    s = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(doce))
    return str((10 - s % 10) % 10)


def codigo_nuevo(orden: str, n: int) -> str:
    base = re.sub(r"\D", "", orden or "")[:8].ljust(8, "0")
    doce = f"{base}{n:04d}"
    return doce + digito_ean13(doce)


def cargar(path: str) -> List[Panel]:
    with open(path, "r", encoding="utf-8") as fh:
        doc = json.load(fh)

    orden = str(doc.get("orden") or "")
    mapa_path = os.path.join(os.path.dirname(os.path.abspath(path)), "codigos.json")
    mapa: Dict[str, str] = {}
    if os.path.exists(mapa_path):
        try:
            with open(mapa_path, encoding="utf-8") as fh:
                mapa = json.load(fh)
        except (ValueError, OSError):
            mapa = {}

    usados = set(mapa.values())
    siguiente = 1
    paneles: List[Panel] = []

    for raw in doc.get("piezas", []):
        nombre = str(raw.get("nombre") or "")
        code = str(raw.get("codigo") or "").strip() or mapa.get(nombre, "")
        if not code:
            while True:
                code = codigo_nuevo(orden, siguiente)
                siguiente += 1
                if code not in usados:
                    break
            usados.add(code)
            mapa[nombre] = code
        paneles.append(_panel(raw, code, doc))

    try:
        with open(mapa_path, "w", encoding="utf-8") as fh:
            json.dump(mapa, fh, ensure_ascii=False, indent=2, sort_keys=True)
    except OSError:
        pass
    return paneles


def _sin_prefijo(nombre: str, ambiente: str, mueble: str) -> str:
    """Saca del nombre de la pieza el ambiente y el mueble, si ya vienen adentro.

    La etiqueta de la lista de corte se arma como ambiente_mueble_pieza. Si el
    cuerpo en Fusion ya se llama "PRUEBA 1_00-Doble c_Roof plate", pegarle otra
    vez el prefijo daria el nombre repetido dos veces.
    """
    for pre in ("%s_%s_" % (ambiente, mueble), "%s_" % ambiente, "%s_" % mueble):
        if pre.strip("_") and nombre.startswith(pre):
            return nombre[len(pre):]
    return nombre


def _panel(raw: Dict[str, Any], code: str, doc: Dict[str, Any]) -> Panel:
    w, h = _f(raw.get("ancho")), _f(raw.get("alto"))
    ab, ar = _f(raw.get("canto_abajo")), _f(raw.get("canto_arriba"))
    iz, de = _f(raw.get("canto_izq")), _f(raw.get("canto_der"))

    p = Panel(
        code=code,
        name=str(raw.get("nombre") or ""),
        width=w, height=h,
        thickness=_f(raw.get("espesor"), 18.0),
        material=str(raw.get("material") or ""),
        grain="2" if str(raw.get("veta", "VERTICAL")).upper() != "HORIZONTAL" else "1",
        quantity=int(_f(raw.get("cantidad"), 1)) or 1,
        # el marco de Fusion ya es el del archivo de maquina: no hay rotacion
        edge_front=ab, edge_back=ar, edge_left=iz, edge_right=de,
        src_width=w, src_height=h, rotated=False,
        # Los campos src_* emulan el marco Y-ABAJO de GuiGui, que es el que usa
        # la lista de corte de la sierra. Como el marco de Fusion es Y-ARRIBA,
        # arriba y abajo se intercambian.
        src_edge_left=iz, src_edge_down=ar, src_edge_right=de, src_edge_up=ab,
        order_no=str(doc.get("orden") or ""),
        room=str(doc.get("ambiente") or ""),
        # location = el MUEBLE/modulo al que pertenece la pieza (va en la
        # etiqueta de la lista de corte). No es la direccion de la obra.
        location=str(raw.get("mueble") or ""),
        short_name=_sin_prefijo(str(raw.get("nombre") or ""),
                               str(doc.get("ambiente") or ""),
                               str(raw.get("mueble") or "")),
        texture=str(raw.get("textura") or ""),
        customer=str(doc.get("cliente") or ""),
        address=str(doc.get("direccion") or doc.get("proyecto") or ""),
        source="fusion",
    )

    for hl in raw.get("agujeros", []):
        p.holes.append(Hole(x=_f(hl.get("x")), y=_f(hl.get("y")),
                            diameter=_f(hl.get("diametro")),
                            depth=_f(hl.get("profundidad")),
                            face=_cara(hl.get("cara")),
                            symbol=str(hl.get("herraje") or "")))
    for s in raw.get("agujeros_canto", []):
        canto = CANTOS.get(str(s.get("canto", "")).strip().upper())
        if canto is None:
            continue
        p.side_holes.append(SideHole(x=_f(s.get("x")), y=_f(s.get("y")),
                                     z=_f(s.get("z"), p.thickness / 2),
                                     diameter=_f(s.get("diametro")),
                                     depth=_f(s.get("profundidad")), edge=canto,
                                     symbol=str(s.get("herraje") or "")))
    for sl in raw.get("ranuras", []):
        p.slots.append(Slot(x1=_f(sl.get("x1")), y1=_f(sl.get("y1")),
                            x2=_f(sl.get("x2")), y2=_f(sl.get("y2")),
                            width=_f(sl.get("ancho")),
                            depth=_f(sl.get("profundidad")),
                            face=_cara(sl.get("cara")),
                            symbol=str(sl.get("herraje") or "")))

    p.edge_slots = list(raw.get("ranuras_canto") or [])

    contorno = raw.get("contorno") or []
    if len(contorno) >= 3:
        p.outline = [Vertex(_f(v.get("x")), _f(v.get("y")), _f(v.get("arco")))
                     for v in contorno]
    return p
