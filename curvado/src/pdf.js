// Hoja de taller en PDF (A4 vertical) para acompañar el paquete.
// Describe la pieza, los programas, cómo se carga en cada máquina y los pasos:
// sierra HP280 → perforadora SKH-612HS (o router) → cantos → plegado.
// Los pasos salen de CONTEXTO.md (sesiones en las máquinas, 23-25/09/2026).
import { jsPDF } from 'jspdf';
import { deg } from './motor.js';

const A4 = { w: 210, h: 297, m: 14 };
const AZUL = [31, 95, 191], GRIS = [110, 110, 105], ROJO = [192, 57, 43], VERDE = [31, 138, 76], NARANJA = [229, 161, 58];
const fx = (v, d = 1) => (Number.isFinite(v) ? (Math.round(v * 10 ** d) / 10 ** d).toLocaleString('es-AR', { maximumFractionDigits: d }) : '-');
// Helvetica de jsPDF es WinAnsi: sin estos caracteres
const limpio = (s) => String(s ?? '').replace(/[≈]/g, '~').replace(/[→]/g, '->').replace(/[⌒]/g, '(convexa)').replace(/[⌣]/g, '(cóncava)')
  .replace(/[–—]/g, '-').replace(/[“”]/g, '"').replace(/[^\x00-\xff]/g, '');

// --- SVG → PNG (para meter los dibujos de la página) -----------------------
function svgPng(svg, anchoPx = 1400) {
  return new Promise((ok) => {
    const vb = /viewBox="([-\d.\s]+)"/.exec(svg);
    const [, , vw, vh] = vb ? vb[1].trim().split(/\s+/).map(Number) : [0, 0, 400, 200];
    const hPx = Math.round((anchoPx * vh) / vw);
    const css = '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#222}.cota line{stroke:#1f5fbf}.cota text{fill:#1f5fbf;font-weight:bold}</style>';
    const s = svg.replace(/var\(--tinta\)/g, '#222').replace(/var\(--objetivo\)/g, '#1f5fbf').replace(/var\(--acento\)/g, '#1f5fbf')
      .replace('<svg ', `<svg width="${anchoPx}" height="${hPx}" `).replace(/(<svg[^>]*>)/, `$1${css}`);
    const img = new Image();
    img.onload = () => {
      const c = document.createElement('canvas'); c.width = anchoPx; c.height = hPx;
      const g = c.getContext('2d'); g.fillStyle = '#fff'; g.fillRect(0, 0, anchoPx, hPx); g.drawImage(img, 0, 0);
      ok({ url: c.toDataURL('image/png'), ar: hPx / anchoPx });
    };
    img.onerror = () => ok(null);
    img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(s);
  });
}

export async function hojaTaller(o) {
  // o: { st, datos, RES, maq ('router'|'perforadora'), archivos:[names], svgPlanta, svgDetalle (2 svgs), svgPlano, png3d, herrTxt(m) }
  const { st, datos, RES, maq } = o;
  const res = RES[maq];
  const doc = new jsPDF({ unit: 'mm', format: 'a4' });
  const W = A4.w - 2 * A4.m;
  let y = A4.m, pagina = 1;

  const pie = () => {
    doc.setFontSize(7.5); doc.setTextColor(...GRIS);
    doc.text(limpio(`${datos.nombre} · código ${datos.codigo} · ${new Date().toLocaleDateString('es-AR')}`), A4.m, A4.h - 7);
    doc.text(`hoja ${pagina}`, A4.w - A4.m, A4.h - 7, { align: 'right' });
    doc.setTextColor(0);
  };
  const nueva = () => { pie(); doc.addPage(); pagina++; y = A4.m; };
  const lugar = (h) => { if (y + h > A4.h - 14) nueva(); };
  const titulo = (t, sub, reserva = 14) => {
    lugar(reserva);
    doc.setFillColor(...AZUL); doc.rect(A4.m, y, W, 7.5, 'F');
    doc.setTextColor(255); doc.setFont('helvetica', 'bold'); doc.setFontSize(11.5);
    doc.text(limpio(t), A4.m + 2.5, y + 5.2);
    if (sub) { doc.setFont('helvetica', 'normal'); doc.setFontSize(8.5); doc.text(limpio(sub), A4.w - A4.m - 2.5, y + 5.2, { align: 'right' }); }
    doc.setTextColor(0); y += 10.5;
  };
  const sub = (t, reserva = 8) => { lugar(reserva); doc.setFont('helvetica', 'bold'); doc.setFontSize(10); doc.setTextColor(...AZUL); doc.text(limpio(t), A4.m, y + 3.5); doc.setTextColor(0); y += 6; };
  const parrafo = (t, { size = 9, color = 0, bold = false, ind = 0 } = {}) => {
    doc.setFont('helvetica', bold ? 'bold' : 'normal'); doc.setFontSize(size); doc.setTextColor(...(Array.isArray(color) ? color : [color, color, color]));
    const ls = doc.splitTextToSize(limpio(t), W - ind);
    lugar(ls.length * size * 0.42 + 1);
    doc.text(ls, A4.m + ind, y + size * 0.35); y += ls.length * size * 0.42 + 1.2; doc.setTextColor(0);
  };
  const pasos = (lista) => {
    lista.forEach((p, i) => {
      doc.setFont('helvetica', 'normal'); doc.setFontSize(9);
      const ls = doc.splitTextToSize(limpio(p), W - 9);
      lugar(ls.length * 3.8 + 1.5);
      doc.setFillColor(...AZUL); doc.circle(A4.m + 2.6, y + 1.8, 2.3, 'F');
      doc.setTextColor(255); doc.setFont('helvetica', 'bold'); doc.setFontSize(7.5);
      doc.text(String(i + 1), A4.m + 2.6, y + 2.9, { align: 'center' });
      doc.setTextColor(0); doc.setFont('helvetica', 'normal'); doc.setFontSize(9);
      doc.text(ls, A4.m + 8, y + 3); y += ls.length * 3.8 + 1.8;
    });
    y += 1;
  };
  const aviso = (t) => {
    doc.setFontSize(8.8); const ls = doc.splitTextToSize(limpio(t), W - 8); lugar(ls.length * 3.7 + 4);
    doc.setFillColor(255, 244, 222); doc.setDrawColor(...NARANJA); doc.rect(A4.m, y, W, ls.length * 3.7 + 3, 'FD');
    doc.setFont('helvetica', 'bold'); doc.setTextColor(120, 70, 0); doc.text('!', A4.m + 2.5, y + 4);
    doc.setFont('helvetica', 'normal'); doc.text(ls, A4.m + 6, y + 4); doc.setTextColor(0); y += ls.length * 3.7 + 5;
  };
  const tabla = (filas, anchos, { head = true, size = 8.5 } = {}) => {
    const x0 = A4.m; let x;
    filas.forEach((f, i) => {
      const alto = 5.2; lugar(alto);
      if (head && i === 0) { doc.setFillColor(238, 236, 230); doc.rect(x0, y, W, alto, 'F'); doc.setFont('helvetica', 'bold'); }
      else doc.setFont('helvetica', 'normal');
      doc.setFontSize(size); x = x0;
      f.forEach((c, j) => { doc.text(limpio(c), x + 1.5, y + 3.7, { maxWidth: anchos[j] * W - 2 }); x += anchos[j] * W; });
      doc.setDrawColor(225); doc.line(x0, y + alto, x0 + W, y + alto); y += alto;
    });
    y += 2;
  };
  const imagen = async (svg, altoMax, anchoFrac = 1) => {
    const im = await svgPng(svg); if (!im) return;
    let w = W * anchoFrac, h = w * im.ar; if (h > altoMax) { h = altoMax; w = h / im.ar; }
    lugar(h + 2); doc.addImage(im.url, 'PNG', A4.m + (W - w) / 2, y, w, h); y += h + 3;
  };

  const curvas = res.tramos.filter((t) => t.tipo === 'curva');
  const cortL = res.L - (st.cIzq || 0) - (st.cDer || 0), cortH = res.H - (st.cArr || 0) - (st.cAbj || 0);
  const perfil = st.segmentos.map((s) => (s.tipo === 'recto' ? `recto ${s.largo}` : `R${s.radio} ${s.angulo}° ${s.lado === 'concava' ? 'cóncava' : 'convexa'}`)).join('  +  ');
  const hT = (m) => { const h = RES[m].herr; return h ? `${String(h.t).startsWith('T') ? h.t : 'T' + h.t} ${o.herrTxt(h)}` : '-'; };

  // ===================================================================== HOJA 1
  doc.setFont('helvetica', 'bold'); doc.setFontSize(17); doc.text(limpio('Hoja de taller · pieza curvada por ranuras'), A4.m, y + 6);
  doc.setFont('helvetica', 'normal'); doc.setFontSize(9.5); doc.setTextColor(...GRIS);
  doc.text(limpio(`${datos.nombre}   ·   orden ${datos.orden || '-'}   ·   cliente ${datos.cliente || '-'}   ·   mueble ${datos.mueble || '-'}`), A4.m, y + 12);
  doc.setTextColor(0); y += 17;
  // código grande
  doc.setDrawColor(0); doc.setLineWidth(0.4); doc.rect(A4.w - A4.m - 62, A4.m, 62, 13);
  doc.setFontSize(7); doc.text(limpio('CÓDIGO / NOMBRE DE ARCHIVO'), A4.w - A4.m - 60, A4.m + 3.5);
  doc.setFont('courier', 'bold'); doc.setFontSize(13); doc.text(datos.codigo, A4.w - A4.m - 31, A4.m + 10, { align: 'center' });
  doc.setFont('helvetica', 'normal'); doc.setLineWidth(0.2);

  titulo('1. La pieza', `${res.material.nombre} ${fx(st.espesor)} mm`);
  tabla([
    ['Dato', 'Valor', 'Dato', 'Valor'],
    ['Desarrollo (terminado)', `${fx(res.L, 2)} mm`, 'Alto (terminado)', `${fx(res.H, 2)} mm`],
    ['Medida de CORTE sierra', `${fx(cortL, 1)} × ${fx(cortH, 1)} mm`, 'Cantidad', String(datos.cantidad || 1)],
    ['Espesor nominal / real', `${fx(st.espesor)} / ${fx(st.espesorReal, 2)} mm`, 'Piel (queda sin ranurar)', `${fx(st.piel, 2)} mm`],
    ['Cantos arr / abj / ini / fin', `${st.cArr} / ${st.cAbj} / ${st.cIzq} / ${st.cDer} mm`, 'Veta', st.veta === '1' ? 'a lo largo del desarrollo' : 'a lo alto'],
    ['Ranuras', `${res.ranuras.length} · prof ${fx(res.profRanura, 2)} mm`, 'Tipo', res.esV ? `V ${fx(deg(res.beta))}°${res.punta ? ` plano ${res.punta}` : ''}` : `${res.forma === 'redonda' ? 'punta redonda' : 'rectas'} de ${fx(res.w, 1)} mm`],
  ], [0.25, 0.25, 0.25, 0.25]);
  parrafo(`Perfil (medido sobre la cara vista): ${perfil}`, { size: 8.8 });
  y += 1;
  sub('Curvas');
  tabla([['Curva', 'Largo', 'Ran. (mín)', 'Paso', 'Costilla', 'Cierre', 'Radio molde*'],
    ...curvas.map((c, i) => [`${i + 1}: R${fx(c.R)} ${fx(c.angulo)}° ${c.convexa ? 'convexa' : 'cóncava'}`, `${fx(c.largo, 1)}`, `${c.N} (${c.Nmin})`, `${fx(c.paso, 2)}`, `${fx(c.costilla, 1)}`,
      c.convexa ? `${fx(c.cierre * 100, 0)} %` : 'se abre', c.convexa ? `R ${fx(c.R - res.t, 1)} (lado ranurado)` : `R ${fx(c.R, 1)} (lado vista)`])],
  [0.26, 0.14, 0.12, 0.1, 0.1, 0.1, 0.18]);
  parrafo('* Radio del molde o de la tapa contra la que se apoya la pieza al plegar.', { size: 7.5, color: GRIS });

  titulo('2. Programas', 'nombre de archivo = código de barras');
  const desc = (n) => n.startsWith('SIERRA/') ? 'Sierra HP280 · importar en AutoCUT'
    : n.includes('/XML3/') ? 'SKH-612HS · formato "KDTXml"' : n.includes('/MPR/') ? `SKH-612HS · formato "Haomai MPR"${n.endsWith('K.mpr') ? ' (cara de abajo)' : ''}`
      : n.endsWith('.nc') ? 'Router SKG-912MZ · G-code Syntec' : n.endsWith('.svg') ? 'plano de la pieza' : n.endsWith('.png') ? 'imagen 3D' : n.endsWith('.pdf') ? 'esta hoja' : '';
  tabla([['Archivo', 'Para qué'], ...o.archivos.map((n) => [n, desc(n)])], [0.55, 0.45], { size: 8 });
  ['perforadora', 'router'].forEach((m) => {
    const r = RES[m];
    if (!r.ok) parrafo(`${m === 'router' ? 'Router' : 'Perforadora'}: no se generó programa. ${r.avisos.filter((a) => a.nivel === 'error').map((a) => a.txt).join(' ')}`, { size: 8.3, color: ROJO });
  });
  parrafo(`Máquina elegida para ranurar: ${maq === 'router' ? 'ROUTER SKG-912MZ' : 'PERFORADORA SKH-612HS'} con ${hT(maq)}. Los ejes de las ranuras (desde INICIO) son iguales en los dos programas sólo si las dos herramientas tienen el mismo ancho.`, { size: 8.5 });

  titulo('3. Plano de corte y ranurado', 'visto desde la cara RANURADA', 80);
  await imagen(o.svgPlano, Math.max(60, A4.h - 14 - y - 22));
  sub('Ejes de ranura medidos desde INICIO (mm)');
  const ejes = res.ranuras.map((r) => fx(r.x, 1));
  const porFila = 10;
  const filas = []; for (let i = 0; i < ejes.length; i += porFila) filas.push(ejes.slice(i, i + porFila).map((e, j) => `${i + j + 1}: ${e}`));
  tabla(filas.map((f) => [...f, ...Array(porFila - f.length).fill('')]), Array(porFila).fill(1 / porFila), { head: false, size: 7.8 });

  // ===================================================================== HOJA 2
  nueva();
  titulo('4. Cómo queda curvada', 'las ranuras van por la cara de atrás');
  await imagen(o.svgPlanta, 50, 0.6);
  parrafo('Planta de la pieza curvada (vista desde arriba). Punteado azul: el perfil que se busca. Punto verde: INICIO.', { size: 8, color: GRIS });
  const [d1, d2] = o.svgDetalle.split('</svg>').filter((x) => x.trim()).map((x) => x + '</svg>');
  sub('Una ranura antes y después de curvar');
  if (d1) await imagen(d1, 25, 0.7);
  if (d2) await imagen(d2, 25, 0.7);
  parrafo(res.esV
    ? 'Cada ranura en V se cierra hasta que sus caras se tocan: la curva queda formada por facetas planas. El pliegue ocurre en la piel, en el fondo de la V.'
    : curvas.some((c) => c.convexa)
      ? 'En las curvas CONVEXAS (cara vista afuera) las ranuras se cierran en cuña: la cara de atrás se acorta y la piel, del lado visto, casi no cambia de largo. Las costillas quedan rectas; la piel se dobla sobre cada ranura.'
      : 'En las curvas CÓNCAVAS (cara vista adentro) las ranuras se abren: quedan luces en cuña en la cara de atrás, que hay que rellenar o tapar.', { size: 8.8 });

  titulo('5. Cómo se apoya en cada máquina');
  const dibujoCarga = (tipo) => {
    const h = 48; lugar(h + 6);
    const x0 = A4.m, y0 = y, w = W;
    doc.setDrawColor(150); doc.setFillColor(245, 244, 240); doc.rect(x0, y0, w, h, 'FD');
    const escala = Math.min((w * 0.5) / res.L, (h * 0.5) / res.H);
    const pw = res.L * escala, ph = res.H * escala;
    const px = x0 + (tipo === 'router' ? 12 : (w - pw) / 2), py = y0 + 9;
    // placa
    doc.setFillColor(214, 184, 140); doc.setDrawColor(90); doc.rect(px, py, pw, ph, 'FD');
    doc.setDrawColor(...ROJO); doc.setLineWidth(0.35);
    res.ranuras.forEach((r) => { const xx = px + r.x * escala; doc.line(xx, py, xx, py + ph); });
    doc.setLineWidth(0.2);
    doc.setFillColor(...VERDE); doc.circle(px + 1.6, py + 1.6, 1.2, 'F');
    doc.setFontSize(7); doc.setTextColor(...VERDE); doc.text('INICIO', px + 3.4, py + 2.5); doc.setTextColor(0);
    doc.setFontSize(7.5);
    if (tipo === 'sierra') {
      doc.text(limpio(`corte ${fx(cortL, 1)}`), px + pw / 2, py - 1.5, { align: 'center' });
      doc.text(limpio(`${fx(cortH, 1)}`), px - 1.5, py + ph / 2, { align: 'right' });
      doc.setFontSize(7.5); doc.setTextColor(...GRIS);
      doc.text(limpio('La sierra corta el rectángulo liso: las ranuras (rojo) se hacen después.'), x0 + 2, y0 + h - 2);
    }
    if (tipo === 'perforadora') {
      // pinzas del lado opuesto al operador (arriba en el dibujo)
      doc.setFillColor(60); doc.rect(px + pw * 0.2, py - 4, 8, 3, 'F'); doc.rect(px + pw * 0.7, py - 4, 8, 3, 'F');
      doc.setFontSize(7); doc.text('pinzas (lado de referencia)', px + pw / 2, py - 5, { align: 'center' });
      doc.text('lado del operador', px + pw / 2, py + ph + 3.5, { align: 'center' });
      doc.setTextColor(...GRIS); doc.setFontSize(7.3);
      doc.text(limpio(st.caraPerf === 'A' ? 'Arriba: cara RANURADA (atrás). Cara vista CONTRA LA MESA.' : 'Arriba: cara VISTA. Ranuras por abajo (husillo inferior).'), x0 + 2, y0 + h - 5.5);
      doc.text(limpio('Canto largo contra las pinzas. Orientar según la flecha que muestra MH2026 al abrir la pieza.'), x0 + 2, y0 + h - 2);
    }
    if (tipo === 'router') {
      doc.setDrawColor(40); doc.setLineWidth(0.6); doc.line(px - 1, py - 1, px - 1, py + ph + 1); doc.line(px - 1, py + ph + 1, px + pw + 1, py + ph + 1); doc.setLineWidth(0.2);
      doc.setFontSize(7); doc.text(limpio(`escuadra · origen X${st.router.x0} Y${st.router.y0}`), px, py + ph + 4.5);
      doc.setTextColor(...GRIS); doc.setFontSize(7.3);
      const tx = Math.max(px + pw + 8, x0 + w * 0.5);
      doc.text(doc.splitTextToSize(limpio('Cara vista CONTRA LA MESA (sacrificio). Z0 = mesa: el fondo de ranura queda en Z = piel.'), x0 + w - tx - 3), tx, y0 + 10);
      doc.text(doc.splitTextToSize(limpio(`Desarrollo a lo largo de ${st.router.sentido}. Vacío encendido. Dibujo esquemático.`), x0 + w - tx - 3), tx, y0 + 20);
    }
    doc.setTextColor(0); y += h + 4;
  };
  sub('Sierra HP280', 60); dibujoCarga('sierra');
  sub(maq === 'router' ? 'Router SKG-912MZ' : 'Perforadora SKH-612HS', 60); dibujoCarga(maq);

  // ===================================================================== HOJA 3
  nueva();
  titulo('6. Paso 1 · Cortar en la sierra HP280', 'AutoCUT + HuaHuaSAW V7');
  pasos([
    'En la PC de la sierra, AutoCUT: Importar -> "Importar varios materiales" -> SIERRA/lista_corte.xlsx (o .csv) -> "Coincidencia" con el perfil de mapeo ya cargado.',
    `Verificar que las columnas de largo y ancho de CORTE vayan a "Longitud/Ancho de apertura" y que AutoCUT NO reste cantos otra vez: tiene que quedar ${fx(cortL, 1)} × ${fx(cortH, 1)}.`,
    'Optimizar -> Guardar como .CUT. Imprimir la etiqueta en la AIBAO.',
    'Control de la sierra: Alarma Off -> VolOrig (origen) -> automático -> Carg Arch -> elegir sólo este material.',
    'Niv Rep (posición inicial). "Sierra ON" hasta que quede "Sierra Arr" en rojo. Verificar el sentido de giro de la hoja contra la flecha.',
    'Cargar la placa con el lado de 1210 contra las pinzas. Botón verde. Corta por niveles: girar la tira 90° y recargar según el dibujo de la pantalla.',
    `Medir la pieza con cinta: ${fx(cortL, 1)} × ${fx(cortH, 1)} mm (±0,5).`,
    'Pegar la etiqueta en la cara de ATRÁS (la que se ranura) y marcar con lápiz el extremo INICIO.',
  ]);
  parrafo('Sin AutoCUT: menú editar -> placa (Length/Width/Thick/quantity) -> "cutting length" + "quantity" -> Add -> confirm -> automático. Saw = kerf 4,4; Trim = refilado 5 por borde.', { size: 8, color: GRIS });

  if (maq === 'perforadora') {
    titulo('7. Paso 2 · Ranurar en la perforadora SKH-612HS', `${hT('perforadora')} · cara ${st.caraPerf}`);
    pasos([
      'Encender: equipo y vacío -> COMPUTER START -> esperar la PC -> POWER (~1 min) -> CncMon32 en "ready" (sin alarma titilando) -> MH2026.',
      'Revisar que la herramienta esté en la revista (T18n = puesto n) y que "Modo de cambio de herramienta" esté APAGADO.',
      `"Tipos completados" -> carpeta -> "Cargar archivo" -> cambiar Formato a "KDTXml" (arranca en "Nueva generaciónXml" y no lista nada) -> PERFORADORA/XML3/${datos.codigo}.xml. Alternativa: "Haomai MPR" con la carpeta MPR.`,
      `Doble clic en la fila para abrirla. En la tabla tienen que aparecer ${res.ranuras.length} ranuras de ancho ${fx(RES.perforadora.w, 1)} y profundidad ${fx(st.espesorReal - st.piel, 2)}, sin filas en rojo ("Motivo no procesado"). Generar.`,
      `Escanear o tipear el código ${datos.codigo}.`,
      `Verde 1ª vez: las pinzas vienen al frente. Colocar la placa ${st.caraPerf === 'A' ? 'con la CARA VISTA CONTRA LA MESA' : 'con la cara vista ARRIBA'}, canto largo contra las pinzas, orientada según la flecha de la pantalla. Verde 2ª vez: mecaniza.`,
      `Primera pieza: medir con calibre la piel en el extremo de una ranura (${fx(st.piel, 2)} ±0,3 mm) y el eje de la primera ranura desde INICIO (${fx(res.ranuras[0]?.x, 1)} mm).`,
    ]);
    aviso('La perforadora mide la profundidad desde la cara de arriba: si la placa viene más gruesa o más fina que el espesor real cargado, la piel cambia. Medir el espesor real de cada lote.');
  } else {
    titulo('7. Paso 2 · Ranurar en el router SKG-912MZ', hT('router'));
    pasos([
      `Montar la herramienta ${hT('router')} y verificar Z0 en la mesa de sacrificio.`,
      `Apoyar la placa con la CARA VISTA CONTRA LA MESA, contra la escuadra en X${st.router.x0} Y${st.router.y0}, con el desarrollo a lo largo de ${st.router.sentido}. INICIO del lado del origen.`,
      'Vacío encendido. Verificar que la placa no se mueva.',
      `Cargar ROUTER/${datos.codigo}_ranuras_T${RES.router.herr?.t}.nc y correrlo. Entra y sale fuera de la placa; ${Math.ceil((st.espesor - st.piel) / Math.max(0.5, st.router.pasada))} pasada(s) por ranura.`,
      `Medir la piel con calibre en el extremo de una ranura: ${fx(st.piel, 2)} ±0,2 mm.`,
    ]);
    aviso('El .nc no trae encabezado ni cambio de herramienta (igual que los de GuiGui), salvo que se haya elegido el preset Syntec. Cargar la herramienta a mano antes de correrlo.');
  }

  nueva();
  titulo('8. Paso 3 · Cantos', 'pegadora HH-509R');
  pasos([
    `Cantos a pegar: arriba ${st.cArr} · abajo ${st.cAbj} · inicio ${st.cIzq} · fin ${st.cDer} mm (0 = sin canto).`,
    'Los extremos INICIO y FIN son rectos: van por la pegadora como cualquier pieza.',
    'Los cantos de arriba y abajo recorren la zona ranurada: en esa zona el canto sólo apoya en la piel y en las costillas. Pasar despacio y con presión pareja; no refilar fuerte sobre las ranuras.',
    'Canto recomendado para la zona curva: PVC o ABS flexible de hasta 1 mm. Uno de 2 mm o de melamina rígida se levanta al plegar.',
  ]);
  aviso('A validar con una probeta: al plegar, en las curvas convexas el lado ranurado se acorta y el canto puede arrugarse o despegarse. Si pasa, pegar los cantos de arriba y abajo DESPUÉS de plegar (a mano, con canto preencolado o cola de contacto), o dejarlos cubiertos por la tapa y el piso del mueble.');

  titulo('9. Paso 4 · Plegar');
  pasos([
    `Tener el molde: la tapa o el piso del mueble con el contorno ya cortado (router). Radios: ${curvas.map((c, i) => `curva ${i + 1} ${c.convexa ? `R ${fx(c.R - res.t, 1)} del lado ranurado` : `R ${fx(c.R, 1)} del lado vista`}`).join(' · ')}.`,
    'Aspirar la viruta de las ranuras. Presentar en seco: la pieza tiene que acompañar el molde sin forzar.',
    curvas.some((c) => c.convexa) ? 'Curvas convexas: cola vinílica dentro de las ranuras (poca, con pincel). Al cerrarse, la curva queda rígida.' : 'Curvas cóncavas: las ranuras se abren; prever relleno (masilla o listones) por detrás.',
    'Doblar de a poco desde un extremo, apoyando contra el molde. No golpear ni forzar en un solo punto: la piel se raja.',
    'Fijar a la tapa y al piso con tornillos en las costillas, cada 80-100 mm, o sujetar con cinchas hasta que seque.',
    'Controlar el radio con una plantilla de cartón o MDF. Limpiar la cola que sale. Dejar secar 24 h antes de mover.',
  ]);

  titulo('10. Control final');
  tabla([
    ['Qué medir', 'Tiene que dar', 'OK'],
    ['Medida de corte', `${fx(cortL, 1)} × ${fx(cortH, 1)} mm`, '[   ]'],
    ['Cantidad de ranuras', `${res.ranuras.length}`, '[   ]'],
    ['Piel en el extremo de una ranura', `${fx(st.piel, 2)} mm`, '[   ]'],
    ['Eje de la primera ranura desde INICIO', `${fx(res.ranuras[0]?.x, 1)} mm`, '[   ]'],
    ['Radio con plantilla', curvas.map((c) => `R ${fx(c.R)}`).join(' / '), '[   ]'],
    ['Cara vista sin rajaduras ni marcas', '-', '[   ]'],
  ], [0.5, 0.38, 0.12]);
  const errores = res.avisos.filter((a) => a.nivel !== 'info');
  if (errores.length) { sub('Avisos del cálculo'); errores.forEach((a) => parrafo('· ' + a.txt, { size: 8.3, color: a.nivel === 'error' ? ROJO : [120, 70, 0] })); }
  pie();
  return doc.output('arraybuffer');
}
