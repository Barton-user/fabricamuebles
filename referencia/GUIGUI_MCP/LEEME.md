# GuiGui MCP — descubierto el 22/09/2026

GuiGui levanta un **servidor MCP real** (Streamable HTTP) en la Mac:

    POST http://127.0.0.1:8010/guigui-mcp
    headers: content-type: application/json, accept: application/json
    initialize → devuelve header `Mcp-Session-Id`, mandarlo en las llamadas siguientes.
    serverInfo: "Guigui MCP Server" 1.1.1 (protocolo 2024-11-05). GET → 405. Sin auth.

Sólo se alcanza desde la propia Mac (el navegador integrado de Claude corre ahí;
el Chrome conectado a la sesión es una PC Windows y no llega).

## Herramientas (23)
`tools.json` tiene el schema completo. Las que importan para nosotros:

| Tool | Qué da | Restricción |
|---|---|---|
| `project_search_order` | lista de órdenes con **todas las habitaciones**: id, nombre, gabinetes (`other_info.wdbNames`), y las URLs `json_url` (.jin, binario/cifrado), `render_url` (**JSON abierto con el modelo 3D completo**), `img_url` | funciona desde cualquier página |
| `design_get_room_structure` | estructura de la habitación abierta (`isRecursive`) | sólo en la página de diseño |
| `export_get_material_bill` / `export_get_quotation` | lista de materiales / cotización | sólo en la página de salida (输出) |
| `santi_get_material_info` / `santi_sync_material_info` | listas de materiales locales (hay que sincronizar antes) | devolvió vacío |
| `design_create_model`, `design_edit_model`, `cdesign_*` | **crear y editar muebles por API** | página de diseño |
| `quick_open_project` | abre (o crea) orden/habitación | — |
| `get_cmodel_list`, `get_model_list` | biblioteca de modelos (paramétricos) del usuario | — |

Recursos: `guigui://info/{mcp_version, mcp_changelog, guigui_version, login_status,
current_page, user_info, supported_component_names/{mode},
supported_component_params/{name}, supported_cmodel_names, supported_cmodel_params/{name}}`.

## El hallazgo: `render_url` → `<id>.render.json`

Es el **modelo 3D completo de la habitación**, público en Aliyun OSS, sin auth:

    http://eggrj.oss-accelerate.aliyuncs.com/renderJSON/<id>.json

Árbol `models[]` (un gabinete c/u, con `anchor` en la habitación, `width/height/depth`
en **metros**) → `children[]` (Plank, Door → SingleDoor → 外框 + 铰链孔, Lintel → Plank).
Cada `Plank` trae **lo mismo que `Mass production.json`** (`plankNum` = código de barras,
`holes/sholes/slots/sslots` con `ocenter`, `edgeInfo`, `connection_types`, `matCode`,
`texDir`, `spec`) **más la posición 3D**: `anchor`, `axis` (normal de la placa: X/Y/Z),
`vertices` (8, en metros, relativos al anchor), `hDir/vDir/dDir`, `referPt`.
Y los herrajes por placa en `partsChildren` (`连接件:三合一`, `灯带:600X9X9`,
`一字底座铰链:全盖式`, `连接件:超长连接杆`).

**Es la tercera entrada del motor** (§16.2): tiene todo lo que tiene el JSON de
producción y además el armado. Sirve para reconstruir el ensamble en Fusion y para
derivar el manual de armado.

## Archivos acá

| Archivo | Habitación | room id | Gabinetes | Placas |
|---|---|---|---|---|
| `207960w11787944219301.*` | **PRUEBA 1** (orden 260625-20) | 104088677 | 00-Doble c/spar01 | 10 (+2 puertas como 外框) |
| `207960w31789042536993.*` | **COCINA MLV** | 112168923 | 14 (bandejero, horno y anafe, cajonera, bajo mesada doble, lavarropa, escobero, 6 alacenas, 2 uñeros) | 116 · 290 tres-en-uno · 4 varillas largas · 11 tiras LED |
| `207960w31787744527615.*` | Placard - malvinas | 112168990 | CabinetA (+Wall01) | 87 · 128 tres-en-uno |

`.render.json` = modelo 3D abierto · `.jin` = archivo de GuiGui (binario, no legible) · `.jpg` = miniatura.
`orden_PRUEBA.json` = respuesta completa de `project_search_order`.

Los códigos de barras de PRUEBA 1 en el render.json coinciden con los de
`etapa2/salida/PRUEBA1/` (9441838670057 … 163).
