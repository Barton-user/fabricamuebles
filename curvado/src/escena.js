// Vista 3D de la pieza ranurada, con el curvado animado.
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { cinematica, seccion } from './motor.js';

export class Escena {
  constructor(el) {
    this.el = el;
    this.renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true, logarithmicDepthBuffer: true });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    el.appendChild(this.renderer.domElement);
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(35, 1, 0.5, 50000);
    this.renderer.sortObjects = true;
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.scene.add(new THREE.HemisphereLight(0xffffff, 0x8a8070, 1.6));
    const d = new THREE.DirectionalLight(0xffffff, 1.7); d.position.set(1500, 2500, 2000); this.scene.add(d);
    const d2 = new THREE.DirectionalLight(0xffffff, 0.6); d2.position.set(-2000, 800, -1500); this.scene.add(d2);
    this.grupo = new THREE.Group(); this.scene.add(this.grupo);
    this.mat = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.75, metalness: 0, side: THREE.DoubleSide, flatShading: true });
    // la cara vista va levemente adelante en profundidad: evita que las ranuras (a 2 mm) se "transparenten" de lejos
    this.matV = this.mat.clone(); this.matV.polygonOffset = true; this.matV.polygonOffsetFactor = -2; this.matV.polygonOffsetUnits = -2;
    new ResizeObserver(() => this.resize()).observe(el);
    this.resize();
    this.sucio = true;
    this.controls.addEventListener('change', () => { this.sucio = true; });
    const loop = () => { this.controls.update(); if (this.sucio) { this.renderer.render(this.scene, this.camera); this.sucio = false; } requestAnimationFrame(loop); };
    loop();
  }

  setFondo(css) { this.scene.background = new THREE.Color(css); this.sucio = true; }

  resize() {
    const w = this.el.clientWidth || 600, h = this.el.clientHeight || 400;
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h; this.camera.updateProjectionMatrix(); this.sucio = true;
  }

  // Arma la geometría para un resultado nuevo. La triangulación de la sección
  // se hace una vez, en plano; al curvar sólo se mueven los vértices.
  cargar(res, colores, encuadrar) {
    this.res = res; this.col = colores;
    if (!res || !res.L || !res.H) { this.grupo.clear(); return; }
    this.pts = seccion(res, Math.max(1, res.L / 600));
    const contorno = this.pts.map((p) => new THREE.Vector2(p.x, p.z));
    this.tris = THREE.ShapeUtils.triangulateShape(contorno, []);
    this.curvar(this.u ?? 1, encuadrar);
  }

  curvar(u, encuadrar = false) {
    this.u = u;
    const res = this.res; if (!res || !this.pts) return;
    const f = cinematica(res, u);
    const P = this.pts.map((p) => f(p.x, p.z));
    const H = res.H;
    const pos = [], col = [], posV = [], colV = [];
    const c = (hex) => new THREE.Color(hex);
    const cVista = c(this.col.vista), cNucleo = c(this.col.nucleo), cRan = c(this.col.ranura), cCanto = c(this.col.nucleo).multiplyScalar(0.82);
    const v = (q, y) => [q[0], y, -q[1]];
    const tri = (a, b, cc, color, vis) => { const P2 = vis ? posV : pos, C2 = vis ? colV : col; P2.push(...a, ...b, ...cc); for (let k = 0; k < 3; k++) C2.push(color.r, color.g, color.b); };
    // tapas (canto de arriba y de abajo de la pieza)
    for (const [i, j, k] of this.tris) {
      tri(v(P[i], 0), v(P[k], 0), v(P[j], 0), cCanto);
      tri(v(P[i], H), v(P[j], H), v(P[k], H), cCanto);
    }
    // paredes
    const n = P.length;
    for (let i = 0; i < n; i++) {
      const a = P[i], b = P[(i + 1) % n];
      const cara = this.pts[i].cara;
      const color = cara === 'vista' ? cVista : (cara === 'ranura' || cara === 'fondo') ? cRan : cNucleo;
      tri(v(a, 0), v(b, 0), v(b, H), color, cara === 'vista');
      tri(v(a, 0), v(b, H), v(a, H), color, cara === 'vista');
    }
    this.grupo.children.forEach((o) => o.geometry && o.geometry.dispose());
    this.grupo.clear();
    for (const [pp, cc, m] of [[pos, col, this.mat], [posV, colV, this.matV]]) {
      const g = new THREE.BufferGeometry();
      g.setAttribute('position', new THREE.Float32BufferAttribute(pp, 3));
      g.setAttribute('color', new THREE.Float32BufferAttribute(cc, 3));
      g.computeVertexNormals();
      this.grupo.add(new THREE.Mesh(g, m));
    }

    // perfil objetivo de la cara vista, a media altura y abajo (punteado)
    if (this.col.objetivo) {
      const ideal = perfilIdeal(res, this.segmentos || []);
      for (const y of [-1, H + 1]) {
        const geo = new THREE.BufferGeometry().setFromPoints(ideal.map((q) => new THREE.Vector3(q[0], y, -q[1])));
        const line = new THREE.Line(geo, new THREE.LineDashedMaterial({ color: this.col.objetivo, dashSize: 12, gapSize: 8 }));
        line.computeLineDistances();
        this.grupo.add(line);
      }
    }
    // marca de INICIO
    const m0 = f(0, 0);
    const pin = new THREE.Mesh(new THREE.SphereGeometry(Math.max(6, res.t * 0.45), 16, 12), new THREE.MeshStandardMaterial({ color: 0x1f8a4c }));
    pin.position.set(m0[0], H + 8, -m0[1]);
    this.grupo.add(pin);

    if (encuadrar) this.encuadrar();
    this.sucio = true;
  }

  encuadrar(lado) {
    if (lado !== undefined) this.lado = lado;
    const box = new THREE.Box3().setFromObject(this.grupo);
    const ctr = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3()).length();
    this.controls.target.copy(ctr);
    const dir = this.lado ? new THREE.Vector3(-0.35, 0.45, -1).normalize() : new THREE.Vector3(0.55, 0.5, 1).normalize();
    this.camera.position.copy(ctr).addScaledVector(dir, size * 1.25);
    this.camera.near = size / 5000; this.camera.far = size * 20; this.camera.updateProjectionMatrix();
    this.controls.update(); this.sucio = true;
  }

  png() { this.renderer.render(this.scene, this.camera); return this.renderer.domElement.toDataURL('image/png'); }
}

// Perfil teórico de la cara vista (rectas y arcos exactos), en planta, con el
// mismo arranque que la cinemática: el punto de la cara vista en x = 0.
export function perfilIdeal(res, segmentos) {
  const s = res.s;
  let P = [0, -s / 2], a = 0;   // cara vista: a la derecha de la línea de desarrollo
  const out = [P.slice()];
  const recta = (L) => { const n = Math.max(1, Math.ceil(L / 20)); for (let k = 1; k <= n; k++) out.push([P[0] + (L * k / n) * Math.cos(a), P[1] + (L * k / n) * Math.sin(a)]); P = out[out.length - 1].slice(); };
  const tramos = res.tramos;
  for (const tr of tramos) {
    if (tr.tipo === 'sobrante' || tr.tipo === 'recto') { recta(tr.largo); continue; }
    if (!(tr.N > 0)) continue;
    const R = tr.R, th = (tr.angulo * Math.PI) / 180, sg = tr.convexa ? 1 : -1;
    const cx = P[0] - sg * R * Math.sin(a), cy = P[1] + sg * R * Math.cos(a);
    const n = Math.max(8, Math.ceil((R * th) / 10));
    const a0 = a;
    for (let k = 1; k <= n; k++) {
      const ak = a0 + sg * th * k / n;
      out.push([cx + sg * R * Math.sin(ak), cy - sg * R * Math.cos(ak)]);
    }
    a = a0 + sg * th; P = out[out.length - 1].slice();
  }
  return out;
}
