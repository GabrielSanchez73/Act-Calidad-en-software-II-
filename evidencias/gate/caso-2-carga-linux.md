### Quality gate de rendimiento — escenario `carga`

**✅ GATE PASA** (0 condición(es) bloqueante(s) incumplida(s))

Huella del entorno: `17a822cdfc04` · origen: Actividad 3 (15-sep-2026) vía datos-a4/

| Regla | Estado | Medido | Umbral | Detalle | Previene |
|---|---|---|---|---|---|
| QG-05 | PASA | 0.000 % | < 1.0 % |  | D-02 |
| QG-06 | PASA | busqueda P95 128.6 ms | < 1000 ms | margen 87.1 % | D-01, D-05 |
| QG-06 | PASA | busqueda P99 141.6 ms | < 1800 ms | margen 92.1 % | D-01, D-05 |
| QG-06 | PASA | carrito P95 14.0 ms | < 700 ms | margen 98.0 % | D-01, D-05 |
| QG-06 | PASA | carrito P99 27.4 ms | < 1200 ms | margen 97.7 % | D-01, D-05 |
| QG-06 | PASA | catalogo P95 33.5 ms | < 800 ms | margen 95.8 % | D-01, D-05 |
| QG-06 | PASA | catalogo P99 42.3 ms | < 1500 ms | margen 97.2 % | D-01, D-05 |
| QG-06 | PASA | checkout P95 58.8 ms | < 1500 ms | margen 96.1 % | D-01, D-05 |
| QG-06 | PASA | checkout P99 61.2 ms | < 2500 ms | margen 97.6 % | D-01, D-05 |
| QG-06 | PASA | detalle P95 73.2 ms | < 900 ms | margen 91.9 % | D-01, D-05 |
| QG-06 | PASA | detalle P99 78.0 ms | < 1600 ms | margen 95.1 % | D-01, D-05 |
| QG-06 | PASA | login P95 35.6 ms | < 1200 ms | margen 97.0 % | D-01, D-05 |
| QG-06 | PASA | login P99 40.8 ms | < 2000 ms | margen 98.0 % | D-01, D-05 |
| QG-07 | PASA | cola máx 1 | <= 8 (2 × pool) |  | D-01, D-02, D-03 |
| QG-07 | PASA | 0 rechazos 503 | <= 0 |  | D-01, D-02, D-03 |
| QG-08 | N/A | - | - | el escenario no define carga objetivo | D-03, D-05 |
| QG-09 | AVISO | - | - | sin línea base para esta huella y escenario: se registra como candidata | D-04 |
código de salida del evaluador: `0`
