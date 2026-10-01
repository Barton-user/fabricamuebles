# Sierra HP280 y AutoCUT

_Cómo se opera la sierra, y la tarea abierta de corregir el mapeo de AutoCUT (cantos cruzados y código de barras)._

_Movido tal cual desde `CONTEXTO.md` el 01/10/2026. Las referencias "§N" dentro del texto son a la numeración vieja de `CONTEXTO.md`: cada sección vieja dejó allí una línea 📦 que dice adónde fue. Si algo de acá contradice a `CONTEXTO.md`, manda `CONTEXTO.md`._

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
barras de AutoCUT.

> ✅ **Hecho el 01/10/2026.** La lista de corte trae ahora una **última columna `条码`** con el código
> solo (p. ej. `9992610010016`). Las demás columnas quedaron iguales, así que el perfil de mapeo
> actual sigue sirviendo. También lo hace la web de curvado. Ya regeneradas: Alacena Spar
> (`fusion/EXPORT_ALACENA_SPAR/salida/` y `PENDRIVE/4_ALACENA_SPAR/`) y COCINA-01.
>
> **Lo que queda en la PC de la sierra**, en "Coincidencia":
> 1. **`条码` → el campo de código de barras** de la etiqueta (hoy está tomando otra cosa y sale `P01`).
> 2. **`开料长` / `开料宽` → largo / ancho de corte**, sin que AutoCUT vuelva a restar cantos.
>    Si AutoCUT insiste en restar, mapear los cantos de modo que `前`/`后` caigan sobre el **largo**
>    y `左`/`右` sobre el **ancho** (hoy están cruzados).
> 3. **`订单号` → el campo "工程" (proyecto)** de la etiqueta.
> 4. Verificar con el techo de PRUEBA 1: tiene que salir **598 × 399** y el código largo, no `P01`.

### Consecuencia pendiente

Con el mapeo corregido hay que **volver a cortar las 7 piezas del gris** — las actuales están
fuera de medida y no sirven para armar PRUEBA 1.

### Qué hace falta para retomarla

- Estar en la **PC de la sierra** con AutoCUT abierto.
- Una captura de la pantalla de **"Coincidencia"** para ver qué campo de AutoCUT recibe cada
  columna nuestra.
- El archivo `etapa2/salida/PRUEBA1/lista_corte.csv` (o el `.xlsx`).

---
