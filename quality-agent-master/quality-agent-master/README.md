# Quality & Governance Agent — Unidad 3

Tercer agente del curso *Ingeniería de Software* (Maestría en Software, UPS).
Verifica **código Spring Boot ya escrito** contra tres pilares y **bloquea** lo que no
cumple. Mismo ADN que el **Discovery Agent** (U1) y el **Agile Delivery Team** (U2):
constitución, skill, comandos, subagentes y un **hook que bloquea**.

```
Discovery (U1)  →  Delivery Team (U2)  →  Quality Agent (U3)  →  paquete listo
   descubre            planifica            verifica el código       ↑
                                            ✗ no cumple → vuelve al equipo
```

## Los tres pilares

| Pilar | Pasa si… | Cómo se mide |
|------|----------|--------------|
| **Pruebas** | todas pasan **y** cobertura ≥ 80% | `./gradlew test jacocoTestReport` + JaCoCo XML |
| **Seguridad** | 0 críticas **y** 0 secretos | **Semgrep MCP** + grep de secretos |
| **Criterios** | cada `FR-xxx` del spec cubierto | cruce `spec.md` (Spec Kit) ↔ pruebas |

El veredicto lo decide el **gate determinista** `.claude/hooks/quality-gate.py`, no el modelo.

## Estructura

```
quality-governance-agent/
├── CLAUDE.md                     # constitución (tres pilares, "el gate manda")
├── .mcp.json                     # conexión MCP (Semgrep) — ver abajo
├── .claude/
│   ├── settings.json             # hook PreToolUse → quality-gate.py
│   ├── agents/                   # auditor + security-reviewer
│   ├── commands/quality/         # verify (núcleo) · review-api · review-architecture · generate-report
│   ├── hooks/quality-gate.py     # EL GATE (determinista)
│   ├── scripts/build-report.py   # reporte HTML (paleta U3)
│   └── skills/quality/SKILL.md   # Definition of Done, umbrales, formatos
└── examples/
    └── citasalud-agenda/         # PROYECTO Spring Boot de ejemplo (con un hueco deliberado)
        ├── build.gradle          # dependency management Gradle
        ├── settings.gradle
        ├── specs/001-agenda-citas/spec.md   # Spec Kit: FRs, escenarios, edge cases (CRITERIOS)
        ├── .specify/memory/constitution.md  # Spec Kit: umbrales (cobertura ≥ 80%)
        ├── src/main/java/...     # el código a verificar
        ├── src/test/java/...     # las pruebas
        └── quality-output/       # lo que GENERA el agente (verification.json + report.html)
```

> **Entrada = la ruta del proyecto.** El usuario pasa la **raíz** de un proyecto Spring Boot
> (donde están `build.gradle`, `src/` y los specs de **Spec Kit** en `specs/`).
> **No hay carpeta `code/` ni `acceptance.json`**: los criterios se leen del `spec.md`.
> El agente genera sus resultados dentro del proyecto, en `quality-output/`.

## De dónde salen los criterios (Spec Kit, no `acceptance.json`)

De los tres pilares, dos se derivan del proyecto: **Pruebas** (Gradle + JaCoCo) y
**Seguridad** (Semgrep). El tercero, **Criterios**, necesita saber *qué se prometió* —
y eso no está en el código. Su valor real es cazar la **omisión silenciosa**: un requisito
que **no tiene ninguna prueba** aunque todo lo demás esté en verde (cobertura no lo ve —
mide líneas ejecutadas, no requisitos cubiertos).

Como el proyecto usa **Spec Kit**, esa fuente de verdad ya existe: el `spec.md` que genera
`/speckit.specify`. El agente lee los **Functional Requirements** (`FR-xxx`), los
**Acceptance Scenarios** y los **Edge Cases** de `specs/<feature>/spec.md`, y verifica
que cada uno tenga una prueba. Esto cierra el bucle de SDD: el Quality Agent es la fase
**verify** que confirma que el código cumple el spec. (Por eso ya **no** hay `acceptance.json`.)

## Para qué se usa el MCP (Semgrep)

El **pilar de Seguridad** se apoya en un servidor **MCP real y oficial de Semgrep**
(`semgrep-mcp`). El agente lo usa para **escanear el código Java/Spring y reunir las
vulnerabilidades** (`semgrep_scan`, `security_check`), que luego pueblan el bloque
`security` de `verification.json`.

> **El MCP reúne la evidencia; el gate decide sobre ella.** El veredicto pasa/bloquea
> NO depende de un servicio externo ni de un modelo: el gate local y determinista mira
> los números (`critical`, `secrets`) y dicta. El MCP son los *sentidos* del agente;
> el gate es el *juez*.

Configuración (en `.mcp.json`, project-scoped y versionable):

```json
{ "mcpServers": {
    "semgrep": { "command": "uvx", "args": ["semgrep-mcp"],
                 "env": { "SEMGREP_APP_TOKEN": "${SEMGREP_APP_TOKEN}" } } } }
```

- Requiere `uv`/`uvx` (o Docker: `ghcr.io/semgrep/mcp -t stdio`).
- `SEMGREP_APP_TOKEN` es **opcional** — sin token, Semgrep escanea con sus reglas
  locales; con token, se conecta a la plataforma AppSec. Expórtalo en tu shell:
  `export SEMGREP_APP_TOKEN=...` (no lo escribas en el archivo).
- Claude Code te pedirá **aprobar** el servidor del `.mcp.json` la primera vez.

## Cómo se usa con Claude Code

```bash
cd quality-governance-agent
claude                                       # aprueba el MCP de Semgrep al inicio

# se pasa la RUTA DEL PROYECTO (la raíz del proyecto Spring Boot):
/quality:verify examples/citasalud-agenda    # o la ruta de TU proyecto
/quality:generate-report examples/citasalud-agenda
```

Cuando el agente escribe `<proyecto>/quality-output/verification.json`, el **gate** se dispara:
- **APROBADO** (exit 0) si los tres pilares pasan.
- **BLOQUEADO** (exit 2) si alguno falla, con el motivo por pilar; el trabajo vuelve al equipo.

## Probar el gate SIN Claude (plan B para clase)

El gate es un script normal de Python; puedes ejecutarlo a mano:

```bash
# El ejemplo trae un hueco deliberado → debe BLOQUEAR (exit 2)
python3 .claude/hooks/quality-gate.py examples/citasalud-agenda/quality-output/verification.json
echo "exit: $?"

# Genera el reporte HTML del veredicto
python3 .claude/scripts/build-report.py examples/citasalud-agenda/quality-output/verification.json
```

El umbral de cobertura se ajusta por entorno:
`QUALITY_MIN_COVERAGE=70 python3 .claude/hooks/quality-gate.py ...`

## El ejemplo (citasalud)

El spec (`specs/001-agenda-citas/spec.md`) declara **FR-006**: ante solicitudes
**concurrentes** sobre la misma franja, solo una debe prosperar. Pero
`AgendaService.reservar()` tiene una **carrera** deliberada: comprueba si la franja está
ocupada y luego inserta, sin atomicidad. Las pruebas cubren el camino feliz y el rechazo
**secuencial**, pero **no** el **concurrente** — así que **FR-006 no tiene prueba**.
Resultado del gate:

```
✗ PRUEBAS:   2 de 130 fallan; cobertura 79.0% < 80%
✓ SEGURIDAD: 0 críticas · 0 secretos   (1 'high' reportado para triage)
✗ CRITERIOS: FR-006: incumple
→ BLOQUEADO
```

Para verlo pasar: sube la cobertura, agrega `reservaFranjaOcupada_concurrente_rechaza`,
corrige `reservar()` (p. ej. `synchronized` o un lock) y actualiza `verification.json`.
