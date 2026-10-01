# COCINA-01 — paquete de producción (pedido de prueba)

Generado el 29/09/2026 desde `recetas/cocina01.py` → Fusion `COCINA-01` (proyecto cocina) →
`ExportarPiezas` → `etapa2/`. Basado en las medidas del modelo de render `COCINA`.

## Qué hay acá

| Carpeta / archivo | Para qué |
|---|---|
| `salida/XML3/` | **Perforadora SKH-612HS** — cargar con Formato **KDTXml** (95 piezas) |
| `salida/MPR/` | alternativa: Formato **Haomai MPR** (79 archivos, con los `K` de cara trasera) |
| `salida/BAN/`, `salida/XML1/` | otros formatos (la SKH-612HS no lee BAN) |
| `salida/lista_corte.csv` / `.xlsx` | **AutoCUT → sierra HP280** (95 piezas) |
| `salida/HOJAS_VERIFICACION.html` | plano acotado de cada pieza con mecanizado, para imprimir y medir |
| `piezas.json` | lo que Fusion leyó del sólido (entrada de etapa2) |

## Muebles (95 placas)

B1 esquinero bajo diagonal · B2 bajo pileta 600 (frente fijo + 2 puertas) · B3 cajonera 320
(4 cajones) · P1/P2 paneles terminales · A1 esquinero alacena diagonal · A2 alacena 600 ·
A3 alacena 800 · A4 alacena 570 (pared corta) · zócalos.
Cuerpos BLANCO 18, frentes/paneles/cenefas/zócalos VERDE 18, fondos 5 en ranura 6×6.

## Herrajes (para comprar)

| Herraje | Cant. |
|---|---|
| 3 en 1 (excéntrica Ø15 + perno 33 + receptor Ø10) | 88 |
| Bisagra de cazoleta Ø35 Grupo Euro (tornillos a 48) con base cruz | 27 |
| Corredera de bolillas 450 (pares) | 4 pares (8 rieles) |
| Soporte de estante Ø5 | 36 |
| Pata regulable 100 | 13 |
| Tira LED (mm) | 516 · 524 · 724 · 494 (la de 494 va pegada, sin ranura) |
| Colgador de alacena regulable | 8 (sin perforación hasta medir el modelo) |
| Clips de zócalo | según patas |

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

- Receta vs. lo que Fusion lee del sólido: **95/95 piezas idénticas** (medidas, contorno,
  cantos, agujeros, ranuras) — `python3 recetas/comparar.py`.
- XML3 releído contra `piezas.json`: 95/95 (tipos de operación y medidas de placa).
- Interferencias en Fusion entre placas: ninguna (salvo el encuentro de zócalos); bisagras,
  correderas, soportes, patas y LED contra placas: ninguna.
- Chequeos de la receta: agujeros fuera de placa o pasantes, cruces entre caras, agujeros que
  pisan otros, ranuras o el perno del 3 en 1, ranuras < 10 en cara B, tamaños fuera del rango
  de la perforadora: ninguno.
