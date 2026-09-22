"""
Punto de entrada unico: dado un archivo, devuelve la lista de `Panel`.

Reconoce solo la fuente y delega:
    <ORDEN>-Mass production.json   ->  guigui.py    (GuiGui)
    piezas.json                    ->  fusion_json.py  (Fusion)

Todo lo que viene despues —los cuatro generadores, la lista de corte, las
hojas de verificacion— trabaja contra `Panel` y no sabe de donde salio.
"""

from __future__ import annotations

import json
import os
from typing import List

from panel import Panel


def detectar(path: str) -> str:
    base = os.path.basename(path)
    if base.endswith("Mass production.json"):
        return "guigui"
    if base == "piezas.json":
        return "fusion"
    try:
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except (ValueError, OSError):
        return "desconocido"
    if isinstance(doc, dict):
        if doc.get("origen") == "fusion" or "piezas" in doc:
            return "fusion"
        if "layoutResult" in doc:
            return "guigui"
    return "desconocido"


def cargar(path: str, rotate_edges: bool = True) -> List[Panel]:
    """`rotate_edges` solo aplica a la entrada de GuiGui; Fusion lo ignora."""
    origen = detectar(path)
    if origen == "guigui":
        from guigui import load_layout, panels_from_layout
        return panels_from_layout(load_layout(path), rotate_edges=rotate_edges)
    if origen == "fusion":
        import fusion_json
        return fusion_json.cargar(path)
    raise ValueError(
        f"No reconozco el formato de {path}. Esperaba un "
        f"'<ORDEN>-Mass production.json' de GuiGui o un 'piezas.json' de Fusion.")


def buscar(path: str) -> List[str]:
    """Acepta un archivo o una carpeta; devuelve las entradas que encuentre."""
    if os.path.isfile(path):
        return [path]
    out = []
    for root, _dirs, files in os.walk(path):
        for f in files:
            if f.endswith("Mass production.json") or f == "piezas.json":
                out.append(os.path.join(root, f))
    return sorted(out)
