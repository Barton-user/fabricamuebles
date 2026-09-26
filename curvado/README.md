# Curvado por ranuras

Página para diseñar piezas curvadas por ranurado (kerf bending) y sacar los
programas de las máquinas de la fábrica. Corre toda en el navegador, sin backend.

- **Entrada**: placa (material, espesor nominal y real, piel, alto, cantos, veta) y
  perfil en tramos: rectos + curvas con radio, ángulo y si la cara vista queda
  convexa o cóncava. El radio se mide sobre la cara vista.
- **Propuesta**: ranuras paralelas (se cierran en las convexas, se abren en las
  cóncavas) o en V (facetado, solo router). Cantidad, paso y costilla automáticos,
  con límite de cierre, flecha máxima y costilla mínima; se puede forzar paso o
  cantidad por curva.
- **Vistas**: 3D con animación plano → curvado, detalle de una ranura (plana y
  curvada, con cotas), planta curvada contra el perfil objetivo, plano de taller.
- **Exportes** (un .zip con todo, o archivo por archivo):
  - `SIERRA/lista_corte.csv|xlsx` → AutoCUT → HP280 (mismas columnas que el 开料清单 de GuiGui)
  - `PERFORADORA/XML3/<código>.xml` (formato **KDTXml**) y `MPR/<código>.mpr` (+`K`) (**Haomai MPR**) → SKH-612HS
  - `ROUTER/<código>_ranuras_T<n>.nc` (+ contorno opcional) → SKG-912MZ, Syntec
  - planos SVG, captura 3D y `LEEME.txt`

## Cálculo

Línea de desarrollo = plano medio de la piel (no cambia de largo al curvar).

| | |
|---|---|
| radio de la línea de desarrollo | `Rm = R ∓ s/2` (convexa / cóncava) |
| largo de la curva desarrollada | `Rm · θ` |
| ranuras mínimas (convexa) | `N ≥ θ · (t − s/2) / (w · cierre)` |
| ranuras por facetado | tramo recto entre ranuras `≤ √(8 · Rm · flecha)` |
| deformación de la piel | `ε ≈ s / (2 Rm)`, límite orientativo por material |
| V | `N = ⌈θ / β⌉`, boca `2 (t − s) tan(β/2)` |

Los límites por material son un punto de partida: **calibrar con probetas**.

## Máquinas (datos de CONTEXTO.md)

- **SKH-612HS**: pieza 250–5000 × 50–1200, espesor 10–48. Ranuras en cara A (husillos
  superiores, cara vista contra la mesa) o B (husillo inferior T11 Ø10). La
  profundidad se mide desde la cara → usa el **espesor real**. Sin fresa en V.
- **SKG-912MZ**: Z0 en la mesa, Z = espesor arriba, Z38 seguro, CRLF, sin encabezado
  (como GuiGui; hay preset Syntec con `T M06 / M03`). La ranura se programa a
  **Z = piel**, exacta aunque la placa varíe. Entra y sale fuera de la placa.
- Tablas de herramientas editables en la página; lo marcado **A CONFIRMAR** hay que
  verificarlo en el taller (T183 profundidad real, herramientas del router, mesa útil).

## Validación

Los escritores (`src/exportar.js`) son puertos de `etapa2/xml3.py`, `mpr.py` y
`listacorte.py`. Se comparan byte a byte:

```
npm test                               # genera test/out/ con el motor JS
python3 test/validar.py ../etapa2      # compara contra el Python → "6 iguales, 0 distintos"
```

## Desarrollo y Vercel

```
npm install
npm run dev        # http://localhost:5173
npm run build      # dist/
```

Vercel: **Add New → Project → importar `Barton-user/fabricamuebles` → Root Directory
`curvado` → Framework Vite** (lo toma de `vercel.json`) → Deploy. Cada push a
`main` vuelve a publicar.
