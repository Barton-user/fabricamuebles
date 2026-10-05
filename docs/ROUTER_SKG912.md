# Router SKG-912MZY (Huahua) — control Syntec + interfaz Huahua "CNC Monitor"

_Última actualización: 05/10/2026. Fuentes: `instructivo/manuales/SKG-912MZY_manual_router.pdf`
(manual mecánico, 65 págs: 33 de manual + esquema eléctrico) y
`instructivo/manuales/Router_guia_operacion_Syntec_开料机操作指导书.pdf` (guía de operación, 39 págs,
chino/inglés: puesta en marcha, G54, almacén, medición de herramientas, carga de programa, M-codes,
alarmas). Estado: **encendido, homing hecho, husillo girado a mano; ningún programa ejecutado todavía**.
Primera prueba preparada en `PENDRIVE/7_ROUTER_PRUEBA/` (ver su LEEME)._

## 1. Qué máquina es

| | |
|---|---|
| Modelo | **SKG-912MZY**: 9 = serie, **12 = almacén lineal de 12 herramientas**, M = estándar, Z = carga automática de placas, Y = rodillo prensor |
| Husillo | **9 kW, 18 000 rpm**, pinza **ER32** (vienen llaves ER32 y ER25). Variador **Folinn** (pantalla "F600.0" = 600 Hz = 18 000 rpm) |
| Área útil | **2800 × 1300** (plano: zona de trabajo 2650 × 1273). Repetibilidad 0,05. Rápidos X/Y 60 m/min, Z 20 |
| Mesa | vacío, **7 zonas**, bomba 7,5 kW (−0,4 a −0,9 MPa). Grasa Klüber GY193 1-2 veces/mes |
| Aire | 0,6–0,8 MPa. **Para soltar herramienta hace falta ≥ 7 bar** |
| Eléctrico | 380 V 3F+PE, 20,5 kW, cable 6 mm². Servos Syntec en X, Y1, Y2 (gantry doble), Z |
| Controlador | **Syntec** (caja con DA, MPG, USB, LAN) con interfaz Huahua "CNC Monitor v10.x" en castellano/chino |
| Auxiliares | pilares de posicionamiento neumáticos (定位柱), empuje lateral, empujador de descarga, campana de aspiración, cepillo |

## 2. Convenciones del programa (lo que importa para generar .nc)

- **Z0 = mesa** (superficie de sacrificio). Z18 = cara de arriba de una placa de 18. Corte pasante a
  **Z −0,1 / −0,2**. Altura segura **Z30** (programa estándar) o Z38 (GuiGui). Igual que nuestros `.nc`.
- La máquina trabaja en Z **negativo** en coordenadas máquina. Un **Z positivo en el programa sólo
  es válido después de `G43 H<n>`** (compensación de largo de la herramienta n); si no, alarma
  "Z supera el límite positivo" (guía §5.4.2.1). Los `.nc` de GuiGui **no traen G43** → la prueba
  `01_AIRE` decide si la interfaz lo agrega sola o si hay que poner encabezado.
- G54 Z = **"Z落差"**: diferencia de altura entre el palpador de herramientas y la mesa (p. ej. 12,497).
  Cada herramienta tiene su largo medido en la tabla; con eso Z0 cae en la mesa para todas.
- G54 X/Y = coordenada máquina del **pilar de posicionamiento** menos el **radio** de la fresa usada
  para calibrar (guía §1.3). Los `.nc` de GuiGui apoyan la placa ahí y dejan 15 mm de margen.
- El programa no puede exceder: X_programa + G54_X ≤ límite de máquina (§5.4.1.5).

**Programa estándar de Huahua (guía §9)** — formato a imitar:
```
%
G54
M78            (bomba de vacío ON)
T1
M03 S18000
G0 X0. Y-4.
G43 H1 Z30.    (largo de herramienta 1, Z seguro)
G1 Z-0.2 F10000
... contorno (G1 F10000, arcos G2/G3 R4 F2500) ...
G0 Z30.
G91 G28 Z0 M5
G90 G49 H0
M05
M79            (bomba de vacío OFF)
M30
%
```

**M-codes** (guía §8): M03/M05 husillo · **M78/M79 bomba de vacío** · M28/M29 cilindro de aspiración
· M20/M21 campana del husillo · M50/M51 soltar/apretar herramienta · M52/M53 almacén afuera/adentro
· M66/M67 pilares de posicionamiento (estación 1) · M68/M69 posicionamiento izq · M70/M71 der ·
M166/M167 posicionamiento placa chica · M74/M75 empuje lateral · M72/M73 empujador trasero ·
M60/M61 cilindro de carga · M62/M63 ventosas · M64/M65 cilindro de descarga · M100 carga/descarga
automática · M101 alimentación automática.

## 3. Operación en la pantalla (interfaz Huahua)

| Qué | Dónde |
|---|---|
| Modos | 自动模式 (auto) · MDI · 手动模式 (manual) · 寸动 (jog) · 手轮模式 (volante) · 原点模式 (homing) · **手轮模拟 (simulación por volante)** · 单节执行 (bloque a bloque) |
| Homing | 原点模式 → buscar origen. Los finales están a 90 mm (Y) / 260 mm (X) / 70 mm (Z) del extremo de guía |
| Límites de software | F8 系统管理 → F3 参数设定 → F6 使用者参数 / F5 行程极限 (parám. 2401–2406, en µm) |
| G54 | inicio → **F3 偏置/设定** → G54P1: cargar X/Y máquina menos radio; Z con **F3 Z落差** desde 自动对刀 |
| Almacén (刀库设定) | 12 puestos. Tabla con X/Y/Z del puesto 1; los siguientes **+100 en X**, mismo Z. Para ajustarlo: sacar la manguera del cilindro del almacén, "刀库气缸", volante, alinear el husillo con el puesto 1, anotar coordenadas máquina |
| Medir herramientas | **自动对刀** → tildar las herramientas → volante hasta centrar sobre el palpador → 对刀设定 (referencia XY) → 自动模式 + 手轮模拟 → arranca y mide. Referencia Z del palpador: 10 mm por encima de donde toca la herramienta más larga; "Z mínimo" 10 mm por debajo de la más corta |
| Cambio manual | 手动模式 → sostener el cono, **botón del husillo 2 s** → suelta. Aire ≥ 7 bar, sin alarmas |
| Cargar programa | **U盘导入** → tildar archivos → F1 拷贝 → inicio → F2 程序编辑 → F8 文件管理 → doble click → **F1 载入执行加工** |
| Correr seguro | 自动模式 + **手轮模拟**: el programa avanza sólo mientras se gira el volante en sentido horario; se para al soltarlo. Confirmado el recorrido, sacar la simulación |
| Reanudar | tras una parada: escribir el nº de línea en la casilla "起始单节" y 启动 |
| Permisos | 用户切换 → usuario **5**, clave **2222** (para corregir nº de herramienta, ver I/O, etc.) |

## 4. Herramientas disponibles (05/10/2026)

Mango **1/2" (12,7)** → pinza ER32 de 13 (agarra 12–13). Vinieron con las máquinas:

| Fresa | Ø × corte | Cant. | Uso |
|---|---|---|---|
| 御 焊片直刀 (recta, plaquitas soldadas) | 10 × 30 | 8 | **la de nesting / contornos** (la Ø10 es también la que Huahua usa de ejemplo) |
| 御 焊片直刀 | 6 × 22 | 1 | ranuras finas, T1 Ø6 del curvado |
| 公制直刀 1801 (recta) | 6 × 20 | 1 | ídem |
| 公制直刀 1801 | 8 × 30 | 1 | |
| 玉威 TCT 三刃通用直刀 (recta 3 filos) | 8 × 20 | 1 | |
| 玉威 月牙扣件刀 | 9,8 × 17,3 | 1 | fresa de forma para un herraje "media luna"; no es de uso general |
| 拉直器刀 L83580 (caja celeste) | 10,9 | 1 | sin identificar; mirarle el filo |

No hay fresas de corte descendente (compresión) ni V ni esféricas: la melamina de arriba puede
astillar con las rectas → probar y, si hace falta, comprar compresión Ø10 para el nesting.

## 5. Alarmas frecuentes (guía §5)

| Alarma | Causa / solución |
|---|---|
| Nº de herramienta erróneo | un cambio quedó a medias → el control pone T=0. Usuario 5 / 2222 → 手动模式 → 刀补坐标系 → 排刀设定 → poner el nº real |
| Límite de software al medir | origen o G54 tocados → rehacer §1.3 de la guía |
| "Llegó al Z mínimo sin señal del palpador" | palpador disparado antes de tiempo → mirar I33/I34 en 硬体接点; si están encendidos sin tocar, palpador roto |
| Z no llega a la referencia y alarma | herramienta demasiado larga → bajar la referencia Z del palpador (p. ej. −120 → −110) |
| **Velocidad cero (零速)** al arrancar el husillo | el variador no devuelve la señal: mirar salida O62 (arranque) y entrada I15 (零速, cable 21 y + del variador, 24 V) |
| Límite X/Y | origen perdido, offset XY en la tabla de herramientas (debe ser 0 en 812/912), offset externo ≠ 0, G54 mal, o programa + G54 > carrera |
| Límite Z positivo | Z positivo sin G43 en el programa; o Z subido a mano → bajar con volante / cambiar el límite temporalmente (§1.2) |
| Z no baja | husillo Z trabado → aflojar tornillos del motor Z; si no, soltar el acople **con el husillo apoyado** |

Entradas útiles: I20 parada de emergencia · I21 零速 · I25 botón de ciclo · I26 presión de aire ·
I27 alarma variador · I28/I29 herramienta apretada/suelta · I30 campana retraída · I31/I32 almacén
afuera/adentro · I33 sobrecarga bomba de vacío. Salidas: O50/51 rodillos · O52 rotura de vacío ·
O53 soltar herramienta · O54 almacén afuera · O56 pilares · O57 empuje lateral · O62 arranque husillo
· O80 bomba de vacío. Variador Folinn: P02.18 = 600 (f máx), aceleración/desaceleración 2,5 s
(P02.50/P02.70); errores E00xx en la guía pág. 25–26.

## 6. Pendientes del router

1. **Primera prueba física** (`PENDRIVE/7_ROUTER_PRUEBA/LEEME.txt`): pinza ER32-13 + fresa Ø10 en T1,
   medirla, aire 04 (estándar) y 01 (GuiGui) con 手轮模拟, corte 03. Decide el preset del generador.
2. Cargar las demás fresas en el almacén y medirlas; anotar la tabla T1–T12.
3. Medir recorrido útil real y G54 → corregir `ROUTER.mesaX/Y` en `curvado/src/herramientas.js`.
4. Comparar nuestra salida con la muestra china (`referencia/.../下料文件/*.nc`) una vez que corra una.
5. Mantenimiento: grasa de la bomba de vacío mensual; filtro semanal; aceite del lubricador 32#;
   batería 3,6 V de los encoders cada 6 meses.
