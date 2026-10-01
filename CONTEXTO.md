# FÁBRICA MUEBLES — Contexto técnico del proyecto

_Última actualización: 01/10/2026 — armado con Claude durante la puesta en marcha de la línea._

> **Cómo retomar con Claude**: abrir un chat con esta carpeta conectada y decir
> "leé CONTEXTO.md y seguimos desde el punto X".
>
> **Estado del proyecto → sección 15. Hoja de ruta (objetivo y etapas) → sección 16. MCP de GuiGui y modelos 3D bajados → sección 17. Web de curvado por ranuras (`curvado/`, Vercel) → sección 20. Herrajes Häfele equivalentes → sección 23. Respuestas de Huahua del 30/09 (y la Ø35 frenada) → sección 26. Alacena Spar por el camino Fusion → sección 27. 🔩 Bisagra real 48/6 (tornillos a 6 de la cazoleta) → sección 28. ✅ T184 = mecha Ø35 para cazoletas (variador a 100 Hz) → sección 29.**


> ### ✅ Vigente al 01/10/2026 — confirmado por Pato (manda sobre cualquier sección de abajo)
>
> - **Cazoleta Ø35**: mecha **FUL Ø35 × 70 R** comprada y montada en el cono de la **T184**
>   (tabla: diámetro 34.8 · ancho 34.8 · Z 27 · avances 5000/500/250). Ver §29.
> - **Variador del husillo (Delta MS300) quedó en 100 Hz ≈ 6000 rpm.** Así está bien para
>   cazoletas; **para ranurar con la T187 o la T11 hay que volver a 300 Hz**.
> - **Tornillos de bisagra: Ø5 para siempre.** La mecha Ø6 **no se compra**.
> - **Bisagra Grupo Euro: tornillos a 6 mm del centro de la cazoleta (48/6), no 14,5** — es la
>   medida vigente, pero **falta confirmarla con calibre** sobre la bisagra. Ver §28.
> - Lo que diga lo contrario más abajo (§5, §15.5, §19–22, §24, §26.2) es historia.

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

> 📦 _«6. Estado actual» → movida a `BITACORA.md`._

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

> 📦 _«10. Lo que FALTA (en orden)» → movida a `BITACORA.md`._

> 📦 _«10-bis. PROTOCOLO DE PRUEBA EN LA SKH-612HS (pendiente — próximo paso)» → movida a `BITACORA.md`._

> 📦 _«11. Preguntas abiertas a HUAHUA (Sra. Tan / 谭小姐, WeChat)» → movida a `BITACORA.md`._

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

> 📦 _«15.10 · Camino Fusion completo, probado como se va a usar (22/09/2026, noche)» → movida a `BITACORA.md`._

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

> 📦 _«15. 23/09/2026 — Primera sesión en la SKH-612HS» → movida a `BITACORA.md`._

> 📦 _«16. Sesión del 24/09 — contraseña, cazoletas resueltas, y el husillo trabado» → movida a `BITACORA.md`._

> 📦 _«17. Respuestas de Huahua (24/09) y traducción real de la botonera» → movida a `BITACORA.md`._

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

> 📦 _«19. Mecha Ø35 para cazoletas — qué comprar (24/09/2026)» → movida a `BITACORA.md`._

> 📦 _«20. Lista completa de mechas que faltan (24/09/2026)» → movida a `BITACORA.md`._

> 📦 _«18. 24/09/2026 (noche) — COCINA MLV armada en Fusion desde el `render.json`» → movida a `BITACORA.md`._

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

> 📦 _«21. COCINA MLV — control contra GuiGui y unión de los uñeros corregida (27/09/2026)» → movida a `BITACORA.md`._

> 📦 _«21. 🚨 HALLAZGO: en el paquete de arriba NO hay lugar para una Ø35 (28/09/2026)» → movida a `BITACORA.md`._

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

## 29. ✅ CAZOLETAS RESUELTAS: la T184 ahora es la mecha Ø35 (01/10/2026)

**La T184 queda fija para cazoletas.** Configuración que funcionó (cazoleta de prueba perfecta en
retazo de 744 × 401 × 18, programa `PENDRIVE/CURVADO_744x401/9992610019095.xml`):

| Qué | Valor |
|---|---|
| Herramienta | **FUL Ø35 × 70 R** (MBD3570, widia, mango Ø10) — la que se compró |
| Dónde | **cono de la T184**, revista puesto 4, pinza ER25 de 10 |
| Salida | **46 mm** desde la cara de la tuerca hasta la punta central (igual que la Ø20) |
| Tabla (Parámetro → Config. de paquete → ícono 184, clave 520) | **diámetro 34.8 · ancho 34.8 · Z 27** |
| Ajuste de velocidad (avances) | **5000 / 500 / 250** (antes 10000 / 1000 / 500) |
| Variador del husillo | **Delta MS300**, gabinete eléctrico: **100 Hz ≈ 6000 rpm** (venía en 300 Hz ≈ 18000) |

**Por qué 34.8 y no 35**: MH2026 trata a la T184 como **fresa** (tipo "Husillo Z negativo") y
planifica la cazoleta como fresado circular. Con herramienta = agujero (35/35) el radio del
círculo da 0 y tira `ArgumentOutOfRangeException ... index` ("error desconocido durante el
fresado"). Con 34.8 el círculo es de 0,1 mm: en la práctica baja derecho. El casillero
**"Cortador de agujero"** está deshabilitado para ese tipo de herramienta; no se cambió el tipo
(es la del husillo y se arriesga el cambio de cono).

**Por qué fallaba antes**: lo que estaba en la T184 como "fresa espiral Ø20x70R" **es una mecha**
(punta de centrado + espuelas), no una fresa de punta plana. No corta de costado: al hacer la
cazoleta por interpolación circular el servo del eje A se sobrecargaba
(`Drv_M3_SYNTEC 202h El motor está sobrecargado` · `203h Anomalía de detección de par` ·
`206h Over Torque`), quemaba el borde y rompía el PET. Bajar avances no lo arregló. La Ø20 quedó
guardada; **no volver a usarla para fresar**.

**Cómo se cambió la mecha** (sirve para cualquier cono):
1. Manual → 612NS → **"Modo de cambio de herramienta"** en verde (sin eso el botón no suelta).
2. Sosteniendo el cono, **botón verde físico del cabezal** (mantener ~1 s) → suelta el cono.
3. Cambiar la mecha en la pinza, misma salida (46).
4. Volver a poner el cono en el husillo (chavetas calzadas) → botón verde → lo chupa.
5. **Apagar el modo de cambio en MH2026 y en CncMon32 ("Cambio de cuchillo")** — si no, MLC 348.
6. Tabla de la T184 (diámetro/ancho) → "almacenar herramientas".

### ⚠️ El variador quedó en 100 Hz — afecta a TODAS las herramientas del husillo

El variador es uno solo para el husillo de fresado: la **T187 (Ø6, ranuras de fondo)** y la T11
también giran a 6000 rpm mientras esté en 100 Hz. Para ranurar, **volver a 300.0** (flecha ▲ +
ENTER con el husillo parado) y para cazoletas bajar a 100. Ojo: el sobrecargo de la ranura de
8 mm del curvado (01/10) fue **a 300 Hz**, así que eso es otro tema (pasada demasiado profunda
para la Ø6, o también es mecha y no fresa — revisarla).

Desde la PC **no** se puede hoy: "Convertidor de frecuencia" (Parámetro → Config. de paquete)
tiene una tabla por herramienta (nº de inversor, código de inicio / parada / velocidad, "Enable
automatic output speed code based on tool speed") pero está **vacía**. Para configurarla hace
falta que Huahua diga qué códigos y qué cableado usa el MS300.

### Pendientes que salen de acá

1. **Preguntar a Huahua** cómo se configura la velocidad por herramienta en "Convertidor de
   frecuencia" para el Delta MS300 (que la T184 vaya sola a 100 Hz y la T187 a 300).
2. **Revisar la T187** (Ø6 de ranurar): ¿es fresa o mecha? Si es mecha, cambiarla por fresa
   espiral Ø6 de verdad.
3. Comprar una **fresa espiral Ø20 de punta plana** (o Ø10/12) si algún día se quiere fresar
   (contornos, cazoletas de otros diámetros). Hoy no hace falta.
4. Las 3 puertas PET de la Alacena Spar tienen cazoletas fresadas mal (borde roto) y los Ø5 a
   14,5 (§28). Rehacer o aceptar según cómo queden con la bisagra puesta.
5. §22 lista de compra: **Ø35 comprada y montada** (vía B, husillo). La pregunta 26.4 A/B ya no hace falta.
