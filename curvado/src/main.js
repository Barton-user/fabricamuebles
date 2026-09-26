import * as XLSX from 'xlsx';
import { calcular, MATERIALES, deg } from './motor.js';
import { xml3, mpr, csvCorte, filaCorte, COLUMNAS, piezaMaquina, hasBackOps, ncRouter, ncContorno } from './exportar.js';
import { PERFORADORA, HERR_PERFORADORA, ROUTER, HERR_ROUTER, ROUTER_CFG, PRESETS_NC } from './herramientas.js';
import { Escena } from './escena.js';
import { svgPlanta, svgDetalle, svgPlano } from './vistas.js';
import { zip } from './zip.js';

const $ = (id) => document.getElementById(id);
const fx = (v, d = 1) => (Number.isFinite(v) ? (Math.round(v * 10 ** d) / 10 ** d).toLocaleString('es-AR', { maximumFractionDigits: d }) : '—');
const clone = (o) => JSON.parse(JSON.stringify(o));
const CLAVE = 'curvado.v1';

const PRESETS = {
  'Mostrador': { alto: 1000, segmentos: [{ tipo: 'recto', largo: 600 }, { tipo: 'curva', radio: 150, angulo: 90, lado: 'convexa' }, { tipo: 'recto', largo: 400 }] },
  'Esquina R100': { alto: 720, segmentos: [{ tipo: 'recto', largo: 400 }, { tipo: 'curva', radio: 100, angulo: 90, lado: 'convexa' }, { tipo: 'recto', largo: 400 }] },
  'Medio círculo': { alto: 900, segmentos: [{ tipo: 'curva', radio: 300, angulo: 180, lado: 'convexa' }] },
  'Onda S': { alto: 900, segmentos: [{ tipo: 'recto', largo: 200 }, { tipo: 'curva', radio: 400, angulo: 60, lado: 'convexa' }, { tipo: 'curva', radio: 400, angulo: 60, lado: 'concava' }, { tipo: 'recto', largo: 200 }] },
  'Cóncava R500': { alto: 900, segmentos: [{ tipo: 'recto', largo: 150 }, { tipo: 'curva', radio: 500, angulo: 90, lado: 'concava' }, { tipo: 'recto', largo: 150 }] },
};

const nuevoCodigo = () => { const d = new Date(); const p = (n) => String(n).padStart(2, '0'); return `999${p(d.getMonth() + 1)}${p(d.getDate())}${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`; };

const DEFAULT = {
  nombre: 'Frente mostrador curvo', codigo: nuevoCodigo(), orden: '', cliente: '', mueble: 'Mostrador', cantidad: 1,
  material: 'mdf_mel', decor: '#f1f0ec', espesor: 18, espesorReal: 18, piel: 2, alto: 1000, veta: '1', textura: 'Blanco',
  cArr: 1, cAbj: 1, cIzq: 0, cDer: 0,
  segmentos: PRESETS['Mostrador'].segmentos, sobIni: 0, sobFin: 0,
  maquina: 'router', tipo: 'paralela', herrSel: { perforadora: 'p187', router: 'r1' }, caraPerf: 'A',
  cierre: 90, tol: 0.2, costilla: 3, modoPaso: 'auto', pasoFijo: 15,
  herrP: HERR_PERFORADORA, herrR: HERR_ROUTER, router: { ...ROUTER_CFG, mesaX: ROUTER.mesaX, mesaY: ROUTER.mesaY },
};

let st;
try { st = { ...clone(DEFAULT), ...(JSON.parse(localStorage.getItem(CLAVE)) || {}) }; } catch { st = clone(DEFAULT); }
const guardar = () => { try { localStorage.setItem(CLAVE, JSON.stringify(st)); } catch { /* sin almacenamiento */ } };

// ------------------------------------------------------------------ formulario
const CAMPOS = ['nombre', 'codigo', 'orden', 'cliente', 'mueble', 'cantidad', 'material', 'decor', 'espesor', 'espesorReal', 'piel', 'alto',
  'veta', 'textura', 'cArr', 'cAbj', 'cIzq', 'cDer', 'sobIni', 'sobFin', 'caraPerf', 'cierre', 'tol', 'costilla', 'modoPaso', 'pasoFijo'];
const NUM = new Set(['cantidad', 'espesor', 'espesorReal', 'piel', 'alto', 'cArr', 'cAbj', 'cIzq', 'cDer', 'sobIni', 'sobFin', 'cierre', 'tol', 'costilla', 'pasoFijo']);

$('material').innerHTML = Object.entries(MATERIALES).map(([k, m]) => `<option value="${k}">${m.nombre}</option>`).join('');
$('presets').innerHTML = Object.keys(PRESETS).map((k) => `<button class="chico" data-p="${k}">${k}</button>`).join('');

function volcarForm() {
  CAMPOS.forEach((k) => { if ($(k)) $(k).value = st[k]; });
  document.querySelectorAll('#maquina button').forEach((b) => b.classList.toggle('on', b.dataset.v === st.maquina));
  document.querySelectorAll('#tipo button').forEach((b) => b.classList.toggle('on', b.dataset.v === st.tipo));
  $('lbl-cara').style.display = st.maquina === 'perforadora' ? '' : 'none';
  $('lbl-paso').style.display = st.modoPaso === 'fijo' ? '' : 'none';
  $('ncHead').value = st.router.encabezado; $('ncFoot').value = st.router.pie;
  segs(); herrSelect(); tablas(); cfgRouter();
}

CAMPOS.forEach((k) => $(k) && $(k).addEventListener('input', () => {
  const v = $(k).value;
  st[k] = NUM.has(k) ? parseFloat(v) : v;
  if (k === 'material') { st.piel = MATERIALES[v].piel; $('piel').value = st.piel; }
  if (k === 'espesor' && Math.abs(st.espesorReal - st.espesor) > 3) { st.espesorReal = st.espesor; $('espesorReal').value = st.espesor; }
  if (k === 'caraPerf') herrSelect();
  if (k === 'modoPaso') $('lbl-paso').style.display = st.modoPaso === 'fijo' ? '' : 'none';
  calc(k === 'decor' ? false : ['espesor', 'alto', 'sobIni', 'sobFin', 'piel'].includes(k));
}));
$('btn-codigo').onclick = () => { st.codigo = nuevoCodigo(); $('codigo').value = st.codigo; calc(); };
document.querySelectorAll('#maquina button').forEach((b) => b.onclick = () => { st.maquina = b.dataset.v; volcarForm(); calc(); });
document.querySelectorAll('#tipo button').forEach((b) => b.onclick = () => { st.tipo = b.dataset.v; volcarForm(); calc(); });
$('presets').onclick = (e) => { const p = e.target.dataset.p; if (!p) return; st.segmentos = clone(PRESETS[p].segmentos); st.alto = PRESETS[p].alto; $('alto').value = st.alto; segs(); calc(true); };
$('add-recto').onclick = () => { st.segmentos.push({ tipo: 'recto', largo: 300 }); segs(); calc(true); };
$('add-curva').onclick = () => { st.segmentos.push({ tipo: 'curva', radio: 200, angulo: 90, lado: 'convexa' }); segs(); calc(true); };
$('ncHead').oninput = () => { st.router.encabezado = $('ncHead').value; calc(); };
$('ncFoot').oninput = () => { st.router.pie = $('ncFoot').value; calc(); };

function segs() {
  $('segs').innerHTML = st.segmentos.map((s, i) => `
    <div class="seg-row ${s.tipo}" data-i="${i}">
      <span class="num">${i + 1}</span>
      <div class="campos">${s.tipo === 'recto'
        ? `<label>Recto · largo<input data-k="largo" type="number" value="${s.largo}"/></label><span></span><span></span><span></span>`
        : `<label>Radio<input data-k="radio" type="number" value="${s.radio}"/></label>
           <label>Ángulo °<input data-k="angulo" type="number" value="${s.angulo}"/></label>
           <label>Cara vista<select data-k="lado"><option value="convexa" ${s.lado !== 'concava' ? 'selected' : ''}>Convexa</option><option value="concava" ${s.lado === 'concava' ? 'selected' : ''}>Cóncava</option></select></label>
           <label>Ranuras<input data-k="n" type="number" min="0" placeholder="auto" value="${s.n || ''}"/></label>`}
      </div>
      <div class="btns"><button data-a="up" title="Subir">▲</button><button data-a="del" title="Borrar">✕</button><button data-a="down" title="Bajar">▼</button></div>
    </div>`).join('');
}
$('segs').addEventListener('input', (e) => {
  const row = e.target.closest('.seg-row'); if (!row) return;
  const s = st.segmentos[+row.dataset.i], k = e.target.dataset.k;
  s[k] = k === 'lado' ? e.target.value : (e.target.value === '' ? 0 : parseFloat(e.target.value));
  calc(true);
});
$('segs').addEventListener('click', (e) => {
  const a = e.target.dataset.a; if (!a) return;
  const i = +e.target.closest('.seg-row').dataset.i, S = st.segmentos;
  if (a === 'del') S.splice(i, 1);
  if (a === 'up' && i > 0) [S[i - 1], S[i]] = [S[i], S[i - 1]];
  if (a === 'down' && i < S.length - 1) [S[i + 1], S[i]] = [S[i], S[i + 1]];
  segs(); calc(true);
});

// ------------------------------------------------------------------ herramientas
const lista = (m) => (m === 'perforadora' ? st.herrP : st.herrR);
function herrValidas(m, tipo = st.tipo) {
  return lista(m).filter((h) => (tipo === 'v' ? h.tipo === 'v' : h.tipo !== 'v') && (m !== 'perforadora' || (h.cara || 'A') === st.caraPerf));
}
function herrDe(m) {
  const vs = herrValidas(m);
  let h = vs.find((x) => x.id === st.herrSel[m]);
  if (!h) { h = vs[0]; if (h) st.herrSel[m] = h.id; }
  return h;
}
function herrSelect() {
  const vs = herrValidas(st.maquina);
  const h = herrDe(st.maquina);
  $('herr').innerHTML = vs.length ? vs.map((x) => `<option value="${x.id}" ${h && x.id === h.id ? 'selected' : ''}>${etiquetaHerr(x)}</option>`).join('')
    : '<option value="">— ninguna para esta combinación —</option>';
}
const etiquetaHerr = (x) => `${x.t.startsWith('T') ? x.t : 'T' + x.t} · ${x.tipo === 'v' ? `V ${x.anguloV}°` : x.tipo === 'disco' ? `disco ${x.ancho} mm` : `recta Ø${x.ancho}`}`;
$('herr').onchange = () => { st.herrSel[st.maquina] = $('herr').value; calc(); };

const COLS_P = [['t', 'T', 't'], ['tipo', 'Tipo', 'sel'], ['ancho', 'Ancho/Ø', 'n'], ['profMax', 'Prof. máx', 'n'], ['cara', 'Cara', 'cara'], ['nota', 'Nota', 't']];
const COLS_R = [['t', 'T', 't'], ['tipo', 'Tipo', 'sel'], ['ancho', 'Ø', 'n'], ['anguloV', 'V°', 'n'], ['largoCorte', 'Largo corte', 'n'], ['rpm', 'rpm', 'n'], ['nota', 'Nota', 't']];
function tabla(el, arr, cols) {
  el.innerHTML = `<table><tr>${cols.map((c) => `<th>${c[1]}</th>`).join('')}<th></th></tr>${arr.map((h, i) => `<tr data-i="${i}">${cols.map(([k, , ty]) => {
    if (ty === 'sel') return `<td><select data-k="${k}">${['recta', 'disco', 'v'].map((o) => `<option ${h[k] === o ? 'selected' : ''}>${o}</option>`).join('')}</select></td>`;
    if (ty === 'cara') return `<td><select data-k="${k}"><option value="A" ${h[k] !== 'B' ? 'selected' : ''}>A arriba</option><option value="B" ${h[k] === 'B' ? 'selected' : ''}>B abajo</option></select></td>`;
    return `<td class="${ty}"><input data-k="${k}" ${ty === 'n' ? 'type="number" step="0.1"' : ''} value="${h[k] ?? ''}"/></td>`;
  }).join('')}<td><button class="chico" data-del="1">✕</button></td></tr>`).join('')}</table>`;
}
function tablas() { tabla($('tab-perf'), st.herrP, COLS_P); tabla($('tab-router'), st.herrR, COLS_R); }
for (const [id, key] of [['tab-perf', 'herrP'], ['tab-router', 'herrR']]) {
  $(id).addEventListener('change', (e) => {
    const tr = e.target.closest('tr'); const k = e.target.dataset.k; if (!tr || !k) return;
    const h = st[key][+tr.dataset.i];
    h[k] = e.target.type === 'number' ? parseFloat(e.target.value) : e.target.value;
    herrSelect(); calc();
  });
  $(id).addEventListener('click', (e) => {
    if (!e.target.dataset.del) return;
    st[key].splice(+e.target.closest('tr').dataset.i, 1); tablas(); herrSelect(); calc();
  });
}
$('add-hp').onclick = () => { st.herrP.push({ id: 'p' + Date.now(), t: 'T', tipo: 'recta', ancho: 6, profMax: 20, cara: 'A', nota: '' }); tablas(); };
$('add-hr').onclick = () => { st.herrR.push({ id: 'r' + Date.now(), t: '3', tipo: 'recta', ancho: 6, anguloV: 90, largoCorte: 20, rpm: 18000, nota: '' }); tablas(); };

const CFG_R = [['x0', 'Origen X pieza'], ['y0', 'Origen Y pieza'], ['sentido', 'Desarrollo a lo largo de'], ['mesaX', 'Mesa útil X'], ['mesaY', 'Mesa útil Y'],
  ['zSeg', 'Z seguro'], ['pasada', 'Prof. por pasada'], ['salida', 'Salida fuera de la placa'], ['fRapido', 'F rápido'], ['fBajada', 'F bajada'],
  ['fCorte', 'F ranurado'], ['fContorno', 'F contorno'], ['fEntrada', 'F entrada contorno'], ['preset', 'Encabezado'], ['contorno', 'Cortar también el contorno'], ['herrContorno', 'Herramienta contorno']];
function cfgRouter() {
  const c = st.router;
  $('cfg-router').innerHTML = CFG_R.map(([k, l]) => {
    if (k === 'sentido') return `<label>${l}<select data-k="${k}"><option value="Y" ${c[k] === 'Y' ? 'selected' : ''}>Y (lado largo)</option><option value="X" ${c[k] === 'X' ? 'selected' : ''}>X</option></select></label>`;
    if (k === 'preset') return `<label>${l}<select data-k="${k}">${Object.entries(PRESETS_NC).map(([pk, p]) => `<option value="${pk}" ${c.preset === pk ? 'selected' : ''}>${p.nombre}</option>`).join('')}<option value="custom" ${c.preset === 'custom' ? 'selected' : ''}>A mano</option></select></label>`;
    if (k === 'contorno') return `<label class="inl"><input type="checkbox" data-k="${k}" ${c[k] ? 'checked' : ''} style="width:auto"/> ${l}</label>`;
    if (k === 'herrContorno') return `<label>${l}<select data-k="${k}">${st.herrR.filter((h) => h.tipo === 'recta').map((h) => `<option value="${h.id}" ${c[k] === h.id ? 'selected' : ''}>${etiquetaHerr(h)}</option>`).join('')}</select></label>`;
    return `<label>${l}<input data-k="${k}" type="number" value="${c[k]}"/></label>`;
  }).join('');
}
$('cfg-router').addEventListener('change', (e) => {
  const k = e.target.dataset.k; if (!k) return;
  const c = st.router;
  c[k] = e.target.type === 'checkbox' ? e.target.checked : e.target.type === 'number' ? parseFloat(e.target.value) : e.target.value;
  if (k === 'preset' && PRESETS_NC[c.preset]) { c.encabezado = PRESETS_NC[c.preset].encabezado; c.pie = PRESETS_NC[c.preset].pie; $('ncHead').value = c.encabezado; $('ncFoot').value = c.pie; }
  calc();
});

// ------------------------------------------------------------------ cálculo
const NUCLEO = { mdf_mel: '#b58c62', agl_mel: '#cdb189', multi: '#d9b98b', mdf_crudo: '#b58c62' };

function params(m) {
  const h = herrDe(m);
  return {
    herr: h,
    p: {
      espesor: st.espesor, piel: st.piel, alto: st.alto, material: st.material, tipo: st.tipo,
      ancho: h ? +h.ancho : 0, anguloV: h ? +h.anguloV || 90 : 90,
      cierreMax: st.cierre / 100, tolFaceta: st.tol, costillaMin: st.costilla, modoPaso: st.modoPaso, pasoFijo: st.pasoFijo,
      sobranteIni: st.sobIni, sobranteFin: st.sobFin, segmentos: st.segmentos,
    },
  };
}

function chequeosMaquina(m, res, h) {
  const av = [];
  const E = (txt) => av.push({ nivel: 'error', txt }), W = (txt) => av.push({ nivel: 'aviso', txt }), I = (txt) => av.push({ nivel: 'info', txt });
  if (!h) { E(st.tipo === 'v' ? `La ${m === 'router' ? 'tabla del router' : 'perforadora'} no tiene ninguna fresa en V cargada.` : 'No hay herramienta cargada para esta combinación.'); return av; }
  if (m === 'perforadora') {
    const P = PERFORADORA;
    const prof = st.espesorReal - st.piel;
    if (st.tipo === 'v') E('La SKH-612HS no tiene fresa en V: el ranurado facetado va por router.');
    const lg = Math.max(res.L, res.H), co = Math.min(res.L, res.H);
    if (lg > P.largoMax || co > P.anchoMax) E(`La pieza (${fx(res.L)} × ${fx(res.H)}) no entra en la perforadora: máximo ${P.largoMax} × ${P.anchoMax}.`);
    if (lg < P.largoMin || co < P.anchoMin) E(`La pieza es chica para la perforadora: mínimo ${P.largoMin} × ${P.anchoMin}.`);
    if (st.espesor < P.espMin || st.espesor > P.espMax) E(`Espesor fuera de rango (${P.espMin}–${P.espMax}).`);
    if (prof > +h.profMax) E(`La ${h.t} llega a ${h.profMax} mm y la ranura pide ${fx(prof, 2)} mm.`);
    if (h.tipo === 'disco') W(`${h.t} es un disco: la profundidad máxima real está sin medir. Verificar antes de mandar la pieza.`);
    if (h.t === 'T184') W('La T184 es espiral de corte ascendente: en la cara de arriba desgarra la melamina. Acá la cara de arriba es la de atrás, así que no se ve, pero conviene una downcut.');
    I(st.caraPerf === 'A'
      ? 'Perforadora: ranuras en la cara de ARRIBA (TypeNo 3). Cargar la placa con la CARA VISTA CONTRA LA MESA.'
      : 'Perforadora: ranuras por ABAJO con el husillo inferior (TypeNo 13 / archivo K del MPR). La cara vista queda arriba.');
    I(`Profundidad programada ${fx(prof, 2)} mm desde la cara ${st.caraPerf === 'A' ? 'de arriba' : 'de abajo'} (espesor real ${fx(st.espesorReal, 2)} − piel ${fx(st.piel, 2)}). Si la placa varía de espesor, varía la piel.`);
  } else {
    const c = st.router;
    const [W2, H2] = c.sentido === 'X' ? [res.L, res.H] : [res.H, res.L];
    if (c.x0 + W2 > c.mesaX || c.y0 + H2 > c.mesaY) E(`La pieza (${fx(W2)} × ${fx(H2)} en la mesa, desde ${c.x0},${c.y0}) no entra en la mesa útil ${c.mesaX} × ${c.mesaY}. Probar el otro sentido.`);
    if (+h.largoCorte < res.profRanura) E(`La fresa T${h.t} corta ${h.largoCorte} mm de largo y la ranura tiene ${fx(res.profRanura, 2)}.`);
    if (/CONFIRMAR/i.test(h.nota || '')) W(`La herramienta T${h.t} del router está marcada A CONFIRMAR.`);
    if (st.tipo !== 'v' && res.w > +h.ancho + 0.01) I('La ranura es más ancha que la fresa: el .nc hace pasadas a lo ancho.');
    const nPas = st.tipo === 'v' ? 1 : Math.ceil((st.espesor - st.piel) / Math.max(0.5, c.pasada) - 1e-9);
    I(`Router: placa con la CARA VISTA CONTRA LA MESA. Z0 en la mesa, fondo de ranura en Z ${fx(st.piel, 2)}: la piel sale exacta aunque la placa varíe. ${nPas} pasada${nPas > 1 ? 's' : ''} por ranura, entrando y saliendo fuera de la placa.`);
  }
  return av;
}

let RES = {}, datos = {}, escena, primera = true;
function calc(encuadrar = false) {
  guardar();
  datos = {
    codigo: st.codigo, nombre: st.nombre, materialCod: MATERIALES[st.material].nombre, textura: st.textura, veta: st.veta,
    cantos: { up: st.cArr, down: st.cAbj, left: st.cIzq, right: st.cDer }, orden: st.orden, cliente: st.cliente, mueble: st.mueble, cantidad: st.cantidad,
  };
  for (const m of ['perforadora', 'router']) {
    const { herr, p } = params(m);
    const res = calcular(p);
    res.herr = herr;
    res.avisos = [...chequeosMaquina(m, res, herr), ...res.avisos];
    res.ok = !res.avisos.some((a) => a.nivel === 'error');
    RES[m] = res;
  }
  const res = RES[st.maquina];
  const col = { vista: st.decor, nucleo: NUCLEO[st.material], ranura: '#c0392b', objetivo: getComputedStyle(document.documentElement).getPropertyValue('--objetivo').trim() || '#1f5fbf' };
  document.documentElement.style.setProperty('--l-vista', st.decor);
  if (!escena) escena = new Escena($('gl'));
  escena.setFondo(getComputedStyle(document.documentElement).getPropertyValue('--gl').trim() || '#eceae4');
  escena.u = +$('u').value / 100;
  escena.cargar(res, col, encuadrar || primera);
  primera = false;
  selRanuras(res);
  dibujar();
  resumen(res);
  exportes();
}

function selRanuras(res) {
  const prev = $('selRan').value;
  const opts = []; let def = 0;
  const curvas = res.tramos.filter((t) => t.tipo === 'curva');
  let idx = 0;
  curvas.forEach((c, ci) => { for (let k = 0; k < c.N; k++, idx++) { opts.push(`<option value="${idx}">Curva ${ci + 1} · ranura ${k + 1}/${c.N}</option>`); if (ci === 0 && k === Math.floor(c.N / 2)) def = idx; } });
  $('selRan').innerHTML = opts.join('');
  $('selRan').value = prev && +prev < idx ? prev : def;
}
$('selRan').onchange = () => dibujar();

function colores() { return { vista: st.decor, nucleo: NUCLEO[st.material] }; }
function dibujar() {
  const res = RES[st.maquina]; const u = +$('u').value / 100;
  $('u-lbl').textContent = `${Math.round(u * 100)} %`;
  $('detalle').innerHTML = svgDetalle(res, +$('selRan').value || 0, u, colores());
  $('planta').innerHTML = svgPlanta(res, u, colores());
  $('plano').innerHTML = svgPlano(res, datos, maqTxt(st.maquina, res));
}
const maqTxt = (m, res) => (m === 'router' ? `Router SKG-912MZ · T${res.herr?.t ?? '?'}` : `Perforadora SKH-612HS · ${res.herr?.t ?? '?'} · cara ${st.caraPerf}`);

function resumen(res) {
  const curvas = res.tramos.filter((t) => t.tipo === 'curva');
  const corteL = res.L - st.cIzq - st.cDer, corteH = res.H - st.cArr - st.cAbj;
  $('resumen').innerHTML = `
    <div class="big">
      <div><b>${fx(res.L, 2)}</b><span>desarrollo (mm)</span></div>
      <div><b>${fx(corteL, 1)} × ${fx(corteH, 1)}</b><span>medida de corte sierra</span></div>
      <div><b>${res.ranuras.length}</b><span>ranuras · prof ${fx(res.profRanura, 2)} · ${res.esV ? `V ${fx(deg(res.beta))}°` : `ancho ${fx(res.w)}`}</span></div>
    </div>
    <table><tr><th>Tramo</th><th>Largo</th><th title="ranuras (mínimo)">Ran.</th><th>Paso</th><th title="costilla">Cost.</th><th>Cierre</th><th title="flecha del facetado">Flecha</th><th title="estiramiento de la piel">ε piel</th></tr>
    ${res.tramos.map((t, i) => t.tipo === 'curva'
      ? `<tr><td title="${t.convexa ? 'convexa' : 'cóncava'}">R${fx(t.R)} ${fx(t.angulo)}° ${t.convexa ? '⌒' : '⌣'}</td><td>${fx(t.largo, 1)}</td><td>${t.N} <small>(${t.Nmin})</small></td><td>${fx(t.paso, 2)}</td><td>${fx(t.costilla, 1)}</td><td>${t.convexa ? fx(t.cierre * 100, 0) + ' %' : 'abre'}</td><td>${fx(t.flecha, 2)}</td><td>${fx(t.eps, 2)}%</td></tr>`
      : `<tr><td>${t.tipo === 'recto' ? 'Recto' : 'Sobrante'}</td><td>${fx(t.largo, 1)}</td><td colspan="6"></td></tr>`).join('')}
    </table>`;
  const orden = { error: 0, aviso: 1, info: 2 };
  $('avisos').innerHTML = [...res.avisos].sort((a, b) => orden[a.nivel] - orden[b.nivel]).map((a) => `<li class="${a.nivel}">${a.txt}</li>`).join('');
  if (!curvas.length) $('resumen').insertAdjacentHTML('beforeend', '<p class="vacio">Agregá una curva al perfil.</p>');
}

// ------------------------------------------------------------------ exportes
function archivos() {
  const f = [];
  const code = st.codigo;
  const pzBase = piezaMaquina(RES.router, datos, 'A', 0);  // la lista de corte no depende de la herramienta
  f.push({ m: 'sierra', name: 'SIERRA/lista_corte.csv', data: csvCorte([pzBase]), mime: 'text/csv' });
  const ws = XLSX.utils.aoa_to_sheet([COLUMNAS, filaCorte(pzBase, 1)]);
  const wb = XLSX.utils.book_new(); XLSX.utils.book_append_sheet(wb, ws, '开料清单');
  f.push({ m: 'sierra', name: 'SIERRA/lista_corte.xlsx', data: new Uint8Array(XLSX.write(wb, { type: 'array', bookType: 'xlsx' })), mime: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });

  const rp = RES.perforadora;
  if (rp.ok) {
    const pz = piezaMaquina(rp, datos, st.caraPerf, st.espesorReal - st.piel);
    f.push({ m: 'perforadora', name: `PERFORADORA/XML3/${code}.xml`, data: xml3(pz), mime: 'application/xml' });
    const gbk = (s) => new TextEncoder().encode(s);   // el texto ya es ASCII: GBK == UTF-8
    if (pz.slots.some((s) => s.face === 'A')) f.push({ m: 'perforadora', name: `PERFORADORA/MPR/${code}.mpr`, data: gbk(mpr(pz, false)), mime: 'text/plain' });
    if (hasBackOps(pz)) f.push({ m: 'perforadora', name: `PERFORADORA/MPR/${code}K.mpr`, data: gbk(mpr(pz, true)), mime: 'text/plain' });
    f.push({ m: 'perforadora', name: `PERFORADORA/${code}_plano.svg`, data: svgPlano(rp, datos, maqTxt('perforadora', rp)), mime: 'image/svg+xml' });
  }
  const rr = RES.router;
  if (rr.ok) {
    const cfg = { ...st.router, nombre: st.nombre };
    f.push({ m: 'router', name: `ROUTER/${code}_ranuras_T${rr.herr.t}.nc`, data: ncRouter(rr, null, cfg, rr.herr), mime: 'text/plain' });
    if (st.router.contorno) {
      const hc = st.herrR.find((h) => h.id === st.router.herrContorno) || st.herrR.find((h) => h.tipo === 'recta');
      if (hc) f.push({ m: 'router', name: `ROUTER/${code}_contorno_T${hc.t}.nc`, data: ncContorno(rr, cfg, hc), mime: 'text/plain' });
    }
    f.push({ m: 'router', name: `ROUTER/${code}_plano.svg`, data: svgPlano(rr, datos, maqTxt('router', rr)), mime: 'image/svg+xml' });
  }
  return f;
}

function leeme(f) {
  const L = [];
  const lin = (m, r) => {
    L.push(`--- ${m.toUpperCase()} ---`);
    if (!r.ok) L.push('NO SE GENERO. Errores:', ...r.avisos.filter((a) => a.nivel === 'error').map((a) => '  - ' + a.txt));
    else {
      L.push(`Herramienta ${String(r.herr.t).startsWith('T') ? r.herr.t : 'T' + r.herr.t} · ${r.ranuras.length} ranuras · profundidad ${fx(r.profRanura, 2)} · desarrollo ${fx(r.L, 2)} x ${fx(r.H, 2)}`);
      L.push(...r.avisos.filter((a) => a.nivel !== 'info' || /Cargar|CARA VISTA|Profundidad|Z0/.test(a.txt)).map((a) => '  - ' + a.txt));
      L.push('  Ejes de ranura desde INICIO: ' + r.ranuras.map((x) => fx(x.x, 2)).join(' · '));
    }
    L.push('');
  };
  L.push(`CURVADO POR RANURAS — ${st.nombre}`, `Codigo ${st.codigo} · ${MATERIALES[st.material].nombre} ${st.espesor} mm · piel ${st.piel} · alto ${st.alto}`,
    `Perfil: ${st.segmentos.map((s) => (s.tipo === 'recto' ? `recto ${s.largo}` : `R${s.radio} ${s.angulo}° ${s.lado}`)).join(' + ')}`, '',
    'SIERRA: lista_corte.csv / .xlsx con las mismas columnas que el 开料清单 de GuiGui (mapeo de AutoCUT ya cargado).', '');
  lin('perforadora', RES.perforadora); lin('router', RES.router);
  L.push('Archivos:', ...f.map((x) => '  ' + x.name));
  return L.join('\r\n');
}

function bajar(name, data, mime) {
  const blob = data instanceof Blob ? data : new Blob([data], { type: mime || 'application/octet-stream' });
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name.split('/').pop();
  document.body.appendChild(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 500);
}

function exportes() {
  const f = archivos();
  const grupo = (m, titulo, desc) => {
    const fs = f.filter((x) => x.m === m);
    const r = RES[m];
    const errs = r && !r.ok && m !== 'sierra' ? r.avisos.filter((a) => a.nivel === 'error').map((a) => a.txt) : [];
    const prev = fs.find((x) => typeof x.data === 'string' && !x.name.endsWith('.svg'));
    return `<div class="exp ${fs.length ? '' : 'off'}"><h4>${titulo}</h4><p>${desc}</p>
      ${errs.length ? `<p class="err">${errs.join('<br>')}</p>` : ''}
      <div class="bs">${fs.map((x) => `<button class="chico" data-f="${x.name}">${x.name.split('/').pop()}</button>`).join('')}</div>
      ${prev ? `<pre class="mono">${prev.data.split(/\r?\n/).slice(0, 14).join('\n').replace(/</g, '&lt;')}\n…</pre>` : ''}</div>`;
  };
  $('exportes').innerHTML =
    grupo('sierra', 'Sierra HP280 · AutoCUT', 'Rectángulo desarrollado. Mismas columnas que el 开料清单.xls de GuiGui.') +
    grupo('perforadora', `Perforadora SKH-612HS · ${RES.perforadora.herr?.t ?? ''}`, 'XML3 → formato "KDTXml". MPR → "Haomai MPR". Nombre de archivo = código de barras.') +
    grupo('router', `Router SKG-912MZ · T${RES.router.herr?.t ?? ''}`, 'G-code Syntec, mismo dialecto que los .nc de GuiGui (Z0 mesa, CRLF).');
  $('exportes').onclick = (e) => { const n = e.target.dataset.f; if (!n) return; const x = archivos().find((y) => y.name === n); if (x) bajar(x.name, x.data, x.mime); };
}

$('btn-zip').onclick = () => {
  const f = archivos();
  const png = escena.png();
  const bin = Uint8Array.from(atob(png.split(',')[1]), (c) => c.charCodeAt(0));
  const todo = [...f, { name: `${st.codigo}_3d.png`, data: bin }, { name: 'LEEME.txt', data: leeme(f) }];
  bajar(`${st.codigo}_curvado.zip`, zip(todo.map((x) => ({ name: `${st.codigo}/${x.name}`, data: x.data }))));
};
$('dl-plano').onclick = () => bajar(`${st.codigo}_plano.svg`, svgPlano(RES[st.maquina], datos, maqTxt(st.maquina, RES[st.maquina])), 'image/svg+xml');

// ------------------------------------------------------------------ animación
$('u').oninput = () => { escena.curvar(+$('u').value / 100); dibujar(); };
$('encuadrar').onclick = () => escena.encuadrar();
$('lado').onclick = () => escena.encuadrar(!escena.lado);
let anim = null;
$('play').onclick = () => {
  if (anim) { cancelAnimationFrame(anim); anim = null; $('play').textContent = '▶ Curvar'; return; }
  const u0 = +$('u').value >= 100 ? 0 : +$('u').value / 100;
  const t0 = performance.now(), dur = 2600 * (1 - u0);
  $('play').textContent = '■ Parar';
  const paso = (t) => {
    const k = Math.min(1, (t - t0) / dur), u = u0 + (1 - u0) * (0.5 - 0.5 * Math.cos(Math.PI * k));
    $('u').value = Math.round(u * 100); escena.curvar(u); dibujar();
    if (k < 1) anim = requestAnimationFrame(paso); else { anim = null; $('play').textContent = '▶ Curvar'; }
  };
  anim = requestAnimationFrame(paso);
};

// pestañas del formulario
$('tabs').onclick = (e) => {
  const t = e.target.dataset.t; if (!t) return;
  st.tab = t; guardar();
  document.querySelectorAll('#tabs button').forEach((b) => b.classList.toggle('on', b.dataset.t === t));
  document.querySelectorAll('.tab-body section').forEach((s) => s.classList.toggle('on', s.dataset.tab === t));
};
if (st.tab) $('tabs').querySelector(`[data-t="${st.tab}"]`)?.click();

// plano en grande
const verPlano = () => { $('plano-grande').innerHTML = svgPlano(RES[st.maquina], datos, maqTxt(st.maquina, RES[st.maquina])); $('dlg-plano').showModal(); };
$('ver-plano').onclick = verPlano;
$('plano').onclick = verPlano;

volcarForm();
calc(true);
