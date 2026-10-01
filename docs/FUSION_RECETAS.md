# Fusion y recetas (Etapa 3)

_Diseñar en Fusion sin GuiGui: cómo se modela, el camino Fusion → archivos de máquina, las recetas (`recetas/`), COCINA-01 y Alacena Spar. Detalle técnico de los scripts en `fusion/README.md`._

_Movido tal cual desde `CONTEXTO.md` el 01/10/2026. Las referencias "§N" dentro del texto son a la numeración vieja de `CONTEXTO.md`: cada sección vieja dejó allí una línea 📦 que dice adónde fue. Si algo de acá contradice a `CONTEXTO.md`, manda `CONTEXTO.md`._

---

## 14. Etapa 3 — diseñar en Fusion, sin GuiGui (VALIDADO 22/09/2026)

El objetivo de no volver a abrir GuiGui está cumplido para el caso probado: **10 piezas
modeladas en Fusion salieron a los cuatro formatos de máquina más la lista de corte, con
toda la geometría igual a la referencia.**

### El flujo

1. Se modela el mueble en Fusion (un cuerpo por placa).
2. `MarcarPlaca` marca cada cuerpo: `MATERIAL | TEXTURA | VETA | abajo,arriba,izq,der`.
3. `ExportarPiezas` lee los sólidos por **B-Rep** y escribe `piezas.json` +
   `diagnostico.txt` + `GENERAR ARCHIVOS.command`.
4. Doble clic en `GENERAR ARCHIVOS.command` → `.ban`, `.mpr`, XML1, XML3, lista de corte
   y hojas de verificación.

No hace falta árbol de operaciones ni nombrar features: se lee la geometría final. Un
cilindro completo es agujero, uno parcial es redondeo de esquina, una cara plana
intermedia es fondo de ranura.

### Resultado

XML3 da **10/10 idéntico**. Los otros tres formatos y la lista de corte dan 8/10 (9/11 en
`.mpr`), y **las diferencias no son geométricas**: son el atributo de cantos de los dos
frentes, el número de placa del anidado (vacío, lo pone la optimizadora) y el material de
3 piezas (falta correr `MarcarPlaca`). Detalle en `fusion/README.md`.

### Lo que se corrigió al validar

- **`长` / `宽` de la lista de corte ahora siguen la veta**, y las cuatro columnas de canto
  giran con ellas. Antes `长` era siempre Y, y `纹路` era una constante que ni miraba el
  dato de veta cargado en la pieza.
- **Profundidad de agujeros de canto**: cuando el Ø8 desemboca en el Ø15, el B-Rep sólo ve
  26,7 mm. Se completa con la tabla `PROFUNDIDAD_CANTO` (Ø8 → 33 mm) y **siempre queda
  constancia en `diagnostico.txt`**. Es el único lugar donde el extractor usa una tabla en
  vez de medir.
- **Guardas contra duplicados**: `PruebaCompleta` no corre sobre un documento con cuerpos,
  y `ExportarPiezas` aborta si hay dos códigos de barras iguales.

### Lo único abierto del camino Fusion

**¿Algo lee `EdgeFBLR` del `.ban`?** GuiGui rota la geometría de una pieza acostada pero
deja las banderas de canto sin rotar; nosotros las rotamos. Si el pegado de cantos se
maneja desde la lista de corte —que es lo que parece—, no tiene efecto. **Medir la primera
fascia board en la máquina.**

### `MarcarPlaca` — validado 22/09/2026

Nunca había corrido, y tenía tres errores: leía al revés lo que devuelve el cuadro de
diálogo de Fusion (reventaba siempre), marcaba componentes en vez de cuerpos (las 10
placas habrían salido con el mismo material), y dependía de la selección previa, que
**Fusion borra al abrir el diálogo de Scripts**. Ahora muestra la lista numerada de
placas y pregunta cuáles marcar. Se agregó `=` como "no tocar", para cargar el material
sin pisar los cantos.

Con las texturas cargadas por pieza, la columna `材料` coincide 10/10 con la referencia.
**La lista de corte da 8/10 filas idénticas en las 19 columnas**; las 2 restantes son
los frentes, y difieren sólo en cuál lado se llama 长 y cuál 宽.

### Contorno irregular — validado 22/09/2026 contra un archivo real de Bluen

El extractor **no leía el contorno**: tomaba el rectángulo del bounding box, así que una
pieza con esquina cortada, redondeo o escotadura salía como un rectángulo liso **sin
ningún aviso**. Ya lee el borde de la cara con los arcos.

Se validó con `6893155441217` del pedido 试生产样品柜 — un lateral de 350 × 500 con
redondeo R50 —, modelándolo de cero en Fusion: **los cuatro formatos salen idénticos a
los de Bluen**. Desvío máximo del contorno 0,014 mm; área 174.463,34 mm² contra
174.463,32 (0,02 mm² de diferencia).

**La trampa:** leer el borde de la cara A no alcanza. Una ranura que llega al borde le
abre un golfo al contorno de esa cara, y si la cruza entera se lo parte en dos. El primer
intento rompió 3 de las 10 piezas ya validadas: en `9441838670132` daba 369,5 de los
400 mm, o sea **la placa 30 mm más angosta**, con archivos de aspecto normal. Se corrigió
leyendo las dos caras y quedándose con la de mayor área, más una red de seguridad que se
niega a exportar un contorno que no ocupe todo el bounding box.

### Ranuras de canto — se detectan, no se exportan

Un canal de 6 mm en el canto se leía como **dos ranuras de 12 mm, una por cara**: la
máquina habría fresado las dos caras. Ahora se empareja el piso con el techo del canal y
se reconoce bien.

No se escribe al archivo: en los 82 `.ban` de referencia el vocabulario completo es
`Plane, Outline, Point, HoleV, HoleH, SlotL`, sin ningún ejemplo de ranura de canto. El
exportador se niega y lo explica, en vez de inventar el formato.

**Va a la lista de preguntas para HUAHUA (sección 11).**

### `PonerHerrajes` — el herrajero (22/09/2026)

Encuentra solo las uniones del mueble y hace los tres agujeros de cada 3 en 1 en las
dos piezas. Probado sobre un mueble armado de 4 placas: 4 uniones encontradas,
36 agujeros, y el chequeo automático confirma que cada Ø8 termina exactamente en el
centro de su Ø15 y que los Ø10 caen donde sale el perno.

**Para que funcione, cada placa tiene que ser un componente con la placa acostada
adentro, puesta en su lugar moviendo la ocurrencia.** Se verificó que `ExportarPiezas`
lee bien un ensamble 3D así: la placa se lee acostada del componente y la ocurrencia
sólo la ubica.

**Las medidas salen de medir los 72 conectores de los archivos reales**, y ahí apareció
algo que no sabíamos: **los dos pedidos usan herrajes distintos.**

| | PRUEBA 1 | muestra |
|---|---|---|
| Ø15 desde el canto / profundidad | 33 / 13,5 | 33 / 13,5 |
| Ø8 profundidad / altura | **33** / 9 | **34** / 9 |
| Ø10 profundidad | **11** | **12** |

Bisagra (PRUEBA 1): cazoleta Ø35 × 13 a 22,5 del canto, y dos Ø6 × 3 a 14,5 más
adentro y ±24 a lo largo.

**Error que esto destapó:** `ExportarPiezas` tenía 33 fijo en la tabla que corrige la
profundidad del Ø8 cuando desemboca en el Ø15. Con el herraje de 34 habría escrito 33
—un milímetro de menos— sin avisar. Ahora el dato lo deja `PonerHerrajes` en la pieza.

### Sin probar todavía

- dirección de veta de los dos frentes, en AutoCUT
### Bisagras — hechas y verificadas (22/09/2026)

`PonerHerrajes` también pone bisagras, en **las dos piezas**: cazoleta Ø35 × 13 a 22,5 del
canto más dos Ø6 × 3 a 37 del canto y ±24 a lo largo en la **puerta**, y los dos Ø6 × 3 del
herraje de la base a **20 y 52 del canto de adelante** en el **lateral**. La altura sale de
la puerta (100 de cada punta) y la correspondencia con el lateral se calcula del ensamble.

**Error que destapó la verificación:** los agujeros se agrupaban por cara y se hacían todos
con la profundidad del más hondo. En una puerta con cazoleta de 13 y tornillos de 3, los
tornillos salían **de 13** — el Ø6 habría pasado de largo. Ahora agrupa por cara y por
profundidad. Lo encontró un chequeo automático contra el patrón medido, no leyendo el código.

---

# 15. ESTADO ACTUAL — 22/09/2026

> **Leer esto primero.** Las secciones 13 y 14 cuentan cómo se llegó; ésta dice
> dónde estamos parados hoy.

## 15.1 · El objetivo, y dónde está

**No volver a abrir GuiGui.** Diseñar en Autodesk Fusion —que corre en la Mac— y
mandar los archivos a las máquinas directamente.

**Está cumplido y validado en el escritorio. Falta confirmarlo sobre metal.**

## 15.2 · Qué anda

| | Estado |
|---|---|
| Fusion → 4 formatos de máquina + lista de corte, sin tocar GuiGui | ✅ |
| Las 10 piezas de PRUEBA 1, toda la geometría igual a GuiGui | ✅ (XML3 idéntico 10/10) |
| Contorno irregular — diagonales, escotaduras, arcos | ✅ validado contra archivo real de Bluen, **4/4 formatos idénticos** |
| Agujeros verticales, de canto y ranuras de cara | ✅ |
| `MarcarPlaca` — material, textura, veta, cantos y mueble por pieza | ✅ |
| `PonerHerrajes` — 3 en 1 y bisagras, en las dos piezas de cada unión | ✅ |
| **Mueble armado en Fusion sin agujeros → PonerHerrajes → máquina** (`ArmarPrueba1`, 22/09) | ✅ **80/80 agujeros iguales a GuiGui**, XML3 10/10; sólo difiere el flag de canto de los zócalos |
| Hojas de verificación acotadas por pieza | ✅ |
| Camino GuiGui (por si hay que volver atrás) | ✅ 41/41 |

## 15.3 · Qué NO anda, y por qué

**Ranuras de canto.** Se detectan correctamente —canto, ancho, profundidad y
altura— pero **el exportador se niega a escribirlas**. En los 82 `.ban` de
referencia el vocabulario completo es `Plane, Outline, Point, HoleV, HoleH,
SlotL`: no hay ni un solo ejemplo de ranura de canto. Inventar el elemento es
mandar un programa equivocado a la perforadora. Es pregunta para la Sra. Tan.

Antes de esto se leían como **dos ranuras de 12 mm, una en cada cara** — la
máquina habría fresado las dos caras de la placa.

## 15.4 · Lo que falta confirmar en la máquina

Todo está en **`MAÑANA_EN_LA_MAQUINA.md`**, con la carpeta `PENDRIVE/` ya armada.

1. **Qué formato lee HHcnc** — sin eso no sabemos cuál de las 4 carpetas usar
2. **Fusion contra GuiGui sobre metal** — el pendrive lleva las mismas 10 piezas
   dos veces, `1_DESDE_GUIGUI` y `2_DESDE_FUSION`
3. **Medida terminada vs. de corte** — medir el techo con calibre contra
   X = 40 / 360 e Y = 9 / 591
4. **Si algo lee `EdgeFBLR`** — mecanizar `9441838670156` de los dos juegos
5. **La veta de los dos frentes en AutoCUT** — 长 564/宽 100 contra 长 100/宽 564
6. **Ranura de canto** — preguntar formato, y si la hace esta máquina

**Dato que falta de la casa:** si el herraje que usan es el de **perno 33** o el
de **34**.

## 15.5 · Tabla de herrajes — medida sobre los archivos reales

Los **72 conectores** y las **4 bisagras** de los dos pedidos de referencia.
Estos números son los que usa `PonerHerrajes`; no salen de ningún catálogo.

### 3 en 1

| | `3EN1-33` (PRUEBA 1) | `3EN1-34` (muestra) |
|---|---|---|
| Ø15 cara — profundidad | 13,5 | 13,5 |
| Ø15 — desde el canto | 33 | 33 |
| Ø8 canto — profundidad | **33** | **34** |
| Ø8 — altura (placa de 18) | 9 | 9 |
| Ø10 en la otra placa | **11** | **12** |

En los 72 el Ø15 es idéntico. Lo único que cambia es cuánto entran el perno y el
receptor. **No es un número universal**, y suponerlo costó un bug (ver 15.6).

### Bisagra de cazoleta

| Pieza | Agujero | Posición |
|---|---|---|
| Puerta | Ø35 × 13 | 22,5 mm del canto |
| Puerta | 2 × Ø6 × 3 | 37 mm del canto (14,5 más adentro), ±24 a lo largo |
| Lateral | 2 × Ø6 × 3 | **20 y 52 mm del canto de adelante**, a la altura de la bisagra |

Altura de las bisagras en PRUEBA 1: **100 mm de cada punta** de la puerta.

## 15.6 · Los errores que se encontraron, y cómo

Vale la pena dejarlos anotados: **ninguno se vio leyendo el código.** Todos los
encontró una comparación contra los archivos reales o un chequeo automático.

| Error | Qué habría pasado |
|---|---|
| El contorno no se leía: sólo el rectángulo del bounding box | Una pieza con esquina cortada o curva salía **rectangular**, sin aviso |
| Primer intento de contorno: leía el borde de una cara | Una ranura que llega al borde parte la cara; en `…132` daba la placa **30 mm más angosta**, con archivos de aspecto normal |
| Ranura de canto leída como dos ranuras de cara | La máquina fresaba **las dos caras** de la placa |
| `PROFUNDIDAD_CANTO` con 33 fijo | Con el herraje de 34, el Ø8 salía **1 mm corto** en silencio |
| `agujero_cara` agrupaba sólo por cara | En una puerta, los tornillos Ø6 de 3 mm salían **de 13** — atravesaban |
| `MarcarPlaca` leía al revés el `inputBox` | Reventaba siempre; **nunca había funcionado** |
| `MarcarPlaca` marcaba componentes, no cuerpos | Las 10 placas salían con **el mismo material** |
| `MarcarPlaca` dependía de la selección previa | Fusion la borra al abrir el diálogo de Scripts: no marcaba nada |
| `长`/`宽` no miraban la veta cargada | Marcar la veta en Fusion **no hacía nada** |

**La lección:** cada vez que el sistema tuvo que suponer algo —un número de
herraje, cuál cara mirar, qué profundidad usar— se equivocó en silencio. Lo que
funcionó fue medir los archivos reales y comparar contra ellos.

## 15.7 · Cómo hay que modelar en Fusion

1. **Cada placa, un componente**, con la placa **acostada** adentro: boceto en XY,
   extruir en Z. El espesor va sobre Z.
2. Se para y se ubica **moviendo la ocurrencia**, no la geometría.
3. `MarcarPlaca` para material, textura, veta, cantos y a qué mueble pertenece.
   **Marcar todas las placas o ninguna**: apenas hay una marcada, las que no lo
   están se ignoran al exportar.
4. `PonerHerrajes` para los 3 en 1 y las bisagras.
5. `ExportarPiezas` → elegir carpeta → doble clic en `GENERAR ARCHIVOS.command`.

Verificado que el extractor lee bien un ensamble 3D así: la placa se lee acostada
del componente y la ocurrencia sólo la ubica.

## 15.8 · El mapa de archivos

```
FABRICA MUEBLES/
├── CONTEXTO.md                      ← este archivo
├── MAÑANA_EN_LA_MAQUINA.md          ← la hoja de campo
├── PENDRIVE/                        ← listo para llevar
│   ├── 1_DESDE_GUIGUI/              ← las 10 piezas, control
│   ├── 2_DESDE_FUSION/              ← las mismas 10, sin tocar GuiGui
│   └── 3_PIEZA_CURVA/               ← contorno R50
├── etapa2/                          ← el generador (Python, sin dependencias)
│   ├── panel.py                     ← el modelo interno
│   ├── guigui.py  fusion_json.py    ← los dos orígenes
│   ├── ban.py  mpr.py  xml1.py  xml3.py
│   ├── exportar.py  listacorte.py  hojas.py  validar.py
│   └── salida/PRUEBA1/              ← el oráculo
├── fusion/                          ← los scripts de Fusion
│   ├── ExportarPiezas/              ← lee los sólidos por B-Rep
│   ├── MarcarPlaca/                 ← los datos que no se deducen del sólido
│   ├── PonerHerrajes/               ← el herrajero
│   └── README.md                    ← el detalle de cada uno
└── referencia/                      ← los archivos de Bluen: el oráculo real
```

## 15.8-bis · Dos cosas de Fusion que cuestan caro

**La posición de una placa no queda guardada sola.** En un diseño paramétrico,
mover una ocurrencia es un cambio "sin capturar": la siguiente operación del timeline
la devuelve al origen. El resultado es un mueble que se arma, se herraja, y termina con
todas las placas apiladas en el origen y los herrajes flotando en el aire donde iban.
Se arregla con `design.snapshots.add()` después de ubicar y antes de taladrar.

**El ícono de ancla.** Una ocurrencia con `isGroundToParent = True` está clavada al
origen y no se mueve hasta soltarla. Fusion ancla la primera sola.

Las dos juntas explican por qué el primer mueble armado aparecía desarmado.

## 15.9 · Git

El proyecto está en un repositorio git **local**, en la misma carpeta. Primer
commit `7187c7b`, 476 archivos, 22/09/2026.

```
cd "~/Documents/Claude/Projects/FABRICA MUEBLES"
git log --oneline          # historial
git status                 # qué cambió
git diff                   # ver los cambios antes de guardar
git add -A && git commit -m "lo que hice"
```

Está todo adentro, incluidas las carpetas `referencia/` y `PENDRIVE/`: pesan poco
y la de referencia es el oráculo contra el que se valida todo, así que conviene
que viaje con el código.

**Queda afuera** (`.gitignore`): `.DS_Store`, los `__pycache__`, y
`fusion/_descartes/`, que son las carpetas de exportaciones de prueba viejas que
se apartaron al ordenar.

**Remoto configurado**: `origin` → https://github.com/Barton-user/fabricamuebles.git
(`main` sigue a `origin/main`). Al cierre de cada sesión: `git add -A && git commit -m "..." && git push`.

> Nota: git necesita borrar sus propios temporales (`index.lock`, `tmp_obj_*`).
> Si alguna vez se traba con "Operation not permitted", es eso.

---

## 25. COCINA-01 — primera cocina diseñada desde cero, por RECETA (29/09/2026)

Se tomó el modelo de render `COCINA` (Fusion, proyecto cocina; son bloques macizos, no placas)
sólo como medidas, y se armó una cocina fabricable con las decisiones de Pato: puertas lisas
melamina 18 (VERDE 18) y cuerpos BLANCO 18, esquineros diagonales con chanfle a mano y puerta
colgada de un **montante a 45°**, cajonera 320 con 4 cajones y corredera de bolillas 450
(37/413), bajo pileta con frente fijo, zócalo clip sobre patas, alacenas hasta 2490 sin
cornisa con cenefa verde de 60, LED en ranura 10×10 en cara B del piso, estantes regulables
Ø5 (sistema 32, banda de 5 agujeros), fondos 5 en ranura 6×6, sin tiradores, mesada externa.

**Camino nuevo, el de la Etapa 3 (§16):** `recetas/cocina01.py` (Python puro) calcula todas las
placas y todos los agujeros → `modelo.json` → `fusion/ArmarReceta` lo arma en Fusion (documento
`COCINA-01`, herrajes STEP de la biblioteca) → `ArmarReceta.exportar()` = ExportarPiezas sin
diálogos → `etapa2/`. La receta escribe además `piezas_receta.json` y `recetas/comparar.py` lo
compara con lo que Fusion lee del sólido: **95/95 idénticas**. Paquete en
`fusion/EXPORT_COCINA-01/` (ver su `LEEME.md`).

Dos errores que encontró la comparación / los chequeos (y ya están corregidos):

1. **Ranuras de fondo en L** (esquineros): si las dos ranuras se tocan, forman un solo fondo de
   ranura en L y `ExportarPiezas` **no la reconoce** ("cara plana 757×757 ignorada") → el archivo
   de máquina salía sin ranuras. Ahora quedan separadas 1 mm.
2. **Corredera contra 3 en 1** en los costados de cajón: el Ø3 del riel (a media altura, cara B)
   se metía en el Ø8 del perno. Ahora el conector va a 30 del borde de arriba, y la receta tiene
   un chequeo de "agujero de cara que se mete en un agujero de canto".

Cajón: frente y contrafrente **por fuera** y costados entre ellos, para que ninguna pieza
mecanizada quede por debajo de los 250 mm que acepta la perforadora (con la cajonera de 320 el
frente interior daba 222).

Pendientes propios de esta cocina: ver `fusion/EXPORT_COCINA-01/LEEME.md` (Ø3 y Ø6 no están en
la máquina, Ø15/Ø10 en cara B, canto 1 mm, colgadores sin medir, paquete de etiquetas/manual
todavía sale sólo desde render.json de GuiGui).

### 25.1 · Puertas y cajones que se mueven (29/09/2026)

Documento aparte **`COCINA-01 movimiento`** (copia; `COCINA-01` queda igual) con juntas de Fusion
hechas por `fusion/MoverPuertas`: 10 juntas de **revolución** (puertas, 0-90°, las bisagras van
pegadas a la puerta en un grupo rígido) y 4 **deslizantes** (cajones, 0-400 mm, frente + caja en
grupo rígido). Se mueven con ENSAMBLAR → *Accionar juntas* o *Estudio de movimiento*.
`MoverPuertas.animar()` saca cuadros y de ahí sale `COCINA-01_puertas_y_cajones.gif` / `.mp4`.

- Las juntas "as-built" sólo existen en diseño **paramétrico** (el documento se convierte).
- Con geometría de vértice, el eje *custom* por arista se ignora: se usa el eje LOCAL de la placa
  (puertas: Y local = vertical → `YAxisJointDirection`; cajones: `ZAxisJointDirection`).
- El pivote es la arista de afuera del lado de bisagras (aproximación: la bisagra real es de 4 barras).
- **Hallazgo:** la puerta de cada esquinero y la puerta vecina (B2 derecha / A2 derecha) **no se
  abren a fondo las dos a la vez**: con la vecina abierta, la del esquinero llega a 45°. Con
  todas abiertas a 90° no hay otro choque; a 95° chocan dos puertas con bisagra en el mismo encuentro.
- Con todo abierto, `ExportarPiezas` da igual 95/95: las juntas no cambian los archivos de máquina.
- **Todas juntas (29/09):** 13 *vínculos de movimiento* (Motion Link) atan todo a la junta
  maestra **`B2 Puerta der`**: maestra 0→90° = puertas 0→90°, esquineros 0→45°, cajones 0→400 mm.
  Se mueve sólo la maestra (Accionar juntas / Animar del vínculo / Estudio de movimiento con esa
  junta), o se corre el script `MoverPuertas` (abre y cierra dos veces). API: `root.motionLinks`
  con las juntas como proxy de la ocurrencia del mueble; tipos `RevoluteJointRotateMotionType` y
  `SliderJointSlideMotionType`.
- ⚠️ **Anclar lo fijo (29/09):** sin anclar, al arrastrar una puerta Fusion resolvía la junta
  moviendo el **lateral** y el mueble se desarmaba (laterales girados ~20°, cajonera corrida 18 cm).
  Ahora las 61 placas fijas y los muebles están anclados (`isGrounded`) en `COCINA-01 movimiento`,
  y `MoverPuertas.preparar()` lo hace solo.

---

## 27. ALACENA SPAR — primer mueble de GuiGui rehecho en Fusion sin tocar GuiGui (01/10/2026)

La diseñadora dibujó en GuiGui (PRUEBA 1, orden 260625-20) una **alacena sobre campana**: 600 × 845
× 400, techo arriba a todo el ancho, laterales, tapa inferior + 2 listones abajo (faldón), estante
fijo, fondo 5, **puerta rebatible arriba** y **dos batientes abajo**, frentes PET GRIS 18, cuerpo GRIS 18.
Se leyó por el MCP de GuiGui (solo lectura) y se rehízo como receta: `recetas/alacena_spar.py`
(usa las funciones de `cocina01.py`) → `fusion/ArmarReceta` → documento Fusion **`ALACENA SPAR`**
(proyecto cocina) → `ArmarReceta.exportar()` → `etapa2/`. Paquete: `fusion/EXPORT_ALACENA_SPAR/`
(ver su `LEEME.md`) y copia para el pendrive en `PENDRIVE/4_ALACENA_SPAR/`.

Problemas del diseño de GuiGui que se corrigieron (decididos con Pato):
- Los 936,5 de alto del cubo de GuiGui incluyen 92 mm vacíos abajo; el mueble real mide 844,47 → **845**.
- Tapa inferior con excéntricas en una cara y ranura de fondo de 6 en la otra (6 en dorso no se
  puede) → excéntricas arriba con la ranura; listones unidos sólo a los laterales.
- Lateral derecho y listón de atrás con todo en cara B → en la receta **cara A = adentro siempre**.
- LED 9×9 arriba del techo, pasante a la vista → **10×10 en la cara B de la tapa inferior** (T11).
- Ø6 de bisagra → **Ø5** en el archivo (evita el crash de la Ø6, §15).

Nuevo en `etapa2/`: **`maestra_fusion.py`** — arma `maestra.json` desde el `piezas.json` de Fusion,
así `etiquetas.py` y `materiales.py` también funcionan por el camino Fusion (antes sólo desde
render.json). `fusion/ArmarReceta` ahora lee `modelo["referencia"]` (lista vacía = sin cajas de
cocina) y conoce los colores GRIS / PET GRIS.

Controles: receta vs sólido 11/11 idénticas; chequeos de la receta sin errores; todas las
herramientas existen en la máquina (Ø15, Ø10, Ø5 T162, Ø35 por T184, Ø8 horiz., ranura 6 T187,
ranura dorso 10 T11). Falta: pistones Bronze (a mano), colgadores, salida del cable LED, canto real.

---

## Manual de armado desde la receta (01/10/2026)

`etapa2/manual_armado.py <modelo.json> -o manual.pdf [--mueble "..."]` — lee el `modelo.json` que
escribe cada receta (placas con O/ex/ey/W/H/T y herrajes con su lugar) y arma un PDF A4 de 2 hojas
**sin Fusion**: dibuja las placas en isométrica él mismo (reportlab).

- **Hoja 1**: explotada con un número por pieza (= orden de armado), tabla de piezas con medida,
  material y **código de la etiqueta**, herrajes con cantidades (3 en 1, bisagras + 4 tornillos c/u,
  correderas, patas, LED) y herramientas.
- **Hoja 2**: pasos dibujados (lo armado en gris, lo nuevo en naranja): preparar herrajes → primer
  lateral → horizontales de abajo hacia arriba → fondo(s) asomando por el lado abierto → otro
  lateral → patas → cajones (sub-armado: se dibuja el cajón 1 solo) → correderas → puertas. Cuenta
  las uniones 3 en 1 de cada paso (perno: la placa donde está la boca − ez; recibe: + ez).
- Abajo, en rojo, las **notas de la receta de ese mueble** ("pendiente de definir en fábrica —
  sacar antes de entregar"). Si hay piezas a 45° (esquineros) agrega un aviso: el orden automático
  puede no servir.
- Con varios muebles en el modelo saca un PDF por mueble (`manual_<mueble>.pdf`).

Salidas: `fusion/EXPORT_ALACENA_SPAR/manual_armado.pdf` (+ copia en `PENDRIVE/4_ALACENA_SPAR/`) y
`fusion/EXPORT_COCINA-01/manuales/`.

Falta: probarlo armando de verdad; sacarlo también por el camino GuiGui (desde `maestra.json`);
esquineros; dibujar los herrajes en los pasos (hoy sólo placas).

