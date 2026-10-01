# Formatos de archivo de las máquinas y generador propio (Etapa 2)

_Sistema de coordenadas, especificación de cada formato con ejemplos literales (`.ban`, `.mpr`, XML1, XML3 / KDTXml, lista de corte) y el generador de `etapa2/`. Es la especificación de salida que cualquier reemplazo de GuiGui tiene que cumplir._

_Movido tal cual desde `CONTEXTO.md` el 01/10/2026. Las referencias "§N" dentro del texto son a la numeración vieja de `CONTEXTO.md`: cada sección vieja dejó allí una línea 📦 que dice adónde fue. Si algo de acá contradice a `CONTEXTO.md`, manda `CONTEXTO.md`._

---

## 3. Sistema de coordenadas y convenciones (crítico para Etapa 2)

Aplica a todos los formatos de pieza (BAN, MPR, XML):

- **Origen** en la esquina inferior izquierda de la pieza vista desde la **cara frontal (A / 正面)**.
- **X** a lo ancho (`Width` / `PanelLength` / `LA`), **Y** a lo largo (`Height` / `PanelWidth` / `BR`).
- **Z = 0** en la superficie de la cara A; **Z negativo hacia adentro** de la placa.
  Un agujero de 13,5 mm de profundidad va de `Z=0` a `Z=-13.5`.
- Los agujeros horizontales se cotan a **media placa**: `Z = -9` en una placa de 18 mm.
- **Contorno (Outline)** en sentido antihorario, cerrando en el punto inicial.

**Nombres de caras** (6 caras de la pieza):

| Código BAN | Significado | Equivalente MPR | Equivalente XML1 | Equivalente XML3 |
|---|---|---|---|---|
| `A` | cara frontal (正面) | `<102 V_DRILLING>` | `direction="1"`, `drillDirection=(0,0,-1)` | `TypeNo=1` |
| `B` | cara trasera (反面) | archivo `...K.mpr` aparte | `positionSide="0"` | `TypeNo=13` |
| `U` | canto superior (Up / Top) | `BM="YM"` | `drillDirection=(0,-1,0)` | `Quadrant` |
| `D` | canto inferior (Down) | `BM="YP"` | `drillDirection=(0,1,0)` | `Quadrant` |
| `L` | canto izquierdo (Left) | `BM="XP"` | `drillDirection=(1,0,0)` | `Quadrant=2` |
| `R` | canto derecho (Right) | `BM="XM"` | `drillDirection=(-1,0,0)` | `Quadrant=1` |

**`EdgeFBLR="1,1,1,1"`** = flags de canto pegado en Front, Back, Left, Right (1 = lleva canto).
**`Grain="2"`** = veta vertical (竖纹). **`PlaneSize="1"`** = cantidad.

> ⚠️ **Trampa detectada**: algunas plantillas rotan la pieza 90° (intercambian Width/Height)
> y en consecuencia reasignan las caras de los agujeros horizontales (R/L ↔ U/D).
> Esto produce muebles **espejados**. Siempre verificar con calibre en la primera pieza.

---

## 4. Formatos de archivo — especificación con ejemplos reales

Todos los ejemplos son del **mismo panel**: `竖隔板01` (divisor vertical), 173 × 350 × 18 mm,
código de barras **6893155441637**, del mueble de muestra de Bluen.
Contiene: 4 agujeros verticales Ø15 prof 13,5 (excéntricas del tres-en-uno),
4 agujeros horizontales Ø8 prof 34 (varillas), y 2 ranuras de 6 mm de ancho × 6 de profundidad.

### 4.1 `.ban` — MicroDrawBan XML 3.0 → PERFORADORA SKH-612HS

Es el formato principal de la perforadora. **XML plano, un archivo por pieza, nombre del
archivo = código de barras**. Codificación UTF-8 (la variante `BAN_SC` lleva BOM).

```xml
<MicroDrawBan_XML Version="3.0" Time="2026/09/16 pm 2:49:37" Source="柜柜软件" SourceType="BAN">
<Plane Width="173.00" Height="350.00" PlaneSize="1" Grain="2" Thickness="18"
       Material="多层实木" EdgeFBLR="1,1,1,1" Name="主卧_地柜A_竖隔板01" Code="6893155441637">
    <Outline>
        <Point Value="0.00 0.00 0"/>
        <Point Value="173.00 0.00 0"/>
        <Point Value="173.00 350.00 0"/>
        <Point Value="0.00 350.00 0"/>
        <Point Value="0.00 0.00 0"/>
    </Outline>
    <HoleV Name="" Diameter="15.00" IsCuted="0" Face="A" Start="140.00 286.00 0"    End="140.00 286.00 -13.50"/>
    <HoleV Name="" Diameter="15.00" IsCuted="0" Face="A" Start="33.00 64.00 0"      End="33.00 64.00 -13.50"/>
    <HoleH Name="" Diameter="8.00"  IsCuted="0" Face="R" Start="173.00 286.00 -9.00" End="139.00 286.00 -9.00"/>
    <HoleH Name="" Diameter="8.00"  IsCuted="0" Face="L" Start="0.00 64.00 -9.00"    End="34.00 64.00 -9.00"/>
    <SlotL Name="" Face="A" Start="173.00 329.50 -6.00" End="0.00 329.50 -6.00" Width="6.00" IsCuted="0"/>
    <SlotL Name="" Face="B" Start="173.00 329.50 -6.00" End="0.00 329.50 -6.00" Width="6.00" IsCuted="0"/>
</Plane>
</MicroDrawBan_XML>
```

Elementos:

- **`<Plane>`** — cabecera de la pieza. `Code` es el código de barras (lo que escanea la pistola).
- **`<Outline>`** — polilínea del contorno. Para piezas rectangulares son 5 puntos (cierra).
- **`<HoleV>`** — agujero vertical. `Start` en la superficie, `End` a profundidad (Z negativo).
  La profundidad es `|Z_End|`.
- **`<HoleH>`** — agujero horizontal. `Start` sobre el canto, `End` hacia adentro.
  La profundidad es la distancia XY entre Start y End (aquí 173−139 = 34 mm).
- **`<SlotL>`** — ranura recta. `Start`/`End` en el eje de la ranura, `Z` = profundidad,
  `Width` = ancho (determina el diámetro de fresa necesario).

**Variantes de plantilla `.ban` observadas** (GuiGui las exporta todas en el modo de prueba):

| Carpeta | Diferencia |
|---|---|
| `BAN` | base, atributo `Height` correcto |
| `BAN2` | igual a BAN pero la ranura de la cara B va a `Z=-12.00` (profundidad medida desde cara A) |
| `BAN3` | igual a BAN con pequeñas variantes de formato |
| `BAN4` | usa `Hight` (typo) + `Code1=""` |
| `BAN_SC` | idéntico a BAN pero con **BOM UTF-8** al inicio |

### 4.2 `.mpr` — WoodWOP / Homag (豪迈) → perforadoras compatibles MPR

Formato de texto plano por bloques, alemán. Un archivo por pieza; **las piezas con
mecanizado en la cara trasera generan un segundo archivo con sufijo `K`**
(ej. `6893155441637.mpr` + `6893155441637K.mpr`).

```
[H\Left:1;Bottom:1;Right:1;Top:1
VERSION="4.0 Alpha"
VIEW="NOMIRROR"
OP="1"
FM="1"
FW="800"
ModusMirror="1"

<100 \WerkStck\          ← pieza
LA="173"                 ← largo (X)
BR="350"                 ← ancho (Y)
DI="18"                  ← espesor

<102 \V_DRILLING\        ← agujero vertical
XA="140"  YA="286"
BM="LS"                  ← modo
TI="13.5"                ← profundidad
DU="15"                  ← diámetro
AB="32"
KAT="Bohren vertikal"
MNM="Vertical drilling"

<103 \End_Boring\        ← agujero horizontal
XA="173"  YA="286"  ZA="9"
DU="8"                   ← diámetro
TI="34"                  ← profundidad
ANA="20"
BM="XM"                  ← XM = canto X máximo (derecho); XP = canto X mínimo (izquierdo)
KAT="Horizontalbohren"

<109 \Nuten\             ← ranura
XA="173" YA="329.5"      ← inicio
XE="0"   YE="329.5"      ← fin
NB="6"                   ← ancho de ranura
TI="6"                   ← profundidad
MV="GL"  MN="GL"
KAT="Nuten"
MNM="Grooving"

<101 \Kommentar\
KM="主卧_地柜A_竖隔板01"   ← ¡codificado en GBK, no UTF-8!
!                        ← fin de archivo
```

> ⚠️ El bloque `\Kommentar\` viene en **GBK**. Si se lee como UTF-8 sale mojibake.

### 4.3 `.xml` (XML1) — formato "Plate" genérico

Legible, buen candidato como formato intermedio propio en la Etapa 2.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Plate plateNumber="6893155441637" plateNickName="主卧_地柜A_竖隔板01"
       width="350.00" depth="173.00" height="18.00" barCode="6893155441637" barCode1="">
    <Bandings>
        <Banding bandingBack="1" bandingRight="1" bandingFront="1" bandingLeft="1"/>
    </Bandings>
    <Holes>
        <Hole point="(140.00,286.00,18.00)" diameter="15.00" depth="13.50"
              direction="1" positionSide="1" drillDirection="(0,0,-1)"/>
        <Hole point="(173.00,286.00,9.00)"  diameter="8.00"  depth="34.00"
              direction="0" positionSide="1" drillDirection="(-1,0,0)"/>
    </Holes>
    <Slottings>
        <Slotting positionSide="1" slottingStartX="173.00" slottingStartY="329.50" slottingStartZ="0.000"
                  slottingEndX="0.00" slottingEndY="329.50" slottingEndZ="0.000"
                  slottingWidth="6.00" slottingDepth="6.00"/>
    </Slottings>
    <YXJSlottings/>
    <H_Slottings/>
    <Points>
        <Point startPoint="(0.00,350.00,18.00)" endPoint="(173.00,350.00,18.00)"
               center="(0,0,0)" radius="" arcDirection="0" millingIndex="0"
               cutHeight="" isLagestEdge="1" cutPositionSide="正面"/>
    </Points>
</Plate>
```

- `direction`: **1 = vertical**, **0 = horizontal**.
- `positionSide`: **1 = cara frontal**, **0 = cara trasera**.
- `drillDirection`: vector unitario de avance de la mecha.
- Ojo: acá `width`=350 y `depth`=173 — **invertidos respecto al `.ban`**.
- `<Points>` es el contorno, con `cutPositionSide` indicando desde qué cara se corta.

### 4.4 `.xml` (XML3) — formato KDT (星辉 / 极东)

Orientado a lista de operaciones tipificadas. Muy fácil de generar y de parsear.

```xml
<KDTPanelFormat>
    <PANEL>
        <PanelLength>173.00</PanelLength>
        <PanelWidth>350.00</PanelWidth>
        <PanelThickness>18.00</PanelThickness>
        <PanelName>主卧_地柜A_竖隔板01</PanelName>
        <Params>
            <Param Key="L" Value="173.00" Comment="板长"/>
            <Param Key="W" Value="350.00" Comment="板宽"/>
            <Param Key="T" Value="18.00" Comment="板厚"/>
        </Params>
    </PANEL>
    <CAD>
        <TypeNo>1</TypeNo><TypeName>Vertical Hole</TypeName>
        <X1>140.00</X1><Y1>286.00</Y1>
        <Depth>13.50</Depth><Diameter>15.00</Diameter>
        <Enable>1</Enable><HoleNo>1</HoleNo>
        <IntervalX>0.00</IntervalX><IntervalY>0.00</IntervalY>
    </CAD>
    <CAD>
        <TypeNo>2</TypeNo><TypeName>Horizontal Hole</TypeName>
        <X1>173.00</X1><Y1>286.00</Y1><Z1>9.00</Z1>
        <Quadrant>1</Quadrant>          <!-- 1 = canto derecho, 2 = canto izquierdo -->
        <Depth>34.00</Depth><Diameter>8.00</Diameter>
        <Enable>1</Enable><HoleNo>1</HoleNo>
    </CAD>
    <CAD>
        <TypeNo>3</TypeNo><TypeName>Line</TypeName>   <!-- 3  = ranura cara frontal -->
        <BeginX>173.00</BeginX><BeginY>329.50</BeginY>
        <EndX>0.00</EndX><EndY>329.50</EndY>
        <Correction>0</Correction>
        <Width>6.00</Width><Depth>6.00</Depth><Enable>1</Enable>
    </CAD>
    <CAD>
        <TypeNo>13</TypeNo><TypeName>Line</TypeName>  <!-- 13 = ranura cara trasera -->
        ...
    </CAD>
</KDTPanelFormat>
```

**Tabla de `TypeNo`** (deducida): `1` agujero vertical · `2` agujero horizontal ·
`3` ranura cara frontal · `13` ranura cara trasera. (Hay más tipos para fresados y
formas irregulares, no observados todavía.)

### 4.5 `.nc` — código G Syntec → ROUTER SKG-912MZ

**Un archivo por placa entera** (no por pieza). Nombre: `001_<material>_<textura>_<espesor>_正面.nc`.
Coordenadas en la placa completa (X hasta ~1210, Y hasta ~2440).

```gcode
G00 X743.00 Y95.00 F12000      ; rápido al punto de entrada
G01 Z18.00 F6000               ; baja a la superficie de la placa (Z=18 = tope)
G01 X743.00 Y15.00 Z-0.10 F3000 ; entra cortando, pasa 0,10 mm el espesor
G01 X1097.00 Y15.00 F8000      ; contorno a velocidad de corte
G01 X1097.00 Y192.00 F8000
G01 X743.00 Y192.00 F8000
G01 X743.00 Y115.00 F8000
G01 X743.00 Y15.00 F3000.0     ; cierra el contorno
G00 Z38.00 F12000              ; sube a altura segura
```

Convenciones:

| Valor | Significado |
|---|---|
| `Z = 18.00` | superficie superior de la placa (Z cero en la mesa) |
| `Z = -0.10` | corte pasante (0,1 mm más que el espesor) |
| `Z = 38.00` | altura segura de traslado |
| `F12000` | avance rápido G00 |
| `F6000` | bajada de la herramienta |
| `F3000` | entrada y salida del material |
| `F8000` | avance de corte en contorno |

Los arcos y las formas irregulares vienen **linealizados**: en vez de `G02/G03` se emiten
cientos de `G01` de ~1 mm con Z interpolada (rampa de entrada helicoidal).

```gcode
G01 X66.99 Y519.00 Z9.14 F3000
G01 X65.83 Y518.99 Z8.88 F3000
G01 X64.67 Y518.95 Z8.61 F3000
...
```

**La sierra HP280 NO usa código G.** Su control lee un `.CUT` generado por AutoCUT.

### 4.6 `开料清单.xls` — lista de corte → AutoCUT → SIERRA HP280

Excel con una fila por pieza. Columnas (en chino en el original):

| Columna | Traducción | Ejemplo |
|---|---|---|
| `序号` | nº de orden | 1 |
| `打包二维码` | QR de empaque | 主卧_地柜A_竖隔板01 |
| `工件名称` | nombre de la pieza | 主卧_地柜A_竖隔板01 |
| `数量` | cantidad | 1 |
| `长` / `宽` | largo / ancho **terminado** | 173 / 350 |
| `成品面积` | área terminada m² | 0.06 |
| `厚` | espesor | 18 |
| `材料` | material | 18_多层实木_T01 |
| `开料长` / `开料宽` | largo / ancho **de corte** | 171 / 348 |
| `切割面积` | área de corte | 0.06 |
| `开料厚` | espesor de corte | 18 |
| `板件条码` | **código(s) de barras** | `6893155441637_6893155441637_6893155441637K` |
| `板号` | nº de placa | 9 |
| `前/后/左/右封边` | canto delante/atrás/izq/der | 1 / 1 / 1 / 1 |
| `纹路` | veta | 竖纹 (vertical) |
| `订单号` | nº de orden | 230714-2 |
| `客户名称` | cliente | 老张 |
| `项目地址` | dirección/proyecto | 试生产样品柜 |
| `部件名称` | nombre del componente | 主卧_地柜A_竖隔板01 |

> **Dato clave**: `板件条码` lista los códigos de barras **y el sufijo `K`** cuando la pieza
> necesita un segundo programa para la cara trasera. Ej: `…441637_…441637_…441637K`.

**Medida terminada vs. medida de corte**: la diferencia (173→171, 350→348) es el espesor del
canto que se va a pegar: **1 mm por cada lado con canto**. Este valor hay que verificarlo
contra el canto real antes de producir en serie.

**Importación en AutoCUT**: botón Importar → "Importar varios materiales" → "Coincidencia"
para mapear columnas. `开料长`/`开料宽` (CutLength/CutWidth) van a **"Longitud/Ancho de apertura"**.

### 4.7 `<ORDEN>-Mass production.json` — el volcado completo (la mina de oro)

Este archivo contiene **absolutamente toda** la información del layout y de la geometría de
cada pieza. **Para la Etapa 2 es la referencia más valiosa**: es el modelo de datos interno
de GuiGui. Estructura:

```
{
  "total": 3,                          // placas
  "statisticObj": "{\"04拉丝胡桃 18 多层实木\":1, ...}",
  "layoutName": "PRUEBA-批量生产-2026.9.16 12:36",
  "version": "5.0.0.4global-9",
  "layoutConfig": { "plankEdgeOff": 18, "cutKnifeRadius": 3 },
  "layoutResult": "<STRING con JSON anidado>"   // ⚠ viene como string, hay que parsear dos veces
}
```

`layoutResult` (tras el segundo parse) es un array de placas:

```
[{
  "thick": "18", "matCode": "多层实木", "texture": "13玛雅灰",
  "plankWidth": 1210, "plankHeight": 2440, "usedRate": ..., "utilization": ...,
  "parts": [ { ...una pieza... }, ... ]
}]
```

Y cada **pieza** (`parts[i]`) tiene:

| Campo | Contenido |
|---|---|
| `plankNum` / `oriPlankNum` | **código de barras** (ej. `9441838670125`) |
| `plankNumType2` | código formateado con guiones (`9441838-67-0125`) |
| `partName`, `name`, `loc`, `roomName` | nombres jerárquicos |
| `rect`, `oRect`, `realRect`, `fullSize` | medidas de corte y terminadas |
| `startX`, `startY`, `rotate`, `cutOrigin` | posición en la placa (`cutOrigin: "rightTop"`) |
| `edgeInfo` | cantos en notación `←0↓0→1↑0` |
| `holes` / `oriHoles` | agujeros de **cara** |
| `sholes` / `oriSholes` | agujeros **laterales** |
| `slots` / `oriSlots` | ranuras de cara |
| `sslots` / `oriSslots` | ranuras de canto |
| `curveHoles`, `millInfo`, `realCurve`, `realCurveEx` | curvas y fresados |
| `connection_types` | `{"front":"三合一","right":"三合一",...}` herraje por lado |
| `texDir`, `axis` | dirección de veta |
| `installNum`, `simplePlankNum` | nº de montaje y nº corto (`1-6`) |

Ejemplo de un agujero de cara y uno lateral:

```json
{"type":"hole",  "deep":13.5, "side":1, "center":{"x":44,"y":534},
 "ocenter":{"x":41,"y":531}, "diameter":15, "holeType":"bigHole",
 "symbol":"3in1Lock", "uniqueId":387}

{"type":"shole", "deep":33, "side":2, "center":{"x":329,"y":9,"z":370},
 "ocenter":{"x":41,"y":564}, "diameter":8, "holeType":"sideHole",
 "symbol":"3in1Lock", "uniqueId":387}
```

Y una ranura:

```json
{"type":"slot","side":1,"pt1":{"x":374.5,"y":14.85},"pt2":{"x":374.5,"y":589.15},
 "deep":6,"width":6,"length":574.3,"symbol":"BP"}
```

**Taxonomía de `symbol`** (tipo funcional del agujero/ranura):

| symbol | Qué es |
|---|---|
| `3in1Lock` | tres-en-uno (excéntrica Ø15 + pre-embedded Ø10 + varilla Ø8) |
| `HINGE` | cazoleta de bisagra Ø35 |
| `HINGESCREW` | tornillo de bisagra Ø6 |
| `jlHoleEX` | agujero auxiliar Ø6 |
| `BP` | ranura de fondo (Back Panel) |
| `lightSlot` | ranura de luz LED |

**Convención de `side`**: en `holes`, `1` = cara frontal, `-1` = cara trasera.
En `sholes`, identifica cuál de los 4 cantos.
`center` = coordenada final; `ocenter` = coordenada original antes de compensaciones.

---

## 12. Notas para la Etapa 2 (reemplazar GuiGui)

Lo que hay que replicar, en orden de dificultad:

1. **Generador de archivos de máquina** (lo más fácil y lo más valioso). Dada una lista de
   piezas con sus agujeros/ranuras, emitir `.ban`, `.mpr`, `.xml` y el `.xls` de la sierra.
   Los formatos están especificados en la sección 4 con ejemplos literales. **Empezar por acá**:
   se puede validar contra los archivos de referencia de Bluen sin tocar ninguna máquina.
2. **Optimizador de despiece** (nesting/guillotina). Hay librerías y algoritmos conocidos;
   `layoutConfig` da los parámetros que usa GuiGui (`plankEdgeOff: 18`, `cutKnifeRadius: 3`).
3. **Modelo paramétrico del mueble** — de un cuerpo con medidas y herrajes a la lista de
   piezas con sus agujeros. Acá es donde Inventor (iLogic) o Fusion aportan: el modelo 3D
   ya existe y sólo hay que extraer la geometría. La taxonomía de `symbol` (sección 4.7)
   es el puente entre "herraje" y "agujeros concretos".
4. **Generación de etiquetas con QR** — trivial una vez definido el código de barras.

**Estrategia de validación**: cualquier generador propio se puede verificar contra los
archivos de referencia guardados (`Six-sided drill-试生产样品柜/`) antes de mandar nada a
una máquina. Mismo mueble, mismos números, diff de texto.

**Pista a explorar**: el servicio **MCP en localhost:8010** que levanta GuiGui podría dar
acceso programático a sus datos y evitar tener que reimplementar el modelo paramétrico
desde cero, al menos en una etapa de transición.

---

## 13. Etapa 2 — generador propio de archivos de máquina

_Agregado el 20/09/2026._

Carpeta **`etapa2/`**. Python 3 sin dependencias (salvo `openpyxl`, opcional, para el
.xlsx de la sierra). Corre igual en la Mac y en la PC de la sierra.

### Qué hace

Lee el `<ORDEN>-Mass production.json` que exporta GuiGui y emite:

| Salida | Destino |
|---|---|
| `.ban` MicroDrawBan XML 3.0 | perforadora SKH-612HS |
| `.mpr` WoodWOP / Homag (+ archivo `K` de cara trasera) | perforadoras compatibles MPR |
| `.xml` formato "Plate" (XML1) | idem |
| `.xml` formato KDT (XML3) | idem |
| `lista_corte.csv` / `.xlsx` | AutoCUT → sierra HP280 |
| `HOJAS_VERIFICACION.html` | dibujo acotado por pieza, para imprimir y medir |

**Resuelve el problema de la sección 6**: los `.ban` de GuiGui salen sin los agujeros
verticales ni las ranuras; los generados los tienen todos.

### Estado de validación

Todo verificado contra los archivos de referencia de Bluen, con diff semántico:

| Formato | Resultado |
|---|---|
| BAN | 12/12 · idénticos salvo la línea de encabezado con la fecha |
| MPR | 12/12 · **byte a byte idénticos**, incluidos los 4 archivos `K` |
| XML1 | 12/12 · geometría idéntica (difiere el orden interno de elementos equivalentes) |
| XML3 | 12/12 · **byte a byte idénticos** |
| Lista de corte | 10/10 piezas × 19 columnas, contra el `开料清单.xls` de GuiGui |

### Archivos

| Archivo | Qué es |
|---|---|
| `panel.py` | modelo interno de pieza — el esquema propio de la sección 12 |
| `guigui.py` | lector del `Mass production.json` |
| `ban.py` `mpr.py` `xml1.py` `xml3.py` | escritores, uno por formato |
| `exportar.py` | CLI: genera los cuatro formatos |
| `listacorte.py` | CLI: lista de corte para AutoCUT |
| `hojas.py` | CLI: hojas de verificación imprimibles |
| `validar.py` | diff semántico contra archivos de referencia |

El día que el origen sea Inventor en vez de GuiGui, **sólo se reemplaza `guigui.py`**.
Todo lo demás habla contra el modelo `Panel`.

### Cosas que se descubrieron al hacerlo

**La transformación de coordenadas.** El JSON usa Y hacia abajo y guarda la pieza en la
orientación de diseño; el `.ban` usa Y hacia arriba y la guarda siempre en retrato.

```
si  oRect.width <= oRect.height   →   X = x        Y = H − y
si  oRect.width >  oRect.height   →   X = H − y    Y = W − x    (rota 90°)
```

Se usan `ocenter` / `opt1` / `opt2` / `realCurve` (marco de la pieza terminada).
Los campos `center` / `pt1` / `pt2` están en el marco de la placa nesteada y **no sirven**
para el archivo de pieza. Ése fue el origen del error de cotas de la sección 5.

**Z se mide siempre desde la cara A.** Un agujero de cara B va de `Z = −espesor` a
`Z = −(espesor − profundidad)`. Las ranuras de cara B, en cambio, llevan `Z = −profundidad`
en el BAN base (la variante BAN2 las cota desde la cara A).

**El MPR parte la pieza en dos programas.** El archivo `K` lleva la **X espejada**
(`X' = LA − X`) y la profundidad real desde esa cara. El MPR además **no representa
contornos irregulares** — la pieza con arco va con el rectángulo envolvente, igual que
en la referencia de Bluen. Y GuiGui **no emite `.mpr` para piezas sin mecanizado**.

**XML3: dos cosas que faltaban en la sección 4.4.** `TypeNo 8` es agujero vertical de
**cara trasera**, y los cuadrantes del agujero horizontal son 1 = derecha, 2 = izquierda,
**3 = arriba, 4 = abajo**.

**Cantos: `前封边` (delante) es el canto de ARRIBA** del marco original, y `后封边` el de
abajo — al revés de lo que sugiere el nombre. Verificado con las dos fascia boards, las
únicas piezas de PRUEBA 1 con delante y atrás distintos.

**GuiGui no rota los flags de canto cuando rota la pieza.** Rota las medidas pero deja los
cantos en el marco original. El generador replica ese comportamiento por defecto
(`--edges-like-guigui`); la opción geométricamente correcta también está disponible.

### Pendiente de verificar

1. **Ranuras de canto (`sslots`) y fresados (`millInfo`, `curveHoles`)** — no hay ninguna
   pieza de referencia con eso. El código las pasa, sin validar.
2. **Medida terminada vs. de corte** — el archivo de máquina lleva la medida **terminada**
   (173 × 350), no la de corte (171 × 348). Es lo que hace Bluen, pero implica que la
   perforadora espera la pieza ya canteada, o que compensa. Confirmar con calibre.
3. **Regla de rotación** — deducida como "el lado largo va sobre Y". Consistente con las
   22 piezas verificadas, pero podría depender en realidad de la veta.
4. **`Grain` queda fijo en `2`** — todas las piezas vistas tienen `texDir: normal`.
5. **`EdgeFBLR` en piezas rotadas** — si la perforadora usa ese dato para compensar el
   canto, las dos opciones dan posiciones distintas. Medir la primera fascia board.

---
