#!/usr/bin/env python3
"""
quality-gate.py  —  EL GATE de la Unidad 3 (determinista)

Se dispara como hook PreToolUse en Write|Edit. Solo le importa un archivo:
verification.json. Cuando el agente intenta escribir/editar ese archivo, este
gate lo intercepta, lee la EVIDENCIA y comprueba los TRES PILARES con números,
no con opiniones:

    1. PRUEBAS    -> passed == total  Y  coverage >= QUALITY_MIN_COVERAGE (def. 80)
    2. SEGURIDAD  -> critical == 0    Y  secrets == 0
    3. CRITERIOS  -> cada criterio con status == "cumple"

Si los tres pasan  -> exit 0  (APROBADO, se permite la escritura).
Si alguno falla    -> exit 2  (BLOQUEADO; el motivo por pilar va a stderr y Claude
                               lo recibe, lo reporta, y el trabajo vuelve al equipo).

Pensado para correr de DOS formas:
  - Como hook de Claude Code: recibe el payload del hook por stdin (JSON).
  - A mano / en clase / plan B:  python3 quality-gate.py ruta/a/verification.json
"""
import json
import os
import sys

# --- el único archivo bajo custodia ---
GATED_FILES = {"verification.json"}

# --- umbral configurable (no se "negocia" en runtime: se fija por entorno) ---
MIN_COVERAGE = float(os.environ.get("QUALITY_MIN_COVERAGE", "80"))


def leer_payload_stdin():
    """Devuelve (file_path, content_str) desde el payload del hook, o (None, None)."""
    data = sys.stdin.read() if not sys.stdin.isatty() else ""
    if not data.strip():
        return None, None
    try:
        payload = json.loads(data)
    except json.JSONDecodeError:
        return None, None
    ti = payload.get("tool_input", {}) or {}
    file_path = ti.get("file_path") or ti.get("path")
    # Write trae 'content'; Edit trae 'new_string' (usamos lo que haya)
    content = ti.get("content")
    if content is None:
        content = ti.get("new_string") or ti.get("new_str")
    return file_path, content


def cargar_verificacion():
    """
    Resuelve de dónde leer la evidencia:
      1) argumento de línea de comandos (modo manual / plan B)
      2) payload del hook por stdin (modo Claude Code)
    Devuelve (file_path, dict) o (file_path, None) si el archivo no está custodiado.
    """
    # Modo manual: ruta como argumento
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.basename(path) not in GATED_FILES:
            return path, None
        with open(path, "r", encoding="utf-8") as fh:
            return path, json.load(fh)

    # Modo hook: stdin
    file_path, content = leer_payload_stdin()
    if not file_path:
        return None, None
    if os.path.basename(file_path) not in GATED_FILES:
        return file_path, None  # no es nuestro archivo: dejar pasar

    if content is not None:
        try:
            return file_path, json.loads(content)
        except json.JSONDecodeError as exc:
            fail([f"verification.json no es JSON válido: {exc}"])
    # Edit sin contenido completo: intenta leer del disco
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as fh:
            return file_path, json.load(fh)
    return file_path, None


# ---------- los tres pilares ----------

def pilar_pruebas(ev):
    t = ev.get("tests", {})
    passed, total = t.get("passed", 0), t.get("total", 0)
    cov = float(t.get("coverage", 0))
    problemas = []
    if total == 0:
        problemas.append("no hay pruebas registradas")
    elif passed < total:
        problemas.append(f"{total - passed} de {total} pruebas fallan")
    if cov < MIN_COVERAGE:
        problemas.append(f"cobertura {cov:.1f}% < umbral {MIN_COVERAGE:.0f}%")
    return problemas


def pilar_seguridad(ev):
    s = ev.get("security", {})
    problemas = []
    crit = s.get("critical", 0)
    secrets = s.get("secrets", 0)
    if crit > 0:
        problemas.append(f"{crit} vulnerabilidad(es) crítica(s)")
    if secrets > 0:
        problemas.append(f"{secrets} secreto(s) expuesto(s) en el código")
    # 'high' se reporta pero NO bloquea (lo triage el equipo); el umbral son críticas/secretos
    return problemas


def pilar_criterios(ev):
    problemas = []
    for c in ev.get("criteria", []):
        if c.get("status") != "cumple":
            cid = c.get("id", "¿?")
            estado = c.get("status", "desconocido")
            problemas.append(f"{cid}: {estado}")
    if not ev.get("criteria"):
        problemas.append("no hay criterios de aceptación registrados")
    return problemas


# ---------- salida ----------

def fail(motivos_por_pilar):
    print("\n  ✗ GATE DE CALIDAD: BLOQUEADO\n", file=sys.stderr)
    for pilar, motivos in motivos_por_pilar:
        marca = "✗" if motivos else "✓"
        if motivos:
            print(f"  {marca} {pilar}: " + "; ".join(motivos), file=sys.stderr)
        else:
            print(f"  {marca} {pilar}: OK", file=sys.stderr)
    print("\n  → El código no cumple la Definition of Done. No se aprueba.", file=sys.stderr)
    print("  → Corrige lo señalado y vuelve a ejecutar `quality verify`.\n", file=sys.stderr)
    sys.exit(2)


def main():
    file_path, ev = cargar_verificacion()
    if ev is None:
        # No es verification.json (o no hay nada que verificar): no es asunto del gate.
        sys.exit(0)

    pruebas = pilar_pruebas(ev)
    seguridad = pilar_seguridad(ev)
    criterios = pilar_criterios(ev)

    resumen = [
        ("PRUEBAS", pruebas),
        ("SEGURIDAD", seguridad),
        ("CRITERIOS", criterios),
    ]

    if pruebas or seguridad or criterios:
        fail(resumen)

    # Todo en verde
    t = ev.get("tests", {})
    print("\n  ✓ GATE DE CALIDAD: APROBADO", file=sys.stderr)
    print(f"  ✓ PRUEBAS: {t.get('passed')}/{t.get('total')} · "
          f"cobertura {float(t.get('coverage',0)):.1f}% ≥ {MIN_COVERAGE:.0f}%", file=sys.stderr)
    print("  ✓ SEGURIDAD: 0 críticas · 0 secretos", file=sys.stderr)
    print(f"  ✓ CRITERIOS: {len(ev.get('criteria', []))} criterios cumplen\n", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
