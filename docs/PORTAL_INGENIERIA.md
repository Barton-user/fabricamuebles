# Muebles en el portal de ingeniería (ingenieria.leiten.com.ar)

_Especificación de la integración FABRICA MUEBLES → portal. Versión 1 · 27/10/2026._

> **Para la conversación del portal.** Este documento define qué manda FABRICA MUEBLES y qué
> tiene que hacer el portal con eso. FABRICA MUEBLES **no toca código del portal**. El portal
> **no lee GuiGui ni corre nuestros scripts**: recibe un paquete ya armado.
> Paquete de ejemplo real: `PENDRIVE/12_COCINA_MLV/portal/paquete_MLV-COCINA.zip`
> (COCINA MLV, 13 módulos, 125 piezas, 17 MB).

## 1. Decisiones (Pato, 27/10/2026)

| Tema | Decisión |
|---|---|
| Empresa | **hemma** |
| Proyecto | **uno por ambiente** (`MLV-COCINA`, aparte `MLV-PLACARD`…) |
| Carga | **automática por API**: un comando en FABRICA MUEBLES sube el paquete |
| Planos de cada pieza | **los dos**: el de IDEE (principal) y el de mecanizado nuestro (acotado con agujeros) |
| Planos de IDEE | los hace IDEE aparte (PDF, una hoja por pieza). FABRICA MUEBLES los parte y los manda ya vinculados a cada pieza |
| Etiquetas | **las genera el portal**, desde la base. El QR apunta al portal |
| QR | **mixto**: sin login se ve lo básico (a definir, propuesta en §5); con login, lo que permitan los permisos del usuario |
| leiten.vercel.app | sigue funcionando hasta que el portal tenga la ficha por QR; después se da de baja |

## 2. Cómo se mapea un mueble al modelo que ya tiene el portal

Nada nuevo en el modelo de datos de base: se usa el maestro y el portal de fabricación existentes.

```
ing_proyectos      empresa=hemma, codigo=MLV-COCINA, nombre="Malvinas · Cocina"
  documento_id ──► ing_documentos  MLV-COCINA          tipo=conjunto   (la cocina entera)
                     ├─ MLV-COCINA-M01  tipo=subconjunto  posicion=1  "Horno y anafe"
                     │    ├─ 1956217421314  tipo=pieza  posicion=1 (= ítem / globo)
                     │    └─ …
                     └─ MLV-COCINA-M13  "Alacena spar"
ing_revisiones     una revisión nueva por cada subida (queda EN CURSO; se libera a mano en el portal)
ing_revision_archivos   los archivos del paquete, con documento_id = la pieza o el módulo
```

- **Código de pieza = el código de barras EAN-13 de GuiGui** (13 dígitos, único; cumple `esCodigoValido`).
  Es lo que lee la perforadora y el nombre de su programa (`<código>.xml`).
- **Código de módulo** = `<proyecto>-Mnn`. **Código del conjunto** = el del proyecto.
- `ing_documentos.archivo_pdf_id` de cada pieza = su **plano de IDEE** (el de mecanizado va como segundo archivo).
- El taller ve sólo la **revisión liberada** (como ya hace `/fabricacion`): la subida no reemplaza lo que se
  está fabricando hasta que alguien la libera.

## 3. El paquete (`fabrica-muebles/paquete@1`)

Un ZIP con `manifest.json` en la raíz y los archivos en las rutas que dice el manifest. Lo arma
`etapa2/paquete_portal.py` (FABRICA MUEBLES).

```
manifest.json
proyecto/   planos_idee.pdf (completo), lista_corte.xlsx/.csv, HOJAS_*.html, LEEME.md, piezas_informe.txt
conjunto/   plano_idee.pdf (hoja 1 de IDEE: el ambiente)
modulos/Mnn/  planos_mecanizado.pdf, manual_armado.pdf, plano_idee.pdf
piezas/<código>/  plano_idee.pdf, plano_mecanizado.pdf, plano_mecanizado.png, ubicacion.svg
programas/perforadora/<código>.xml          (y 99….xml = paso 2)
programas/perforadora_un_paso/<código>.xml  (alternativa a probar)
```

### manifest.json

```jsonc
{
  "formato": "fabrica-muebles/paquete@1",
  "generado": "2026-10-27T14:45:30-03:00",
  "origen": { "programa": "…paquete_portal.py", "commit": "86ab716",
              "guigui": { "orden": "260625-20", "ambiente": "COCINA MLV", "guardado": "22/10/2026", "render": "…json" } },
  "empresa": "hemma",
  "proyecto": { "codigo": "MLV-COCINA", "nombre": "Malvinas · Cocina", "obra": "Malvinas",
                "ambiente": "COCINA MLV", "orden": "260625-20" },
  "conjunto": { "codigo": "MLV-COCINA", "descripcion": "Malvinas · Cocina", "tipo": "conjunto",
                "archivos": [ { "rol": "plano_idee", "ruta": "conjunto/plano_idee.pdf" } ] },
  "archivos_proyecto": [ { "rol": "lista_corte", "maquina": "corte_hp280", "ruta": "proyecto/lista_corte.xlsx" }, … ],
  "modulos": [ {
      "n": 1, "codigo": "MLV-COCINA-M01", "nombre": "Horno y anafe", "tipo": "subconjunto", "cantidad": 1,
      "ancho": 600, "alto": 780, "prof": 580,
      "archivos": [ { "rol": "planos_mecanizado", "ruta": "modulos/M01/planos_mecanizado.pdf" },
                    { "rol": "manual_armado", "publico": true, "ruta": "modulos/M01/manual_armado.pdf" },
                    { "rol": "plano_idee", "ruta": "modulos/M01/plano_idee.pdf" } ],
      "piezas": [ {
          "item": 3, "codigo": "1956217421345", "id_etiqueta": 1448, "cantidad": 1,
          "nombre": "Piso 564x562x18", "nombre_guigui": "Base01", "tipo": "Piso", "rol": "PLACA", "cajon": 0,
          "medida": { "terminada": [564, 562], "corte": [564, 561], "espesor": 18 },
          "material": "Estructura (N) 18", "material_codigo": "NEstructura", "color": "Blanco", "veta": "vertical",
          "cantos": { "izq": 0, "der": 1, "abajo": 0, "arriba": 0 },
          "mecanizados": [ { "tipo": "Excéntrica 3 en 1", "n": 6 }, { "tipo": "Perno 3 en 1", "n": 6 } ],
          "dos_pasos": null,                 // o { "paso2": "99…" }
          "avisos": [],                      // texto para el taller ("pieza con recorte…", "ranura de canto…")
          "archivos": [
            { "rol": "plano_idee", "principal": true, "ruta": "piezas/1956217421345/plano_idee.pdf" },
            { "rol": "plano_mecanizado", "principal": false, "ruta": "piezas/1956217421345/plano_mecanizado.pdf" },
            { "rol": "plano_mecanizado_png", "ruta": "piezas/1956217421345/plano_mecanizado.png" },
            { "rol": "ubicacion", "publico": true, "ruta": "piezas/1956217421345/ubicacion.svg" },
            { "rol": "programa", "maquina": "perforadora_6caras", "paso": null,
              "ruta": "programas/perforadora/1956217421345.xml" } ] } ] } ],
  "avisos": []                               // problemas del paquete (p. ej. pieza sin plano de IDEE)
}
```

Reglas del formato:

- **`item`** es el número de globo de la pieza dentro del módulo: el mismo en la etiqueta, el plano de
  mecanizado, el manual y la lista de corte. **`id_etiqueta`** es el "ID" de GuiGui que usan los planos de IDEE.
- **Medidas en mm.** `terminada` = con canto; `corte` = la que sale de la sierra. `[ancho, alto]` del plano de la pieza.
- **`cantos`**: 1 = lleva canto de 1 mm en ese borde, en el marco del plano de mecanizado de la pieza
  (izq/der/abajo/arriba del dibujo).
- **`publico: true`** marca los archivos que se pueden ver sin login (ver §5). Lo que no lo tiene, es con login.
- **`maquina`** usa los códigos de `ing_maquinas`. Hace falta una nueva: **`perforadora_6caras`** (§6).
- **Piezas en dos pasos**: `programa` con `paso: 1` (código de la pieza) y `paso: 2` (código `99…`, con
  `codigo_programa`). Los dos se vinculan a la **misma** pieza. `programa_alternativo` = versión en un paso, a probar.
- Mismo proyecto, segunda subida: mismos códigos. Las piezas que ya no vienen tienen que quedar señaladas
  (no borrarlas: puede haber avance y reportes).

## 4. Lo que tiene que hacer el portal (para la otra conversación)

1. **Recibir el paquete por API.** Endpoint en la API externa que ya existe, con API key de alcance `hemma`.
   Propuesta: `POST /api/externo/v1/fabricacion/paquetes` (multipart, campo `paquete` = el ZIP),
   `?dry=1` para validar sin escribir. Respuesta: proyecto, revisión, cuántas piezas nuevas / cambiadas /
   que ya no vienen, y los avisos. Debe ser idempotente (subir dos veces el mismo ZIP no duplica nada).
2. **Cargarlo en el modelo** como dice §2: proyecto, árbol, revisión en curso, archivos con `documento_id`,
   plano principal de cada pieza, máquina de cada programa. La revisión se libera a mano.
3. **Entrada por código: `https://ingenieria.leiten.com.ar/p/<código>`** (eso va en el QR). Busca la pieza
   en hemma y muestra una **ficha para celular**. Sin login, lo básico (§5) y un botón "Entrar para ver más"
   que, después del login, **vuelve a la misma pieza** (hoy el login manda siempre al dashboard). Con login,
   lo que den sus permisos: planos, programas por máquina, avance, reportar problema.
4. **Etiquetas** (§7): generarlas desde la base, por proyecto o por módulo, en 60 × 39 y en A4.
5. **Máquina nueva** `perforadora_6caras` y reglas (§6).

## 5. Qué se ve sin login (propuesta, a definir)

| Se ve sin login | Sólo con login |
|---|---|
| Nombre de la pieza, ítem, módulo y ambiente | Planos (IDEE y mecanizado) |
| Medida terminada, espesor, material y color | Programas y lista de corte |
| Cantos (dibujo) | Avance de fabricación y reportes |
| "Dónde va en el mueble" (`ubicacion.svg`) | Obra / orden / cliente |
| Manual de armado del módulo | Avisos para el taller |

Pensado para el instalador o el cliente que escanea una pieza suelta. No mostrar datos del cliente ni la dirección.

## 6. Máquinas

| Código | Nombre | Archivos | Nota |
|---|---|---|---|
| `corte_hp280` | Corte HP280 (ya existe) | `lista_corte.xlsx/.csv` | la columna `条码` es el código; AutoCUT todavía mal mapeado (ver FABRICA MUEBLES) |
| **`perforadora_6caras`** | **Perforadora SKH-612HS** (nueva) | `<código>.xml` (KDTXml / XML3) | **un archivo por pieza, el nombre es el código**: el operario escanea la etiqueta y la máquina lo carga |
| `cantos` | Pegadora de cantos (ya existe) | — | usa los cantos de la ficha |
| `armado` | Armado (ya existe) | `manual_armado.pdf` | |

La regla `xml → perforadora_6caras` conviene por **subcarpeta** (p. ej. `Programas_CAM/Perforadora`), porque
`.xml` es una extensión genérica. El `router_6ejes` del catálogo ("piezas curvas") **no** es esta máquina.

## 7. Etiqueta (la arma el portal)

Rollo de **60 × 39 mm** (impresora AIBAO = TSC TTP-245C; su sensor de gap no anda, por eso también A4 para
imprimir en impresora común y recortar). Un PDF de una etiqueta por página de 60 × 39, y otro A4 con grilla.
Orden: por módulo y por ítem.

Contenido (el diseño actual está en `PENDRIVE/12_COCINA_MLV/etiquetas_qr_web/etiquetas_60x39.pdf`):

- **Código de barras EAN-13** con el código de la pieza — lo lee la perforadora. Tamaño legible por la pistola.
- **QR** con `https://ingenieria.leiten.com.ar/p/<código>`. Si la pistola de la perforadora es 2D, tiene que
  quedar claro cuál es cuál (el QR más chico y separado del EAN).
- Ambiente y módulo (`Mnn · Horno y anafe`), **ítem** (globo) e **ID etiqueta** de IDEE.
- Nombre de la pieza, **medida de corte** × espesor, material y color, veta.
- Dibujo de los cantos (rectángulo con los bordes marcados).

## 8. Del lado de FABRICA MUEBLES (esta conversación)

- `etapa2/generar_desde_render.sh` genera todo lo de fábrica desde GuiGui (ya existe).
- `etapa2/paquete_portal.py` arma el ZIP de §3 (ya existe; probado con COCINA MLV: 125/125 piezas con plano
  de IDEE y de mecanizado verificados por código, ID etiqueta igual a IDEE en las 125).
- `etapa2/subir_portal.py` (pendiente): manda el ZIP al endpoint de §4.1. Necesita la URL y la API key
  (la key va en una variable de entorno, nunca en git).

## 9. Pendiente de definir

- Lo que se ve sin login (§5).
- Nombre definitivo del endpoint y si la respuesta trae algo más.
- Si el portal quiere también el **render** o las **etiquetas de referencia** dentro del paquete.
