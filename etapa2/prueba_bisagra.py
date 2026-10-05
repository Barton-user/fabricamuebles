"""
prueba_bisagra — programa de prueba de bisagra (cazoleta Ø35 + 2 tornillos) para puertas.

Arma las dos puertas (DER = bisagra en x = 0, IZQ = bisagra en x = ancho) a la medida de
CORTE, con las medidas de herrajes/medidas.json, descontando el canto (se perfora antes de
cantear). Escribe XML3 (KDTXml) + hoja de verificacion.

    python3 etapa2/prueba_bisagra.py --ancho 295 --alto 386.06 --canto 1 \
        --cazoletas 100 --codigos 9992610019101 9992610019118 -o PENDRIVE/PRUEBA_BISAGRA

--cazoletas: distancia del centro de cada cazoleta al canto de arriba y de abajo, en medida
TERMINADA (la Spar: 100). Las dos puertas son la misma pieza girada 180°.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from panel import Hole, Panel          # noqa: E402
from xml3 import write_xml3            # noqa: E402
import hojas                           # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def puerta(code, nombre, ancho, alto, canto, desde_borde, b, lado):
    cz = b["cazoleta_desde_canto"] - canto              # desde el borde crudo
    tx = cz + b["tornillos_desde_cazoleta"]
    yc = [desde_borde - canto, alto - (desde_borde - canto)]
    if lado == "IZQ":
        cz, tx = ancho - cz, ancho - tx
    p = Panel(code=code, name=nombre, width=ancho, height=alto, thickness=18.0,
              material="18_PET_PET GRIS 18", edge_front=canto, edge_back=canto,
              edge_left=canto, edge_right=canto)
    for y in yc:
        for dy in (b["tornillos_a_lo_largo"], -b["tornillos_a_lo_largo"]):
            p.holes.append(Hole(tx, y + dy, b["tornillo_d"], b["tornillo_prof"], symbol="HINGESCREW"))
        p.holes.append(Hole(cz, y, b["cazoleta_d"], b["cazoleta_prof"], symbol="HINGE"))
    return p


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ancho", type=float, required=True)
    ap.add_argument("--alto", type=float, required=True)
    ap.add_argument("--canto", type=float, default=1.0)
    ap.add_argument("--cazoletas", type=float, default=100.0)
    ap.add_argument("--codigos", nargs=2, required=True, metavar=("DER", "IZQ"))
    ap.add_argument("--nombre", default="PRUEBA BISAGRA")
    ap.add_argument("-o", "--salida", required=True)
    a = ap.parse_args(argv)

    with open(os.path.join(RAIZ, "herrajes", "medidas.json"), encoding="utf-8") as fh:
        b = json.load(fh)["bisagra"]
    med = f"{a.ancho:g}x{a.alto:g} corte"
    ps = [puerta(a.codigos[0], f"{a.nombre}_Puerta DER ({med})", a.ancho, a.alto, a.canto, a.cazoletas, b, "DER"),
          puerta(a.codigos[1], f"{a.nombre}_Puerta IZQ ({med})", a.ancho, a.alto, a.canto, a.cazoletas, b, "IZQ")]
    os.makedirs(os.path.join(a.salida, "XML3"), exist_ok=True)
    for p in ps:
        write_xml3(p, os.path.join(a.salida, "XML3", p.code + ".xml"))
    with open(os.path.join(a.salida, "HOJA_VERIFICACION.html"), "w", encoding="utf-8") as fh:
        fh.write(hojas.build(ps, a.nombre))
    for p in ps:
        print(p.code, p.name)
        for h in p.holes:
            print(f"   Ø{h.diameter:g} x{h.depth:g}  X {h.x:.2f}  Y {h.y:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
