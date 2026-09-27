// Catálogo de fresas comerciales para ranurar/curvar.
// Medidas tomadas de fichas de fabricantes (ver `fuente`). Se agregan a la
// tabla de herramientas de la perforadora o del router desde la página.
//
//   tipo:  recta | redonda | v | disco
//   ancho: Ø de corte (recta/redonda), Ø exterior del cono (v), espesor (disco)
//   largo: largo de corte útil (hasta dónde puede bajar)
//   corte: descendente | ascendente | compresion (sólo rectas)

const cono = (ang, d = 6) => +((d / 2) / Math.tan((ang * Math.PI) / 360)).toFixed(1);

export const CATALOGO = [
  // --- rectas espiral HM (métricas, Whiteside MD…) ---
  { grupo: 'Recta espiral descendente', nombre: 'Ø6 × 22 · mango 6', tipo: 'recta', ancho: 6, largo: 22, mango: '6 mm', corte: 'descendente', fuente: 'Whiteside MD622' },
  { grupo: 'Recta espiral descendente', nombre: 'Ø8 × 25 · mango 8', tipo: 'recta', ancho: 8, largo: 25, mango: '8 mm', corte: 'descendente', fuente: 'Whiteside MD825' },
  { grupo: 'Recta espiral descendente', nombre: 'Ø8 × 32 · mango 8', tipo: 'recta', ancho: 8, largo: 32, mango: '8 mm', corte: 'descendente', fuente: 'Whiteside MD832' },
  { grupo: 'Recta espiral descendente', nombre: 'Ø10 × 32 · mango 10', tipo: 'recta', ancho: 10, largo: 32, mango: '10 mm', corte: 'descendente', fuente: 'Whiteside MD1032' },
  { grupo: 'Recta espiral descendente', nombre: 'Ø10 × 38 · mango 10', tipo: 'recta', ancho: 10, largo: 38, mango: '10 mm', corte: 'descendente', fuente: 'Whiteside MD1038' },
  { grupo: 'Recta espiral ascendente', nombre: 'Ø6 × 22 · mango 6 · 2 filos', tipo: 'recta', ancho: 6, largo: 22, mango: '6 mm', corte: 'ascendente', fuente: 'genérica 6×22 CEL (mercado)' },

  // --- punta redonda ---
  { grupo: 'Punta esférica (ball nose)', nombre: 'Ø6 R3 × 22 · mango 6', tipo: 'redonda', ancho: 6, largo: 22, mango: '6 mm', fuente: 'Amana 46456' },
  { grupo: 'Media caña (core box)', nombre: 'Ø9 × 7 · mango ½″', tipo: 'redonda', ancho: 9, largo: 7, mango: '½″', fuente: 'core box métrica (FindBuyTool)' },
  { grupo: 'Media caña (core box)', nombre: 'Ø11 × 8,5 · mango ½″', tipo: 'redonda', ancho: 11, largo: 8.5, mango: '½″', fuente: 'core box métrica (FindBuyTool)' },
  { grupo: 'Media caña (core box)', nombre: 'Ø12 × 9 · mango ½″', tipo: 'redonda', ancho: 12, largo: 9, mango: '½″', fuente: 'core box métrica (FindBuyTool)' },
  { grupo: 'Media caña (core box)', nombre: 'Ø15 × 10,5 · mango ½″', tipo: 'redonda', ancho: 15, largo: 10.5, mango: '½″', fuente: 'core box métrica (FindBuyTool)' },

  // --- V de grabado HM, mango 6 (el largo útil lo da el cono) ---
  ...[15, 20, 30, 45, 60].map((a) => ({ grupo: 'V de grabado HM · mango 6', nombre: `${a}° · punta 0,2 · llega a ${cono(a)} mm`, tipo: 'v', ancho: 6, anguloV: a, punta: 0.2, largo: cono(a), mango: '6 mm', fuente: 'V-bits de grabado 6 mm (Eternal Tools / mercado)' })),

  // --- V de insertos, mango ½″ ---
  { grupo: 'V de insertos · mango ½″', nombre: '40° · Ø18,7 × 25,4', tipo: 'v', ancho: 18.7, anguloV: 40, punta: 0, largo: 25.4, mango: '½″', fuente: 'ToolsToday / Amana V-groove' },
  { grupo: 'V de insertos · mango ½″', nombre: '45° · Ø20,6 × 22,2', tipo: 'v', ancho: 20.6, anguloV: 45, punta: 0, largo: 22.2, mango: '½″', fuente: 'ToolsToday / Amana V-groove' },
  { grupo: 'V de insertos · mango ½″', nombre: '60° · Ø27 × 23', tipo: 'v', ancho: 27, anguloV: 60, punta: 0, largo: 23, mango: '½″', fuente: 'ToolsToday / Amana V-groove' },
  { grupo: 'V de insertos · mango ½″', nombre: '90° · Ø38,1 × 19', tipo: 'v', ancho: 38.1, anguloV: 90, punta: 0, largo: 19.05, mango: '½″', fuente: 'ToolsToday / Amana V-groove' },

  // --- V de plegado con fondo plano ---
  { grupo: 'V de plegado con fondo plano · ½″', nombre: '90° · plano 2,3 · Ø38,1 × 17,9', tipo: 'v', ancho: 38.1, anguloV: 90, punta: 2.3, largo: 17.9, mango: '½″', fuente: 'Amana RC-1172' },
  { grupo: 'V de plegado con fondo plano · ½″', nombre: '110° · plano 2 · Ø44 × 14,7', tipo: 'v', ancho: 44, anguloV: 110, punta: 2, largo: 14.7, mango: '½″', fuente: 'Amana RC-1175' },

  // --- disco ---
  { grupo: 'Disco de ranurar', nombre: 'Ø45 × 3 (62211-4T, mango 12,7)', tipo: 'disco', ancho: 3, largo: 10, mango: '12,7', fuente: 'la T183 de la SKH-612HS · profundidad A MEDIR' },
];

export function opcionesCatalogo() {
  const grupos = {};
  CATALOGO.forEach((c, i) => { (grupos[c.grupo] ||= []).push(`<option value="${i}">${c.nombre}</option>`); });
  return '<option value="">+ agregar del catálogo…</option>' +
    Object.entries(grupos).map(([g, o]) => `<optgroup label="${g}">${o.join('')}</optgroup>`).join('');
}
