# -*- coding: utf-8 -*-
"""
alacena_spar — receta de la "Alacena Spar" (alacena sobre campana) de PRUEBA 1,
rehecha desde el diseno de GuiGui (render.json del 01/10/2026) con las
correcciones para fabricar sin GuiGui.

    python3 recetas/alacena_spar.py        -> recetas/salida/ALACENA-SPAR/

Usa las herramientas de cocina01 (Placa, tres_en_uno, bisagras, chequeos, a_json).

Decisiones de Pato del 01/10/2026 sobre el diseno de GuiGui:
  * alto real 844,47 -> 845 (laterales 827, listones 98, puertas 390 / 376)
  * tapa inferior: excentricas ARRIBA (cara de adentro) junto con la ranura del
    fondo -> sale de una sola cara; los listones se unen solo a los laterales
  * LED: ranura 10x10 en la cara de ABAJO de la tapa inferior, a 60 del frente
    (la de GuiGui era 9x9 arriba del techo, pasante de lado a lado)
  * puerta de arriba rebatible: 2 bisagras de cazoleta en el canto superior con
    base en el techo + piston a gas por lado, atornillado a mano (sin CNC)
Ademas, decidido por Claude (avisado):
  * cada pieza con TODO su mecanizado en la cara A (salvo la LED en la B, 10 de
    ancho = T11) -> nada depende del paquete de abajo
  * tornillos de bisagra y de base en O5 (la maquina no tiene O6 y con O6 el
    software crashea); se vuelve a 6 cuando se monte la mecha
  * canto 1 mm tambien abajo de laterales y listones (se ven desde abajo)

Mundo (mm): X a lo ancho (0 = lado derecho de quien mira), Y desde la pared
(0) hacia el frente (400), Z desde el borde de abajo del mueble (0) hacia arriba.
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import cocina01 as C  # noqa: E402

SALIDA = os.path.join(AQUI, "salida", "ALACENA-SPAR")
C.ORDEN = "PRUEBA1-SPAR"
C.CLIENTE = "PRUEBA"
C.AMBIENTE = "ALACENA-SPAR"
C.PREFIJO_CODIGO = "999261001"
C.TOR = dict(C.TOR, d=5.0)
C.BASE = dict(C.BASE, d=5.0)

MUEBLE = "Alacena Spar"
GRIS, PET, BLANCO5 = "GRIS 18", "PET GRIS 18", "BLANCO 5"
MEL, MPET = "Melamina", "PET"

T = 18.0
W, D, H = 600.0, 400.0, 845.0
H_LISTON = 98.0                  # bajo la tapa inferior (GuiGui 97,87)
Z_PUERTA0 = 74.5                 # borde de abajo de las puertas (GuiGui 74,37)
H_PUERTA_ABAJO = 390.0
LUZ, JUNTA = 1.5, 3.0
BP_X = 20.5                      # centro de la ranura del fondo, desde atras (GuiGui)
BP_ANCHO, BP_PROF = 6.0, 6.0
ESTANTE_Y0 = 23.0                # el estante arranca delante del fondo (GuiGui)
LED_DESDE_FRENTE, LED_MARGEN, LED_ANCHO, LED_PROF = 60.0, 20.0, 10.0, 10.0


def armar():
    P = C.mueble(MUEBLE)
    pc = lambda nm, x0, x1, y0, y1, z0, z1, A, X, tex, **kw: C.placa_caja(
        MUEBLE, nm, x0, x1, y0, y1, z0, z1, A, X, tex, **kw)
    zt = H - T
    # ---- cuerpo (cara A = la de adentro en todas)
    techo = pc("Techo", 0, W, 0, D, zt, H, "-Z", "+Y", GRIS, cantos=("+Y", "+X", "-X"))
    ld = pc("Lateral der", 0, T, 0, D, 0, zt, "+X", "+Y", GRIS, cantos=("+Y", "-Z"))
    li = pc("Lateral izq", W - T, W, 0, D, 0, zt, "-X", "-Y", GRIS, cantos=("+Y", "-Z"))
    ti = pc("Tapa inferior", T, W - T, 0, D, H_LISTON, H_LISTON + T, "+Z", "+X", GRIS, cantos=("+Y",))
    lf = pc("Liston frente", T, W - T, D - T, D, 0, H_LISTON, "-Y", "+X", GRIS, cantos=("-Z",))
    la = pc("Liston atras", T, W - T, 0, T, 0, H_LISTON, "+Y", "-X", GRIS, cantos=("-Z",))
    # estante fijo centrado en la junta entre la puerta de abajo y la de arriba
    zj = Z_PUERTA0 + H_PUERTA_ABAJO + JUNTA / 2.0
    es = pc("Estante", T, W - T, ESTANTE_Y0, D, zj - T / 2.0, zj + T / 2.0, "-Z", "+X", GRIS, cantos=("+Y",))
    # fondo de 5 en las ranuras (5 adentro de cada ranura de 6)
    fo = pc("Fondo", T - 5, W - T + 5, BP_X - 2.5, BP_X + 2.5, H_LISTON + T - 5, zt + 5, "+Y", "-X",
            BLANCO5, rol="FONDO", material=MEL)
    fo.T = 5.0
    P += [techo, ld, li, ti, lf, la, es, fo]
    # ---- ranuras del fondo (cara A)
    # techo: X local = profundidad, Y local = ancho; cortada 12,85 antes de los costados (se ven)
    techo.ranura(BP_X, 12.85, BP_X, W - 12.85, BP_ANCHO, BP_PROF, "A", "BP")
    # laterales: desde donde apoya el fondo (5 abajo de la tapa inferior) hasta arriba
    yb = H_LISTON + T - 5 - 1.0
    ld.ranura(BP_X, yb, BP_X, ld.H, BP_ANCHO, BP_PROF, "A", "BP")
    li.ranura(li.W - BP_X, yb, li.W - BP_X, li.H, BP_ANCHO, BP_PROF, "A", "BP")
    ti.ranura(0, BP_X, ti.W, BP_X, BP_ANCHO, BP_PROF, "A", "BP")
    # ---- LED 10x10 en la cara B (abajo) de la tapa inferior
    yl = ti.H - LED_DESDE_FRENTE
    x1, x2 = LED_MARGEN, ti.W - LED_MARGEN
    ti.ranura(x1, yl, x2, yl, LED_ANCHO, LED_PROF, "B", "lightSlot")
    C.herraje(MUEBLE, "Tira LED %d" % int(round(x2 - x1)), ti.mundo(x1, yl, -ti.T), ti.vec(0, 0, 1), ti.ex,
              "led", largo=x2 - x1)
    # ---- uniones 3 en 1 (excentrica siempre en la cara A = adentro)
    for lat in (ld, li):
        C.tres_en_uno(lat, techo, "A")
        C.tres_en_uno(ti, lat, "A")
        C.tres_en_uno(es, lat, "A")
        C.tres_en_uno(lf, lat, "A")
        C.tres_en_uno(la, lat, "A")
    # ---- puertas PET (cara A = interior)
    cant = ("+X", "-X", "+Z", "-Z")
    xm = W / 2.0
    za, zb = Z_PUERTA0, Z_PUERTA0 + H_PUERTA_ABAJO
    pdr = pc("Puerta der", LUZ, xm - JUNTA / 2, D, D + T, za, zb, "-Y", "+X", PET, rol="PUERTA",
             cantos=cant, material=MPET)
    piz = pc("Puerta izq", xm + JUNTA / 2, W - LUZ, D, D + T, za, zb, "-Y", "+X", PET, rol="PUERTA",
             cantos=cant, material=MPET)
    # rebatible: X local hacia abajo (x=0 = canto de arriba, el de bisagras), Y local a lo ancho
    psu = pc("Puerta rebatible", LUZ, W - LUZ, D, D + T, zb + JUNTA, H - LUZ, "-Y", "-Z", PET, rol="PUERTA",
             cantos=cant, material=MPET)
    P += [pdr, piz, psu]
    C.bisagras(pdr, ld, "IZQ", "DER", "A")
    C.bisagras(piz, li, "DER", "IZQ", "A")
    C.bisagras(psu, techo, "IZQ", "DER", "A")
    C.AVISOS.append("Puerta rebatible: lleva 2 pistones a gas (Bronze), uno por lado, atornillados a mano. "
                    "No tienen agujeros de CNC ni estan dibujados. Fuerza a definir (puerta PET 597x376x18).")
    C.AVISOS.append("Colgadores de alacena: no estan en el diseno ni perforados.")
    C.AVISOS.append("LED: falta definir por donde sale el cable (no hay agujero pasante).")
    C.AVISOS.append("Tornillos de bisagra y de base en O5 (no hay O6 en la maquina).")
    return P


def main():
    armar()
    malos = C.chequeos()
    # chequeo propio: ranura de una cara contra agujero de la otra que se pisan en espesor
    for _, placas in C.MUEBLES:
        for p in placas:
            for r in p.ranuras:
                xa, xb = sorted((r["x1"], r["x2"])); ya, yb = sorted((r["y1"], r["y2"]))
                w = r["ancho"] / 2.0
                if xa == xb: xa, xb = xa - w, xb + w
                else: ya, yb = ya - w, yb + w
                for h in p.agujeros:
                    if h["cara"] == r["cara"]:
                        continue
                    rr = h["d"] / 2.0
                    if xa - rr < h["x"] < xb + rr and ya - rr < h["y"] < yb + rr and r["prof"] + h["prof"] > p.T:
                        malos.append("%s: O%g cara %s choca con ranura %s cara %s"
                                     % (p.nombre, h["d"], h["cara"], r["sym"], r["cara"]))
    modelo, exp = C.a_json()
    modelo["referencia"] = []
    os.makedirs(SALIDA, exist_ok=True)
    with open(os.path.join(SALIDA, "modelo.json"), "w", encoding="utf-8") as fh:
        json.dump(modelo, fh, ensure_ascii=False, indent=1)
    with open(os.path.join(SALIDA, "piezas_receta.json"), "w", encoding="utf-8") as fh:
        json.dump(exp, fh, ensure_ascii=False, indent=1)
    cuenta = Counter(h["nombre"].split(" base")[0] if h["nombre"].startswith("Bisagra") else
                     ("Tira LED" if h["nombre"].startswith("Tira LED") else h["nombre"]) for h in C.HERRAJES)
    lin = ["ALACENA SPAR — receta (%s)" % C.ORDEN, ""]
    for nombre, placas in C.MUEBLES:
        for p in placas:
            caras = sorted(set([h["cara"] for h in p.agujeros] + [r["cara"] for r in p.ranuras]))
            lin.append("    %-13s %-17s %6.1f x %6.1f x %4.1f  %-11s ag %2d canto %d ran %d  caras %s"
                       % (p.codigo, p.nombre, p.W, p.H, p.T, p.textura, len(p.agujeros), len(p.canto),
                          len(p.ranuras), "".join(caras) or "-"))
    lin += ["", "HERRAJES:"] + ["    %-26s %3d" % kv for kv in sorted(cuenta.items())] + [""]
    lin += ["AVISO: " + a for a in C.AVISOS] + ["ERROR: " + m for m in malos]
    with open(os.path.join(SALIDA, "resumen.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lin) + "\n")
    print("\n".join(lin))
    return 1 if malos else 0


if __name__ == "__main__":
    sys.exit(main())
