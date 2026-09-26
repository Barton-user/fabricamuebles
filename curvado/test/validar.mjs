// Genera casos de prueba con el motor + escritores JS y los deja en test/out/
// para compararlos contra etapa2 (Python) con test/validar.py
import fs from 'node:fs';
import { calcular } from '../src/motor.js';
import { xml3, mpr, csvCorte, piezaMaquina, hasBackOps, ncRouter } from '../src/exportar.js';

const casos = [
  { nombre: 'Mostrador R150', cara: 'A', veta: '2', cantos: { up: 1, down: 1, left: 0, right: 0 },
    p: { espesor: 18, piel: 2, alto: 1000, material: 'mdf_mel', tipo: 'paralela', ancho: 6, anguloV: 90,
      cierreMax: 0.9, tolFaceta: 0.2, costillaMin: 3, modoPaso: 'auto',
      segmentos: [{ tipo: 'recto', largo: 600 }, { tipo: 'curva', radio: 150, angulo: 90, lado: 'convexa' }, { tipo: 'recto', largo: 400 }] } },
  { nombre: 'Columna S doble cara B', cara: 'B', veta: '1', cantos: { up: 0.5, down: 1, left: 1, right: 0 },
    p: { espesor: 18, piel: 2.5, alto: 720.5, material: 'agl_mel', tipo: 'paralela', ancho: 10, anguloV: 90,
      cierreMax: 0.85, tolFaceta: 0.3, costillaMin: 3, modoPaso: 'auto',
      segmentos: [{ tipo: 'recto', largo: 123.45 }, { tipo: 'curva', radio: 300, angulo: 60, lado: 'convexa' },
        { tipo: 'curva', radio: 250, angulo: 45, lado: 'concava' }, { tipo: 'recto', largo: 80 }] } },
];
fs.mkdirSync('test/out', { recursive: true });
const piezas = [];
casos.forEach((c, i) => {
  const res = calcular(c.p);
  const pz = piezaMaquina(res, { codigo: `99900000009${i}`, nombre: c.nombre, materialCod: 'MDF', textura: 'Blanco',
    veta: c.veta, cantos: c.cantos, orden: 'TEST-1', cliente: 'Prueba', direccion: 'Taller', mueble: 'Mostrador' }, c.cara, res.profRanura);
  piezas.push(pz);
  fs.writeFileSync(`test/out/${pz.code}.json`, JSON.stringify(pz));
  fs.writeFileSync(`test/out/${pz.code}.xml`, xml3(pz));
  fs.writeFileSync(`test/out/${pz.code}.mpr`, mpr(pz, false));
  if (hasBackOps(pz)) fs.writeFileSync(`test/out/${pz.code}K.mpr`, mpr(pz, true));
  console.log(c.nombre, 'L=', res.L.toFixed(2), 'ranuras', res.ranuras.length, res.avisos.map((a) => a.nivel + ':' + a.txt).join(' | '));
});
fs.writeFileSync('test/out/lista_corte.csv', csvCorte(piezas));
