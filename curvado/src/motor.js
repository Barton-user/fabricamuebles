// Motor de cálculo del curvado por ranuras (kerf bending).
//
// Convenciones (las mismas de etapa2/panel.py, CONTEXTO §3):
//   x  = a lo largo del DESARROLLO de la pieza, 0 en el extremo INICIO (mm)
//   y  = a lo alto de la pieza (las ranuras corren en y, de canto a canto)
//   z  = dentro del espesor, 0 en la CARA VISTA, t en la cara ranurada
//
// La cara vista nunca se toca: es la "piel" que queda entera. Las ranuras van
// siempre por la cara de atrás. En una curva CONVEXA (la cara vista queda afuera)
// las ranuras quedan del lado cóncavo y se CIERRAN al curvar. En una CÓNCAVA
// (la cara vista queda adentro) las ranuras quedan del lado convexo y se ABREN.
//
// La línea de desarrollo es el plano medio de la piel (z = s/2): es la que no
// cambia de largo al curvar.

export const MATERIALES = {
  mdf_mel:  { nombre: 'Melamina MDF',          piel: 2.0, epsMax: 1.2, nota: 'La más pareja para ranurar.' },
  agl_mel:  { nombre: 'Melamina aglomerado',   piel: 3.0, epsMax: 0.7, nota: 'El aglomerado se desgrana en la piel: dejar más piel y radios más grandes.' },
  multi:    { nombre: 'Multilaminado',          piel: 2.5, epsMax: 1.5, nota: 'Conviene que la piel sea una o dos chapas enteras; la veta de la chapa exterior tiene que correr a lo largo del desarrollo.' },
  mdf_crudo:{ nombre: 'MDF crudo / enchapar',  piel: 2.0, epsMax: 1.2, nota: 'Para laquear o enchapar después; se puede masillar el facetado.' },
};

export const deg = (r) => (r * 180) / Math.PI;
export const rad = (d) => (d * Math.PI) / 180;

/**
 * Calcula el desarrollo y las ranuras.
 * p: {
 *   espesor, piel, alto, material,
 *   tipo: 'paralela' | 'v',
 *   ancho,            // ancho de ranura (paralela) = ancho de la herramienta
 *   anguloV,          // ángulo incluido de la fresa en V (grados)
 *   puenteV,          // ancho de la punta/puente de la V (mm), solo para dibujar
 *   cierreMax,        // fracción máxima de cierre admitida (0..1), ranuras que cierran
 *   tolFaceta,        // flecha máxima admitida entre ranuras (mm)
 *   costillaMin,      // costilla mínima entre ranuras (mm)
 *   modoPaso: 'auto' | 'fijo', pasoFijo,
 *   sobranteIni, sobranteFin,
 *   segmentos: [{tipo:'recto', largo} | {tipo:'curva', radio, angulo, lado:'convexa'|'concava', n?}]
 * }
 */
export function calcular(p) {
  const t = +p.espesor, s = +p.piel, H = +p.alto;
  const mat = MATERIALES[p.material] || MATERIALES.mdf_mel;
  const avisos = [];      // {nivel:'error'|'aviso'|'info', txt}
  const tramos = [];      // tramos del desarrollo
  const ranuras = [];     // {x, ancho, prof, curva, phi, tipo, boca}
  const esV = p.tipo === 'v';
  const w = esV ? 0 : +p.ancho;
  const beta = rad(+p.anguloV || 90);
  const profRanura = t - s;
  const bocaV = 2 * profRanura * Math.tan(beta / 2);

  if (!(t > 0)) avisos.push({ nivel: 'error', txt: 'El espesor tiene que ser mayor que cero.' });
  if (!(s > 0) || s >= t) avisos.push({ nivel: 'error', txt: 'La piel tiene que ser mayor que cero y menor que el espesor.' });
  if (!esV && !(w > 0)) avisos.push({ nivel: 'error', txt: 'Falta el ancho de ranura (el de la herramienta).' });

  let x = +p.sobranteIni || 0;
  if (x > 0) tramos.push({ tipo: 'sobrante', x0: 0, x1: x, largo: x });

  (p.segmentos || []).forEach((seg, i) => {
    if (seg.tipo === 'recto') {
      const L = Math.max(0, +seg.largo || 0);
      tramos.push({ tipo: 'recto', idx: i, x0: x, x1: x + L, largo: L });
      x += L;
      return;
    }
    // --- curva ---
    const R = +seg.radio, thDeg = +seg.angulo, th = rad(thDeg);
    const convexa = seg.lado !== 'concava';
    const c = { tipo: 'curva', idx: i, R, angulo: thDeg, convexa, avisos: [] };
    if (!(R > 0) || !(th > 0)) {
      c.avisos.push({ nivel: 'error', txt: 'Radio y ángulo tienen que ser mayores que cero.' });
      tramos.push({ ...c, x0: x, x1: x, largo: 0, N: 0 });
      return;
    }
    const Rm = convexa ? R - s / 2 : R + s / 2;       // radio de la línea de desarrollo
    const arco = Rm * th;
    const h = t - s / 2;                              // bisagra → cara ranurada
    const Rint = convexa ? R - t : R + t;             // radio de la cara ranurada
    if (convexa && Rint <= 0) c.avisos.push({ nivel: 'error', txt: `Con R ${R} la cara de atrás quedaría con radio negativo: el radio tiene que ser mayor que el espesor.` });

    let Nmin = 1, Ntol = 1, N;
    if (esV) {
      if (!convexa) c.avisos.push({ nivel: 'error', txt: 'La ranura en V solo sirve si la cara vista queda convexa (la V tiene que cerrarse).' });
      N = Math.max(1, Math.ceil(th / beta - 1e-9));
      Nmin = N;
    } else {
      if (convexa) Nmin = Math.max(1, Math.ceil((th * h) / (w * (+p.cierreMax || 1)) - 1e-9));
      const cMax = Math.sqrt(8 * Rm * (+p.tolFaceta || 0.2));   // tramo recto máximo entre ranuras
      Ntol = Math.max(1, Math.ceil(arco / (cMax + w) - 1e-9));
      N = Math.max(Nmin, Ntol);
      if (p.modoPaso === 'fijo' && +p.pasoFijo > 0) {
        N = Math.max(1, Math.round(arco / +p.pasoFijo));
        if (N < Nmin) c.avisos.push({ nivel: 'error', txt: `Con paso ${p.pasoFijo} entran ${N} ranuras y hacen falta al menos ${Nmin}: las ranuras se cierran antes de llegar al radio y la pieza se raja.` });
      }
    }
    if (seg.n > 0) {   // cantidad forzada a mano en esta curva
      N = Math.round(seg.n);
      if (N < Nmin) c.avisos.push({ nivel: 'error', txt: `Forzaste ${N} ranuras y hacen falta al menos ${Nmin}.` });
    }
    const paso = arco / N;
    const phi = th / N;
    const anchoEf = esV ? bocaV : w;
    const costilla = paso - anchoEf;
    const cierre = esV ? phi / beta : convexa ? (phi * h) / w : 0;   // fracción de cierre de cada ranura
    const apertura = !esV && !convexa ? w + phi * h : 0;             // ancho en la boca, abierta
    const recto = esV ? paso : paso - w;
    const flecha = (recto * recto) / (8 * Rm);
    const eps = (s / (2 * Rm)) * 100;                 // % deformación de la piel (radio medio)
    const rhoPuente = esV ? 0 : w / phi;              // radio local de la piel sobre la ranura

    if (costilla < +p.costillaMin) c.avisos.push({ nivel: 'error', txt: `Las ranuras quedan casi pegadas (costilla de ${costilla.toFixed(1)} mm, mínimo ${p.costillaMin}). Usar una herramienta más fina, o un radio más grande.` });
    if (eps > mat.epsMax) c.avisos.push({ nivel: 'aviso', txt: `La piel se estira ${eps.toFixed(2)} % y el límite orientativo del ${mat.nombre} es ${mat.epsMax} %: riesgo de rajar la cara. Bajar la piel o agrandar el radio (y probar con una probeta).` });
    if (esV && Math.abs(phi - beta) > rad(0.5)) c.avisos.push({ nivel: 'aviso', txt: `Con una V de ${deg(beta).toFixed(1)}° y ${N} pliegues cada uno cierra ${deg(phi).toFixed(1)}°: queda una luz en cuña de ${deg(beta - phi).toFixed(1)}° por pliegue. Ideal: fresa de ${deg(phi).toFixed(1)}°.` });
    if (esV && s > 1.2) c.avisos.push({ nivel: 'info', txt: 'En V el pliegue es casi un canto vivo: con más de ~1 mm de piel la cara tiende a marcarse o rajarse.' });
    if (!esV && convexa && cierre > 0.98) c.avisos.push({ nivel: 'info', txt: 'Las ranuras cierran del todo: la pieza toma el radio sola, pero no admite más curva.' });
    if (flecha > (+p.tolFaceta || 0.2) * 1.05) c.avisos.push({ nivel: 'aviso', txt: `Facetado visible: flecha de ${flecha.toFixed(2)} mm entre ranuras.` });

    const x0 = x;
    for (let k = 0; k < N; k++) {
      ranuras.push({
        x: x0 + (k + 0.5) * paso,
        ancho: esV ? bocaV : w,
        prof: profRanura,
        curva: i, phi: convexa ? phi : -phi,
        tipo: esV ? 'v' : 'paralela',
        abre: !convexa,
      });
    }
    Object.assign(c, { x0, x1: x0 + arco, largo: arco, Rm, Rint, N, Nmin, Ntol, paso, phi, costilla, cierre, apertura, flecha, eps, rhoPuente, recto });
    tramos.push(c);
    x += arco;
  });

  const fin = +p.sobranteFin || 0;
  if (fin > 0) { tramos.push({ tipo: 'sobrante', x0: x, x1: x + fin, largo: fin }); x += fin; }
  const L = x;

  tramos.filter((c) => c.tipo === 'curva').forEach((c) => c.avisos.forEach((a) => avisos.push({ ...a, txt: `Curva ${c.idx + 1}: ${a.txt}` })));
  if (!(p.segmentos || []).some((sg) => sg.tipo === 'curva')) avisos.push({ nivel: 'info', txt: 'El perfil no tiene ninguna curva: no hay nada que ranurar.' });
  if (!(H > 0)) avisos.push({ nivel: 'error', txt: 'Falta el alto de la pieza.' });
  if (mat.nota) avisos.push({ nivel: 'info', txt: mat.nota });

  return { L, H, t, s, w, esV, bocaV, beta, profRanura, tramos, ranuras, avisos, material: mat };
}

// ---------------------------------------------------------------------------
// Cinemática: posición de un punto (x, z) de la pieza plana cuando se curva.
// Las costillas son rígidas; la piel se dobla SOLO sobre cada ranura (puente).
// u = 0 plano, u = 1 curvado del todo.
// Devuelve una función (x, z) -> [X, Y] en planta.
// ---------------------------------------------------------------------------
export function cinematica(res, u = 1, puenteV = 0.6) {
  const s = res.s;
  const zm = s / 2;
  // tramos de curvatura constante a lo largo de la línea de desarrollo
  const piezas = [];
  let xa = 0;
  const bridges = res.ranuras.map((r) => {
    const wb = r.tipo === 'v' ? puenteV : r.ancho;
    return { a: r.x - wb / 2, b: r.x + wb / 2, k: (r.phi * u) / wb };
  }).sort((p, q) => p.a - q.a);
  for (const br of bridges) {
    if (br.a > xa) piezas.push({ a: xa, b: br.a, k: 0 });
    piezas.push({ a: Math.max(br.a, xa), b: br.b, k: br.k });
    xa = br.b;
  }
  if (res.L > xa) piezas.push({ a: xa, b: res.L, k: 0 });
  // estado al inicio de cada pieza
  let P = [0, 0], al = 0;
  for (const pz of piezas) {
    pz.P = P.slice(); pz.al = al;
    const len = pz.b - pz.a;
    const e = avanza(P, al, pz.k, len);
    P = e.P; al = e.al;
  }
  function avanza(P0, a0, k, d) {
    if (Math.abs(k) < 1e-12) return { P: [P0[0] + d * Math.cos(a0), P0[1] + d * Math.sin(a0)], al: a0 };
    const a1 = a0 + k * d;
    return { P: [P0[0] + (Math.sin(a1) - Math.sin(a0)) / k, P0[1] - (Math.cos(a1) - Math.cos(a0)) / k], al: a1 };
  }
  function buscar(x) {
    let lo = 0, hi = piezas.length - 1;
    while (lo < hi) { const m = (lo + hi) >> 1; if (piezas[m].b < x) lo = m + 1; else hi = m; }
    return piezas[lo] || { a: 0, b: 0, k: 0, P: [0, 0], al: 0 };
  }
  // normal hacia la cara ranurada = izquierda del avance (la curva convexa gira a la izquierda)
  const f = (x, z) => {
    const pz = buscar(x);
    const e = avanza(pz.P, pz.al, pz.k, x - pz.a);
    const n = [-Math.sin(e.al), Math.cos(e.al)];
    return [e.P[0] + (z - zm) * n[0], e.P[1] + (z - zm) * n[1]];
  };
  f.heading = (x) => { const pz = buscar(x); return pz.al + pz.k * (x - pz.a); };
  return f;
}

// Contorno de la sección de la pieza plana (x, z), en sentido antihorario,
// subdividido para que se doble prolijo. Devuelve [{x, z, cara}] donde cara
// indica a qué cara pertenece el tramo que ARRANCA en ese punto.
export function seccion(res, paso = 2, puenteV = 0.6) {
  const { L, t, s } = res;
  const pts = [];
  const add = (x, z, cara) => pts.push({ x, z, cara });
  // cara vista: z = 0, de 0 a L (subdividida fino sobre cada ranura)
  const cortes = new Set([0, L]);
  for (const r of res.ranuras) {
    const wb = r.tipo === 'v' ? puenteV : r.ancho;
    for (let k = 0; k <= 8; k++) cortes.add(r.x - wb / 2 + (wb * k) / 8);
  }
  for (let xx = 0; xx < L; xx += paso) cortes.add(xx);
  const xs = [...cortes].filter((v) => v >= 0 && v <= L).sort((a, b) => a - b);
  xs.forEach((xx) => add(xx, 0, 'vista'));
  // canto final
  pts[pts.length - 1].cara = 'canto';
  // cara ranurada: de L a 0 a z = t, con las muescas
  const rs = [...res.ranuras].sort((a, b) => b.x - a.x);
  let xcur = L;
  const back = [];
  const pushLine = (x0, x1) => { // de x0 a x1 (x0 > x1) en z = t
    if (x0 - x1 < 1e-6) return;
    const n = Math.max(1, Math.ceil((x0 - x1) / paso));
    for (let k = 0; k < n; k++) back.push({ x: x0 - ((x0 - x1) * k) / n, z: t, cara: 'atras' });
  };
  for (const r of rs) {
    const half = r.ancho / 2;
    const xa = Math.min(xcur, r.x + half), xb = Math.max(0, r.x - half);
    pushLine(xcur, xa);
    if (r.tipo === 'v') {
      back.push({ x: xa, z: t, cara: 'ranura' });
      back.push({ x: r.x + puenteV / 2, z: s, cara: 'ranura' });
      back.push({ x: r.x - puenteV / 2, z: s, cara: 'ranura' });
    } else {
      back.push({ x: xa, z: t, cara: 'ranura' });
      for (let k = 0; k <= 8; k++) back.push({ x: xa - ((xa - xb) * k) / 8, z: s, cara: 'fondo' });
      back[back.length - 1].cara = 'ranura';
    }
    xcur = xb;
  }
  pushLine(xcur, 0);
  back.push({ x: 0, z: t, cara: 'canto' });
  pts.push(...back);
  return pts;
}
