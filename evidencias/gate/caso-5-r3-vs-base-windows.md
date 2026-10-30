### Quality gate de rendimiento — escenario `carga`

**✅ GATE PASA** (0 condición(es) bloqueante(s) incumplida(s))

Huella del entorno: `130f82d1e6ee` · origen: Actividad 3 (15-sep-2026) vía datos-a4/

| Regla | Estado | Medido | Umbral | Detalle | Previene |
|---|---|---|---|---|---|
| QG-05 | PASA | 0.000 % | < 1.0 % |  | D-02 |
| QG-06 | PASA | busqueda P95 139.6 ms | < 1000 ms | margen 86.0 % | D-01, D-05 |
| QG-06 | PASA | busqueda P99 150.1 ms | < 1800 ms | margen 91.7 % | D-01, D-05 |
| QG-06 | PASA | carrito P95 21.1 ms | < 700 ms | margen 97.0 % | D-01, D-05 |
| QG-06 | PASA | carrito P99 31.0 ms | < 1200 ms | margen 97.4 % | D-01, D-05 |
| QG-06 | PASA | catalogo P95 40.6 ms | < 800 ms | margen 94.9 % | D-01, D-05 |
| QG-06 | PASA | catalogo P99 46.8 ms | < 1500 ms | margen 96.9 % | D-01, D-05 |
| QG-06 | PASA | checkout P95 82.5 ms | < 1500 ms | margen 94.5 % | D-01, D-05 |
| QG-06 | PASA | checkout P99 96.0 ms | < 2500 ms | margen 96.2 % | D-01, D-05 |
| QG-06 | PASA | detalle P95 214.3 ms | < 900 ms | margen 76.2 % | D-01, D-05 |
| QG-06 | PASA | detalle P99 269.0 ms | < 1600 ms | margen 83.2 % | D-01, D-05 |
| QG-06 | PASA | login P95 43.3 ms | < 1200 ms | margen 96.4 % | D-01, D-05 |
| QG-06 | PASA | login P99 52.2 ms | < 2000 ms | margen 97.4 % | D-01, D-05 |
| QG-07 | N/A | - | <= 8 | la corrida no trae métricas del servicio (/metricas) | D-01, D-02, D-03 |
| QG-08 | N/A | - | - | el escenario no define carga objetivo | D-03, D-05 |
| QG-09 | PASA | busqueda P95 139.6 ms vs base 137.4 ms | <= +20 % | +1.6 % | D-04 |
| QG-09 | PASA | carrito P95 21.1 ms vs base 25.4 ms | <= +20 % | -16.9 % | D-04 |
| QG-09 | PASA | catalogo P95 40.6 ms vs base 42.2 ms | <= +20 % | -3.8 % | D-04 |
| QG-09 | PASA | checkout P95 82.5 ms vs base 76.0 ms | <= +20 % | +8.6 % | D-04 |
| QG-09 | PASA | detalle P95 214.3 ms vs base 217.3 ms | <= +20 % | -1.4 % | D-04 |
| QG-09 | PASA | login P95 43.3 ms vs base 43.1 ms | <= +20 % | +0.5 % | D-04 |
| QG-09 | PASA | throughput 20.02 vs base 19.71 req/s | caída <= 10 % | +1.6 % | D-04 |
código de salida del evaluador: `0`
