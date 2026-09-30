# FÁBRICA MUEBLES — Contexto técnico del proyecto

_Última actualización: 30/09/2026 — armado con Claude durante la puesta en marcha de la línea._

> **Cómo retomar con Claude**: abrir un chat con esta carpeta conectada y decir
> "leé CONTEXTO.md y seguimos desde el punto X".
>
> **Estado del proyecto → sección 15. Hoja de ruta (objetivo y etapas) → sección 16. MCP de GuiGui y modelos 3D bajados → sección 17. Web de curvado por ranuras (`curvado/`, Vercel) → sección 20. Herrajes Häfele equivalentes → sección 23. Respuestas de Huahua del 30/09 (y la Ø35 frenada) → sección 26.**

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

**Pegadora de cantos HH-509R** — manual: `instructivo/manuales/HH-509R_manual_pegadora_cantos.pdf`
(HUAHUA, *Automatic edge banding series user's manual*, 99 págs, en inglés: ajustes de cada grupo,
panel de control, parámetros, alarmas, mantenimiento y repuestos).

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
   **Rearmado el 23/09/2026** con todo este documento: 14 secciones (LEEME, parque de máquinas,
   hoja de ruta, mapa general con los dos caminos, camino con GuiGui, camino Fusion, qué archivo
   va a qué máquina con ejemplos reales, sierra + AutoCUT, etiquetado, perforadora paso a paso con
   árbol de alarmas y tabla de herramientas, router, cantos y armado, pendientes/preguntas HUAHUA,
   referencia Bluen). Las 18 capturas que ya estaban en el tablero quedaron en sus secciones.
   **Faltan las capturas de la SKH-612HS del 23/09** (PgDrillCam32, tabla de herramientas, revista):
   no están guardadas en la carpeta; pegarlas en la sección F4 del tablero.
   **24/09/2026**: el tablero quedó dividido en dos zonas. ZONA A · DISEÑO (izquierda, secciones
   0-6, 12, 13) para el que diseña, hasta la carpeta del pedido. ZONA B · FÁBRICA (derecha) para el
   que fabrica: F0 recorrido de la pieza, F1 doce CARTELES para imprimir (etiqueta, plano, sierra,
   AutoCUT, perforadora encendido / ciclo / herramientas por posición / alarmas, cantos, armado,
   mantenimiento, carpeta del pedido) y F2-F6 el detalle de cada máquina. El cartel 7 (herramientas
   por posición) hay que actualizarlo cada vez que se cambia una fresa o mecha.
   **24/09 (tarde)**: las 43 capturas de la sesión en la máquina están en `instructivo/capturas/`
   (índice en `instructivo/INDICE.md`; copias reducidas a 1400 px en `instructivo/capturas_web/`, que son
   las que están subidas al tablero). Todas están montadas: sección **F7 · Instructivo de la perforadora**
   (11 capítulos, cada captura con qué se ve / qué enseña) y las clave repetidas dentro de los carteles
   1, 6, 7 y 8. Los carteles 7 y 8 y la sección F4 ya reflejan la contraseña 520 y la T184 en Ø20.

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

### 25/09/2026 — Sesión en la sierra: E13 y E06 resueltos, manual básico conseguido

**Manuales que ahora tenemos** (guardados en `instructivo/manuales/`): *Basic operation of HuaHuaSAW V7
software* (8 págs) y *Basic Operations of AUTOCUT10* (4 págs). El de la sierra no tiene sección de
alarmas; sólo operación básica. El software del control se llama **HuaHuaSAW V7**.

**Corte manual sin AutoCUT** — no hace falta contraseña, se hace en el menú `editar`:
`VolOrig` → `MatRes` (los dos obligatorios) → `editar` → arriba a la derecha placa Length/Width/Thick/
quantity (el ancho de placa se carga acá, NO en `parámetro`) → abajo "cutting length" + "quantity" →
Add por cada medida → botón rojo confirm → pasa a `automático` → Saw.ON + VentInic → placa → verde.
`Saw` = kerf 4,4; `Trim` = refilado por borde 5 (poner 0 si no se quiere perder). El menú `parámetro`
pide contraseña que NO tenemos (520 de la perforadora no sirve; pedir a la Sra. Tan).

**E13 "Alarma de límite de avance lateral"** — la torre del prensor lateral (la torre blanca con los
manómetros, montada sobre la viga naranja del empujador, corre por un riel SHAC a lo largo de la viga)
llegó al tope de su recorrido. En `E/S` se ve como **X36 "límite de avance de presión lateral"** en rojo.
El sensor es el **inductivo de ABAJO de los dos que están en la escuadra a la izquierda de la torre**
(LED rojo encendido = detectando); detecta la pletina blanca fija de la viga. Cómo se llegó: `AliLatDr`
mandó la torre al tope (Pos Lat 1466 → 1821). Por qué no sale: el motor lateral (KM3) tiene freno, no se
puede empujar a mano, y el PLC no deja moverlo mientras X36 esté activo → sin salida desde software.
**Salida que funcionó**: hongo → desenroscar el inductivo de abajo → destrabar hongo → `Alarma Off` →
`AliLatIz` (ahora sí se mueve) → alejarla 5-10 cm del tope → hongo → reponer el inductivo (1-2 mm de la
pletina) → `VolOrig`. Botones relacionados: `AliLatIz`/`AliLatDr` mueven la torre lateral; `EmpTraExt/Ret`
es el cilindro neumático Y16 (activarlo sin placa también da E13 hasta apagarlo); "Uso Lateral Stg" en
`automático` activa/desactiva el uso del alineador pero NO borra la E13.

**E06 "Anomalía motora"** — es **X24 "sobrecarga del motor"**: saltó un **relé térmico** del gabinete.
Apareció al pedirle mover a la torre lateral atorada contra el tope. Los dos servodrivers INVT
SV-DA200 (驱动1 / 驱动2, empujador y sierra) marcaban 00 = sanos. **Se resolvió rearmando el térmico
de KM3** (contactor del motor del alineador lateral). El gabinete tiene KM1…KM8 con térmicos debajo de
KM3, KM4/KM5 y KM6: cualquiera de ellos saltado da E06, así que ante E06 mirar primero los térmicos
(botón de rearme) antes que los drivers. Cortar energía no lo resuelve.

**CAUSA RAÍZ de E13 + E06 (25/09, tarde): secuencia de fases invertida.** El carro lateral (motor de
contactor KM3, no servo) se movía al revés de lo que indicaban `AliLatIz`/`AliLatDr` y el dibujo de la
pantalla. Por eso fue al tope equivocado (E13) y se sobrecargó (E06). La alimentación trifásica del taller
tenía la secuencia R-S-T invertida respecto del cableado de fábrica. **Se invirtieron dos fases en la entrada
general** y el lateral pasó a moverse bien. Afecta a TODOS los motores de contactor (hoja principal, incisor,
ventilador, lateral); los servos INVT no. **Después de tocar la alimentación, verificar siempre el sentido de
giro de la hoja contra la flecha antes de cortar.**

**Arranque del ciclo automático — lo que aprendimos al cortar para Vicente (25/09):**
- En `editar`, **Longitud = el lado que el empujador consume; Ancho = el largo de cada tira.** Tiras de
  500 × 2440 de placa 1220 × 2440 → Longitud 1220, Ancho 2440, Longitud de corte 500 × Cantidad 2 → Añadir →
  Confirmación. Sobrante 206,2.
- **El botón verde no hace nada si la hoja no gira.** "Sierra ON" tiene que quedar como **"Sierra Arr"**
  en rojo; "Flot St" como "Flot Stg". Los botones de la barra muestran el estado actual.
- "1ra Cuch Paused" en rojo = pausa en el primer corte activada; tocándolo queda "1ra Cuch Pausa" azul.
  "Pausa" es momentáneo (rojo sólo mientras se aprieta).
- **"Niv Rep" = "Initial position" del manual, obligatorio en automático** antes del verde (no es lo mismo
  que MatRes de manual).
- Para verificar que el verde llega al PLC: `E/S` → **X22 "arranque automático"** se pone roja al apretarlo.
- Capturas e índice completo: `instructivo/capturas/sierra/` + `INDICE_SIERRA.md` (50 archivos, S01–S32).

**Otras alarmas vistas**: E12 "debe volver al origen" (normal tras emergencia → `VolOrig`); E20 =
hongo apretado; E21 "fallo del interruptor fotoeléctrico" = cortina de luz interrumpida; E16 = carro
sierra fuera de origen. La pantalla `alarma` resalta en rojo las activas y `E/S` muestra qué entrada
las dispara — usar las dos juntas para diagnosticar.


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

- ~~**Remoto de git.**~~ ✅ Hecho: `origin` en GitHub (Barton-user/fabricamuebles).
- Decidir el herraje de la casa: **perno 33 o 34** (§15.5).
  - Marca ya definida: **Häfele** (§5). Falta elegir el modelo concreto de 3 en 1 en su catálogo y ver si el perno es de 33 o 34.
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

---

## 15. 23/09/2026 — Primera sesión en la SKH-612HS

### El software no se llama HHcnc

En la PC industrial hay **CncMon32** y **PgDrillCam32**. El que opera la máquina es
PgDrillCam32, cuyo título real es **`桦桦数控钻 MH2026_Drill 3.0.5.0`** (build 2025/12/15),
marca **HUAHUA**. Tiene interfaz en español (botones Inglés / Chino / Español en el panel
"Personalización automática").

Layout: arriba pestañas Manual / Automático / Parámetro / Configuración / Mantenimiento,
estado (Sin conexión / **Listo**), Iniciar / Pausa / Reiniciar / Simulación / alarma.
Izquierda: "Personalización automática", "Tipos completados", "Cola".
Derecha: campo **"Escanear código"** — acepta tipeo manual, no hace falta escanear.
Barra de edición 2D: Generar, Guardar como, Nuevo, Acumulado, Ocultar proceso, Modificar,
Desplazamiento, Rotar, **Voltear placa**, **Reflejar**, Doble placa.
Columna de operaciones: Vertical, Horizontal, **Ranura**, Fresado de perfil, Acortar esquina,
Rectángulo, Bisagra, Gripless, Lamello, Inclinado, Bisel, I. Rectangle.

### ✅ RESUELTO — qué formato lee la máquina

Panel "Tipos completados" → icono de carpeta → diálogo **"Cargar archivo"** → desplegable
**"Formato"**. La lista completa:

```
formato final                              Formato de prohibición
Formato final V2                           Formato de prohibición (ranura lateral SlotH)
Formato de prohibición (ranura lat. SlotSid)  Formato Pytha DXF
ByasBpp                                    formato PYXCAM
Sesgo CIX                                  Formato SCM xxl
YimuXml                                    Nueva generaciónXml        ← default
Wei Lun Xml (Inicio 3D)                    Xml de nueva generación (fresado 3D)
WeilonXml                                  Json de nueva generación
WeilonXmlV2                                DXF de nueva generación
formato Hisense                            Formato Wang Shi PDX
Haomai MPR              ← nuestro MPR      estilo yuncheng
HomagVHoleIgnoreZA
KDTXml                  ← nuestro XML3
```

**Conclusión**: los dos formatos que validamos byte a byte contra Bluen están en la lista.

| Nuestra carpeta | Opción del desplegable | Validación |
|---|---|---|
| `XML3/` | **KDTXml** | 12/12 byte a byte |
| `MPR/` | **Haomai MPR** | 12/12 byte a byte (incl. archivos K) |

**No existe opción `.ban`.** La carpeta `BAN/` no sirve para esta máquina, y la pelea con la
plantilla `六面钻BAN洪德（贺耀）` de GuiGui era por un formato que esta perforadora ni lee.
XML1 no tiene correspondencia obvia; los candidatos serían "Nueva generaciónXml" o alguno de
los "formato final".

### ⚠️ Las piezas del gris están mal cortadas

La etiqueta del techo dice:

```
工程: 0203米格样柜电子锯文     ← nombre de otra orden, no 260625-20
客户: PRUEBA
材料: 多层实木 13玛雅灰
部件: P01                      ← código de barras mal mapeado
规格: 599 X 398
```

Medido con calibre: **599 × 398**. Confirmado.

Las dos listas de corte (la de GuiGui y la nuestra) dicen **598 × 399**. La diferencia es
exactamente lo que da si se invierte a qué lado pertenece cada bandera de canto:

- correcto: `前`/`后` sobre el lado de 600 → 598 · `左`/`右` sobre el de 400 → 399
- cruzado:  `前`/`后` sobre el lado de 400 → 398 · `左`/`右` sobre el de 600 → 599

**AutoCUT quedó con el mapeo de las columnas de canto cruzado** en la "Coincidencia" de
importación. Las 7 piezas del gris se cortaron con ese error y hay que volver a cortarlas
antes de armar el mueble. Es el mismo problema de mapeo que ya estaba anotado para el código
de barras (sección 9).

Para confirmar en otra pieza — si da la columna derecha, está cruzado:

| Pieza | Correcto | Cruzado |
|---|---|---|
| Partition02 | 564 × 369 | 563 × 370 |
| Left / Right board | 741,83 × 399 | 740,83 × 400 |
| Fascia | 99 × 564 | 100 × 563 |

### Consecuencia para la prueba

El programa está hecho sobre la medida **terminada 400 × 600**; la placa real mide 398 × 599.
La pieza está 2 mm angosta y 1 mm corta respecto del marco del programa. Sirve igual como
pieza de sacrificio: hay que medir cada agujero **desde los dos bordes opuestos** y anotar
ambos valores, para deducir desde qué esquina referencia la máquina.

### Archivos preparados

`etapa2/salida/PRUEBA1/PARA_PENDRIVE/` — sólo la pieza de prueba (techo, 9441838670057)
en los cuatro formatos, para copiar al pendrive.

### Lo que se logró en la sesión del 23/09

1. **Importación validada.** `Cargar archivo` → Formato **KDTXml** → ruta de la carpeta →
   el archivo aparece en "Tipos completados" con la placa bien leída (400 × 600 × 18).
   ⚠️ El desplegable arranca en **"Nueva generaciónXml"** y con ese no lee nada, sin dar
   error: simplemente no lista archivos. Hay que cambiarlo a mano cada vez.
2. **Doble clic en la fila** dibuja la pieza en "Edición 2D" y llena la tabla de operaciones.
3. **El software rota la pieza**: la muestra como `600 × 400`, con el cartel
   **`CCW Rotate 270°`** y una flecha grande que indica el sentido de carga.
   Las coordenadas de la tabla ya vienen en ese marco rotado: el Ø10 que en el archivo está
   en (360, 591) aparece como **(591, 360, 18)**.
4. **Asignación de herramientas correcta**, sin tocar nada:

   | Operación | Herramienta |
   |---|---|
   | Ø10 prof 11 en (591,360) y (9,360) | **T56** |
   | Ø10 prof 11 en (591,40) y (9,40) | **T158** |
   | Ranura 6 × 6 cara frente | **T187** |

5. **La ranura de 9 × 9 de cara trasera la rechaza**: columna "Motivo no procesado" dice
   **"Diámetro de herramienta demasiado grande"**. Destildando su casilla "Habilitar" y
   apretando **Generar**, la cola pasa de "Error en conversión" (rojo) a
   **"Procesamiento asignado"** (azul). Falta averiguar cuál es el ancho máximo de fresa
   para ranura en cara trasera de esta máquina.

### ❌ Donde quedó trabado

Con el trabajo en "Procesamiento asignado" y el estado en **"Listo"**, tanto el botón físico
de Start del panel como el botón **"Iniciar"** del software dan el mismo error, con alarma
sonora:

> **coordinate 71 — el procedimiento de tramitación no se especifica el nombre principal
> del programa**

(traducción rota de algo como 加工程序未指定主程序名 — "el programa de mecanizado no tiene
nombre de programa principal").

Cosas que se probaron y **no** lo destrabaron:

- Homing completo desde CncMon32.
- Escribir el código `9441838670057` en el campo **"Escanear código"** y dar Enter — el campo
  lo acepta (no hace falta escanear) pero no cambia el estado de la cola.
- Hacer clic en **"El usuario no ha iniciado sesión"** (abajo a la derecha) — no abre ningún
  login, no hace nada.
- Apretar "Automático" en la barra superior.

**Aclaración**: los cinco botones de arriba (Manual / Automático / Parámetro / Configuración /
Mantenimiento) **no son selectores de modo**, son menús desplegables. El rojo permanente de
"Mantenimiento" es un **aviso de mantenimiento vencido**, no el modo activo.

### Mantenimiento vencido

Menú Mantenimiento → "Mantenimiento de equipos" → pestaña Drill: **las 12 tareas están
vencidas**, último registro **2026-01-04**, tiempos restantes en rojo (−232 / −261).
La primera (`水平油嘴`, picos de lubricación horizontales) pide recarga cada
**120-150 h de trabajo del pack de mechas**, con aceite **ISOFLEX TOPAS L 32 N**.
No bloquea la operación, pero hay que hacerlo y marcarlo en la columna "renovar".

### Mecánica de carga (corregido)

La placa **no** va apoyada contra la regla del lado del operador. Las que agarran son dos
**pinzas neumáticas** montadas sobre una viga en el **lado opuesto** de la mesa perforada.
Según la secuencia del manual, la primera pulsación del verde acerca las pinzas al frente y
la máquina queda esperando la pieza; recién ahí se coloca. **No confirmado en la práctica**,
porque nunca se llegó a arrancar el ciclo.

### Preguntas pendientes para HUAHUA (agregar a la sección 11)

6. Con un trabajo en estado "Procesamiento asignado" y la máquina en "Listo", ¿cuál es la
   secuencia exacta para arrancar el ciclo? El error es "坐标71 / 加工程序未指定主程序名".
7. ¿Hace falta iniciar sesión de usuario? El pie dice "El usuario no ha iniciado sesión" y
   el clic no abre nada. ¿Usuario y contraseña?
8. ¿Cuál es el ancho máximo de fresa para ranura en **cara trasera**? La de 9 mm la rechaza
   por "diámetro de herramienta demasiado grande".
9. ¿Se puede fijar **KDTXml** como formato por defecto del diálogo "Cargar archivo"?

### ✅ DESTRABADO — la máquina mecanizó la primera pieza (23/09, ~02:00)

El error `coordinate 71` era porque **las pinzas no estaban en posición de carga**. La
secuencia correcta, confirmada en la práctica:

1. Importar con **Formato = KDTXml** → doble clic en la fila → destildar la fila 5 →
   **Generar** → la cola queda en "Procesamiento asignado".
2. **Botón verde, primera pulsación**: las pinzas se acercan al frente, entra el aire, la
   máquina queda esperando la pieza. *(Apretar Iniciar antes de esto da el error de
   "programa principal".)*
3. **Colocar la placa contra el tope**, del lado de las pinzas.
4. **Botón verde, segunda pulsación**: las pinzas cierran, el tope se acomoda y mecaniza.

**Alarma de medida**: con la placa de 398 y el programa de 400 salta
`MLC 148 PLC — ancho de placa demasiado pequeño, r49,3`.
Se resuelve con **Reiniciar** + destildar **"Detección de ancho"** en el panel
"Personalización automática". Con la detección apagada la máquina toma los 400 nominales del
programa, así que todo lo referido al borde lejano queda corrido los 2 mm de diferencia.

**Resultado**: las 5 operaciones habilitadas salieron — los 4 Ø10 y la ranura de 6 × 6.
Falta sólo la ranura de 9 × 9 de cara trasera, que es la que se había destildado.

**Pendiente de medir con calibre** (no se completó esa noche): posiciones exactas y,
sobre todo, si hay espejado — la ranura tiene que dar a **372,5** desde un borde de 398,
no a 27,5.

### Tabla de herramientas de la máquina — dónde está y qué tiene

**Ruta**: menú **Parámetro** → pestaña **"Configuración de paquete de…"** → panel derecho
**"Herramientas de corte generales"** (la otra pestaña es "cuerpo cruzado"). A la izquierda,
el diagrama **"bolsa de taladro 1 / 2"** muestra la disposición física.

Columnas: Nº · permitir · número de cuchillo · grupo · **diámetro** · **ancho de aserrado** ·
tipo de herramienta · X · Y · desplazamiento X/Y.

**Taladros verticales** (tipo `Z positivo` = cara frente, `Z negativo` = cara dorso):
Ø5, Ø8, Ø10, Ø12, Ø15, Ø20. Taladros horizontales (`X±`, `Y±`): Ø8.

**Husillos y sierras** (el bloque en X −24,5 / Y 388,8):

| Tnn | Ø | Ancho | Tipo | Estado |
|---|---|---|---|---|
| 11 | 10 | 10 | husillo (X −25,4 / Y 80) | **cargada** — hizo la ranura de dorso |
| 181 | 100,2 | 7 | sierra lateral | |
| 182 | 9,8 | 9,8 | Lamello | |
| 183 | 43,9 | 3 | hoja de sierra | |
| 184 | 10 | 10 | husillo | **puesto VACÍO** |
| 185 | 3,2 | 3,2 | husillo | |
| 186 | 24 | 24 | — | **sin cargar** (lugar libre) |
| 187 | 6 | 6 | husillo | **cargada** — hizo la ranura del frente |
| 188 | 10 | 10 | husillo | |
| 190 | 0 | 0 | — | |

### ⚠️ Tres herramientas que faltan para producir PRUEBA 1

| Falta | Para qué | Cómo se manifiesta |
|---|---|---|
| **Vertical Ø6 prof 3** | tornillos de bisagra (16 agujeros) | **crasheo del software**: `System.ArgumentOutOfRangeException: el índice estaba fuera del intervalo`. No avisa que falta la herramienta, se rompe. Hay Ø5 — habría que decidir si los tornillos van con Ø5. |
| **Fresa de ranurar Ø9** | ranura de luz del techo | "Diámetro de herramienta demasiado grande". El ancho mínimo de ranura en **cara dorso** es ~10 (la fresa más chica disponible para esa cara). Con ancho 10 la acepta y asigna **T11**. |
| **Cazoleta Ø35** | bisagras de las puertas (4) | No existe Ø35; el post planifica **fresado circular** con **T184**, cuyo puesto está vacío → alarma `MLC 142 · señal de sujeción del husillo anormal · r48,13` en pleno cambio de herramienta. |

El puesto **186** está libre para cargar una fresa.

### Otras alarmas y comportamientos vistos

- `MLC 148 PLC — ancho de placa demasiado pequeño, r49,3`: la placa medida no coincide con la
  del programa. Se saltea destildando **"Detección de ancho"** (y "Detección de longitud"
  para el largo) en "Personalización automática".
- El campo **"Escanear código"** define qué pieza sale; si queda el código viejo, arranca la
  pieza vieja. La **cola** procesa en orden: hay que borrar los trabajos pendientes que no se
  quieren, con "Eliminación".
- Arriba, donde dice "Listo", puede aparecer **"Bloque individual"** en rojo = modo paso a
  paso; si se frena entre movimientos, Iniciar de nuevo.
- Cada pieza trae su propia rotación: el techo **CCW Rotate 270°** con flecha a la izquierda,
  la puerta **CCW Rotate 90°** con flecha a la derecha. **No cargar de memoria.**
- Un circulito rojo aparece fuera del contorno en el dibujo 2D de todas las piezas. Sin
  identificar; probablemente el marcador de esquina de referencia.

### Segunda pieza probada — puerta izquierda 9441838670088

Importó bien (297 × 681,83 × 18). De sus 6 operaciones: las 2 de Ø35 fallan por lo de arriba,
y las 4 de Ø6 crashean. **Cambiando los Ø6 a Ø5 el software las toma sin error.**

Dato útil: la puerta no tiene orientación equivocada posible. Cargada girada 180°, las
cazoletas caen en (274,5, 581,83) y (274,5, 100) — que son exactamente las coordenadas de la
puerta derecha. La placa simplemente pasa a ser la otra puerta.

### La revista de fresas — cómo es y cómo se numera

Pantalla **Manual** (pestaña `612NS`): diagrama de los dos paquetes de mechas (Motor1 y
Motor2), tabla de coordenadas de los 9 ejes (X, Y2, Z2, U, V, W, A, Y, Z), botonera de jog,
y abajo cuatro botones grandes: **Modo de origen · Reinicio de engrase · Modo de cambio de
herramienta · RESET**.

Apretando **"Modo de cambio de herramienta"** (queda en verde) salen los tres
**"Cilindro de revista de herramientas"** y la revista queda accesible.

**Es una revista lineal de conos**, no pinzas en el husillo. Cada puesto tiene una horquilla
amarilla y su asiento, rotulados `1号 … 8号`. Las fresas van montadas en cono y el husillo
las toma de ahí.

**Regla de numeración descubierta: `T18n` = puesto `n` de la revista.**

| Tnn | Puesto | Ø | Estado observado |
|---|---|---|---|
| 184 | **4** | 10 | **VACÍO** — sólo la horquilla |
| 185 | 5 | 3,2 | cono montado |
| 186 | 6 | 24 | cono montado (la tabla lo daba "sin cargar" — revisar) |
| 187 | 7 | 6 | cono montado, **funcionando** (hizo la ranura de 6) |
| 188 | 8 | 10 | — |

En la grilla T1…T9 de esa pantalla, **T1/T3/T5/T7/T9 salen con círculo rojo y T2/T4/T6/T8 en
negro**. Pendiente confirmar si el rojo marca puesto ocupado.

**Consecuencia**: la alarma `MLC 142 · señal de sujeción del husillo anormal · r48,13` al
fresar la cazoleta Ø35 es simplemente que el puesto 4 está vacío. No falta comprar una
máquina ni una herramienta exótica: falta **un cono con fresa para el puesto 4**.

**Atajo**: se puede forzar otra fresa con el campo **"Asignar número"** del diálogo de la
operación. Para la cazoleta Ø35 se puede usar la **187** (Ø6, puesto 7, montada) — fresa el
círculo en más vueltas pero sale.

### Instalación de herramientas (manual, sección 11.3)

- Husillo **ER25**. Llave de fresa incluida en la caja de accesorios.
- La fresa debe sobresalir **más de 45 mm**, idealmente lo mismo que la que se saca.
- La profundidad se ajusta con el valor **"+Z"** de la herramienta en el almacén: más valor,
  más profundo. Es común a las fresas de arriba y de abajo.
  ⚠️ **FALSO: es al revés — menos valor = más profundo** (§16, confirmado por Huahua el 30/09).
- **Después de cambiar, corregir el diámetro en la tabla de herramientas**, o el software
  sigue calculando con el viejo.
- Mechas: prisionero bien trabado, altura de instalación ≤ 1 mm, nada de mechas gastadas, y
  **prohibido poner una mecha de más de Ø10 en la herramienta Nº 1**.
- Al terminar, llamar todas las herramientas y verificar que las puntas queden en el mismo
  plano, **±1 mm**.
- Velocidades por diámetro: Ø5/6/8 → 4500 · Ø10/12 → 1-4000 · Ø15 → 1-2200 · Ø20 → 1-1200.

### Segunda parte de la noche (23/09, 02:00 – 02:30)

**Se montó una fresa en el puesto 4.** Fresa espiral marcada `Ø20x70R 250710`, giro a derecha,
montada en un cono vacío con **46 mm de voladizo** desde la cara de la tuerca (el manual pide
>45). El cono se apoyó en la horquilla del puesto 4.

También apareció una **fresa de disco `62211-4T 12.7*45*H3`**: mango 12,7 (1/2"), Ø45, 4 filos,
**3 mm de espesor de ranura**. Coincide con la **T183** de la tabla (43,9 × 3). Es de ranurar de
costado, **no puede hundirse**, así que no sirve para cazoletas — sí para ranuras de 3.

#### La tabla de herramientas está protegida por contraseña

Al intentar cambiar el diámetro de la T184 (de 10 a 20) el software **pide contraseña de
fábrica**. No se puede editar ni desde la celda de la tabla (es de sólo lectura) ni desde el
panel "Configuraciones de uso común" (pide seleccionar la herramienta en el diagrama, y ahí
salta la contraseña).

**CONTRASEÑA: `520`** — la pasó 桦桦唐玮民 (Huahua, Tang Weimin) por WeChat el 24/09.
Sirve para entrar a editar la tabla de herramientas: se cliquea el ícono de la herramienta en
el diagrama de la izquierda, se ingresa `520`, se editan diámetro y ancho en el panel
"Configuraciones de uso común", y se guarda con **"almacenar herramientas"**.

#### Truco para fresar sin la contraseña — compensación en el archivo

Mientras la tabla diga que la T184 es de Ø10 y la fresa real sea de Ø20, se compensa pidiendo
un diámetro más chico en la operación:

```
diámetro a pedir = diámetro real deseado − (Ø real de la fresa − Ø declarado en la tabla)
para la cazoleta:  35 − (20 − 10) = 25
```

Razón: el software recorre un círculo de `pedido − declarado`. Pidiendo 25 recorre 25−10 = 15,
y con la fresa real de 20 barriendo, el agujero sale 15 + 20 = **35**.

**Sin verificar todavía** — hay que fresar un agujero en un recorte y medirlo con calibre. Si
da 45, el software no compensa el radio y el truco no sirve.

⚠️ El día que llegue la contraseña: corregir el diámetro de la T184 a 20 en la tabla y volver
a pedir 35 en el archivo. El truco es un parche, no la solución.

#### Otras cosas aprendidas

- **El override de herramienta** ("Asignar nú" en el diálogo de la operación) abre el selector
  **"Especificar herramienta"**, que sólo lista las herramientas válidas para ese tipo de
  operación. El campo de texto es de sólo lectura: hay que **cliquear el ícono en el diagrama**.
  La **T187 no aparece** para agujeros verticales de cara frente.
- Forzar la **T188** para la cazoleta **es rechazado**: *"no se puede usar la herramienta
  especificada para el procesamiento"*. En el diagrama la 188 está dibujada como herramienta
  horizontal — no puede hundirse en la cara.
- La tabla de operaciones tiene **dos columnas "Herramienta"**: la primera es la forzada por el
  usuario, la segunda la que asigna el post. Hasta que no se aprieta Generar, la segunda
  conserva la asignación vieja.
- **Ojo al probar con un recorte de otra medida**: el techo de descarte mide 599 de largo y el
  programa de la puerta está hecho sobre 681,83, así que la operación en X = 605,83 **cae fuera
  de la placa**. Hay que destildar las filas cuyas coordenadas se salgan del recorte.
- Los agujeros de bisagra **Ø6 cambiados a Ø5 se procesan sin problema**, con **T162**.

#### Donde quedó esta vez

Con el cono ya puesto en el puesto 4 y el trabajo asignado, al dar verde salta:

> **"Se prohíbe el mecanizado cuando el husillo no está sujeto"**

y antes de eso la placa quedó trabada adentro en el paso del cambio de herramienta, con el
estado en "Listo" y la cola vaciándose sola.

**Causa muy probable, sin confirmar**: quedó activo el **"Modo de cambio de herramienta"** de
la pantalla Manual → 612NS. En ese modo el husillo queda liberado, así que el control se niega
a mecanizar. Se le dijo al operador que lo apague y vuelva a Automático, pero se fue antes de
probarlo.

**Lo primero a hacer la próxima vez:**

1. Manual → 612NS → **apagar "Modo de cambio de herramienta"** (que no quede en verde).
2. Volver a Automático, mandar el trabajo, verde dos veces.
3. Si vuelve a dar la misma alarma, no insistir: es configuración de máquina y va con Huahua.

### Pendientes concretos al cierre del 23/09

| # | Qué | Estado |
|---|---|---|
| 1 | ~~Contraseña de la tabla de herramientas~~ | ✅ **520** |
| 2 | ~~Verificar el truco de compensación~~ | ya no hace falta: la T184 quedó en Ø20 y el archivo pide 35 |
| 3 | Apagar el modo de cambio de herramienta y reintentar | sin probar |
| 4 | Medir con calibre la primera pieza (techo) — ¿hay espejado? | **sin hacer** |
| 5 | Corregir mapeo de cantos y de código de barras en AutoCUT | sin empezar |
| 6 | Recortar las 7 piezas del gris con las medidas correctas | sin empezar |
| 7 | Mecha vertical Ø6 (o pasar los tornillos de bisagra a Ø5) | decidido: reemplazar un Ø10 del paquete de arriba (§26) |
| 8 | Lubricación — 12 tareas vencidas desde 2026-01-04 | sin hacer · se marca con permiso + **Actualizar** (§26) |
| 9 | Router: cargar T1 Ø6 en su almacén | sin empezar |

---

## 16. Sesión del 24/09 — contraseña, cazoletas resueltas, y el husillo trabado

### ✅ Contraseña de la tabla de herramientas: `520`

La pasó **桦桦唐玮民 (Huahua, Tang Weimin)** por WeChat. Flujo para editar:

**Parámetro → "Configuración de paquete de…" → cliquear el ícono de la herramienta en el
diagrama de la izquierda → contraseña `520` → editar diámetro y ancho en el panel
"Configuraciones de uso común" → guardar con "almacenar herramientas".**

⚠️ La celda de la tabla es de **sólo lectura**; no se edita ahí. Y si no se selecciona primero
la herramienta en el diagrama, sale el cartel *"Por favor seleccione la herramienta de edición"*.

### ✅ Las cazoletas Ø35 — resueltas (post + calibración de Z)

Se corrigió el **diámetro de la T184 de 10 a 20** (la fresa espiral Ø20 que se montó en el
puesto 4). Con eso el post **resuelve el fresado circular de la cazoleta Ø35 solo**, sin
override ni compensación: las dos filas salen con **Ø35, profundidad 13, cara frente, T184
asignada, sin error**.

El truco de compensación (pedir 25 para obtener 35) quedó como curiosidad documentada; ya no
hace falta.

Eso resolvió el **post** (que genere el programa sin error y con T184 asignada). Faltaba además
calibrar el **`desplazamiento Z` de la T184 en `27`** para que la profundidad saliera bien — ver
la sección "RESUELTO — la cazoleta Ø35: el husillo de fresa estaba descalibrado en Z".

### ⚠️ El `.scx` guarda las ediciones y las devuelve al re-importar

Al editar una operación, el software guarda la pieza como `.scx`. **Re-importar el mismo XML
devuelve la versión editada, no el original.** Para volver al archivo limpio hay que **borrar
primero la fila del panel "Tipos completados"**.

Eso produjo el episodio más peligroso de la sesión: las cazoletas quedaron desdobladas en
**4 operaciones de Ø20 profundidad 9,5, una por cara** — o sea **dos agujeros pasantes de Ø20**
en la puerta en vez de dos cazoletas — y **la tabla estaba toda verde, sin un solo error**,
con T2 y T153 asignadas. El software encontró herramientas y hacía exactamente lo pedido.

> **Regla de oro para el operador: que no haya error NO significa que esté bien.**
> Antes de dar verde, leer la tabla fila por fila y comparar cara, coordenada, profundidad y
> diámetro contra el plano.

### ✅ RESUELTO — el husillo vacío y la MLC 349

**Síntoma**: el husillo de fresa queda **físicamente vacío** pero CncMon32 muestra arriba a la
derecha **`T 187`** — el control tiene registrada una herramienta que no está. Al arrancar
cualquier ciclo intenta devolverla, abre la mordaza, no encuentra nada, y cae en:

> `MLC 349 — Se prohíbe el mecanizado cuando el husillo no está sujeto (R46.18)`

**El interlock es global**: se probó con la pieza reducida a sólo agujeros de mecha (sin ninguna
operación de fresado) y **también salta**. No se puede esquivar mecanizando otra cosa.

**Origen**: en un cambio de herramienta fallido la máquina devuelve la herramienta que tenía y
no logra tomar la nueva (por ejemplo porque el puesto está vacío). Queda el registro apuntando
a una herramienta ausente. **Apagar y prender NO lo arregla** — no es un estado colgado, falta
la herramienta físicamente.

#### LA SOLUCIÓN: montar el cono a mano con el botón verde del cabezal

**Hay un botón verde FÍSICO en el cabezal, al lado del husillo** — no está en ninguna pantalla
del software ni del CNC, por eso no aparecía buscando entre los botones de la interfaz. Ése es
el de sujeción de herramienta.

Procedimiento: se apoya el cono en el husillo con la mano, bien asentado y calzando la muesca
con las chavetas de arrastre, y **se aprieta ese botón verde del cabezal**. El husillo lo chupa
y queda sujeto. La MLC 349 se limpia y la máquina mecaniza normalmente, cambios de herramienta
incluidos.

**Recomendación**: montar el cono del puesto que el control tiene registrado (si muestra T187,
el del puesto 7) para que registro y realidad coincidan.

#### Cómo leer las alarmas de verdad

**CncMon32 → botón `alarma` → pestaña "Alertas existentes".** El mensaje que muestra MH2026 es
la consecuencia; el listado del CNC es la causa. Son dos alarmas distintas y sólo se ve una
por vez:

| Alarma | Registro | Qué es |
|---|---|---|
| **MLC 348** | R46.17 | la máquina está en modo de cambio de herramienta |
| **MLC 349** | R46.18 | se prohíbe el mecanizado con el husillo no sujeto |

#### MLC 348 — modo de cambio de herramienta

Es un **modo del CNC** (R46.17), no sólo un botón del software. En CncMon32 aparece en el menú
de la izquierda como **"Cambio de cuchillo"**, y es un **interruptor**: se aprieta para entrar y
**se aprieta de nuevo para salir**. No se sale eligiendo otro modo — apretar "automático" no
hace nada mientras está puesto.

Y mientras el botón "Modo de cambio de herramienta" de MH2026 (Manual → 612NS) esté en verde,
**el software vuelve a poner el flag al arrancar**. Hay que apagarlo en **los dos** lados.

#### Qué es realmente "Placa de sujeción del cortador"

Ese botón de la pantalla 612NS **no acciona la mordaza del husillo**. Es la **campana de
aspiración** — la "pollera" que rodea al router y baja para chupar la viruta durante el
fresado. En el diagrama eléctrico figura como *"upper milling cutter supporting plate"*.
Al apretarlo baja un cobertor; **no hace succión de sujeción de herramienta**.

Su estado de reposo es **arriba**. Si queda accionada, la máquina **bloquea el arranque** con
`MLC 129` (un cilindro no retornó). Apretarla limpia momentáneamente la MLC 349, pero el ciclo
la vuelve a disparar.

### ✅ RESUELTO — la cazoleta Ø35: el husillo de fresa estaba descalibrado en Z

**`desplazamiento Z` de la T184 = `27`.** Ése es el número. Con eso la profundidad sale exacta.

> Huahua (30/09) confirma que así se calibra: con el Z de cada herramienta en la tabla, no hay
> pantalla de medición. Mencionaron también la **T190** ("同动刀") — **no tocarla**, ver §26.

#### El síntoma

Se pedía **Ø35 profundidad 13** sobre placa de 18 y salía **pasante y deformada** (26 × 32 en vez
de 35 redondo), con el borde desgarrado.

#### Cómo se encontró

La clave fue un **test con tres cazoletas de profundidades distintas** en la misma corrida.
Si la máquina las hacía todas iguales, la profundidad no la controlaba el programa; si salían
distintas, sí. **Salieron distintas** — y separadas por la diferencia correcta. O sea que el
programa manda, pero con un **offset constante**.

Primera medición, con Z = 8,7, sobre **dos placas de 18 apiladas** (para poder medir lo que se
pasaba de los 18):

| Pedido | Real | Error |
|---|---|---|
| 13 | 18 + 15 = 33 | +20 |
| 8 | 18 + 10 = 28 | +20 |
| 3 | 18 + 3 = 21 | +18 |

#### ⚠️ El signo está AL REVÉS de lo que dice el manual

El manual (sección 11.3) dice *"the larger the value, the deeper the groove"*. **Es falso.**

**Menos valor = MÁS profundo. Más valor = menos profundo.**

Se comprobó a lo bruto: bajar el Z a `-11,3` hizo que la fresa se clavara hasta atravesar las
dos placas apiladas (36 mm) y el husillo quedó trabado contra la madera — hubo que usar el paro
de emergencia. **No repetir.**

#### La calibración, en dos pasos y desde el lado seguro

Regla de oro: **acercarse siempre desde arriba** (valores altos de Z = poco profundo). Errarle
para poco profundo no rompe nada; errarle para profundo clava la fresa.

| Z | Pedido 12 / 8 / 4 | Error |
|---|---|---|
| 31 | 7,7 / 4 / ~0 | −4,2 |
| **27** | **12 / 7,6 / 4** | **≈ 0** |

Con dos puntos la recta queda determinada: pendiente ≈ 1,08 (o sea prácticamente 1 mm de Z =
1 mm de profundidad) y cruce por cero en 27,1. Coincide con la medición directa.

**Fórmula para recalibrar cuando se cambie de fresa o de voladizo:**

```
Z nuevo = Z actual − (profundidad pedida − profundidad medida)
```

#### Un solo error explicaba los cuatro síntomas

- **Profundidad de más**: pedías 13 y bajaba 33.
- **Canaleta entre agujeros**: la altura de retracción también estaba corrida 20 mm, así que el
  husillo "levantaba" a una cota que seguía estando dentro de la placa y **viajaba enterrado**,
  abriendo una canaleta larga que unía los tres agujeros.
- **Agujero ovalado (26 × 32) y borde desgarrado**: venía arrastrando.
- **Marca circular de 85-90 mm en la superficie**: el frente del husillo bajaba hasta apoyarse
  contra la placa. Esa marca fue la primera pista de que era un problema de referencia de Z.

#### Procedimiento de prueba que sirvió (reutilizable)

1. **Tres cazoletas de profundidades distintas en la misma corrida**, separadas en la placa —
   así se distingue "offset constante" de "no controlado" en una sola pasada.
2. **Dos placas apiladas** cuando se espera que atraviese, para poder medir el exceso.
   ⚠️ Declarar el espesor real (36) en el archivo, nunca 18 con 36 cargados.
3. **Una sola placa** cuando ya se está cerca, con profundidades chicas (4 / 8 / 12).
4. Ubicar los agujeros **lejos de las pinzas** y de mecanizados anteriores.
5. **Generar de nuevo** después de cada cambio en la tabla de herramientas — el código se arma
   con el valor que había.

Archivos de prueba usados: `9990000000037.xml` (36 mm) y `9990000000038.xml` (18 mm).

### Calidad de corte — a tener en cuenta cuando se resuelva

El borde de la cazoleta salió desgarrado. Tres causas, independientes de lo anterior:

1. **Sale pasante**: al atravesar la melamina sin material atrás, el borde de salida revienta.
   Se resuelve solo cuando la cazoleta sea ciega.
2. **El avance está seteado para otra fresa.** En la fila de la T184, sección **"Ajuste de
   velocidad"**, los valores vistos eran 10000 / 1000 / 500 y velocidad 5000 — configurados
   para una fresa de Ø10. Una de Ø20 barre el doble por vuelta. **Hay que bajar el avance.**
3. **Geometría de la fresa.** La montada es **espiral de corte ascendente** (`Ø20x70R`): levanta
   la viruta hacia arriba y **arranca la melamina de la cara superior**. Para melamina
   corresponde **corte descendente (downcut) o compresión**.

### Datos sueltos de la sesión

- El **selector de herramienta** ("Asignar nú" → "Especificar herramienta") **filtra por tipo
  de operación**: para un agujero vertical de cara frente no ofrece la T187. El campo de texto
  es de sólo lectura, hay que cliquear el ícono del diagrama.
- Forzar la **T188** para la cazoleta es rechazado (*"no se puede usar la herramienta
  especificada para el procesamiento"*): en el diagrama está dibujada como herramienta
  horizontal, no puede hundirse en la cara.
- La tabla de operaciones tiene **dos columnas "Herramienta"**: la primera es la forzada por el
  usuario, la segunda la que asigna el post; la segunda no cambia hasta apretar Generar.
- Los agujeros de bisagra **Ø6 pasados a Ø5 se procesan sin problema**, con **T162**.
- **Al probar en un recorte más chico que la pieza del programa**, hay que destildar las
  operaciones cuyas coordenadas caigan fuera de la placa (la puerta tiene una en X = 605,83 y
  el recorte del techo mide 599 → taladraría al aire).
- Los **marcadores del dibujo 2D** (dos rectángulos grises y un círculo rosa, fuera del
  contorno) **no son mecanizados** — no figuran en la tabla. Probablemente las pinzas y la
  esquina de referencia. Sin confirmar.
- La **puerta no tiene orientación equivocada posible**: cargada girada 180°, las cazoletas
  caen en las coordenadas exactas de la puerta derecha.

### Material para el instructivo

Carpeta **`instructivo/`**: 51 capturas con nombres descriptivos en `capturas/`, más
`INDICE.md` con 13 capítulos que explican qué se ve y qué enseña cada una. Listo para montar
el board en Figma.

Falta capturar: la secuencia de encendido, las pinzas viniendo al frente después del primer
verde, una cazoleta Ø35 terminada, y la primera pieza medida con calibre.

---

## 17. Respuestas de Huahua (24/09) y traducción real de la botonera

### ✅ La salida hacia adelante existe y se elige con un botón

Tang Weimin (桦桦唐玮民) mandó una captura con flecha roja a **前出料** y el texto
*"这里可以选择前出料"* — "acá podés elegir salida adelante". Está en el panel
**"Personalización automática"**, arriba a la izquierda de MH2026.

### 🔑 Lo que de verdad dicen los botones de "Personalización automática"

La traducción al español de ese panel es engañosa. Comparando con la captura en chino:

| Etiqueta en español | Chino | Qué es de verdad |
|---|---|---|
| **"Descarg"** | 前出料 | **salida hacia ADELANTE** (la pieza vuelve a la mesa del operador) |
| **"Después"** | 后出料 | **salida hacia atrás** |
| **"todo despejado"** | 解除板宽板长警报 | **borra la alarma de medida de placa** (la MLC 148) |
| "Detección de longitud" | 板长检测 | verificación de largo |
| "Detección de ancho" | 板宽检测 | verificación de ancho |
| "Encender el ventilador" | 曲用风机 | ventilador |
| "Apantallamiento lateral" | 屏幕演示 | demo en pantalla |

**Importante**: venía seleccionado **"Después"**, o sea salida hacia atrás. Por eso la máquina
mandaba la pieza terminada al fondo en vez de devolverla.

Y **"todo despejado" es la forma prolija de limpiar la alarma de medida** — mejor que destildar
"Detección de longitud" y "Detección de ancho", que lo que hace es desactivar la verificación.

### Instalación manual de herramienta: hay video

Huahua mandó un **video de 0:55** con el texto *"看视频手动安装刀具"* — "mirá el video,
instalación manual de herramienta". Confirma que el montaje a mano del cono es el procedimiento
correcto. **Pendiente de ver y documentar paso por paso.**

### Login

A la pregunta del usuario y contraseña del login contestó **"密码 520"** — la misma clave que la
tabla de herramientas. Candidato para el usuario: **`Admin`**, que es el que muestra CncMon32.
**Sin confirmar.**

### Preguntas mandadas el 24/09 — contestadas el 30/09 (ver sección 26)

Se le mandó un mensaje consolidado con 12 preguntas en 5 bloques:

1. **La cazoleta Ø35** (6 preguntas): calibración de largo de fresa y en qué pantalla se hace;
   si 46 mm de voladizo es demasiado; el procedimiento concreto de la sección 18 del manual
   ("todas las puntas en el mismo plano ±1 mm"); por qué sale ovalada y dónde están los
   parámetros de interpolación circular; si se puede agregar una mecha de Ø35 al paquete de
   verticales; y dónde se cambia el avance de la T184.
   Se le pasó la evidencia clave: **la marca circular de 85-90 mm en la superficie, concéntrica
   con el agujero, que prueba que el husillo topó contra la placa** — o sea que la profundidad
   la limita el tope mecánico y no el programa.
2. **Cómo poner el registro de "herramienta actual en el husillo" en T0.**
3. **La mecha vertical Ø6**: si se puede agregar, o si los tornillos de bisagra van con Ø5. Y el
   aviso de que el software **crashea** (`System.ArgumentOutOfRangeException`) en vez de avisar
   que falta la herramienta.
4. **Ancho mínimo de ranura en cara trasera** (9 lo rechaza, 10 lo acepta).
5. **Software**: KDTXml como formato por defecto; usuario del login; y cómo marcar el
   mantenimiento como hecho.

### ⚠️ El reloj de la PC industrial está mal

Adelantado unas **13 horas**. Consecuencia práctica: **los timestamps de "Alertas históricas"
de CncMon32 no sirven** para reconstruir en qué orden entraron las alarmas. Conviene ponerlo
en hora.

### Ventana horaria para hablar con Huahua

China está **+11 h** respecto de Argentina. Su mañana de trabajo cae entre las **22:00 y las
03:00 hora argentina** — que es cuando efectivamente contestaron. Escribirles a la tarde
argentina es escribirles a la madrugada de ellos.

---

## 18. TAREA ABIERTA — Corregir el mapeo de AutoCUT (sierra HP280)

> **Se trabaja en la PC de la sierra, no en la de la perforadora.** Quedó pendiente el 24/09
> para una sesión aparte.

### Contexto

`AutoCUT` es el software de la **sierra HP280**: importa la lista de corte, optimiza el
despiece, guarda el `.CUT` que carga el control de la sierra, e imprime las etiquetas en la
**AIBAO**. Es el paso anterior a la perforadora en la cadena.

Flujo actual (sección 9): **Importar → "Importar varios materiales" → "Coincidencia"** para
mapear columnas → Optimizar → Guardar como `.CUT`.

### Los dos errores a corregir

**1. Las columnas de canto quedaron cruzadas → las piezas se cortan 1 mm mal en cada lado.**

Nuestra lista ya trae `开料长` y `开料宽` **calculados y verificados** (10/10 contra el
`开料清单.xls` de GuiGui). Para el techo: **598 × 399**. Pero las etiquetas salieron
**599 × 398**, y las piezas se cortaron así.

La diferencia es exactamente la que da al invertir a qué lado pertenece cada bandera de canto:

```
correcto: 前/后 sobre el lado de 600 → 598  ·  左/右 sobre el de 400 → 399
cruzado:  前/后 sobre el lado de 400 → 398  ·  左/右 sobre el de 600 → 599
```

Confirmado con calibre en el techo (599 × 398) y con la etiqueta.

**Objetivo**: que AutoCUT **tome `开料长` / `开料宽` tal cual y no vuelva a restar nada**. La
cuenta del canto ya está hecha en nuestra lista; si AutoCUT la repite con su propia convención,
se rompe.

Para verificar en otra pieza — si da la columna derecha, sigue cruzado:

| Pieza | Correcto | Cruzado |
|---|---|---|
| Partition02 | 564 × 369 | 563 × 370 |
| Left / Right board | 741,83 × 399 | 740,83 × 400 |
| Fascia | 99 × 564 | 100 × 563 |

**2. El código de barras sale como `P01, P02…` en vez del código real.**

La etiqueta del techo decía `部件: P01`. **La perforadora busca el archivo por ese código**, así
que con `P01` el escaneo del QR no encuentra nada y hay que cargar el programa a mano (es lo
que se viene haciendo). También el campo `工程` (proyecto) sale con el nombre de otra orden
(`0203米格样柜电子锯文`) en vez de `260625-20`.

⚠️ **Detalle a resolver**: nuestra columna `板件条码` trae el código **repetido con guiones
bajos**, tal como lo emite GuiGui:
`9441838670057_9441838670057_9441838670057K`. Si AutoCUT no lo parte solo, la etiqueta va a
salir con todo ese texto.

**Solución propuesta desde nuestro lado**: agregarle a `etapa2/listacorte.py` una **columna
extra con el código limpio**, uno solo y sin sufijos, para mapear directo al campo de código de
barras de AutoCUT. Pendiente de hacer.

### Consecuencia pendiente

Con el mapeo corregido hay que **volver a cortar las 7 piezas del gris** — las actuales están
fuera de medida y no sirven para armar PRUEBA 1.

### Qué hace falta para retomarla

- Estar en la **PC de la sierra** con AutoCUT abierto.
- Una captura de la pantalla de **"Coincidencia"** para ver qué campo de AutoCUT recibe cada
  columna nuestra.
- El archivo `etapa2/salida/PRUEBA1/lista_corte.csv` (o el `.xlsx`).


### ⚠️ Lo que queda abierto del fresado (24/09, después de calibrar el Z)

**1. Marca de entrada de la fresa.** En los fresados más profundos queda un **lóbulo que
sobresale del círculo** en el punto donde la fresa baja y sale al contorno. Cuanto más profundo,
más marcado — es deflexión de la herramienta al penetrar.

*Para cazoletas de bisagra es cosmético*: queda tapado por la bisagra y, al sobresalir hacia
afuera, no interfiere con el encastre del cuerpo de Ø35. No frena la producción.

Qué probar: **bajar el avance de penetración** de la T184 (fila de la herramienta, sección
"Ajuste de velocidad" — los valores vistos fueron 10000 / 1000 / 500; el más chico suele ser el
de bajada). Eliminarlo del todo depende de la estrategia de entrada del post (si tiene arco de
entrada o entra radial) — preguntado a Huahua.

**2. La campana de aspiración no baja sola.** Tiene que descender **comandada por el programa**
durante el fresado y no lo hace, así que **la viruta no se aspira**. No se puede forzar a mano:
si se baja antes de arrancar, salta `MLC 129` y el ciclo queda bloqueado. Es otro ítem de puesta
en marcha del husillo de fresa, igual que el Z. Preguntado a Huahua.

**3. Corregir el manual.** La sección 11.3 dice *"the larger the value, the deeper the groove"*
para el `+Z` de las fresas. **Es al revés.** Se le avisó a Huahua.

---

## 19. Mecha Ø35 para cazoletas — qué comprar (24/09/2026)

> ⚠️ **SUPERADA EN PARTE POR LA SECCIÓN 21 (28/09).** Se descubrió que la Ø35 **no entra en el
> paquete de taladros** (paso 32 mm) y va sí o sí en el **husillo ER25**, con giro **DERECHA**.
> Las opciones izquierda de esta sección **ya no sirven**. La lista de compra vigente está al
> final de la sección 21.

### El problema

La cazoleta la estamos fresando con la **fresa espiral Ø20 del puesto 4 (T184)**, interpolando
un círculo. Sale mal: ovalada (30,16 × 32,7 pidiendo 35), con lóbulo de entrada, y el borde
despeluchado. La solución de fondo es una **mecha Ø35 de cazoleta en el paquete de taladros
verticales**, que hunde y sale — sin interpolar.

### Especificación que hay que pedir

| Dato | Valor |
|---|---|
| Diámetro | **35 mm** |
| Vástago (mango) | **Ø10 mm**, con plano de fijación y prisionero |
| Largo total | **70 mm** (hay de 57 también) |
| Giro | **derecha o izquierda SEGÚN LA POSICIÓN** del paquete |
| Tipo | **no pasante** (agujero ciego), 3 puntas |

⚠️ **Los husillos del paquete de taladros alternan el giro** (uno horario, el siguiente
antihorario). Si se compra la mano equivocada, la mecha **no corta**. Antes de comprar hay que
saber **qué posición del paquete la va a alojar y con qué giro** — está preguntado a Huahua.

⚠️ **NO sirve una mecha Forstner de ferretería** (las de tope, guía y llave hexagonal, $5.000 a
$30.000). Son para taladro de mano o de banco: mango corto, sin plano de fijación, sin
especificación de giro. No entran en el mandril de acople rápido del paquete.

### Lo que hay en el mercado argentino (24/09/2026)

**La línea correcta es Euro Hard, vendida por SOLUZIONE ACCESORIOS (tienda oficial ML,
MercadoLíder Platinum, San Justo, Zona Oeste).** La descripción dice textualmente
*"Brocas con filos de carburo de tungsteno, para agujereadoras múltiples y máquinas CNC"* y
*"Vástago Ø10 para mandriles de acople rápido, con plano de fijación y prisionero de ajuste"*.
Filos Widia, revestimiento PTFE. **Naranja = izquierda, negro = derecha.**

| Modelo | Medida | Giro | Precio | Link |
|---|---|---|---|---|
| **EHBRO3570NPI** | 35 × 70 | **izquierda** | **$54.061** | https://www.mercadolibre.com.ar/broca-mecha-para-bisagras-no-pasante-35-mm-x-70-mm-izquierda/up/MLAU126621939 |
| EHBRO4057NPD (código dudoso) | 35 × 57 | **derecha** | $52.861 | https://www.mercadolibre.com.ar/broca-mecha-para-bisagras-no-pasante-35-mm-x-57-mm-derecha/p/MLA2097192249 |

> El código de la derecha dice `40` donde debería decir `35` — probable error de carga del
> vendedor. **Preguntar antes de comprar** si es Ø35 y de qué largo.

Alternativas más caras, misma familia (marca ITALIANA / FUL, "Mecha Fresa Para Madera Bisagra
35x70mm Izquierda Widia HM"): **$73.238 a $82.628**. La Euro Hard es la misma cosa más barata.

### Decisión

**No comprar hasta que Huahua conteste** qué posición del paquete acepta la Ø35 y con qué giro.
Si contestan "izquierda", la EHBRO3570NPI a $54.061 es la compra. Si contestan "derecha", hay
que preguntarle a SOLUZIONE por la 35 × 70 derecha (debería existir como EHBRO3570NPD).

### Mientras tanto — parche vigente

Seguir fresando con la Ø20 del puesto 4, **declarando el diámetro de la T184 en 15,3** en la
tabla de herramientas (dejando `ancho de aserrado` = 20 y `desplazamiento Z` = 27). Así los
archivos siguen pidiendo 35 y la máquina compensa el déficit medido de ~4,7 en X.

### 🔴 PENDIENTE ABIERTO — resolver el giro antes de comprar

**Lo único que falta para apretar "Comprar" es saber si la mecha va a giro DERECHA o IZQUIERDA.**

Depende de en qué posición del paquete de taladros verticales se monte: los husillos del
paquete alternan el sentido de giro, uno sí y uno no. Si se compra la mano equivocada, la
mecha gira al revés y **no corta**.

Está preguntado a Huahua por WeChat. La pregunta concreta es:

> ¿Qué posición del paquete de taladros verticales puede alojar una mecha de Ø35, y esa
> posición gira a derecha o a izquierda? Vástago Ø10, largo 70 mm.

**En cuanto contesten:**
- Si dicen **izquierda** → comprar la **EHBRO3570NPI, $54.061**, link arriba.
- Si dicen **derecha** → preguntarle a SOLUZIONE ACCESORIOS por la **35 × 70 derecha**; la que
  tienen publicada es 35 × 57 y con el código dudoso (`EHBRO4057NPD`).

---

## 20. Lista completa de mechas que faltan (24/09/2026)

### Lo que piden los archivos de PRUEBA 1

Contados directamente sobre los 10 XML3 de `etapa2/salida/PRUEBA1/XML3/`:

| Operación | Ø | Cantidad total | ¿Hay herramienta? |
|---|---|---|---|
| Agujero vertical | **6** | 16 | ❌ **NO** — hoy se hace con Ø5 (T162) |
| Agujero vertical | 10 | 20 | ✅ sí |
| Agujero vertical | 15 | 16 | ✅ sí |
| Agujero vertical | **35** (cazoleta) | 4 | ❌ **NO** — hoy se fresa con la Ø20 del puesto 4 |
| Agujero horizontal | 8 | 14 | ✅ sí |
| Ranura (Line) | ancho 6 | 4 | ✅ T187 |
| Ranura (Line) | ancho **9** | 1 | ⚠️ el mínimo en cara dorso es 10 → se cambió a 10, lo hace **T11** |

**Taladros verticales que tiene la máquina hoy: Ø5, Ø8, Ø10, Ø12, Ø15, Ø20. Horizontales: Ø8.**

### Entonces faltan DOS mechas, no una

#### 1. Mecha vertical Ø6 — para los 16 tornillos de bisagra

Misma línea Euro Hard, mismo vendedor (SOLUZIONE ACCESORIOS). Descripción idéntica:
*"para agujereadoras múltiples y máquinas CNC"*, *"Vástago Ø10 para mandriles de acople rápido,
con plano de fijación y prisionero de ajuste"*. Filos Widia, PTFE, 3 puntas, no pasante.

| Modelo | Medida | Giro | Precio | Link |
|---|---|---|---|---|
| **EHBRO0670NPD** | 6 × 70 | **derecha** | **$27.855** | https://www.mercadolibre.com.ar/broca-mecha-no-pasante-6-mm-x-70mm-derecha-p-placas-madera/up/MLAU126150590 |
| — | 6 × 57 | **izquierda** | $27.855 | https://www.mercadolibre.com.ar/broca-mecha-no-pasante-6mm-x-57mm-izquierda-p-placas-madera/up/MLAU126142924 |
| — | 6 × 57 | derecha | $29.535 | https://www.mercadolibre.com.ar/broca-mecha-no-pasante-6-mm-x-57mm-derecha-p-placas-madera/up/MLAU126317831 |

> La 6 × 70 **izquierda** no apareció publicada. Si hace falta esa mano, preguntarle al vendedor.

**Mismo problema de giro que la Ø35**: depende de qué posición del paquete la aloje. La
pregunta a Huahua sirve para las dos — hay que pedir que contesten por ambas.

**Mientras tanto el parche funciona**: los Ø6 pasados a Ø5 se procesan sin error con la T162.
Se pierde apriete del tornillo de bisagra, pero mecaniza.

#### 2. Cazoleta Ø35 — ver sección 19

### Lo que NO hace falta comprar

- **Fresa de ranurar Ø9**: no se compra, se cambia el diseño. El ancho mínimo de ranura en cara
  dorso es 10 y la T11 (Ø10) ya la hace bien. Dejar las ranuras de dorso en 10 mm.
- **Ø8 horizontal, Ø10, Ø15 verticales**: ya están montadas y funcionando.

### Sigue pendiente aparte (otra máquina)

- **Router: cargar T1 Ø6 en su almacén** — es el router, no la perforadora. Va en otra sesión.
- **Fresa espiral Ø20 de repuesto** para el puesto 4: la que está hoy hace las cazoletas y se
  va a gastar. No es urgente hasta que llegue la Ø35.

### Resumen de la compra

| Qué | Cuánto | Cuándo |
|---|---|---|
| Mecha Ø35 cazoleta (Euro Hard) | ~$54.000 | cuando Huahua diga el giro |
| Mecha Ø6 vertical (Euro Hard) | ~$28.000 | cuando Huahua diga el giro |
| **Total** | **~$82.000** | mismo vendedor, un solo envío |

---

## 18. 24/09/2026 (noche) — COCINA MLV armada en Fusion desde el `render.json`

Nuevo script **`fusion/ArmarDesdeRender`**: lee el `render.json` de GuiGui (§17) y
arma el ambiente completo en Fusion, con agujeros, ranuras, contornos, colores
por textura y los herrajes dibujados (3 en 1, bisagras, correderas, tiras LED).
COCINA MLV: 14 muebles, 128 placas, 930 herrajes, 15 s. Guardado en Fusion como
`COCINA MLV` (carpeta `cocina`). Se leyó GuiGui por su MCP **solo lectura**
(`project_search_order`); el `render.json` bajado es byte a byte el mismo del
22/09 (`update_time` 2026-09-10 20:15:49).

Lo importante quedó en `fusion/README.md`, sección `ArmarDesdeRender`:

- **el marco de GuiGui descifrado** (`hdvDir`, `ocenter`, `side` de cara y de
  canto, `lastCurve` espejado, `sslots`), verificado contra los 80 agujeros de
  PRUEBA 1 y contra la propia geometría de la cocina;
- **cajones, zócalos, tapas y uñeros vienen girados 180°** respecto de `hdvDir`;
  no hay dato que lo diga, se decide por consistencia (perno ↔ receptor,
  ranura ↔ fondo, cazoleta ↔ base). 290/294 pernos cierran; los 4 restantes son
  los dos uñeros, que GuiGui dibuja con perno de los dos lados del encuentro;
- dos trampas de la API: `addExistingComponent` compone la matriz con la de otra
  ocurrencia (se asigna `transform2` sobre el proxy del root), y el diseño va en
  modo directo.

Pendiente: ejecutar `ExportarPiezas` sobre COCINA MLV y validar contra el
`Mass production.json` de la cocina cuando lo tengamos (la cara A la elige el
script: cara `side −1` de GuiGui, que no siempre es la que GuiGui mecaniza —
ver README, es una diferencia de marco, no de geometría).

### ⚠️ Aclaración importante sobre el giro (25/09) — la fresa que tenemos NO sirve de referencia

La fresa que está montada en el **puesto 4** está grabada `Ø20x70R 250710` (captura
`35_fresa_espiral_o20x70R.jpg`). La **R final significa Right = giro a derecha**. O sea: **el
husillo de fresado ER25 gira a derecha.**

**Pero eso no contesta la pregunta de las mechas.** Son dos cosas distintas:

| | Fresa Ø20x70R (la que tenemos) | Mechas Ø35 y Ø6 (las que faltan) |
|---|---|---|
| Dónde va | husillo **ER25** de la revista de conos (puesto 4) | **paquete de taladros verticales** |
| Mango | cilíndrico liso, lo aprieta la pinza ER25 | **Ø10 con plano de fijación y prisionero** |
| Giro | el del husillo de fresado — **derecha** | el de **su posición del paquete**, que alterna |

Los husillos del paquete de taladros **alternan el sentido uno sí y uno no**, y no tienen nada
que ver con el husillo de fresado. Que la fresa sea derecha **no implica** que la posición del
paquete donde vaya la Ø35 sea derecha.

#### Cómo averiguarlo sin esperar a Huahua

**Sacar una de las mechas verticales que ya están montadas y leer el grabado del mango.**
Vienen marcadas con `L` / `R` (o `I` / `D`), y algunas marcas usan color: naranja = izquierda,
negro = derecha (así las marca Euro Hard). Mirando dos mechas **vecinas** se confirma de una
si el paquete alterna, y qué mano le toca a la posición libre.

Pendiente de hacer en la máquina.

### Contactos técnicos de Huahua (grupo de WeChat) — 25/09/2026

| Nombre | Rol | Empresa | Contacto |
|---|---|---|---|
| **谭小姐 / 谭文舒** (Srta. Tan) | comercial / primera línea | Win-HUAHUA | el contacto habitual del grupo |
| **周涛 (Zhou Tao)** | **técnico** | 昶盛机械制造有限公司 (Changsheng Machinery Manufacturing) | **139 2595 7559** |
| **唐玮民 (Tang Weimin)** | técnico | 桦桦 (Huahua) | por el grupo |

**Dato nuevo**: el fabricante detrás de la marca Huahua es **昶盛机械制造有限公司 — Changsheng
Machinery Manufacturing Co., Ltd.** Los técnicos son de ahí, no de la comercial.

**Estado de las preguntas al 25/09**: la Srta. Tan escaló las 12 preguntas, etiquetó a los dos
técnicos y sumó a Zhou Tao al grupo. Zhou Tao confirmó: *"这个是上班以后处理"* — se resuelve
apenas vuelvan del feriado (Festival del Medio Otoño). Esperar al lunes.

---

## 20. Curvado por ranuras — web `curvado/` (26–27/09/2026)

Web para diseñar piezas curvadas por ranurado (kerf bending) y sacar todo el paquete de
producción. Vite + three.js + jsPDF, **corre entera en el navegador** (sin backend).
Código en `curvado/` (ver `curvado/README.md`). Publicada en **Vercel, equipo LeitenTeam**,
proyecto importado de `Barton-user/fabricamuebles` con **Root Directory = `curvado`**, framework
Vite. Cada push a `main` que toque `curvado/` se publica solo.

### Qué hace

- **Entrada**: placa (material, espesor nominal y **real**, piel, alto, cantos, veta) y perfil en
  tramos: rectos + curvas (radio **sobre la cara vista**, ángulo, **convexa/cóncava** por curva,
  cantidad de ranuras automática o forzada). Presets: mostrador, esquina R100, medio círculo,
  onda S, cóncava. Deslizadores + número en espesor, piel, alto, largo, radio, ángulo y ranuras.
- **Cálculo** (`src/motor.js`): línea de desarrollo = plano medio de la piel.
  `Rm = R ∓ s/2`, largo de curva `Rm·θ`; ranuras mínimas (convexa) `θ·(t − s/2)/(w·cierre)`;
  por facetado, tramo recto entre ranuras `≤ √(8·Rm·flecha)`; piel `ε ≈ s/2Rm` contra un límite
  orientativo por material; costilla mínima. Cóncavas: las ranuras se abren.
  V: `N = ⌈θ/β⌉`, boca `plano + 2(t−s)tan(β/2)`.
- **Herramientas** (la forma de la ranura la define la fresa elegida): recta (corte
  descendente/ascendente/compresión), punta redonda (esférica / media caña), V (con o sin fondo
  plano), disco. Tablas editables por máquina + **catálogo de medidas comerciales**
  (`src/catalogo.js`: Whiteside MD 6×22…10×38, Amana 46456 esférica Ø6×22, media caña métrica,
  V de grabado 6 mm 15–60°, V de insertos 40–90°, V de plegado con fondo plano Amana
  RC-1172 / RC-1175).
- **Vistas**: 3D con curvado en **loop** (pausa, deslizador, ⇄ lado, 🔍 ranura, ⌖ Centrar /
  doble clic, ⟲ Inicial; la pieza se mantiene centrada), detalle de una ranura plana y curvada
  con cotas, planta curvada contra el perfil objetivo, plano de taller. Todo en una pantalla
  (formulario en pestañas Pieza / Perfil / Ranurado / Máquinas).
- **Paquete .zip** (carpeta = código `999MMDDhhmmss`):
  - `SIERRA/lista_corte.csv|xlsx` → AutoCUT (mismas columnas que `listacorte.py`)
  - `PERFORADORA/XML3/<código>.xml` (KDTXml, TypeNo 3 cara A / 13 cara B) y `MPR/<código>.mpr` (+K)
  - `ROUTER/<código>_ranuras_T<n>.nc` (+ contorno opcional), dialecto GuiGui: Z0 mesa, Z = piel
    en el fondo, Z38, CRLF, sin encabezado (preset Syntec con `T M06 / M03` opcional). Entra y
    sale fuera de la placa, pasadas de profundidad configurables.
  - **`<código>_hoja_de_taller.pdf` A4 (4 hojas)**: pieza y programas, plano y ejes de ranura,
    cómo queda curvada, cómo se apoya en la HP280 y en la máquina elegida, pasos sierra →
    ranurado → cantos (HH-509R) → plegado, tabla de control final.
  - planos SVG, captura 3D, `LEEME.txt`.
- **Validación**: los escritores JS (`src/exportar.js`) son puertos de `etapa2/xml3.py`,
  `mpr.py`, `listacorte.py`: `npm test` + `python3 curvado/test/validar.py etapa2` → 6/6 iguales.

### Decisiones tomadas

- Perforadora: ranuras en **cara A** (husillos superiores) = placa con la **cara vista contra la
  mesa**; profundidad = espesor **real** − piel (Z0 en la cara). Cara B sólo con T11 Ø10 → poco útil.
- Router: fondo en **Z = piel desde la mesa** → la piel sale exacta aunque varíe la placa.
- Fuera de la SKH-612HS: ranura en V (no la hace); pieza fuera de 250–5000 × 50–1200 o
  espesor fuera de 10–48 (manual SKH-612H).
- Tip de catálogo: la **media caña con mango ½″ no llega a 16 mm** (baja 7–10,5); en 18 mm la
  punta redonda útil es la **esférica Ø6×22**. De las V de grabado de 6 mm sólo la de 15° llega.

### Lo que FALTA (en orden)

1. **Medir en el taller** y cargar en la tabla de la web:
   - profundidad máxima real del disco **T183** (Ø43,9 × 3);
   - herramientas reales del **router SKG-912MZ** (T1 Ø6 sigue sin cargar en el almacén;
     ¿hay V? ¿esférica?) y su largo de corte;
   - **mesa útil** del router (quedó 1250 × 2500 como supuesto).
2. **Probetas por material** (MDF, aglomerado, multilaminado, MDF crudo): ranurar un retazo,
   curvarlo y ajustar piel mínima y el límite `epsMax` de `MATERIALES` en `src/motor.js`.
3. **Primera pieza real** por perforadora y por router: medir piel, eje de la 1ª ranura desde
   INICIO y cantidad; confirmar que MH2026 asigna la herramienta esperada al ancho de ranura.
4. **Cantos en zona curva**: probar si el canto de arriba/abajo pegado antes de plegar se arruga;
   si pasa, cambiar el paso 3 de la hoja de taller (pegar después de plegar o cubrir con tapa).
5. **Tapas / molde**: generar desde la misma web el piso y el techo con el contorno (router,
   `.nc` de contorno curvo) — hoy la hoja sólo da el radio del molde.
6. Mapeo de AutoCUT (§18) sigue pendiente: afecta también a esta lista de corte (código limpio
   para la etiqueta).
7. Opcional: el `.nc` de ranuras con cambio de herramienta Syntec validado en la máquina.

> **Git**: el sandbox de Claude no puede borrar archivos en la carpeta; cuando hace `git status`
> suele quedar un `.git/index.lock` vacío. Antes de commitear: `rm -f .git/index.lock`.

---

## 21. COCINA MLV — control contra GuiGui y unión de los uñeros corregida (27/09/2026)

- `ExportarPiezas` sobre COCINA MLV → `fusion/EXPORT_COCINA_MLV/` (128 piezas; BAN/XML1/XML3 126,
  MPR 202, lista de corte 128, hojas 110). Faltan los 2 travesaños con ranura de canto (sslot `BP`
  para el fondo): el generador no escribe ranuras de canto → pregunta a Huahua (formato "SlotH").
- Comparado pieza por pieza contra el `render.json`: 113/128 idénticas. Diferencias explicadas:
  16 Ø3 de corredera **duplicados en GuiGui** (Fusion deja uno); 5 Ø8 de la escotadura del uñero en
  laterales (Cajonera ×2, Bajo mesada ×1) que **están en el modelo pero `ExportarPiezas` descarta**
  ("cilindro horizontal ignorado: no toca ningún canto") → **pendiente arreglar el exportador**.
- **Error de GuiGui corregido en Fusion**: los dos tramos del uñero (01 y 02) se tocan en X=350 y
  GuiGui les puso un 3 en 1 en cada punta mirando al otro, sin receptor (los únicos 4 pernos de 294
  sin receptor). `fusion/CorregirUnero/` los saca, pone Ø10 en los 4 tramos y agrega el 3 en 1 en la
  escotadura de los laterales de abajo (Bandejero Right board01, Horno Left board01), igual que la
  Cajonera. Verificado: 294 pernos / 294 receptores. Guardado como versión nueva de COCINA MLV.
- **`ExportarPiezas` lee ahora los agujeros de canto de una escotadura** (`Marco.canto_interior`):
  el contorno se lee antes que los agujeros y un Ø8 que arranca en un tramo recto interior toma la
  letra del canto por la normal de salida (escalón con material abajo = U, tramo vertical con
  material a la izquierda = R, igual que GuiGui). Los escritores ya aceptaban la boca en cualquier
  punto. El lanzador `GENERAR ARCHIVOS.command` ya no se corta si `exportar.py` rechaza una pieza.
- Re-export completo (27/09, 22:19): **128/128 piezas con los mismos agujeros que GuiGui corregido**
  (posición incluida; diferencias < 0,002 mm). Totales: Ø15 294, Ø8 canto 294, Ø10 266 + 28 de canto,
  Ø6 100, Ø35 25, Ø3 32. BAN/XML1/XML3 126, MPR 202, lista de corte 128.
- ⚠️ **A confirmar en la SKH-612HS**: los 9 Ø8 que entran por la escotadura del uñero (50 × 70). No
  sabemos si el husillo horizontal entra en ese hueco. Probar con la primera pieza (lateral de la Cajonera).

### 25-28/09 — Código de colores confirmado, y por qué "arriba" no define el giro

**Se sacó una mecha del paquete de ABAJO y es NARANJA.** Confirma que la máquina usa la
convención estándar, la misma que declara Euro Hard en sus publicaciones:

> **NARANJA = IZQUIERDA · NEGRO = DERECHA**

Desde ahora el giro de cualquier mecha se lee de un vistazo, sin desmontar nada.

#### ⚠️ Arriba / abajo NO define el giro

En un paquete de taladros el accionamiento es un **tren de engranajes**: cada husillo engrana
con el de al lado, así que **husillos vecinos giran al revés uno del otro**. Por eso alternan.

- Que la Ø35 baje desde arriba dice **en qué paquete va**, no con qué mano.
- El giro lo define **la posición exacta** dentro de ese paquete.
- Tampoco sirve de referencia la mecha naranja de abajo: es otro paquete.
- Tampoco el husillo de fresado ER25 (la Ø20x70R, derecha): es otro motor.

#### Cómo resolverlo en 2 minutos, sin esperar a Huahua

1. En la tabla de herramientas, el diagrama **"bolsa de taladro 1 / 2"** muestra la disposición
   física de los verticales de arriba con sus coordenadas X/Y. Ubicar **qué posición está libre**
   (candidata para la Ø35 y la Ø6).
2. Mirar el **color** de las mechas vecinas a ese hueco, contando a lo largo de la fila.
   Alternan naranja–negro–naranja–negro.
3. La posición libre hereda la mano que le toca por alternancia. Ese es el giro a comprar.

Anotar en esta sección qué posición es y de qué color son las vecinas.

#### Duda que sigue abierta

El paso entre husillos del paquete ronda los 32 mm y la tabla de verticales no pasa de Ø20.
**Puede que físicamente no haya lugar para una Ø35 en el paquete.** Si es así, la única vía es
el husillo ER25 en el puesto 186 (que está libre): ahí el giro sería **derecha** y el largo
**70 mm**, pero habría que poder bajar las RPM del husillo (gira a 18000; una mecha de tres
puntas Ø35 quiere ~3000). Las dos cosas están preguntadas a Huahua.

---

## 21. 🚨 HALLAZGO: en el paquete de arriba NO hay lugar para una Ø35 (28/09/2026)

Releyendo las capturas de la tabla de herramientas (`15_`, `17_`, `18_` de `instructivo/capturas/`)
aparece el dato que faltaba. **La tabla NO tiene columna de giro** — las columnas son:
No · permitir · número de cuchillo · ajuste automático · grupo · diámetro · ancho de aserrado ·
en forma de T · **tipo de herramienta** · X · Y · desplazamiento X/Y. Así que el software no
puede decirnos izquierda o derecha.

**Pero dice algo más importante: la geometría del paquete.**

### Paquete de ARRIBA (`Z positivo` = cara frente) — filas 1 a 9

| Fila | Nº cuchillo | Ø | X | Y |
|---|---|---|---|---|
| 1 | 1 | **10** | 0 | 0 |
| 2 | 2 | **20** | −32 | 0 |
| 3 | 3 | **5** | −64 | 0 |
| 4 | 4 | **8** | 0 | −32 |
| 5 | 5 | **15** | −32 | −32 |
| 6 | 6 | **12** | −64 | −32 |
| 7 | 7 | **10** | 0 | −64 |
| 8 | 8 | **8** | −32 | −64 |
| 9 | 9 | **10** | −64 | −64 |

> ⚠️ **Corregido el 30/09 (§26.2):** la conclusión de abajo de que "una Ø35 no entra en paso 32"
> es un error de cuenta — chocan si la suma de los **radios** pasa 32, o sea que entra con vecinas
> de hasta Ø29. La vía del paquete vuelve a estar abierta.

**Es una grilla de 3 × 3, paso 32 mm en X y en Y. Las nueve posiciones están ocupadas y
habilitadas.** No hay hueco libre, y **una mecha de Ø35 no entra en un paso de 32 mm**: chocaría
con la vecina. Por eso la tabla de verticales se corta en Ø20 — es el máximo que permite el paso.

> ⚠️ Las filas **15 a 27** de la tabla no están capturadas. Por la numeración (1-9 = Z positivo,
> luego 11 y 20, luego 51+ = Z negativo) parece que el bloque de arriba termina en la 9, pero
> **hay que scrollear esas filas y confirmarlo**.

### Consecuencias — esto cambia el plan de compra

**1. La cazoleta Ø35 NO puede ir en el paquete. Queda una sola vía: el husillo ER25.**

El puesto **186** figura en la tabla como **"Sin carg..."** (Ø24, ancho 24, en X −24,5 / Y 388,8):
está libre. Ahí la pinza ER25 toma un mango Ø10 sin problema.

→ La mecha a comprar es **Ø35 × 70 mm GIRO DERECHA** (el husillo es R, confirmado por la
`Ø20x70R`; y 70 porque el manual pide más de 45 mm de voladizo — con 57 no alcanza).
→ SOLUZIONE no la tiene publicada en 70 derecha. **Hay que pedírsela.**
→ Falta confirmar con Huahua si se puede bajar la velocidad del husillo (gira a 18000; una
mecha de tres puntas Ø35 quiere ~3000 rpm).

**2. La Ø6 tampoco tiene hueco: hay que REEMPLAZAR una mecha existente.**

Los programas de PRUEBA 1 usan Ø10 ×20, Ø15 ×16, Ø6 ×16, Ø8 horizontal ×14. Arriba hay **tres
Ø10** (posiciones 1, 7 y 9) y **dos Ø8** (4 y 8). Sobra un Ø10.

→ **Candidata a reemplazar: la posición 7 o la 9** (Ø10 redundante) por una **Ø6**.
→ Y ahora el giro se resuelve solo: **sacar esa mecha y mirarle el color.** Naranja =
izquierda, negro = derecha. Es del paquete de arriba, así que esta vez sí es la referencia
correcta.
→ Después de cambiarla, corregir el diámetro a 6 en la tabla (contraseña `520`) y regenerar.

### Qué preguntar / hacer, en orden

| # | Qué | Quién |
|---|---|---|
| 1 | Sacar la mecha de la posición **7** (Ø10, X 0 / Y −64) y leer su color → giro de la Ø6 | Pato, en la máquina |
| 2 | Scrollear las filas 15-27 de la tabla y confirmar que no hay más posiciones arriba | Pato |
| 3 | Preguntar a SOLUZIONE: ¿tienen **Ø35 × 70 giro derecha**, vástago Ø10 con plano? | Pato, por ML |
| 4 | Preguntar a Huahua: ¿se puede bajar la RPM del husillo de fresado por herramienta? ¿Y se puede montar una Ø35 en el cono del puesto 186? | WeChat |

### ✅ 28/09 — Giro resuelto y mecha Ø35 DERECHA encontrada

**La Ø35 va en el husillo ER25 (puesto 186, libre). Mismo husillo que la `Ø20x70R`, o sea
mismo giro: DERECHA.** Y el largo también queda confirmado: la Ø20 mide 70 de largo total y dio
los 46 mm de voladizo que pide el manual → la Ø35 también va de **70**.

**Especificación final: Ø35 · largo total 70 mm · vástago Ø10 · giro DERECHA · no pasante.**

#### Dónde comprarla

| Marca | Modelo | Precio | Con cupón | Link |
|---|---|---|---|---|
| **FUL** | **MBD3570** | **$73.516,30** | **$70.016,30** (siguiendo la tienda) | https://www.mercadolibre.com.ar/mecha-fresa-para-madera-bisagra--35mm-x70mm-derecha-widia/up/MLAU3931773080 |
| FUL | MBD3570 | $77.094,14 | $73.594,14 | https://www.mercadolibre.com.ar/mecha-fresa-para-madera-bisagra--35mm-x70mm-derecha-widia/up/MLAU3920150205 |

Widia, 35 mm de diámetro de corte, 70 mm de largo total. **La primera es la más barata.**
La publicación no declara el vástago; es la familia estándar de Ø10, pero conviene
preguntárselo al vendedor antes de comprar.

> La Euro Hard (EHBRO3570NPI, $54.061) es más barata pero es **IZQUIERDA** — no sirve para el
> husillo. Su versión derecha publicada es de 57 mm, demasiado corta para la pinza ER25.

#### Sigue abierto

- **RPM**: el husillo gira a 18000 y una mecha de tres puntas Ø35 quiere ~3000. Preguntado a
  Huahua si la velocidad se baja por herramienta. **Es el riesgo principal de esta vía.**
- **La Ø6**: va en el paquete de arriba, reemplazando un Ø10 redundante (posición 7 o 9). Su
  giro sale de mirarle el color a la mecha que se saque.

---

## 22. 🛒 LISTA DE COMPRA VIGENTE (28/09/2026)

Esta tabla reemplaza a todo lo anterior. Las secciones 19 y 20 quedan como historial.

| # | Qué | Especificación | Estado | Precio | Link |
|---|---|---|---|---|---|
| 1 | **Mecha cazoleta Ø35** | Ø35 · **70 mm** · vástago Ø10 · **DERECHA** · no pasante | 🛑 **FRENADA (30/09)** — no se sabe si va en el husillo o en el paquete; ver §26.2 | **$73.516** (cupón $70.016) | [FUL MBD3570](https://www.mercadolibre.com.ar/mecha-fresa-para-madera-bisagra--35mm-x70mm-derecha-widia/up/MLAU3931773080) |
| 2 | **Mecha vertical Ø6** | Ø6 · 57 o 70 mm · vástago Ø10 · **giro a confirmar** | ⏸ Huahua confirmó (30/09): cambiar la mecha y poner 6 en la tabla. Falta leer **color y largo** de las posiciones 7 y 9 del paquete de arriba | ~$28.000 | [derecha 6×70](https://www.mercadolibre.com.ar/broca-mecha-no-pasante-6-mm-x-70mm-derecha-p-placas-madera/up/MLAU126150590) · [izquierda 6×57](https://www.mercadolibre.com.ar/broca-mecha-no-pasante-6mm-x-57mm-izquierda-p-placas-madera/up/MLAU126142924) |
| 3 | Fresa espiral Ø20 de repuesto | igual a la `Ø20x70R` del puesto 4 | 🕓 no urgente | — | — |
| 4 | Fresa Ø6 para el **router** (T1) | otra máquina | 🕓 otra sesión | — | — |

**No se compra**: fresa de ranurar Ø9 (se cambia el diseño a ranuras de 10 mm, que la T11 ya
hace bien). Ø8 horizontal, Ø10 y Ø15 verticales ya están montadas.

**30/09:** Huahua dio dos respuestas opuestas sobre dónde va la Ø35 y la cuenta de §21 estaba mal →
la compra de la FUL queda frenada hasta que contesten la pregunta cerrada de §26.4.

**Riesgo a cubrir antes de usar la Ø35**: el husillo gira a 18000 rpm y una mecha de tres puntas
Ø35 quiere ~3000. Si Huahua confirma que no se puede bajar, la mecha se quema. Preguntado.

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

## 26. Respuestas de Huahua a las 12 preguntas (30/09/2026)

Contestaron en el grupo de WeChat, en chino, **intercaladas debajo de cada pregunta** del mensaje
del 24/09 (§17). Las preguntas nuevas del fresado (marca de entrada, campana) y el aviso del
manual **no tienen respuesta todavía**, salvo un mensaje suelto sobre la Ø35 (ver 26.2).

### 26.1 Pregunta por pregunta

| # | Pregunta | Respuesta literal | Qué dice | Qué cambia para nosotros |
|---|---|---|---|---|
| 1 | Cómo se calibra el largo de la fresa; en qué pantalla | 调整对应刀具库z偏移（深度） | "Ajustar el desplazamiento Z (profundidad) de esa herramienta en la biblioteca de herramientas." | **Confirma lo que ya hicimos.** No hay pantalla de medición de herramienta: se calibra a mano con el Z de cada una (T184 = **27**, fórmula en §16). |
| — | (anotado junto a la pista de la marca de 85–90 mm) | 应该调整同动刀190/Z偏移/ | "Había que ajustar la herramienta asociada **190** / el desplazamiento Z." | **Dato nuevo: la T190** (en la tabla figura Ø0, sin uso aparente, sesión del 23/09) sería una herramienta "同动" (que se mueve junto con el husillo — probablemente la referencia de altura del cabezal de fresado). Como ya quedó bien con el Z de la T184, **no tocar la T190** sin saber qué es: si es la referencia común, moverla descalibra todas las fresas. Repreguntado. |
| 2 | ¿46 mm de voladizo es demasiado? | 打开铣刀压板，不超过压板即可 | "Bajá la placa de la fresa (压板); alcanza con que la fresa no sobresalga de la placa." | **Regla de voladizo:** con la placa abajo, la punta **no tiene que pasar el borde inferior de la placa**. Medirlo con la Ø20 montada. Ojo con el nombre: 压板 es "placa prensora", lo mismo que la interfaz llama "Placa de sujeción del cortador" y que en §16 identificamos como campana de aspiración. Puede que, además de encerrar la viruta, **apriete la placa** alrededor de la fresa. |
| 3 | Procedimiento de "todas las puntas en el mismo plano ±1 mm" (manual cap. 18) | 打开所有垂直钻，保持同一个高度，误差不超过正负1 | "Bajá todos los taladros verticales; que queden a la misma altura, con error no mayor a ±1." | **Procedimiento:** Manual → bajar todos los verticales a la vez → con calibre de profundidad o una regla apoyada, comprobar que todas las puntas queden a ±1 mm → la que no, aflojar prisionero y correrla en el mandril. **Hacerlo cada vez que se monte una mecha** (la Ø6, y la Ø35 si va al paquete). |
| 4 | Por qué sale ovalado; dónde está la interpolación circular | 调整对应刀具进给速度慢速即可 | "Alcanza con bajar la velocidad de avance de esa herramienta." | No hay parámetros de interpolación para tocar. El ovalado grande (26 × 32) era el Z; el que quedó (30,16 × 32,7, §19) **probar bajando el avance de la T184**. Si con avance bajo sale redonda y a medida, **se puede sacar el parche de diámetro 15,3** y volver a 20. |
| 5 | ¿Se puede agregar una Ø35 al paquete de verticales? | 不建议安装 | "No se recomienda instalarla." | **Se contradice con otro mensaje — ver 26.2.** |
| 6 | Dónde se cambia el avance de la T184 | 刀具库设定，每一把都是独立设定 | "En la configuración de la biblioteca de herramientas; cada una tiene su ajuste independiente." | Confirma: fila de la T184 → **"Ajuste de velocidad"** (10000 / 1000 / 500, vel. 5000). Cambiar sólo esa; no afecta a las otras. |
| 7 | Cómo poner "herramienta en el husillo" en T0 | 这种情况需要装回187号刀具 | "En ese caso hay que volver a montar la herramienta 187." | **No hay forma de ponerlo en T0 por software.** Lo que hicimos el 24/09 (montar el cono a mano con el botón verde del cabezal, §16) es el procedimiento oficial. |
| 8 | Ø6: ¿se puede agregar, o pasar a Ø5? Y el crash | 直接换刀具就行（刀具库直径需要对应） · 需要提供文件和软件备份测试这个情况 | "Alcanza con cambiar la mecha (el diámetro de la tabla tiene que coincidir)." · "Para el crash necesitan el archivo y un backup del software para probarlo." | **Confirma el plan de §21:** sacar un Ø10 redundante del paquete de arriba (posición 7 o 9), poner la Ø6, cargar **6** en la tabla (clave 520) y regenerar. Para el crash: mandarles un XML con Ø6 (`9441838670057.xml` de PRUEBA 1 sirve) + el backup — falta saber cómo se saca el backup. |
| 9 | Ancho mínimo de ranura en cara dorso | 刀具库没有对应的刀具直径 | "La biblioteca no tiene una herramienta de ese diámetro." | El mínimo es **la herramienta más chica cargada para esa cara** (T11, Ø10). Queda como decidimos: ranuras de dorso de **10 mm**. |
| 10 | KDTXml como formato por defecto | 提供操作视频 | "Proporcionar video de la operación." | **Ambiguo**: o nos mandan un video de cómo se configura, o nos piden que filmemos el problema. Repreguntado. Mientras tanto, cambiarlo a mano cada vez (sesión del 23/09). |
| 11 | Usuario del login (¿clave 520?) | — | sin respuesta | Sigue candidato **`Admin` / 520**, sin confirmar. |
| 12 | Cómo marcar el mantenimiento como hecho | 输入权限后点击更新就可以 | "Después de ingresar el permiso, apretar **Actualizar**." | Mantenimiento → ingresar el permiso (probar **520**) → **Actualizar** en cada tarea. **Hacer primero la lubricación de verdad** (12 tareas vencidas desde 2026-01-04, ver manual). |

### 26.2 🚨 La Ø35: dos respuestas que se contradicen — FRENAR la compra de la FUL

- A la pregunta 5 (¿Ø35 en el paquete de verticales?) contestaron **不建议安装 — "no se recomienda"**.
- En un mensaje aparte, contestando al "please i need those answers", escribieron:
  **安装一把35直径刀具。钻包设置里面把直径改一下就可以了。** — *"Montá una herramienta de Ø35.
  En la configuración del paquete de taladros cambiás el diámetro y listo."*

"钻包设置" es la pantalla **"Configuración de paquete de…"**, donde están **tanto los verticales
como las fresas** (T184, T186…). Así que la frase no aclara si la Ø35 va en el paquete o en el
husillo ER25.

**⚠️ Corrección a §21: la cuenta de "una Ø35 no entra en paso de 32 mm" estaba mal.** Dos mechas
vecinas chocan sólo si la suma de sus **radios** supera la distancia entre centros:
`17,5 + r_vecina < 32` → **entra con cualquier vecina de hasta Ø29**. Las vecinas de la
posición 7 (Ø8 en la 4 y en la 8) y de la 9 (Ø12 en la 6, Ø8 en la 8) dejan **9 a 11 mm de luz**.
Que la tabla de verticales llegue sólo hasta Ø20 no prueba que no entre. En la industria las
cazoletas de 35 se montan habitualmente en paquetes de paso 32. Lo que sí puede frenarla es algo
que no vemos (peso, torque del motor del paquete, carrera) — quizá por eso el "no se recomienda".

**Así quedan las dos vías:**

| | A · En el paquete de arriba | B · En el husillo ER25 (puesto 186) |
|---|---|---|
| Dónde | reemplaza un Ø10 redundante (pos. 7 o 9); la Ø6 va en la otra | puesto 186, libre |
| Giro | el de esa posición → **color de la mecha que se saque** | **DERECHA** (igual que la Ø20x70R) |
| Largo | **el mismo que las otras mechas del paquete** (regla ±1 mm) — medir: 57 o 70 | 70 |
| RPM | la del paquete, apta para Ø35 | **18000** — riesgo de quemarla si no se puede bajar |
| Qué comprar | Euro Hard 35 × 57/70 de la mano que toque | **FUL MBD3570** (§22) |
| Dijo Huahua | "no se recomienda" | nada claro |

**Decisión: no comprar la Ø35 hasta que contesten A o B** con la pregunta cerrada de 26.4. Si
ya se compró la FUL derecha 70, sirve igual para la vía B, y para la A sólo si la posición resulta
negra (derecha) y el paquete usa mechas de 70.

**Lo que se puede hacer ya, sin esperar:** sacar las mechas de las posiciones **7 y 9** del paquete de
arriba y anotar **color (giro) y largo total**. Con eso la vía A queda especificada y la Ø6 también.

### 26.3 Lo que sigue sin respuesta

1. **RPM del husillo de fresado por herramienta** (18000 → ~3000 para una Ø35). Clave para la vía B.
2. **Marca de entrada del fresado circular**: ¿hay arco de entrada/salida? ¿cuál de los tres valores
   de "Ajuste de velocidad" es el de bajada? (La respuesta 6 sólo dice que es por herramienta.)
3. **La campana / placa prensora no baja sola** durante el fresado; bajada a mano → `MLC 129`.
4. **Qué es la T190** (同动刀) y si hay que tocarla.
5. **Usuario del login.**
6. **KDTXml por defecto**: ¿el video lo mandan ellos o lo pedimos nosotros?
7. **Cómo sacar el backup del software** para que prueben el crash de la Ø6.
8. **Manual 11.3** ("más valor, más profundo" es al revés): avisado dos veces, sin acuse.

### 26.4 Mensaje listo para mandar (pegar en el grupo)

```
谢谢您的回复！还有几个问题需要确认：

1. Ø35 铰链杯：第5题您说立钻"不建议安装"，后面又说"安装一把35直径刀具，钻包设置里改直径"。
   请确认 Ø35 钻头应该装在哪里？
   A. 上钻包的立钻位置（替换7号或9号 Ø10 钻头）——这个位置是左转还是右转？钻头长度用57还是70？
   B. 铣刀主轴 ER25（186号刀位，现在是空的）——主轴转速可以按刀具单独设定吗？
      现在是18000转，Ø35 三刃钻头大约需要3000转。

2. "同动刀190"是什么？需要调整吗？（T184 Z偏置设成27以后深度已经准了）

3. 铣刀压板在铣削的时候不会自动下降。怎么设置成铣削时自动下降？手动按下去会报 MLC 129。

4. 铣圆入刀点有凸出的痕迹。有没有圆弧切入/切出的参数？"速度调整"里三个数值（10000/1000/500），
   哪一个是下刀进给速度？

5. 第10题"提供操作视频"：是您发给我们视频，还是需要我们拍视频给您？

6. 登录的用户名是什么？（密码520）

7. Ø6 崩溃的问题：软件备份怎么导出？我们把文件和备份一起发给您。

谢谢！
```

Traducción para control: 1) ¿Ø35 en el paquete (pos. 7/9, qué giro, 57 o 70) o en el husillo
ER25 (¿se puede bajar la RPM por herramienta?)? 2) ¿Qué es la T190? 3) ¿Cómo hago que la placa
baje sola al fresar? 4) ¿Hay arco de entrada/salida y cuál de los tres valores es la bajada?
5) ¿El video lo mandan ustedes o lo filmamos nosotros? 6) Usuario del login. 7) ¿Cómo exporto
el backup?
