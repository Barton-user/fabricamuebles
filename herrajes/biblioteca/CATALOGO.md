# Biblioteca de herrajes — Leiten Com

**Regla: no volver a modelar estos herrajes. Importar el .step de esta carpeta.**

`ArmarDesdeRender.herraje()` ya lo hace solo: antes de dibujar busca en
`indice.json` un archivo cuyo prefijo coincida con el nombre del componente
(`Bisagra O35 base -6` → prefijo `Bisagra O35`). Si lo encuentra, importa el
STEP; si no, dibuja la forma con código, como antes.

Los STEP están **en el marco de uso**, no en el marco en que vienen de fábrica:
el origen de cada pieza cae exactamente sobre el agujero que hace la CNC, con
los ejes que usan los scripts. Eso quiere decir que se insertan con la misma
matriz que ya calcula `poner_tres_en_uno()` / `poner_bisagras()` y caen en su
lugar sin tocar nada.

---

## Piezas en STEP

### `excentrica_O15_hafele_262-26-034.step`
La caja excéntrica del 3 en 1 (lo que GuiGui llama 偏心件).

| | |
|---|---|
| Origen | centro del Ø15 sobre la cara de la placa |
| Ejes | +Z hacia adentro de la placa |
| Medidas | Ø14,9 × 14,0 mm de alto |
| Agujero de máquina | Ø15 prof. 12,5 |
| Origen del archivo | Häfele CADClick, artículo 262.26.034 (Minifix 15) |
| Verificado | Contra foto del herraje real (29/09/2026). Coincide. La real tiene ranura recta para destornillador plano, la de Häfele es de cruz — no cambia ningún agujero. |

### `perno_O8x33_dibujado.step`
El perno del 3 en 1, con su expansor.

| | |
|---|---|
| Origen | boca del agujero Ø8 en el canto |
| Ejes | +Z saliendo del canto hacia la excéntrica; la rosca va hacia −Z |
| Agujero de máquina | Ø8 prof. **33** (GuiGui). Häfele especifica 34 para el suyo. |
| Origen del archivo | dibujado por nosotros, medido sobre los archivos de PRUEBA 1 |
| Verificado | Contra foto (29/09/2026). Son **3 piezas**, no 2: perno + tarugo expansor azul + excéntrica. |

> El original de Häfele está en `perno_expansor_hafele_262-09-313.step`, pero
> viene con el eje sobre X y el origen corrido, así que no se usa todavía.

### `bisagra_cazoleta_O35.step`
Bisagra de cazoleta completa, **en posición cerrada**.

| | |
|---|---|
| Origen | centro de la cazoleta sobre la cara interior de la puerta |
| Ejes | X hacia el centro de la puerta, Y a lo largo del canto, Z hacia adentro de la puerta |
| Agujeros de máquina | cazoleta Ø35 × 13 prof., a 22,5 mm del canto (`HINGE`) + dos Ø6 × 3 a 14,5 mm hacia adentro y ±24 mm del centro (`HINGESCREW`) |
| Origen del archivo | híbrido: cazoleta y ala originales de Häfele 311.04.239; brazo, placa base y tornillos dibujados por nosotros |
| Verificado | Separación entre tornillos medida con cinta sobre el herraje real: **48 mm**. El archivo de GuiGui perfora a 48 (y=75 y 123, cazoleta en 99). Coinciden. |

**Ojo con esta pieza — dos cosas que hay que saber:**

1. El herraje real de la fábrica es **Grupo Euro** (marca argentina), *no* Häfele,
   aunque en su momento nos dijeron que sí. Está estampado en la cazoleta.
2. Por eso el ala del STEP de Häfele trae los ojales a **53,5 mm** y no a 48.
   Los tornillos del modelo están puestos en **48**, que es donde perfora la
   máquina, así que se ven corridos hacia una punta del ojal. Eso no es un error
   de modelado: es la diferencia real entre las dos marcas. Si algún día se
   compra Häfele, hay que cambiar el parámetro `HINGESCREW` en GuiGui.

El brazo está dibujado porque el STEP de Häfele viene con la bisagra **abierta a
90°** y no hay rotación rígida que la cierre (es un mecanismo de cuatro barras:
al cerrarse el brazo no gira, se pliega). El original abierto quedó guardado en
`ref_bisagra_hafele_311-04-239_ABIERTA.step` por si alguna vez se necesita.

---

## Piezas que siguen siendo código (a propósito)

Estas cambian de largo según el mueble, así que un STEP fijo sería peor que la
función que las genera. Están en `indice.json` bajo `parametricos_por_codigo`.

| Pieza | Dónde está | Notas |
|---|---|---|
| Corredera telescópica de bolas | `ArmarDesdeRender.forma_corredera_bolas(tbm, largo)` | Tres tramos, 45 mm de alto, 12,7 de espesor cerrada. Marco: origen en el frente del riel sobre la cara del lateral, X hacia atrás, Y arriba, Z hacia el cajón. **Se dibuja una sola vez, del lado del lateral** — incluye los tres miembros. Verificada contra foto el 29/09/2026; antes eran dos piezas mal dibujadas (canal + barra). |
| Tira LED | `ArmarDesdeRender.forma_led(tbm, largo)` | Perfil de aluminio 9×9 con difusor. **Sin verificar contra el herraje real.** |
| Receptor Ø10 | `PonerHerrajes._forma_receptor(tbm, recibe)` | Sin verificar. |

---

## Archivos de referencia (no se usan para armar)

| Archivo | Qué es |
|---|---|
| `ref_bisagra_hafele_311-04-239_ABIERTA.step` | El original de Häfele, abierto a 90°, en su marco de fábrica |
| `perno_expansor_hafele_262-09-313.step` | Perno original de Häfele, eje sobre X |
| `placa_base_bisagra_hafele_311-71-500.step` | Placa base de bisagra de Häfele, recta. La real de la fábrica es **cruciforme** y viene puesta en la bisagra. |
| `tira_led_hafele_833-76-303.step` | Tira LED de Häfele, 104 × 5 × 1,4 mm |
| `ref_excentrica_dibujada.step` | La excéntrica que habíamos dibujado antes de tener la de Häfele |

---

## Herrajes que faltan modelar

Aparecieron en las fotos del 29/09/2026 pero **no están en el 3D ni en el
archivo de GuiGui**:

- **Pistón a gas** (marca Bronze) — para puertas que levantan. Falta saber dónde
  se usa y con qué fuerza (60N / 80N / 100N).
- **Escuadra de unión** — ángulo metálico con tapa plástica. Va atornillada, no
  lleva agujeros de CNC, por eso no aparece en el corte.

---

## Comparación visual

El cuadro con el dibujo del 3D al lado de la foto del herraje real está en
Figma: https://www.figma.com/design/FBehv5P3VSuDUbLplOPRit
