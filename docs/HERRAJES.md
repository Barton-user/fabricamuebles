# Herrajes

_Parámetros de herrajes y placa, equivalencias Häfele, biblioteca 3D (`herrajes/biblioteca/`) y la bisagra real. ⚠️ **La medida vigente de la bisagra es la de la última sección (48/6)**; las anteriores dicen 14,5._

_Movido tal cual desde `CONTEXTO.md` el 01/10/2026. Las referencias "§N" dentro del texto son a la numeración vieja de `CONTEXTO.md`: cada sección vieja dejó allí una línea 📦 que dice adónde fue. Si algo de acá contradice a `CONTEXTO.md`, manda `CONTEXTO.md`._

---

## 5. Parámetros de herrajes y placa

> **🔩 Marca de herrajes de la casa: HÄFELE** (decidido 28/09/2026).
> Todos los herrajes que se usen (3 en 1 / conectores, bisagras, correderas, etc.) salen de
> Häfele Argentina. Catálogos y folletos: <https://www.hafele.com.ar/es/info/servicios/cat-logos-y-folletos/268936/>
> **Equivalencias con lo modelado y qué cambia en las perforaciones → §23.**
> Cuando un herraje nuevo entre a `PonerHerrajes`, tomar las cotas del catálogo Häfele del
> modelo elegido **y medirlo igual** contra la pieza real (ver §15.5 — no suponer números).

Confirmados contra el `Process settings.png` que viene en el mueble de muestra de Bluen
(sección 连接件 → 三合一 = tres-en-uno):

| Parámetro | Valor |
|---|---|
| Excéntrica: diámetro (D) | **15 mm** |
| Excéntrica: distancia al borde (A) | **33 mm** |
| Excéntrica: profundidad (S) | **13,5 mm** |
| Varilla: diámetro (d) | **8 mm** |
| Varilla: profundidad (c) | **33 mm** |
| Pre-embedded: diámetro (d0) | **10 mm** |
| Pre-embedded: profundidad (C) | **11 mm** |

**Placa**: 2440 × 1210 mm (¡ojo, los defaults chinos usan 1220!).
Espesores en uso: **18 mm** (cuerpo y puertas), **5 mm** (fondos).
Refilado de sierra: 5 mm por borde. Kerf configurado 4,4 / 4,5 mm (**verificar contra la hoja real**).
Canto: se asumió **1,0 mm** para calcular medidas de corte (**VERIFICAR el canto real**).

### Herramientas necesarias para PRUEBA 1

Extraído del JSON de layout, agregando todas las piezas:

| Tipo | Ø | Profundidad | Cantidad | Uso |
|---|---|---|---|---|
| Vertical | 6 mm | 3 mm | 16 | tornillos de bisagra (`HINGESCREW`) + `jlHoleEX` |
| Vertical | 10 mm | 11 mm | 20 | tres-en-uno, pre-embedded |
| Vertical | 15 mm | 13,5 mm | 20 | tres-en-uno, excéntrica |
| Vertical | 35 mm | 13 mm | 4 | cazoletas de bisagra |
| **Horizontal** | 8 mm | 33 mm | 20 | tres-en-uno, varilla |
| Fresa ranurar | **6 mm** | 6 mm | 4 ranuras | fondo (`BP`) |
| Fresa ranurar | **9 mm** | 9 mm | 1 ranura | ranura de luz (`lightSlot`) |

**Primera pieza de prueba — techo 400 × 600, código 9441838670057**:
4 agujeros Ø10 prof 11 en **X = 40 y 360, Y = 9 y 591** (cara A);
1 ranura 6 × 6 (fondo, a X = 372,5) y 1 ranura 9 × 9 (luz, **cara B**, a X = 304,5).

> ⚠️ **Corregido el 20/09/2026.** Antes decía X = 42 y 362, Y = 11 y 593. Esos valores
> salen del campo `center` del JSON, que está en el marco de la **placa nesteada** (+2 mm).
> El archivo de máquina usa `ocenter`, el marco de la **pieza terminada**. Los valores
> de arriba están verificados 12/12 contra los archivos de referencia de Bluen.

### Despiece completo de PRUEBA 1 (orden 260625-20)

| Código de barras | Pieza | Medida | Esp. | AgV | AgH | Ranuras |
|---|---|---|---|---|---|---|
| 9441838670057 | Roof plate01 (techo) | 400 × 600 | 18 | 4 | 0 | 2 |
| 9441838670064 | Left board01 | 400 × 741,83 | 18 | 12 | 2 | 1 |
| 9441838670071 | Right board01 | 400 × 741,83 | 18 | 12 | 2 | 1 |
| 9441838670088 | Puerta doble izquierda | 297 × 681,83 | 18 | 6 | 0 | 0 |
| 9441838670101 | Puerta doble derecha | 297 × 681,83 | 18 | 6 | 0 | 0 |
| 9441838670125 | Partition02 | 370 × 564 | 18 | 4 | 4 | 0 |
| 9441838670132 | Partition01 | 400 × 564 | 18 | 8 | 4 | 1 |
| 9441838670149 | Back panel01 (fondo) | 574 × 633,83 | 5 | 0 | 0 | 0 |
| 9441838670156 | Fascia board02 | 564 × 100 | 18 | 4 | 4 | 0 |
| 9441838670163 | Fascia board01 | 564 × 100 | 18 | 4 | 4 | 0 |

Materiales: `13玛雅灰 18mm` (gris, cuerpo), `04拉丝胡桃 18mm` (nogal cepillado, puertas),
`d02白麻面 5mm` (fondo).

---

## 23. Herrajes Häfele equivalentes a los modelados (28/09/2026)

Fuente: catálogo nacional **"El Gran Häfele" (ff_HAR_2024, 639 págs.)** de hafele.com.ar, leído página por
página. Las páginas se ven sueltas en
`https://www.hafele.com/INTERSHOP/web/WFS/Haefele-HAR-Site/es_AR/-/EUR/Static-View/pdfcatalog/es_AR/catalogs/catalogs/ff_HAR_2024/large/bk_<N>.jpg`
(N = nº de página del visor; el PDF completo pesa ~325 MB en `.../ff_HAR_2024/pdf/complete.pdf`).

### ¿Se pueden bajar planos / 3D?

- **hafele.com.ar**: solo catálogos (visor + PDF). Sin CAD por artículo.
- **haefele.de (Häfele Alemania)**: cada artículo tiene **"CAD-Daten"** (visor CADclick, `teccad.hafele.com`):
  pestañas **3D / 2D / 3D PDF**, descarga en "todos los formatos CAD habituales" y una opción
  **"inkl. Bearbeitungen (Bohrungen, Nuten)"** que trae el herraje **con los agujeros** que pide en la placa.
  Häfele también ofrece datos **CAM** (~18.000 artículos con perforaciones/ranuras), pero sólo vía software de la
  industria. Los mismos nº de artículo sirven para Argentina. **Todavía no se bajó nada.**
- Las páginas del catálogo con el ícono **CAD** tienen modelo disponible (Minifix, Metalla, correderas, Loox).

### Tabla: lo que tenemos modelado → Häfele

| Nuestro (GuiGui / `PonerHerrajes`) | Häfele equivalente | Nº art. | Pág. cat. | Diferencia de perforación |
|---|---|---|---|---|
| **3 en 1 – caja** Ø15 × 13,5, alto 9 (placa 18) | **Minifix 15** sin reborde, desde 18 mm | 262.26.034 | M 3.6 | Ø15 × **13,5** y A = **9** → **idénticos**. Pero el centro de la caja va a **B = 34** del canto (Häfele ofrece 24 o 34), no a 33 |
| **3 en 1 – perno** Ø8 en canto, 33/34 | **Perno expansible C100 para Ø10**, B 34, rosca 11,5 | 262.09.313 | solo en haefele.de (el catálogo AR trae el C100 para Ø8, 262.09.302, M 3.7) — **confirmar que se consiga acá** | Ø8 de canto hasta la caja (B 34). Coincide con nuestro **`3EN1-34`** |
| **3 en 1 – receptor** Ø10 × 11/12 en la otra placa | (el manguito viene en el mismo C100) | 262.09.313 | — | Ø10 × **12** → coincide con `3EN1-34`. El `3EN1-33` (Ø10 × 11, caja a 33) **no tiene equivalente Häfele** |
| **Bisagra cazoleta** Ø35 × 13, a 22,5 del canto (E = 5) | **Metalla 310 SM 110°**, montaje angular (sobrepuesta), cierre automático | 311.04.239 (push 311.84.506) | M 4.8 | Cazoleta Ø35 × **11** (13 sobra, se puede dejar 12). E = 5 con placa 0 → **solape 16 mm**. Tornillos **48/6**: ±24 ✓ pero a **6 mm** del centro de la cazoleta (**28,5 del canto**), no a 14,5 (37 del canto) → **cambiar** |
| Variante con amortiguador | **Metalla SM Kombi 110°** angular | 311.04.003 | M 4.7 | Cazoleta × 12, patrón 48/6 igual que arriba |
| **Base de bisagra** (一字底座) 2 × Ø6 × 3 a **20 y 52** del frente | **Placa en cruz Metalla SM** altura 0 (o la de leva 311.70.610) | 311.71.500 | M 4.14 | Sistema 37/32 → agujeros a **21 y 53** del frente → **correr 1 mm** |
| **Corredera telescópica 450** (三节滑轨, TOPCENT SL.8450 soft close, 13 mm) | **Corredera de bolillas extensión total con autocierre y amortiguación Smuso**, 450 | 494.02.074 (negro) / 494.02.064 (blanco) | M 8.45 | 13 mm de juego ✓, alto 45,7. Agujeros en lateral: **35 · 163 · 259** del frente (primer agujero a 35, luego +128 y +224). Hoy GuiGui hace **37 y 413** → ninguno cae justo → **cambiar a 35 / 163 / 259** |
| Corredera 450 sin amortiguar | Bolillas **sobreextensión** 450 | 494.02.374 / 494.02.364 | M 8.47 | Agujeros 37 · 165 · 261 · 389 |
| **Tira LED** en ranura 9 × 9 | **Loox5 LED 3040**, 24 V, 5 mm de ancho | 833.76.296 (3000 K) / 833.76.303 (5000 K) | M 2.17 | Entra en la ranura 9 × 9 sin perfil. El perfil para embutir Loox (833.72.983) pide ranura **18 × 9,5** → no hay perfil Häfele para 9 × 9 |
| **Riel de puerta corrediza** (移门滑轨) | **Infront** (juego 2 puertas 407.40.008, riel sup. 940.43.xxx) | 407.40.008 | M 9.12 | **Sin verificar** contra nuestra geometría |
| Patas regulables (no están en el JSON) | Patas regulables Häfele | 637.xx | págs. 613-614 del visor | Sin revisar |

**Resumen:** con Häfele se usa **un solo 3 en 1: el de 34** (`3EN1-34`, con la caja a 34 del canto en vez de 33) — si se consigue el C100 Ø10 en Argentina.
Hay que tocar `PonerHerrajes` en cuatro puntos: caja 33 → **34**; tornillos de bisagra 14,5 → **6** del centro
de la cazoleta; base 20/52 → **21/53**; corredera 37/413 → **35/163/259** (Smuso) o 37/165/261/389 (sin amortiguar). Antes de cambiar
nada, **medir el herraje real** (o bajar su 2D con "inkl. Bearbeitungen") como se hizo con los 72 conectores.

**⚠️ Ojo con la mecha Ø6 (§22):** las Metalla SM de la tabla vienen **con tornillos para aglomerado**
(Ø3,5–4), y un agujero Ø6 × 3 es más grande que el tornillo. Con Häfele los tornillos de la bisagra y de la
base van **sin agujero** o con un guía chico. La única variante Häfele que pide agujero es la placa con
**tornillos Euro premontados** (311.71.510), que usa **Ø5**. Conviene definir esto **antes de comprar la Ø6**.

**Pendiente:** bajar de haefele.de el 3D (STEP) + 2D con perforaciones de 262.26.034, 262.09.313, 311.04.239,
311.71.500 y 494.02.074 y guardarlos en `referencia/HAFELE/`. El agujero de la corredera en el costado del
cajón (hoy 37 y 413 sobre un costado de 450) no figura en el catálogo → sacarlo del 2D.

---

## 24. 🔧 BIBLIOTECA DE HERRAJES — no volver a modelarlos (29/09/2026)

**Si en una conversación nueva hace falta poner herrajes en un mueble: leer
`herrajes/biblioteca/CATALOGO.md` y usar los STEP de esa carpeta. No modelarlos
de nuevo.**

`ArmarDesdeRender.herraje()` ya lo hace solo. Antes de dibujar busca en
`herrajes/biblioteca/indice.json` un archivo cuyo **prefijo** coincida con el
nombre del componente (`Bisagra O35 base -6` → prefijo `Bisagra O35`). Si lo
encuentra importa el STEP; si no, dibuja la forma con código como antes. Los
STEP están en el marco de uso (origen sobre el agujero de la CNC), así que caen
en su lugar con la misma matriz que ya se calculaba.

Piezas en STEP: excéntrica Ø15, perno Ø8×33, bisagra de cazoleta Ø35 completa
y cerrada. Piezas que siguen siendo código porque cambian de largo: corredera
de bolas, tira LED, receptor Ø10.

### 24.1 Lo que se verificó contra el herraje real (fotos del 29/09)

| Herraje | Resultado |
|---|---|
| Caja excéntrica Ø15 | Coincide |
| Perno + expansor | Coincide. Son 3 piezas, no 2 (perno + tarugo azul + excéntrica) |
| Bisagra cazoleta Ø35 | Cazoleta coincide. **Tornillos del ala: 48 mm, no 53,5** |
| Placa base de bisagra | Coincide, pero la real es **cruciforme** y viene puesta en la bisagra |
| Corredera | **NO coincidía.** Era de bolas de 3 tramos, no canal + barra. Rehecha. |
| Tira LED | Sin foto todavía |

### 24.2 🚨 La marca NO es Häfele

Los herrajes de la fábrica son **Grupo Euro** (marca argentina), estampado en la
cazoleta y en la placa base. A Pato le habían dicho que eran Häfele y no lo son.

Los STEP de Häfele se usaron porque eran el único 3D real disponible, y para la
cazoleta sirven (Ø35 y profundidad idénticas). Pero **el ala de Häfele trae los
tornillos a 53,5 mm y la de Grupo Euro a 48**. Los archivos de GuiGui perforan a
48 (`HINGESCREW` Ø6 × 3, a y=75 y y=123 con la cazoleta en y=99, y a x=36 contra
x=21,5 → 14,5 mm hacia adentro).

**Consecuencia práctica:** una bisagra Häfele NO se puede atornillar en una
puerta perforada por GuiGui sin cambiar ese parámetro. Hoy no importa porque se
compra Grupo Euro, pero conviene no olvidarlo.

Lección para la próxima: **verificar la marca antes de bajar un CAD de un
fabricante y meterlo en el modelo.** Acá se metió Häfele en 26 bisagras antes de
mirar el estampado del herraje real.

### 24.3 Por qué la bisagra es híbrida

El STEP de Häfele 311.04.239 viene con la bisagra **abierta a 90°**. No hay
rotación rígida que la cierre: una bisagra de cazoleta es un mecanismo de cuatro
barras, al cerrarse el brazo no gira sino que se pliega. Si se la rota 90° sobre
el perno principal el brazo termina 40 mm adentro del lateral.

Por eso quedó: cazoleta y ala originales de Häfele, brazo + placa base +
tornillos dibujados en posición cerrada. El original abierto está guardado en
`ref_bisagra_hafele_311-04-239_ABIERTA.step`.

### 24.4 Herrajes que faltan modelar

- **Pistón a gas** (marca Bronze). No está en el 3D ni en el archivo de GuiGui.
  Falta saber dónde se usa y con qué fuerza.
- **Escuadra de unión** metálica con tapa plástica. Va atornillada, no lleva
  agujeros de CNC.

### 24.5 Cuadro de comparación en Figma

https://www.figma.com/design/FBehv5P3VSuDUbLplOPRit — una fila por herraje con
el dibujo sacado del 3D, la foto real, qué medir y el veredicto.

---

## 28. 🔩 BISAGRA REAL: tornillos a 6 mm de la cazoleta, no 14,5 (01/10/2026) — MEDIDA OFICIAL

Al perforar las 3 puertas PET de la Alacena Spar (PRUEBA 1) los Ø5 de los tornillos no calzaban
con la bisagra **Grupo Euro** que tenemos: quedaban **~9 mm** corridos hacia el centro de la puerta.
Medido sobre la puerta con el herraje apoyado (foto del 01/10).

**Medida real de la bisagra (la que se usa por ahora, en todo):**

| | Antes (GuiGui / receta / biblioteca) | **Real Grupo Euro** |
|---|---|---|
| Cazoleta | Ø35 × 13, centro a 22,5 del canto | igual ✓ |
| Separación entre tornillos (a lo largo del canto) | 48 (±24) | **48 (±24)** ✓ |
| Tornillos desde el centro de la cazoleta, hacia adentro de la puerta | **14,5** (x = 37 del canto) | **≈ 6** → x = **28,5 del canto** (patrón estándar **48/6**) |

→ Los tornillos van **8,5 mm más cerca del canto** que en los archivos de GuiGui.
⚠️ El 6 sale de la marca sobre la puerta; **confirmarlo con calibre sobre la bisagra en la mano**
(centro de cazoleta → línea de los dos tornillos) antes de producir en serie.

Hecho hoy: programas corregidos de las 3 puertas en `PENDRIVE/5_ALACENA_SPAR_GUIGUI/XML3_PUERTAS_V2/`
(completo) y `XML3_SOLO_TORNILLOS/` (sólo los 4 Ø5, para re-pasar puertas ya perforadas). Las 3
puertas de esta alacena ya tienen los Ø5 viejos a 14,5; quedan esos agujeros de más (cara interior).

### PENDIENTE — todo lo que hay que cambiar para que quede con la bisagra real

> **Estado al 01/10/2026 (noche):** las medidas viven ahora en **`herrajes/medidas.json`** (un solo
> lugar). ✅ 2 recetas (leen el json; `recetas/salida/` regenerado: sólo cambiaron los tornillos)
> · ✅ 3 `PonerHerrajes` (lee el json; `ArmarDesdeRender` y `ArmarReceta` usan su forma 3D)
> · ✅ 5 `etapa2/ajustar_maquina.py --bisagra` corrige lo que venga de GuiGui (probado con la Spar:
> da lo mismo que las puertas corregidas a mano). ✅ COCINA-01 y ALACENA SPAR re-armadas en Fusion y
> re-exportadas (01/10, noche): receta vs sólido **0 diferencias** (95/95 y 11/11), sin ningún Ø6;
> guardadas como versión nueva; pendrive de la Spar actualizado. (`COCINA-01 movimiento` sigue con la
> bisagra vieja dibujada: es sólo para la animación.) **Falta**: medir con calibre (si no es 6,
> cambiar sólo el json y repetir), y los puntos 1, 4, 6 y 7.

1. **Biblioteca 3D de Fusion** (`herrajes/biblioteca/`): revisar los STEP contra las piezas
   **reales** (no son exactamente las de Häfele). En especial `bisagra_cazoleta_O35.step`: el ala
   y los tornillos tienen que quedar a **6** de la cazoleta y 48 entre sí; placa base cruciforme
   Grupo Euro. Revisar también excéntrica, perno y receptor contra lo que se compra.
2. **Recetas**: `recetas/cocina01.py` → `TOR = {"adentro": 14.5}` pasa a **6.0** (afecta a todas
   las recetas que lo importan, p. ej. `alacena_spar.py`). Regenerar COCINA-01 y ALACENA-SPAR.
3. **PonerHerrajes / ArmarDesdeRender** (`_forma_bisagra`, posiciones `HINGESCREW`): misma corrección.
4. **GuiGui** (la diseñadora): parámetro de bisagra **`HINGESCREW`** → tornillos a 6 del centro
   de la cazoleta (48/6). Mientras no se cambie, todo lo que salga de GuiGui trae 14,5 y hay que
   corregirlo al generar (hoy se hizo a mano para la Spar).
5. **Generador `etapa2/`**: opcional, una corrección automática de `HINGESCREW` (como
   `ajustar_maquina.py --o6-a-o5`) para no depender de que GuiGui esté bien.
6. **Placa base en el lateral** (`jlHoleEX`, hoy Ø6/Ø5 a 20 y 52 del frente): **sin verificar**
   contra la placa base cruciforme real. Medirla.
7. `herrajes/biblioteca/CATALOGO.md` y §24: actualizar la tabla de la bisagra con esta medida.

---
