# -*- coding: utf-8 -*-
"""
CorregirUnero — aplica corregir_unero.py sobre el diseño COCINA MLV abierto.

Rehace las 6 placas afectadas con el mismo constructor de ArmarDesdeRender
(cuerpo_placa) y los agujeros corregidos, conserva nombre, atributos y
apariencia del cuerpo, borra los herrajes dibujados que sobran (excéntrica y
perno de las puntas del unero) y dibuja los nuevos. Log en CorregirUnero.log.
"""
import adsk.core, adsk.fusion, importlib.util, os, copy, traceback, time

AQUI = "/Users/patriciokeogan/Documents/Claude/Projects/FABRICA MUEBLES/fusion/CorregirUnero"
BASE = os.path.dirname(os.path.dirname(AQUI))
ADR_PATH = os.path.join(BASE, "fusion", "ArmarDesdeRender", "ArmarDesdeRender.py")
RENDER = os.path.join(BASE, "referencia", "GUIGUI_MCP", "207960w31789042536993.render.json")
LOG = os.path.join(AQUI, "CorregirUnero.log")


def _mod(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class _Tmp(object):
    pass


def run(context=None):
    f = open(LOG, "w", encoding="utf-8")
    def L(s):
        f.write(s + "\n"); f.flush()
    t0 = time.time()
    try:
        ADR = _mod("ArmarDesdeRender", ADR_PATH)
        CU = _mod("corregir_unero", os.path.join(AQUI, "corregir_unero.py"))
        app = adsk.core.Application.get()
        design = adsk.fusion.Design.cast(app.activeProduct)
        root = design.rootComponent
        tbm = adsk.fusion.TemporaryBRepManager.get()
        muebles, d = ADR.leer_render(RENDER, None, None)
        T = {pz.codigo: pz for mu in muebles for pz in mu["piezas"] if pz.codigo in CU.CODIGOS}
        antes = {c: (copy.deepcopy(T[c].holes), copy.deepcopy(T[c].sholes)) for c in CU.CODIGOS}
        CU.corregir(T, L)
        L("leido y corregido (%.1f s)" % (time.time() - t0))

        comps = {}
        for i in range(design.allComponents.count):
            c = design.allComponents.item(i)
            if c.partNumber in CU.CODIGOS:
                comps[c.partNumber] = c
        faltan = [c for c in CU.CODIGOS if c not in comps]
        if faltan:
            raise RuntimeError("no encuentro los componentes %s" % faltan)
        ap_metal = ADR._ph()._apariencia_metal()

        for cod in CU.CODIGOS:
            pz = T[cod]; comp = comps[cod]
            occs = root.allOccurrencesByComponent(comp)
            if occs.count != 1:
                raise RuntimeError("%s: %d ocurrencias" % (cod, occs.count))
            occ = occs.item(0)
            occ_m = occ.assemblyContext
            m = occ.transform2
            # 1) placa nueva
            viejo = comp.bRepBodies.item(0)
            attrs = [(a.groupName, a.name, a.value) for a in viejo.attributes]
            ap, nombre, vol0 = viejo.appearance, viejo.name, viejo.volume
            nuevo = comp.bRepBodies.add(ADR.cuerpo_placa(tbm, pz, L))
            nuevo.name = nombre
            for g, n, v in attrs:
                nuevo.attributes.add(g, n, v)
            if ap is not None:
                nuevo.appearance = ap
            viejo.deleteMe()
            L("%s %s/%s: placa rehecha, volumen %.3f -> %.3f cm3" % (cod, pz.mueble, pz.nombre, vol0, nuevo.volume))
            # 2) herrajes dibujados que sobran
            h0, s0 = antes[cod]
            quit_h = [h for h in h0 if h not in pz.holes]
            quit_s = [h for h in s0 if h not in pz.sholes]
            puntos = []
            for h in quit_s:
                bx, by = ADR.boca_canto(pz, h["x"], h["y"], h["side"])
                puntos.append(("Perno O8 x 33", (bx, by, -pz.T / 2.0)))
            for h in quit_h:
                z0, sg = ADR.z_cara(pz, h["side"])
                puntos.append(("Excentrica O15", (h["x"], h["y"], z0)))
            for nom, (x, y, z) in puntos:
                p = adsk.core.Point3D.create(x * 0.1, y * 0.1, z * 0.1)
                p.transformBy(m)
                borrado = False
                hijos = occ_m.childOccurrences
                for i in range(hijos.count - 1, -1, -1):
                    o = hijos.item(i)
                    if o.component.name != nom:
                        continue
                    if o.transform2.translation.asPoint().distanceTo(p) < 0.05:
                        o.deleteMe(); borrado = True
                        break
                L("   herraje %s en %s: %s" % (nom, (round(x, 1), round(y, 1)), "borrado" if borrado else "NO ENCONTRADO"))
            # 3) herrajes nuevos
            tmp = _Tmp()
            tmp.W, tmp.H, tmp.T = pz.W, pz.H, pz.T
            tmp.holes = [h for h in pz.holes if h not in h0]
            tmp.sholes = [h for h in pz.sholes if h not in s0]
            n = ADR.poner_3en1(design, occ_m, tmp, occ, ap_metal, L)
            L("   dibujados %d herrajes nuevos" % n)
        L("LISTO en %.1f s" % (time.time() - t0))
    except Exception:
        L("ERROR:\n" + traceback.format_exc())
    finally:
        f.close()
