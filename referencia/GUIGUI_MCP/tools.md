# GuiGui MCP — herramientas (v1.1.1, 22/09/2026)

Schema resumido. Llamada: `tools/call` con `{name, arguments}`.

- `project_search_order` {key_words, search_key: buyer_address|order_code|customer_name|designer, begin_day, end_day, page, limit, status, status_type} → órdenes con `room[]` (id, name, other_info.wdbNames, json_url, render_url, img_url). **Funciona desde cualquier página.**
- `project_get_order_statistic` {} → estadísticas.
- `quick_open_project` {designInfo:{orderCode, buyerAddress, roomName | roomNames[]}} → abre o crea orden/habitación.
- `design_get_room_structure` {isRecursive, onlyWardrobe, exportSnapshot} → estructura de la habitación abierta. **Sólo en página de diseño.**
- `design_get_model_params` {componentNo, names[]} → propiedades del componente seleccionado.
- `design_get_room_info` {info: 千里眼链接|微信二维码链接}.
- `design_create_model` {type: 模型|参数化模型, models:[{id|name, cube:{x,y,z,width,height,depth}, params[], cparams[], rotate}]} → crea muebles de la biblioteca en la habitación.
- `design_edit_model` {operate: 清空柜体|进入房间|进入柜体|组合柜体|选中组件|清空组件|添加组件|修改位置及尺寸|修改工艺参数|删除组件, content:[{componentNo, componentName, name, cube, coord: 正面墙|背面墙|左侧墙|右侧墙|地板, params[]}]}.
- `design_use_design_tool` {toolName: Save | Exploded view | Structural diagram | Display board number | All slots | Mirror | Copy | Paste | Delete | Equally divided | Order review | Supplement | Customize Shapes | 切角 | …}.
- `export_get_material_bill` {} / `export_get_quotation` {} → **sólo en la página de salida (输出).**
- `cdesign_create_cmodel` {designInfo:{cmodelName}} / `cdesign_edit_cmodel` {operate: 编辑属性|编辑参数化属性, params:{componentNo|compId, params[], cparams[{name,key,value,minValue,maxValue,type,valueType}]}} / `cdesign_save_cmodel` {name} / `cdesign_get_cmodel_structure` {} / `cdesign_import_external_model` {filePath} → editor de **modelos paramétricos**.
- `get_model_list` {source: user|main|public} (lento) / `get_cmodel_list` {} → bibliotecas.
- `get_supplement_list` {} → lista de repuestos.
- `santi_get_material_info` {orderIds[], roomIds[]} / `santi_sync_material_info` {} → listas de materiales locales ("三体"); devolvió vacío sin sincronizar.
- `get_sk` {name} → token del usuario (no usar).
- `send_feedback_to_rd` {title, body, type, context} → manda mensaje al equipo de desarrollo de GuiGui (no usar sin querer).

Recursos (`resources/read` {uri}): `guigui://info/mcp_version`, `mcp_changelog`, `guigui_version`, `login_status`, `current_page`, `user_info`, `supported_component_names/{房间模式|柜体模式}`, `supported_component_params/{name}`, `supported_cmodel_names`, `supported_cmodel_params/{name}`.

Nota del changelog: la API cambia entre versiones (0.0.1 → 1.1.1 en 6 meses, con herramientas removidas). No depender de ella para producción; sí para extraer.
