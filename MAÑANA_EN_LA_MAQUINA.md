# Mañana en la máquina — las 6 cosas que sólo se contestan ahí

El protocolo completo de encendido y operación está en **CONTEXTO.md §10-bis**.
Esta hoja es sólo lo que quedó abierto, con la respuesta que hay que traer.

**Llevar:** la carpeta `PENDRIVE/` entera, calibre, y las hojas de verificación impresas.

---

## 1 · ¿Qué formato lee HHcnc?

**La más importante, y es gratis.** En HHcnc, abrir el diálogo de importar
archivo/directorio y mirar el **filtro de tipos**: ahí se ve si acepta `.ban`,
`.mpr`, `.xml` o varios.

→ **Sacar captura.** Define qué carpeta usamos de acá en adelante y qué plantilla
hay que dejar configurada.

---

## 2 · La prueba de fuego: ¿la máquina distingue los dos juegos?

En el pendrive hay **las mismas 10 piezas dos veces**:

- `1_DESDE_GUIGUI` — el control, lo que GuiGui manda hoy
- `2_DESDE_FUSION` — modeladas en Fusion, sin abrir GuiGui

Toda la geometría es idéntica. Si la máquina procesa las dos igual, **el camino
Fusion está probado sobre metal** y GuiGui deja de hacer falta.

→ Cargar la misma pieza de los dos juegos y comparar. Empezar por el **techo
400 × 600, código `9441838670057`**.

---

## 3 · Medida terminada vs. medida de corte

El archivo lleva la medida **terminada**. Hay que saber si la perforadora espera
la pieza **ya canteada** o si compensa ella.

→ Mecanizar el techo y medir con calibre:

| Qué | Esperado |
|---|---|
| X del primer agujero | **40,0** |
| X del último agujero | **360,0** |
| Y del primer agujero | **9,0** |
| Y del último agujero | **591,0** |
| Ancho de la placa | 400,0 |
| Alto de la placa | 600,0 |

Si los agujeros caen corridos justo el espesor del canto, ya sabemos la respuesta.

---

## 4 · ¿Algo lee el atributo de cantos (`EdgeFBLR`)?

Es la **única diferencia** entre los dos juegos, y está en las dos fascia boards:
`9441838670156` y `9441838670163`.

GuiGui rota la geometría de esas piezas pero deja la bandera de canto sin rotar;
nosotros la rotamos. Las dos describen la misma pieza física.

→ Mecanizar `9441838670156` de **los dos juegos** y comparar. Si salen idénticas,
el atributo no lo lee nadie y la diferencia no existe en la práctica.

---

## 5 · La veta de los frentes, en AutoCUT

Para esas mismas dos piezas, nuestra lista de corte dice **长 564 / 宽 100** donde
GuiGui dice **长 100 / 宽 564**. Las medidas son las mismas; cambia cuál se llama
largo y cuál ancho.

→ Cargar las dos listas de corte en AutoCUT y mirar **cómo queda orientada la
pieza en el tablero**. Eso dice si `长` manda la dirección de la veta o es sólo
una etiqueta.

---

## 6 · Para preguntarle a la Sra. Tan: la ranura de canto

**¿Cómo se declara una ranura de canto en el `.ban`?** El canal fresado en el
borde, el típico para el fondo.

En los 82 archivos de referencia no hay ni uno, y el vocabulario que sí aparece es
sólo `Plane, Outline, Point, HoleV, HoleH, SlotL`. Hoy el generador **se niega a
escribirla** en vez de inventar el formato.

→ Preguntar también: **¿esa operación la hace la SKH-612HS, o va en otra máquina?**
Puede que la respuesta sea que no corresponde y el tema se cierra ahí.

---

## Extra, si sobra tiempo: el contorno curvo

`3_PIEZA_CURVA` es un lateral de 350 × 500 con redondeo R50, modelado en Fusion.
Los cuatro formatos salieron **idénticos** a los que generó Bluen para esa misma
pieza. Si la máquina la hace bien, el contorno irregular queda cerrado.

---

## Anotar también

- El **número de herramienta** de cada diámetro en la Knife Library
  (para PRUEBA 1 hacen falta Ø6, Ø8, Ø10, Ø15, Ø35 y fresa Ø6 y Ø9)
- Si el herraje real es el de **perno 33** o el de **34** — los dos pedidos de
  referencia usan distinto, y el script necesita saber cuál es el de la casa
