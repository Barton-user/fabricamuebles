# Woodwork for Inventor — evaluación para reemplazar GuiGui

_20/09/2026. Investigación sobre documentación oficial, manual, help desk y foro del fabricante._

## Veredicto

**Hacer la prueba gratis.** No resuelve el problema solo, pero cubre la parte cara
(modelo paramétrico + herrajes + cantos + BOM) y **deja abierta la puerta exacta** que
hace falta para la SKH-612HS: un post-procesador propio.

---

## El hallazgo que cambia el análisis

W4I tiene una **API de post-procesadores en JavaScript**, y es abierta:

> *"All Post-Processors are open source and can be modified and adapted to your own
> CNC machines and company rules."*

- SDK instalado localmente, con ejemplos y un archivo
  `Woodwork for Inventor Postprocessor API Help.chm` que documenta el modelo de objetos.
- Ruta v16: `C:\Users\Public\Documents\Woodwork for Inventor\2026\v16\SDK\PostProcessors`
- Existe desde la v13. El fabricante también escribe posts a pedido, caso por caso.

**Por qué importa:** ninguna suite comercial soporta taladradoras chinas de 6 caras.
La pregunta correcta no era "¿soporta mi máquina?" sino "¿me entrega los datos de
mecanizado en algún punto donde yo pueda escribir el `.ban`?". La respuesta es sí.

Confirmado además que el `.mpr` de W4I es **descriptivo, no trayectoria** — respuesta
oficial de soporte:

> *"In these files is defined only operation type, hole position, depth and etc.
> Final tool trajectory formation takes place when Woodwop post-processing is performed."*

Eso es exactamente la naturaleza de dato que necesita la perforadora.

Confirmado también: husillos horizontales en **+X, −X, +Y, −Y**, y cada amarre genera
planos de trabajo **Top / Front / Back / Left / Right**. Las seis caras están cubiertas
conceptualmente.

---

## Pipeline completo sin GuiGui

```
Inventor + Woodwork for Inventor
   │
   ├─ CAM  →  post-procesador JS propio  →  .ban por pieza  →  PERFORADORA SKH-612HS
   │
   └─ BOM "Cutting Parts List"  →  CSV  →  AutoCUT  →  .CUT  →  SIERRA HP280
                                              └─ etiquetas QR (ya las imprime hoy)
```

**No hace falta el módulo Nesting.** El Nesting de W4I es *true shape* (algoritmo Deep Nest)
para router. Para seccionadora se usa optimización guillotina, y eso **ya lo tenés en
AutoCUT**. W4I documenta exportación de la lista de corte a optimizadores de guillotina
(Ardis Cutting, Cut Rite); a AutoCUT se llega con el mismo mapeo de columnas que ya usás.

→ La edición que corresponde es **base + CAM**, no la de Nesting.

---

## Qué cubre y qué no

| Necesidad | W4I | Nota |
|---|---|---|
| Modelo paramétrico del mueble | ✅ | es Inventor |
| Biblioteca de herrajes | ✅ | ~150, incluye **Minifix** (excéntrica) y espigas |
| Herrajes auto-posicionados | ✅ | "Smart Hardware" + iMates + multiplicación por geometría |
| Agujeros de herraje | ✅ | por sustracción de cuerpos |
| Cantos por lado, con efecto en medidas | ✅ | espesor **y** posición (encima / hundido) |
| Dirección de veta + sobremedidas | ✅ | afecta el tamaño del bruto |
| Lista de corte / BOM | ✅ | Excel, plantillas editables |
| Optimización guillotina | ❌ | exporta a optimizador externo → **AutoCUT** |
| Nesting true-shape (router) | ✅ | módulo aparte, **no lo necesitás** |
| Archivo CNC por pieza | ✅ | uno por pieza del ensamble |
| **Nombre de archivo = código de barras** | ❌ | *"For now, it is impossible to do that"* |
| Códigos de barras / QR en etiquetas | ❓ | sin documentación pública |
| Soporte a taladradoras de 6 caras | ❌ | el producto es router-céntrico; **el post lo escribís vos** |
| API para leer datos CAM desde Inventor | ❌ | no existe hoy; sólo "planes" (abr-2025) |

### Los dos problemas reales, y su tamaño

**1. Nombre de archivo.** La perforadora busca el archivo por el código de barras. W4I hoy
no deja configurar el nombre. Workaround ya usado por otros usuarios: renombrado posterior
por script. Mapear *part number → código de barras* es un script de veinte líneas.
**No es bloqueante.**

**2. El post-procesador lo escribís vos.** Es trabajo, pero es el trabajo chico: el formato
`.ban` ya está especificado y validado 12/12 en `etapa2/`. El post JS tiene que emitir lo
mismo que ya emite el generador Python. **Semanas, no meses.**

---

## Condiciones comerciales

- **Precio: no publicado.** El fabricante declara *"three pricing zones"* según país.
- Única referencia pública: un revendedor sudafricano, **ZAR 17.995 ex VAT ≈ USD 1.000**,
  una sola zona, sin aclarar si es perpetua o anual. **No extrapolable a Argentina.**
- Modelo: **licencia perpetua + plan de mantenimiento anual**, o suscripción de 1/2/3 años.
  Sin mantenimiento se conserva la última versión. **Monousuario**, no transferible.
  El mantenimiento incluye una *Home Use license* para una segunda máquina.
- **No hay partner en Argentina.** El único de Latinoamérica es **Datec (México)** —
  Raúl Benítez, rbenitez@datec.mx. Alternativa: **Graitec Iberia** —
  comercial.iberia@graitec.com, +34 976 458 145. La web dice: *"If your country is not listed, contact us."*
- Fabricante: **Čeli APS**. Versión actual **v17.1.1** (09/07/2026).

### Prueba gratis

Existe, con **CAM y Nesting incluidos**. Duración contradictoria entre fuentes oficiales:
el EULA dice **30 días**, el blog dice **45**. Hay un procedimiento formal de extensión.
Formulario en `woodworkforinventor.com/get-trial`; el enlace llega por mail.

### Requisitos

- **Windows 10 u 11.** No hay Mac (Inventor tampoco).
- **Inventor 2025, 2026 o 2027** — estándar o Professional. Sin requisito de tier de suscripción.
- .NET 8+ · **16 GB RAM** mínimo (32 GB si el ensamble supera 1000 componentes) · 40 GB de disco.
- **Excel 2016+ o LibreOffice 7.2+** — necesario para los informes BOM.

---

## Qué preguntar antes de pagar

1. ¿Puede un post-procesador JS propio **fijar el nombre del archivo de salida**
   (por ejemplo desde una iProperty con el código de barras)?
2. ¿Pueden mandar el **`Postprocessor API Help.chm`** para evaluar qué expone el modelo de
   objetos: taladro horizontal por canto, ranuras, profundidades, contorno?
3. ¿El post `.mpr` emite el bloque **`<103 \End_Boring\`** en los cuatro cantos?
   Pedir un `.mpr` de ejemplo de una pieza con taladro horizontal en los 4 cantos.
4. ¿Cómo se nombra el programa del **segundo amarre** (cara trasera)? ¿Sigue la convención
   de sufijo **"K"** de WoodWOP?
5. ¿Existe algún **export de datos** (XML/CSV) de agujeros y ranuras, además de los posts?
6. ¿La biblioteca trae el **tres-en-uno** con Ø15 excéntrica / Ø10 pre-embedded / Ø8 varilla,
   y la **cazoleta Ø35**? ¿Son paramétricos al cambiar medidas del panel?
7. ¿Las etiquetas soportan **código de barras o QR**?
8. ¿Han hecho posts para **taladradoras de 6 caras**? Costo y plazo de uno a medida.
9. **Precio para Argentina**, edición base + CAM, perpetua vs suscripción.

---

## Prueba a hacer durante el trial

La misma jugada que ya funcionó: **validar contra un oráculo conocido**.

1. Modelar en Inventor el **techo de PRUEBA 1**: 400 × 600 × 18, con 4 agujeros Ø10 prof 11
   en X = 40 y 360, Y = 9 y 591, más la ranura de 6×6 y la de 9×9.
2. Generar el programa CNC con el post `.mpr` de fábrica.
3. Comparar contra `etapa2/salida/PRUEBA1_BAN/9441838670057.ban`, que ya está validado.
4. Abrir el SDK y ver si el objeto de programa expone todo lo que hace falta.

Si los datos están completos, el post propio es trabajo mecánico y la decisión está tomada.
Si falta información en el objeto, W4I no sirve para esta máquina y volvemos a construir
el extractor propio.

---

## Comparación contra construirlo

| | Comprar W4I | Construir |
|---|---|---|
| Modelo paramétrico + herrajes | incluido | ~2 meses |
| Cantos, veta, BOM | incluido | ~3 semanas |
| Archivo de máquina | post JS propio, semanas | **ya hecho** |
| Optimización de corte | AutoCUT (ya lo tenés) | AutoCUT (ya lo tenés) |
| Dependencia | licencia + mantenimiento anual | ninguna |
| Riesgo | que el SDK no exponga lo necesario | tiempo |

La pieza que W4I ahorra es justamente la más cara y la que menos ganas dan de escribir.
