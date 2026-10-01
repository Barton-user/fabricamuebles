# Curvado por ranuras (web `curvado/`)

_La web para piezas curvadas por ranurado. Detalle técnico en `curvado/README.md`._

_Movido tal cual desde `CONTEXTO.md` el 01/10/2026. Las referencias "§N" dentro del texto son a la numeración vieja de `CONTEXTO.md`: cada sección vieja dejó allí una línea 📦 que dice adónde fue. Si algo de acá contradice a `CONTEXTO.md`, manda `CONTEXTO.md`._

---

## 20. Curvado por ranuras — web `curvado/` (26–27/09/2026)

Web para diseñar piezas curvadas por ranurado (kerf bending) y sacar todo el paquete de
producción. Vite + three.js + jsPDF, **corre entera en el navegador** (sin backend).
Código en `curvado/` (ver `curvado/README.md`). Publicada en **Vercel, equipo LeitenTeam**,
proyecto importado de `Barton-user/fabricamuebles` con **Root Directory = `curvado`**, framework
Vite. Cada push a `main` que toque `curvado/` se publica solo.

### Qué hace

- **Entrada**: placa (material, espesor nominal y **real**, piel, alto, cantos, veta) y perfil en
  tramos: rectos + curvas (radio **sobre la cara vista**, ángulo, **convexa/cóncava** por curva,
  cantidad de ranuras automática o forzada). Presets: mostrador, esquina R100, medio círculo,
  onda S, cóncava. Deslizadores + número en espesor, piel, alto, largo, radio, ángulo y ranuras.
- **Cálculo** (`src/motor.js`): línea de desarrollo = plano medio de la piel.
  `Rm = R ∓ s/2`, largo de curva `Rm·θ`; ranuras mínimas (convexa) `θ·(t − s/2)/(w·cierre)`;
  por facetado, tramo recto entre ranuras `≤ √(8·Rm·flecha)`; piel `ε ≈ s/2Rm` contra un límite
  orientativo por material; costilla mínima. Cóncavas: las ranuras se abren.
  V: `N = ⌈θ/β⌉`, boca `plano + 2(t−s)tan(β/2)`.
- **Herramientas** (la forma de la ranura la define la fresa elegida): recta (corte
  descendente/ascendente/compresión), punta redonda (esférica / media caña), V (con o sin fondo
  plano), disco. Tablas editables por máquina + **catálogo de medidas comerciales**
  (`src/catalogo.js`: Whiteside MD 6×22…10×38, Amana 46456 esférica Ø6×22, media caña métrica,
  V de grabado 6 mm 15–60°, V de insertos 40–90°, V de plegado con fondo plano Amana
  RC-1172 / RC-1175).
- **Vistas**: 3D con curvado en **loop** (pausa, deslizador, ⇄ lado, 🔍 ranura, ⌖ Centrar /
  doble clic, ⟲ Inicial; la pieza se mantiene centrada), detalle de una ranura plana y curvada
  con cotas, planta curvada contra el perfil objetivo, plano de taller. Todo en una pantalla
  (formulario en pestañas Pieza / Perfil / Ranurado / Máquinas).
- **Paquete .zip** (carpeta = código `999MMDDhhmmss`):
  - `SIERRA/lista_corte.csv|xlsx` → AutoCUT (mismas columnas que `listacorte.py`)
  - `PERFORADORA/XML3/<código>.xml` (KDTXml, TypeNo 3 cara A / 13 cara B) y `MPR/<código>.mpr` (+K)
  - `ROUTER/<código>_ranuras_T<n>.nc` (+ contorno opcional), dialecto GuiGui: Z0 mesa, Z = piel
    en el fondo, Z38, CRLF, sin encabezado (preset Syntec con `T M06 / M03` opcional). Entra y
    sale fuera de la placa, pasadas de profundidad configurables.
  - **`<código>_hoja_de_taller.pdf` A4 (4 hojas)**: pieza y programas, plano y ejes de ranura,
    cómo queda curvada, cómo se apoya en la HP280 y en la máquina elegida, pasos sierra →
    ranurado → cantos (HH-509R) → plegado, tabla de control final.
  - planos SVG, captura 3D, `LEEME.txt`.
- **Validación**: los escritores JS (`src/exportar.js`) son puertos de `etapa2/xml3.py`,
  `mpr.py`, `listacorte.py`: `npm test` + `python3 curvado/test/validar.py etapa2` → 6/6 iguales.

### Decisiones tomadas

- Perforadora: ranuras en **cara A** (husillos superiores) = placa con la **cara vista contra la
  mesa**; profundidad = espesor **real** − piel (Z0 en la cara). Cara B sólo con T11 Ø10 → poco útil.
- Router: fondo en **Z = piel desde la mesa** → la piel sale exacta aunque varíe la placa.
- Fuera de la SKH-612HS: ranura en V (no la hace); pieza fuera de 250–5000 × 50–1200 o
  espesor fuera de 10–48 (manual SKH-612H).
- Tip de catálogo: la **media caña con mango ½″ no llega a 16 mm** (baja 7–10,5); en 18 mm la
  punta redonda útil es la **esférica Ø6×22**. De las V de grabado de 6 mm sólo la de 15° llega.

### Lo que FALTA (en orden)

1. **Medir en el taller** y cargar en la tabla de la web:
   - profundidad máxima real del disco **T183** (Ø43,9 × 3);
   - herramientas reales del **router SKG-912MZ** (T1 Ø6 sigue sin cargar en el almacén;
     ¿hay V? ¿esférica?) y su largo de corte;
   - **mesa útil** del router (quedó 1250 × 2500 como supuesto).
2. **Probetas por material** (MDF, aglomerado, multilaminado, MDF crudo): ranurar un retazo,
   curvarlo y ajustar piel mínima y el límite `epsMax` de `MATERIALES` en `src/motor.js`.
3. **Primera pieza real** por perforadora y por router: medir piel, eje de la 1ª ranura desde
   INICIO y cantidad; confirmar que MH2026 asigna la herramienta esperada al ancho de ranura.
4. **Cantos en zona curva**: probar si el canto de arriba/abajo pegado antes de plegar se arruga;
   si pasa, cambiar el paso 3 de la hoja de taller (pegar después de plegar o cubrir con tapa).
5. **Tapas / molde**: generar desde la misma web el piso y el techo con el contorno (router,
   `.nc` de contorno curvo) — hoy la hoja sólo da el radio del molde.
6. Mapeo de AutoCUT (§18) sigue pendiente: afecta también a esta lista de corte (código limpio
   para la etiqueta).
7. Opcional: el `.nc` de ranuras con cambio de herramienta Syntec validado en la máquina.

> **Git**: el sandbox de Claude no puede borrar archivos en la carpeta; cuando hace `git status`
> suele quedar un `.git/index.lock` vacío. Antes de commitear: `rm -f .git/index.lock`.

---
