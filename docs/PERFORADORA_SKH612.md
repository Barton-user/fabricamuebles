# Perforadora SKH-612HS — operación, herramientas y alarmas

_Vigente al 01/10/2026. Juntado de la bitácora (sesiones 23/09 y 24/09), las respuestas de Huahua
(30/09), la prueba de la Ø35 (01/10) y el manual del fabricante (citado como "manual, cap. N"). Cuando algo cambie, **se corrige acá** (no se agrega abajo);
el relato de cómo se llegó va a `BITACORA.md`._

**Fabricante**: Guangdong Shunde Changsheng Machinery (昶盛机械), marca **Huahua CNC**.
Manual: `User Manual_SKH-612 Series_260706_115944.pdf` (raíz del proyecto). Las capturas de
pantalla con explicación están en `instructivo/` (`INDICE.md`).

---

## 1. La PC y el software

- En la PC industrial hay dos programas: **CncMon32** (el CNC Syntec) y **PgDrillCam32**, cuyo
  título real es **`桦桦数控钻 MH2026_Drill 3.0.5.0`**. Al que en documentos viejos se le dice
  "HHcnc" es este MH2026.
- Idioma: botones Inglés / Chino / Español en "Personalización automática". **La traducción al
  español es engañosa** (ver §5).
- Los cinco botones de arriba (Manual / Automático / Parámetro / Configuración / Mantenimiento)
  **son menús, no modos**. El rojo permanente de "Mantenimiento" es el aviso de mantenimiento
  vencido.
- **Login**: abajo a la derecha dice "El usuario no ha iniciado sesión". Clave **`520`**
  (confirmada); usuario probable **`Admin`** (sin confirmar). No hace falta loguearse para
  mecanizar.
- ⚠️ **El reloj de la PC está adelantado ~13 h**: los horarios de "Alertas históricas" no sirven
  para saber en qué orden pasaron las cosas.

## 2. Datos técnicos (manual, cap. 4 — columna SKH612H)

| Qué | Valor |
|---|---|
| Placa — largo | **250 a 5000 mm** |
| Placa — ancho | **50 a 1200 mm** |
| Placa — espesor | **10 a 48 mm** |
| Pieza "normal" más chica (línea de seis caras) | 120 × 300 mm |
| Paquete de taladros de **arriba** | **12 verticales** (ver §6.2: contamos 9) + **8 horizontales** |
| Paquete de taladros de **abajo** | **9 verticales** |
| Motor de los paquetes | 2,2 kW · **2800 rpm** |
| Husillos de fresado | **dos (arriba y abajo)** · 3,5 kW c/u · pinza **ER25** · 18000 rpm |
| Recorridos | X/U 5800 mm (130 m/min) · Y 1680 (80) · Z 90 (30) · V 1200 (80) · W 100 (30) · A 1260 (30) |
| Aire | **0,7 a 0,8 MPa** (con menos de 0,7 no arrancar) |
| Eléctrico | 380 V / 50 Hz · 19,2 kW |
| Mesa | 960 mm de alto |
| Peso / medidas | 3500 kg · 6500 × 2840 × 2200 mm |

**Ejes** (manual, cap. 5): X / U = manipuladores (las dos pinzas) · Y, Z = cabezal de arriba ·
V, W = cabezal de abajo · A = componente de apoyo lateral (empuja de costado y mide el ancho).

**Seguridad**: las puertas izquierda, derecha y la guarda del frente tienen **sensor**: si se
abren con la máquina andando, se para. Paro de emergencia: se suelta girando ~45° a la derecha.

## 3. Encendido

**Antes de prender** (manual 7.1): aceitador automático con aceite · aire seco y **> 0,7 MPa** ·
mechas afiladas y firmes · el lote de piezas coincide con la orden.


1. Equipo y vacío → **COMPUTER START** → esperar que la PC arranque del todo.
2. **POWER** → esperar ~1 minuto.
3. Abrir **CncMon32** → estado "ready", sin alarma titilando → minimizar.
4. Abrir **MH2026** (PgDrillCam32).
5. **Programa de calentamiento** (manual 16.10): MH2026 → "Configuración de máquina" →
   "Programa de calentamiento". Dura ~1 minuto. Al terminar, verificar que todas las mechas
   volvieron arriba.

**Apagado** (manual 8.4), en este orden: cerrar **MH2026** → cerrar **CncMon32** → apagar la PC
normalmente → POWER OFF → recién ahí la llave general. **Entre apagado y encendido, más de 1
minuto.** Un corte de luz con la PC prendida puede dañar el sistema.

**Al terminar el día** (manual 7.4 y 11.5): limpiar viruta y polvo adentro y afuera (después de
fresar, sí o sí), y anotar en el registro de la máquina cualquier problema.


## 4. Cargar un programa y mecanizar

1. "Tipos completados" → ícono de carpeta → **"Cargar archivo"**.
2. **Formato = `KDTXml`** (nuestra carpeta `XML3/`). ⚠️ El desplegable arranca en
   "Nueva generaciónXml" y con ese **no lista nada y no da error**. Hay que cambiarlo cada vez.
   Alternativa válida: `Haomai MPR` (carpeta `MPR/`). **No existe `.ban`**: la carpeta `BAN/`
   no sirve para esta máquina.
3. **Doble clic en la fila** → dibuja la pieza y llena la tabla de operaciones.
4. **Mirar el cartel de rotación y la flecha** (`CCW Rotate 270°`, `90°`…): dicen cómo cargar la
   placa. Cada pieza trae la suya — **no cargar de memoria**. Las coordenadas de la tabla ya
   vienen rotadas.
5. **Leer la tabla fila por fila** (cara, coordenada, profundidad, diámetro) contra el plano.
   > **Regla de oro: que no haya error NO significa que esté bien.**
6. Si hay filas en rojo, la columna **"Motivo no procesado"** dice por qué. Se puede destildar
   "Habilitar" en las que no se quieran hacer.
7. **Generar** → la cola pasa a "Procesamiento asignado" (azul). La segunda columna
   "Herramienta" es la que asigna el post y **no cambia hasta apretar Generar**.
8. **Botón verde, 1ª vez**: las pinzas vienen al frente y la máquina espera la pieza.
   Apoyar la placa contra el tope, del lado de las pinzas.
9. **Botón verde, 2ª vez**: las pinzas cierran y mecaniza.

**Trampas conocidas**

- **El `.scx` guarda las ediciones**: si se editó una operación, re-importar el mismo XML
  devuelve la versión editada. Para volver al original, **borrar primero la fila de "Tipos
  completados"**. (Así salieron una vez dos agujeros pasantes de Ø20 en una puerta, con la
  tabla toda en verde.)
- **"Escanear código"** define qué pieza sale; si queda el código viejo, sale la pieza vieja. La
  cola procesa en orden: borrar con "Eliminación" lo que no se quiera.
- **Probar en un recorte más chico**: destildar las operaciones cuyas coordenadas caen fuera.
- **"Bloque individual"** en rojo arriba = modo paso a paso.
- Los marcadores grises y el círculo rosa/rojo fuera del contorno del dibujo **no son
  mecanizados** (probablemente pinzas y esquina de referencia).
- La puerta no tiene orientación equivocada posible: girada 180° pasa a ser la otra puerta.
- **Si un ciclo se interrumpe, la cola se vacía sola.** Hay que volver a mandar el trabajo.
- El diálogo de **Ranura no tiene campo de posición**: se mueve arrastrando en el dibujo o con
  "Desplazamiento". El de **Vertical** sí (Posición, Pasante, Múltiple, "Asignar nú").
- **Importar no es abrir**: si el editor sigue mostrando la pieza anterior, falta el doble clic.
- El menú **Configuración pide login**.

**Cómo se apoya la placa**: las dos **pinzas neumáticas** están del lado opuesto al operador y
**ése es el lado de referencia**: el canto largo va contra las pinzas, apoyado contra el tope.
Placas chicas: **empujarlas con un palo o una herramienta, nunca con la mano** (manual 7.2).

### Escaneo continuo — el modo de producción (manual 16.12)

1. "Configuración de máquina" → tildar **"Escanear varias placas antes del procesamiento
   automático"**.
2. Importar la orden → modo escaneo → escanear las etiquetas (se pueden cargar dos adelantadas).
3. Verde 1ª vez → poner la placa → verde 2ª vez. Al sacarla, a 1 segundo arranca sola con la
   siguiente escaneada.
4. Para saltear la placa en curso: "Reinicio del sistema". Si hay una falla: **vaciar la lista
   primero** y después resolver la falla.

Necesita que las etiquetas traigan **el código real** (hoy AutoCUT imprime `P01`, ver
`docs/SIERRA_AUTOCUT.md`). Acepta etiquetas "5+1" (un código para cinco caras y otro para la sexta).


## 5. Botonera "Personalización automática" — qué es cada botón de verdad

| En pantalla (español) | Chino | Qué hace |
|---|---|---|
| **"Descarg"** | 前出料 | **salida hacia ADELANTE** — la pieza vuelve al operador. **Es la que se usa** (confirmado 01/10). |
| **"Después"** | 后出料 | salida hacia atrás |
| **"todo despejado"** | 解除板宽板长警报 | **borra la alarma de medida de placa** (MLC 148) |
| "Detección de longitud" / "de ancho" | 板长检测 / 板宽检测 | verificación de medida (mejor no apagarlas; usar "todo despejado") |
| "Encender el ventilador" | 曲用风机 | ventilador |
| "Apantallamiento lateral" | 屏幕演示 | demo en pantalla |

## 6. Herramientas

### 6.1 La tabla de herramientas y cómo se edita

**Parámetro → "Configuración de paquete de…" → "Herramientas de corte generales".** A la
izquierda, el diagrama "bolsa de taladro 1 / 2" con la disposición física.

Para editar: **cliquear el ícono de la herramienta en el diagrama → clave `520` → editar en
"Configuraciones de uso común" → "almacenar herramientas"**. La celda de la tabla es de sólo
lectura. **Después de cualquier cambio, volver a Generar** (el código se arma con el valor viejo).

La tabla **no tiene columna de giro**. El giro de una mecha se lee por el color:
**naranja = izquierda · negro = derecha**.

### 6.2 Paquete de taladros de arriba (cara frente, `Z positivo`)

Grilla 3 × 3, paso 32 mm, las nueve posiciones ocupadas:

| Pos. | Ø | X | Y |
|---|---|---|---|
| 1 | 10 | 0 | 0 |
| 2 | 20 | −32 | 0 |
| 3 | 5 | −64 | 0 |
| 4 | 8 | 0 | −32 |
| 5 | 15 | −32 | −32 |
| 6 | 12 | −64 | −32 |
| 7 | 10 | 0 | −64 |
| 8 | 8 | −32 | −64 |
| 9 | 10 | −64 | −64 |

El paquete de abajo (cara dorso, `Z negativo`) son las filas 51 en adelante. Horizontales: Ø8
(los horizontales se numeran 17±, 18±, 19±, 20± en el manual).
⚠️ Filas 15–27 de la tabla nunca se capturaron. **El manual dice 12 verticales arriba y nosotros
contamos 9**: las 3 que faltan pueden estar en esas filas. Capturarlas.

**Herramientas de referencia** (manual 18.1): **T1** es la de referencia del paquete de arriba y
**T21** la del de abajo. Todas las demás se miden contra ellas.

### 6.3 Husillo de fresado y revista de conos

Revista lineal de conos, puestos rotulados `1号…8号`. **`T18n` = puesto `n`.** Pinza **ER25**.

**Hay dos husillos de fresado** (manual cap. 4 y 6): el de **arriba** (cara frente) toma los conos
de esta revista; el de **abajo** (cara dorso) es el que hace las ranuras de cara dorso — la
**T11** sería ése (manual 18.3.2 lo llama "tool magazine W1"). Por eso abajo sólo hay Ø10.

| T | Qué hay | Tabla (Ø / ancho / Z) | Uso |
|---|---|---|---|
| **184** (puesto 4) | **Mecha FUL Ø35 × 70 R** (MBD3570, widia, mango Ø10), salida 46 | **34,8 / 34,8 / Z 27** · avances **5000/500/250** | **cazoletas** — fija para esto |
| 187 (puesto 7) | Ø6 de ranurar | 6 / 6 | ranuras de fondo cara frente. ⚠️ **revisar si es fresa o mecha** (§14) |
| 11 | Ø10 | 10 / 10 | ranuras de cara dorso (mínimo de esa cara: **10**) |
| 183 | disco `62211-4T` Ø45 × 3 | 43,9 / 3 | ranura de 3 de costado; no se hunde |
| 185 (puesto 5) | Ø3,2 | 3,2 | — |
| 186 (puesto 6) | tabla dice "sin cargar" (Ø24); se vio un cono montado | — | **mirar qué hay** (§14) |
| 188 (puesto 8) | Ø10, dibujada como horizontal | — | no se puede hundir en la cara |
| 181 / 182 | sierra lateral Ø100 / Lamello | — | — |
| **190** | Ø0 — Huahua la llamó "同动刀" | — | **no tocar** hasta saber qué es |

**Por qué la T184 está en 34,8 y no en 35**: MH2026 trata a la T184 como fresa y planifica la
cazoleta como fresado circular. Con 35/35 el radio del círculo da 0 y tira
`ArgumentOutOfRangeException`. Con 34,8 el círculo es de 0,1 mm: baja derecho.

⚠️ **La "fresa espiral Ø20x70R" que estaba antes en la T184 es una mecha** (punta de centrado +
espuelas), no corta de costado. **No volver a usarla para fresar**: sobrecarga el servo.
Si algún día hace falta fresar de verdad, comprar una **fresa espiral de punta plana**.

### 6.4 Qué herramienta hace cada operación de nuestros archivos

| Operación | Herramienta | Nota |
|---|---|---|
| Vertical Ø5 | T162 | **también los tornillos de bisagra: Ø5 para siempre** |
| Vertical Ø6 | — | **no existe: el software crashea** (`ArgumentOutOfRangeException`). Pasar a Ø5 (`etapa2/ajustar_maquina.py --o6-a-o5`) |
| Vertical Ø3 (corredera) | — | no existe en la máquina; se hace a mano |
| Vertical Ø10 | T56 / T158 | |
| Vertical Ø15 | paquete | |
| Cazoleta Ø35 | **T184** | variador en **100 Hz** |
| Horizontal Ø8 | paquete horizontal | |
| Ranura 6 cara frente | T187 | variador en **300 Hz** |
| Ranura cara dorso | T11 | **ancho mínimo 10** (no hay herramienta más chica para esa cara) |
| Ranura de canto | — | el formato no está resuelto (¿"SlotH"?) |

### 6.5 Qué se puede hacer de cada cara

| | Cara de **arriba** (frente, `Z+`) | Cara de **abajo** (dorso, `Z−`) |
|---|---|---|
| Verticales | 9 (12 según manual) — Ø5 a Ø20 | 9 |
| Ranuras | T187 (Ø6) y más | **sólo T11 → ancho mínimo 10** |
| Cazoleta Ø35 | **T184** | **no** |
| Agujeros de Ø20 o más | sí | no |

Por eso `etapa2/ajustar_maquina.py` **da vuelta las piezas solo** (por defecto): pone arriba la
cara que tiene ranuras de menos de 10 o cazoletas/agujeros de Ø20 o más; si ninguna lo exige,
la que tiene más trabajo. Dar vuelta = espejar en X (x → ancho − x, cara A ↔ B, canto izq ↔ der).
Opciones: `--o6-a-o5` (Ø6 → Ø5), `--led10` (ranuras 9 × 9 → 10 × 10), `--sin-voltear`.

### 6.6 Variador del husillo de arriba (Delta MS300)

Está en el **gabinete eléctrico**. Se cambia con flecha ▲ + ENTER, **con el husillo parado**.

⚠️ El manual lista **dos variadores** (husillo de arriba y de abajo, con alarmas separadas). Si la
T11 es el husillo de abajo, **el MS300 que se bajó a 100 Hz no la afecta** — confirmar mirando
si hay un segundo variador en el gabinete.

| Para | Frecuencia | rpm |
|---|---|---|
| **Cazoletas (T184, Ø35)** | **100 Hz** | ≈ 6000 |
| **Ranuras (T187, T11)** | **300 Hz** | ≈ 18000 |

**Hoy quedó en 100 Hz.** Antes de ranurar, subirlo a 300; antes de hacer cazoletas, bajarlo
a 100. Desde la PC todavía no se puede: la tabla "Convertidor de frecuencia" (Parámetro →
Config. de paquete) existe pero está vacía; falta que Huahua diga cómo se configura con el MS300.

### 6.7 Calibración de profundidad (desplazamiento Z)

- Se calibra con el **desplazamiento Z de cada herramienta** en la tabla. No hay pantalla de
  medición de herramienta (confirmado por Huahua).
- ⚠️ **El signo es al revés de lo que dice el manual (11.3): MENOS valor = MÁS profundo.**
- **Acercarse siempre desde arriba** (Z alto = poco profundo). Errarle para poco profundo no
  rompe nada; para profundo clava la fresa (con Z = −11,3 atravesó 36 mm y hubo que usar el
  paro de emergencia).
- Fórmula: **`Z nuevo = Z actual − (profundidad pedida − profundidad medida)`**.
- Prueba que sirve: **tres cazoletas de profundidades distintas en la misma corrida** (p. ej.
  4 / 8 / 12), lejos de las pinzas. Si salen separadas por la diferencia correcta, el programa
  manda y sólo hay un offset. Si se espera que atraviese, usar **dos placas y declarar 36**.
- Pista de que el Z está mal: **marca circular de 85–90 mm en la placa** (el frente del husillo
  apoyando) y canaletas entre agujeros (viaja enterrado al trasladarse).

### 6.8 Cambiar la herramienta de un cono

1. Manual → 612NS → **"Modo de cambio de herramienta"** en verde (si no, el botón no suelta).
2. Sosteniendo el cono, **botón verde físico del cabezal** (al lado del husillo, ~1 s) → suelta.
3. Cambiar la herramienta en la pinza. **Salida 46 mm** desde la cara de la tuerca hasta la
   punta. Regla de Huahua: con la placa prensora abajo, la punta **no tiene que pasar el borde
   de la placa**.
4. Volver a poner el cono (chavetas calzadas) → botón verde → lo chupa.
5. **Apagar el modo de cambio en MH2026 Y en CncMon32 ("Cambio de cuchillo")** — es un
   interruptor: se aprieta de nuevo para salir. Si queda prendido en uno: MLC 348.
6. Tabla de esa herramienta (diámetro, ancho, Z) → "almacenar herramientas" → Generar de nuevo.

**Si el husillo queda vacío pero CncMon32 muestra una herramienta** (p. ej. `T 187`): no se
puede poner en T0 por software. **Montar a mano el cono de esa herramienta** con el botón
verde. Apagar y prender no lo arregla.

### 6.9 Mechas del paquete

- Al cambiar una: prisionero bien trabado, mecha no gastada, **corregir el diámetro en la tabla**.
- **Prohibido poner una mecha de más de Ø10 en la posición 1.**
- **Todas las puntas en el mismo plano ±1 mm**: Manual → bajar todos los verticales a la vez →
  comprobar con calibre de profundidad o regla → la que no, aflojar prisionero y correrla.
  Hacerlo cada vez que se cambie una mecha.
- Velocidades del manual: Ø5/6/8 → 4500 · Ø10/12 → hasta 4000 · Ø15 → hasta 2200 ·
  Ø20 → hasta 1200 rpm. (Ojo: el mismo manual dice que el motor del paquete gira a **2800 rpm**;
  esa tabla parece ser de **avance**, no de giro. Sin confirmar.)
- **Cómo bajar mechas a mano** (manual 15.1.1 y 15.1.2): máquina en "ready" sin alarma →
  CncMon32 → botón **"M"** → modo **"Manual continuo"** → cliquear la parte a mover. O por
  **MDI**: `T1` baja la mecha 1, `T1T2T3` baja la 1, 2 y 3, `T00` sube todas. **Al terminar,
  Ctrl+Alt** para que todo vuelva a reposo.

## 7. Alarmas y mensajes

**Dónde se lee la causa: CncMon32 → botón `alarma` → "Alertas existentes".** El cartel de MH2026
es la consecuencia; el CNC muestra la causa, y se ve una alarma por vez.

| Alarma / mensaje | Qué es | Qué hacer |
|---|---|---|
| `coordinate 71` — "no se especifica el nombre principal del programa" | se apretó Iniciar sin las pinzas en posición de carga | verde una vez (pinzas al frente), cargar, verde otra vez |
| `MLC 148` — ancho/largo de placa demasiado pequeño (r49,3) | la placa medida no coincide con la del programa | **"todo despejado"** en Personalización automática (y revisar por qué no coincide) |
| `MLC 349` — prohibido mecanizar con el husillo no sujeto (R46.18) | husillo vacío con una herramienta registrada | montar a mano el cono registrado (§6.8) |
| `MLC 348` — modo de cambio de herramienta (R46.17) | quedó activo el modo de cambio | apagarlo en MH2026 **y** en CncMon32 |
| `MLC 142` — señal de sujeción del husillo anormal (r48,13) | el puesto de la revista que pide está vacío | cargar un cono en ese puesto |
| `MLC 129` — un cilindro no retornó | la placa prensora / campana quedó abajo | subirla; el reposo es arriba |
| `Drv_M3_SYNTEC 202h / 203h / 206h` (sobrecarga, par, over torque) | herramienta trabajando de costado sin poder (una mecha usada como fresa, o pasada muy profunda) | parar; revisar herramienta y profundidad |
| `System.ArgumentOutOfRangeException` (índice fuera del intervalo) | agujero sin herramienta (Ø6), o T184 con diámetro = agujero (35/35) | Ø6 → Ø5; T184 en 34,8 |
| "Diámetro de herramienta demasiado grande" | no hay herramienta tan chica para esa cara (ranura de 9 en dorso) | ranura de 10 |
| "No se puede usar la herramienta especificada" | se forzó una herramienta que no sirve (p. ej. T188 horizontal para cazoleta) | dejar que asigne el post |
| "Por favor seleccione la herramienta de edición" | se quiso editar la tabla sin cliquear el diagrama | cliquear el ícono primero |
| "Error en conversión" (cola en rojo) | consecuencia de una fila con error | mirar "Motivo no procesado" |

### Familias de alarmas del CNC (manual 16.5)

`OP` operación del sistema · `MOT` servo / ejes · `COR` programa · **`MLC` PLC (las de la
máquina)** · `SPD` husillo · `ROT` revista · `SRI` módulos · `AL-xxx` del drive del servo
(`1xx` drive, `2xx` motor, `3xx` encoder, `4xx` ajuste, `5xx` aplicación, `9xx` avisos).

| Alarma | Qué es | Qué hacer |
|---|---|---|
| `OP-023` "Corte de energía durante el procesamiento, revise los datos" | se cortó la luz mecanizando | reiniciar control y drive (dos veces), esperar 30 s y prender |
| `MOT-008` falta comando de posición / eje deshabilitado | un eje recibió un golpe de fuerza | < 60 % de la fuerza del motor: se va con **Reset**. > 60 %: el eje se deshabilita y hay que **reiniciar normal** |
| `MOT-011` comunicación con el drive anormal | cable flojo, ruido, tierra | revisar cables y puesta a tierra |
| `MOT-019` / `MOT-023` error de seguimiento | el eje no sigue al comando: algo traba el movimiento | revisar lubricación, cuerpos extraños, que no esté trabado |
| `ROT` desviación de posición muy grande | se cortó un posicionamiento de la revista (paro de emergencia o reinicio) | eliminar herramienta trabada (manual adelante/atrás) y reposicionar |
| `AL-101` sobrecarga del drive | motor trabado mecánicamente o carga excesiva | sacar la causa mecánica; bajar la carga |
| `AL-203` detección de par anormal | carga excesiva (lo vimos con la Ø20 fresando de costado) | igual que arriba |
| "Por favor contacte a posventa, cambiar la batería" | batería del control agotada | ver §8 |

## 8. Recuperación de fallas (manual cap. 15 y 16)

**La máquina se paró por una falla** (16.1), en este orden:
1. ¿Hubo choque? → Reset y revisar que la parte golpeada esté entera y en su lugar.
2. Sin choque → leer la alarma (CncMon32 → `alarma` → "Alertas existentes"; historial:
   **F5 → F1 → F2**).
3. El estado tiene que ser **"Ready"**. Si dice "Not Ready", resolver la alarma y reiniciar el
   sistema de abajo (el control).
4. Revisar **presión de aire**, **límites de recorrido** y torque.

**Paro de emergencia con ejes en movimiento** (16.3.1): sacar la placa → revisar que nada haya
chocado → reiniciar normal.

**Apagado incompleto / el software quedó colgado** (16.2): cerrar todos los programas (la PC no) →
**apagar la llave, esperar 1 minuto** → prenderla, esperar 1 minuto → abrir los programas.

**Después de un corte de luz** aparece el archivo `o010000` (16.11): CncMon32 → **F2** Edición
de programa → **F8** Gestión de archivos → doble clic en `o010000` → **F1** cargar y ejecutar.

**MH2026 muestra "Close Program" al abrir** (16.9): en la PC, `D:\DiskC-(versión)` → descomprimir
**`OpenCnc Shared`** en esa misma carpeta → "Sí a todo".

**CncMon32 no conecta con el control** (15.1.5–6): aparece la IP **192.168.2.10**. Apretar F6 (no
tocar otras teclas) y esperar a que el control termine de arrancar. Si sigue: **F5** Mantenimiento
→ **F2** Red → **F4** conexión → **F2** conectar IP → reiniciar CncMon32. Si falla, revisar el
cable de red.

**Batería del control** (15.1.7): **3 pilas AA de 1,5 V cada 3 a 6 meses**. Cambiarlas con la
máquina **prendida**: Ctrl+7 (origen) → paro de emergencia → mantener **Ctrl+Alt ~6 s** hasta que
se vaya la alarma → cambiar. Sacar foto de la polaridad antes de abrir.

### Backup de la máquina (manual 16.13)

En la PC industrial: **`D:\DiskC-(número de versión)`** → comprimir esa carpeta entera. Contiene la
comunicación y pantalla del control **y la tabla de herramientas de MH2026**. Hacerlo **antes de
tocar la tabla** y cada tanto. Es también lo que pidió Huahua para probar el crash
(`BITACORA.md`, respuestas del 30/09). El Windows completo se puede respaldar con Ghost.

## 9. Mantenimiento (manual cap. 7 y 11)

**Estado**: Mantenimiento → "Mantenimiento de equipos" → pestaña Drill: **12 tareas vencidas**
desde el último registro, **2026-01-04**. **Para marcarlas como hechas: ingresar el permiso
(probar `520`) → "Actualizar"** en cada tarea. Hacer el trabajo de verdad antes de marcarlo.

| Qué | Cada cuánto | Cómo |
|---|---|---|
| **Engrase de los paquetes de taladros** | **120–150 h** de trabajo del paquete | grasa **Klüber Isoflex Topas L32-N** (la pantalla dice "ISOFLEX TOPAS L 32 N"; es la misma). Una inyección con pistola por pico. **Arriba: 2 picos principales + 4 de los horizontales (`水平油嘴`). Abajo: 1 pico principal.** Sólo esa grasa |
| **Lubricación de las guías** | automática | revisar que el aceitador tenga aceite y que las guías estén aceitadas. Si falta: botón **"Lubricant"** en la pantalla del botón **"M"** de CncMon32 (anda en cualquier modo; se puede poner de más, no saltear) |
| Ajuste de la lubricación automática | al instalar | CncMon32 → F8 → F3 → F5 → parámetro **3430** (intervalo) y **3431** (tiempo de bombeo) |
| **Aire** | diario | sin pérdidas en entrada/salida · vaciar el vaso del **filtro** si pasa la marca máxima · **lubricador** (FRL) por encima de la mínima, completar con aceite neumático · **purgar el tanque** de aire |
| **Polvo** | cada mantenimiento | limpiar los puntos marcados en el manual (11.2) para que no se acumule |
| Viruta | al terminar el día / después de fresar | limpiar adentro y afuera; el soplador manda la viruta a la salida de aspiración (izquierda de la máquina) |
| **Batería del control** | 3–6 meses | ver §8 |
| Mechas | siempre | afiladas, prisionero firme; si el prisionero patina, cambiarlo |

## 10. Ajuste de precisión — si los agujeros salen corridos (manual cap. 18)

**Primero** (18.1): bajar la velocidad al **30 %** para la primera prueba · todas las puntas en el
mismo plano ±1 mm (§6.9) · con el Z en origen, los horizontales no tienen que chocar con los
manipuladores · fijar los límites de recorrido para que no haya choque posible.

**Orden**: se ajusta primero la herramienta de referencia de arriba (**T1**), después la de abajo
(**T21**) contra la T1, después cada herramienta con sus desplazamientos X/Y/Z en la tabla.
Después de mover la referencia hay que recalibrar el parámetro **124** (posición de la columna
de posicionamiento) y los límites de recorrido.

| Para corregir… | Dónde | Sentido (según el manual) |
|---|---|---|
| Agujeros verticales — adelante/atrás | Configuración → Componentes neumáticos → **base de la columna de posicionamiento X** | más valor → **más cerca** del canto de referencia |
| Columna de posicionamiento — izq/der | ídem → **base Y** | menos valor → más a la izquierda |
| Agujeros verticales — izq/der | **G54 de nueva generación**, Y | menos valor → más cerca de la referencia |
| Agujeros verticales — profundidad | **G54 de nueva generación**, Z | más valor → mecha más arriba → **menos profundo** |
| Paquete de abajo vs. arriba — adelante/atrás | Configuración → Ajustes comunes → **parámetro 121** | menos valor → más cerca |
| Paquete de abajo — izq/der / profundidad | G54, V / W | V: menos valor → más cerca · W: más valor → sube la mecha |
| Horizontales — altura | tabla, Z de la herramienta | más valor → más cerca de la mesa |
| Horizontales — distancia de la punta al canto antes de entrar | tabla → **distancia de seguridad** | menos valor → más cerca |
| Fresa de arriba — posición | tabla, desplazamiento X / Y | más valor → más lejos de la referencia |
| Fresa de arriba — profundidad | tabla, Z | ⚠️ el manual dice "más valor, más profundo": **en esta máquina es al revés** (§6.7) |
| Fresa de abajo | tabla "W1", desplazamientos X / Y | más valor → más lejos de la referencia |

Para los horizontales 17± / 18± / 19± / 20± el manual da un sentido distinto para cada uno
(18.2.2); consultarlo ahí antes de tocar. **Hacer backup (§8) antes de cualquier ajuste.**

## 11. CncMon32: atajos, MDI y códigos

**Atajos** (manual cap. 14): **Ctrl+2** automático · **Ctrl+4** manual continuo (habilita todo el
botón "M") · **Ctrl+7** volver al origen · **Ctrl+Alt** reset / retraer / quitar alarma.

**Menús útiles**: F8 Sistema → F2 Diagnóstico → **F5 señales de entrada** (para ver qué sensor
falla; si la máquina se para por una señal, la pantalla marca en amarillo qué revisar, con el
formato `M52 I31 P1` = señal Nº 31 presente) · F8 → F3 → F5 **ir a parámetro** · idioma:
parámetro **3209** (`0` = inglés).

**MDI** (manual 15.1.2–3), para probar a mano (siempre en condición segura):
`G00 A0` mueve el eje A a 0 · `G01 Y900 F15000` mueve Y a 900 a 15 m/min · `T1` baja la mecha 1 ·
`T00` sube todas · `M50` / `M51` baja / sube la rueda de presión de adelante · `G04 P1000` espera
1 s · `M00` para hasta el próximo verde · `M27` fin.

**Códigos M de las salidas** (manual cap. 12):

| Código | Qué acciona |
|---|---|
| M3 / M5 | husillo de fresado de arriba |
| M13 / M15 | husillo de fresado de abajo |
| M6 / M7 · M16 / M17 | paquete de taladros arriba · abajo |
| **M64 / M65** | **"Milling cutter pallet" — la placa de la fresa (campana / placa prensora)** |
| M40 / M41 · M60 / M61 | electroválvula del cilindro del husillo de arriba · de abajo |
| M36 / M37 | cilindro de posicionamiento |
| M20 / M21 · M22 / M23 | pinza izquierda · derecha |
| M28/29 · M50/51 · M32/33 · M34/35 | ruedas de presión 1 a 4 |
| M26 / M27 | ventilador |

El botón de cambio de herramienta del panel físico es la entrada **R60.3** ("Tool change key").

## 12. Reglas de oro

1. Que no haya error no significa que esté bien: **leer la tabla fila por fila**.
2. **Z siempre desde arriba.** Menos valor = más profundo.
3. **Después de tocar la tabla, Generar de nuevo.**
4. **Variador**: 100 Hz para cazoletas, 300 Hz para ranurar. Mirar en qué quedó antes de arrancar.
5. La Ø20x70R es una mecha: **nunca para fresar**.
6. Formato **KDTXml** en cada carga.

## 13. Contacto técnico

Grupo de WeChat con Huahua: **Srta. Tan (谭小姐)** comercial; técnicos **周涛 Zhou Tao**
(139 2595 7559, Changsheng Machinery) y **唐玮民 Tang Weimin**. China está **+11 h**: contestan
entre las **22:00 y las 03:00** hora argentina. Lo ya preguntado y respondido: `BITACORA.md`
(24/09 y 30/09).

## 14. Pendiente en esta máquina

| # | Qué | Cómo / a quién |
|---|---|---|
| 1 | Velocidad por herramienta desde la PC ("Convertidor de frecuencia" con el MS300), para no tocar el variador a mano | Huahua |
| 2 | **T187: ¿fresa o mecha?** Sobrecargó en la ranura de 8 del curvado a 300 Hz. Si es mecha, cambiarla por una fresa espiral Ø6 | mirarla en la máquina |
| 3 | La placa prensora / campana **no baja sola** al fresar (la viruta no se aspira); bajada a mano → MLC 129 | Huahua |
| 4 | Qué es la **T190** ("同动刀") | Huahua |
| 5 | Usuario del login | Huahua |
| 6 | KDTXml por defecto: contestaron "提供操作视频" — ¿mandan ellos un video o lo piden? | Huahua |
| 7 | Formato de la **ranura de canto** y si esta máquina la hace | Huahua |
| 8 | ¿Entra el horizontal Ø8 por la escotadura del uñero (50 × 70)? | primera pieza: lateral de la Cajonera |
| 9 | **Espejado**: nunca se midió formalmente con calibre (las puertas de la Spar tampoco se controlaron, 01/10) (techo: la ranura tiene que dar a 372,5 desde un borde de 398) | calibre |
| 10 | Capturar las filas 15–27 de la tabla de herramientas | captura |
| 11 | Ver y documentar el video de 0:55 de instalación manual de herramienta que mandó Huahua | WeChat |
| 12 | Hacer la lubricación vencida y marcarla | en la máquina |
| 13 | Avisarles que el manual 11.3 tiene el signo del Z al revés (avisado dos veces, sin acuse) | Huahua |
| 14 | Poner en hora el reloj de la PC industrial | en la máquina |
| 15 | **Campana / placa prensora (ítem 3)**: según el manual se acciona con **M64 / M65**. Preguntar a Huahua si el post de MH2026 manda M64 al fresar y cómo se habilita | Huahua |
| 16 | **12 verticales arriba según el manual, 9 en la tabla** — capturar filas 15–27 y mirar el cabezal | captura + mirar |
| 17 | **¿Hay dos variadores?** Si la T11 tiene el suyo, el de 100 Hz no la afecta | mirar el gabinete |
| 18 | La tabla de "velocidades por diámetro" del manual (4500…1200) vs. motor del paquete a 2800 rpm: ¿es avance? | Huahua |
| 19 | Pruebas de `MAÑANA_EN_LA_MAQUINA.md` sin resultado anotado: **medida terminada vs. de corte** (techo: X 40 / 360, Y 9 / 591), **¿lee `EdgeFBLR`?** (fascia `9441838670156` de los dos juegos), **Fusion vs. GuiGui** (mismas 10 piezas), **pieza curva R50** (`PENDRIVE/3_PIEZA_CURVA`) | en la máquina |
| 20 | Hacer el primer **backup** de `D:\DiskC-…` y guardarlo fuera de la máquina | en la PC |
| 21 | Capturas que faltan para el instructivo: encendido (panel), pinzas viniendo al frente, placa bien apoyada, cazoleta Ø35 terminada y medida, pieza medida con calibre, botón de cambio de herramienta del panel | fotos |
| 22 | **Puesto 6 (T186)**: ¿hay cono montado y qué herramienta tiene? Si está libre, anotarlo; si no, cargarla en la tabla | mirar la revista |
