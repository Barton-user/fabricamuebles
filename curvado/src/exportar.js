// Escritores de archivos de máquina.
//
// Son puertos 1:1 de etapa2/ (xml3.py, mpr.py, listacorte.py), que están
// validados byte a byte contra Bluen y probados en la SKH-612HS. Cualquier
// cambio acá tiene que seguir dando lo mismo que el Python (ver test/validar.mjs).
//
// Una "pieza" acá es el mismo modelo que etapa2/panel.py:Panel, reducido a lo
// que usa una pieza curvada: rectángulo + ranuras de cara.
//   { code, name, width (X), height (Y), thickness, material, texture, grain,
//     quantity, edges: {up, down, left, right}, slots: [{x1,y1,x2,y2,width,depth,face}],
//     order_no, customer, address, room, location, short_name, plank_id }

export const FACE_FRONT = 'A';
export const FACE_BACK = 'B';

// ---------------------------------------------------------------- XML3 (KDTXml)
const n2 = (v) => { let r = Math.round((+v + 0) * 100) / 100; if (Object.is(r, -0) || r === 0) r = 0; return r.toFixed(2); };
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

export function xml3(p) {
  const L = ['<KDTPanelFormat>', '    <PANEL>'];
  L.push(`        <PanelLength>${n2(p.width)}</PanelLength>`);
  L.push(`        <PanelWidth>${n2(p.height)}</PanelWidth>`);
  L.push(`        <PanelThickness>${n2(p.thickness)}</PanelThickness>`);
  L.push(`        <PanelName>${esc(p.name)}</PanelName>`);
  L.push('        <Params>');
  L.push(`            <Param Key="L" Value="${n2(p.width)}" Comment="板长"/>`);
  L.push(`            <Param Key="W" Value="${n2(p.height)}" Comment="板宽"/>`);
  L.push(`            <Param Key="T" Value="${n2(p.thickness)}" Comment="板厚"/>`);
  L.push('        </Params>');
  L.push('    </PANEL>');
  for (const sl of p.slots) {
    const tn = sl.face === FACE_BACK ? 13 : 3;
    L.push('    <CAD>',
      `        <TypeNo>${tn}</TypeNo>`,
      '        <TypeName>Line</TypeName>',
      `        <BeginX>${n2(sl.x1)}</BeginX>`,
      `        <BeginY>${n2(sl.y1)}</BeginY>`,
      `        <EndX>${n2(sl.x2)}</EndX>`,
      `        <EndY>${n2(sl.y2)}</EndY>`,
      '        <Correction>0</Correction>',
      `        <Width>${n2(sl.width)}</Width>`,
      `        <Depth>${n2(sl.depth)}</Depth>`,
      '        <Enable>1</Enable>',
      '    </CAD>');
  }
  L.push('</KDTPanelFormat>');
  return L.join('\n') + '\n';
}

// ---------------------------------------------------------------- MPR (Haomai MPR)
const nm = (v) => { let s = (Math.round((+v + 0) * 100) / 100).toFixed(2).replace(/0+$/, '').replace(/\.$/, ''); return (s === '' || s === '-0') ? '0' : s; };
const kv = (pairs) => pairs.map(([k, v]) => `${k}="${v}"`);
const NUT_TAIL = [['RK', 'NoWRK'], ['EM', 'MOD1'], ['AD', '0'], ['TV', '0'], ['MV', 'GL']];
const NUT_TAIL2 = [['XY', '100'], ['MN', 'GL'], ['OP', '0'], ['AN', '0'], ['HP', '0'], ['SP', '0'], ['YVE', '0'],
  ['WW', '40,41,42,45,141,142,144,145'], ['ASG', '2'], ['KAT', 'Nuten'], ['MNM', 'Grooving'],
  ['MX', '0'], ['MY', '0'], ['MZ', '0'], ['MXF', '1'], ['MYF', '1'], ['MZF', '1']];

export function hasBackOps(p) { return p.slots.some((s) => s.face === FACE_BACK); }
export function hasFrontOps(p) { return p.slots.some((s) => s.face !== FACE_BACK); }

export function mpr(p, back = false) {
  const e = p.edges || {};
  // El .mpr usa edge_front (y=0) / edge_back (y=H) / left / right del marco de máquina
  const lines = [
    `[H\\Left:${nm(e.left || 0)};Bottom:${nm(e.down || 0)};Right:${nm(e.right || 0)};Top:${nm(e.up || 0)}`,
    'VERSION="4.0 Alpha"', 'VIEW="NOMIRROR"', 'OP="1"', 'FM="1"', 'FW="800"',
    'HP="1"', 'UP="0"', 'GX="1"', 'DW="0"', 'ModusMirror="1"', '',
    '<100 \\WerkStck\\',
    `LA="${nm(p.width)}"`, `BR="${nm(p.height)}"`, `DI="${nm(p.thickness)}"`,
    'FNX="0"', 'FNY="0"', 'RNX="0"', 'RNY="0"', 'RNZ="0"', 'AX="0"', 'AY="0"', '',
  ];
  const mx = back ? (v) => p.width - v : (v) => v;
  const face = back ? FACE_BACK : FACE_FRONT;
  for (const sl of p.slots) {
    if ((sl.face || FACE_FRONT) !== face) continue;
    lines.push('<109 \\Nuten\\', `XA="${nm(mx(sl.x1))}"`, `YA="${nm(sl.y1)}"`, 'WI="0"',
      `XE="${nm(mx(sl.x2))}"`, `YE="${nm(sl.y2)}"`, `NB="${nm(sl.width)}"`,
      ...kv(NUT_TAIL), `TI="${nm(sl.depth)}"`, ...kv(NUT_TAIL2), '');
  }
  lines.push('<101 \\Kommentar\\', `KM="${asciiGbk(p.name)}"`, '!');
  return lines.join('\r\n');
}

// El .mpr va en GBK. El navegador no tiene codificador GBK: el comentario se
// escribe en ASCII (sin tildes) para que el archivo sea idéntico en GBK y en UTF-8.
function asciiGbk(s) {
  return String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^\x20-\x7e]/g, '?');
}

// ---------------------------------------------------------------- Lista de corte (AutoCUT)
export const COLUMNAS = ['序号', '打包二维码', '工件名称', '数量', '长', '宽', '成品面积', '厚', '材料', '开料长', '开料宽',
  '切割面积', '开料厚', '板件条码', '板号', '前封边', '后封边', '左封边', '右封边', '纹路', '订单号', '客户名称', '项目地址', '部件名称'];

const nc = (v) => (Math.abs(v - Math.round(v)) < 1e-9 ? Math.round(v) : Math.round(v * 100) / 100);
const r2 = (v) => Math.round(v * 100) / 100;

export function barcodes(p) {
  if (!p.slots.length) return p.code;
  if (hasBackOps(p)) return `${p.code}_${p.code}_${p.code}K`;
  return `${p.code}_${p.code}`;
}

// Puerto de listacorte.fila(). El marco de la pieza curvada no se rota, así que
// src_* = medidas de máquina.
export function filaCorte(p, n) {
  const e = p.edges || {};
  const alto = p.height, anchoX = p.width;
  const corteAlto = alto - (e.up || 0) - (e.down || 0);
  const corteAnchoX = anchoX - (e.left || 0) - (e.right || 0);
  let largo, ancho, cL, cA, cF, cB, cI, cD;
  if (String(p.grain) === '1') {       // veta horizontal: a lo largo de X (el desarrollo)
    largo = anchoX; ancho = alto; cL = corteAnchoX; cA = corteAlto;
    cF = e.left || 0; cB = e.right || 0; cI = e.up || 0; cD = e.down || 0;
  } else {                              // veta vertical: a lo largo de Y (el alto)
    largo = alto; ancho = anchoX; cL = corteAlto; cA = corteAnchoX;
    cF = e.up || 0; cB = e.down || 0; cI = e.left || 0; cD = e.right || 0;
  }
  const etiqueta = [p.room, p.location, p.short_name].filter(Boolean).join('_') || p.name;
  const veta = String(p.grain) === '1' ? '横纹' : '竖纹';
  return [n, etiqueta, etiqueta, p.quantity, nc(largo), nc(ancho), r2((largo * ancho) / 1e6), nc(p.thickness),
    [nc(p.thickness), p.material, p.texture].filter((x) => String(x)).join('_'),
    nc(cL), nc(cA), r2((cL * cA) / 1e6), nc(p.thickness), barcodes(p), p.plank_id,
    nc(cF), nc(cB), nc(cI), nc(cD), veta, p.order_no, p.customer, p.address, p.name];
}

export function csvCorte(piezas) {
  const q = (v) => { const s = String(v ?? ''); return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };
  const rows = [COLUMNAS, ...piezas.map((p, i) => filaCorte(p, i + 1))];
  return '﻿' + rows.map((r) => r.map(q).join(',')).join('\r\n') + '\r\n';
}

// ---------------------------------------------------------------- Router SKG-912MZ (Syntec)
//
// Mismo dialecto que los .nc de GuiGui (CONTEXTO §4.5): Z0 en la MESA, Z = espesor
// en la cara de arriba de la placa, Z38 seguro, CRLF, dos decimales.
// La pieza va con la CARA RANURADA ARRIBA (cara vista contra la mesa).
// Como Z0 es la mesa, el fondo de ranura Z = piel sale exacto aunque la placa
// venga más gruesa o más fina.
const f2 = (v) => (Math.round(v * 100) / 100).toFixed(2);

export function ncRouter(res, pz, cfg, tool) {
  // cfg: { x0, y0, sentido: 'Y'|'X', zSeg, fRapido, fBajada, fEntrada, fCorte, pasada,
  //        salida, encabezado, pie, nombre }
  const out = [];
  const t = res.t, s = res.s, H = res.H;
  const D = +tool.ancho;
  const zSeg = +cfg.zSeg || 38;
  const r = D / 2;
  const salida = (+cfg.salida || 2) + r;       // la fresa arranca y termina fuera de la placa
  const sub = (tpl) => (tpl || '').replace(/\{T\}/g, tool.t).replace(/\{S\}/g, tool.rpm || '')
    .replace(/\{nombre\}/g, cfg.nombre || '').replace(/\{zseg\}/g, f2(zSeg));
  const head = sub(cfg.encabezado).split(/\r?\n/).filter((l) => l.trim() !== '');
  out.push(...head);

  // placa en la mesa: el desarrollo corre en cfg.sentido. Coordenada en mesa:
  const XY = (xDes, yAlto) => (cfg.sentido === 'X'
    ? [cfg.x0 + xDes, cfg.y0 + yAlto]
    : [cfg.x0 + yAlto, cfg.y0 + xDes]);

  // niveles de profundidad (desde arriba hasta Z = piel)
  const esV = tool.tipo === 'v';
  const niveles = [];
  const pasada = esV ? t : Math.max(0.5, +cfg.pasada || t);
  for (let z = t - pasada; z > s + 1e-6; z -= pasada) niveles.push(z);
  niveles.push(s);

  // pasadas a lo ancho si la ranura es más ancha que la fresa
  const offsets = [];
  if (!esV && res.w > D + 0.01) {
    const extra = res.w - D;
    const nPas = Math.ceil(extra / (D * 0.8)) + 1;
    for (let k = 0; k < nPas; k++) offsets.push(-extra / 2 + (extra * k) / (nPas - 1));
  } else offsets.push(0);

  let ida = true;
  for (const rn of res.ranuras) {
    for (const off of offsets) {
      for (const z of niveles) {
        const ya = ida ? -salida : H + salida, yb = ida ? H + salida : -salida;
        const [ax, ay] = XY(rn.x + off, ya);
        const [bx, by] = XY(rn.x + off, yb);
        out.push(`G00 X${f2(ax)} Y${f2(ay)} F${cfg.fRapido}`);
        out.push(`G01 Z${f2(z)} F${cfg.fBajada}`);
        out.push(`G01 X${f2(bx)} Y${f2(by)} F${cfg.fCorte}`);
        ida = !ida;
      }
      out.push(`G00 Z${f2(zSeg)} F${cfg.fRapido}`);
    }
  }
  out.push(...sub(cfg.pie).split(/\r?\n/).filter((l) => l.trim() !== ''));
  return out.join('\r\n') + '\r\n';
}

// Contorno del rectángulo desarrollado, con el patrón de entrada de GuiGui
// (rampa de 80 mm sobre el lado de arriba, sobrepasada de 20 mm al cerrar).
export function ncContorno(res, cfg, tool) {
  const t = res.t, D = +tool.ancho, r = D / 2, zSeg = +cfg.zSeg || 38;
  const sub = (tpl) => (tpl || '').replace(/\{T\}/g, tool.t).replace(/\{S\}/g, tool.rpm || '')
    .replace(/\{nombre\}/g, cfg.nombre || '').replace(/\{zseg\}/g, f2(zSeg));
  const [W, Hh] = cfg.sentido === 'X' ? [res.L, res.H] : [res.H, res.L];
  const x0 = cfg.x0 - r, y0 = cfg.y0 - r, x1 = cfg.x0 + W + r, y1 = cfg.y0 + Hh + r;
  const out = sub(cfg.encabezado).split(/\r?\n/).filter((l) => l.trim() !== '');
  out.push(`G00 X${f2(x0 + 80)} Y${f2(y1)} F${cfg.fRapido}`,
    `G01 Z${f2(t)} F${cfg.fBajada}`,
    `G01 X${f2(x0)} Y${f2(y1)} Z-0.10 F${cfg.fEntrada}`,
    `G01 X${f2(x0)} Y${f2(y0)} F${cfg.fContorno}`,
    `G01 X${f2(x1)} Y${f2(y0)} F${cfg.fContorno}`,
    `G01 X${f2(x1)} Y${f2(y1)} F${cfg.fContorno}`,
    `G01 X${f2(x0 + 100)} Y${f2(y1)} F${cfg.fContorno}`,
    `G01 X${f2(x0)} Y${f2(y1)} F${cfg.fEntrada}.0`,
    `G00 Z${f2(zSeg)} F${cfg.fRapido}`);
  out.push(...sub(cfg.pie).split(/\r?\n/).filter((l) => l.trim() !== ''));
  return out.join('\r\n') + '\r\n';
}

// ---------------------------------------------------------------- pieza de máquina
// Arma la "Panel" para la perforadora a partir del resultado del motor.
//   cara: 'A' → ranuras en la cara de ARRIBA (husillos superiores), la cara vista
//               va contra la mesa.  'B' → ranuras por ABAJO (husillo inferior),
//               la cara vista queda arriba.
export function piezaMaquina(res, datos, cara, profundidad) {
  return {
    code: datos.codigo,
    name: datos.nombre,
    width: res.L, height: res.H, thickness: res.t,
    material: datos.materialCod, texture: datos.textura, grain: datos.veta,
    quantity: datos.cantidad || 1,
    edges: datos.cantos || {},
    slots: res.ranuras.map((r) => ({
      x1: r.x, y1: 0, x2: r.x, y2: res.H, width: r.ancho, depth: profundidad, face: cara,
    })),
    order_no: datos.orden || '', customer: datos.cliente || '', address: datos.direccion || '',
    room: '', location: datos.mueble || '', short_name: datos.nombre || '', plank_id: datos.placa || '',
  };
}
