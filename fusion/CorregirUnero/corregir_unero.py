# -*- coding: utf-8 -*-
"""
corregir_unero — COCINA MLV (orden 30346169), union entre 01-Unero y 02-Unero.

El problema (visto en el render.json de GuiGui, 27/09/2026): los dos tramos del
unero se encuentran punta con punta en X = 350 (sobre el encuentro Bandejero /
Horno y anafe) y GuiGui le puso a CADA punta un 3 en 1 completo (excentrica O15
+ perno O8) apuntando al otro tramo, sin receptor O10 en ninguno. Son 4 pernos
que no se pueden armar (los unicos 4 de 294 que no caen en un receptor).

La correccion (mismo criterio que la Cajonera, donde GuiGui lo hace bien):
  - en las 4 piezas del unero se sacan la excentrica y el perno de la punta del
    encuentro, y se pone un receptor O10 donde entra el perno del lateral;
  - en los dos laterales de abajo (Bandejero Right board01 y Horno y anafe Left
    board01) se agrega el 3 en 1 en la escotadura del unero, igual al de la
    Cajonera: O15 en (555,677) con O8 desde el escalon y=710, y O15 en (497,754)
    con O8 desde el canto x=530. La excentrica va en la cara interior (la de los
    otros receptores del lateral).

Las coordenadas son las del marco de ArmarDesdeRender (placa acostada, mm).
"""

LAT_BANDEJERO = "7432755750054"   # 00-Bandejero Right board01
LAT_HORNO = "7432755750177"       # 00-Horno y anafe Left board01
U01_RP = "7432755751044"          # 01-Unero Roof plate01 (frente, 52 x 280.93)
U01_VP = "7432755751051"          # 01-Unero Vertical Partition01 (piso, 50 x 280.93)
U02_RP = "7432755751020"          # 02-Unero Roof plate01 (52 x 2200)
U02_VP = "7432755751037"          # 02-Unero Vertical Partition01 (50 x 2200)
CODIGOS = [LAT_BANDEJERO, LAT_HORNO, U01_RP, U01_VP, U02_RP, U02_VP]


def _h(x, y, side, d, prof):
    return {"x": float(x), "y": float(y), "side": side, "d": float(d), "prof": float(prof), "sym": "3in1Lock"}


def _quitar(pz, y_punta, x_cam, y_cam, log):
    antes_s, antes_h = len(pz.sholes), len(pz.holes)
    pz.sholes = [h for h in pz.sholes
                 if not (abs(h["d"] - 8.0) < 0.5 and h["side"] in (2, 4) and abs(h["y"] - y_punta) < 0.5)]
    pz.holes = [h for h in pz.holes
                if not (abs(h["d"] - 15.0) < 0.5 and abs(h["x"] - x_cam) < 0.5 and abs(h["y"] - y_cam) < 0.5)]
    q = (antes_s - len(pz.sholes), antes_h - len(pz.holes))
    if log:
        log("  %s %s: saco %d perno(s) O8 y %d excentrica(s) O15" % (pz.codigo, pz.nombre, q[0], q[1]))
    if q != (1, 1):
        raise RuntimeError("%s: esperaba sacar 1 perno y 1 excentrica, saque %s" % (pz.codigo, q))


def corregir(piezas, log=None):
    """piezas = dict codigo -> Pieza (de ArmarDesdeRender.leer_render). Modifica en el lugar."""
    T = piezas
    # --- unero 01 (X 69..350): la punta del encuentro es y = H
    p = T[U01_RP]; _quitar(p, p.H, 26.0, p.H - 33.0, log); p.holes.append(_h(26.0, p.H - 9.0, 1, 10, 11))
    p = T[U01_VP]; _quitar(p, p.H, 25.0, p.H - 33.0, log); p.holes.append(_h(25.0, p.H - 9.0, -1, 10, 11))
    # --- unero 02 (X 350..2550): la punta del encuentro es y = 0
    p = T[U02_RP]; _quitar(p, 0.0, 26.0, 33.0, log); p.holes.append(_h(26.0, 9.0, 1, 10, 11))
    p = T[U02_VP]; _quitar(p, 0.0, 25.0, 33.0, log); p.holes.append(_h(25.0, 9.0, -1, 10, 11))
    # --- laterales: 3 en 1 en la escotadura, excentrica en la cara interior
    for cod, side in ((LAT_BANDEJERO, -1), (LAT_HORNO, 1)):
        p = T[cod]
        p.holes.append(_h(555.0, 677.0, side, 15, 13.5))
        p.holes.append(_h(497.0, 754.0, side, 15, 13.5))
        p.sholes.append(_h(555.0, 710.0, 2, 8, 33))
        p.sholes.append(_h(530.0, 754.0, 3, 8, 33))
        if log:
            log("  %s %s: agrego 2 excentricas O15 (cara %d) y 2 pernos O8" % (cod, p.nombre, side))
    for c in (U01_RP, U01_VP, U02_RP, U02_VP):
        if log:
            log("  %s %s: agrego 1 receptor O10" % (c, T[c].nombre))
    return T
