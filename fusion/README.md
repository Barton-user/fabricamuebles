# Fusion → máquinas

Los dos scripts de Autodesk Fusion que sacan a GuiGui del circuito de diseño.

```
Fusion  ──(ExportarPiezas)──►  piezas.json  ──(etapa2/exportar.py)──┬─► .ban   perforadora
                                                                    ├─► .mpr
                                                                    ├─► XML1 / XML3
                                                                    ├─► lista_corte.csv → AutoCUT → sierra
                                                                    └─► hojas de verificación
```

> Se evaluó Inventor primero, por los iFeatures. Se descartó: el herraje en Fusion
> se escribe como código, que es el mismo proyecto que el extractor — una sola
> herramienta, en Python, y corriendo en la Mac. La API y los scripts están
> disponibles en Fusion, incluso en la licencia personal.

---

## Instalación

En Fusion: **Utilidades → Scripts y complementos → pestaña Scripts → el `+` verde →**
elegir la carpeta `ExportarPiezas`. Repetir con `MarcarPlaca`.

Quedan en la lista y se corren con **Ejecutar**. No hace falta copiar nada a mano ni
adivinar rutas.

---

## Los scripts

### `PruebaTecho`

Modela solo el techo de PRUEBA 1 y lo deja marcado: 400 × 600 × 18, cuatro Ø10
prof 11, ranura 6×6 en la cara A y ranura 9×9 en la cara B.

Existe para sacar el modelado de la ecuación: si después el export no da lo
esperado, el problema está en el extractor y no en cómo se modeló.

**Correrlo en un documento nuevo y vacío**, en milímetros.

### `MarcarPlaca`

Pone en la pieza los datos que **no se pueden deducir del sólido**: material,
textura, veta, espesor de canto por lado y a qué mueble pertenece.

**No hace falta seleccionar nada antes de correrlo.** Fusion borra la selección
al abrir el diálogo de Scripts, así que el script muestra la lista numerada de
las placas del diseño y pregunta cuáles marcar:

```
 1  9441838670057    600 x 400 x 18     多层实木 / 13玛雅灰
 2  9441838670064    741.8 x 400 x 18   多层实木 / 13玛雅灰
 ...
Cuáles marco?   todas   |   1,3,5   |   1-7   |   1-3,8
```

Después pide los datos en una línea:

```
multilaminado | 13 gris | VERTICAL | 1,1,1,0 | 00-Doble c/spar01
```

`MATERIAL | TEXTURA | VETA | cantos abajo,arriba,izq,der | MUEBLE`, cantos en
milímetros. `MUEBLE` es el módulo al que pertenece la pieza y sale en la etiqueta
de la lista de corte.

**Un `=` en cualquier campo deja lo que la pieza ya tenía.** Para cambiar sólo el
material sin pisar los cantos:

```
04 nogal | 04 nogal | = | = | =
```

También vale canto por canto: `1,=,=,0`.

Escribiendo **`MUEBLE`** en vez de los números, pide en cambio
`ORDEN | CLIENTE | DIRECCION | AMBIENTE` y lo guarda en el diseño.

La marca va en el **cuerpo**, no en el componente: es lo que hay que hacer cuando
varias placas viven en el mismo componente, porque marcando el componente
saldrían todas con el mismo material. `ExportarPiezas` lee primero el cuerpo y
después el componente, así que se puede marcar lo general en el componente y
pisar una pieza suelta marcando su cuerpo.

> ⚠️ **Marcá todas las placas, o ninguna.** Apenas hay una pieza marcada, las que
> no lo están se ignoran al exportar. `ExportarPiezas` avisa cuando pasa.

### `PonerHerrajes`

Busca **solo** las uniones del mueble y hace los agujeros de los herrajes en las
dos piezas de cada una.

Una unión es una placa que **apoya su canto contra la cara de otra**. El script
las encuentra comparando dónde quedó cada placa en el mueble, las lista y
pregunta cuáles herrajear:

```
 1  Estante          -> Lateral izq        400 mm de contacto
 2  Estante          -> Lateral der        400 mm de contacto
 3  Techo            -> Lateral izq        400 mm de contacto
 4  Techo            -> Lateral der        400 mm de contacto

Cuáles?   todas | 1,3 | 1-4   |   3EN1-33   |   3
```

Por cada conector hace los tres agujeros donde van:

- **Ø15 × 13,5** en la cara de la placa que apoya, a 33 mm del canto
- **Ø8** por el canto de esa misma placa, a media placa, hasta el centro del Ø15
- **Ø10** en la cara de la otra placa, justo donde sale el perno

Elige sola la cara correcta en cada pieza: en el lateral izquierdo los Ø10 salen
en la cara A y en el derecho en la B, porque son espejo.

#### Las medidas no son inventadas

Salen de medir los **72 conectores** de los archivos reales de Bluen. Y ahí
apareció algo que no sabíamos: **los dos pedidos usan herrajes distintos.**

| | `3EN1-33` (PRUEBA 1) | `3EN1-34` (muestra) |
|---|---|---|
| Ø15 cara, profundidad | 13,5 | 13,5 |
| Ø15 desde el canto | 33 | 33 |
| Ø8 canto, profundidad | **33** | **34** |
| Ø8 altura | 9 | 9 |
| Ø10 en la otra placa | **11** | **12** |

En los 72 el Ø15 va a 33 mm del canto con 13,5 de profundidad, y el Ø8 entra a
9 mm. Lo único que cambia es cuánto entran el perno y el receptor.

Eso destapó un error: `ExportarPiezas` tenía **33 fijo** en la tabla que corrige
la profundidad del Ø8 cuando desemboca en el Ø15. Con el herraje de 34 habría
escrito 33, un milímetro de menos, en silencio. Ahora `PonerHerrajes` deja el
dato en la pieza y el exportador lo lee de ahí; la tabla quedó sólo como último
recurso.

#### Bisagras

```
BISAGRAS | 4 | 1 | 2
```

El número de la puerta, el del lateral, y cuántas bisagras. Hace los agujeros en
**las dos piezas**:

- en la **puerta**: cazoleta **Ø35 × 13** a 22,5 mm del canto, y dos **Ø6 × 3** a
  37 mm del canto (14,5 más adentro) y ±24 mm a lo largo
- en el **lateral**: dos **Ø6 × 3** del herraje de la base, a **20 y 52 mm del
  canto de adelante**, a la altura de la bisagra

Todo eso también está medido sobre las 4 bisagras de PRUEBA 1. El lateral y la
cara correcta los deduce de dónde quedaron las piezas: en el lateral izquierdo la
base va en la cara A y en el derecho en la B.

La altura de cada bisagra sale de la puerta: 100 mm de cada punta, que es lo que
usa PRUEBA 1. La correspondencia con el lateral se calcula del ensamble, así que
si la puerta está levantada 5 mm, los agujeros del lateral salen 5 mm más arriba.

#### Un error que encontró la verificación

`agujero_cara` agrupaba los agujeros por cara y los hacía todos con la
profundidad del más hondo. En una puerta con cazoleta de 13 y tornillos de 3, los
tornillos salían **de 13 mm**: el Ø6 habría pasado de largo. Ahora agrupa por cara
**y por profundidad**.

Lo encontró un chequeo automático que compara lo que sale contra el patrón medido
en PRUEBA 1, no la lectura del código.

#### Cómo hay que modelar

Cada placa, **un componente**, con la placa **acostada** adentro (boceto en XY,
extruir en Z). Después se para y se ubica moviendo la ocurrencia. Es como modela
cualquiera un mueble, y es lo que ya pedía `ExportarPiezas`.

Si las placas están sueltas o acostadas una al lado de la otra no hay uniones que
buscar, y el script lo dice en vez de no hacer nada.

### `ExportarPiezas`

Recorre el diseño, reconoce las placas y escribe `piezas.json` más un
`diagnostico.txt` en la carpeta que elijas.

---

## La convención

### 1 · El marco de coordenadas

El script toma la **caja envolvente del cuerpo** y arma el marco solo:

- el **espesor** es la dimensión menor, y tiene que estar sobre **Z**
- la **cara A** es la de Z mayor
- el origen queda en la esquina inferior izquierda

Eso es exactamente el marco del archivo de máquina, así que **no hay ninguna
conversión que pueda salir espejada**. Es la decisión que hace todo lo demás seguro.

Lo único que tenés que respetar: **la placa acostada, boceto en XY, extruir en Z.**
Dónde queda parada en el ensamble no importa — el script trabaja en el espacio del
componente, no del ensamble.

### 2 · Qué cuenta como placa

Un componente con **un cuerpo sólido de espesor constante**. Nada más.

El script lo reconoce solo. Si querés ser explícito, `MarcarPlaca` le pone
`TIPO = PLACA`; y para que ignore algo a propósito, ponele `TIPO = HERRAJE`.

### 3 · Agujeros y ranuras: no hay reglas

**El script lee el sólido, no el árbol de operaciones.** Busca caras cilíndricas y
caras planas intermedias:

| Lo que encuentra | Cómo lo interpreta |
|---|---|
| cilindro completo, eje en Z | agujero vertical — cara A o B según de dónde arranque |
| cilindro completo, eje en el plano | agujero de canto — el canto sale de dónde entra |
| cilindro **parcial** | redondeo del contorno, lo ignora |
| cara plana entre las dos caras | fondo de ranura |

Por eso **da lo mismo cómo modelaste el agujero**: con la herramienta Agujero, con
un corte extruido, con una revolución. Y no hay que nombrar ni etiquetar nada.

La profundidad, el diámetro y la posición salen de la geometría real, que es la que
va a tener la pieza.

### 4 · Herrajes

El vocabulario del mueble de placa es chico y sin ambigüedad:

| Herraje | Agujeros |
|---|---|
| Tres en uno — excéntrica | Ø15 prof 13,5 en la cara **+** Ø8 prof 33 entrando por el canto, que lo cruza |
| Tres en uno — espiga | Ø10 prof 11 en la cara de la placa de enfrente |
| Bisagra — cazoleta | Ø35 prof 13 |
| Bisagra — tornillos | 2 × Ø6 prof 3 |

Ningún par diámetro-profundidad se repite, así que el archivo de máquina no necesita
saber qué significa cada agujero: sólo dónde está.

**Cómo funciona el tres en uno**, según los datos reales: la excéntrica Ø15 y la
varilla Ø8 van en la **misma** placa — la varilla entra por el canto hasta cruzarse
con el Ø15. La placa de enfrente lleva sólo el Ø10.

> Lo que sigue pendiente es el **colocador** de herrajes: un comando que ponga los
> tres agujeros con un clic y que los siga cuando cambien las medidas. Es el paso
> siguiente y es código, no configuración.

### 5 · Los códigos de barras

No los escribís vos. Si una pieza va sin código, el generador le asigna uno de
**13 dígitos con verificador EAN-13** a partir del número de orden, y guarda el mapeo
en `codigos.json` al lado del `piezas.json` — así el mismo mueble da siempre los
mismos códigos.

### 6 · Lo que NO hay que hacer

- **No uses "Reflejar"** para hacer el lateral derecho a partir del izquierdo. Es la
  forma más rápida de terminar con un mueble espejado, y el archivo de máquina no
  tiene cómo darse cuenta.
- **No pongas el espesor sobre X o sobre Y.** El script te avisa y saltea la pieza.
- **No metas dos cuerpos sólidos** en un mismo componente.

---

## Estado — VALIDADO

**22/09/2026 — el camino Fusion → máquina está cerrado punta a punta, con las 10 piezas
de PRUEBA 1.**

`PruebaCompleta` modeló las 10 placas en Fusion, `ExportarPiezas` las leyó por B-Rep y
escribió `piezas.json`, y el generador produjo los cuatro formatos de máquina más la
lista de corte.

### Resultado del diff contra el oráculo

| formato | resultado |
|---|---|
| `.ban`  | 8/10 idénticas, 2 difieren **sólo** en el atributo `EdgeFBLR` |
| `.mpr`  | 9/11 idénticas, 2 difieren **sólo** en el bloque `[H\` |
| XML1    | 8/10 idénticas, 2 difieren **sólo** en `banding*` |
| XML3    | **10/10 idénticas** |
| lista de corte | 8/10 idénticas en las 19 columnas |

**Toda la geometría coincide en las 10 piezas de los cuatro formatos**: contornos,
agujeros verticales, agujeros de canto, ranuras, caras, profundidades. Las únicas
diferencias están en los datos declarativos que se listan abajo.

### Las tres diferencias que quedan, y por qué ninguna es un error del generador

**1. Los dos frentes (`…156` y `…163`) — marco de origen distinto, no medida distinta.**

En GuiGui esas dos piezas venían acostadas (564 × 100) y en Fusion están paradas
(100 × 564). GuiGui rota la geometría a retrato pero **no rota las banderas de canto**,
así que su `EdgeFBLR` termina apuntando a un borde de 100 mm. El nuestro apunta al de
564 mm, que es donde el canto está de verdad.

Las dos descripciones son la misma pieza física: en ambas el lado de 100 mm es el que
pierde 1 mm al pegar el canto (`开料` 99), y el canto va sobre un borde de 564 mm.
Cambia sólo cuál de los dos lados se llama 长 y cuál 宽.

**Hay que confirmar en la máquina si algo lee `EdgeFBLR` del `.ban`.** Si el pegado de
cantos se maneja desde la lista de corte —que es lo que parece—, la diferencia no tiene
efecto. Hasta confirmarlo, es el único punto abierto del camino Fusion.

**2. `板号` (número de placa) viene vacío.** Es el número de tablero del anidado, lo
asigna la optimizadora al nestear, no el diseñador. GuiGui lo traía porque ya había
anidado. Falta verificar que AutoCUT lo complete solo.

**3. ~~`材料` no coincide en 3 piezas.~~ RESUELTO 22/09/2026.** Se cargaron las texturas
por pieza (`04拉丝胡桃` en las puertas, `d02白麻面` en el fondo) y las 10 filas de la
columna `材料` coinciden ahora con la referencia.

### `MarcarPlaca` — validado, después de tres arreglos

Nunca había corrido. Al probarlo aparecieron tres problemas:

1. **Leía al revés lo que devuelve el cuadro de diálogo de Fusion** (`inputBox`
   devuelve `(texto, cancelado)`, no `(ok, texto)`). Reventaba siempre, con
   cualquier entrada. Ahora se detecta por tipo, así que no depende de la versión
   de la API.
2. **Marcaba componentes, no cuerpos.** Las 10 placas viven como cuerpos de un
   solo componente, así que las 10 habrían salido con el mismo material — justo
   lo que se quería arreglar. Ahora marca cuerpos.
3. **Dependía de la selección previa, y Fusion la borra** al abrir el diálogo de
   Scripts. Ahora el script muestra la lista numerada de placas y pregunta cuáles
   marcar; no hace falta seleccionar nada.

También se agregó `=` como "no tocar" en cualquier campo, porque si no, cargar el
material pisaba los cantos que ya estaban bien.

Probado con 21 casos contra un simulador de la API (rangos, listas sueltas,
cancelaciones, entradas inválidas, ambos órdenes posibles de `inputBox`) y después
contra el diseño real de las 10 piezas.

### Corregido en esta vuelta

- **`长` / `宽` ahora siguen la veta.** `竖纹` → 长 es la dimensión en Y; `横纹` → 长 es
  la dimensión en X. Las cuatro columnas de canto giran con el par. Antes `长` era
  siempre Y y la columna `纹路` era una constante que no miraba el dato de veta.
- **Profundidad de agujeros de canto.** Cuando el Ø8 desemboca en el Ø15, el B-Rep sólo
  ve 26,7 mm de cilindro. Se corrige con la tabla `PROFUNDIDAD_CANTO`, y **siempre se
  deja constancia en `diagnostico.txt`**.
- **Piezas duplicadas.** `PruebaCompleta` se niega a correr sobre un documento que ya
  tiene cuerpos, y `ExportarPiezas` aborta si hay dos códigos de barras iguales.

### Contorno irregular — VALIDADO contra un archivo real de Bluen (22/09/2026)

El extractor **no leía el contorno**: sólo tomaba el rectángulo del bounding box.
Una pieza con esquina cortada, redondeo o escotadura salía a la máquina como un
rectángulo liso, **sin ningún aviso**.

Ahora lee el borde de la cara, sigue las aristas en orden y saca cada vértice con
el ángulo del arco que llega a él.

**La validación**: en los archivos de referencia hay 5 piezas con contorno curvo.
Se tomó una — `6893155441217`, un lateral de 350 × 500 con redondeo R50, 8 agujeros
Ø10 y 2 ranuras —, se modeló de cero en Fusion y se comparó contra los archivos de
Bluen:

| formato | resultado |
|---|---|
| `.ban` | **idéntico** |
| `.mpr` | **idéntico** |
| XML1 | **idéntico** |
| XML3 | **idéntico** |

Sobre el contorno en sí: desvío máximo **0,014 mm** entre las dos polilíneas, y
174.463,34 mm² de área contra 174.463,32 de Bluen — 0,02 mm² de diferencia.

### La trampa del contorno: hay que leer la SILUETA, no una cara

El primer intento leía el borde de la cara A. Funcionaba en las piezas de prueba y
**rompía tres de las diez ya validadas**. Una ranura que llega hasta el borde le
abre un golfo al contorno de esa cara; si la cruza entera, se lo parte en dos. En
`9441838670132` el lado bueno medía 369,5 de los 400 mm: la placa habría salido
**30 mm más angosta**, y los archivos se ven perfectamente normales.

Se corrigió leyendo **las dos caras** y quedándose con la de mayor área, que es la
que no está comida por la ranura. Además hay una red de seguridad: si el contorno
elegido no ocupa todo el bounding box, no se exporta y queda escrito en
`diagnostico.txt`:

```
!! CONTORNO SOSPECHOSO: ocupa x 30.5..400.0  y 0.0..564.0
   pero la pieza mide 400.0 x 564.0. No se exporta el contorno.
```

Si la pieza es un rectángulo liso no se emite contorno, así que las 10 piezas ya
validadas salen exactamente igual que antes.

### Ranuras de canto — se detectan, pero NO se exportan

Un canal de 6 mm en el canto se leía como **dos ranuras de 12 mm, una en cada
cara**: la máquina habría fresado las dos caras de la placa. Ahora se empareja el
piso con el techo del canal y se reconoce bien.

**Pero no se escribe al archivo.** En los 82 `.ban` de referencia el vocabulario
completo es `Plane, Outline, Point, HoleV, HoleH, SlotL` — no hay ni un solo
ejemplo de ranura de canto. El elemento de máquina es desconocido, e inventarlo es
mandar un programa equivocado a la perforadora. El exportador se niega y lo dice:

```
!! 9000000000002 tiene RANURA DE CANTO — se omite
   canto L, 6.0 ancho x 12.0 prof
   El formato de maquina para ranuras de canto todavia no esta verificado.
```

**Pregunta para HUAHUA:** cómo se declara una ranura de canto en el `.ban`.

### Lo que sigue sin probarse


- ~~contorno irregular~~ — **validado contra un archivo real de Bluen**, 4/4 formatos
- ~~ranuras de canto~~ — se detectan bien; falta que HUAHUA diga cómo se escriben
- ~~`MarcarPlaca`~~ — **validado 22/09/2026**: 10 piezas marcadas, materiales y texturas
  correctos en la lista de corte. Ver abajo.
- la dirección de veta de los dos frentes, **en AutoCUT**
- medida terminada vs. medida de corte, **con calibre sobre la pieza real**
