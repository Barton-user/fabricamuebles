# -*- coding: utf-8 -*-
"""
Marcar Placa — script de Autodesk Fusion para FABRICA MUEBLES.

Pone en las piezas los datos que el archivo de maquina y la lista de corte
necesitan y que NO se pueden deducir del solido: material, textura, veta y
espesor de canto por lado.

COMO SE USA
-----------
Correr el script. NO hace falta seleccionar nada antes: Fusion borra la
seleccion al abrir el dialogo de Scripts, asi que el script muestra el una
lista numerada de las placas y pregunta cuales marcar.

  1)  Que piezas:   "todas"  |  "1,3,5"  |  "1-7"  |  "1-3,8"
      o la palabra MUEBLE para cargar orden / cliente / direccion / ambiente.

  2)  Los datos, en una linea:

          MATERIAL | TEXTURA | VETA | abajo,arriba,izq,der | MUEBLE

      por ejemplo

          multilaminado | 13 gris | VERTICAL | 1,1,1,0 | 00-Doble c/spar01

      Los cantos van en MILIMETROS (0 = sin canto), en el marco de la pieza:
      abajo = Y0, arriba = Y maximo, izq = X0, der = X maximo.
      MUEBLE es el modulo al que pertenece la pieza; sale en la etiqueta.

UN "=" EN CUALQUIER CAMPO DEJA LO QUE LA PIEZA YA TENIA. Sirve para cambiar
solo el material sin pisar los cantos:

    04 nogal | 04 nogal | = | = | =

Tambien vale canto por canto:  1,=,=,0

Si hay algo seleccionado cuando arranca, se usa eso y no se pregunta la lista.
La marca va en el CUERPO, no en el componente: es lo que hay que hacer cuando
varias placas viven en el mismo componente.
"""


import traceback

import adsk.core
import adsk.fusion

GRUPO = "FabricaMuebles"

IGUAL = "="      # en cualquier campo: dejar lo que ya tenia

CAMPOS_PLACA = ("MATERIAL", "TEXTURA", "VETA",
                "CANTO_ABAJO", "CANTO_ARRIBA", "CANTO_IZQ", "CANTO_DER")

CAMPOS_MUEBLE = ("ORDEN", "CLIENTE", "DIRECCION", "AMBIENTE")


# --------------------------------------------------------------------------- #
#  atributos
# --------------------------------------------------------------------------- #

def poner(obj, nombre, valor):
    obj.attributes.add(GRUPO, nombre, str(valor))


def leer(obj, nombre, defecto=""):
    a = obj.attributes.itemByName(GRUPO, nombre)
    return a.value if a is not None and a.value is not None else defecto


# --------------------------------------------------------------------------- #
#  dialogo
# --------------------------------------------------------------------------- #

def pedir(ui, prompt, titulo, defecto):
    """inputBox devuelve (texto, cancelado).

    No damos por sentado el orden: buscamos por tipo. Asi el script no depende
    de la version de la API.
    """
    r = ui.inputBox(prompt, titulo, defecto)
    if not isinstance(r, (tuple, list)):
        r = (r,)
    texto, cancelado = None, False
    for v in r:
        if isinstance(v, bool):
            cancelado = v
        elif isinstance(v, str):
            texto = v
    if cancelado or texto is None:
        return None
    return texto


# --------------------------------------------------------------------------- #
#  seleccion
# --------------------------------------------------------------------------- #

def seleccionados(ui):
    """Devuelve (cuerpos, componentes) segun lo que haya seleccionado."""
    cuerpos, comps, vistos = [], [], set()
    for i in range(ui.activeSelections.count):
        ent = ui.activeSelections.item(i).entity

        body = adsk.fusion.BRepBody.cast(ent)
        if body:
            if body.entityToken not in vistos:
                vistos.add(body.entityToken)
                cuerpos.append(body)
            continue

        comp = None
        occ = adsk.fusion.Occurrence.cast(ent)
        if occ:
            comp = occ.component
        else:
            comp = adsk.fusion.Component.cast(ent)
        if comp and comp.id not in vistos:
            vistos.add(comp.id)
            comps.append(comp)

    return cuerpos, comps


def nombre_de(obj):
    try:
        return obj.name
    except Exception:
        return "?"


# --------------------------------------------------------------------------- #
#  marcado
# --------------------------------------------------------------------------- #

def todos_los_cuerpos(design):
    """Todos los cuerpos solidos y visibles, en orden estable."""
    root = design.rootComponent
    comps = [root]
    vistos = set()
    for i in range(root.allOccurrences.count):
        c = root.allOccurrences.item(i).component
        if c.id not in vistos:
            vistos.add(c.id)
            comps.append(c)
    cuerpos = []
    for comp in comps:
        for j in range(comp.bRepBodies.count):
            b = comp.bRepBodies.item(j)
            if b.isSolid and b.isVisible:
                cuerpos.append(b)
    return cuerpos


def medida(b):
    bb = b.boundingBox
    return "%g x %g x %g" % tuple(sorted(
        (round((bb.maxPoint.x - bb.minPoint.x) * 10, 1),
         round((bb.maxPoint.y - bb.minPoint.y) * 10, 1),
         round((bb.maxPoint.z - bb.minPoint.z) * 10, 1)), reverse=True))


def parsear_indices(texto, total):
    """"todas" | "1,3,5" | "1-7" | "1-3,8"  ->  lista de indices 0-based."""
    t = texto.strip().lower()
    if t in ("todas", "todos", "all", "*"):
        return list(range(total))
    idx = []
    for trozo in t.replace(" ", "").split(","):
        if not trozo:
            continue
        if "-" in trozo:
            a, _, b = trozo.partition("-")
            if not (a.isdigit() and b.isdigit()):
                return None
            for n in range(int(a), int(b) + 1):
                idx.append(n)
        elif trozo.isdigit():
            idx.append(int(trozo))
        else:
            return None
    fuera = [n for n in idx if not 1 <= n <= total]
    if fuera or not idx:
        return None
    vistos, limpio = set(), []
    for n in idx:
        if n not in vistos:
            vistos.add(n)
            limpio.append(n - 1)
    return limpio


def elegir_cuerpos(ui, design):
    """Devuelve (cuerpos, "mueble" | None). Lista numerada, sin depender de la seleccion."""
    cuerpos = todos_los_cuerpos(design)
    if not cuerpos:
        ui.messageBox("No encuentro cuerpos solidos en este diseno.", "Marcar Placa")
        return None, None

    lineas = []
    for n, b in enumerate(cuerpos, 1):
        mat = leer(b, "MATERIAL")
        tex = leer(b, "TEXTURA")
        extra = ("   %s / %s" % (mat, tex)) if (mat or tex) else ""
        lineas.append("%2d  %-16s %-18s%s" % (n, b.name[:16], medida(b), extra))

    texto = pedir(
        ui,
        "%d placas en el diseno:\n\n%s\n\n"
        "Cuales marco?   todas   |   1,3,5   |   1-7   |   1-3,8\n"
        "(o escribi MUEBLE para cargar orden / cliente / direccion / ambiente)"
        % (len(cuerpos), "\n".join(lineas)),
        "Marcar placa — que piezas", "todas")
    if texto is None:
        return None, None
    if texto.strip().lower() in ("mueble", "muebles", "orden"):
        return None, "mueble"

    idx = parsear_indices(texto, len(cuerpos))
    if idx is None:
        ui.messageBox("No entiendo '%s'.\n\nUsa: todas | 1,3,5 | 1-7 | 1-3,8"
                      % texto, "Marcar Placa")
        return None, None
    return [cuerpos[i] for i in idx], None


def marcar_placas(ui, objetos, que):
    ref = objetos[0]
    actual = "%s | %s | %s | %s,%s,%s,%s | %s" % (
        leer(ref, "MATERIAL"), leer(ref, "TEXTURA"), leer(ref, "VETA", "VERTICAL"),
        leer(ref, "CANTO_ABAJO", "0"), leer(ref, "CANTO_ARRIBA", "0"),
        leer(ref, "CANTO_IZQ", "0"), leer(ref, "CANTO_DER", "0"),
        leer(ref, "MUEBLE"))

    texto = pedir(
        ui,
        "MATERIAL | TEXTURA | VETA | cantos abajo,arriba,izq,der | MUEBLE\n"
        "Cantos en mm. MUEBLE es opcional.\n"
        "Un '=' en un campo deja lo que la pieza ya tenia.\n\n"
        "Se marcan %d %s:\n  %s" % (
            len(objetos), que,
            "\n  ".join(nombre_de(o) for o in objetos[:12])
            + ("\n  ..." if len(objetos) > 12 else "")),
        "Marcar placa", actual)
    if texto is None:
        return None

    partes = [p.strip() for p in texto.split("|")]
    while len(partes) < 5:
        partes.append(IGUAL if len(partes) == 4 else "")
    material, textura, veta, mueble = partes[0], partes[1], partes[2], partes[4]

    if veta != IGUAL:
        veta = (veta or "VERTICAL").upper()
        if veta not in ("VERTICAL", "HORIZONTAL"):
            ui.messageBox("VETA tiene que ser VERTICAL u HORIZONTAL, vino '%s'." % veta,
                          "Marcar Placa")
            return None

    if partes[3] == IGUAL:
        cantos = [IGUAL] * 4
    else:
        cantos = [c.strip() or "0" for c in partes[3].split(",")]
        while len(cantos) < 4:
            cantos.append("0")
        cantos = cantos[:4]
        for c in cantos:
            if c == IGUAL:
                continue
            try:
                float(c)
            except ValueError:
                ui.messageBox("Los cantos van en milimetros. No entiendo '%s'." % c,
                              "Marcar Placa")
                return None

    valores = list(zip(CAMPOS_PLACA + ("MUEBLE",),
                       (material, textura, veta) + tuple(cantos) + (mueble,)))
    for o in objetos:
        poner(o, "TIPO", "PLACA")
        for k, v in valores:
            if v == IGUAL:          # "=" -> se deja lo que ya tenia la pieza
                continue
            poner(o, k, v)

    def muestra(v):
        return "(sin cambio)" if v == IGUAL else (v or "(vacio)")

    return "%d %s marcada(s):\n\n  material : %s\n  textura  : %s\n  veta     : %s\n" \
           "  cantos   : abajo %s / arriba %s / izq %s / der %s\n  mueble   : %s" % (
               len(objetos), que, muestra(material), muestra(textura), muestra(veta),
               muestra(cantos[0]), muestra(cantos[1]),
               muestra(cantos[2]), muestra(cantos[3]), muestra(mueble))


def marcar_orden(ui, root):
    actual = "%s | %s | %s | %s" % tuple(leer(root, c) for c in CAMPOS_MUEBLE)
    texto = pedir(
        ui,
        "Sin piezas seleccionadas: se marcan los datos del mueble.\n\n"
        "ORDEN | CLIENTE | DIRECCION | AMBIENTE",
        "Datos del mueble", actual)
    if texto is None:
        return None
    partes = [p.strip() for p in texto.split("|")]
    while len(partes) < 4:
        partes.append("")
    for nombre, valor in zip(CAMPOS_MUEBLE, partes):
        if valor == IGUAL:
            continue
        poner(root, nombre, valor)
    return "Datos del mueble guardados:\n\n  %s" % " | ".join(
        p or "(vacio)" for p in partes[:4])


# --------------------------------------------------------------------------- #

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox("Abri un diseno de Fusion antes de correr el script.",
                          "Marcar Placa")
            return

        cuerpos, comps = seleccionados(ui)

        if cuerpos:
            msg = marcar_placas(ui, cuerpos, "pieza(s)")
        elif comps:
            msg = marcar_placas(ui, comps, "componente(s)")
        else:
            # Fusion borra la seleccion al abrir el dialogo de Scripts, asi que
            # este es el camino normal, no la excepcion.
            elegidos, modo = elegir_cuerpos(ui, design)
            if modo == "mueble":
                msg = marcar_orden(ui, design.rootComponent)
            elif elegidos:
                msg = marcar_placas(ui, elegidos, "pieza(s)")
            else:
                return

        if msg:
            ui.messageBox(msg, "Marcar Placa")

    except Exception:
        if ui:
            ui.messageBox("Fallo:\n%s" % traceback.format_exc(), "Marcar Placa")
