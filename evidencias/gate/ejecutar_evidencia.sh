#!/usr/bin/env bash
# Ejecuta el evaluador de quality gates sobre las corridas reales de la Actividad 3
# y guarda reporte + código de salida de cada caso (evidencia de la sección 4).
#   bash evidencias/gate/ejecutar_evidencia.sh
set -u
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
G="$RAIZ/evidencias/gate"
EV="python3 -I $RAIZ/pipeline/gates/evaluar_gate.py --umbrales $RAIZ/pipeline/gates/umbrales.json"
rm -rf "$G/resultados" "$G/lineas-base" "$G/lineas-base-solo-linux" "$G"/caso-*.md "$G/registro.txt"
python3 -I "$RAIZ/pipeline/gates/desde_datos_a3.py" "$RAIZ/datos-a4" "$G/resultados"
mkdir -p "$G/lineas-base-vacia"

caso () {  # nombre, resultado, carpeta de líneas base, [extra]
  local nombre="$1" res="$2" lb="$3"; shift 3
  echo "== $nombre ==" | tee -a "$G/registro.txt"
  $EV --resultado "$G/resultados/$res" --lineas-base "$lb" --reporte "$G/$nombre.md" "$@" >/dev/null
  local rc=$?
  echo "código de salida: $rc" | tee -a "$G/registro.txt"
  echo "código de salida del evaluador: \`$rc\`" >> "$G/$nombre.md"
}

# 1. La corrida de ruta crítica de la A3 frente a los gates de rendimiento
caso caso-1-ruta-critica resultado-ruta_critica.json "$G/lineas-base-vacia"
# 2. La corrida base de carga (Linux) — cumple los SLO; se guarda como línea base de su huella
caso caso-2-carga-linux resultado-carga.json "$G/lineas-base-solo-linux" --guardar-linea-base
# 3. Repetición en Windows comparada con la base Linux: el gate se niega a comparar (D-04)
caso caso-3-windows-vs-base-linux resultado-carga-r2.json "$G/lineas-base-solo-linux"
# 4. Se registra r1 como base de la huella Windows y se comparan r2 y r3 contra ella
cp -r "$G/lineas-base-solo-linux" "$G/lineas-base"
$EV --resultado "$G/resultados/resultado-carga-r1.json" --lineas-base "$G/lineas-base" --guardar-linea-base >/dev/null
caso caso-4-r2-vs-base-windows resultado-carga-r2.json "$G/lineas-base"
caso caso-5-r3-vs-base-windows resultado-carga-r3.json "$G/lineas-base"
rmdir "$G/lineas-base-vacia"
