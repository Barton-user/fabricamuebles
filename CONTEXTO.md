# FÁBRICA MUEBLES — Contexto técnico del proyecto

_Última actualización: 01/10/2026 — armado con Claude durante la puesta en marcha de la línea._

> **Cómo retomar con Claude**: abrir un chat con esta carpeta conectada y decir
> "leé CONTEXTO.md y seguimos desde el punto X".
>
> **Estado del proyecto → sección 15. Hoja de ruta (objetivo y etapas) → sección 16. MCP de GuiGui y modelos 3D bajados → sección 17. Web de curvado por ranuras (`curvado/`, Vercel) → sección 20. Herrajes Häfele equivalentes → sección 23. Respuestas de Huahua del 30/09 (y la Ø35 frenada) → sección 26. Alacena Spar por el camino Fusion → sección 27. 🔩 Bisagra real 48/6 (tornillos a 6 de la cazoleta) → sección 28. ✅ T184 = mecha Ø35 para cazoletas (variador a 100 Hz) → sección 29.**


> ### ✅ Vigente al 01/10/2026 — confirmado por Pato (manda sobre cualquier sección de abajo)
>
> - **Cazoleta Ø35**: mecha **FUL Ø35 × 70 R** comprada y montada en el cono de la **T184**
>   (tabla: diámetro 34.8 · ancho 34.8 · Z 27 · avances 5000/500/250). Ver §29.
> - **Variador del husillo (Delta MS300) quedó en 100 Hz ≈ 6000 rpm.** Así está bien para
>   cazoletas; **para ranurar con la T187 o la T11 hay que volver a 300 Hz**.
> - **Tornillos de bisagra: Ø5 para siempre.** La mecha Ø6 **no se compra**.
> - **Bisagra Grupo Euro: tornillos a 6 mm del centro de la cazoleta (48/6), no 14,5** — es la
>   medida vigente, pero **falta confirmarla con calibre** sobre la bisagra. Ver §28.
> - Lo que diga lo contrario más abajo (§5, §15.5, §19–22, §24, §26.2) es historia.

---

## 0. Objetivo y etapas

**Etapa 1 (en curso)** — poner en marcha el flujo completo de producción de muebles de placa:
diseño → despiece → corte → etiquetado → perforado → cantos → armado.

**Etapa 2 (EN CURSO — generador de archivos de máquina ya funcionando)** — **reemplazar GuiGui**. El software es malo:
UI rota (textos superpuestos, mezcla chino/inglés, layout que no se adapta), configuración
atada a un servidor en China, verificación por SMS en cada cambio, bloqueos arbitrarios.
La idea es construir algo propio: una aplicación, un iLogic para Inventor, un plugin para
Fusion, o un generador independiente. **Por eso este documento describe los formatos de
archivo de cada máquina con ejemplos literales**: son la especificación de salida que
cualquier reemplazo tiene que cumplir. Si se generan esos archivos correctamente, las
máquinas no se enteran de que GuiGui desapareció.

> **Estado 20/09/2026**: el generador existe y está validado. Ver la **sección 13**.
> Lee el `Mass production.json` y emite `.ban`, `.mpr`, XML1, XML3 y la lista de corte
> de la sierra, todo verificado contra los archivos de referencia de Bluen.
> Carpeta: `etapa2/`.

---

## 1. Parque de máquinas

| Equipo | Modelo | Rol | Control / software | Consume |
|---|---|---|---|---|
| Diseño | GuiGui 柜柜 v5.0.0.4global-9 (Mac) | Diseño paramétrico y despiece | Cliente Electron + nube **bluen.cn** | — |
| Optimizador | AutoCUT | Optimización de corte para la sierra | Windows, PC de la sierra | Excel/CSV |
| Sierra | **HP280** (HUAHUA) | Corte recto seccionadora | Control HUAHUA propietario (gabinete azul) | archivo `.CUT` generado por AutoCUT |
| Router | **SKG-912MZ** | Nesting: corte con fresa, ranuras, agujeros de cara | **Syntec** | `.nc` (código G) |
| Perforadora | **SKH-612HS** | Agujeros en 6 caras, ranuras, fresados | **CncMon32** (Syntec) + **HHcnc** | 1 archivo por pieza, nombre = código de barras |
| Pegadora de cantos | **HH-509R** | Cantos | — (manual) | nada, el operario lee la etiqueta |
| Impresora etiquetas | **AIBAO BC-80152T** | Etiquetas térmicas con QR | Driver solo Windows, instalada en la PC de la sierra | imprime desde AutoCUT o desde el control ("Imp Lbl") |

**Fabricante de la perforadora**: Guangdong Shunde Changsheng Machinery Manufacturing Co., Ltd.
(广东顺德长盛机械), marca comercial **Huahua CNC** — el mismo HUAHUA de la sierra.
Manual: `User Manual_SKH-612 Series_260706_115944.pdf` (series SKH-690 / SKH-612H / SKH-612S).

**Pegadora de cantos HH-509R** — manual: `instructivo/manuales/HH-509R_manual_pegadora_cantos.pdf`
(HUAHUA, *Automatic edge banding series user's manual*, 99 págs, en inglés: ajustes de cada grupo,
panel de control, parámetros, alarmas, mantenimiento y repuestos).

**Contacto proveedor**: Sra. Tan (谭小姐), por WeChat.
**Cuenta GuiGui/Bluen**: verificada por SMS al celular terminado en **2352**.

---

## 2. Flujo de trabajo completo

```
GuiGui (diseño 3D paramétrico del mueble)
   │
   ├─ Output → layout → Start layout   (optimización de despiece, online vía Bluen)
   │
   └─ Output NC file → Export NC file
         │
         └─ escribe en  <destino>/<ORDEN>/BluenNC/
              ├─ saw/开料清单.xls ............ lista de corte  → AutoCUT → .CUT → SIERRA HP280
              ├─ 下料文件/*.nc ............... código G nesting → ROUTER SKG-912MZ
              ├─ <carpeta plantilla>/*.ban ... 1 archivo x pieza → PERFORADORA SKH-612HS
              ├─ new_nc_params.json .......... parámetros del post-procesador
              └─ <ORDEN>-Mass production.json  TODO el layout + geometría (la mina de oro)

Sierra corta las piezas  →  se imprimen y pegan las etiquetas con QR
   ↓
Perforadora: se escanea el QR → busca el archivo cuyo nombre = código de barras → mecaniza
   ↓
Pegadora de cantos (operario lee la etiqueta)
   ↓
Armado
```

**Dos rutas alternativas de corte**: sierra (corte recto, más rápido para piezas rectangulares)
o router en nesting (permite formas irregulares y hace agujeros/ranuras de cara en la misma
operación). Hoy se usa la sierra.

---

> 📦 _«3. Sistema de coordenadas y convenciones (crítico para Etapa 2)» → movida a `docs/FORMATOS.md`._

> 📦 _«4. Formatos de archivo — especificación con ejemplos reales» → movida a `docs/FORMATOS.md`._

> 📦 _«5. Parámetros de herrajes y placa» → movida a `docs/HERRAJES.md`._

> 📦 _«6. Estado actual» → movida a `BITACORA.md`._

> 📦 _«7. Notas de operación de GuiGui / Bluen (aprendidas a los golpes)» → movida a `docs/GUIGUI.md`._

> 📦 _«8. Problemas resueltos (por si vuelven)» → movida a `docs/GUIGUI.md`._

> 📦 _«9. Operación de la sierra HP280 (probada)» → movida a `docs/SIERRA_AUTOCUT.md`._

> 📦 _«10. Lo que FALTA (en orden)» → movida a `BITACORA.md`._

> 📦 _«10-bis. PROTOCOLO DE PRUEBA EN LA SKH-612HS (pendiente — próximo paso)» → movida a `BITACORA.md`._

> 📦 _«11. Preguntas abiertas a HUAHUA (Sra. Tan / 谭小姐, WeChat)» → movida a `BITACORA.md`._

> 📦 _«12. Notas para la Etapa 2 (reemplazar GuiGui)» → movida a `docs/FORMATOS.md`._

> 📦 _«13. Etapa 2 — generador propio de archivos de máquina» → movida a `docs/FORMATOS.md`._

> 📦 _«14. Etapa 3 — diseñar en Fusion, sin GuiGui (VALIDADO 22/09/2026)» → movida a `docs/FUSION_RECETAS.md`._

> 📦 _«15. ESTADO ACTUAL — 22/09/2026» → movida a `docs/FUSION_RECETAS.md`._

# 16. HOJA DE RUTA — hacia dónde va todo esto

_Agregado el 22/09/2026, después de definir el objetivo completo del proyecto._

## 16.1 · El objetivo, en tres frases

1. **Fabricar todo lo modelado en GuiGui**, camino 100 % funcional.
2. **Modelar en Fusion y fabricar con nuestras máquinas**, camino 100 % funcional.
3. **Tienda online** con ~10 modelos, visor y configurador 3D (medidas generales y
   alguna opción, sin salir de la estandarización). Pedido confirmado y pagado →
   se dispara toda la documentación del mueble.

**"100 % funcional" significa siempre lo mismo**: programas de máquina + lista de
corte + **etiquetas** + **manual de armado de 1-2 hojas** (los muebles se entregan
desarmados). Ese conjunto se llama de acá en adelante el **paquete de producción**.

## 16.2 · La idea que ordena todo: un motor, tres entradas

No son tres caminos. `etapa2/` —el modelo `Panel` y sus escritores— **ya es el
motor**. GuiGui (`guigui.py`) y Fusion (`fusion_json.py`) son dos formas de llenar
`Panel`. La web va a ser la tercera. Todo lo que falta (etiquetas, manual, precios)
se construye **una vez, sobre `Panel`**, y sirve para las tres entradas.

Consecuencias:

- **Camino 1 (GuiGui): no invertir más.** Está 41/41. Queda como respaldo. Lo que
  le falta es lo mismo que le falta al camino 2, y se hace una sola vez.
- **Camino 2 (Fusion) es la columna vertebral.** Se cierra sobre metal en la Etapa 0
  y se estresa con muebles distintos después.
- **Camino 3: el configurador NO depende de Fusion en tiempo de ejecución.** Fusion
  es de escritorio y licenciado; correrlo en un servidor cuando entra un pedido es
  caro y frágil. Cada uno de los 10 modelos será una **receta paramétrica en
  código**: una función Python que, dadas medidas y opciones, devuelve la lista de
  `Panel` con sus agujeros. Fusion sirve para **diseñar y validar** la receta (se
  modela el mueble, se exporta, y `validar.py` compara contra lo que da la receta —
  la misma metodología de oráculo de las secciones 13 y 14). El pedido → archivos
  corre puro código, en segundos. El visor 3D dibuja a partir de la misma receta.
- **El manual de armado sale casi gratis**: `PonerHerrajes` ya conoce el grafo de
  uniones del mueble. De ahí se deriva el orden de armado y la vista explotada.

## 16.3 · Las etapas

| Etapa | Qué | Cuándo está terminada |
|---|---|---|
| **0 · Sobre metal** | `MAÑANA_EN_LA_MAQUINA.md`: formato de HHcnc, Fusion vs GuiGui, terminada vs corte, `EdgeFBLR`, veta en AutoCUT, herraje 33 vs 34 | Las 6 preguntas contestadas y anotadas acá |
| **1 · Paquete de producción** | Generador propio de etiquetas con QR (hoy AutoCUT, con el código mal mapeado, §9); manual de armado generado en 1-2 hojas (explotada + pasos por unión + lista de herrajes); ranura de canto resuelta con la Sra. Tan; **fabricar y armar PRUEBA 1 completo** con ese paquete | Caminos 1 y 2 son 100 % funcionales según la definición de 16.1 |
| **2 · Estresar Fusion** | 2-3 muebles distintos de cero: cajonera con correderas, algo con zócalo y patas, estantes regulables. Cada herraje nuevo entra a `PonerHerrajes` **medido**, como el 3 en 1 | Lista real de herrajes de la casa (que después es lista de precios y de compras) |
| **3 · Recetas** | Los 10 modelos como código paramétrico con rangos permitidos y opciones; cada receta validada contra su modelo de Fusion; esquema propio de códigos de barras y nº de orden; costo por m² + herrajes. Sin web: un CLI que dice "modelo 4, 900×2100×450, 2 puertas" y devuelve el paquete | Los 10 modelos producen paquete completo desde la línea de comando |
| **4 · Visor y configurador 3D** | Página con three.js que lee las mismas recetas, deja mover medidas dentro de los rangos, muestra mueble y precio en vivo. Sin carrito. Ya sirve para vender | Se configura y se ve cualquiera de los 10 modelos en el navegador |
| **5 · Tienda y disparo** | Catálogo, carrito, pago (Mercado Pago), y al confirmarse: correr receta → paquete en carpeta de orden en la fábrica → aviso por mail. Panel interno mínimo de pedidos y estados | Un pedido pagado por un desconocido termina en un pendrive listo para la máquina |

Las etapas 0-2 son de taller y código; 3-5 son de producto. **No empezar la 4 ni la
5 antes de tener la 3**: el riesgo es terminar con un configurador lindo que no
puede fabricar nada.

## 16.4 · Antes de todo eso

- ~~**Remoto de git.**~~ ✅ Hecho: `origin` en GitHub (Barton-user/fabricamuebles).
- Decidir el herraje de la casa: **perno 33 o 34** (§15.5).
  - Marca ya definida: **Häfele** (§5). Falta elegir el modelo concreto de 3 en 1 en su catálogo y ver si el perno es de 33 o 34.
- Verificar canto real y kerf real (§5) — condicionan la lista de corte.

## 16.5 · Estado por etapa

| Etapa | Estado |
|---|---|
| 0 | ⏳ se ejecuta 23/09/2026 |
| 1 | ⬜ |
| 2 | ⬜ |
| 3 | ⬜ |
| 4 | ⬜ |
| 5 | ⬜ |

> Actualizar esta tabla al cerrar cada etapa, y anotar en la sección que
> corresponda qué se aprendió.

---

> 📦 _«15.10 · Camino Fusion completo, probado como se va a usar (22/09/2026, noche)» → movida a `BITACORA.md`._

> 📦 _«17. El MCP de GuiGui — explorado el 22/09/2026» → movida a `docs/GUIGUI.md`._

> 📦 _«15. 23/09/2026 — Primera sesión en la SKH-612HS» → movida a `BITACORA.md`._

> 📦 _«16. Sesión del 24/09 — contraseña, cazoletas resueltas, y el husillo trabado» → movida a `BITACORA.md`._

> 📦 _«17. Respuestas de Huahua (24/09) y traducción real de la botonera» → movida a `BITACORA.md`._

> 📦 _«18. TAREA ABIERTA — Corregir el mapeo de AutoCUT (sierra HP280)» → movida a `docs/SIERRA_AUTOCUT.md`._

> 📦 _«19. Mecha Ø35 para cazoletas — qué comprar (24/09/2026)» → movida a `BITACORA.md`._

> 📦 _«20. Lista completa de mechas que faltan (24/09/2026)» → movida a `BITACORA.md`._

> 📦 _«18. 24/09/2026 (noche) — COCINA MLV armada en Fusion desde el `render.json`» → movida a `BITACORA.md`._

> 📦 _«20. Curvado por ranuras — web `curvado/` (26–27/09/2026)» → movida a `docs/CURVADO.md`._

> 📦 _«21. COCINA MLV — control contra GuiGui y unión de los uñeros corregida (27/09/2026)» → movida a `BITACORA.md`._

> 📦 _«21. 🚨 HALLAZGO: en el paquete de arriba NO hay lugar para una Ø35 (28/09/2026)» → movida a `BITACORA.md`._

## 22. 🛒 LISTA DE COMPRA VIGENTE (28/09/2026)

Esta tabla reemplaza a todo lo anterior. Las secciones 19 y 20 quedan como historial.

| # | Qué | Especificación | Estado | Precio | Link |
|---|---|---|---|---|---|
| 1 | **Mecha cazoleta Ø35** | Ø35 · **70 mm** · vástago Ø10 · **DERECHA** · no pasante | 🛑 **FRENADA (30/09)** — no se sabe si va en el husillo o en el paquete; ver §26.2 | **$73.516** (cupón $70.016) | [FUL MBD3570](https://www.mercadolibre.com.ar/mecha-fresa-para-madera-bisagra--35mm-x70mm-derecha-widia/up/MLAU3931773080) |
| 2 | **Mecha vertical Ø6** | Ø6 · 57 o 70 mm · vástago Ø10 · **giro a confirmar** | ⏸ Huahua confirmó (30/09): cambiar la mecha y poner 6 en la tabla. Falta leer **color y largo** de las posiciones 7 y 9 del paquete de arriba | ~$28.000 | [derecha 6×70](https://www.mercadolibre.com.ar/broca-mecha-no-pasante-6-mm-x-70mm-derecha-p-placas-madera/up/MLAU126150590) · [izquierda 6×57](https://www.mercadolibre.com.ar/broca-mecha-no-pasante-6mm-x-57mm-izquierda-p-placas-madera/up/MLAU126142924) |
| 3 | Fresa espiral Ø20 de repuesto | igual a la `Ø20x70R` del puesto 4 | 🕓 no urgente | — | — |
| 4 | Fresa Ø6 para el **router** (T1) | otra máquina | 🕓 otra sesión | — | — |

**No se compra**: fresa de ranurar Ø9 (se cambia el diseño a ranuras de 10 mm, que la T11 ya
hace bien). Ø8 horizontal, Ø10 y Ø15 verticales ya están montadas.

**30/09:** Huahua dio dos respuestas opuestas sobre dónde va la Ø35 y la cuenta de §21 estaba mal →
la compra de la FUL queda frenada hasta que contesten la pregunta cerrada de §26.4.

**Riesgo a cubrir antes de usar la Ø35**: el husillo gira a 18000 rpm y una mecha de tres puntas
Ø35 quiere ~3000. Si Huahua confirma que no se puede bajar, la mecha se quema. Preguntado.

---

> 📦 _«23. Herrajes Häfele equivalentes a los modelados (28/09/2026)» → movida a `docs/HERRAJES.md`._

> 📦 _«24. 🔧 BIBLIOTECA DE HERRAJES — no volver a modelarlos (29/09/2026)» → movida a `docs/HERRAJES.md`._

> 📦 _«25. COCINA-01 — primera cocina diseñada desde cero, por RECETA (29/09/2026)» → movida a `docs/FUSION_RECETAS.md`._

> 📦 _«26. Respuestas de Huahua a las 12 preguntas (30/09/2026)» → movida a `BITACORA.md`._

> 📦 _«27. ALACENA SPAR — primer mueble de GuiGui rehecho en Fusion sin tocar GuiGui (01/10/2026)» → movida a `docs/FUSION_RECETAS.md`._

> 📦 _«28. 🔩 BISAGRA REAL: tornillos a 6 mm de la cazoleta, no 14,5 (01/10/2026) — MEDIDA OFICIAL» → movida a `docs/HERRAJES.md`._

> 📦 _«29. ✅ CAZOLETAS RESUELTAS: la T184 ahora es la mecha Ø35 (01/10/2026)» → movida a `BITACORA.md`._
