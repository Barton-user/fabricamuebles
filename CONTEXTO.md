# FÁBRICA MUEBLES — Contexto del proyecto

_Leiten Com · Pato · Última actualización: **18/10/2026**_

> **Cómo se usa este archivo.** Es lo único que hay que leer al empezar una conversación.
> Dice **qué es cierto hoy**. El detalle de cada tema está en `docs/` (mapa en §7) y la historia
> de cómo se llegó, en `BITACORA.md`, que **no se lee al arrancar**.
> Reglas para mantenerlo en §8.

---

## 1. Qué es el proyecto

Una línea de producción de **muebles de placa** (melamina 18, fondos 5) que se entregan
desarmados: diseño → despiece → corte → etiquetado → perforado → cantos → armado.

**El objetivo, en tres frases:**

1. **Fabricar todo lo modelado en GuiGui**, camino 100 % funcional.
2. **Modelar en Fusion y fabricar con nuestras máquinas**, sin GuiGui, 100 % funcional.
3. **Tienda online** con ~10 modelos, visor y configurador 3D (medidas generales y alguna opción,
   sin salir de la estandarización). Pedido pagado → se genera toda la documentación del mueble.

**"100 % funcional"** = programas de máquina + lista de corte + **etiquetas** + **manual de armado
de 1-2 hojas**. Ese conjunto es el **paquete de producción**.

**La idea que ordena todo: un motor, tres entradas.** `etapa2/` (el modelo `Panel` y sus
escritores) es el motor. GuiGui (`guigui.py`), Fusion (`fusion_json.py`) y las **recetas** en
código (`recetas/`) son tres formas de llenar `Panel`. Lo que falta (etiquetas, manual, precios)
se construye una vez sobre `Panel` y sirve para las tres.

- **GuiGui: no invertir más.** Queda como respaldo y como fuente de diseños de la diseñadora.
- **Fusion es la columna vertebral** para diseñar y validar.
- **El configurador NO usa Fusion en tiempo de ejecución**: cada modelo es una receta paramétrica
  en Python; Fusion sirve para validarla (receta vs. sólido, "oráculo").

¿Por qué reemplazar GuiGui? UI rota, configuración atada a un servidor en China, SMS en cada
cambio, bloqueos arbitrarios. Si nuestros archivos son iguales a los suyos, las máquinas no se
enteran (especificación en `docs/FORMATOS.md`).

---

## 2. Dónde estamos (01/10/2026)

| Etapa | Qué | Estado |
|---|---|---|
| **0 · Sobre metal** | probar en las máquinas lo que sólo se contesta ahí | 🟡 casi: la perforadora lee **KDTXml** y mecaniza; Ø35 resuelta. Faltan las pruebas de `MAÑANA_EN_LA_MAQUINA.md` (§5) |
| **1 · Paquete de producción** | etiquetas propias, manual de armado, ranura de canto, **fabricar y armar PRUEBA 1** | 🟡 en curso: Alacena Spar (PRUEBA 1) perforada; `etapa2/etiquetas.py` funciona por los dos caminos; AutoCUT sigue mal mapeado |
| **2 · Estresar Fusion** | 2-3 muebles distintos de cero, cada herraje nuevo **medido** | 🟡 **COCINA-01 = la cocina de JUJUY** (Fusion: documento `COCINA-01`, proyecto/carpeta `cocina`, guardado por Pato el 18/10 con la versión final). Rediseñada 18/10 como el render: vitrinas de marco de madera maciza con Minifix, A2 dos hojas rebatibles sin piso con escurreplatos sobre la bacha, A4 mueble campana oculta (SDC-100), bacha Tawak 55, tiradores de cobre, travesaños para colgar, viga (2160/120) y columna (60×180) resueltas; 108 placas, 108/108 receta = sólido. Sin fabricar. Detalle en `docs/FUSION_RECETAS.md` §25.2 y `fusion/EXPORT_COCINA-01/LEEME.md` |
| **3 · Recetas** | los 10 modelos como código paramétrico + CLI | 🟡 empezada: `recetas/cocina01.py`, `recetas/alacena_spar.py` |
| 4 · Visor / configurador 3D | three.js sobre las recetas | ⬜ no empezar antes de la 3 |
| 5 · Tienda y disparo | catálogo, Mercado Pago, pedido → paquete | ⬜ |

**Lo que anda hoy:** generador propio validado byte a byte contra Bluen (`.ban`, `.mpr`, XML1,
XML3, lista de corte); camino Fusion → archivos (`fusion/ExportarPiezas`, `fusion/ArmarReceta`);
recetas → Fusion → archivos con control 1:1; perforadora mecanizando nuestros XML3; web de
curvado por ranuras (`curvado/`); **manual de armado de 2 hojas desde la receta**
(`etapa2/manual_armado.py modelo.json -o manual.pdf`: explotada numerada, piezas con código de
etiqueta, herrajes, pasos dibujados; cajones como sub-armado). Hechos: Alacena Spar y los 10
muebles de COCINA-01. ⚠️ Los esquineros (piezas a 45°) salen con aviso: revisar los pasos a mano.

---

## 3. Las máquinas

| Equipo | Modelo | Rol | Software | Consume | Documento |
|---|---|---|---|---|---|
| Diseño | GuiGui 柜柜 v5.0.0.4 (Mac) + nube **bluen.cn** | diseño paramétrico y despiece | — | — | `docs/GUIGUI.md` |
| Diseño | **Fusion** | diseño propio | scripts en `fusion/` | — | `docs/FUSION_RECETAS.md` |
| Optimizador | **AutoCUT** (PC de la sierra) | optimiza el corte, imprime etiquetas | Windows | lista de corte Excel/CSV | `docs/SIERRA_AUTOCUT.md` |
| Sierra | **HP280** (Huahua) | corte recto | control Huahua | `.CUT` de AutoCUT | `docs/SIERRA_AUTOCUT.md` |
| Router | **SKG-912MZY** (Huahua) | nesting, contornos, almacén de 12 | Syntec + interfaz Huahua | `.nc` (Z0 = mesa, ver doc) | **`docs/ROUTER_SKG912.md`** · encendido y con homing; primera prueba lista en `PENDRIVE/7_ROUTER_PRUEBA/` |
| Perforadora | **SKH-612HS** (Huahua) | agujeros 6 caras, ranuras, cazoletas | **MH2026** + CncMon32 | **XML3 = KDTXml** (1 archivo por pieza, nombre = código de barras) | **`docs/PERFORADORA_SKH612.md`** |
| Pegadora de cantos | **HH-509R** | cantos | manual | la etiqueta | manual en `instructivo/manuales/` |
| Etiquetas | **AIBAO BC-80152T** | térmicas con QR | driver Windows, en la PC de la sierra | — | — |

Manuales: perforadora `User Manual_SKH-612 Series_260706_115944.pdf` (raíz); sierra, AutoCUT,
pegadora y **router (manual + guía de operación Syntec)** en `instructivo/manuales/`. Capturas explicadas de la perforadora: `instructivo/INDICE.md`.

**Flujo:**

```
GuiGui ──(Mass production.json / render.json)──┐
Fusion ──(fusion/ExportarPiezas)───────────────┼──► etapa2/  ──►  lista de corte → AutoCUT → SIERRA → etiquetas
recetas/ ──(fusion/ArmarReceta)────────────────┘      │
                                                      └──►  XML3 (KDTXml) por pieza → PENDRIVE → PERFORADORA
                                                            (se escanea la etiqueta → busca el archivo por código)
                                                      → pegadora de cantos → armado
```

---

## 4. Datos vigentes — lo que manda sobre cualquier otro documento

**Perforadora** (detalle en `docs/PERFORADORA_SKH612.md`)

- Formato de carga: **KDTXml** (carpeta `XML3/`). El `.ban` **no** lo lee.
- **Cazoleta Ø35 = T184**: mecha **FUL Ø35 × 70 R** (MBD3570), salida 46 mm, tabla
  **34,8 / 34,8 / Z 24** (con Z 27 salía de 10; con 24 da **13**, calibre 05/10), avances **3500 / 350 / 175** (con 5000/500/250 saltaba `203h/206h` del **eje A = apoyo lateral**: la Ø35 a 13 empuja la placa; al 80 % anduvo bien). **No repasar cazoletas ya hechas.** La Ø20x70R que estaba antes **es una mecha,
  no una fresa: nunca para fresar**.
- **Variador del husillo de arriba (Delta MS300): hoy en 100 Hz** (≈ 6000 rpm, para cazoletas).
  **Para ranurar con la T187, subirlo a 300 Hz.**
- **Z: menos valor = más profundo** (el manual dice lo contrario y está mal).
- Clave de la tabla de herramientas y del permiso: **`520`**.
- **Tornillos de bisagra: Ø5 para siempre** (la Ø6 no existe en la máquina y el software crashea).
  `etapa2/ajustar_maquina.py --o6-a-o5` lo hace solo.
- **Ranuras de cara dorso: mínimo 10 mm** (sólo hay T11 Ø10 abajo). LED: ranura **10 × 10**.
- **Alarma `202h AEje` (motor sobrecargado) = la pieza es más ancha que lo programado.** El eje A es el carro del apoyo lateral: aprieta la placa hasta el ancho del programa, y si la pieza tiene 1–2 mm de más empuja contra la madera y se sobrecarga. **Medir cada pieza con calibre antes de mecanizar**; si no coincide, recortarla o pedir el programa con la medida real (resuelto 07/10, Spar en fenólico: placas de 400/401 con programa de 399). Dejar prendidas las detecciones de ancho y largo.
- **Fresa de abajo (T11, husillo de cara dorso)**: se cambia a mano con una **llave fija de 28** (traba el eje) y la **llave del mandril** (tuerca ER25). No tiene cono ni botón. 06/10: estaba gastada y se cambió. Detalle en `docs/PERFORADORA_SKH612.md` §6.8.
- **Mechas de repuesto** (vinieron con las máquinas, 05/10): Ø5 (6R+5L+1 Yuwei), Ø8 (7R+1L), Ø10 (4R+3L+1 Yuwei), Ø12 (3R), Ø15 (8L+1 Yuwei), mango Ø10×70. Ninguna Ø6. Detalle en `docs/PERFORADORA_SKH612.md`.
- Cazoletas y ranuras de menos de 10 **sólo desde arriba** → `ajustar_maquina.py` da vuelta las
  piezas solo.
- Pieza: **250–5000 × 50–1200 mm, 10–48 de espesor**. Cajones: ninguna pieza mecanizada de menos de 250.
- Salida de la pieza: **hacia adelante** ("Descarg").

**Herrajes** (detalle en `docs/HERRAJES.md`)

- La marca es **Grupo Euro**, no Häfele (los STEP de Häfele se usan como 3D de referencia).
- **Bisagra: tornillos a 6 mm del centro de la cazoleta, ±24 (patrón 48/6), x = 28,5 del canto.**
  Cazoleta Ø35 × 13 a 22,5 del canto. **Placa base (lateral): 2 × Ø5 × 3 a 37 del frente, uno arriba del otro a ±16 de la cazoleta** (Häfele 311.04.003 codo 0, probada 16/10; `PENDRIVE/PRUEBA_BISAGRA_HAFELE/`). Está en `medidas.json` (`base_frente` / `base_a_lo_largo`) y las recetas lo usan desde el 18/10; `fusion/PonerHerrajes` (camino GuiGui) sigue con 20/52. Esquema para la diseñadora en Figma (página "Bisagra – medidas para GuiGui" del archivo de herrajes). ⚠️ El 6 sale de la marca sobre la puerta: **confirmarlo con
  calibre**. La medida vive en **`herrajes/medidas.json`**; GuiGui todavía trae 14,5 → generar con
  `ajustar_maquina.py --bisagra`.
- **3 en 1: el perno es de rosca para madera (sin taco) → receptor Ø5 × 12** (probado 06/10; el Ø10 × 11 de GuiGui
  es para taco y el perno baila). Medida en `herrajes/medidas.json` (`tres_en_uno`); las recetas la leen desde el 18/10 (ya no dibujan receptor). GuiGui todavía saca Ø10.
- Biblioteca 3D en `herrajes/biblioteca/` (`CATALOGO.md`): **no volver a modelar herrajes**.

**Sierra / AutoCUT**: el mapeo está **mal** (cantos cruzados → piezas 1 mm mal por lado; código de
barras sale `P01`). Hasta corregirlo, la perforadora no encuentra el archivo al escanear.

---

## 5. Pendientes del proyecto, en orden

| # | Qué | Dónde está el detalle |
|---|---|---|
| 1 | **Corregir el mapeo de AutoCUT** (cantos y código de barras real) y volver a cortar las 7 piezas del gris. Nuestro lado ya está: la lista trae la columna `条码` con el código limpio; falta mapearla en la PC de la sierra | `docs/SIERRA_AUTOCUT.md` |
| 2 | **Bisagra 48/6: ✅ calza** en las 2 puertas chicas (05/10, `PENDRIVE/PRUEBA_BISAGRA/`, `etapa2/prueba_bisagra.py`): tornillos sobre los agujeros del ala, cazoleta centrada. Falta la profundidad (ver T184 en §4). El código ya lee de ahí (recetas, `PonerHerrajes`, `ajustar_maquina.py --bisagra` para lo de GuiGui) y COCINA-01 y Alacena Spar ya están re-exportadas con 48/6. Falta: la biblioteca STEP, el parámetro `HINGESCREW` de GuiGui y medir la placa base en el lateral (20 / 52) | `docs/HERRAJES.md` (última sección) |
| 3 | **Pruebas de la Etapa 0 sin resultado**: medida terminada vs. de corte (⚠️ los XML3 de `PENDRIVE/4_ALACENA_SPAR` vienen en medida **terminada**, p. ej. puertas 297 × 390, y la lista de corte las corta a 295 × 388: no perforar piezas crudas con esos hasta resolverlo), ¿lee `EdgeFBLR`?, Fusion vs. GuiGui (mismas 10 piezas), pieza curva R50, veta en AutoCUT, **espejado** | `MAÑANA_EN_LA_MAQUINA.md` · `docs/PERFORADORA_SKH612.md` §14 |
| 4 | **Perforadora**: velocidad por herramienta desde la PC, campana que no baja (M64), T187 ¿fresa o mecha?, T190, T186, filas 15–27, login, backup, lubricación vencida | `docs/PERFORADORA_SKH612.md` §14 (22 ítems) |
| 5 | **Ranura de canto**: no sabemos el formato (¿"SlotH"?) ni si la hace la SKH-612HS; el generador se niega a escribirla | `docs/FORMATOS.md` · pregunta a Huahua |
| 6 | Armar PRUEBA 1 completo (cantos HH-509R + armado). **Manual de armado**: ya sale de la receta (`etapa2/manual_armado.py`, ver §2); falta probarlo armando la Alacena Spar con el manual en la mano, y que también salga por el camino GuiGui | `docs/FUSION_RECETAS.md` |
| 7 | **Perno del 3 en 1: 33 o 34** (con el herraje Grupo Euro real) · canto real (¿1 mm?) · kerf real de la sierra | `docs/HERRAJES.md` |
| 8 | **`ArmarDesdeRender`: el canto de las piezas Lintel (listones) sale del lado equivocado** (arriba en vez de abajo; corregido a mano en la Spar 05/10) y `ExportarPiezas` da el fondo sin el encastre (564×710,6 en vez de 574×720,6) · COCINA-01: Ø3 de corredera (no hay en la máquina), colgadores sin medir, pistones de la rebatible; Alacena Spar: pistones Bronze, salida de cable LED | `fusion/EXPORT_COCINA-01/LEEME.md` · `docs/FUSION_RECETAS.md` §25.2 |
| 9 | **Router**: primera prueba física (cuadrado 100, decide si los `.nc` de GuiGui necesitan encabezado `G43`), cargar y medir las fresas en el almacén, medir mesa útil. Fresas ya identificadas: 8 × Ø10 rectas de 1/2", Ø6, Ø8 | `docs/ROUTER_SKG912.md` · `PENDRIVE/7_ROUTER_PRUEBA/LEEME.txt` |
| 10 | Curvado: probetas por material, primera pieza real, cantos en zona curva | `docs/CURVADO.md` |
| 11 | **Cocina de Jujuy (COCINA-01)**: medir en mano y ajustar en la receta: altura real del visor y posición de la salida Ø150 de la SDC-100; alturas de las rejillas del escurreplatos LC-560 y medidas del cubiertero; plantilla de calado de la bacha Tawak 55 (supuesto 530×440); confirmar que el visor banca el frente de madera; comprar pistones 60 N / 80–100 N; `.nc` o caladora para pasos del ducto, escotaduras y rincones; `PonerHerrajes` sigue con placa base 20/52 (recetas ya 37/±16) | `fusion/EXPORT_COCINA-01/LEEME.md` · `docs/FUSION_RECETAS.md` §25.2 |

---

## 6. Lista de compra

| # | Qué | Estado |
|---|---|---|
| 1 | Mecha cazoleta **FUL Ø35 × 70 R** (MBD3570) | ✅ **comprada y montada** en la T184 |
| 2 | Mecha vertical Ø6 | ❌ **no se compra** — Ø5 para siempre |
| 3 | **Fresa espiral de punta plana** (Ø20, o Ø10/12) | 🕓 sólo si algún día hay que fresar contornos o cazoletas de otro diámetro (la Ø20x70R es mecha) |
| 4 | Fresa espiral Ø6 de verdad para la T187 | ⏸ si se confirma que la actual es mecha |
| 4b | **Fresa Ø10 de repuesto para la T11** (husillo de abajo, pinza ER25) | 🛒 la de la máquina se rompió el 06/10 — tener siempre una de repuesto |
| 5 | Fresa Ø6 para el **router** (T1) | ✅ **ya hay**: vinieron 2 (Ø6×22 y Ø6×20, mango 1/2"). Falta confirmar pinza **ER32 de 13** |

No se compra: fresa de ranurar Ø9 (se diseña con ranuras de 10).

---

## 7. Mapa — qué leer para cada tema

| Tema | Documento |
|---|---|
| **Perforadora** (operación, herramientas, alarmas, mantenimiento, ajuste) | `docs/PERFORADORA_SKH612.md` (versión MindNode: `.opml`) |
| Formatos de archivo y generador `etapa2/` | `docs/FORMATOS.md` · `etapa2/README.md` |
| Fusion, recetas, COCINA-01, Alacena Spar | `docs/FUSION_RECETAS.md` · `fusion/README.md` |
| Herrajes y bisagra | `docs/HERRAJES.md` · `herrajes/biblioteca/CATALOGO.md` |
| Sierra y AutoCUT | `docs/SIERRA_AUTOCUT.md` |
| GuiGui / Bluen y su MCP | `docs/GUIGUI.md` · `referencia/GUIGUI_MCP/` |
| **Router** SKG-912MZY (operación, G54, almacén, M-codes, alarmas, fresas) | `docs/ROUTER_SKG912.md` |
| Curvado por ranuras | `docs/CURVADO.md` · `curvado/README.md` |
| Instructivo con capturas | `instructivo/INDICE.md` |
| Historia: cómo se llegó a cada cosa | `BITACORA.md` |
| Diseñar un mueble nuevo | skill **`mueble-nuevo`** |

**Contactos**

- **Huahua** (perforadora y sierra), grupo de WeChat: **Srta. Tan (谭小姐)** comercial; técnicos
  **周涛 Zhou Tao** (139 2595 7559, Changsheng Machinery) y **唐玮民 Tang Weimin**. China está +11 h:
  contestan entre las **22:00 y las 03:00** de Argentina.
- **GuiGui / Bluen**: cuenta verificada por SMS al celular terminado en **2352**.
- **Git**: `origin` → https://github.com/Barton-user/fabricamuebles.git

---

## 8. Reglas para mantener este archivo

1. **Acá va sólo lo que es cierto hoy.** Si un dato cambia, **se reemplaza** en su lugar; no se
   agrega una sección nueva abajo.
2. **Cada tema vive en un solo lugar.** El detalle va al documento de `docs/` que corresponde; acá,
   una línea con el valor vigente y el link.
3. **La historia va a `BITACORA.md`**: al cerrar una sesión, una entrada con fecha (qué se probó,
   qué salió, qué se decidió). Nunca se borra nada de ahí.
4. Si dos documentos dicen cosas distintas, **manda éste**; corregir el otro en el momento.
5. Al terminar: actualizar la fecha de arriba, `git add -A && git commit && git push`.
   (Si git se traba con "Operation not permitted", hay que borrar `.git/index.lock` y `.git/HEAD.lock`.)
6. **Cada vez que se le pasan archivos a Pato, terminar con el comando de terminal para abrir la
   carpeta**: `open "/Users/patriciokeogan/Documents/Claude/Projects/FABRICA MUEBLES/<carpeta>"`.

---

## Anexo · Dónde quedó cada sección vieja

Los documentos de `docs/` y `BITACORA.md` se movieron tal cual y todavía citan "§N" con la
numeración vieja de este archivo. Equivalencias:

| § viejo | Ahora en |
|---|---|
| 0, 1, 2, 16 (hoja de ruta), 22 (compras) | este archivo (§1–§6) |
| 3, 4, 12, 13 | `docs/FORMATOS.md` |
| 5, 23, 24, 28 | `docs/HERRAJES.md` |
| 7, 8, 17 (MCP de GuiGui) | `docs/GUIGUI.md` |
| 9, 18 (AutoCUT) | `docs/SIERRA_AUTOCUT.md` |
| 14, 15.1–15.9, 25, 27 | `docs/FUSION_RECETAS.md` |
| 20 (curvado) | `docs/CURVADO.md` |
| 6, 10, 10-bis, 11, 15 (23/09), 15.10, 16 (24/09), 17 (Huahua 24/09), 18 (COCINA MLV), 19, 20 (mechas), 21 (×2), 26, 29 | `BITACORA.md` |
