#!/usr/bin/env python3
"""
Actividad 5 — Insumo cuantitativo para el triage.

Lee los datos consolidados de la Actividad 4 (que a su vez provienen de la
ejecución de la Actividad 3) y calcula la evidencia de cada defecto. No hay
valores escritos a mano: todo número citado en el acta y en el análisis
causa-raíz sale de evidencias/hallazgos.json, que genera este script.

  python3 analisis/analizar_defectos.py

Salidas:
  evidencias/hallazgos.json            cifras por defecto (D-01 … D-04)
  evidencias/figuras/ev-*.png          figuras de evidencia
"""
import json, os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS = os.path.join(RAIZ, "datos-a4")
FIG = os.path.join(RAIZ, "evidencias", "figuras")
os.makedirs(FIG, exist_ok=True)

POOL = 4                      # conexiones máximas del pool (Actividad 3)
SLO = {"detalle": 900, "busqueda": 1000, "catalogo": 800, "login": 1200,
       "carrito": 700, "checkout": 1500}

# Paleta de referencia (skill dataviz, modo claro)
AZUL, NARANJA, AGUA = "#2a78d6", "#eb6834", "#1baf7a"
TINTA, TINTA2, REJILLA = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": TINTA2,
    "axes.labelcolor": TINTA, "xtick.color": TINTA2, "ytick.color": TINTA2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
    "grid.color": REJILLA, "grid.linewidth": 0.8, "figure.dpi": 150,
    "lines.linewidth": 2, "axes.axisbelow": True,
})

serie = pd.read_csv(os.path.join(DATOS, "serie-temporal.csv"))
kpis = pd.read_csv(os.path.join(DATOS, "kpis-escenario.csv")).set_index("escenario")
tx = pd.read_csv(os.path.join(DATOS, "p95-transacciones.csv"))

rc = serie[serie.escenario == "ruta_critica"].copy()
es = serie[serie.escenario == "estres"].copy()
h = {}

# ---------------------------------------------------------------- D-01
codo = rc[rc.p95_ms > 1000].iloc[0]
pre = rc[rc.db_cola <= 2 * POOL]            # tramo sin saturación del pool
det_rc = tx[(tx.escenario == "ruta_critica") & (tx.transaccion == "detalle")].iloc[0]
bus_rc = tx[(tx.escenario == "ruta_critica") & (tx.transaccion == "busqueda")].iloc[0]
det_c = tx[(tx.escenario == "carga") & (tx.transaccion == "detalle")].iloc[0]
h["D-01"] = {
    "p95_global_ms": float(kpis.loc["ruta_critica", "p95_ms"]),
    "p99_global_ms": float(kpis.loc["ruta_critica", "p99_ms"]),
    "p95_detalle_ms": float(det_rc.p95_ms), "p99_detalle_ms": float(det_rc.p99_ms),
    "max_detalle_ms": float(det_rc.max_ms), "p50_detalle_ms": float(det_rc.p50_ms),
    "slo_detalle_ms": SLO["detalle"],
    "veces_sobre_slo": round(float(det_rc.p95_ms) / SLO["detalle"], 1),
    "p95_busqueda_ms": float(bus_rc.p95_ms), "slo_busqueda_ms": SLO["busqueda"],
    "margen_busqueda_pct": float(bus_rc.margen_p95_pct),
    "p95_detalle_carga_ms": float(det_c.p95_ms),
    "ratio_detalle_vs_busqueda": round(float(det_rc.p95_ms) / float(bus_rc.p95_ms), 1),
    "codo_t_s": int(codo.t_seg), "codo_ts": codo.ts,
    "cola_max": int(rc.db_cola.max()), "pool": POOL,
    "cpu_host_max_pct": float(kpis.loc["ruta_critica", "cpu_host_max_pct"]),
    "cpu_sut_max_pct": float(kpis.loc["ruta_critica", "cpu_sut_max_pct"]),
    "lag_p99_max_ms": float(kpis.loc["ruta_critica", "lag_p99_max_ms"]),
    "peticiones": int(kpis.loc["ruta_critica", "peticiones"]),
    "sesiones": int(kpis.loc["ruta_critica", "sesiones"]),
}

# ---------------------------------------------------------------- D-02
rc["errores"] = (rc.error_pct / 100 * rc.peticiones).round()
con_error = rc[rc.errores > 0]
h["D-02"] = {
    "error_pct": float(kpis.loc["ruta_critica", "error_pct"]),
    "errores": int(rc.errores.sum()), "rechazos_503": int(rc.r503_s.sum()),
    "peticiones": int(rc.peticiones.sum()),
    "presupuesto_consumido_pct": float(kpis.loc["ruta_critica", "presupuesto_error_consumido_pct"]),
    "ventana_errores_t_s": [int(con_error.t_seg.min()), int(con_error.t_seg.max()) + 5],
    "error_pct_max_bucket": float(rc.error_pct.max()),
    "cola_al_primer_503": int(rc[rc.r503_s > 0].iloc[0].db_cola),
    "p95_previo_al_503_ms": float(rc[rc.t_seg == int(con_error.t_seg.min()) - 5].p95_ms.iloc[0]),
    "otros_escenarios_error_pct": {e: float(kpis.loc[e, "error_pct"])
                                   for e in ["carga", "estres", "pico", "resistencia"]},
}

# ---------------------------------------------------------------- D-03
x_max = float(pre.rps.max())
sat = rc[(rc.t_seg >= int(codo.t_seg) - 5) & (rc.t_seg <= 220)]
pend, intercepto = np.polyfit(es[(es.t_seg >= 20) & (es.t_seg <= 205)].vus,
                              es[(es.t_seg >= 20) & (es.t_seg <= 205)].rps, 1)
r = np.corrcoef(es[(es.t_seg >= 20) & (es.t_seg <= 205)].vus,
                es[(es.t_seg >= 20) & (es.t_seg <= 205)].rps)[0, 1]
little = [{"t_s": int(f.t_seg), "vus": float(f.vus), "rps": float(f.rps),
           "R_little_s": round(f.vus / f.rps, 2), "p50_ms": float(f.p50_ms),
           "p95_ms": float(f.p95_ms), "cola": int(f.db_cola)} for _, f in sat.iterrows()]
h["D-03"] = {
    "throughput_max_sin_saturar_req_s": x_max,
    "sesiones_s_max": round(x_max / 2, 1),
    "tiempo_retencion_conexion_ms": round(POOL / x_max * 1000, 1),
    "tiempo_retencion_por_sesion_ms": round(POOL / (x_max / 2) * 1000, 1),
    "p50_detalle_baja_carga_ms": float(det_rc.p50_ms),
    "throughput_en_saturacion_req_s": [float(sat.rps.min()), float(sat.rps.max())],
    "vus_en_saturacion": [float(sat.vus.min()), float(sat.vus.max())],
    "little": little,
    "estres_pendiente_req_s_por_vu": round(float(pend), 3),
    "estres_r": round(float(r), 4),
    "estres_throughput_max_req_s": float(es.rps.max()),
    "estres_vus_max": float(es.vus.max()), "estres_cola_max": int(es.db_cola.max()),
    "pico_throughput_meseta_req_s": float(kpis.loc["pico", "throughput_req_s"]),
}

# ---------------------------------------------------------------- D-04
lin = tx[tx.escenario == "carga"].set_index("transaccion")
win = tx[tx.escenario.isin(["carga-r1", "carga-r2", "carga-r3", "carga-integridad"])]
win_m = win.groupby("transaccion")[["p50_ms", "p95_ms"]].mean()
comp = pd.DataFrame({"p50_linux": lin.p50_ms, "p50_windows": win_m.p50_ms,
                     "p95_linux": lin.p95_ms, "p95_windows": win_m.p95_ms})
comp["delta_p50_ms"] = comp.p50_windows - comp.p50_linux
comp["factor_p50"] = comp.p50_windows / comp.p50_linux
reps = kpis.loc[["carga-r1", "carga-r2", "carga-r3", "carga-integridad"]]
# Δ por ida y vuelta a la BD ≈ Δp50 de transacciones de una consulta (catálogo, carrito)
delta_rtt = float(comp.loc[["catalogo", "carrito"], "delta_p50_ms"].mean())
h["D-04"] = {
    "p95_global_linux_ms": float(kpis.loc["carga", "p95_ms"]),
    "p95_global_windows_media_ms": round(float(reps.p95_ms.mean()), 1),
    "cv_p95_windows_pct": round(float(reps.p95_ms.std() / reps.p95_ms.mean() * 100), 2),
    "incremento_p95_global_pct": round(float(reps.p95_ms.mean() / kpis.loc["carga", "p95_ms"] - 1) * 100, 1),
    "throughput_linux": float(kpis.loc["carga", "throughput_req_s"]),
    "throughput_windows_media": round(float(reps.throughput_req_s.mean()), 2),
    "por_transaccion": comp.round(1).reset_index().rename(columns={"index": "transaccion"}).to_dict("records"),
    "delta_ida_vuelta_estimado_ms": round(delta_rtt, 1),
    "consultas_detalle_estimadas": round(float(comp.loc["detalle", "delta_p50_ms"]) / delta_rtt, 1),
    "corridas_windows_sin_metricas_host": int(reps.cpu_host_max_pct.isna().sum()),
}

with open(os.path.join(RAIZ, "evidencias", "hallazgos.json"), "w", encoding="utf-8") as f:
    json.dump(h, f, ensure_ascii=False, indent=2)


# ================================================================ FIGURAS
def guardar(fig, nombre):
    fig.savefig(os.path.join(FIG, nombre), bbox_inches="tight", facecolor="white")
    plt.close(fig)


# Fig. throughput frente a concurrencia (responde a la observación de la A4)
fig, (a, b) = plt.subplots(1, 2, figsize=(10.5, 4.0), sharey=True)
m = es[(es.t_seg <= 205)]
a.scatter(m.vus, m.rps, s=22, color=AZUL, edgecolor="white", linewidth=0.8, zorder=3)
xs = np.linspace(0, m.vus.max(), 50)
a.plot(xs, pend * xs + intercepto, color=AZUL, linewidth=1.2, linestyle="--", alpha=0.7)
a.set_title("Estrés (mezcla de 6 transacciones)", loc="left", fontsize=10.5, color=TINTA)
a.set_xlabel("Usuarios virtuales concurrentes")
a.set_ylabel("Throughput (req/s)")
a.text(0.03, 0.95, f"crece lineal: {pend:.2f} req/s por VU (r = {r:.3f})\nsin meseta hasta {es.vus.max():.0f} VU · cola máx {int(es.db_cola.max())}",
       transform=a.transAxes, va="top", fontsize=8.8, color=TINTA2)
pre_c = rc[rc.t_seg < int(codo.t_seg) - 5]
post_c = rc[(rc.t_seg >= int(codo.t_seg) - 5) & (rc.t_seg <= 220)]
b.scatter(pre_c.vus, pre_c.rps, s=22, color=AZUL, edgecolor="white", linewidth=0.8, zorder=3,
          label="antes del codo (cola ≤ 2)")
b.scatter(post_c.vus, post_c.rps, s=30, color=NARANJA, edgecolor="white", linewidth=0.8, zorder=4,
          label="después del codo (cola 9 → 216)")
b.axhline(x_max, color=TINTA2, linewidth=1, linestyle=":")
b.text(250, x_max + 1.5, f"techo ≈ {x_max:.1f} req/s", ha="right", fontsize=8.8, color=TINTA2)
b.set_xscale("log")
b.set_xlabel("Usuarios virtuales concurrentes (escala log)")
b.set_title("Ruta crítica (búsqueda + detalle)", loc="left", fontsize=10.5, color=TINTA)
b.legend(frameon=False, fontsize=8.5, loc="lower right")
guardar(fig, "ev-throughput-vs-concurrencia.png")

# Fig. línea de tiempo de la ruta crítica alrededor del codo (tres paneles, un eje cada uno)
v = rc[(rc.t_seg >= 150)]
fig, ejes = plt.subplots(3, 1, figsize=(10.5, 6.4), sharex=True)
ejes[0].plot(v.t_seg, v.p95_ms, color=AZUL); ejes[0].set_ylabel("P95 (ms)")
ejes[0].axhline(800, color=TINTA2, linestyle="--", linewidth=1)
ejes[0].text(152, 1100, "SLO 800 ms", fontsize=8.5, color=TINTA2)
ejes[1].plot(v.t_seg, v.db_cola, color=NARANJA); ejes[1].set_ylabel("Cola del pool")
ejes[1].axhline(POOL, color=TINTA2, linestyle="--", linewidth=1)
ejes[1].text(152, 20, "pool = 4 conexiones", fontsize=8.5, color=TINTA2)
ejes[2].bar(v.t_seg, v.r503_s, width=3.6, color=AGUA); ejes[2].set_ylabel("Rechazos 503")
ejes[2].set_xlabel("Segundos de prueba")
for ax in ejes:
    ax.axvline(int(codo.t_seg), color=TINTA2, linewidth=1, linestyle=":")
ejes[0].text(int(codo.t_seg) + 1, ejes[0].get_ylim()[1] * 0.85, f"codo t={int(codo.t_seg)} s", fontsize=8.5, color=TINTA2)
ejes[0].set_title("Ruta crítica: P95, cola del pool y rechazos 503 (buckets de 5 s)", loc="left", fontsize=10.5)
guardar(fig, "ev-linea-tiempo-ruta-critica.png")

# Fig. P95 de detalle y búsqueda frente a su SLO por escenario (escala log)
esc = ["carga", "estres", "pico", "resistencia", "ruta_critica"]
p = tx[tx.transaccion.isin(["detalle", "busqueda"]) & tx.escenario.isin(esc)]
fig, ax = plt.subplots(figsize=(10.5, 3.8))
w = 0.38
idx = np.arange(len(esc))
for i, (t, col) in enumerate([("busqueda", AZUL), ("detalle", NARANJA)]):
    vals = [float(p[(p.escenario == e) & (p.transaccion == t)].p95_ms.iloc[0]) for e in esc]
    ax.bar(idx + (i - 0.5) * w, vals, width=w - 0.04, color=col, label={"busqueda": "búsqueda"}.get(t, t))
    for xi, vv in zip(idx + (i - 0.5) * w, vals):
        ax.text(xi, vv * 1.12, f"{vv:,.0f}".replace(",", "."), ha="center", fontsize=8, color=TINTA)
ax.axhline(900, color=TINTA2, linestyle="--", linewidth=1)
ax.text(-0.45, 1000, "SLO detalle 900 ms", fontsize=8.5, color=TINTA2, ha="left")
ax.set_yscale("log"); ax.set_ylim(5, 30000)
ax.set_xticks(idx); ax.set_xticklabels(["carga", "estrés", "pico", "resistencia", "ruta crítica"])
ax.set_ylabel("P95 (ms, escala log)")
ax.legend(frameon=False, ncol=2, loc="upper left")
ax.set_title("P95 por transacción y escenario", loc="left", fontsize=10.5)
guardar(fig, "ev-p95-detalle-busqueda.png")

# Fig. Linux vs Windows por transacción (D-04)
orden = ["carrito", "catalogo", "login", "checkout", "busqueda", "detalle"]
fig, ax = plt.subplots(figsize=(10.5, 3.6))
idx = np.arange(len(orden))
ax.bar(idx - w / 2, comp.loc[orden, "p50_linux"], width=w - 0.04, color=AZUL, label="Linux (corrida base)")
ax.bar(idx + w / 2, comp.loc[orden, "p50_windows"], width=w - 0.04, color=NARANJA, label="Windows (media de 4 repeticiones)")
for i, t in enumerate(orden):
    ax.text(i + w / 2, comp.loc[t, "p50_windows"] + 4, f"+{comp.loc[t, 'delta_p50_ms']:.0f} ms", ha="center", fontsize=8.5, color=TINTA)
ax.set_xticks(idx); ax.set_xticklabels(["carrito", "catálogo", "login", "checkout", "búsqueda", "detalle"])
ax.set_ylabel("P50 (ms)")
ax.legend(frameon=False, loc="upper left")
ax.set_title("Escenario de carga: P50 por transacción según entorno", loc="left", fontsize=10.5)
guardar(fig, "ev-linux-vs-windows.png")

print(json.dumps(h, ensure_ascii=False, indent=1)[:3500])
