# FÁBRICA MUEBLES — Contexto técnico del proyecto

_Última actualización: 22/09/2026 — armado con Claude durante la puesta en marcha de la línea._

> **Cómo retomar con Claude**: abrir un chat con esta carpeta conectada y decir
> "leé CONTEXTO.md y seguimos desde el punto X".
>
> **Estado del proyecto → sección 15. Hoja de ruta (objetivo y etapas) → sección 16. MCP de GuiGui y modelos 3D bajados → sección 17.**

---

## 0. Objetivo y etapas

**Etapa 1 (en curso)** — poner en marcha el flujo completo de producción de muebles de placa:
diseño → despiece → corte → etiquetado → perforado → cantos → armado.

**Etapa 2 (EN CURSO — generador de archivos de máquina ya funcionando)** — **reemplazar GuiGui**. El software es malo:
UI rota (textos superpuestos, mezcla chino/inglés, layout que no se adapta), configuración
atada a un servidor en China, verificación por SMS en cada cambio, bloqueos arbitrarios.
La idea es construir algo propio: una aplicación, un iLogic para Inventor, un plugin para
Fusion, o un generador independiente. **Por eso este documento describe los formatos de
archivo de cada máquina con ejemplos literales**: son la especificación de salida que
cualquier reemplazo tiene que cumplir. Si se generan esos archivos correctamente, las
máquinas no se enteran de que GuiGui desapareció.

> **Estado 20/09/2026**: el generador existe y está validado. Ver la **sección 13**.
> Lee el `Mass production.json` y emite `.ban`, `.mpr`, XML1, XML3 y la lista de corte
> de la sierra, todo verificado contra los archivos de referencia de Bluen.
> Carpeta: `etapa2/`.

---

## 1. Parque de máquinas

| Equipo | Modelo | Rol | Control / software | Consume |
|---|---|---|---|---|
| Diseño | GuiGui 柜柜 v5.0.0.4global-9 (Mac) | Diseño paramétrico y despiece | Cliente Electron + nube **bluen.cn** | — |
| Optimizador | AutoCUT | Optimización de corte para la sierra | Windows, PC de la sierra | Excel/CSV |
| Sierra | **HP280** (HUAHUA) | Corte recto seccionadora | Control HUAHUA propietario (gabinete azul) | archivo `.CUT` generado por AutoCUT |
| Router | **SKG-912MZ** | Nesting: corte con fresa, ranuras, agujeros de cara | **Syntec** | `.nc` (código G) |
| Perforadora | **SKH-612HS** | Agujeros en 6 caras, ranuras, fresados | **CncMon32** (Syntec) + **HHcnc** | 1 archivo por pieza, nombre = código de barras |
| Pegadora de cantos | **HH-509R** | Cantos | — (manual) | nada, el operario lee la etiqueta |
| Impresora etiquetas | **AIBAO BC-80152T** | Etiquetas térmicas con QR | Driver solo Windows, instalada en la PC de la sierra | imprime desde AutoCUT o desde el control ("Imp Lbl") |

**Fabricante de la perforadora**: Guangdong Shunde Changsheng Machinery Manufacturing Co., Ltd.
(广东顺德长盛机械), marca comercial **Huahua CNC** — el mismo HUAHUA de la sierra.
Manual: `User Manual_SKH-612 Series_260706_115944.pdf` (series SKH-690 / SKH-612H / SKH-612S).

**Contacto proveedor**: Sra. Tan (谭小姐), por WeChat.
**Cuenta GuiGui/Bluen**: verificada por SMS al celular terminado en **2352**.

---

## 2. Flujo de trabajo completo

```
GuiGui (diseño 3D paramétrico del mueble)
   │
   ├─ Output → layout → Start layout   (optimización de despiece, online vía Bluen)
   │
   └─ Output NC file → Export NC file
         │
         └─ escribe en  <destino>/<ORDEN>/BluenNC/
              ├─ saw/开料清单.xls ............ lista de corte  → AutoCUT → .CUT → SIERRA HP280
              ├─ 下料文件/*.nc ............... código G nesting → ROUTER SKG-912MZ
              ├─ <carpeta plantilla>/*.ban ... 1 archivo x pieza → PERFORADORA SKH-612HS
              ├─ new_nc_params.json .......... parámetros del post-procesador
              └─ <ORDEN>-Mass production.json  TODO el layout + geometría (la mina de oro)

Sierra corta las piezas  →  se imprimen y pegan las etiquetas con QR
   ↓
Perforadora: se escanea el QR → busca el archivo cuyo nombre = código de barras → mecaniza
   ↓
Pegadora de cantos (operario lee la etiqueta)
   ↓
Armado
```

**Dos rutas alternativas de corte**: sierra (corte recto, más rápido para piezas rectangulares)
o router en nesting (permite formas irregulares y hace agujeros/ranuras de cara en la misma
operación). Hoy se usa la sierra.

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

## 5. Parámetros de herrajes y placa

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

## 6. Estado actual

### ✅ Hecho y validado

1. GuiGui configurado: placa 2440 × 1210, líneas de producción.
2. **Flujo de sierra completo, probado punta a punta** con PRUEBA 1 (orden 260625-20).
   Piezas del gris cortadas, etiquetas impresas y pegadas.
3. **Línea de producción configurada en Bluen** (Device Link → Line Mgmt):
   - **"SIERRA + PERFORADORA"** — Cutting Equipment = *Electronic Saw*;
     H&S Equipment = *Five/Six-Face Drilling Machine* (Equipment Type: **Six-Sided Drill**).
     ⚠️ El cliente de GuiGui la sigue mostrando como **"Default production line"** (cachea
     el nombre viejo). Es la correcta.
   - **"New Production Line 1"** — Engraving machine (router), H&S = *Not Enabled*.
4. **El export ya genera solo el archivo de la sierra** (`BluenNC/saw/开料清单.xls`) —
   reemplaza la conversión manual del xmlFile a CSV que se hacía antes.
5. Knife Storage de la perforadora cargado con las 2 fresas de ranurar (Ø6 nº1, Ø9 nº2).
6. **Mueble de muestra de Bluen ejecutado**, con archivos de referencia en los 8 formatos.
7. Tablero resumen en FigJam: https://www.figma.com/board/0xeK22MK3OofuUNPr21bis

### ✅ RESUELTO (20/09/2026) — drill files incompletos

**La solución fue no usar el exportador de GuiGui.** El `<ORDEN>-Mass production.json`
tiene toda la geometría que a los `.ban` les falta. El generador de `etapa2/` la lee y
escribe los archivos completos. No hizo falta ni Bluen ni la Sra. Tan.

El diagnóstico de abajo queda como documentación de qué hacía mal la plantilla.

#### Diagnóstico original

**Síntoma**: los `.ban` que genera GuiGui para la SKH-612 contienen **sólo los agujeros
laterales** (`HoleH`). Faltan **todos** los agujeros verticales (`HoleV`) y **todas** las
ranuras (`SlotL`).

**Evidencia dura** — mismo panel, misma orden, mismo momento:

| | Referencia Bluen (`Six-sided drill-…/BAN/`) | Nuestra plantilla (`自定义六面钻/`) |
|---|---|---|
| Orientación | 173 × 350 | **350 × 173 (rotada 90°)** |
| `HoleV` | 4 × Ø15 prof 13,5 cara A | **ninguno** |
| `HoleH` | 4 × Ø8 caras **R / L** | 4 × Ø8 caras **U / D** |
| `SlotL` | 2 × ancho 6, caras A y B | **ninguna** |
| Material | `多层实木` (el real) | `颗粒板` (fijo en la plantilla) |
| Atributo | `Height` | `Hight` (typo) |
| Nombre | `主卧_地柜A_竖隔板01` | `竖隔板01` |
| Timestamp | fecha real | congelado en `2022/04/06` |

**Plantilla seleccionada actualmente**: `六面钻BAN洪德（贺耀）(.BAN)`.
En la lista de "Generated File Type" **no existe ninguna plantilla de Changsheng / Huahua**.
Hay: 南兴 (Nanxing), 豪迈 (Homag), 极东 (Jidong), 先达 (Xianda), 星辉 (Xinghui),
迪马 (Dima), 瑞诺, 郑太, 亨达, 桦桦, 品迈, 迈盛达, 金雕, 宏大博刻… y genéricas
`xml2`, `mpr`, `dxf`, `ban`.

**Hipótesis principal**: no es (sólo) la plantilla, es la **distribución de agujeros entre
máquinas** (孔槽分流). GuiGui parece asignar los agujeros de cara y las ranuras a la máquina
de corte — patrón normal en una línea con router — y como acá la máquina de corte es una
sierra, se pierden. La línea SIERRA + PERFORADORA **no muestra panel "Processing Settings"**
donde cambiar ese reparto (en la línea del router sí aparece, con la opción
*Processing Method: Only Cutting / Only Process Front Holes / Only Process Front and Back*).

**Pista**: la página de la perforadora menciona dos veces **"Huahua automatic line"**
(华华自动线) — Bluen conoce al fabricante. Falta encontrar dónde se activa.

**Archivos de referencia guardados — NO BORRAR**
`~/Downloads/NCFolder/试生产样品柜_主卧/BluenNC/`

```
Six-sided drill-试生产样品柜/
    BAN/ BAN2/ BAN3/ BAN4/ BAN_SC/   ← .ban completos y correctos
    MPR/                              ← .mpr (+ variantes K de cara trasera)
    XML1/ XML3/                       ← los dos dialectos XML
Trial production sample cabinet sample picture/
    Hole map.png
    Plate hole and slot diagram.pdf   ← plano acotado de agujeros y ranuras
    Process settings.png              ← parámetros de herrajes
    sample1-4.png, Special1-3.png
saw/开料清单.xls
下料文件/*.nc
自定义六面钻/                          ← lo que genera nuestra plantilla (incompleto)
试生产样品柜-Mass production.json
```

---

## 7. Notas de operación de GuiGui / Bluen (aprendidas a los golpes)

- **La configuración de equipos vive en la nube** (`bluen.cn`), no en la Mac. Si la app no
  llega al servidor, el generador de NC falla con errores tipo `找不到刀具T1`
  ("no se encuentra la herramienta T1").
- El cliente **cachea los nombres de línea**: renombrar en Bluen no se refleja en el
  desplegable de GuiGui.
- **Cada cambio de configuración pide código SMS.** Agrupar todos los cambios antes de guardar.
- Después de configurar en Bluen, **NO guardar en la página de device docking del cliente**:
  resetea los parámetros (lo avisa en rojo la propia página).
- **Cambiar la plantilla de la perforadora bloquea el software** hasta hacer la "producción de
  prueba del mueble de muestra", o firmar un descargo de responsabilidad que pide foto del
  mueble armado + teléfono + SMS. El botón **"Trial production sample cabinet"** carga el
  mueble de muestra en la lista de órdenes y destraba — y de paso entrega los archivos de
  referencia en todos los formatos, que es oro puro.
- El **Knife Storage** de la perforadora es para **fresas** (compensa el radio de corte),
  no para mechas. Las mechas viven en el Knife Library de HHcnc, en la máquina.
  Cada fila necesita "Knife Number" **único y no vacío** o no deja guardar
  (`刀库-刀具编号重复或为空，请检查`).
- La UI está rota: textos superpuestos, botones cortados, mezcla de chino e inglés,
  layout que no se adapta a la pantalla. Leer los carteles con cuidado igual, algunos importan.
- GuiGui levanta un **servicio MCP en `localhost:8010`** (lo muestra en verde abajo a la
  derecha: `MCP服务已启动, 端口: 8010, 版本: 1.1.1`). **Pendiente de explorar** — podría
  permitir automatizar GuiGui desde afuera, o ser una vía de integración para la Etapa 2.

### Secuencia de encendido de la SKH-612HS (del manual, sección 8)

1. Encender equipo y **vacío**.
2. **COMPUTER START** en el panel → esperar a que la PC industrial arranque **por completo**.
3. **POWER** → esperar ~1 minuto.
4. Doble clic en **CncMon32** → verificar estado **"ready"** (la alarma no debe titilar) → minimizar.
5. Doble clic en **HHcnc** → interfaz de operación.
6. Importar archivos/directorio → pasar a **modo escaneo** → escanear QR → colocar la placa.
7. **Botón verde dos veces**: la primera deja la máquina esperando la pieza, la segunda mecaniza.

Apagado: cerrar HHcnc → CncMon32 → apagar la PC normalmente → recién ahí cortar la energía.
**Entre apagado y encendido deben pasar más de 60 segundos.**

Idioma: HHcnc → botón (S) en el área de proceso → system settings → language.
CncMon32 → F8 System Management → F3 parameter setting → F5 jump to parameter →
parámetro **3209** = `0` para inglés.

Si tras un corte de energía aparece un archivo raro: F2 Program Edit → F8 File Management →
doble clic en `o010000` → F1 cargar y ejecutar.

Mantenimiento: engrasar los packs de mechas cada **120-150 horas** con **Klüber L32-N**.

### Procesos que soporta HHcnc

Agujeros verticales, agujeros horizontales, ranuras, fresado, fresado rectangular,
fresado circular, chaflán, **Lamello** y **Locking**. Cubre todo lo que necesita PRUEBA 1.

---

## 8. Problemas resueltos (por si vuelven)

- **E03** — empujador no está en origen de carga: botón **MatRes** en manual, o la placa está
  mal orientada / demasiado metida.
- **E08 / Er17-1** en el drive INVT DA200 = **sobrecarga del servo del empujador**, NO es un
  servo roto. Causa típica: placa cruzada o material trabado. Se resetea cortando la energía
  general 1 minuto. Si el puente del empujador queda torcido (un lado al tope, el otro
  separado), **escuadrarlo antes de seguir**.
- **E16** — carro de sierra fuera de origen: Alarma Off + VolOrig completo.
- La pantalla "alarma" del control **es un catálogo de códigos**; las alarmas activas
  aparecen en la franja roja de abajo.
- **`找不到刀具T1`** al exportar: la línea de producción apuntaba al router y su almacén de
  herramientas estaba vacío (o no había conexión con bluen.cn).
- **`ERR_SOCKET_NOT_CONNECTED`** al abrir Equipment integration: la ventana embebida perdió
  la red. Reintentar, o abrir `https://www.bluen.cn` en Chrome. El servidor suele estar bien.

---

## 9. Operación de la sierra HP280 (probada)

1. AutoCUT: Importar → "Importar varios materiales" → "Coincidencia" para mapear columnas.
   `开料长`/`开料宽` → **"Longitud/Ancho de apertura"**.
2. Optimizar → Guardar como `.CUT`.
3. En el control HUAHUA: **Alarma Off** → **VolOrig** (homing) → **automático** → **Carg Arch**
   → seleccionar **sólo el material que se va a cortar**.
4. Cargar la placa con el **lado de 1210 contra las pinzas**.
5. Botón verde.
6. **Corta por niveles**: placa → tiras → girar la tira 90° y recargar según indique el dibujo
   en pantalla.

Etiquetas: se imprimen en la AIBAO desde AutoCUT.
⚠️ Pendiente: el campo "código de barras" en AutoCUT quedó mapeado como `P01, P02…` en vez
del código largo de GuiGui. **Corregirlo** si se imprimen etiquetas desde AutoCUT, porque
la perforadora busca el archivo por ese código.

---

## 10. Lo que FALTA (en orden)

1. ~~**Resolver los drill files incompletos.**~~ ✅ Resuelto con el generador propio
   (sección 13). Ya no depende de Bluen ni de la Sra. Tan.
   Sigue abierta una sola pregunta, y se contesta mirando la máquina, no preguntando:
   **qué formato lee HHcnc exactamente**. Para eso están las cuatro carpetas de
   `etapa2/salida/PRUEBA1/`.
2. **Primer encendido de la SKH-612HS** y chequeo del **Knife Library** contra las mechas
   físicas (tabla de la sección 5).
3. **Primera pieza**: el techo 400 × 600. Importar en HHcnc, escanear QR, procesar y
   **medir todo con calibre** — especialmente que no salga espejado.
4. **Pegar cantos** (HH-509R) y armar PRUEBA 1.
5. **Cerrar el flujo del router**: en la línea "New Production Line 1" falta cargar T1 Ø6
   en su almacén de herramientas. Después comparar la salida contra la muestra china
   (carpetas CUT / PRINT / ROBOT que está en WeChat, carpeta 2026-08, `加工程序`).
6. **Verificaciones**: espesor real del canto (si no es 1 mm hay que regenerar el despiece),
   kerf real de la hoja de sierra, mapeo del código de barras en AutoCUT.

---

## 10-bis. PROTOCOLO DE PRUEBA EN LA SKH-612HS (pendiente — próximo paso)

> Este es el checklist concreto para la primera prueba en la perforadora.
> Estado al 16/09/2026: **no ejecutado todavía**.

> ### 📋 22/09/2026 — ver antes `MAÑANA_EN_LA_MAQUINA.md`
>
> Una hoja con las **6 preguntas que sólo se contestan frente a la máquina**, cada una
> con la respuesta concreta que hay que traer. Lo de abajo sigue siendo el protocolo de
> encendido y operación.
>
> La carpeta `PENDRIVE/` ya está armada, con **las mismas 10 piezas dos veces**:
> `1_DESDE_GUIGUI` (el control) y `2_DESDE_FUSION` (modeladas en Fusion sin abrir
> GuiGui), más `3_PIEZA_CURVA`. Si la máquina procesa los dos juegos igual, el camino
> Fusion queda probado sobre metal.

### ⚠️ Actualizado el 20/09/2026 — ahora se prueba con PRUEBA 1

Antes había que probar con el mueble de muestra porque los `.ban` de PRUEBA 1 salían
incompletos. **Ya no.** El generador de `etapa2/` produce los archivos completos de
PRUEBA 1 en los cuatro formatos, y están en:

```
etapa2/salida/PRUEBA1/
    BAN/ MPR/ XML1/ XML3/          ← las cuatro carpetas para el pendrive
    HOJAS_VERIFICACION.html        ← dibujo acotado de cada pieza, para imprimir
    LEEME.txt                      ← el protocolo paso a paso
    lista_corte.csv / .xlsx        ← para AutoCUT
```

**Llevar esa carpeta entera.** La pieza de prueba pasa a ser el **techo 400 × 600
(9441838670057)**, que es la primera de PRUEBA 1 y tiene agujeros, ranura de cara A y
ranura de cara B. El detalle está en el `LEEME.txt`.

Lo de abajo queda como referencia del protocolo original con el mueble de muestra.

#### Protocolo original (mueble de muestra)

### Pieza elegida para la prueba

**`竖隔板01` — código de barras `6893155441637`** · 173 × 350 × 18 mm

Es la mejor pieza de prueba porque contiene los tres tipos de operación a la vez:

| Operación | Detalle |
|---|---|
| 4 × agujero vertical | Ø15, profundidad 13,5 mm, cara A |
| 4 × agujero horizontal | Ø8, profundidad 34 mm, cantos L y R, a media placa (Z=9) |
| 2 × ranura | 6 mm de ancho × 6 mm de profundidad, caras A y B |

Herramientas mínimas necesarias: **vertical Ø15**, **horizontal Ø8**, **fresa de ranurar Ø6**.

### Dónde están los archivos

Carpeta raíz de referencia (⚠️ **mover a FABRICA MUEBLES, Downloads se limpia sola**):

```
~/Downloads/NCFolder/试生产样品柜_主卧/BluenNC/
│
├── Six-sided drill-试生产样品柜/     ← ARCHIVOS DE REFERENCIA, COMPLETOS Y CORRECTOS
│   ├── BAN/6893155441637.ban         ← llevar esta carpeta si HHcnc lee .ban
│   ├── BAN2/  BAN3/  BAN4/  BAN_SC/  ← variantes del mismo formato
│   ├── MPR/6893155441637.mpr         ← llevar esta si lee .mpr
│   │   └── 6893155441637K.mpr        ← ¡programa de la CARA TRASERA, segunda pasada!
│   ├── XML1/6893155441637.xml        ← llevar esta si lee formato <Plate>
│   └── XML3/6893155441637.xml        ← o esta si lee formato KDT
│
├── Trial production sample cabinet sample picture/
│   ├── Plate hole and slot diagram.pdf   ← PLANO ACOTADO de agujeros y ranuras (imprimir)
│   ├── Hole map.png
│   ├── Process settings.png              ← parámetros de herrajes
│   └── sample1-4.png, Special1-3.png     ← fotos del mueble armado
│
├── saw/开料清单.xls                  ← lista de corte del mueble de muestra
├── 下料文件/*.nc                     ← código G del router
├── 自定义六面钻/                     ← lo que genera NUESTRA plantilla (INCOMPLETO, no usar)
└── 试生产样品柜-Mass production.json
```

Carpeta de PRUEBA 1 (incompleta, sólo para referencia):
`~/Downloads/NCFolder/PRUEBA_PRUEBA-1/BluenNC/`

### Pasos, en orden

**1 · Encendido**
Equipo y vacío → **COMPUTER START** → esperar a que la PC industrial arranque **por completo**
→ **POWER** → esperar ~1 minuto → doble clic en **CncMon32** → verificar estado **"ready"**
(la alarma no debe titilar) → minimizar → doble clic en **HHcnc**.

**2 · Averiguar qué formato lee HHcnc** ← *el paso más importante, y es gratis*
En HHcnc, abrir el diálogo de **importar archivo/directorio** y mirar el **filtro de tipos de
archivo**. Ahí se ve si acepta `.ban`, `.mpr`, `.xml` o varios.
**Sacar captura.** Esto responde de una la pregunta que le íbamos a hacer a la Sra. Tan y
define qué plantilla hay que configurar en Bluen.

**3 · Knife Library**
Botón en el área de proceso de HHcnc (o menú S / 系统设置). Comparar la tabla contra las
mechas físicas instaladas. Anotar **qué número de herramienta tiene cada diámetro**.
Regla: al cambiar una mecha física, actualizar su diámetro en la tabla.
Para esta prueba hacen falta Ø15 vertical, Ø8 horizontal y fresa Ø6.
Para producción completa de PRUEBA 1 hacen falta además Ø6, Ø10, Ø35 verticales y fresa Ø9
(ver tabla de la sección 5).

**4 · Llevar los archivos** en pendrive — la carpeta que corresponda según el paso 2.

**5 · Cortar una pieza de 173 × 350 de 18 mm** de un recorte.
No hace falta cortar el mueble de muestra entero: con una pieza se valida todo.

**6 · Cargar el programa a mano y VERIFICAR EN PANTALLA antes de tocar nada**
Todavía no hay etiqueta con ese código de barras, así que en lugar de escanear el QR se
elige el archivo `6893155441637` de la lista.
En el dibujo tienen que verse: 4 agujeros en la cara, 4 en los cantos izquierdo y derecho,
y una ranura cruzando el ancho cerca de un extremo.
**Si el dibujo no coincide, parar ahí.**

**7 · Botón verde dos veces**
La primera deja la máquina esperando la pieza; la segunda mecaniza.
Seguridad: asegurarse de que no haya nadie cerca antes de insertar la placa.

**8 · Medir todo con calibre.** Valores esperados:

| Qué | Dónde | Valor |
|---|---|---|
| 4 × Ø15 en la cara | desde un borde de 173 | **33 mm** y **140 mm** |
| | desde un borde de 350 | **64 mm** y **286 mm** |
| | profundidad | **13,5 mm** |
| 4 × Ø8 en cantos L y R | desde un borde de 350 | **64 mm** y **286 mm** |
| | altura | **9 mm** (media placa) |
| | profundidad | **34 mm** |
| Ranura | desde un borde de 350 | **329,5 mm** |
| | ancho × profundidad | **6 × 6 mm** |
| | largo | cruza los 173 mm |

**9 · Interpretar el resultado**

- **Todo coincide** → máquina y formato validados. Siguiente: resolver el problema de los
  drill files incompletos (sección 6) para poder producir PRUEBA 1.
- **Medidas correctas pero espejadas** (ej. los Ø15 a 140/33 contados desde el borde opuesto)
  → problema de mirroring. No rompe nada. Se corrige con la orientación de carga o con los
  parámetros de la plantilla (`Plank Placement Method`, `Five/Six-Sided Drill Slot or Special
  Placement Direction`, o `ModusMirror` / `VIEW="NOMIRROR"` en el MPR).
- **Diámetros o profundidades mal** → la tabla del Knife Library no coincide con las mechas
  físicas. Volver al paso 3.
- **La máquina no abre el archivo** → formato equivocado. Probar otra de las carpetas de
  referencia (BAN → MPR → XML1 → XML3).

### Para acordarse de llevar

- Pendrive con la carpeta de referencia
- Calibre
- El **`Plate hole and slot diagram.pdf`** impreso (plano acotado de la pieza)
- Un recorte de 18 mm para cortar la pieza de 173 × 350

---

## 11. Preguntas abiertas a HUAHUA (Sra. Tan / 谭小姐, WeChat)

1. ¿Qué plantilla de GuiGui/Bluen corresponde a la **SKH-612HS**? ¿Qué formato importa HHcnc
   exactamente (`.ban`, `.mpr`, `.xml`)? ¿Pueden mandar un archivo de ejemplo real?
2. ¿El nombre del archivo **debe** ser el código de barras para que el escaneo del QR lo encuentre?
3. Perfil/configuración de GuiGui para el router **SKG-912MZ** y lista de herramientas
   instaladas con diámetros.
4. Manual de operación de la **HP280** y procedimiento para escuadrar el puente del empujador.
5. ¿La HP280 tiene puerto/opción para impresora de etiquetas integrada ("Imp Lbl")?

---

**(agregada 22/09/2026) ¿Cómo se declara una RANURA DE CANTO en el `.ban`?** Un canal
fresado en el borde de la placa — el típico para el fondo. En los 82 archivos de
referencia que tenemos no hay ni uno, y el vocabulario del `.ban` que sí aparece es sólo
`Plane, Outline, Point, HoleV, HoleH, SlotL`. ¿Hay un elemento para eso, o esa operación
no la hace la SKH-612HS y va en otra máquina?

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

**Todavía no hay remoto.** Si se quiere respaldo fuera de la Mac hay que crear un
repo en GitHub o similar y agregarlo con `git remote add origin ...`.

> Nota: git necesita borrar sus propios temporales (`index.lock`, `tmp_obj_*`).
> Si alguna vez se traba con "Operation not permitted", es eso.

---

# 16. HOJA DE RUTA — hacia dónde va todo esto

_Agregado el 22/09/2026, después de definir el objetivo completo del proyecto._

## 16.1 · El objetivo, en tres frases

1. **Fabricar todo lo modelado en GuiGui**, camino 100 % funcional.
2. **Modelar en Fusion y fabricar con nuestras máquinas**, camino 100 % funcional.
3. **Tienda online** con ~10 modelos, visor y configurador 3D (medidas generales y
   alguna opción, sin salir de la estandarización). Pedido confirmado y pagado →
   se dispara toda la documentación del mueble.

**"100 % funcional" significa siempre lo mismo**: programas de máquina + lista de
corte + **etiquetas** + **manual de armado de 1-2 hojas** (los muebles se entregan
desarmados). Ese conjunto se llama de acá en adelante el **paquete de producción**.

## 16.2 · La idea que ordena todo: un motor, tres entradas

No son tres caminos. `etapa2/` —el modelo `Panel` y sus escritores— **ya es el
motor**. GuiGui (`guigui.py`) y Fusion (`fusion_json.py`) son dos formas de llenar
`Panel`. La web va a ser la tercera. Todo lo que falta (etiquetas, manual, precios)
se construye **una vez, sobre `Panel`**, y sirve para las tres entradas.

Consecuencias:

- **Camino 1 (GuiGui): no invertir más.** Está 41/41. Queda como respaldo. Lo que
  le falta es lo mismo que le falta al camino 2, y se hace una sola vez.
- **Camino 2 (Fusion) es la columna vertebral.** Se cierra sobre metal en la Etapa 0
  y se estresa con muebles distintos después.
- **Camino 3: el configurador NO depende de Fusion en tiempo de ejecución.** Fusion
  es de escritorio y licenciado; correrlo en un servidor cuando entra un pedido es
  caro y frágil. Cada uno de los 10 modelos será una **receta paramétrica en
  código**: una función Python que, dadas medidas y opciones, devuelve la lista de
  `Panel` con sus agujeros. Fusion sirve para **diseñar y validar** la receta (se
  modela el mueble, se exporta, y `validar.py` compara contra lo que da la receta —
  la misma metodología de oráculo de las secciones 13 y 14). El pedido → archivos
  corre puro código, en segundos. El visor 3D dibuja a partir de la misma receta.
- **El manual de armado sale casi gratis**: `PonerHerrajes` ya conoce el grafo de
  uniones del mueble. De ahí se deriva el orden de armado y la vista explotada.

## 16.3 · Las etapas

| Etapa | Qué | Cuándo está terminada |
|---|---|---|
| **0 · Sobre metal** | `MAÑANA_EN_LA_MAQUINA.md`: formato de HHcnc, Fusion vs GuiGui, terminada vs corte, `EdgeFBLR`, veta en AutoCUT, herraje 33 vs 34 | Las 6 preguntas contestadas y anotadas acá |
| **1 · Paquete de producción** | Generador propio de etiquetas con QR (hoy AutoCUT, con el código mal mapeado, §9); manual de armado generado en 1-2 hojas (explotada + pasos por unión + lista de herrajes); ranura de canto resuelta con la Sra. Tan; **fabricar y armar PRUEBA 1 completo** con ese paquete | Caminos 1 y 2 son 100 % funcionales según la definición de 16.1 |
| **2 · Estresar Fusion** | 2-3 muebles distintos de cero: cajonera con correderas, algo con zócalo y patas, estantes regulables. Cada herraje nuevo entra a `PonerHerrajes` **medido**, como el 3 en 1 | Lista real de herrajes de la casa (que después es lista de precios y de compras) |
| **3 · Recetas** | Los 10 modelos como código paramétrico con rangos permitidos y opciones; cada receta validada contra su modelo de Fusion; esquema propio de códigos de barras y nº de orden; costo por m² + herrajes. Sin web: un CLI que dice "modelo 4, 900×2100×450, 2 puertas" y devuelve el paquete | Los 10 modelos producen paquete completo desde la línea de comando |
| **4 · Visor y configurador 3D** | Página con three.js que lee las mismas recetas, deja mover medidas dentro de los rangos, muestra mueble y precio en vivo. Sin carrito. Ya sirve para vender | Se configura y se ve cualquiera de los 10 modelos en el navegador |
| **5 · Tienda y disparo** | Catálogo, carrito, pago (Mercado Pago), y al confirmarse: correr receta → paquete en carpeta de orden en la fábrica → aviso por mail. Panel interno mínimo de pedidos y estados | Un pedido pagado por un desconocido termina en un pendrive listo para la máquina |

Las etapas 0-2 son de taller y código; 3-5 son de producto. **No empezar la 4 ni la
5 antes de tener la 3**: el riesgo es terminar con un configurador lindo que no
puede fabricar nada.

## 16.4 · Antes de todo eso

- **Remoto de git.** Repo privado en GitHub (o similar) y `git remote add origin`.
  Hoy el único respaldo es esta Mac.
- Decidir el herraje de la casa: **perno 33 o 34** (§15.5).
- Verificar canto real y kerf real (§5) — condicionan la lista de corte.

## 16.5 · Estado por etapa

| Etapa | Estado |
|---|---|
| 0 | ⏳ se ejecuta 23/09/2026 |
| 1 | ⬜ |
| 2 | ⬜ |
| 3 | ⬜ |
| 4 | ⬜ |
| 5 | ⬜ |

> Actualizar esta tabla al cerrar cada etapa, y anotar en la sección que
> corresponda qué se aprendió.

---

## 15.10 · Camino Fusion completo, probado como se va a usar (22/09/2026, noche)

`fusion/ArmarPrueba1` modela PRUEBA 1 **armado**, sin ningún agujero de herraje,
con las posiciones sacadas del `render.json` de GuiGui (§17). `PonerHerrajes`
encontró las 12 uniones y puso los 20 tres en uno y las 4 bisagras solo.
`validar.py` contra el oráculo: **XML3 10/10; BAN/XML1 8/10 y MPR 9/11, donde
lo único distinto es el flag de canto de los dos zócalos** (la rareza de GuiGui
de §13). Los 80 agujeros coinciden en las 10 piezas.

Tres reglas de GuiGui que aparecieron y quedaron en el código
(detalle en `fusion/README.md`, sección `ArmarPrueba1`):

1. **Conectores en grilla de 32 mm**, mínimo 40 del extremo, centrados
   (400 → 40/360, 370 → 41/329, 564 → 42/522); uniones ≤ 200 mm llevan uno.
2. **La excéntrica va en la cara menos visible**: abajo en horizontales, atrás
   en zócalos, hacia adentro en laterales. El piso es la excepción: GuiGui lo
   da vuelta para que la ranura del fondo quede en A.
3. **GuiGui es mano izquierda**: `x_fusion = −x_guigui`.

Y dos correcciones a `PonerHerrajes`: `_cara_hacia` suponía que la cara A era
siempre la coordenada mayor del mundo (falso), y faltaba excluir puertas y
fondos de las uniones (`ROL`).

**Herrajes dibujados.** `PonerHerrajes` pone además el cuerpo de cada herraje
(excéntrica, perno, receptor, bisagra completa) como componentes `TIPO =
HERRAJE`, para la explotada y el manual de armado. El exportador los ignora; la
validación no cambia. El mueble queda parado (Z arriba, frente −Y).

# 17. El MCP de GuiGui — explorado el 22/09/2026

La pista de §7 y §12 dio resultado. Detalle completo en **`referencia/GUIGUI_MCP/LEEME.md`**
y `tools.md`.

- Endpoint: `POST http://127.0.0.1:8010/guigui-mcp` (Streamable HTTP, sin auth, sesión
  por header `Mcp-Session-Id`). Sólo alcanzable desde la Mac; desde Claude se llega con
  el **navegador integrado** de la app (el Chrome conectado es la PC Windows).
- `project_search_order` devuelve, para cada habitación, la URL de un **`render.json`
  público en Aliyun** con el **modelo 3D completo**: cada placa con posición (`anchor`,
  `axis`, `vertices`), código de barras, agujeros/ranuras (mismo esquema que el
  `Mass production.json`), cantos, material, veta y herrajes por placa.
- Ya bajados a `referencia/GUIGUI_MCP/`: **PRUEBA 1**, **COCINA MLV** (14 gabinetes,
  116 placas) y **Placard - malvinas** (87 placas). No hizo falta exportar nada a mano.
- El MCP también permite **crear y editar muebles** (`design_create_model`,
  `design_edit_model`, `cdesign_*`) y guardar. Queda como opción para automatizar
  GuiGui mientras siga en uso; no se probó ninguna herramienta que escriba.
- La API cambió 7 veces en 6 meses (ver changelog). Sirve para **extraer**, no para
  apoyar producción encima.

**Consecuencia para §16:** el `render.json` es la tercera entrada del motor y trae el
armado, que al `Mass production.json` le faltaba. Con él se puede reconstruir el
ensamble en Fusion y derivar el manual de armado sin adivinar posiciones.
