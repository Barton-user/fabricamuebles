# ALACENA SPAR (PRUEBA 1) — paquete de producción

Generado el 01/10/2026 **sin GuiGui**: `recetas/alacena_spar.py` → Fusion `ALACENA SPAR`
(proyecto cocina) → `ExportarPiezas` (lee el sólido) → `etapa2/`.
Receta contra sólido: **11/11 piezas idénticas** (`recetas/comparar.py`).

Rehecha desde la "Alacena Spar" de GuiGui (habitación PRUEBA 1, orden 260625-20) con estas correcciones:

| GuiGui | Ahora |
|---|---|
| alto 844,47 (laterales 826,47, puertas 388,06 / 377,53) | **845** (laterales 827, puertas 390 / 376) |
| tapa inferior con excéntricas abajo y ranura arriba (dos caras) | **todo arriba**; listones unidos sólo a los laterales |
| lateral derecho y listón de atrás con todo en cara B | **cara A = la de adentro en todas las piezas** |
| LED 9×9 arriba del techo, pasante | **LED 10×10 abajo de la tapa inferior**, a 60 del frente, 524 de largo (T11) |
| tornillos de bisagra/base Ø6 (no hay mecha → crashea) | **Ø5** (T162). Volver a 6 cuando se monte la Ø6 |
| canto sólo al frente de laterales y listones | también **abajo** (se ven desde abajo) |

## Qué hay acá

| Archivo | Para qué |
|---|---|
| `salida/XML3/` | **SKH-612HS** — Formato **KDTXml** (11 archivos, nombre = código) |
| `salida/MPR/` | alternativa: Formato **Haomai MPR** |
| `salida/lista_corte.xlsx/.csv` | AutoCUT (⚠️ mapeo de AutoCUT todavía roto, ver CONTEXTO §18) |
| `etiquetas/etiquetas_60x40.pdf` | **AIBAO**, una por página · `etiquetas_A4.pdf` para probar |
| `etiquetas/piezas_autocut.csv` | lista con el código limpio de 13 dígitos |
| `etiquetas/lista_materiales.xlsx` | piezas, herrajes, m² por material |
| `salida/HOJAS_VERIFICACION.html` | plano acotado de cada pieza, para medir la primera |

## Piezas (medida de CORTE = terminada − canto 1 mm)

| # | Código | Pieza | Material | Corte | Canto |
|---|---|---|---|---|---|
| 1 | 9992610010023 | Lateral der | GRIS 18 | 826 × 399 | frente + abajo |
| 2 | 9992610010030 | Lateral izq | GRIS 18 | 826 × 399 | frente + abajo |
| 3 | 9992610010061 | Listón atrás | GRIS 18 | 564 × 97 | abajo |
| 4 | 9992610010054 | Listón frente | GRIS 18 | 564 × 97 | abajo |
| 5 | 9992610010047 | Tapa inferior | GRIS 18 | 564 × 399 | frente |
| 6 | 9992610010078 | Estante (fijo) | GRIS 18 | 564 × 376 | frente |
| 7 | 9992610010016 | Techo | GRIS 18 | 598 × 399 | frente + 2 costados |
| 8 | 9992610010085 | Fondo | BLANCO 5 | 721 × 574 | — |
| 9 | 9992610010092 | Puerta der | PET GRIS 18 | 388 × 295 | 4 lados |
| 10 | 9992610010108 | Puerta izq | PET GRIS 18 | 388 × 295 | 4 lados |
| 11 | 9992610010115 | Puerta rebatible | PET GRIS 18 | 595 × 374 | 4 lados |

Herrajes: 16 tres en uno (excéntrica + perno 33 + receptor), 6 bisagras cazoleta Ø35 Grupo Euro,
1 tira LED 524, **2 pistones a gas Bronze** para la rebatible (a mano, sin CNC).

## 3 · Sierra HP280 — corte manual en `editar` (placas 1832 × 2601)

`VolOrig` → `MatRes` → `editar`. Placa: **Longitud 1832 · Ancho 2601** (el empujador consume el
lado de 1832; las tiras salen de 2601). Kerf 4,4 · Trim 5.

**PET GRIS 18** — nivel 1: tiras **388** ×1 y **374** ×1 → nivel 2 (girar la tira, Longitud 2601):
de la de 388 → **295 ×2**; de la de 374 → **595 ×1**. Sobra una placa de ~1830 × 1056.

**GRIS 18** — nivel 1: tiras **399** ×1 y **564** ×1 → nivel 2:
de la de 399 → **826 ×2 + 598 ×1**; de la de 564 → **399 + 376 + 97 + 97**.

**BLANCO 5** — tira **574** → **721 ×1**.

Pegar la etiqueta apenas sale cada pieza (las medidas de corte están en la etiqueta).
Medir la primera de cada material con cinta antes de seguir.

## 4 · Perforadora SKH-612HS

1. Encendido normal (CONTEXTO §7). Pendrive → `salida/XML3/`.
2. Tipos completados → carpeta → Cargar archivo → **Formato = KDTXml** (hay que cambiarlo cada vez).
3. Escanear el código de la etiqueta (o tipearlo) → doble clic en la fila.
4. **Leer la tabla fila por fila** antes de dar verde:
   - Ø35 → la resuelve sola con la **T184** (fresado). Ø5 → **T162**. Ranura 6 → **T187**.
   - Tapa inferior: ranura 10×10 de **cara dorso** → **T11** (primera vez a 10 de profundidad).
   - Ninguna fila con "Motivo no procesado".
5. **Todas las piezas van con la cara de ADENTRO del mueble hacia arriba** (cara A).
   Las puertas: cara interior arriba (la de las cazoletas).
6. Generar → verde dos veces.

**Primera pieza: Puerta der (9992610010092).** Medir: cazoletas Ø35 a **22,5** del canto de
bisagras, a **100 y 290** del canto de abajo; tornillos Ø5 a 37 del canto, ±24 de cada cazoleta.
Después la **tapa inferior**: confirmar que la ranura LED queda abajo a **60 del frente**
(si sale a 60 del fondo, la cara B está espejada y hay que avisar).

## Sin verificar

- Espesor real del canto (se supuso 1 mm en todo, también en el PET).
- Ranura de 10 de profundidad en cara dorso con la T11.
- Pistón de la rebatible: fuerza y posición (no está en el diseño).
- Colgadores de la alacena y salida del cable de la LED: no están en el diseño.
- Primer mueble que sale entero por el camino Fusion: la geometría está verificada contra la
  receta, pero todavía no se armó ninguno así.
