#!/usr/bin/env python3
"""
Evaluador de quality gates de rendimiento (QG-05 … QG-09).

k6 ya hace fallar el pipeline cuando un threshold se incumple (código 99). Este
evaluador añade lo que k6 no puede hacer solo:
  - QG-09: comparar contra la línea base del MISMO entorno (huella), y negarse a
    comparar huellas distintas en vez de producir un falso positivo (D-04);
  - un reporte legible por regla, con el defecto que cada regla previene, para
    el resumen del job y el comentario del PR (trazabilidad).

Uso:
  python3 evaluar_gate.py --resultado resultados/resultado-ruta_critica.json \
      [--lineas-base gates/lineas-base] [--reporte reporte.md] [--guardar-linea-base]

Código de salida: 0 si no falla ninguna regla bloqueante; 1 si falla alguna.
"""
import argparse, hashlib, json, os, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
OK, FALLA, NA, AVISO = "PASA", "FALLA", "N/A", "AVISO"


def huella_id(huella: str) -> str:
    return hashlib.sha256(huella.encode()).hexdigest()[:12]


def evaluar(res, umb, base):
    reglas = {r["id"]: r for r in umb["reglas"]}
    slo = umb["slo"]
    out = []

    def add(id_, estado, medido, umbral, detalle=""):
        r = reglas[id_]
        out.append({"id": id_, "regla": r["regla"], "estado": estado, "medido": medido,
                    "umbral": umbral, "defectos": r["defectos"], "bloqueante": r["bloqueante"],
                    "detalle": detalle})

    # QG-05 tasa de error
    e = res.get("error_pct")
    add("QG-05", NA if e is None else (OK if e < slo["error_pct_max"] else FALLA),
        None if e is None else f"{e:.3f} %", f"< {slo['error_pct_max']} %")

    # QG-06 percentiles por transacción
    for t, m in sorted(res.get("transacciones", {}).items()):
        for p in ("p95", "p99"):
            v, lim = m.get(f"{p}_ms"), slo[f"{p}_ms"].get(t)
            if v is None or lim is None:
                continue
            add("QG-06", OK if v < lim else FALLA, f"{t} {p.upper()} {v:,.1f} ms",
                f"< {lim} ms", f"{v / lim:.1f}× el SLO" if v >= lim else f"margen {100 * (1 - v / lim):.1f} %")

    # QG-07 saturación del pool
    q = reglas["QG-07"]["umbral"]
    cola, r503 = res.get("db_cola_max"), res.get("rechazos_503")
    if cola is not None:
        add("QG-07", OK if cola <= q["cola_max"] else FALLA, f"cola máx {cola:g}",
            f"<= {q['cola_max']} (2 × pool)", f"{cola / res.get('pool', 4):.0f}× el tamaño del pool" if cola > q["cola_max"] else "")
    if r503 is not None:
        add("QG-07", OK if r503 <= q["rechazos_503"] else FALLA, f"{r503:g} rechazos 503", f"<= {q['rechazos_503']}")
    if cola is None and r503 is None:
        add("QG-07", NA, None, f"<= {q['cola_max']}", "la corrida no trae métricas del servicio (/metricas)")

    # QG-08 capacidad sostenida
    obj, thr = res.get("carga_objetivo_req_s"), res.get("throughput_meseta_req_s")
    if obj and thr is not None:
        frac = reglas["QG-08"]["umbral"]
        add("QG-08", OK if thr >= frac * obj else FALLA, f"{thr:.1f} req/s",
            f">= {frac * obj:.1f} req/s ({int(frac * 100)} % de {obj})",
            f"{100 * thr / obj:.0f} % del objetivo")
    else:
        add("QG-08", NA, None, "-", "el escenario no define carga objetivo")

    # QG-09 regresión frente a línea base del mismo entorno
    u9 = reglas["QG-09"]["umbral"]
    if base is None:
        add("QG-09", AVISO, None, "-", "sin línea base para esta huella y escenario: se registra como candidata")
    elif base.get("huella") != res.get("huella"):
        add("QG-09", AVISO, None, "-",
            f"NO COMPARABLE: huella {huella_id(res.get('huella', ''))} ≠ base {huella_id(base.get('huella', ''))}")
    else:
        for t, m in sorted(res.get("transacciones", {}).items()):
            b = base.get("transacciones", {}).get(t, {}).get("p95_ms")
            v = m.get("p95_ms")
            if b and v is not None:
                inc = 100 * (v / b - 1)
                add("QG-09", OK if inc <= u9["p95_max_incremento_pct"] else FALLA,
                    f"{t} P95 {v:.1f} ms vs base {b:.1f} ms", f"<= +{u9['p95_max_incremento_pct']} %", f"{inc:+.1f} %")
        bt, vt = base.get("throughput_req_s"), res.get("throughput_req_s")
        if bt and vt is not None:
            caida = 100 * (1 - vt / bt)
            add("QG-09", OK if caida <= u9["throughput_max_caida_pct"] else FALLA,
                f"throughput {vt:.2f} vs base {bt:.2f} req/s", f"caída <= {u9['throughput_max_caida_pct']} %", f"{-caida:+.1f} %")
    return out


def reporte_md(res, evals):
    fallas = [e for e in evals if e["estado"] == FALLA and e["bloqueante"]]
    veredicto = "❌ GATE FALLA — el cambio no puede fusionarse" if fallas else "✅ GATE PASA"
    l = [f"### Quality gate de rendimiento — escenario `{res.get('escenario')}`", "",
         f"**{veredicto}** ({len(fallas)} condición(es) bloqueante(s) incumplida(s))", "",
         f"Huella del entorno: `{huella_id(res.get('huella', ''))}` · origen: {res.get('origen', '-')}"
         + (f" · commit `{res['commit'][:7]}`" if res.get("commit") else ""), "",
         "| Regla | Estado | Medido | Umbral | Detalle | Previene |", "|---|---|---|---|---|---|"]
    for e in evals:
        l.append(f"| {e['id']} | {e['estado']} | {e['medido'] or '-'} | {e['umbral']} | {e['detalle']} | {', '.join(e['defectos'])} |")
    return "\n".join(l) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--resultado", required=True)
    ap.add_argument("--umbrales", default=os.path.join(AQUI, "umbrales.json"))
    ap.add_argument("--lineas-base", default=os.path.join(AQUI, "lineas-base"))
    ap.add_argument("--reporte")
    ap.add_argument("--guardar-linea-base", action="store_true",
                    help="guarda este resultado como línea base de su huella (solo en main, tras pasar el gate)")
    a = ap.parse_args()

    res = json.load(open(a.resultado, encoding="utf-8"))
    umb = json.load(open(a.umbrales, encoding="utf-8"))
    ruta_base = os.path.join(a.lineas_base, f"{res['escenario']}-{huella_id(res.get('huella', ''))}.json")
    base = json.load(open(ruta_base, encoding="utf-8")) if os.path.exists(ruta_base) else None
    if base is None:  # ¿hay base del escenario con otra huella? se informa como no comparable
        otras = [f for f in os.listdir(a.lineas_base) if f.startswith(res["escenario"] + "-")] if os.path.isdir(a.lineas_base) else []
        if otras:
            base = json.load(open(os.path.join(a.lineas_base, sorted(otras)[0]), encoding="utf-8"))

    evals = evaluar(res, umb, base)
    md = reporte_md(res, evals)
    print(md)
    if a.reporte:
        with open(a.reporte, "w", encoding="utf-8") as f:
            f.write(md)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write(md)
    fallo = any(e["estado"] == FALLA and e["bloqueante"] for e in evals)
    if a.guardar_linea_base and not fallo:
        os.makedirs(a.lineas_base, exist_ok=True)
        with open(ruta_base, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
        print(f"Línea base actualizada: {ruta_base}")
    sys.exit(1 if fallo else 0)


if __name__ == "__main__":
    main()
