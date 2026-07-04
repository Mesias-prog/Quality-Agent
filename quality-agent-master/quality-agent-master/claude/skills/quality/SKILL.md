---
name: quality
description: El estándar de calidad del proyecto — Definition of Done, umbrales, y los formatos de spec.md (Spec Kit) y verification.json. Cárgalo antes de verificar.
---

# Skill · Estándar de calidad

Este skill define **qué cuenta como "bien"** en este proyecto Spring Boot. El auditor
lo carga antes de verificar. Aquí viven los umbrales y los formatos de archivo.

## Definition of Done (DoD)

Un trabajo está terminado cuando, sobre el **código ya escrito**:

- **Pruebas:** todas pasan y la **cobertura ≥ 80%** (`QUALITY_MIN_COVERAGE`).
- **Seguridad:** **0** vulnerabilidades **críticas** y **0** secretos en el código.
  (Las `high` se reportan y se triagean; no bloquean por sí solas.)
- **Criterios:** **todos** los Functional Requirements del `spec.md` están
  `cumple`, incluidos los **casos de error** (rechazos, validaciones, concurrencia).

> El gate (`.claude/hooks/quality-gate.py`) comprueba estos tres umbrales de forma
> determinista. Cambiar el umbral se hace por entorno, no "negociando" en runtime.

## Cómo se mide cada pilar (Spring Boot + Gradle)

- **Pruebas:** `./gradlew test jacocoTestReport`. La cobertura sale del XML de JaCoCo:
  `build/reports/jacoco/test/jacocoTestReport.xml`. No se estima: se lee.
- **Seguridad:** **Semgrep MCP** (`semgrep_scan`, `security_check`) sobre `src/main/java`,
  más un grep de secretos en `src/main` y la config. Ver `.mcp.json` y el README.
- **Criterios:** se cruza cada **Functional Requirement** (`FR-xxx`) y cada **Edge Case**
  del `spec.md` (Spec Kit) con la prueba que lo cubre (por el nombre del test).
  Sin prueba que lo demuestre → `incumple`.

## Formato de entrada — `<proyecto>/specs/<feature>/spec.md`  (Spec Kit)

Los criterios **no** se escriben a mano en un JSON: se leen del `spec.md` que ya genera
**Spec Kit** (`/speckit.specify`). El auditor extrae de cada spec:

- **Functional Requirements** — `- **FR-001**: El sistema MUST …` (los IDs `FR-xxx` son
  la unidad verificable y trazable).
- **Acceptance Scenarios** — los Given/When/Then de cada User Story.
- **Edge Cases** — casos límite y de error declarados (p. ej. concurrencia).

Si existe `<proyecto>/.specify/memory/constitution.md`, sus principios fijan umbrales
(p. ej. cobertura ≥ 80%, "cada FR una prueba") que el gate hace cumplir.

> Esto cierra el bucle de SDD: el `spec.md` es la fuente de verdad; el Quality Agent es
> la fase **verify** que confirma que el código cumple lo especificado.

Ejemplo (extracto de `spec.md`):

```markdown
### Functional Requirements
- **FR-003**: El sistema MUST rechazar una segunda reserva (secuencial) sobre una franja ocupada.
- **FR-006**: El sistema MUST garantizar que, ante solicitudes concurrentes sobre la misma
  franja, solo una prospere (sin doble reserva por condición de carrera).
```

## Formato de salida — `<proyecto>/quality-output/verification.json`  (ARCHIVO CUSTODIADO)

Lo escribe el auditor. **Al guardarlo, el gate decide pasa/bloquea.** Es la evidencia,
no la opinión: cada dato cita su fuente.

```json
{
  "proyecto": "citasalud-agenda",
  "version": "1.1.0",
  "fecha": "2026-06-27",
  "commit": "a1b2c3d",
  "tests":    { "comando": "./gradlew test jacocoTestReport",
                "passed": 130, "total": 130, "coverage": 86.0,
                "coverage_fuente": "build/reports/jacoco/test/jacocoTestReport.xml" },
  "security": { "fuente": "Semgrep MCP (semgrep_scan) + grep de secretos",
                "critical": 0, "high": 0, "secrets": 0, "hallazgos": [] },
  "spec": "specs/001-agenda-citas/spec.md",
  "criteria": [
    { "id": "FR-006", "fuente": "spec.md · FR-006 (concurrencia)", "status": "cumple",
      "evidencia": "prueba reservaFranjaOcupada_concurrente_rechaza PASA" }
  ]
}
```

- `tests.passed/total/coverage` → pilar **Pruebas**.
- `security.critical/secrets` → pilar **Seguridad** (`high` informativo).
- `criteria[].id` referencia el **`FR-xxx`** del `spec.md`; `criteria[].status` ∈
  { `cumple`, `incumple`, `desconocido` } → pilar **Criterios**.
  Solo `cumple` pasa. `desconocido` nunca se asume como `cumple`.

## El reporte

`python3 .claude/scripts/build-report.py <proyecto>/quality-output/verification.json` genera `report.html`
con la paleta de la Unidad 3, aplicando la **misma** regla del gate.
