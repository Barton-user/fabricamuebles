# FÁBRICA MUEBLES — Bitácora de sesiones

_Historia del proyecto en orden de fecha: cómo se llegó a cada cosa. **No se lee al arrancar una conversación**;
lo vigente está en `CONTEXTO.md`. Si algo de acá contradice a `CONTEXTO.md`, manda `CONTEXTO.md`._

_Creado el 01/10/2026 moviendo tal cual las secciones de sesión de `CONTEXTO.md` (sin reescribir)._

---

## 6. Estado actual
_(antes en `CONTEXTO.md`)_


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

## 10. Lo que FALTA (en orden)
_(antes en `CONTEXTO.md`)_


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
_(antes en `CONTEXTO.md`)_


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
_(antes en `CONTEXTO.md`)_


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

---

## 15.10 · Camino Fusion completo, probado como se va a usar (22/09/2026, noche)
_(antes en `CONTEXTO.md`)_


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

---

## 15. 23/09/2026 — Primera sesión en la SKH-612HS
_(antes en `CONTEXTO.md`)_


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
_(antes en `CONTEXTO.md`)_


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
_(antes en `CONTEXTO.md`)_


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

## 19. Mecha Ø35 para cazoletas — qué comprar (24/09/2026)
_(antes en `CONTEXTO.md`)_


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
_(antes en `CONTEXTO.md`)_


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
_(antes en `CONTEXTO.md`)_


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

## 21. COCINA MLV — control contra GuiGui y unión de los uñeros corregida (27/09/2026)
_(antes en `CONTEXTO.md`)_


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
_(antes en `CONTEXTO.md`)_


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

## Fresado — lo que quedaba abierto el 24/09 (después de calibrar el Z)
_(antes al final de §18 de `CONTEXTO.md`; resuelto en buena parte el 01/10, ver `docs/PERFORADORA_SKH612.md`)_


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

## 26. Respuestas de Huahua a las 12 preguntas (30/09/2026)
_(antes en `CONTEXTO.md`)_


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

## 29. ✅ CAZOLETAS RESUELTAS: la T184 ahora es la mecha Ø35 (01/10/2026)
_(antes en `CONTEXTO.md`)_


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

---

## 30/09–01/10/2026 — Respuestas de Huahua y reestructuración de la documentación

- **30/09**: llegaron las respuestas de Huahua a las 12 preguntas del 24/09 (están arriba, sección 26).
  Se frenó la compra de la Ø35 por dos respuestas contradictorias; el 01/10 se resolvió en la
  práctica: FUL Ø35 × 70 R montada en la T184 (sección 29).
- **01/10, decisiones de Pato**: tornillos de bisagra **Ø5 para siempre** (no se compra la Ø6);
  variador del husillo de arriba queda en **100 Hz**; la salida de pieza es **hacia adelante**;
  la bisagra 48/6 sigue sin medir con calibre; T186 y espejado sin controlar.
- **01/10, reestructuración**: `CONTEXTO.md` tenía 3.279 líneas, mezclaba estado, especificación
  e historia, y se contradecía (Ø35, bisagra 14,5 vs 6, la Ø20 que era mecha). Quedó así:
  `CONTEXTO.md` (207 líneas, sólo lo vigente + reglas), `docs/` por tema (movido tal cual) y esta
  bitácora. `docs/PERFORADORA_SKH612.md` se escribió de nuevo juntando todo lo de la máquina más
  el manual del fabricante (datos técnicos, mantenimiento completo, fallas, backup, ajuste de
  precisión, códigos M — **M64/M65 = placa de la fresa**, pista para la campana que no baja).
  Versión MindNode: `docs/PERFORADORA_SKH612.opml` (conversor `docs/md2opml.py`).
- Del manual salió que **hay dos husillos de fresado** (arriba y abajo) y probablemente **dos
  variadores**, y que el paquete de arriba tendría **12 verticales** (contamos 9).
- Git: todo commiteado; **push pendiente** (sin credenciales en la VM).

## 01/10/2026 (noche) — Lista de corte, bisagra en un solo lugar, hoja de taller y manual de armado

- **AutoCUT**: la lista de corte suma al final la columna `条码` con el código limpio (Python y web de
  curvado, test 6/6). Regeneradas Spar (+ pendrive) y COCINA-01. Falta mapearla en la PC de la sierra.
- **Bisagra 48/6**: medidas en `herrajes/medidas.json`; recetas y `PonerHerrajes` las leen;
  `ajustar_maquina.py --bisagra` corrige lo de GuiGui (con la Spar da lo mismo que las puertas
  corregidas a mano). Recetas regeneradas: sólo cambiaron tornillos (Spar 12; COCINA-01 108 Ø6→Ø5).
  Falta re-armar/exportar en Fusion.
- **Hoja de taller** nueva (`MAÑANA_EN_LA_MAQUINA.md` + `Hoja_taller.pdf`, también en el pendrive).
- **Manual de armado**: `etapa2/manual_armado.py`, desde la receta, sin Fusion. Probado en la Spar y
  en los 10 muebles de COCINA-01. Bug encontrado al hacerlo: las caras visibles se calculaban con el
  centro de la pieza sin desplazar → en la explotada algunas placas salían de canto.
- Propuesta la skill `cerrar-sesion-fabrica`.

