#!/usr/bin/env python3
"""
Adaptador de evidencia: convierte las corridas reales de la Actividad 3
(consolidadas en la Actividad 4, carpeta datos-a4/) al mismo formato normalizado
que produce handleSummary de k6 en el pipeline. Sirve para ejecutar el evaluador
de quality gates sobre datos reales y demostrar que las reglas habrían bloqueado
los defectos D-01 … D-04.

  python3 pipeline/gates/desde_datos_a3.py <datos-a4> <carpeta_salida>
"""
import json, os, sys
import pandas as pd

datos, salida = sys.argv[1], sys.argv[2]
os.makedirs(salida, exist_ok=True)
kpis = pd.read_csv(os.path.join(datos, "kpis-escenario.csv")).set_index("escenario")
tx = pd.read_csv(os.path.join(datos, "p95-transacciones.csv"))
serie = pd.read_csv(os.path.join(datos, "serie-temporal.csv"))

HUELLA_LINUX = "Linux | 1 vCPU | servicio y k6 en la misma VM | k6 v1.0.0"
HUELLA_WINDOWS = "Windows | equipo personal | k6 v1.0.0 | sin muestreo de host"


def nn(x):
    return None if pd.isna(x) else float(x)


def resultado(esc, huella, objetivo=None, throughput_meseta=None):
    k = kpis.loc[esc]
    t = tx[tx.escenario == esc].set_index("transaccion")
    s = serie[serie.escenario == esc]
    return {
        "escenario": "ruta_critica" if esc == "ruta_critica" else "carga",
        "corrida": esc,
        "origen": "Actividad 3 (15-sep-2026) vía datos-a4/",
        "huella": huella,
        "carga_objetivo_req_s": objetivo,
        "error_pct": float(k.error_pct),
        "p95_global_ms": float(k.p95_ms),
        "throughput_req_s": float(k.throughput_req_s),
        "transacciones": {i: {"p95_ms": float(r.p95_ms), "p99_ms": float(r.p99_ms), "n": int(r.n)}
                          for i, r in t.iterrows()},
        "db_cola_max": nn(k.db_cola_max),
        "pool": 4,
        "rechazos_503": float(s.r503_s.sum()) if len(s) else None,
        "throughput_meseta_req_s": throughput_meseta,
    }


rc = serie[serie.escenario == "ruta_critica"]
capacidad = float(rc[rc.db_cola <= 8].rps.max())   # mejor throughput sostenido sin saturar el pool
corridas = {
    "ruta_critica": resultado("ruta_critica", HUELLA_LINUX, 60, capacidad),
    "carga": resultado("carga", HUELLA_LINUX),
    "carga-r1": resultado("carga-r1", HUELLA_WINDOWS),
    "carga-r2": resultado("carga-r2", HUELLA_WINDOWS),
    "carga-r3": resultado("carga-r3", HUELLA_WINDOWS),
}
for n, r in corridas.items():
    with open(os.path.join(salida, f"resultado-{n}.json"), "w", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, indent=2)
print(f"{len(corridas)} resultados normalizados en {salida}")
