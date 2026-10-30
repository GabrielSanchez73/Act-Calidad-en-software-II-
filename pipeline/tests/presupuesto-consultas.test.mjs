// QG-03 — Presupuesto de consultas SQL por petición (guardia contra N+1).
//
// Cuenta las sentencias que llegan a MySQL mientras se atiende UNA petición,
// leyendo los contadores globales Com_select/insert/update/delete antes y después.
// No depende de cómo esté escrito el backend (pool.query, ORM, etc.): mide lo que
// realmente llega a la base de datos. Por eso exige una base de datos exclusiva
// para la prueba (el contenedor de servicio de MySQL del pipeline).
//
//   BASE_URL=http://localhost:3000 DB_HOST=127.0.0.1 DB_USER=root DB_PASSWORD=ci \
//   node --test pipeline/tests/presupuesto-consultas.test.mjs
//
// Falla si un endpoint supera su presupuesto (umbrales.json → QG-03). Con el N+1
// de la Actividad 3 el detalle supera ampliamente 3 consultas (estimación ~20).
import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import mysql from 'mysql2/promise';

const BASE = process.env.BASE_URL || 'http://localhost:3000';
const umbrales = JSON.parse(await readFile(new URL('../gates/umbrales.json', import.meta.url)));
const PRESUPUESTO = umbrales.reglas.find((r) => r.id === 'QG-03').umbral;

const RUTAS = {
  detalle: process.env.RUTA_DETALLE_PRUEBA || '/api/productos/1',
  busqueda: process.env.RUTA_BUSQUEDA_PRUEBA || '/api/productos/buscar?q=cafe',
  catalogo: process.env.RUTA_CATALOGO_PRUEBA || '/api/productos?pagina=1',
};

let conexion;
before(async () => {
  conexion = await mysql.createConnection({
    host: process.env.DB_HOST || '127.0.0.1', port: Number(process.env.DB_PORT || 3306),
    user: process.env.DB_USER || 'root', password: process.env.DB_PASSWORD || '',
  });
});
after(async () => conexion && conexion.end());

async function sentencias() {
  const [filas] = await conexion.query(
    "SHOW GLOBAL STATUS WHERE Variable_name IN ('Com_select','Com_insert','Com_update','Com_delete')");
  return filas.reduce((s, f) => s + Number(f.Value), 0);
}

async function consultasPorPeticion(ruta) {
  await fetch(BASE + ruta);                     // calentamiento: cachés y conexiones del pool
  const medidas = [];
  for (let i = 0; i < 3; i++) {
    const reposo0 = await sentencias();          // calibración: actividad de fondo sin peticiones
    const reposo1 = await sentencias();
    const antes = await sentencias();
    const r = await fetch(BASE + ruta);
    assert.ok(r.ok, `${ruta} respondió ${r.status}`);
    await r.arrayBuffer();
    const despues = await sentencias();
    medidas.push(despues - antes - (reposo1 - reposo0));
  }
  return Math.max(...medidas);
}

for (const [transaccion, ruta] of Object.entries(RUTAS)) {
  test(`QG-03 ${transaccion}: <= ${PRESUPUESTO[transaccion]} consultas por petición`, async (t) => {
    const n = await consultasPorPeticion(ruta);
    t.diagnostic(`${transaccion}: ${n} consultas por petición (presupuesto ${PRESUPUESTO[transaccion]})`);
    assert.ok(n <= PRESUPUESTO[transaccion],
      `${transaccion} ejecuta ${n} consultas por petición; presupuesto ${PRESUPUESTO[transaccion]} ` +
      `(posible N+1, ver D-01 en el acta de triage)`);
  });
}
