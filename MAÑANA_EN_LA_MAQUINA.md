# Hoja para la próxima visita al taller

_Actualizada el 01/10/2026. Imprimir y tildar. Lo que se descubra se anota acá al lado y después
se pasa a `CONTEXTO.md` / `docs/` (ver reglas en `CONTEXTO.md` §8). La versión anterior de esta
hoja (22/09) está en el historial de git._

**Llevar:** pendrive con la carpeta `PENDRIVE/` entera · **calibre** · una bisagra Grupo Euro y su
placa base · celular para fotos · un recorte de 18 de al menos 400 × 600 · esta hoja.

---

## A · Antes de prender nada (5 min)

- [ ] **Variador del husillo de arriba** (gabinete eléctrico, Delta MS300): ¿en qué quedó? _______ Hz
      (100 = cazoletas · 300 = ranurar).
- [ ] **¿Hay un segundo variador** en el gabinete (para el husillo de abajo)? Sacar foto de los dos.
- [ ] **Revista de conos, puesto 6 (T186)**: ¿hay cono? ¿con qué herramienta? _______________
- [ ] **T187 (puesto 7)**: sacar el cono y mirar la herramienta. ¿Es **fresa** (corta de costado,
      punta plana o con filos laterales) o **mecha** (punta de centrado y espuelas)? Foto. _______
- [ ] Aire: manómetro **≥ 0,7 MPa** · vaciar el vaso del filtro · purgar el tanque.

## B · En la PC de la perforadora (antes de mecanizar)

- [ ] **Backup**: `D:\DiskC-(versión)` → comprimir la carpeta entera → copiar al pendrive.
      **Hacerlo antes de tocar cualquier cosa.**
- [ ] **Tabla de herramientas**: capturar las **filas 15 a 27** (Parámetro → Configuración de
      paquete). El manual dice 12 verticales arriba y contamos 9: ¿aparecen las otras 3? ____
- [ ] **Poner en hora el reloj** de la PC (está ~13 h adelantado).
- [ ] **Programa de calentamiento** después de prender ("Configuración de máquina" → "Programa de
      calentamiento", ~1 min).

## C · Pruebas en la perforadora

Las cuatro primeras son las de la Etapa 0 que nunca se anotaron. Para todas: **leer la tabla fila
por fila antes de dar verde**, formato **KDTXml**.

- [ ] **1. Medida terminada vs. de corte + espejado** — `1_DESDE_GUIGUI/XML3/9441838670057.xml`
      (techo 400 × 600). Cortar el recorte a **400 × 600 exacto**. Medir con calibre:

      | Qué | Esperado | Medido |
      |---|---|---|
      | X del primer agujero Ø10 (desde el borde de referencia) | 40,0 | |
      | X del último | 360,0 | |
      | Y del primero | 9,0 | |
      | Y del último | 591,0 | |
      | Ranura de 6: distancia al borde (si salió del lado opuesto, hay espejado) | anotar de los dos lados | |

      Si los agujeros caen corridos justo el espesor del canto → la máquina espera la pieza ya
      canteada (o compensa). Si la ranura sale del otro lado → espejado.
- [ ] **2. ¿Lee el atributo de cantos `EdgeFBLR`?** — mecanizar la fascia **`9441838670156`** de
      **`1_DESDE_GUIGUI/XML3`** y de **`2_DESDE_FUSION/XML3`** (dos recortes de la misma medida).
      ¿Salen iguales? ____
- [ ] **3. Fusion vs. GuiGui** — con lo de la prueba 1 y 2 alcanza; si sobra tiempo, otra pieza de
      los dos juegos. ¿Iguales? ____
- [ ] **4. Pieza curva R50** — `3_PIEZA_CURVA/XML3/6893155441217.xml` (lateral 350 × 500).
      ¿Hace bien el contorno? ____
- [ ] **5. Cazoleta con la Ø35 medida y fotografiada** (para el instructivo): Ø real ____ ·
      profundidad real ____ (pedido 13).
- [ ] **6. Horizontal Ø8 por la escotadura del uñero** (50 × 70) — lateral de la Cajonera de
      COCINA MLV, si se llega. ¿Entra el husillo? ____

## D · Campana / placa prensora

- [ ] Fresar algo con la T184 o la T187 y mirar: **¿baja sola?** ____ (Según el manual se acciona
      con **M64 / M65**.) Si no baja, sacar foto de la pantalla de CncMon32 mientras fresa
      (botón "M" → ver si hay un botón de "placa de la fresa").

## E · Mantenimiento (si hay tiempo)

- [ ] **Engrase** con Klüber Isoflex Topas L32-N: **arriba 2 picos principales + 4 de los
      horizontales, abajo 1 principal**. Una inyección por pico.
- [ ] Marcar las 12 tareas: Mantenimiento → "Mantenimiento de equipos" → permiso (probar `520`) →
      **"Actualizar"**. ¿Funcionó el 520? ____
- [ ] Guías aceitadas (si no: CncMon32 → botón "M" → "Lubricant").

## F · En el banco, con calibre — la bisagra

- [ ] **Centro de la cazoleta → línea de los dos tornillos**: ______ mm (esperado **6**).
- [ ] **Entre tornillos** (a lo largo del canto): ______ mm (esperado **48**).
- [ ] **Placa base cruciforme**: distancia de sus dos agujeros al **frente** del lateral, con la
      bisagra armada como va: ______ y ______ mm (hoy usamos **20 y 52**).
- [ ] **Perno del 3 en 1** Grupo Euro: largo ______ (¿33 o 34?).
- [ ] **Canto real**: espesor ______ mm (hoy suponemos 1).

> Si la bisagra no da 6 / 48, cambiar **sólo** `herrajes/medidas.json` y regenerar.

## G · En la PC de la sierra (AutoCUT)

Llevar `PENDRIVE/4_ALACENA_SPAR/lista_corte.xlsx` (ya trae la columna nueva **`条码`**).

- [ ] Importar → "Importar varios materiales" → **"Coincidencia"**: **sacar foto ANTES de cambiar**.
- [ ] **`条码` → campo de código de barras** de la etiqueta.
- [ ] **`开料长` / `开料宽` → largo / ancho de corte**, sin restar cantos otra vez.
- [ ] **`订单号` → "工程"** (proyecto).
- [ ] Guardar el perfil. Probar con una etiqueta: el código tiene que ser el largo (no `P01`).
- [ ] Probar con el techo de PRUEBA 1: tiene que salir **598 × 399**.
- [ ] Si quedó bien: **volver a cortar las 7 piezas del gris**.

## H · Traer de vuelta

- [ ] El backup de `D:\DiskC-…` en el pendrive.
- [ ] Fotos: variadores, revista (puestos 6 y 7), T187, tabla filas 15–27, pantalla de
      "Coincidencia" de AutoCUT (antes y después), la cazoleta medida, la bisagra con el calibre.
