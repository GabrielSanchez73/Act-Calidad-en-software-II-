#!/usr/bin/env python3
"""
Diagramas de Ishikawa (causa-efecto) de los defectos D-01 … D-04.

Categorías: las 6M adaptadas a software (Código ≈ método, Configuración,
Infraestructura ≈ máquina, Datos ≈ material, Medición y pruebas, Proceso y
personas ≈ mano de obra). Cada causa lleva su estado de verificación:
  ✔ verificada con evidencia de la A3/A4   ? por validar   ✖ descartada con evidencia
La causa raíz que cierra los 5 porqués se resalta en negrita y color.

  python3 analisis/ishikawa.py   → evidencias/figuras/ishikawa-D-0N.png
"""
import os, textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(RAIZ, "evidencias", "figuras")
TINTA, TINTA2, ESPINA, RAIZC = "#0b0b0b", "#52514e", "#8a8984", "#c4471b"
COLOR_ESTADO = {"V": "#0b6b4a", "I": "#2a78d6", "H": "#9a6a00", "X": "#8a8984"}
SIMBOLO = {"V": "✔", "I": "≈", "H": "?", "X": "✖"}

CATS = ["Código", "Configuración", "Infraestructura",
        "Datos", "Medición y pruebas", "Proceso y personas"]

DEFECTOS = {
    "D-01": ("P95 de detalle = 9.124,6 ms en ruta crítica\n(SLO 900 ms; 10,1 veces el objetivo)", {
        "Código": [("I", "~20 idas y vueltas estimadas (Δ131 ms ÷ 6,2 ms; no es conteo SQL)"),
                   ("H", "N+1: relaciones cargadas en bucle de consultas"),
                   ("H", "cada subconsulta re-adquiere conexión y se re-encola")],
        "Configuración": [("V", "pool de 4 conexiones"),
                          ("H", "sin timeout de adquisición; verificar configuración"),
                          ("V", "cola admitida hasta 250 peticiones")],
        "Infraestructura": [("X", "CPU: host 47,5 %, servicio 12 % → no satura"),
                            ("X", "event loop: lag P99 ≤ 11 ms → no bloquea"),
                            ("H", "MySQL comparte la VM de 1 vCPU")],
        "Datos": [("H", "productos con muchas relaciones (N crece)"),
                  ("H", "claves foráneas de tablas hijas sin índice")],
        "Medición y pruebas": [("V", "ninguna prueba previa superaba 25 sesiones/s"),
                               ("V", "no se mide el tiempo de espera por conexión")],
        "Proceso y personas": [("R", "sin control automático de consultas ni latencia por endpoint en el pipeline"),
                               ("H", "revisión de código sin checklist de acceso a datos")],
    }),
    "D-02": ("Tasa de error 1,329 % en ruta crítica\n(SLO < 1 %; 105 respuestas 503)", {
        "Código": [("V", "105 de 105 errores son 503 por pool agotado"),
                   ("H", "sin degradación (caché de detalle) en saturación")],
        "Configuración": [("V", "primer 503 observado con cola = 250"),
                          ("I", "250 ÷ 49,4 req/s ≈ 5 s (estimación de espera)"),
                          ("H", "503 sin cabecera Retry-After")],
        "Infraestructura": [("X", "caídas de proceso o red: 0 % de error en los\notros 4 escenarios"),
                            ("X", "CPU no saturada (12 % servicio)")],
        "Datos": [("H", "acceso concentrado en productos populares\nsin caché")],
        "Medición y pruebas": [("V", "SLO evaluado solo al final de la corrida"),
                               ("V", "sin alerta por consumo del presupuesto (132,9 %)")],
        "Proceso y personas": [("R", "no existe política de sobrecarga derivada del SLO (cuándo y qué rechazar)"),
                               ("V", "no se prueba el comportamiento en saturación")],
    }),
    "D-03": ("Throughput se estanca en 49,4 req/s y cae a 42,4\nmientras la concurrencia sube de 13 a 224 VU", {
        "Código": [("I", "retención ≈162 ms por sesión (estimada)"),
                   ("I", "estimación: búsqueda P50 111 ms + detalle P50 51 ms"),
                   ("H", "re-encolado de subconsultas acelera el retroceso")],
        "Configuración": [("I", "pool de 4: capacidad estimada por Ley de Little"),
                          ("H", "max_connections de MySQL sin revisar")],
        "Infraestructura": [("X", "CPU host 47,5 % en el techo → no es cómputo"),
                            ("V", "estrés llega a 73 req/s sin techo (cola ≤ 9)")],
        "Datos": [("H", "búsqueda LIKE sin índice: 111 ms constantes"),
                  ("V", "búsqueda no varía con red (+6 ms) ni carga")],
        "Medición y pruebas": [("V", "A3/A4 no reportaron la curva throughput–VU"),
                               ("V", "sin prueba de capacidad automatizada")],
        "Proceso y personas": [("R", "pool dimensionado sin modelo de capacidad ni prueba que lo verifique"),
                               ("H", "sin demanda objetivo documentada por ruta")],
    }),
    "D-04": ("Línea base no reproducible: P95 de carga\n106,6 ms (Linux) vs 201,4 ms (Windows, +89 %)", {
        "Código": [("I", "diferencias calculadas: detalle +131 ms; simples +6 ms"),
                   ("H", "N+1 multiplica la latencia de red (~21 × 6,2 ms)")],
        "Configuración": [("H", "versiones de MySQL / Node distintas"),
                          ("H", "red de Docker Desktop / WSL en Windows")],
        "Infraestructura": [("V", "base en Linux; 4 repeticiones en Windows"),
                            ("I", "CV del P95 Windows = 0,89 % (cálculo)")],
        "Datos": [("H", "volumen de datos equivalente (confirmar\nconteo de filas)")],
        "Medición y pruebas": [("V", "muestreador lee /proc: 4 corridas sin métricas"),
                               ("V", "resultado sin huella del entorno")],
        "Proceso y personas": [("R", "no hay procedimiento de línea base reproducible (entorno fijo + huella)"),
                               ("V", "repeticiones en el equipo disponible")],
    }),
    "D-05": ("Búsqueda retiene la conexión ≈111 ms por petición\n(P50 constante; 2/3 del tiempo de pool en ruta crítica)", {
        "Código": [("H", "LIKE con comodín inicial ('%término%')"),
                   ("H", "sin caché para términos repetidos")],
        "Configuración": [("X", "pool: sin cola (carga baja) igual tarda 111 ms"),
                          ("H", "sin límite de resultados (LIMIT) por consulta")],
        "Infraestructura": [("I", "diferencia estimada en consultas simples: +6 ms"),
                            ("X", "carga: P50 de 110–117 ms en los 5 escenarios")],
        "Datos": [("H", "columna de nombre/descr. sin índice FULLTEXT"),
                  ("H", "tabla crece con el catálogo → recorrido mayor")],
        "Medición y pruebas": [("I", "SLO 1.000 ms puede ocultar costo de recursos"),
                               ("V", "A3/A4 no miden espera de conexión por petición")],
        "Proceso y personas": [("R", "no se revisa el plan de ejecución (EXPLAIN) de consultas nuevas"),
                               ("V", "el SLO solo mira latencia, no costo en recursos")],
    }),
}


def dibujar(clave, efecto, causas):
    plt.rcParams["font.family"] = "DejaVu Sans"
    W, H = 19.0, 8.6
    fig, ax = plt.subplots(figsize=(15.5, 7.4))
    ax.set_xlim(0, W); ax.set_ylim(-0.7, H); ax.axis("off")
    y0, x_ini, x_fin = 3.95, 0.2, 13.4
    ax.annotate("", xy=(x_fin + 0.05, y0), xytext=(x_ini, y0),
                arrowprops=dict(arrowstyle="-|>", color=ESPINA, lw=2.4, mutation_scale=18))
    ax.text(x_fin + 0.25, y0, efecto, va="center", ha="left", fontsize=10, weight="bold",
            color=TINTA, bbox=dict(boxstyle="round,pad=0.5", fc="#fbeee8", ec=RAIZC, lw=1.2),
            wrap=True)
    xs = [4.6, 8.9, 13.2]
    for i, cat in enumerate(CATS):
        arriba = i < 3
        xb = xs[i % 3]
        ytop = 7.55 if arriba else 0.35
        xtop = xb - 1.6
        ax.plot([xtop, xb], [ytop, y0], color=ESPINA, lw=1.6)
        ax.text(xtop, ytop + (0.15 if arriba else -0.15), cat, ha="center",
                va="bottom" if arriba else "top", fontsize=10, weight="bold", color=TINTA,
                bbox=dict(boxstyle="round,pad=0.3", fc="#eef3fb", ec="#2a78d6", lw=1))
        items = causas.get(cat, [])
        n = len(items)
        for j, (estado, txt) in enumerate(items):
            frac = (j + 0.75) / (n + 0.5)
            yc = ytop + (y0 - ytop) * frac
            xc = xtop + (xb - xtop) * frac
            ax.plot([xc - 0.15, xc], [yc, yc], color=ESPINA, lw=1)
            raiz = estado == "R"
            simbolo = "★" if raiz else SIMBOLO[estado]
            color = RAIZC if raiz else COLOR_ESTADO[estado]
            base = txt.replace("\n", " ")
            lineas = "\n".join(textwrap.wrap(base, 34))
            ax.text(xc - 0.2, yc, f"{simbolo} {lineas}", ha="right", va="center",
                    fontsize=8.1, color=color if (raiz or estado in {"I", "X"}) else TINTA,
                    weight="bold" if raiz else "normal", linespacing=1.12)
    ley = [("✔ observado en evidencia", COLOR_ESTADO["V"]),
           ("≈ inferencia/cálculo derivado", COLOR_ESTADO["I"]),
           ("? hipótesis por validar", COLOR_ESTADO["H"]),
           ("✖ explicación descartada por la evidencia", COLOR_ESTADO["X"]),
           ("★ causa raíz sistémica inferida", RAIZC)]
    for x, (t, c) in zip([0.2, 3.9, 7.7, 11.1, 15.0], ley):
        ax.text(x, -0.65, t, fontsize=7.6, color=c, va="bottom", weight="bold")
    ax.text(0.2, H, f"Diagrama de Ishikawa — {clave}", fontsize=12, weight="bold", color=TINTA, va="top")
    fig.savefig(os.path.join(FIG, f"ishikawa-{clave}.png"), dpi=150, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    for k, (efecto, causas) in DEFECTOS.items():
        dibujar(k, efecto, causas)
    print("ok")
