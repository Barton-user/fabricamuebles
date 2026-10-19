# COCINA-01 — la cocina de JUJUY — paquete de producción

Fusion: documento **`COCINA-01`**, proyecto y carpeta **`cocina`** (guardado 18/10/2026 con la versión final).

Generado el 29/09/2026 desde `recetas/cocina01.py` → Fusion `COCINA-01` (proyecto cocina) →
`ExportarPiezas` → `etapa2/`. Basado en las medidas del modelo de render `COCINA`.

**Regenerado el 18/10/2026** con el diseño nuevo (como el render verde con vitrinas y cobre): sin
lavavajillas, cajonera 450 + B4 bajo tacho 322, alacenas de 1450 a 2450 (techo a 2470) **sin cenefa ni cornisa** (LED embutido) y con
**travesaño trasero 18×80 para colgarlas**, A3/A4/esquinero vitrinas, A2 rebatible, tiradores Ø5
pasantes, receptor Ø5×12, placa base 37/±16.  Los archivos del paquete viejo que ya no
corresponden quedaron en `salida/_obsoleto_18-10/`.
**Vitrinas (18/10, versión final):** marcos de **4 piezas de madera maciza de 18** (montantes 60,
travesaños 70) unidos con Minifix + tarugo Ø8; vidrio de 4 en ranura 12 × 5 por atrás; cruz de
listones 25 × 8 pegada al vidrio (a mano). Todo lo perfora la SKH-612. **Las 16 piezas de madera
están en `lista_corte.csv` con material "Madera maciza" y aparte en `lista_corte_MADERA_MACIZA.csv`:
no cargarlas en AutoCUT** (eso es sólo para la placa). **108 placas.**

## Qué hay acá

| Carpeta / archivo | Para qué |
|---|---|
| `salida/XML3/` | **Perforadora SKH-612HS** — cargar con Formato **KDTXml** (108 piezas) |
| `salida/MPR/` | alternativa: Formato **Haomai MPR** (97 archivos, con los `K` de cara trasera) |
| `salida/BAN/`, `salida/XML1/` | otros formatos (la SKH-612HS no lee BAN) |
| `salida/lista_corte.csv` / `.xlsx` | **AutoCUT → sierra HP280** (108 piezas) |
| `salida/HOJAS_VERIFICACION.html` | plano acotado de cada pieza con mecanizado, para imprimir y medir |
| `piezas.json` | lo que Fusion leyó del sólido (entrada de etapa2) |

## Muebles (108 placas: 100 de melamina + 8 de madera maciza)

B1 esquinero bajo diagonal · B2 bajo pileta 600 (frente fijo + 2 puertas) · B3 cajonera 450
(4 cajones) · **B4 bajo tacho 322** (una puerta, para tacho extraíble de módulo 300) · P1/P2 paneles terminales · A1 esquinero
alacena diagonal **vitrina** (1 puerta de 633) · **A2 alacena 600 rebatible** (dos hojas rebatibles hacia
arriba, 38/62; **sin piso**, abierta sobre la bacha, con escurreplatos; listón frente con el LED y travesaño trasero inferior) · **A3 vitrina 800** (2 puertas de
397) · **A4 mueble campana 570** (pared corta, 1794–2450, puerta ciega, campana SDC-100 colgada debajo, ducto Ø150 a la salida de aire) · zócalos. Vitrinas = marcos de madera maciza. Alacenas sin cenefa ni cornisa; travesaño trasero para colgar.
Cuerpos BLANCO 18, frentes/paneles/zócalos VERDE 18, fondos 5 en ranura 6×6.

## Herrajes (para comprar)

| Herraje | Cant. |
|---|---|
| 3 en 1 / Minifix (excéntrica Ø15 + perno 33 rosca madera, receptor Ø5×12 sin taco) | 122 (106 cuerpos + 16 marcos) |
| Bisagra de cazoleta Ø35 Grupo Euro (tornillos a 48) con base (37 / ±16) | 27 |
| Corredera de bolillas 450 (pares) | 4 pares (8 rieles) |
| Soporte de estante Ø5 | 32 |
| Pata regulable 100 | 17 |
| Tirador barral cobre 128 e.c. | 11 |
| Perilla cobre | 3 |
| **Escurreplatos Bronzen LC-560** (564×270, 2 rejillas, inox, MLAU156309472) | 1 — se atornilla a los laterales de A2 (Ø3 a mano); alturas supuestas 280/130 bajo el estante fijo |
| **Cubiertero colgante 3 compartimentos Toly Poken** (MLA2121276022) | 1 — colgado de la rejilla de abajo; medidas supuestas 240×120×140 |
| **Bacha Tawak Delta Simple 55** (55×46×22, acero 304, sobre mesada, MLA80311064) | 1 — calado de mesada supuesto 530×440, confirmar con la plantilla |
| Vidrio 4 mm | 535×879 · 2 × 299×879 |
| **Campana Serie Dorada SDC-100** extensible 60 (600×194×284, Ø150, MLA47228749) | 1 — colgada bajo el piso de A4, boca a 1600 |
| Ducto Ø150 flexible + codo + abrazaderas, hasta la salida de aire (Y 1120 / Z 2120) | 1 |
| Tarugo Ø8 × 30 | 16 |
| Listones 25 × 8 para las cruces (2×3 por puerta) | 4 puertas |
| Junquillos para el vidrio | 4 puertas |
| Pistón a gas para rebatible (A2): 2 × 60 N para la hoja de arriba 597×379, 2 × 80–100 N para la de abajo 597×615 | 4 |
| Perfil de aluminio con difusor para LED embutido | 4 tiras |
| Tornillos a la pared por travesaño trasero | 2 por alacena (4 en el esquinero) |
| Tira LED (mm) | 516 · 524 · 724 · 494 (la de 494 va pegada, sin ranura) |
| Colgador de alacena regulable | 8 (sin perforación hasta medir el modelo) |
| Clips de zócalo | según patas |

## Mueble campana A4 (18/10)

A4 es ahora un mueble corto **1794–2450** con puerta ciega y **frente de campana** hasta 1450 (fijo 567×149,5 con
escuadras al piso + móvil 567×188,5 atornillado al visor, que se mueve con él) para que el frente quede parejo
con las vitrinas ("campana oculta"); la **campana extensible SDC-100** (600 ancho) va
atornillada bajo el piso con el visor a ras de la puerta, boca a 700 sobre la mesada (gas). Asoma 15 mm por
lado (el mueble mide 570). El ducto Ø150 sube por adentro y entra a la **salida de aire existente** (Ø150,
centro a 2120 del piso y 1120 de la pared larga) con un codo. Pasos de 170×170 en el piso y en el fondo y
de 180×180 en el estante: **a caladora o router, no salen en los archivos de la perforadora.** La posición
de la salida de la campana (150 de la pared) está supuesta: confirmar con la campana en mano.

## Columna en el rincón (18/10)

En el rincón entre las dos paredes hay una columna que sale **60 de la pared corta y 180 de la pared larga**,
de piso a techo. Los dos esquineros (B1 y A1) llevan el rincón recortado **65 × 185** en piso, techo y
estantes (contorno de 7 vértices: el chanfle a 45° más el rincón); los fondos arrancan después de la columna
(Fondo A desde X = 65, Fondo B desde Y = 185) y las ranuras de fondo salen abiertas al rincón; los travesaños
de colgar de A1 también arrancan después de ella. La mesada lleva el recorte. El rincón se corta con la
sierra (dos cortes) o el router, igual que el chanfle.

## Viga en la pared larga (18/10)

Hay una viga de 120 de saliente desde 2160 hasta el techo (2470), de punta a punta en la pared de la
bacha. A1, A2 y A3 llevan **escotadura de 125 × 277** atrás-arriba en los laterales (y en el Fondo B del
esquinero), el techo arranca a 125 de la pared, el fondo de 5 termina a 2152 y la viga queda a la vista
adentro; el travesaño de colgar va **atornillado a la viga**. Los pines de estante que caían en la
escotadura se omitieron (una posición menos arriba de todo, en la columna de atrás). A4 (pared corta)
no cambia. El corte de la escotadura lo hace la sierra (dos cortes) o el router; en el XML3 va como
contorno de 6 vértices.

## Orden de trabajo para los esquineros (piso, techo y estantes con chanfle)

1. La sierra corta el **rectángulo** (782 × 782 y 750 × 750).
2. **Perforar antes de hacer el chanfle**: así la placa entra entera a la máquina y las
   esquinas de referencia están.
3. Chanfle a 45° a mano (la hoja de verificación muestra el contorno con cotas).
4. Canto del lado diagonal a mano (no figura en la lista de corte).

## Lo que queda SIN verificar

- **Canto de 1 mm** supuesto: si es otro, hay que regenerar la lista de corte.
- **Mecha Ø3** de los agujeros de corredera (32 agujeros: 16 en los laterales, 16 en cara B
  de los costados de cajón): la máquina no tiene Ø3. Igual que en COCINA MLV.
- **Mecha Ø6** de tornillos de bisagra y de base (108 agujeros): hoy se pasa a Ø5 (T162) en la máquina.
- **Ø15 / Ø10 en cara B** (16 excéntricas de los pisos de bajo mesada y esquineros, 8 receptores
  de cenefa): confirmar que el paquete de abajo tiene esos diámetros.
- **Cazoleta Ø35**: sigue fresada con la Ø20 (T184) hasta que llegue la mecha.
- La **ranura LED 10 × 10 en cara B** (3 pisos de alacena) usa la T11; no se probó a 10 de
  profundidad.
- El montante a 45° del esquinero va unido con 3 en 1 al piso y al techo; no se armó nunca.
- Los zócalos se ajustan en obra (encuentro a 45°).
- Mueble **diseñado desde cero** (sin GuiGui): primera vez que se fabrica por este camino.

## Controles que sí se hicieron

- Receta vs. lo que Fusion lee del sólido: **108/108 piezas idénticas** (18/10; medidas,
  contorno, cantos, agujeros, ranuras) — `python3 recetas/comparar.py`. `ExportarPiezas`
  ahora ignora cajeados de más de 40 de ancho (`RANURA_ANCHO_MAX`) y sólo estira un Ø8 de canto a
  33 si de verdad desemboca en la excéntrica (los tarugos quedan en 15).
- XML3 releído contra `piezas.json`: 95/95 el 29/09 (no repetido el 18/10).
- Interferencias en Fusion entre placas: ninguna (salvo el encuentro de zócalos); bisagras,
  correderas, soportes, patas y LED contra placas: ninguna.
- Chequeos de la receta: agujeros fuera de placa o pasantes, cruces entre caras, agujeros que
  pisan otros, ranuras o el perno del 3 en 1, ranuras < 10 en cara B, tamaños fuera del rango
  de la perforadora: ninguno.
