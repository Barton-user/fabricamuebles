# Instructivo SKH-612HS — índice de capturas

Material para armar el instructivo en Figma. Cada entrada dice **qué se ve** y **qué enseña**,
para que al montarlo en el board no haya que volver a interpretar las pantallas.

Máquina: **perforadora de seis caras HUAHUA SKH-612HS**
Software: **桦桦数控钻 MH2026_Drill 3.0.5.0** (build 2025/12/15) + **CncMon32**
Sesión de origen: 23–24/09/2026, primera puesta en marcha con PRUEBA 1 (orden 260625-20)

---

## Capítulo 1 · Antes de la máquina — la pieza y su etiqueta

| # | Archivo | Qué se ve | Qué enseña |
|---|---|---|---|
| 01 | `01_etiqueta_pieza_599x398.jpg` | Etiqueta pegada en el techo: 工程 `0203米格样柜电子锯文`, 部件 `P01`, 规格 `599 X 398` | **Dos errores de mapeo de AutoCUT**: el código de barras sale como `P01` en vez del código largo (la perforadora busca el archivo por ese código, así que el escaneo no funciona), y la medida sale 599 × 398 en vez de 598 × 399 porque las columnas de canto quedaron cruzadas |

---

## Capítulo 2 · Importar el archivo

| # | Archivo | Qué se ve | Qué enseña |
|---|---|---|---|
| 02 | `02_pantalla_principal_mh2026.png` | Pantalla de arranque: barra Manual / Automático / Parámetro / Configuración / Mantenimiento, estado, Iniciar / Pausa / Reiniciar / Simulación | Layout general. **El rojo permanente de "Mantenimiento" es un aviso de vencimiento, no el modo activo**; esos cinco son menús desplegables |
| 03 | `03_cargar_archivo_lista_de_formatos.png` | Diálogo **"Cargar archivo"** con el desplegable **Formato** abierto, ~24 opciones | **El dato más importante de la sesión**: hay `KDTXml` (nuestro XML3) y `Haomai MPR` (nuestro MPR). **No existe `.ban`** |
| 04 | `04_cargar_archivo_formato_por_defecto_no_lista_nada.png` | Mismo diálogo con Formato = **"Nueva generaciónXml"**, lista vacía | **Trampa**: el desplegable arranca en el formato equivocado y **no da error** — simplemente no lista archivos. Hay que cambiarlo a mano cada vez |
| 05 | `05_archivo_importado_kdtxml_400x600x18.png` | "Tipos completados" con la fila `9441838670057`, tamaño de placa `400 x 600 x 18` | Importación correcta: leyó bien las medidas de la placa desde el XML |

---

## Capítulo 3 · Leer la pieza en el editor

| # | Archivo | Qué se ve | Qué enseña |
|---|---|---|---|
| 06 | `06_pieza_dibujada_edicion_2d_rotada_270.png` | Pieza dibujada, cartel **`CCW Rotate 270°`**, flecha grande a la izquierda, tabla de operaciones | Doble clic en la fila abre la pieza. **El software rota cada pieza y eso define cómo cargarla** — el techo 270° con flecha a la izquierda, la puerta 90° con flecha a la derecha. Las coordenadas de la tabla ya vienen rotadas |
| 08 | `08_tabla_operaciones_fila5_diametro_demasiado_grande.png` | Las 6 operaciones; fila 5 en rojo, columna "Motivo no procesado" = *"Diámetro de herramienta demasiado grande"* | Dónde se lee **por qué** una operación no se puede hacer. Acá: la ranura de 9 × 9 de cara dorso |
| 07 | `07_cola_error_en_conversion.png` | Fila de la cola en rojo, **"Error en conversión"**, Estación única, Taladro de seis caras (2 paquetes) | El error de la cola es consecuencia, no causa: siempre mirar "Motivo no procesado" de la tabla |
| 09 | `09_procesamiento_asignado_t56_t158_t187.png` | Cola en azul **"Procesamiento asignado"**; herramientas asignadas: Ø10 → T56 y T158, ranura de 6 → T187 | Destildando la operación imposible y apretando **Generar**, el trabajo queda listo. **El software asigna las herramientas solo** |

---

## Capítulo 4 · Cargar la placa y mecanizar

| # | Archivo | Qué se ve | Qué enseña |
|---|---|---|---|
| 10 | `10_zona_de_carga_placa_apoyada.jpg` | Mesa perforada con la placa apoyada suelta en el medio | Cómo **no** va: sin apoyar contra ningún tope |
| 11 | `11_pinzas_neumaticas_lado_de_referencia.jpg` | Las dos pinzas neumáticas sobre su viga, del lado opuesto al operador | **Ese es el lado de referencia.** El canto largo va contra las pinzas |
| 13 | `13_campo_escanear_codigo.png` | Campo **"Escanear código"** con el código tipeado a mano | Acepta tipeo, no hace falta escanear. **Define qué pieza sale**: si queda el código viejo, arranca la pieza vieja |
| 20 | `20_placa_con_ranura_de_6_hecha.png` | La placa sobre la mesa con la ranura de 6 ya mecanizada | Primera pieza mecanizada con archivos generados sin el exportador de GuiGui |
| 21 | `21_ranura_dorso_t11_en_ejecucion.png` | Fila 5 con **T11** asignada, cola **"En ejecución"**, ranura marcada en verde | La ranura de dorso sale poniendo ancho 10 (el mínimo de esa cara) |

**Secuencia de arranque (para el board — no hay captura, es de manual):**
equipo + vacío → COMPUTER START → esperar que arranque la PC → POWER → ~1 min → CncMon32 en
*ready* → HHcnc/MH2026 → importar → Generar → **verde 1ª vez** (las pinzas vienen al frente y
entra el aire) → **colocar la placa** → **verde 2ª vez** (mecaniza).
Apretar Iniciar antes del verde da `coordinate 71 — no se especifica el nombre principal del programa`.

---

## Capítulo 5 · Las alarmas y qué significan

| # | Archivo | Qué se ve | Qué enseña |
|---|---|---|---|
| 12 | `12_mantenimiento_12_tareas_vencidas.png` | Ventana de mantenimiento, 12 tareas en rojo, último registro 2026-01-04 | Lubricación vencida. No bloquea la operación. Aceite **ISOFLEX TOPAS L 32 N**, cada 120-150 h de trabajo del pack |
| 25 | `25_puerta_tooltip_argumentoutofrange.png` | Tooltip: *"Se produjo un error desconocido durante el fresado… System.ArgumentOutOfRangeException: el índice estaba fuera del intervalo"* | **Crash del software cuando falta una herramienta.** No avisa "falta la mecha Ø6", se rompe. Los verticales disponibles son Ø5, Ø8, Ø10, Ø12, Ø15, Ø20 |
| 24 | `24_puerta_filas_o6_en_rojo.png` | Las 4 filas de Ø6 en rojo, las 2 de Ø35 sin error | Mismo caso, visto en la tabla. **Cambiando los Ø6 a Ø5 se procesan sin problema, con T162** |
| 40 | `40_cola_vacia_trabajo_cancelado.png` | Cola completamente vacía, Total 0 | Un ciclo interrumpido **vacía la cola solo**. Hay que volver a mandar el trabajo |
| 41 | `41_cola_con_el_trabajo_reasignado.png` | El trabajo de vuelta en "Procesamiento asignado" | Recuperado |

**Alarmas sin captura, anotadas en `CONTEXTO.md`:**

- `MLC 148 PLC — ancho de placa demasiado pequeño, r49,3` → la placa medida no coincide con el programa. Se saltea destildando **"Detección de ancho"** y **"Detección de longitud"**.
- `MLC 142 — señal de sujeción del husillo anormal, r48,13` → fue a buscar una herramienta a un puesto vacío.
- `"Se prohíbe el mecanizado cuando el husillo no está sujeto"` → quedó activo el modo de cambio de herramienta.

---

## Capítulo 6 · La tabla de herramientas

| # | Archivo | Qué se ve | Qué enseña |
|---|---|---|---|
| 17 | `17_tabla_herramientas_filas_1_14.png` | Filas 1-14: verticales `Z positivo` Ø10, Ø20, Ø5, Ø8, Ø15, Ø12 | Dónde vive la tabla: **Parámetro → "Configuración de paquete de…" → "Herramientas de corte generales"**. A la izquierda el diagrama "bolsa de taladro 1 / 2" |
| 18 | `18_tabla_herramientas_filas_14_27.png` | Filas 14-27: verticales `Z negativo` (cara dorso) y horizontales `X±` / `Y±` Ø8 | El tipo de herramienta dice en qué cara trabaja |
| 15 | `15_tabla_herramientas_filas_28_41.png` | Filas 28-41 | — |
| 16 | `16_tabla_herramientas_filas_44_57_husillos.png` | Filas 44-57: **181** sierra lateral Ø100,2 ancho 7 · **182** Lamello Ø9,8 · **183** hoja de sierra Ø43,9 ancho 3 · **184** husillo Ø10 · **185** Ø3,2 · **186** Ø24 sin cargar · **187** Ø6 · **188** Ø10 · **190** | **El bloque clave.** Acá se ve qué hay para ranurar y fresar, y que **no hay Ø35 ni Ø9** |
| 14 | `14_ranura_dorso_sin_herramienta_asignada.png` | Fila 5 con 6/6 y la columna Herramienta **vacía**, sin motivo de rechazo | Estado intermedio: cambiar el valor no alcanza, hay que apretar **Generar** para que asigne |
| 19 | `19_dialogo_ranura_frente_dorso.png` | Diálogo **Ranura**: Frente/Dorso, Ancho, Profundidad, "Asignar nú", Distancia, Reducción, Múltiple | **Este diálogo no tiene campo de posición** — la posición se mueve arrastrando en el dibujo o con "Desplazamiento" |

---

## Capítulo 7 · Herramientas: la revista y el cambio

| # | Archivo | Qué se ve | Qué enseña |
|---|---|---|---|
| 27 | `27_manual_612ns_modo_cambio_de_herramienta.png` | Pantalla Manual → pestaña `612NS`: diagramas de los dos paquetes, coordenadas de los 9 ejes, jog, y abajo **Modo de origen · Reinicio de engrase · Modo de cambio de herramienta · RESET** | Con **"Modo de cambio de herramienta"** en verde salen los cilindros de la revista. ⚠️ **Hay que apagarlo antes de mecanizar**: en ese modo el husillo queda liberado y el control se niega a trabajar |
| 28 | `28_revista_de_conos_puesto_4_vacio.jpg` | Revista lineal rotulada `4号 5号 6号 7号 8号`; los puestos 5, 6 y 7 con cono, **el 4 vacío** | **Es una revista de conos, no pinzas en el husillo.** Y la regla de numeración: **`T18n` = puesto `n`** (T184 → puesto 4, T187 → puesto 7) |
| 29 | `29_fresa_disco_62211_4T_45x3.jpg` | Fresa marcada `62211-4T 12.7*45*H3` | Disco de ranurar: mango 12,7, Ø45, 4 filos, **3 mm de espesor**. Corresponde a la T183. **Corta de costado, no puede hundirse** — no sirve para cazoletas |
| 35 | `35_fresa_espiral_o20x70R.jpg` | Fresa marcada `Ø20x70R 250710` | Fresa espiral de mango: **sí se hunde**, y con Ø20 fresa el círculo de Ø35 |
| 36 | `36_medicion_voladizo_46mm.jpg` | Midiendo con cinta desde la cara de la tuerca hasta la punta | **El manual pide más de 45 mm de voladizo.** Quedó en 46. La pinza tiene que agarrar sobre el mango cilíndrico, nunca sobre los filos |

---

## Capítulo 8 · Forzar una herramienta (override)

| # | Archivo | Qué se ve | Qué enseña |
|---|---|---|---|
| 31 | `31_dialogo_vertical_asignar_numero.png` | Diálogo **Vertical**: Frente/Dorso, Diámetro, Profundidad, Pasante, **botón "Asignar nú" + casillero + tachito**, Posición, Múltiple | El casillero es **de sólo lectura** — se llena desde el selector, no a mano |
| 30 | `30_selector_especificar_herramienta.png` | Selector **"Especificar herramienta"**: diagramas clicables + campos Número / diámetro / tipo | Se elige **cliqueando el ícono en el diagrama** |
| 32 | `32_selector_no_muestra_la_187.png` | El mismo selector; están 181, 188, 190 y las mechas — **la 187 no aparece** | El selector **filtra por tipo de operación**. Para un vertical de cara frente no ofrece la 187 |
| 33 | `33_override_t188_primera_columna.png` | Fila 2 con **T188** en la primera columna Herramienta y **T184** en la segunda | **Hay dos columnas "Herramienta"**: la primera es la forzada por el usuario, la segunda la que asigna el post. La segunda no cambia hasta apretar Generar |
| 34 | `34_filas_2y5_con_t188.png` | Las dos cazoletas con T188 forzada | Resultado: **rechazado** — *"no se puede usar la herramienta especificada para el procesamiento"*. En el diagrama la 188 está dibujada como horizontal, no puede hundirse |

---

## Capítulo 9 · Editar la tabla de herramientas (requiere contraseña)

| # | Archivo | Qué se ve | Qué enseña |
|---|---|---|---|
| 37 | `37_aviso_seleccione_la_herramienta_de_edicion.png` | Cartel **"Por favor seleccione la herramienta de edición"** | No se puede editar escribiendo en el panel de abajo sin antes seleccionar la herramienta en el diagrama. **La celda de la tabla es de sólo lectura** |
| 42 | `42_wechat_contrasena_520.png` | WeChat con 桦桦唐玮民 (Huahua): `密码 520` | **La contraseña de fábrica de la tabla de herramientas es `520`** |
| 43 | `43_t184_diametro_20_guardado.png` | Fila 52 (T184) con **diámetro 20 y ancho 20** | Flujo completo: cliquear el ícono en el diagrama → contraseña `520` → editar diámetro y ancho en "Configuraciones de uso común" → **"almacenar herramientas"** |

**El truco de compensación** (para cuando no se tiene la contraseña, o mientras la tabla está mal):

```
diámetro a pedir = diámetro real deseado − (Ø real de la fresa − Ø declarado en la tabla)
ejemplo: cazoleta de 35 con fresa real de 20 declarada como 10  →  35 − 10 = 25
```

| # | Archivo | Qué se ve |
|---|---|---|
| 38 | `38_filas_2y5_diametro_25_compensado.png` | Las cazoletas pedidas como Ø25 para que salgan Ø35 |

---

## Capítulo 10 · Probar en un recorte de otra medida

| # | Archivo | Qué se ve | Qué enseña |
|---|---|---|---|
| 39 | `39_fila_1_destildada_cae_fuera_de_la_placa.png` | Fila 1 destildada (X = 605,83) | **Si el recorte es más chico que la pieza del programa, hay operaciones que caen fuera de la placa** y la máquina taladraría al aire. Comparar cada coordenada contra la medida del recorte antes de dar verde |
| 26 | `26_puerta_apoyada_en_la_mesa.jpg` | La puerta apoyada, lado largo en el sentido de la mesa | Orientación correcta para esa pieza. Caso curioso: cargada 180° girada, la puerta izquierda pasa a ser exactamente la derecha |

---

## Capítulo 11 · El origen de los archivos (contexto, no operación)

| # | Archivo | Qué se ve | Qué enseña |
|---|---|---|---|
| 22 | `22_puerta_importada_editor_todavia_con_techo.png` | Puerta importada arriba (297 × 681,83) pero el editor sigue mostrando el techo | Importar no es abrir: **hay que hacer doble clic en la fila** |
| 23 | `23_fusion_render_puerta_cazoletas.png` | Render de Fusion de la puerta con las 2 cazoletas Ø35 y los 4 tornillos | La geometría del modelo coincide con el archivo de máquina generado |
| — | `9441838670057.xml` | El KDTXml del techo | Ejemplo de archivo de entrada: `<KDTPanelFormat>`, `TypeNo 1` = agujero vertical, `TypeNo 3` = ranura cara A, `TypeNo 13` = ranura cara B |

---

## Pendiente de capturar

Para que el instructivo quede completo faltan fotos de:

- La secuencia de encendido (panel: equipo, vacío, COMPUTER START, POWER) y CncMon32 en *ready*
- El momento en que las pinzas vienen al frente después del primer verde
- La placa correctamente apoyada contra el tope del lado de las pinzas
- Una cazoleta Ø35 terminada y medida con calibre
- La pieza medida con calibre — las cotas reales contra las esperadas
- El botón de cambio de herramienta del panel físico (el "Tool change key" del manual)

---

## Capítulo 12 · El `.scx` guarda tus ediciones — la trampa más peligrosa

Cuando se edita una operación en el editor, el software **guarda la pieza como `.scx`** con
esos cambios. Al re-importar el mismo XML **devuelve la versión editada, no el original**.
Para volver al archivo limpio hay que **borrar la fila de "Tipos completados"** primero.

| # | Archivo | Qué se ve | Qué enseña |
|---|---|---|---|
| 44 | `44_cazoletas_mal_o20_pasante_dos_caras.png` | 8 filas en vez de 6. Cada cazoleta desdoblada en dos: una cara "atrás" y una "frente", **Ø20 profundidad 9,5** | Ediciones viejas que sobrevivieron al re-import. 9,5 + 9,5 = 19 sobre una placa de 18 → **agujero pasante de Ø20**, no una cazoleta |
| 45 | `45_cazoletas_mal_sin_error_t2_t153_PELIGRO.png` | Las mismas 8 filas, **todas verdes**, con T2 y T153 asignadas | ⚠️ **La lección más importante del instructivo: que no haya error NO significa que esté bien.** El software encontró las mechas verticales de Ø20 y hace exactamente lo pedido — y lo pedido estaba mal. Dos agujeros pasantes en la puerta |
| 47 | `47_importacion_limpia_cazoletas_o35_ok.png` | 6 filas. Cazoletas **Ø35 prof 13 cara frente, sin error**; los cuatro Ø6 en rojo | Después de borrar el `.scx` y re-importar. **Con el diámetro de la T184 corregido a 20, las cazoletas se resuelven solas** — sin override ni compensación. Sólo quedan los Ø6 |

**Regla para el operador**: antes de dar verde, leer la tabla de operaciones fila por fila y
comparar cara, coordenada, profundidad y diámetro contra el plano. El color verde sólo dice
que hay herramienta disponible, no que la geometría sea la correcta.

## Capítulo 13 · Los marcadores del dibujo 2D

| # | Archivo | Qué se ve | Qué enseña |
|---|---|---|---|
| 46 | `46_zoom_marcadores_pinzas_y_esquina_referencia.png` | Zoom del dibujo: dos rectángulos grises con círculos y un círculo rosa, **todos fuera del contorno de la placa** | **No son mecanizados** — no figuran en la tabla de operaciones. Lectura probable, sin confirmar: los grises son las dos pinzas dibujadas donde van a agarrar, el rosa es la esquina de referencia. Útil para ver si alguna operación cae donde agarra la pinza |
