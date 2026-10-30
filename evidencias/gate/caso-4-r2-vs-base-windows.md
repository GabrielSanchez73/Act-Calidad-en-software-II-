### Quality gate de rendimiento — escenario `carga`

**✅ GATE PASA** (0 condición(es) bloqueante(s) incumplida(s))

Huella del entorno: `130f82d1e6ee` · origen: Actividad 3 (15-sep-2026) vía datos-a4/

| Regla | Estado | Medido | Umbral | Detalle | Previene |
|---|---|---|---|---|---|
| QG-05 | PASA | 0.028 % | < 1.0 % |  | D-02 |
| QG-06 | PASA | busqueda P95 139.4 ms | < 1000 ms | margen 86.1 % | D-01, D-05 |
| QG-06 | PASA | busqueda P99 150.2 ms | < 1800 ms | margen 91.7 % | D-01, D-05 |
| QG-06 | PASA | carrito P95 24.6 ms | < 700 ms | margen 96.5 % | D-01, D-05 |
| QG-06 | PASA | carrito P99 31.3 ms | < 1200 ms | margen 97.4 % | D-01, D-05 |
| QG-06 | PASA | catalogo P95 38.5 ms | < 800 ms | margen 95.2 % | D-01, D-05 |
| QG-06 | PASA | catalogo P99 47.0 ms | < 1500 ms | margen 96.9 % | D-01, D-05 |
| QG-06 | PASA | checkout P95 78.5 ms | < 1500 ms | margen 94.8 % | D-01, D-05 |
| QG-06 | PASA | checkout P99 100.9 ms | < 2500 ms | margen 96.0 % | D-01, D-05 |
| QG-06 | PASA | detalle P95 209.8 ms | < 900 ms | margen 76.7 % | D-01, D-05 |
| QG-06 | PASA | detalle P99 243.3 ms | < 1600 ms | margen 84.8 % | D-01, D-05 |
| QG-06 | PASA | login P95 43.6 ms | < 1200 ms | margen 96.4 % | D-01, D-05 |
| QG-06 | PASA | login P99 52.0 ms | < 2000 ms | margen 97.4 % | D-01, D-05 |
| QG-07 | N/A | - | <= 8 | la corrida no trae métricas del servicio (/metricas) | D-01, D-02, D-03 |
| QG-08 | N/A | - | - | el escenario no define carga objetivo | D-03, D-05 |
| QG-09 | PASA | busqueda P95 139.4 ms vs base 137.4 ms | <= +20 % | +1.5 % | D-04 |
| QG-09 | PASA | carrito P95 24.6 ms vs base 25.4 ms | <= +20 % | -3.1 % | D-04 |
| QG-09 | PASA | catalogo P95 38.5 ms vs base 42.2 ms | <= +20 % | -8.8 % | D-04 |
| QG-09 | PASA | checkout P95 78.5 ms vs base 76.0 ms | <= +20 % | +3.3 % | D-04 |
| QG-09 | PASA | detalle P95 209.8 ms vs base 217.3 ms | <= +20 % | -3.5 % | D-04 |
| QG-09 | PASA | login P95 43.6 ms vs base 43.1 ms | <= +20 % | +1.2 % | D-04 |
| QG-09 | PASA | throughput 19.86 vs base 19.71 req/s | caída <= 10 % | +0.8 % | D-04 |
código de salida del evaluador: `0`
