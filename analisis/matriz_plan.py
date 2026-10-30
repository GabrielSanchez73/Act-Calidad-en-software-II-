#!/usr/bin/env python3
"""Matriz impacto / esfuerzo del plan de mejora → evidencias/figuras/matriz-impacto-esfuerzo.png"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
plt.rcParams["font.family"] = "DejaVu Sans"
# (id, nombre corto, impacto 1-10, esfuerzo en días-persona, ola)
ACC = [("A-02", "Política de sobrecarga", 8.6, 1.0, 1), ("A-01", "Eliminar N+1 en detalle", 9.6, 2.0, 1),
       ("A-03", "Índice + caché de búsqueda", 8.9, 1.5, 1), ("A-04", "Test de presupuesto de consultas", 8.0, 1.0, 1),
       ("A-05", "Gate k6 de ruta crítica", 8.3, 3.0, 2), ("A-06", "Dimensionar pool (Little)", 5.6, 0.5, 2),
       ("A-07", "Línea base reproducible", 5.9, 2.5, 2), ("A-08", "Alertas burn rate", 5.2, 2.5, 3),
       ("A-09", "Métrica de espera de conexión", 6.2, 1.0, 2)]
COL = {1: "#c4471b", 2: "#2a78d6", 3: "#52514e"}
fig, ax = plt.subplots(figsize=(9.5, 5.6))
ax.axvline(2.25, color="#8a8984", lw=1); ax.axhline(7, color="#8a8984", lw=1)
ax.set_xlim(0, 3.5); ax.set_ylim(4, 10.4)
for x, y, t in [(0.08, 10.2, "QUICK WINS — se hacen primero"), (2.33, 10.2, "PROYECTOS — se planifican"),
                (0.08, 4.15, "MEJORAS MENORES"), (2.33, 4.15, "SE DIFIEREN")]:
    ax.text(x, y, t, fontsize=9, color="#52514e", weight="bold", va="top" if y > 7 else "bottom")
off = {"A-02": (-8, 0), "A-01": (8, 4), "A-03": (8, 6), "A-04": (8, -10), "A-05": (-8, 8), "A-06": (8, -4),
       "A-07": (8, 6), "A-08": (8, -10), "A-09": (8, 4)}
for i, n, imp, esf, ola in ACC:
    ax.scatter(esf, imp, s=110, color=COL[ola], edgecolor="white", linewidth=1.5, zorder=3)
    dx, dy = off[i]
    ax.annotate(f"{i} {n}", (esf, imp), xytext=(dx, dy), textcoords="offset points", fontsize=8.6,
                ha="left" if dx > 0 else "right", va="center", color="#0b0b0b")
for ola, t in [(1, "Ola 1 (P1, 6–13 nov)"), (2, "Ola 2 (P2, 20 nov)"), (3, "Ola 3 (25 nov)")]:
    ax.scatter([], [], s=80, color=COL[ola], label=t)
ax.legend(frameon=False, loc="center right", fontsize=8.6)
ax.set_xlabel("Esfuerzo estimado (días-persona) · bajo ≤ 2 días"); ax.set_ylabel("Impacto estimado sobre los SLO (1–10)")
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.grid(color="#e4e3df", lw=0.8); ax.set_axisbelow(True)
ax.set_title("Matriz impacto / esfuerzo del plan de mejora", loc="left", fontsize=11)
fig.savefig(os.path.join(RAIZ, "evidencias", "figuras", "matriz-impacto-esfuerzo.png"), dpi=150, bbox_inches="tight", facecolor="white")
print("ok")
