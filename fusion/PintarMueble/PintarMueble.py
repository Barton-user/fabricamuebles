# -*- coding: utf-8 -*-
"""
Pintar Mueble — script de Autodesk Fusion para FABRICA MUEBLES.

Le pone a cada placa el color de su TEXTURA, para que el mueble se vea como en
GuiGui en vez de todo gris.

El dato sale del atributo TEXTURA que carga MarcarPlaca. No cambia nada de la
geometria ni de los archivos de maquina: es solo apariencia.

Correr el script y listo, no pregunta nada.

PARA AGREGAR UN MATERIAL NUEVO
------------------------------
Sumar una linea a PALETA. El valor puede ser:

    (r, g, b)            un color liso, 0..255
    "Walnut"             el nombre de una apariencia de la biblioteca de Fusion

La clave se busca por PEDAZO de texto, sin distinguir mayusculas, asi que
"nogal" alcanza para "04 nogal brillante".
"""

import traceback

import adsk.core
import adsk.fusion

GRUPO = "FabricaMuebles"

# apariencias de madera que trae Fusion: Oak, Oak - Semigloss, Walnut, Cherry, Pine
PALETA = [
    # --- lo que usan los pedidos reales ---
    ("玛雅灰", (146, 146, 148)),          # 13玛雅灰  gris maya
    ("暖白", (246, 241, 229)),            # 01暖白  blanco calido
    ("拉丝胡桃", "Walnut"),           # 拉丝胡桃  nogal cepillado
    ("白麻面", (234, 231, 223)),          # 白麻面  blanco lino
    # --- nombres en castellano, por comodidad ---
    ("nogal", "Walnut"),
    ("roble", "Oak"),
    ("cerezo", "Cherry"),
    ("pino", "Pine"),
    ("blanco", (240, 239, 235)),
    ("negro", (38, 38, 40)),
    ("gris", (146, 146, 148)),
    ("beige", (214, 201, 178)),
    ("arena", (206, 190, 164)),
]

# si la textura no figura en la paleta
POR_DEFECTO = (205, 192, 170)          # melamina clara
BASE_COLOR = "Plastic - Matte (White)"  # de donde se copian los colores lisos


def leer(obj, nombre, defecto=""):
    a = obj.attributes.itemByName(GRUPO, nombre)
    return a.value if a is not None and a.value is not None else defecto


def _buscar(coleccion, nombre):
    """itemByName revienta si el nombre no esta, en vez de devolver None."""
    try:
        a = coleccion.itemByName(nombre)
        if a is not None:
            return a
    except Exception:
        pass
    for i in range(coleccion.count):
        if coleccion.item(i).name == nombre:
            return coleccion.item(i)
    return None


def _de_biblioteca(app, design, nombre):
    """Trae una apariencia de las bibliotecas al diseno (o la reusa)."""
    ya = _buscar(design.appearances, nombre)
    if ya is not None:
        return ya
    for i in range(app.materialLibraries.count):
        lib = app.materialLibraries.item(i)
        try:
            aps = lib.appearances
        except Exception:
            continue
        a = _buscar(aps, nombre)
        if a is not None:
            try:
                return design.appearances.addByCopy(a, nombre)
            except Exception:
                pass
    return None


def _color(app, design, rgb, etiqueta):
    """Una apariencia lisa del color pedido, copiando la base y pintandola."""
    nombre = "FM %s" % etiqueta
    ya = _buscar(design.appearances, nombre)
    if ya is not None:
        return ya
    base = _de_biblioteca(app, design, BASE_COLOR)
    if base is None:
        return None
    nueva = design.appearances.addByCopy(base, nombre)
    for k in range(nueva.appearanceProperties.count):
        p = nueva.appearanceProperties.item(k)
        if p.objectType.endswith("ColorProperty") and p.name == "Color":
            try:
                p.value = adsk.core.Color.create(rgb[0], rgb[1], rgb[2], 255)
            except Exception:
                pass
            break
    return nueva


def apariencia_de(app, design, textura, material, cache):
    clave = ("%s %s" % (textura, material)).strip().lower()
    for pedazo, valor in PALETA:
        if pedazo.lower() in clave:
            break
    else:
        pedazo, valor = "(sin textura)", POR_DEFECTO
    if pedazo in cache:
        return cache[pedazo], pedazo
    ap = _de_biblioteca(app, design, valor) if isinstance(valor, str) \
        else _color(app, design, valor, pedazo)
    cache[pedazo] = ap
    return ap, pedazo


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox("Abri un diseno de Fusion antes de correr el script.",
                          "Pintar Mueble")
            return

        root = design.rootComponent
        comps = [root] + [root.allOccurrences.item(i).component
                          for i in range(root.allOccurrences.count)]
        vistos, cache, cuenta, sin_dato = set(), {}, {}, 0

        for comp in comps:
            if comp.id in vistos:
                continue
            vistos.add(comp.id)
            for j in range(comp.bRepBodies.count):
                b = comp.bRepBodies.item(j)
                tipo = str(leer(b, "TIPO") or leer(comp, "TIPO")).strip().upper()
                if tipo and tipo != "PLACA":
                    continue                      # los herrajes ya vienen metalicos
                tex = str(leer(b, "TEXTURA") or leer(comp, "TEXTURA"))
                mat = str(leer(b, "MATERIAL") or leer(comp, "MATERIAL"))
                if not tex and not mat:
                    sin_dato += 1
                ap, etiqueta = apariencia_de(app, design, tex, mat, cache)
                if ap is None:
                    continue
                try:
                    b.appearance = ap
                    cuenta[etiqueta] = cuenta.get(etiqueta, 0) + 1
                except Exception:
                    pass

        if not cuenta:
            ui.messageBox(
                "No encontre placas para pintar.\n\nEl script pinta los cuerpos "
                "marcados TIPO=PLACA, o los que no tienen TIPO. Los herrajes los "
                "deja como estan.", "Pintar Mueble")
            return

        detalle = "\n".join("  %-22s %d placa(s)" % (k, v)
                            for k, v in sorted(cuenta.items()))
        extra = ("\n\n%d placa(s) sin material ni textura cargados: van con el "
                 "color por defecto. Corre MarcarPlaca para darles el suyo."
                 % sin_dato) if sin_dato else ""
        ui.messageBox("Pintado por textura:\n\n%s%s" % (detalle, extra),
                      "Pintar Mueble")

    except Exception:
        if ui:
            ui.messageBox("Fallo:\n%s" % traceback.format_exc(), "Pintar Mueble")
