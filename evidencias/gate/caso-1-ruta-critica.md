### Quality gate de rendimiento — escenario `ruta_critica`

**❌ GATE FALLA — el cambio no puede fusionarse** (6 condición(es) bloqueante(s) incumplida(s))

Huella del entorno: `17a822cdfc04` · origen: Actividad 3 (15-sep-2026) vía datos-a4/

| Regla | Estado | Medido | Umbral | Detalle | Previene |
|---|---|---|---|---|---|
| QG-05 | FALLA | 1.329 % | < 1.0 % |  | D-02 |
| QG-06 | PASA | busqueda P95 850.8 ms | < 1000 ms | margen 14.9 % | D-01, D-05 |
| QG-06 | PASA | busqueda P99 941.8 ms | < 1800 ms | margen 47.7 % | D-01, D-05 |
| QG-06 | FALLA | detalle P95 9,124.6 ms | < 900 ms | 10.1× el SLO | D-01, D-05 |
| QG-06 | FALLA | detalle P99 9,335.7 ms | < 1600 ms | 5.8× el SLO | D-01, D-05 |
| QG-07 | FALLA | cola máx 250 | <= 8 (2 × pool) | 62× el tamaño del pool | D-01, D-02, D-03 |
| QG-07 | FALLA | 105 rechazos 503 | <= 0 |  | D-01, D-02, D-03 |
| QG-08 | FALLA | 49.4 req/s | >= 57.0 req/s (95 % de 60) | 82 % del objetivo | D-03, D-05 |
| QG-09 | AVISO | - | - | sin línea base para esta huella y escenario: se registra como candidata | D-04 |
código de salida del evaluador: `1`
