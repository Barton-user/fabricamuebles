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

## 20/10/2026 — La HP280 corta 1–2 mm de más: cómo diagnosticarlo y qué hacer mientras tanto

**Síntoma**: piezas de 299 salen 300/301 → en la perforadora salta `202h AEje` (el carro A aprieta al ancho
programado). Lo vimos el 06–07/10 (Spar: 399 → 400/401) y el 20/10 (cajón del Bandejero).

**Prueba para saber de dónde viene el error** (10 minutos, un retazo largo):
1. Cortar en `editar` una secuencia **200 · 200 · 200 · 200** de una misma tira, con `Trim` como esté.
2. Medir cada pieza con calibre en los dos extremos (también dice si el corte sale a escuadra).
3. Medir el espesor real de la hoja: cortar 10 mm adentro de un retazo sin pasar y medir la ranura (kerf).
   La máquina tiene `Saw = 4,4`.

| Resultado | Causa | Corrección |
|---|---|---|
| Todas iguales y todas +1 (o +2) | **offset del origen del empujador** (cero de la regla) | parámetro de compensación/origen del empujador (menú `parámetro`, con contraseña) o, si no, restar ese valor fijo en AutoCUT/`editar` |
| La 1ª bien y después crecen (+1, +2, +3…) | **kerf mal cargado** (`Saw` ≠ espesor real de la hoja) | poner en `Saw` el kerf medido |
| Un extremo distinto del otro | la pieza no está a escuadra: alineador lateral / tope / puente del empujador torcido | escuadrar (ver E13/E06 arriba) y revisar la presión del prensor lateral |
| La primera pieza de la tira distinta de las demás | `Trim` (5) mal interpretado o el refilado no se hizo | mirar si la primera pieza incluye el refilado |

**El menú `parámetro` pide contraseña que no tenemos** → pedirla a la Sra. Tan (Huahua) junto con el nombre
exacto del campo de compensación. Mientras tanto hay dos salidas que ya funcionaron:

- **Descontar el error fijo al cortar**: si la sierra siempre da +1, pedirle 298 para obtener 299. En AutoCUT
  o en `editar`. Es lo más simple si la prueba de arriba da error constante.
- **Perforar a la medida real** (`etapa2/a_medida_real.py`): medir la pieza con calibre y regenerar el programa
  con esa medida; el sobrante queda en el borde del canto y los mecanizados quedan referidos al borde opuesto.
  Sirve para el **ancho** (la medida que mide el carro A). ⚠️ **No sirve para el largo que lleva pernos de
  3 en 1 en los extremos** (frentes y fondos de cajón, estantes entre laterales): ahí la excéntrica tiene
  que quedar a 34 del canto, así que ese sobrante se recorta en la sierra.

```
python3 etapa2/a_medida_real.py piezas_maquina.json -o piezas_real.json --pieza CODIGO=ANCHOxALTO [--pieza ...]
python3 etapa2/exportar.py piezas_real.json -o salida_real/
```

## Impresora de etiquetas (PC de la sierra) — configuración que anda (22/10/2026)

La AIBAO BC-80152T se instala en Windows como **TSC TTP-245C** con driver Seagull (BarTender) v7.x, firmware V2.4F.

- **Idioma del driver**: venía en chino porque toma el formato regional de Windows. Se cambia en *Propiedades de impresora*
  (no Preferencias) → Herramientas → Opciones de controlador → Opciones regionales → Idioma: Español, Unidad: mm.
  Ojo: en Región de Windows **no tocar "Administrativo / idioma para programas no Unicode"**: AutoCUT y HHcnc lo necesitan en chino.
- **Papel**: Preferencias de impresión → Preparar página → Material → Nuevo: `60x40`, ancho 60, alto 40 (los 1,3 mm de
  soporte expuesto quedan). Orientación Vertical.
- **Material**: Método **Térmica directa**, Tipo **Etiquetas con espacios**, altura del espacio **3 mm**, post-impresión Rasgar.
  Con "Usar valor de impresora actual" la impresora quedaba en gap 0 (continuo) y arrancaba en cualquier lado.
- **Calibrar el sensor de gap**: FEED apretado al encender y soltar cuando el LED parpadea **rojo** (primer estado). Ámbar
  = autotest y deja la impresora en modo dump (apagar y prender para salir); verde = reset de fábrica (evitar).
  El USB es sólo de ida: "Consulta" del driver se queda en "Solicitando información" (no es un error).
- **Imprimir**: `etiquetas_60x40.pdf` (una etiqueta por página) desde el visor del navegador, disposición Vertical, papel
  60x40, escala 100 %. Probado con `PENDRIVE/12_COCINA_MLV/etiquetas/PRUEBA_IMPRESORA_1_etiqueta.pdf`: sale entera y nítida
  (2 mm más de margen arriba; si molesta, Material → desplazamiento vertical −2 mm).

### Estado al 22/10 (noche): el sensor de gap no anda — diagnóstico y plan

**Hechos:**
- Las etiquetas del rollo miden **60 × 39**, gap ~3, paso **42,2** (medido: 20 etiquetas = 841 mm). No 60 × 40.
- La impresora **nunca calibra el gap**: `GAPDETECT`, `GAPDETECT 320,24`, `BLINEDETECT` y la calibración por botón
  (FEED al encender, soltar en rojo = calibración + autotest + dump en este firmware; el LED nunca pasa por ámbar)
  dejan todo igual: autotest con `GAP DAC LEVEL: 0, 3` y comportamiento de papel continuo (avanza SIZE fijo).
- Con GAP 3 y SIZE 40 se atrasaba ~2-3 mm por etiqueta; con BLINE se adelantaba ~1: avanza una longitud fija,
  no ve ninguna marca.
- **Sensores encontrados:** (1) carrito con ventanita sobre una cremallera dentada, en el centro del recorrido:
  es el de **marca negra**, ajustable (se movió bajo la etiqueta, no cambió nada). (2) Par fijo a la **izquierda**:
  LED en la tapa (sale **violeta** en la foto = IR encendido) + lente al lado de un tornillo en la base. Es el
  **sensor de gap** (transmisivo). **El papel de 60 pasa a la derecha de ese par**: el sensor ve luz siempre,
  "gap permanente", calibración imposible. La BC-80152T está pensada para rollo de 80 mm centrado.
- El driver Seagull no manda comandos sueltos ("Enviar comando" no hace nada, "Consulta" se cuelga: USB de ida).
  Lo que sí anda: compartir la impresora (`rundll32 printui.dll,PrintUIEntry /Xs /n "TSC TTP-245C" attributes +Shared sharename TSC`)
  y `copy /b archivo.txt \\localhost\TSC`. Archivos de prueba en `C:\tsc\` de la PC de la sierra
  (`test.txt` = `SELFTEST`, `p3.txt` = 3 etiquetas PRUEBA en modo GAP).
- `BACKFEED` es impreciso y limitado (~20 mm): no usarlo. `FEED` es exacto.

**Pendiente (mañana):**
1. Medir desde la pared izquierda del recorrido: distancia a la lente del sensor y al borde izquierdo de la tira.
2. Si la lente queda fuera del papel: abrir las guías del porta-rollo y de la base, correr el rollo contra la
   izquierda (tapar la lente con ≥ 5 mm de margen), calibrar por botón (soltar en rojo), apagar/prender,
   `copy /b C:\tsc\p3.txt \\localhost\TSC`: las 3 PRUEBA tienen que salir iguales. Si sí, driver con
   Tipo = etiquetas con espacios 3 mm y listo.
3. Si el rollo no se puede correr: comprar rollo de **80 mm de ancho** (60 × 40 sobre soporte de 80, o 80 × 40),
   o reclamar/cambiar la impresora. Mientras tanto, modo continuo (abajo).

**Parche que funciona (modo continuo, sin sensor): `etapa2/etiquetas_tspl.py`**
`python3 etiquetas_tspl.py maestra.json -o carpeta --orden 260625-20 --cliente MALVINAS --paso 42.8 --alto 39 --cabezal 16.4`
- `--paso` es lo que hay que PEDIR para que avance el paso real: con este rollo pidiendo 42 avanzaba 41,4
  (medido: 10 etiquetas impresas = 414 mm) → 42 × 42,2 / 41,4 = **42,8**. Con 42,8, 5 reglas seguidas salen iguales.
- `--cabezal` ajusta la fase (avance inicial = paso − cabezal − gap): se calibra con `00_PRUEBA5.txt` (5 reglas)
  alineando a mano el gap en la cuchilla antes de mandar. Último valor probado: 16.4 (v8, `PENDRIVE/12_COCINA_MLV/etiquetas_tspl_v8/`).
- En 125 seguidas (`TODAS.txt`) se acumula desfase (décimas por etiqueta): **imprimir por mueble** (13 archivos,
  máx. 24 etiquetas) realineando el gap en la cuchilla antes de cada archivo. No cortar entre tandas sin realinear:
  al cortar en la cuchilla el papel se mueve ~5 mm.
- Para afinar el paso con precisión: en una tira larga impresa medir 40 pasos impresos y 40 pasos de etiqueta;
  paso_nuevo = paso_pedido × (etiqueta / impreso).
