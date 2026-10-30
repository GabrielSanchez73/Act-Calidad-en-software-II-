#!/usr/bin/env python3
"""Matriz impacto × urgencia del triage → evidencias/figuras/matriz-impacto-urgencia.png"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
plt.rcParams["font.family"] = "DejaVu Sans"
# prioridad resultante por celda (fila = impacto, columna = urgencia)
PRIO = {("Alto", "Alta"): "P1", ("Alto", "Media"): "P2", ("Alto", "Baja"): "P3",
        ("Medio", "Alta"): "P1", ("Medio", "Media"): "P2", ("Medio", "Baja"): "P3",
        ("Bajo", "Alta"): "P2", ("Bajo", "Media"): "P3", ("Bajo", "Baja"): "P4"}
FONDO = {"P1": "#f6d5c8", "P2": "#dbe7f8", "P3": "#ecebe7", "P4": "#f7f7f5"}
DEF = {("Alto", "Alta"): ["EG1-RND-001 (D-01)", "EG1-DIS-002 (D-02)"], ("Alto", "Media"): ["EG1-CAP-003 (D-03)"],
       ("Medio", "Media"): ["EG1-MED-004 (D-04)", "EG1-RND-005 (D-05)"]}
imp, urg = ["Alto", "Medio", "Bajo"], ["Baja", "Media", "Alta"]
fig, ax = plt.subplots(figsize=(9.5, 5.6))
for i, im in enumerate(imp):
    for j, ur in enumerate(urg):
        y = 2 - i
        p = PRIO[(im, ur)]
        ax.add_patch(Rectangle((j, y), 1, 1, fc=FONDO[p], ec="white", lw=3))
        ax.text(j + 0.06, y + 0.9, p, fontsize=10, weight="bold", color="#52514e", va="top")
        for k, d in enumerate(DEF.get((im, ur), [])):
            ax.text(j + 0.5, y + 0.55 - k * 0.22, d, ha="center", va="center", fontsize=9.2, color="#0b0b0b",
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#8a8984", lw=0.8))
ax.set_xlim(0, 3); ax.set_ylim(0, 3)
ax.set_xticks([0.5, 1.5, 2.5]); ax.set_xticklabels(["Baja\n(después de la campaña)", "Media\n(antes del 20-nov)", "Alta\n(antes del 13-nov)"])
ax.set_yticks([0.5, 1.5, 2.5]); ax.set_yticklabels(["Bajo\n(S4)", "Medio\n(S3)", "Alto\n(S1–S2)"])
ax.set_xlabel("Urgencia frente al Black Friday del 27-nov-2026 (escenario supuesto)")
ax.set_ylabel("Impacto (severidad)")
for s in ax.spines.values(): s.set_visible(False)
ax.tick_params(length=0)
ax.set_title("Matriz impacto × urgencia: prioridades registradas en el triage", loc="left", fontsize=11)
fig.savefig(os.path.join(RAIZ, "evidencias", "figuras", "matriz-impacto-urgencia.png"), dpi=150, bbox_inches="tight", facecolor="white")
print("ok")
