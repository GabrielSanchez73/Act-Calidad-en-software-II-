// Configuración compartida por los scripts de quality gate.
// Las rutas deben coincidir con las de los scripts k6 de la Actividad 3;
// se pueden sobrescribir sin tocar código con variables de entorno.
import http from 'k6/http';
import { check } from 'k6';

export const BASE = __ENV.BASE_URL || 'http://localhost:3000';
export const UMBRALES = JSON.parse(open(__ENV.UMBRALES || '../gates/umbrales.json'));

export const RUTAS = {
  login:    __ENV.RUTA_LOGIN    || '/api/auth/login',
  catalogo: __ENV.RUTA_CATALOGO || '/api/productos?pagina=1',
  busqueda: __ENV.RUTA_BUSQUEDA || '/api/productos/buscar?q=',
  detalle:  __ENV.RUTA_DETALLE  || '/api/productos/',
  carrito:  __ENV.RUTA_CARRITO  || '/api/carrito',
  checkout: __ENV.RUTA_CHECKOUT || '/api/pedidos',
  metricas: __ENV.RUTA_METRICAS || '/metricas',
};

export const TERMINOS = ['cafe', 'leche', 'arroz', 'jabon', 'aceite', 'pan'];
export const IDS_PRODUCTO = (__ENV.IDS_PRODUCTO || '1,2,3,4,5,6,7,8,9,10').split(',');

// Cada petición lleva la etiqueta "transaccion": los thresholds por transacción
// (QG-06) se definen sobre esa etiqueta, igual que en la Actividad 3.
export function get(transaccion, ruta, params = {}) {
  const r = http.get(`${BASE}${ruta}`, Object.assign({ tags: { transaccion } }, params));
  check(r, { [`${transaccion} 2xx`]: (x) => x.status >= 200 && x.status < 300 }, { transaccion });
  return r;
}

export function post(transaccion, ruta, cuerpo, params = {}) {
  const r = http.post(`${BASE}${ruta}`, JSON.stringify(cuerpo), Object.assign({
    headers: { 'Content-Type': 'application/json' }, tags: { transaccion },
  }, params));
  check(r, { [`${transaccion} 2xx`]: (x) => x.status >= 200 && x.status < 300 }, { transaccion });
  return r;
}

// Lee el endpoint /metricas del servicio. Admite el formato plano usado por el
// muestreador de la Actividad 3 (db_cola, rechazos_503) y uno anidado (db.cola).
export function leerMetricas() {
  const r = http.get(`${BASE}${RUTAS.metricas}`, { tags: { transaccion: 'monitor' } });
  if (r.status !== 200) return null;
  const m = r.json();
  return {
    cola: Number(m.db_cola ?? (m.db && m.db.cola) ?? 0),
    activas: Number(m.db_activas ?? (m.db && m.db.activas) ?? 0),
    rechazos: Number(m.rechazos_503 ?? (m.db && m.db.rechazos_503) ?? 0),
  };
}

// Huella del entorno: la calcula el pipeline (uname, nproc, versiones) y la pasa
// en HUELLA. Sin huella, el evaluador no compara contra ninguna línea base (QG-09).
export const HUELLA = __ENV.HUELLA || 'sin-huella';
