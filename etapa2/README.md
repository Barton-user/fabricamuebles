# Etapa 2 — generador de archivos de máquina

Primer ladrillo del reemplazo de GuiGui: **convertir el JSON de producción en los
`.ban` de la perforadora SKH-612HS**, sin pasar por el exportador de GuiGui.

Resuelve el problema abierto de `CONTEXTO.md` §6: GuiGui escribe `.ban` incompletos
(sólo `HoleH`), pero el `<ORDEN>-Mass production.json` tiene **toda** la geometría.

---

## Uso

```bash
cd etapa2
python3 json2ban.py "../referencia/PRUEBA_PRUEBA-1/BluenNC/PRUEBA-Mass production.json" -o salida/PRUEBA1_BAN
```

Opciones:

| Flag | Para qué |
|---|---|
| `--bom` | escribe con BOM UTF-8 (variante `BAN_SC`) |
| `--back-slot-from-front` | variante `BAN2`: ranura de cara B cotada desde la cara A |
| `--arc-step N` | paso de linealización de arcos en mm (default 1.12, igual que GuiGui) |
| `--edges-like-guigui` | no rotar los flags de canto en piezas rotadas (ver abajo) |
| `--source X` | valor del atributo `Source` del encabezado |

También acepta una **carpeta**: busca recursivamente todos los `*Mass production.json`.

Verificar contra archivos de referencia:

```bash
python3 validate_ban.py salida/MUESTRA_BAN ../referencia/试生产样品柜_主卧/BluenNC/Six-sided\ drill-试生产样品柜/BAN
```

Sin dependencias: sólo Python 3 estándar. Corre igual en la Mac y en la PC de la sierra.

---

## Estado de validación

Mueble de muestra de Bluen (试生产样品柜), **12 de 12 piezas idénticas** a los archivos
de referencia: mismas medidas, mismo material, mismos cantos, mismos agujeros verticales,
horizontales y ranuras, mismo contorno (incluida la pieza con arco de 90°).

El diff textual crudo de una pieza rectangular da **una sola línea distinta**: el
encabezado con la fecha y `Source`.

Verificación independiente sobre PRUEBA 1 (orden 260625-20): el recuento de agujeros
por pieza coincide pieza por pieza con la tabla de despiece de `CONTEXTO.md` §5, y el
inventario de herramientas sale:

| Tipo | Ø | Prof. | Cantidad |
|---|---|---|---|
| Vertical | 6 | 3 | 16 |
| Vertical | 10 | 11 | 20 |
| Vertical | 15 | 13,5 | 20 |
| Vertical | 35 | 13 | 4 |
| Horizontal | 8 | 33 | 20 |
| Fresa ranurar | 6 | 6 | **4** |
| Fresa ranurar | 9 | 9 | 1 |

### Dos correcciones a `CONTEXTO.md`

**§5, primera pieza de prueba (techo 400×600, código 9441838670057).** El documento dice
*"4 agujeros Ø10 prof 11 en X = 42 y 362, Y = 11 y 593"*. Esos números salen del campo
`center` del JSON, que está en el marco de la placa **nesteada** (+2 mm). El `.ban` usa
`ocenter`, el marco de la pieza terminada — validado 12/12 contra los archivos de Bluen.

> Los valores correctos para medir con calibre son **X = 40 y 360**, **Y = 9 y 591**.

**§5, tabla de herramientas.** Dice **5** ranuras de 6 mm. El conteo real sobre los
> archivos da 4 (techo, izquierda, derecha, Partition01) más 1 de 9 mm = 5 ranuras en
> total. Probablemente la tabla contó el total y lo anotó en la fila del Ø6.

---

## Cómo funciona la transformación de coordenadas

Derivada y verificada contra los archivos de Bluen. Es la parte que hay que entender
si algo sale espejado.

El JSON usa **Y hacia abajo** (`rect` trae `top: 0` / `bottom: height`) y guarda la
pieza en la orientación de diseño. El `.ban` usa **Y hacia arriba** y guarda la pieza
siempre en **retrato** (lado largo sobre Y).

```
si  oRect.width <= oRect.height      →   X = x           Y = H − y
si  oRect.width >  oRect.height      →   X = H − y       Y = W − x     (y se rota 90°)
```

Las dos tienen determinante −1 respecto de los números crudos del JSON, lo cual es
**correcto**: como el JSON es Y-abajo, el resultado neto es una rotación propia, no un
espejado. Ésa es exactamente la diferencia con la plantilla `自定义六面钻`, que rota la
pieza y reasigna mal las caras (R/L ↔ U/D) y produce muebles espejados.

Se usan los campos **`ocenter` / `opt1` / `opt2` / `realCurve`**, que están en el sistema
de la pieza terminada (`oRect`). Los campos `center` / `pt1` / `pt2` están en el sistema
de la placa nesteada y **no sirven** para el archivo de pieza.

Otras convenciones confirmadas contra la referencia:

- **Z siempre se mide desde la cara A.** Un agujero de cara B va de `Z = −espesor` hasta
  `Z = −(espesor − profundidad)`. Un agujero de cara A va de `0` a `−profundidad`.
- Las **ranuras de cara B** en el `.ban` base se cotan con `Z = −profundidad` (no desde
  la cara A). La variante `BAN2` las cota desde la cara A; para eso está el flag.
- Los agujeros de cara B **no** se espejan en X/Y: van en el mismo marco que la cara A.
- Código de canto lateral en el JSON (marco Y-abajo): `1` = x=0, `2` = y=H, `3` = x=W,
  `4` = y=0. El lector **no confía** en ese código: deduce el canto de la coordenada y
  usa el código sólo como respaldo.
- El `z` del agujero horizontal (altura dentro del espesor) vive en `center['y']`.
- El contorno se emite antihorario, arrancando por el vértice más cercano al origen.
  Los arcos vienen como `b` (ángulo incluido en grados) sobre el vértice de llegada.

---

## Cantos (`EdgeFBLR`) — validado, con una salvedad

Las 12 piezas del mueble de muestra tienen los cuatro cantos iguales, así que no servían
para validar el orden Front/Back/Left/Right. Se validó contra
`referencia/PRUEBA_PRUEBA-1/BluenNC/saw/开料清单.xls`, que trae las columnas
前/后/左/右封边 por código de barras:

- **Las 8 piezas no rotadas de PRUEBA 1 coinciden exactamente.** El mapeo es correcto.
- **Las 2 piezas rotadas (fascia boards, 564×100) no coinciden.** GuiGui rota las medidas
  de la pieza pero **no** rota los flags de canto. El generador, por defecto, sí los rota
  (es lo geométricamente correcto). Con `--edges-like-guigui` replica el comportamiento de
  GuiGui y las 10 piezas coinciden al 100 %.

Los archivos de `salida/PRUEBA1_BAN/` están generados **con `--edges-like-guigui`**, para
que sean idénticos a lo que habría producido GuiGui salvo por los agujeros que le faltan.

> ⚠️ Si la perforadora usa `EdgeFBLR` para compensar el espesor del canto, en una pieza
> rotada con cantos asimétricos las dos opciones dan posiciones distintas. Verificar con
> calibre la primera fascia board antes de producir en serie.

---

## Puntos a verificar antes de producir en serie
1. **Ranuras de canto (`sslots`)** y **fresados (`millInfo`, `curveHoles`)**: no hay
   ninguna muestra de referencia. El lector los pasa, pero sin validar.
2. **Agujeros de cara B**: validados en posición y profundidad, pero ninguna pieza de la
   muestra tiene además ranura de cara B con geometría asimétrica.
3. **`Grain` queda fijo en `2`.** Las 12 piezas tienen `texDir: normal`. Si aparece otro
   valor de `texDir`, hay que ver qué `Grain` corresponde.
4. **Regla de rotación**: se dedujo como "el lado largo va sobre Y". Es consistente con las
   12 piezas, pero podría depender en realidad de la veta. Si aparece una pieza con veta
   cruzada, revisar.
5. **Medida terminada vs. de corte.** El `.ban` lleva la medida **terminada** (173×350),
   no la de corte (171×348). Es lo que hace Bluen, así que se replica — pero significa que
   la perforadora espera la pieza ya con canto pegado, o que compensa. Confirmar con
   calibre en la primera pieza.

---

## Archivos

| Archivo | Qué es |
|---|---|
| `panel.py` | modelo interno de pieza (`Panel`, `Hole`, `SideHole`, `Slot`) + geometría |
| `guigui.py` | lector del `Mass production.json` → modelo |
| `ban.py` | escritor modelo → `.ban` |
| `json2ban.py` | CLI |
| `validate_ban.py` | diff semántico entre dos `.ban` (tolerancia, no texto) |
| `salida/PRUEBA1_BAN/` | los 10 `.ban` completos de PRUEBA 1 |
| `salida/MUESTRA_BAN/` | los 12 `.ban` del mueble de muestra (para comparar) |

`panel.py` es el **esquema propio** del que habla `CONTEXTO.md` §12. Los próximos
generadores (`.mpr`, `.xml` Plate, `.xml` KDT, el `.xls` de la sierra, las etiquetas QR)
se escriben contra ese mismo modelo, y el día que el origen sea Inventor o Fusion en vez
de GuiGui, sólo se reemplaza `guigui.py`.

---

# Los otros tres formatos

Además del `.ban`, el modelo `Panel` ahora emite los cuatro formatos que puede
leer una perforadora de seis caras. Todos validados contra la referencia de Bluen.

```bash
python3 exportar.py "<ORDEN>-Mass production.json" -o salida/
python3 validar.py mpr salida/MPR ../referencia/.../MPR
```

`exportar.py` reemplaza a `json2ban.py` (que sigue funcionando para el `.ban` solo).
`validar.py` reemplaza a `validate_ban.py` y cubre los cuatro formatos.

## Estado de validación

Mueble de muestra, **48 de 48 archivos iguales**: 12 BAN · 12 MPR (8 base + 4 K) ·
12 XML1 · 12 XML3. Los MPR y los XML3 salen **byte a byte idénticos**. Los XML1
coinciden en geometría; difieren sólo en el orden interno de elementos equivalentes
(GuiGui ordena los agujeros de canto distinto en cada formato, y arranca el contorno
en otro vértice). Los BAN difieren sólo en la línea de encabezado con la fecha.

## `.mpr` — WoodWOP / Homag

- Codificación **GBK**, saltos **CRLF**, sin salto final después de `!`.
- `<100 WerkStck>` lleva sólo el rectángulo envolvente: **el formato no representa
  contornos irregulares**. La pieza con arco de la muestra tampoco lo trae en la
  referencia de Bluen.
- Sólo van las operaciones de **cara A**. La cara B va en un segundo archivo
  `<código>K.mpr`, con la **X espejada** (`X' = LA − X`) y la profundidad real
  desde esa cara.
- `BM` del taladro horizontal: `XP` = x0 (izq) · `XM` = xLA (der) · `YP` = y0 (abajo) ·
  `YM` = yBR (arriba).
- Cantos en el encabezado: `[H\Left:…;Bottom:…;Right:…;Top:…` — nombres explícitos,
  más claros que el `EdgeFBLR` del `.ban`.
- **GuiGui no emite `.mpr` para piezas sin ningún mecanizado** (los fondos de 5 mm).
  El generador replica eso.

## `.xml` XML1 — formato "Plate"

- ⚠️ En la cabecera, `width` es el **alto** del panel y `depth` el **ancho**
  (invertidos respecto del `.ban`). Las coordenadas de agujeros y ranuras, no.
- `direction`: 1 vertical, 0 horizontal. `positionSide`: 1 cara A, 0 cara B.
- `drillDirection`: L=(1,0,0) · R=(−1,0,0) · D=(0,1,0) · U=(0,−1,0) ·
  cara A=(0,0,−1) · cara B=(0,0,1).
- Los agujeros de cara B **no** se espejan y llevan `point` con z = espesor.
- El contorno va como segmentos, en sentido inverso al del `.ban`, con los arcos
  ya linealizados: el formato no usa arcos.
- Las colecciones vacías se auto-cierran (`<Slottings/>`).

## `.xml` XML3 — formato KDT

El más simple: lista plana de operaciones, sin contorno.

| TypeNo | Operación |
|---|---|
| 1 | agujero vertical, cara frontal |
| **8** | **agujero vertical, cara trasera** |
| 2 | agujero horizontal — `Quadrant` 1 = x=L · 2 = x=0 · 3 = y=W · 4 = y=0 |
| 3 | ranura, cara frontal |
| 13 | ranura, cara trasera |

`TypeNo 8` y los cuadrantes 3 y 4 no estaban en `CONTEXTO.md` §4.4; salieron de
esta validación.

⚠️ `PanelLength` es el **ancho** y `PanelWidth` el **alto**.

---

# Entrada desde Fusion

`cargar.py` es ahora el punto de entrada único: detecta la fuente y delega.

| Archivo | Lector |
|---|---|
| `<ORDEN>-Mass production.json` | `guigui.py` |
| `piezas.json` | `fusion_json.py` |

`exportar.py`, `listacorte.py` y `hojas.py` aceptan cualquiera de los dos sin cambios
en la línea de comandos. Los generadores no saben de dónde salieron los paneles.

Los scripts de Fusion que producen el `piezas.json` están en `../fusion/`, con su
propio README y la convención de modelado.

**Probado**: un `piezas.json` con el techo de PRUEBA 1 genera un `.ban` idéntico al
que ya estaba validado contra Bluen. La mitad de abajo del camino nuevo está cerrada.
