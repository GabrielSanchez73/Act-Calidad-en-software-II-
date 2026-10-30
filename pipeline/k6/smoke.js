// QG-04 — Smoke de las 6 transacciones (fail-fast, ~30 s).
// Falla el pipeline (k6 sale con código 99) si alguna transacción no se ejecuta,
// si algún check falla o si hay un solo error HTTP.
//   k6 run pipeline/k6/smoke.js -e BASE_URL=http://localhost:3000
import { sleep } from 'k6';
import { Counter } from 'k6/metrics';
import { RUTAS, TERMINOS, IDS_PRODUCTO, get, post } from './comun.js';

const ejecutadas = new Counter('transacciones_ejecutadas');
const TX = ['login', 'catalogo', 'busqueda', 'detalle', 'carrito', 'checkout'];

const umbralesPorTx = {};
for (const t of TX) {
  // "count>0" por transacción = cobertura mínima del smoke: 6/6
  umbralesPorTx[`transacciones_ejecutadas{transaccion:${t}}`] = ['count>0'];
  umbralesPorTx[`checks{transaccion:${t}}`] = ['rate==1'];
}

export const options = {
  vus: 1,
  iterations: 3,
  thresholds: Object.assign({
    http_req_failed: [{ threshold: 'rate==0', abortOnFail: true }],
    checks: [{ threshold: 'rate==1', abortOnFail: true }],
  }, umbralesPorTx),
};

export default function () {
  const usuario = { correo: __ENV.USUARIO || 'qa@g1.test', clave: __ENV.CLAVE || 'qa-g1' };
  const marca = (t) => ejecutadas.add(1, { transaccion: t });

  const sesion = post('login', RUTAS.login, usuario); marca('login');
  const token = sesion.status === 200 ? (sesion.json('token') || '') : '';
  const auth = { headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' } };

  get('catalogo', RUTAS.catalogo); marca('catalogo');
  get('busqueda', RUTAS.busqueda + TERMINOS[__ITER % TERMINOS.length]); marca('busqueda');
  const id = IDS_PRODUCTO[__ITER % IDS_PRODUCTO.length];
  get('detalle', RUTAS.detalle + id); marca('detalle');
  post('carrito', RUTAS.carrito, { productoId: Number(id), cantidad: 1 }, auth); marca('carrito');
  post('checkout', RUTAS.checkout, { metodoPago: 'prueba' }, auth); marca('checkout');
  sleep(1);
}
