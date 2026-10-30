// QG-05 … QG-08 — Gate de rendimiento de la ruta crítica (búsqueda + detalle).
//
// Modelo abierto (ramping-arrival-rate), igual que la prueba de ruta crítica de la
// Actividad 3: la llegada de usuarios no depende de lo rápido que responda el
// servicio, por eso una cola en el pool se ve como latencia, VU crecientes e
// iteraciones descartadas, en lugar de quedar escondida.
//
// Carga objetivo: 60 req/s = 30 sesiones/s (1,1 × meseta de pico de la A3).
// Duración total: 60 s de rampa + 120 s de meseta = 3 min.
//
//   k6 run pipeline/k6/ruta-critica-gate.js -e BASE_URL=http://localhost:3000 -e HUELLA="$HUELLA"
//
// Sale con código 99 si se incumple cualquier threshold; los marcados con
// abortOnFail cortan la prueba en cuanto el fallo es evidente (fail-fast).
import { sleep } from 'k6';
import exec from 'k6/execution';
import { Counter, Trend } from 'k6/metrics';
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.2/index.js';
import { UMBRALES, RUTAS, TERMINOS, IDS_PRODUCTO, HUELLA, get, leerMetricas } from './comun.js';

const OBJ_REQ_S = UMBRALES.carga_objetivo.ruta_critica_req_s;   // 60
const OBJ_SES_S = OBJ_REQ_S / 2;                                // 2 peticiones por sesión
const RAMPA_S = 60, MESETA_S = 120, MARGEN_S = 10;
const POOL = UMBRALES.carga_objetivo.pool_conexiones;
const regla = (id) => UMBRALES.reglas.find((r) => r.id === id);
const slo = UMBRALES.slo;

// Métricas propias
const colaPool = new Trend('db_cola');                 // QG-07, sondeada en /metricas
const rechazos503 = new Counter('rechazos_503');      // QG-07, contador del servicio
const peticionesMeseta = new Counter('peticiones_meseta');  // QG-08

const minimoMeseta = Math.floor(regla('QG-08').umbral * OBJ_REQ_S * (MESETA_S - MARGEN_S));
const totalIter = OBJ_SES_S * (RAMPA_S / 2 + MESETA_S);

export const options = {
  summaryTrendStats: ['avg', 'min', 'med', 'p(90)', 'p(95)', 'p(99)', 'max', 'count'],
  scenarios: {
    ruta_critica: {
      executor: 'ramping-arrival-rate',
      startRate: 2, timeUnit: '1s',
      preAllocatedVUs: 40,
      // Tope de VU = tasa × 4 s: si el servicio tarda más de 4 s por sesión, k6
      // descarta iteraciones y QG-08 lo detecta (en la A3 llegó a 254 VU).
      maxVUs: OBJ_SES_S * 4,
      stages: [
        { target: OBJ_SES_S, duration: `${RAMPA_S}s` },
        { target: OBJ_SES_S, duration: `${MESETA_S}s` },
      ],
      exec: 'rutaCritica',
    },
    monitor: {
      executor: 'constant-vus', vus: 1, duration: `${RAMPA_S + MESETA_S}s`,
      exec: 'monitor',
    },
  },
  thresholds: {
    // QG-05: error < 1 %. Fail-fast: se evalúa desde el segundo 30.
    'http_req_failed{scenario:ruta_critica}': [
      { threshold: `rate<${slo.error_pct_max / 100}`, abortOnFail: true, delayAbortEval: '30s' },
    ],
    // QG-06: P95/P99 dentro del SLO. Corte anticipado si el P95 triplica el SLO.
    'http_req_duration{transaccion:detalle}': [
      `p(95)<${slo.p95_ms.detalle}`, `p(99)<${slo.p99_ms.detalle}`,
      { threshold: `p(95)<${slo.p95_ms.detalle * 3}`, abortOnFail: true, delayAbortEval: '30s' },
    ],
    'http_req_duration{transaccion:busqueda}': [
      `p(95)<${slo.p95_ms.busqueda}`, `p(99)<${slo.p99_ms.busqueda}`,
      { threshold: `p(95)<${slo.p95_ms.busqueda * 3}`, abortOnFail: true, delayAbortEval: '30s' },
    ],
    'http_req_duration{scenario:ruta_critica}': [`p(95)<${slo.p95_global_ms}`],
    // QG-07: el pool no debe saturarse a la carga objetivo
    db_cola: [`max<=${regla('QG-07').umbral.cola_max}`],
    rechazos_503: [`count<=${regla('QG-07').umbral.rechazos_503}`],
    // QG-08: capacidad sostenida >= 95 % del objetivo e iteraciones descartadas <= 1 %
    peticiones_meseta: [`count>=${minimoMeseta}`],
    dropped_iterations: [`count<=${Math.ceil(totalIter * 0.01)}`],
    'checks{scenario:ruta_critica}': ['rate>0.99'],
  },
};

export function rutaCritica() {
  const t = (Date.now() - exec.scenario.startTime) / 1000;
  const enMeseta = t >= RAMPA_S + MARGEN_S;
  const termino = TERMINOS[exec.scenario.iterationInTest % TERMINOS.length];
  const id = IDS_PRODUCTO[exec.scenario.iterationInTest % IDS_PRODUCTO.length];

  const r1 = get('busqueda', RUTAS.busqueda + termino);
  const r2 = get('detalle', RUTAS.detalle + id);
  if (enMeseta) peticionesMeseta.add([r1, r2].filter((r) => r.status < 400).length);
}

let ultimoRechazos = null;
export function monitor() {
  const m = leerMetricas();
  if (m) {
    colaPool.add(m.cola);
    // Mismo método que la A3: diferencia del contador rechazos_503 del servicio
    if (ultimoRechazos === null) rechazos503.add(0);   // la métrica existe aunque no haya 503
    if (ultimoRechazos !== null && m.rechazos > ultimoRechazos) {
      rechazos503.add(m.rechazos - ultimoRechazos);
    }
    ultimoRechazos = m.rechazos;
  }
  sleep(1);
}

// Resultado normalizado para el evaluador (QG-09) y para el reporte del PR.
export function handleSummary(data) {
  const v = (n, k) => (data.metrics[n] && data.metrics[n].values[k] !== undefined ? data.metrics[n].values[k] : null);
  const tx = {};
  for (const t of ['busqueda', 'detalle']) {
    const n = `http_req_duration{transaccion:${t}}`;
    tx[t] = { p95_ms: v(n, 'p(95)'), p99_ms: v(n, 'p(99)'), n: v(n, 'count') };
  }
  const resultado = {
    escenario: 'ruta_critica',
    origen: 'k6 handleSummary',
    huella: HUELLA,
    commit: __ENV.GITHUB_SHA || null,
    carga_objetivo_req_s: OBJ_REQ_S,
    error_pct: (v('http_req_failed{scenario:ruta_critica}', 'rate') ?? 0) * 100,
    p95_global_ms: v('http_req_duration{scenario:ruta_critica}', 'p(95)'),
    transacciones: tx,
    db_cola_max: v('db_cola', 'max'),
    pool: POOL,
    rechazos_503: v('rechazos_503', 'count') ?? 0,
    throughput_meseta_req_s: (v('peticiones_meseta', 'count') ?? 0) / (MESETA_S - MARGEN_S),
    throughput_req_s: (v('peticiones_meseta', 'count') ?? 0) / (MESETA_S - MARGEN_S),
    iteraciones_descartadas_pct: ((v('dropped_iterations', 'count') ?? 0) / totalIter) * 100,
    checks_rate: v('checks{scenario:ruta_critica}', 'rate'),
    thresholds_fallidos: Object.entries(data.metrics)
      .flatMap(([n, m]) => Object.entries(m.thresholds || {}).filter(([, t]) => !t.ok).map(([e]) => `${n}: ${e}`)),
  };
  return {
    stdout: textSummary(data, { indent: '  ', enableColors: false }),
    'resultados/resultado-ruta_critica.json': JSON.stringify(resultado, null, 2),
    'resultados/k6-summary-ruta_critica.json': JSON.stringify(data, null, 2),
  };
}
