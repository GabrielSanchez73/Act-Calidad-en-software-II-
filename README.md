# Actividad 5 — Sesión de triage + plan de mejora

**Servicio:** API REST del proyecto *E-commerce Flutter G1* (Node.js + Express + MySQL)
**Insumo:** ejecución de la Actividad 3 (k6 v1.0.0, 15-sep-2026) consolidada en la Actividad 4
**Autores:** Jeisson Andrés Villarraga Reyes y Gabriel Alejandro Sanchez Mora — Universidad de La Salle

Este repositorio contiene los anexos del informe de la Actividad 5 (entregado en la plataforma del curso):
datos de entrada, figuras de evidencia, diagramas Ishikawa, matrices de priorización, scripts de análisis y
la configuración de quality gates. Las figuras del informe se generan desde `evidencias/figuras/`.

## Anexos del informe

| Anexo                   | Carpetas                                                                                                  |
| ----------------------- | --------------------------------------------------------------------------------------------------------- |
| A. Entradas y evidencia | `datos-a4/`, `evidencias/hallazgos.json`, `evidencias/panel-*.png`, `evidencias/figuras/ev-*.png` |
| B. Triage               | `evidencias/figuras/matriz-impacto-urgencia.png`                                                        |
| C. Causa raíz          | `evidencias/figuras/ishikawa-D-0*.png`, `analisis/`                                                   |
| D. Plan de mejora       | `evidencias/figuras/matriz-impacto-esfuerzo.png`                                                        |
| E. Quality gates        | `pipeline/`, `evidencias/gate/`                                                                       |

## Contenido

| Carpeta / archivo                                              | Qué es                                                                                                                                                                     |
| -------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `datos-a4/`                                                  | Datos consolidados de la A4 (copiados sin cambios): única fuente de todas las cifras                                                                                       |
| `analisis/analizar_defectos.py`                              | Recalcula la evidencia de los defectos → `evidencias/hallazgos.json` y figuras `ev-*.png` (D-05 usa `datos-a4/p95-transacciones.csv` directamente)                   |
| `analisis/ishikawa.py`                                       | Genera los 5 diagramas de Ishikawa con etiquetas uniformes: V (observado), I (inferencia), H (hipótesis), X (descartada por la evidencia) y ★ (causa sistémica inferida) |
| `analisis/matriz_triage.py`                                  | Matriz impacto × urgencia del triage (prioridad P1–P4)                                                                                                                    |
| `analisis/matriz_plan.py`, `analisis/pipeline.mmd`         | Matriz impacto/esfuerzo y diagrama del pipeline                                                                                                                             |
| `evidencias/figuras/`                                        | Figuras usadas en el documento                                                                                                                                              |
| `evidencias/panel-*.png`                                     | Capturas del dashboard de la A4 usadas como evidencia                                                                                                                       |
| `evidencias/gate/`                                           | Ejecución del evaluador de quality gates sobre las corridas reales: reportes por caso, `registro.txt` con códigos de salida, líneas base generadas                     |
| `pipeline/gates/umbrales.json`                               | **Fuente única de umbrales** QG-01 … QG-11, cada regla con el defecto que previene                                                                                  |
| `.github/workflows/gate-evidencia.yml` | Workflow que se ejecuta en este repositorio: aplica QG-05 a QG-09 a las corridas de la A3 (carga pasa, ruta crítica se bloquea) |
| `pipeline/ci/quality-gates.yml` | Pipeline completo propuesto para el repositorio del API (jobs `estatica`, `servicio` y `despliegue`, fail-fast; QG-11 con `npm audit`) |
| `pipeline/k6/smoke.js`, `pipeline/k6/ruta-critica-gate.js` | QG-04 … QG-08 con thresholds y `abortOnFail`                                                                                                                             |
| `pipeline/tests/presupuesto-consultas.test.mjs`              | QG-03: guardia contra N+1 (cuenta consultas reales en MySQL)                                                                                                                |
| `pipeline/gates/evaluar_gate.py`                             | QG-09 (regresión por huella de entorno) y reporte por regla para el PR                                                                                                     |
| `pipeline/gates/desde_datos_a3.py`                           | Adaptador: corridas de la A3 → formato de `handleSummary` de k6                                                                                                          |
| `pipeline/sonar-project.properties`                          | QG-01 / QG-02 (SonarQube, gate «Sonar way»)                                                                                                                               |
| `pipeline/alertas/slo-reglas.yml`                            | QG-10: alertas de burn rate y saturación del pool (Prometheus)                                                                                                             |
| `.github/PULL_REQUEST_TEMPLATE.md` | Trazabilidad defecto → acción → KPI en cada PR                                                                                                                           |

## Reproducir

```bash
pip install pandas matplotlib
python3 analisis/analizar_defectos.py      # cifras + figuras de evidencia
python3 analisis/ishikawa.py               # diagramas de Ishikawa
python3 analisis/matriz_plan.py            # matriz impacto / esfuerzo
python3 analisis/matriz_triage.py          # matriz impacto × urgencia
bash evidencias/gate/ejecutar_evidencia.sh # evaluador de gates sobre la A3 (caso 1 sale con código 1)
```

## Evidencia en GitHub Actions

`gate-evidencia.yml` se ejecuta en cada pull request hacia `main` (o manualmente desde la pestaña Actions).
Normaliza las corridas de `datos-a4/` con `pipeline/gates/desde_datos_a3.py` y aplica el evaluador de gates:

- **Gate de rendimiento - escenario carga:** pasa (cumple los SLO de error, latencia y saturación).
- **Gate de rendimiento - ruta crítica:** falla con 6 condiciones bloqueantes (QG-05, QG-06, QG-07, QG-08).

El reporte por regla queda en el resumen de cada job y como artefacto `reporte-quality-gate`.

## Llevar el pipeline al repositorio del API

1. Copiar `pipeline/ci/quality-gates.yml` a `.github/workflows/` del repositorio del API, junto con
   `pipeline/k6/`, `pipeline/gates/` y `pipeline/tests/`, y ajustar las rutas relativas si cambia la estructura.
2. Configurar los secretos `SONAR_TOKEN` y `SONAR_HOST_URL` (SonarQube Cloud es gratuito para repos públicos).
3. Configurar el job `despliegue`: `scripts/desplegar.sh`, el secreto `DEPLOY_TOKEN` y la variable `PROD_URL`.
4. Revisar en `pipeline/k6/comun.js` y en el workflow las rutas del API, `db/esquema.sql`, `db/semilla.sql`
   y el formato de `/metricas`; todas se pueden sobrescribir con variables de entorno.
5. Proteger `main` exigiendo los checks `estatica` y `servicio`.
6. Abrir un PR: con el código actual debe fallar en QG-03 (N+1 del detalle). Ese PR fallido, con su
   reporte, es la evidencia «pipeline/MR» de la rúbrica; el PR de la acción A-01 debe pasarlo.

## Límites conocidos

- Los scripts k6 y la prueba de consultas se validaron sintácticamente, pero no se ejecutaron contra el API
  (el repositorio no estaba disponible al preparar la entrega). Las rutas son las de referencia.
- Las fechas objetivo son del plan de mejora. El objetivo de 60 req/s y la referencia a Black Friday son
  supuestos del escenario de planificación, no una previsión validada de demanda.
- `pipeline/ci/quality-gates.yml` se preparó como diseño técnico y no se ejecutó contra el API real; adaptar
  rutas, secretos, runner y comandos al repositorio de servicio antes de habilitar los checks como obligatorios.
  Lo que sí se ejecuta en este repositorio es `gate-evidencia.yml`, sobre los datos reales de la A3.
