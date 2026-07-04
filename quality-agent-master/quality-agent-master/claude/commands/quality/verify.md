---
description: Verifica el código de un proyecto Spring Boot ya escrito contra los tres pilares (pruebas, seguridad, criterios) y genera quality-output/verification.json. Los criterios salen del spec.md de Spec Kit. El gate decide pasa/bloquea.
argument-hint: <ruta-del-proyecto>  (la raíz del proyecto Spring Boot, ej. ../citasalud-agenda)
---

# /quality:verify

Verifica el proyecto ubicado en **$ARGUMENTS**.

`$ARGUMENTS` es la **raíz del proyecto Spring Boot** que pasa el usuario: ahí están
`build.gradle`, `settings.gradle`, `src/` y los specs de **Spec Kit** en `specs/`.
**No hay carpeta `code/` ni `acceptance.json`**: los criterios viven en los `spec.md`.
Los resultados se generan en `$ARGUMENTS/quality-output/`.

Eres el orquestador. Usa el subagente `auditor` (y, dentro de él, `security-reviewer`).

## Pasos

1. **Carga los criterios desde el spec** — lee `$ARGUMENTS/specs/**/spec.md` (Spec Kit).
   La lista de criterios a verificar son los **Functional Requirements** (`FR-xxx`), los
   **Acceptance Scenarios** (Given/When/Then) y los **Edge Cases** de cada spec.
   Si hay `$ARGUMENTS/.specify/memory/constitution.md`, respeta sus umbrales (p. ej. cobertura).
   Lee también `.claude/skills/quality/SKILL.md` (Definition of Done y formato de salida).
2. **Pruebas** — sitúate en la raíz del proyecto y ejecuta:
   ```bash
   cd "$ARGUMENTS" && ./gradlew test jacocoTestReport
   ```
   Extrae `passed`, `total` y la cobertura desde
   `$ARGUMENTS/build/reports/jacoco/test/jacocoTestReport.xml`.
3. **Seguridad** — delega en `security-reviewer` (usa el **Semgrep MCP**) sobre
   `$ARGUMENTS/src/main/java`. Recoge `critical`, `high`, `secrets` y hallazgos con archivo:línea.
4. **Criterios** — para CADA `FR-xxx` (y cada edge case relevante) del spec, busca la
   prueba que lo cubre (Grep sobre `$ARGUMENTS/src/test`). Casos de error y concurrencia:
   con lupa. Sin prueba que lo demuestre → `incumple`. Referencia el `FR-xxx` en la evidencia.
5. Escribe el resultado en `$ARGUMENTS/quality-output/verification.json` con el esquema del SKILL
   (incluye `"spec"` apuntando al `spec.md` usado; crea `quality-output/` si no existe).
   **Al guardar, el gate se dispara.**
   - exit 0 → **APROBADO**: informa el resumen verde.
   - exit 2 → **BLOQUEADO**: informa el motivo por pilar y **qué** corregir; el trabajo
     vuelve al equipo. No reintentes editando números: arregla el código, las pruebas o el spec.

> Esto es la fase **verify** de Spec-Driven Development: confirmar que la implementación
> cumple el `spec.md`. Tú reúnes la evidencia honesta; el **gate** dicta el veredicto.
