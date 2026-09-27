// Tablas de herramientas y datos de máquina por defecto.
// Salen de CONTEXTO.md (sesiones del 23 y 24/09/2026 en la SKH-612HS) y del
// manual SKH-612 Series. Todo es editable en la página y queda guardado en
// el navegador.

export const PERFORADORA = {
  modelo: 'HUAHUA SKH-612HS',
  // Manual SKH-612H, tabla 4.1
  largoMin: 250, largoMax: 5000, anchoMin: 50, anchoMax: 1200, espMin: 10, espMax: 48,
};

export const HERR_PERFORADORA = [
  { id: 'p187', t: 'T187', tipo: 'recta', ancho: 6, corte: '', profMax: 20, cara: 'A',
    nota: 'Fresa Ø6, husillo superior (revista, puesto 7). Hizo la ranura de 6 del techo de PRUEBA 1.' },
  { id: 'p183', t: 'T183', tipo: 'disco', ancho: 3, discoD: 43.9, profMax: 10, cara: 'A',
    nota: 'Disco de ranurar 62211-4T Ø45 × 3 mm. Corta de costado y no se hunde. PROFUNDIDAD MÁXIMA A MEDIR: con Ø43,9 puede no llegar a 16 mm.' },
  { id: 'p184', t: 'T184', tipo: 'recta', ancho: 20, corte: 'ascendente', profMax: 25, cara: 'A',
    nota: 'Fresa espiral Ø20x70R (la de las cazoletas). Es de corte ascendente: levanta la melamina de la cara de arriba.' },
  { id: 'p11', t: 'T11', tipo: 'recta', ancho: 10, profMax: 20, cara: 'B',
    nota: 'Husillo INFERIOR: la única para la cara dorso. Ancho mínimo aceptado en cara dorso: 10.' },
];

export const ROUTER = {
  modelo: 'SKG-912MZ (Syntec)',
  mesaX: 1250, mesaY: 2500,   // A CONFIRMAR: útil de la mesa
};

export const HERR_ROUTER = [
  { id: 'r1', t: '1', tipo: 'recta', ancho: 6, corte: 'descendente', largoCorte: 22, rpm: 18000,
    nota: 'A CONFIRMAR. Es la T1 Ø6 que CONTEXTO dice que falta cargar en el almacén.' },
  { id: 'r2', t: '2', tipo: 'v', ancho: 38.1, anguloV: 90, punta: 2.3, largoCorte: 17.9, rpm: 18000,
    nota: 'A CONFIRMAR si existe. V de plegado 90° con fondo plano 2,3 (tipo Amana RC-1172).' },
  { id: 'r3', t: '3', tipo: 'redonda', ancho: 6, largoCorte: 22, rpm: 18000,
    nota: 'A CONFIRMAR. Punta esférica Ø6 R3 × 22 (tipo Amana 46456).' },
];

export const ROUTER_CFG = {
  x0: 15, y0: 15,            // la pieza apoyada contra la escuadra, como en los .nc de GuiGui
  sentido: 'Y',              // el desarrollo a lo largo de Y (el lado largo de la mesa)
  zSeg: 38, fRapido: 12000, fBajada: 6000, fEntrada: 3000, fCorte: 4000, fContorno: 8000,
  pasada: 9, salida: 2,
  preset: 'guigui',
  encabezado: '', pie: '',
  contorno: false, herrContorno: 'r1',
};

export const PRESETS_NC = {
  guigui: { nombre: 'Igual que GuiGui (sin encabezado)', encabezado: '', pie: '' },
  syntec: {
    nombre: 'Syntec con cambio de herramienta',
    encabezado: '%\n(CURVADO {nombre})\nG90 G17 G40 G49 G80\nG54\nT{T} M06\nM03 S{S}\nG00 Z{zseg}',
    pie: 'G00 Z{zseg}\nM05\nG00 X0 Y0\nM30\n%',
  },
};
