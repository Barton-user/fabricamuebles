// Dibujos en SVG: planta curvada, detalle de ranura y plano de taller.
import { cinematica, seccion, deg } from './motor.js';
import { perfilIdeal } from './escena.js';

const NS = 'http://www.w3.org/2000/svg';
const fx = (v, d = 1) => (Math.round(v * 10 ** d) / 10 ** d).toLocaleString('es-AR', { maximumFractionDigits: d });

function poly(pts) { return pts.map((p) => `${p[0].toFixed(3)},${p[1].toFixed(3)}`).join(' '); }

// ------------------------------------------------------------- planta
export function svgPlanta(res, u, col) {
  if (!res.L) return '';
  const pts = seccion(res, Math.max(1, res.L / 800));
  const f = cinematica(res, u);
  const P = pts.map((p) => { const q = f(p.x, p.z); return [q[0], -q[1]]; });
  const ideal = perfilIdeal(res).map((q) => [q[0], -q[1]]);
  const all = P.concat(ideal);
  const xs = all.map((p) => p[0]), ys = all.map((p) => p[1]);
  const pad = Math.max(res.t * 3, (Math.max(...xs) - Math.min(...xs)) * 0.06);
  const vb = [Math.min(...xs) - pad, Math.min(...ys) - pad, Math.max(...xs) - Math.min(...xs) + 2 * pad, Math.max(...ys) - Math.min(...ys) + 2 * pad];
  const sw = vb[2] / 500;
  const s0 = f(0, 0);
  return `<svg xmlns="${NS}" viewBox="${vb.join(' ')}" class="dib">
    <polyline points="${poly(ideal)}" fill="none" stroke="var(--objetivo)" stroke-width="${sw * 1.2}" stroke-dasharray="${sw * 6} ${sw * 4}"/>
    <polygon points="${poly(P)}" fill="${col.nucleo}" stroke="var(--tinta)" stroke-width="${sw * 0.6}" stroke-linejoin="round"/>
    <circle cx="${s0[0]}" cy="${-s0[1]}" r="${sw * 5}" fill="#1f8a4c"/>
    <text x="${s0[0]}" y="${-s0[1] + sw * 22}" font-size="${sw * 13}" class="lbl" text-anchor="middle">INICIO</text>
  </svg>`;
}

// ------------------------------------------------------------- detalle de una ranura
// Muestra la zona alrededor de una ranura, plana y curvada, con la cara vista
// abajo y la ranura arriba, girada para que quede horizontal.
export function svgDetalle(res, idxRanura, u, col) {
  const r = res.ranuras[idxRanura];
  if (!r) return '<p class="vacio">No hay ranuras.</p>';
  const curva = res.tramos.find((t) => t.tipo === 'curva' && t.idx === r.curva);
  const ventana = Math.min(Math.max(curva.paso * 1.6, r.ancho * 2.2, res.t * 2.2), Math.max(res.t * 5, r.ancho * 1.4));
  const pts = seccion(res, 0.25).filter(() => true);
  const flat = cinematica(res, 0), bent = cinematica(res, u);
  const vista = (f) => {
    const o = f(r.x, 0), a = f.heading(r.x);
    const ca = Math.cos(-a), sa = Math.sin(-a);
    return pts.map((p) => { const q = f(p.x, p.z); const dx = q[0] - o[0], dy = q[1] - o[1]; return [dx * ca - dy * sa, -(dx * sa + dy * ca)]; });
  };
  const A = vista(flat), B = vista(bent);
  const W = ventana * 2, Hh = res.t * 3.2;
  const sw = W / 260;
  const clip = (id) => `<clipPath id="${id}"><rect x="${-ventana}" y="${-res.t * 1.9}" width="${W}" height="${Hh}"/></clipPath>`;
  const phi = Math.abs(r.phi) * u;
  const h = res.t - res.s / 2;
  const luz = r.tipo === 'v' ? r.ancho - 2 * res.profRanura * Math.tan(phi / 2) * 0 : r.abre ? r.ancho + phi * h : r.ancho - phi * h;
  const cot = (x1, x2, y, txt) => `<g class="cota"><line x1="${x1}" y1="${y}" x2="${x2}" y2="${y}" stroke-width="${sw * 0.7}"/>
      <line x1="${x1}" y1="${y - sw * 5}" x2="${x1}" y2="${y + sw * 5}" stroke-width="${sw * 0.7}"/><line x1="${x2}" y1="${y - sw * 5}" x2="${x2}" y2="${y + sw * 5}" stroke-width="${sw * 0.7}"/>
      <text x="${(x1 + x2) / 2}" y="${y - sw * 6}" font-size="${sw * 12}" text-anchor="middle">${txt}</text></g>`;
  const cotV = (x, y1, y2, txt) => `<g class="cota"><line x1="${x}" y1="${y1}" x2="${x}" y2="${y2}" stroke-width="${sw * 0.7}"/>
      <text x="${x + sw * 6}" y="${(y1 + y2) / 2 + sw * 4}" font-size="${sw * 12}">${txt}</text></g>`;
  const t = res.t, s = res.s;
  const panel = (pts2, id, titulo, extra) => `<svg xmlns="${NS}" viewBox="${-ventana} ${-t * 1.9} ${W} ${Hh}" class="dib det">
      <defs>${clip(id)}</defs>
      <g clip-path="url(#${id})">
        <polygon points="${poly(pts2)}" fill="${col.nucleo}" stroke="var(--tinta)" stroke-width="${sw}" stroke-linejoin="round"/>
        <line x1="${-ventana}" y1="${0}" x2="${ventana}" y2="0" stroke="${col.vista}" stroke-width="${sw * 3}" opacity="0.0"/>
      </g>
      <text x="${ventana - sw * 8}" y="${-t * 1.9 + sw * 16}" font-size="${sw * 13}" class="lbl" text-anchor="end">${titulo}</text>
      ${extra}
    </svg>`;
  const exA = [
    cot(-r.ancho / 2, r.ancho / 2, -t - sw * 14, r.tipo === 'v' ? `boca ${fx(r.ancho)}` : `ancho ${fx(r.ancho)}`),
    r.x + curva.paso < res.L ? cot(0, curva.paso, -t - sw * 34, `paso ${fx(curva.paso, 2)}`) : '',
    cotV(-ventana + sw * 30, 0, -s, `piel ${fx(s)}`),
    cotV(r.ancho / 2 + sw * 8, -s, -t, `prof ${fx(res.profRanura)}`),
    `<text x="${-ventana + sw * 8}" y="${t * 1.2}" font-size="${sw * 11}" class="lbl">cara vista ↓</text>`,
  ].join('');
  const exB = [
    `<text x="${-ventana + sw * 8}" y="${t * 1.05}" font-size="${sw * 12}" class="lbl">${r.abre ? 'la ranura se ABRE' : 'la ranura se CIERRA'} ${fx(deg(phi), 2)}° · ${r.tipo === 'v' ? 'caras de la V' : 'boca'} ${r.tipo === 'v' ? (Math.abs(deg(res.beta) - deg(phi)) < 0.05 ? 'se tocan' : `luz ${fx(deg(res.beta - phi), 1)}°`) : `${fx(Math.max(0, luz), 2)} mm`}</text>`,
  ].join('');
  return panel(A, 'ca', 'Plana, antes de curvar', exA) + panel(B, 'cb', `Curvada ${Math.round(u * 100)} %`, exB);
}

// ------------------------------------------------------------- plano de taller
export function svgPlano(res, datos, maq) {
  if (!res.L) return '';
  const L = res.L, H = res.H;
  const m = Math.max(L, H) * 0.06;
  const top = m * 2.6, left = m * 1.2;
  const W = L + left + m, Ht = H + top + m * 3.2;
  const sw = W / 900;
  const fs = sw * 13;
  const g = [];
  g.push(`<rect x="${left}" y="${top}" width="${L}" height="${H}" fill="#fff" stroke="#222" stroke-width="${sw * 1.4}"/>`);
  // tramos
  for (const tr of res.tramos) {
    if (tr.tipo === 'curva') g.push(`<rect x="${left + tr.x0}" y="${top}" width="${tr.largo}" height="${H}" fill="#e9f1fb"/>`);
    const lab = tr.tipo === 'recto' ? `Recto ${fx(tr.largo)}` : tr.tipo === 'sobrante' ? `Sobrante ${fx(tr.largo)}` : `R${fx(tr.R)} ${fx(tr.angulo)}° ${tr.convexa ? 'convexa' : 'cóncava'} · ${tr.N} ran. · paso ${fx(tr.paso, 2)}`;
    g.push(`<text x="${left + (tr.x0 + tr.x1) / 2}" y="${top + H + m * 0.9}" font-size="${fs}" text-anchor="middle">${lab}</text>`);
    g.push(`<line x1="${left + tr.x1}" y1="${top + H}" x2="${left + tr.x1}" y2="${top + H + m * 1.2}" stroke="#888" stroke-width="${sw * 0.7}"/>`);
  }
  // ranuras
  res.ranuras.forEach((r, i) => {
    g.push(`<rect x="${left + r.x - r.ancho / 2}" y="${top}" width="${Math.max(r.ancho, sw)}" height="${H}" fill="${r.abre ? '#e5a13a' : '#c0392b'}" opacity="0.85"/>`);
  });
  // cota acumulada de cada ranura desde INICIO, en vertical sobre su eje
  res.ranuras.forEach((r) => {
    const y = top - m * 0.12;
    g.push(`<line x1="${left + r.x}" y1="${top}" x2="${left + r.x}" y2="${y}" stroke="#555" stroke-width="${sw * 0.5}"/>`);
    g.push(`<text x="${left + r.x + fs * 0.3}" y="${y - sw * 2}" font-size="${fs * 0.78}" transform="rotate(-90 ${left + r.x + fs * 0.3} ${y - sw * 2})">${fx(r.x, 1)}</text>`);
  });
  // cotas generales
  g.push(`<line x1="${left}" y1="${top - m * 1.7}" x2="${left + L}" y2="${top - m * 1.7}" stroke="#222" stroke-width="${sw * 0.8}"/>`);
  g.push(`<text x="${left + L / 2}" y="${top - m * 1.85}" font-size="${fs * 1.2}" text-anchor="middle" font-weight="600">Desarrollo ${fx(L, 2)} mm</text>`);
  g.push(`<text x="${left - m * 0.35}" y="${top + H / 2}" font-size="${fs * 1.2}" text-anchor="middle" transform="rotate(-90 ${left - m * 0.35} ${top + H / 2})" font-weight="600">Alto ${fx(H, 2)}</text>`);
  g.push(`<text x="${left}" y="${top - m * 2.25}" font-size="${fs}" fill="#1f8a4c" font-weight="700">◀ INICIO</text>`);
  const info = [
    `${datos.nombre || ''} · código ${datos.codigo} · ${res.material.nombre} ${fx(res.t)} mm`,
    `${res.ranuras.length} ranuras ${res.esV ? `en V ${fx(deg(res.beta))}°` : `de ${fx(res.w)} mm`} · piel ${fx(res.s)} · ${maq}`,
    'Vista desde la CARA RANURADA (la de atrás). Ranuras pasantes de canto a canto. Cotas al eje de cada ranura, desde INICIO.',
    'Rojo: ranura que se cierra (cara vista convexa). Naranja: ranura que se abre (cara vista cóncava).',
  ];
  info.forEach((t, i) => g.push(`<text x="${left}" y="${top + H + m * (1.9 + i * 0.5)}" font-size="${fs * (i ? 0.95 : 1.1)}" ${i ? '' : 'font-weight="600"'}>${t}</text>`));
  return `<svg xmlns="${NS}" viewBox="0 0 ${W} ${Ht}" class="dib plano" font-family="Inter, Arial, sans-serif">${g.join('')}</svg>`;
}
