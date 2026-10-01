# GuiGui / Bluen

_Notas de operación de GuiGui y Bluen aprendidas a los golpes, problemas resueltos y el MCP de GuiGui._

_Movido tal cual desde `CONTEXTO.md` el 01/10/2026. Las referencias "§N" dentro del texto son a la numeración vieja de `CONTEXTO.md`: cada sección vieja dejó allí una línea 📦 que dice adónde fue. Si algo de acá contradice a `CONTEXTO.md`, manda `CONTEXTO.md`._

---

## 7. Notas de operación de GuiGui / Bluen (aprendidas a los golpes)

- **La configuración de equipos vive en la nube** (`bluen.cn`), no en la Mac. Si la app no
  llega al servidor, el generador de NC falla con errores tipo `找不到刀具T1`
  ("no se encuentra la herramienta T1").
- El cliente **cachea los nombres de línea**: renombrar en Bluen no se refleja en el
  desplegable de GuiGui.
- **Cada cambio de configuración pide código SMS.** Agrupar todos los cambios antes de guardar.
- Después de configurar en Bluen, **NO guardar en la página de device docking del cliente**:
  resetea los parámetros (lo avisa en rojo la propia página).
- **Cambiar la plantilla de la perforadora bloquea el software** hasta hacer la "producción de
  prueba del mueble de muestra", o firmar un descargo de responsabilidad que pide foto del
  mueble armado + teléfono + SMS. El botón **"Trial production sample cabinet"** carga el
  mueble de muestra en la lista de órdenes y destraba — y de paso entrega los archivos de
  referencia en todos los formatos, que es oro puro.
- El **Knife Storage** de la perforadora es para **fresas** (compensa el radio de corte),
  no para mechas. Las mechas viven en el Knife Library de HHcnc, en la máquina.
  Cada fila necesita "Knife Number" **único y no vacío** o no deja guardar
  (`刀库-刀具编号重复或为空，请检查`).
- La UI está rota: textos superpuestos, botones cortados, mezcla de chino e inglés,
  layout que no se adapta a la pantalla. Leer los carteles con cuidado igual, algunos importan.
- GuiGui levanta un **servicio MCP en `localhost:8010`** (lo muestra en verde abajo a la
  derecha: `MCP服务已启动, 端口: 8010, 版本: 1.1.1`). **Pendiente de explorar** — podría
  permitir automatizar GuiGui desde afuera, o ser una vía de integración para la Etapa 2.

### Secuencia de encendido de la SKH-612HS (del manual, sección 8)

1. Encender equipo y **vacío**.
2. **COMPUTER START** en el panel → esperar a que la PC industrial arranque **por completo**.
3. **POWER** → esperar ~1 minuto.
4. Doble clic en **CncMon32** → verificar estado **"ready"** (la alarma no debe titilar) → minimizar.
5. Doble clic en **HHcnc** → interfaz de operación.
6. Importar archivos/directorio → pasar a **modo escaneo** → escanear QR → colocar la placa.
7. **Botón verde dos veces**: la primera deja la máquina esperando la pieza, la segunda mecaniza.

Apagado: cerrar HHcnc → CncMon32 → apagar la PC normalmente → recién ahí cortar la energía.
**Entre apagado y encendido deben pasar más de 60 segundos.**

Idioma: HHcnc → botón (S) en el área de proceso → system settings → language.
CncMon32 → F8 System Management → F3 parameter setting → F5 jump to parameter →
parámetro **3209** = `0` para inglés.

Si tras un corte de energía aparece un archivo raro: F2 Program Edit → F8 File Management →
doble clic en `o010000` → F1 cargar y ejecutar.

Mantenimiento: engrasar los packs de mechas cada **120-150 horas** con **Klüber L32-N**.

### Procesos que soporta HHcnc

Agujeros verticales, agujeros horizontales, ranuras, fresado, fresado rectangular,
fresado circular, chaflán, **Lamello** y **Locking**. Cubre todo lo que necesita PRUEBA 1.

---

## 8. Problemas resueltos (por si vuelven)

- **E03** — empujador no está en origen de carga: botón **MatRes** en manual, o la placa está
  mal orientada / demasiado metida.
- **E08 / Er17-1** en el drive INVT DA200 = **sobrecarga del servo del empujador**, NO es un
  servo roto. Causa típica: placa cruzada o material trabado. Se resetea cortando la energía
  general 1 minuto. Si el puente del empujador queda torcido (un lado al tope, el otro
  separado), **escuadrarlo antes de seguir**.
- **E16** — carro de sierra fuera de origen: Alarma Off + VolOrig completo.
- La pantalla "alarma" del control **es un catálogo de códigos**; las alarmas activas
  aparecen en la franja roja de abajo.
- **`找不到刀具T1`** al exportar: la línea de producción apuntaba al router y su almacén de
  herramientas estaba vacío (o no había conexión con bluen.cn).
- **`ERR_SOCKET_NOT_CONNECTED`** al abrir Equipment integration: la ventana embebida perdió
  la red. Reintentar, o abrir `https://www.bluen.cn` en Chrome. El servidor suele estar bien.

---

# 17. El MCP de GuiGui — explorado el 22/09/2026

La pista de §7 y §12 dio resultado. Detalle completo en **`referencia/GUIGUI_MCP/LEEME.md`**
y `tools.md`.

- Endpoint: `POST http://127.0.0.1:8010/guigui-mcp` (Streamable HTTP, sin auth, sesión
  por header `Mcp-Session-Id`). Sólo alcanzable desde la Mac; desde Claude se llega con
  el **navegador integrado** de la app (el Chrome conectado es la PC Windows).
- `project_search_order` devuelve, para cada habitación, la URL de un **`render.json`
  público en Aliyun** con el **modelo 3D completo**: cada placa con posición (`anchor`,
  `axis`, `vertices`), código de barras, agujeros/ranuras (mismo esquema que el
  `Mass production.json`), cantos, material, veta y herrajes por placa.
- Ya bajados a `referencia/GUIGUI_MCP/`: **PRUEBA 1**, **COCINA MLV** (14 gabinetes,
  116 placas) y **Placard - malvinas** (87 placas). No hizo falta exportar nada a mano.
- El MCP también permite **crear y editar muebles** (`design_create_model`,
  `design_edit_model`, `cdesign_*`) y guardar. Queda como opción para automatizar
  GuiGui mientras siga en uso; no se probó ninguna herramienta que escriba.
- La API cambió 7 veces en 6 meses (ver changelog). Sirve para **extraer**, no para
  apoyar producción encima.

**Consecuencia para §16:** el `render.json` es la tercera entrada del motor y trae el
armado, que al `Mass production.json` le faltaba. Con él se puede reconstruir el
ensamble en Fusion y derivar el manual de armado sin adivinar posiciones.

---
