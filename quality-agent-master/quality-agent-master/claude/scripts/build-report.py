#!/usr/bin/env python3
"""
build-report.py  —  Reporte HTML de calidad (paleta Unidad 3: rojo + dorado).

Lee un verification.json y produce report.html al lado. Aplica EXACTAMENTE la misma
regla que el gate (quality-gate.py), para que el reporte y el gate nunca se contradigan.

Uso:  python3 build-report.py <ruta/a/verification.json>
"""
import json
import os
import sys

MIN_COVERAGE = float(os.environ.get("QUALITY_MIN_COVERAGE", "80"))

OK, BAD = "#2E7D52", "#B3402F"          # verde "pasa" / rojo "falla" (semánticos)
INK, PAPER = "#0E1A26", "#F3F4F1"
BRAND, GOLD = "#9E1B2E", "#C99A3A"      # rojo de marca / dorado (U3)


def evaluar(ev):
    t = ev.get("tests", {})
    passed, total, cov = t.get("passed", 0), t.get("total", 0), float(t.get("coverage", 0))
    pruebas_ok = total > 0 and passed == total and cov >= MIN_COVERAGE
    s = ev.get("security", {})
    seg_ok = s.get("critical", 0) == 0 and s.get("secrets", 0) == 0
    crit = ev.get("criteria", [])
    crit_ok = bool(crit) and all(c.get("status") == "cumple" for c in crit)
    return pruebas_ok, seg_ok, crit_ok


def chip(ok):
    color = OK if ok else BAD
    label = "PASA" if ok else "FALLA"
    return (f'<span style="background:{color};color:#fff;padding:3px 12px;'
            f'border-radius:999px;font:700 13px/1 IBM Plex Mono,monospace">{label}</span>')


def main():
    if len(sys.argv) < 2:
        print("uso: build-report.py <verification.json>", file=sys.stderr)
        sys.exit(1)
    path = sys.argv[1]
    with open(path, encoding="utf-8") as fh:
        ev = json.load(fh)

    pruebas_ok, seg_ok, crit_ok = evaluar(ev)
    aprobado = pruebas_ok and seg_ok and crit_ok
    veredicto = "APROBADO" if aprobado else "BLOQUEADO"
    vcolor = OK if aprobado else BAD

    t = ev.get("tests", {})
    s = ev.get("security", {})
    filas_crit = "".join(
        f'<tr><td style="font-family:IBM Plex Mono,monospace">{c.get("id","")}</td>'
        f'<td>{chip(c.get("status")=="cumple")}</td>'
        f'<td>{c.get("evidencia","")}</td></tr>'
        for c in ev.get("criteria", [])
    )
    filas_seg = "".join(
        f'<tr><td>{h.get("severidad","")}</td>'
        f'<td style="font-family:IBM Plex Mono,monospace">{h.get("archivo","")}:{h.get("linea","")}</td>'
        f'<td>{h.get("nota","")}</td></tr>'
        for h in s.get("hallazgos", [])
    ) or '<tr><td colspan="3" style="color:#5a6b78">Sin hallazgos.</td></tr>'

    html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<title>Reporte de calidad · {ev.get('proyecto','')}</title>
<style>
 body{{margin:0;background:{PAPER};color:{INK};font:16px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;padding:40px}}
 .wrap{{max-width:880px;margin:0 auto}}
 h1{{font-size:30px;margin:0 0 4px;letter-spacing:-.02em}}
 .eyebrow{{font:700 12px/1 IBM Plex Mono,monospace;color:{BRAND};letter-spacing:.12em;text-transform:uppercase}}
 .verdict{{display:inline-block;background:{vcolor};color:#fff;font:800 20px/1 IBM Plex Mono,monospace;padding:12px 22px;border-radius:10px;margin:14px 0 28px}}
 .pillars{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:28px}}
 .card{{border:1px solid #d7dad5;border-radius:12px;padding:16px;background:#fbfcfa}}
 .card h3{{margin:0 0 8px;font-size:15px;letter-spacing:.04em;text-transform:uppercase;color:#46535f}}
 .big{{font-size:22px;font-weight:800;margin-top:6px}}
 table{{width:100%;border-collapse:collapse;margin:10px 0 26px;font-size:14px}}
 th{{text-align:left;font:700 11px/1 IBM Plex Mono,monospace;letter-spacing:.08em;text-transform:uppercase;color:#46535f;border-bottom:2px solid {BRAND};padding:8px 10px}}
 td{{padding:9px 10px;border-bottom:1px solid #e6e8e4;vertical-align:top}}
 h2{{font-size:13px;letter-spacing:.1em;text-transform:uppercase;color:{GOLD==GOLD and '#8F6A1C'};margin:24px 0 6px}}
 .meta{{color:#5a6b78;font:13px/1.5 IBM Plex Mono,monospace}}
</style></head><body><div class="wrap">
 <div class="eyebrow">Quality &amp; Governance Agent · Unidad 3</div>
 <h1>Reporte de calidad — {ev.get('proyecto','')} <span class="meta">v{ev.get('version','')}</span></h1>
 <div class="meta">commit {ev.get('commit','—')} · {ev.get('fecha','')} · umbral cobertura {MIN_COVERAGE:.0f}%</div>
 <div class="verdict">{veredicto}</div>
 <div class="pillars">
   <div class="card"><h3>Pruebas {chip(pruebas_ok)}</h3>
     <div class="big">{t.get('passed','?')}/{t.get('total','?')}</div>
     <div class="meta">cobertura {float(t.get('coverage',0)):.1f}%</div></div>
   <div class="card"><h3>Seguridad {chip(seg_ok)}</h3>
     <div class="big">{s.get('critical',0)} críticas</div>
     <div class="meta">{s.get('high',0)} high · {s.get('secrets',0)} secretos</div></div>
   <div class="card"><h3>Criterios {chip(crit_ok)}</h3>
     <div class="big">{sum(1 for c in ev.get('criteria',[]) if c.get('status')=='cumple')}/{len(ev.get('criteria',[]))}</div>
     <div class="meta">criterios que cumplen</div></div>
 </div>
 <h2>Criterios de aceptación</h2>
 <table><thead><tr><th>Criterio</th><th>Estado</th><th>Evidencia</th></tr></thead><tbody>{filas_crit}</tbody></table>
 <h2>Hallazgos de seguridad (Semgrep MCP)</h2>
 <table><thead><tr><th>Severidad</th><th>Ubicación</th><th>Nota</th></tr></thead><tbody>{filas_seg}</tbody></table>
 <div class="meta">Generado por build-report.py · misma regla del gate · "el gate manda, no el modelo".</div>
</div></body></html>"""

    out = os.path.join(os.path.dirname(path), "report.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"Reporte escrito: {out}  ·  veredicto: {veredicto}")


if __name__ == "__main__":
    main()
