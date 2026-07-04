---
description: Genera el reporte HTML de calidad a partir de quality-output/verification.json (paleta de la Unidad 3).
argument-hint: <ruta-del-proyecto>
---

# /quality:generate-report

Genera un reporte HTML legible a partir del veredicto ya producido para el proyecto en **$ARGUMENTS**.

Pasos:
1. Confirma que existe `$ARGUMENTS/quality-output/verification.json`.
2. Ejecuta el generador determinista (aplica la MISMA regla del gate):
   ```bash
   python3 .claude/scripts/build-report.py "$ARGUMENTS/quality-output/verification.json"
   ```
3. El reporte se escribe junto al JSON como `quality-output/report.html`. Informa la ruta y el veredicto.

> El reporte no recalcula la verdad a su manera: usa la misma lógica del gate, para que
> el HTML y el gate **nunca** se contradigan.
