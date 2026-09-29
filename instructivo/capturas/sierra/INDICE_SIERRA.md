# Instructivo SIERRA HP280 — índice de capturas

Máquina: **seccionadora HUAHUA HP280** · Software del control: **HuaHuaSAW V7**
Sesiones: 24/09/2026 (tarde) y 25/09/2026. Pedido: tiras de 500 × 2440 para Vicente.
Manuales: `instructivo/manuales/Basic_operation_of_HuaHuaSAW_V7_software.pdf` y `..._AUTOCUT10_...pdf`

Cada entrada: **qué se ve → qué enseña**. Los números siguen el orden en que pasó.

---

## Capítulo A · La pantalla manual y los primeros intentos (24/09)

| # | Archivo | Qué se ve → qué enseña |
|---|---|---|
| S01 | `S01_24-09_manual_pantalla_inicial_E13.png` | Pantalla `manual` con la botonera completa y la E13 abajo → layout: VolOrig, MatRes, MatRetr/MatAvan, MatSuj, PrsVigBj/Sb, SierraCarIz/Dr, SierraHojaSb/Bj, MiniSierSb, AliLatIz/Dr, AliBckBj, EmpTraExt, Sierra ON, VentInic, CambSierHoj |
| S02 | `S02_..._empujador_2830_para_cargar_placa.png` | Empujador en 2830 (fondo) → la placa se apoya en la mesa de atrás con el lado de 2440 paralelo a la viga |
| S03–S04 | `AnchoCorteUn 1000 → 500` | El campo azul de abajo a la derecha es el ancho de corte único del modo manual |
| S05 | `E13 titila, Pos Lat 1466` | E13 = el carro lateral está en su fin de carrera; Alarma Off no la borra mientras siga ahí |
| S06 | `E13 al reabrir el programa` | Si el software se cuelga, reabrirlo no borra la E13 |
| S07–S08 | `MatRes` | MatRes = un toque, el empujador va solo a la posición inicial (300) |
| S09 | `AliLatDr, Pos Lat no cambia` | Con el carro en el tope, AliLat no lo mueve |
| S10–S11 | `automático, Uso Lateral` | "Uso Lateral / Stg" activa o desactiva el uso del alineador; **no borra la E13** |
| S12 | `Pos Lat 1783` | El carro se había movido con AliLatDr… hacia el lado equivocado (ver capítulo E) |

## Capítulo B · Diagnóstico con la pantalla E/S (24/09)

| # | Archivo | Qué se ve → qué enseña |
|---|---|---|
| S13–S14 | `E/S` | Menú `E/S`: izquierda entradas X (sensores), derecha salidas Y (válvulas/motores). Rojo = activa |
| S15 | `EmpTraRet en rojo` | EmpTraExt/Ret maneja el cilindro neumático **Y16 válvula solenoide lateral** |
| S16–S17 | `X36 rojo` | **X36 "límite de avance de presión lateral"** activa = causa de la E13 |
| S18 | `EmpTraExt → E13 desaparece` | Apagar Y16 limpió la E13 momentáneamente… |
| S19 | `MatRes → E13 vuelve` | …pero vuelve apenas se intenta mover el empujador: X36 sigue pisado |
| S19b | `Y16 apagada, X36 rojo` | Válvula apagada pero el sensor sigue detectando → problema físico, no de software |
| S19c | `X14 azul` | Con el hongo apretado X14 "circuito de parada de emergencia" pasa a azul: así se confirma que la máquina está parada |
| S19d / S19r | `FOTO torre` / `cilindro marcado` | La torre blanca del prensor lateral sobre la viga naranja del empujador |
| S19e–S19h | `E12`, `sin alarma`, `E13 vuelve` | E12 "volver al origen" es normal tras una emergencia → VolOrig. La E13 vuelve cada vez que el empujador intenta moverse |

## Capítulo C · El sensor X36 y el térmico (25/09)

| # | Archivo | Qué se ve → qué enseña |
|---|---|---|
| S19i–S19j | `automático`, `Uso Lateral rojo` | Probar Uso Lateral en los dos estados: la E13 no depende de eso |
| S19k | `FOTO extremo viga` | Sensor del extremo de la viga con lengüeta perforada = tope del **empujador**, no del lateral |
| S19l | `FOTO torre, sensores y cilindro` | En la escuadra a la izquierda de la torre hay **dos inductivos** (arriba y abajo) |
| S19m | `FOTO inductivos, LED rojo abajo` | **El inductivo de ABAJO con LED rojo encendido = X36.** Detecta la pletina blanca fija de la viga. La torre estaba contra el tope y el motor tiene freno: no se puede empujar a mano. **Salida: desenroscar ese inductivo → Alarma Off → AliLatIz → reponerlo** |
| S19n | `catálogo E20 E21` | Pantalla `alarma`: catálogo E00–E38, las activas en rojo. E20 = hongo apretado; E21 = fotoeléctrico |
| S19o | `E06 anomalía motora` | Al mover el lateral atorado saltó **E06 = X24 sobrecarga del motor** |
| S19p | `FOTO etiqueta INVT SV-DA200` | Servo driver INVT (empujador / carro). Con display en 00 = sano. **No era eso** |
| S19q | `FOTO gabinete KM1–KM8` | **Se rearmó el relé térmico de KM3** (motor del alineador lateral) y la E06 se fue. Hay térmicos también debajo de KM4/KM5 y KM6: ante E06 mirar primero los térmicos |

## Capítulo D · Corte sin AutoCUT: el menú editar (25/09)

| # | Archivo | Qué se ve → qué enseña |
|---|---|---|
| S20 | `manual, origen ok` | 1 · VolOrig → sin alarmas. 2 · MatRes (un toque) |
| S21 | `Ed. Gráfica con programa viejo` | 3 · Menú `editar` abre "Ed. Gráfica". Puede traer el programa anterior |
| S22 | `cortes vaciados` | 4 · "Vaciar todos los cortes" |
| S23 | `Longitud 1220, Ancho 2440` | 5 · **Longitud = el lado que el empujador va consumiendo; Ancho = el largo de cada tira.** Para tiras de 500 × 2440 de una placa 1220 × 2440: Longitud 1220, Ancho 2440. Costura de sierra 4.4 = kerf. "Valor de borde" 5 = refilado |
| S24 | `2 tiras de 500` | 6 · Longitud de corte 500 · Cantidad 2 → Añadir. Queda sobrante 206,2 |
| S25 | `automático, programa cargado` | 7 · "Confirmación" → pasa a automático con el dibujo del plan de corte |
| S26 | `Vel Cort 30, Modo Sing` | Revisar Vel Cort (30). "Modo Sing" = un corte por verde; "Modo Cont" = seguidos |
| S26b | `verde no arranca, sierra apagada` | **El verde no hace nada si la hoja no está girando** |
| S27 | `Sierra Arr + Flot Stg` | 8 · "Sierra ON" → cambia a **"Sierra Arr"** rojo; "Flot St" → **"Flot Stg"** rojo. Los botones muestran el estado |
| S28–S29 | `E/S X22` | **X22 "arranque automático"** se pone roja al apretar el verde: sirve para verificar que el botón llega al PLC |
| S30 | `1ra Cuch Pausa desactivado` | "1ra Cuch Paused" en rojo = pausa en el primer corte activada; tocándolo queda "1ra Cuch Pausa" azul. "Pausa" es un botón momentáneo |
| S31 | `dibujo lateral a la derecha / real a la izquierda` | **La pista clave:** el carro lateral se movía al revés de lo que mostraba el dibujo y de lo que decían los botones |
| S32 | `automático tras invertir fases` | Listo para cortar después de corregir las fases |

## Capítulo E · Causa raíz: secuencia de fases invertida (25/09)

Sin captura (es eléctrico). Los motores de contactor (hoja principal, incisor, carro lateral, ventilador)
giraban **al revés** porque la alimentación trifásica del taller estaba conectada con R-S-T en otro orden
que el de fábrica. El lateral fue contra el tope equivocado (E13) y se sobrecargó (E06). **Se invirtieron
dos fases en la entrada general** y se corrigieron todos juntos. Los servos INVT no se afectan.

**Regla:** después de cualquier trabajo eléctrico o de volver a conectar la máquina, verificar el sentido
de giro de la hoja contra la flecha antes de cortar. Recomendado: relé de secuencia de fases en el tablero
y revisar la pegadora de cantos HH-509R si está en el mismo tablero.

---

## Secuencia completa para cortar tiras sin AutoCUT (para el cartel 13)

1. `manual` → **VolOrig** → **MatRes** (un toque cada uno). Sin alarmas.
2. `editar` → "Vaciar todos los cortes".
3. Longitud = lado a consumir (1220) · Ancho = largo de la tira (2440) · Espesor 18 · Cantidad 1.
4. Longitud de corte + Cantidad → Añadir (una vez por cada medida).
5. **Confirmación** → pasa a automático.
6. Revisar Vel Cort (30) y el modo (Sing / Cont). "1ra Cuch Pausa" en azul.
7. **Niv Rep** (posición inicial del automático — el manual dice que es obligatorio).
8. **Sierra ON** → tiene que quedar **"Sierra Arr"** rojo y la hoja girando **en el sentido de la flecha**.
9. **Flot St** → "Flot Stg" rojo.
10. Placa con el lado de 2440 contra el empujador, escuadrada contra la regla.
11. Manos fuera, nadie cerca → **botón verde**. Si no arranca: E/S → X22 tiene que ponerse roja al apretarlo.
12. Medir la primera tira con calibre (¿descuenta el kerf?).

## Pendiente de capturar

- El primer corte en marcha y la tira medida con calibre
- La botonera física (verde, hongo, selector si tiene)
- La flecha de sentido de giro de la hoja
- La bornera R-S-T con las fases marcadas
