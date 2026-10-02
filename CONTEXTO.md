# FÁBRICA MUEBLES — Contexto del proyecto

_Leiten Com · Pato · Última actualización: **01/10/2026**_

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
| **2 · Estresar Fusion** | 2-3 muebles distintos de cero, cada herraje nuevo **medido** | 🟡 COCINA-01 (cajonera, zócalo, esquineros, estantes) diseñada y exportada, sin fabricar |
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
| Router | **SKG-912MZ** | nesting, contornos | Syntec | `.nc` | — (sin poner en marcha) |
| Perforadora | **SKH-612HS** (Huahua) | agujeros 6 caras, ranuras, cazoletas | **MH2026** + CncMon32 | **XML3 = KDTXml** (1 archivo por pieza, nombre = código de barras) | **`docs/PERFORADORA_SKH612.md`** |
| Pegadora de cantos | **HH-509R** | cantos | manual | la etiqueta | manual en `instructivo/manuales/` |
| Etiquetas | **AIBAO BC-80152T** | térmicas con QR | driver Windows, en la PC de la sierra | — | — |

Manuales: perforadora `User Manual_SKH-612 Series_260706_115944.pdf` (raíz); sierra, AutoCUT y
pegadora en `instructivo/manuales/`. Capturas explicadas de la perforadora: `instructivo/INDICE.md`.

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
  **34,8 / 34,8 / Z 27**, avances **5000 / 500 / 250**. La Ø20x70R que estaba antes **es una mecha,
  no una fresa: nunca para fresar**.
- **Variador del husillo de arriba (Delta MS300): hoy en 100 Hz** (≈ 6000 rpm, para cazoletas).
  **Para ranurar con la T187, subirlo a 300 Hz.**
- **Z: menos valor = más profundo** (el manual dice lo contrario y está mal).
- Clave de la tabla de herramientas y del permiso: **`520`**.
- **Tornillos de bisagra: Ø5 para siempre** (la Ø6 no existe en la máquina y el software crashea).
  `etapa2/ajustar_maquina.py --o6-a-o5` lo hace solo.
- **Ranuras de cara dorso: mínimo 10 mm** (sólo hay T11 Ø10 abajo). LED: ranura **10 × 10**.
- Cazoletas y ranuras de menos de 10 **sólo desde arriba** → `ajustar_maquina.py` da vuelta las
  piezas solo.
- Pieza: **250–5000 × 50–1200 mm, 10–48 de espesor**. Cajones: ninguna pieza mecanizada de menos de 250.
- Salida de la pieza: **hacia adelante** ("Descarg").

**Herrajes** (detalle en `docs/HERRAJES.md`)

- La marca es **Grupo Euro**, no Häfele (los STEP de Häfele se usan como 3D de referencia).
- **Bisagra: tornillos a 6 mm del centro de la cazoleta, ±24 (patrón 48/6), x = 28,5 del canto.**
  Cazoleta Ø35 × 13 a 22,5 del canto. ⚠️ El 6 sale de la marca sobre la puerta: **confirmarlo con
  calibre**. La medida vive en **`herrajes/medidas.json`**; GuiGui todavía trae 14,5 → generar con
  `ajustar_maquina.py --bisagra`.
- Biblioteca 3D en `herrajes/biblioteca/` (`CATALOGO.md`): **no volver a modelar herrajes**.

**Sierra / AutoCUT**: el mapeo está **mal** (cantos cruzados → piezas 1 mm mal por lado; código de
barras sale `P01`). Hasta corregirlo, la perforadora no encuentra el archivo al escanear.

---

## 5. Pendientes del proyecto, en orden

| # | Qué | Dónde está el detalle |
|---|---|---|
| 1 | **Corregir el mapeo de AutoCUT** (cantos y código de barras real) y volver a cortar las 7 piezas del gris. Nuestro lado ya está: la lista trae la columna `条码` con el código limpio; falta mapearla en la PC de la sierra | `docs/SIERRA_AUTOCUT.md` |
| 2 | **Bisagra 48/6**: medir con calibre (si no da 6, cambiar sólo `herrajes/medidas.json`). El código ya lee de ahí (recetas, `PonerHerrajes`, `ajustar_maquina.py --bisagra` para lo de GuiGui) y COCINA-01 y Alacena Spar ya están re-exportadas con 48/6. Falta: la biblioteca STEP, el parámetro `HINGESCREW` de GuiGui y medir la placa base en el lateral (20 / 52) | `docs/HERRAJES.md` (última sección) |
| 3 | **Pruebas de la Etapa 0 sin resultado**: medida terminada vs. de corte, ¿lee `EdgeFBLR`?, Fusion vs. GuiGui (mismas 10 piezas), pieza curva R50, veta en AutoCUT, **espejado** | `MAÑANA_EN_LA_MAQUINA.md` · `docs/PERFORADORA_SKH612.md` §14 |
| 4 | **Perforadora**: velocidad por herramienta desde la PC, campana que no baja (M64), T187 ¿fresa o mecha?, T190, T186, filas 15–27, login, backup, lubricación vencida | `docs/PERFORADORA_SKH612.md` §14 (22 ítems) |
| 5 | **Ranura de canto**: no sabemos el formato (¿"SlotH"?) ni si la hace la SKH-612HS; el generador se niega a escribirla | `docs/FORMATOS.md` · pregunta a Huahua |
| 6 | Armar PRUEBA 1 completo (cantos HH-509R + armado). **Manual de armado**: ya sale de la receta (`etapa2/manual_armado.py`, ver §2); falta probarlo armando la Alacena Spar con el manual en la mano, y que también salga por el camino GuiGui | `docs/FUSION_RECETAS.md` |
| 7 | **Perno del 3 en 1: 33 o 34** (con el herraje Grupo Euro real) · canto real (¿1 mm?) · kerf real de la sierra | `docs/HERRAJES.md` |
| 8 | COCINA-01: Ø3 de corredera (no hay en la máquina), colgadores sin medir; Alacena Spar: pistones Bronze, salida de cable LED | `fusion/EXPORT_COCINA-01/LEEME.md` · `docs/FUSION_RECETAS.md` |
| 9 | Router SKG-912MZ: cargar T1 Ø6, medir mesa y herramientas | `docs/CURVADO.md` |
| 10 | Curvado: probetas por material, primera pieza real, cantos en zona curva | `docs/CURVADO.md` |

---

## 6. Lista de compra

| # | Qué | Estado |
|---|---|---|
| 1 | Mecha cazoleta **FUL Ø35 × 70 R** (MBD3570) | ✅ **comprada y montada** en la T184 |
| 2 | Mecha vertical Ø6 | ❌ **no se compra** — Ø5 para siempre |
| 3 | **Fresa espiral de punta plana** (Ø20, o Ø10/12) | 🕓 sólo si algún día hay que fresar contornos o cazoletas de otro diámetro (la Ø20x70R es mecha) |
| 4 | Fresa espiral Ø6 de verdad para la T187 | ⏸ si se confirma que la actual es mecha |
| 5 | Fresa Ø6 para el **router** (T1) | 🕓 cuando se ponga en marcha el router |

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
