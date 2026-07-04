# Feature Specification: Agenda de citas con bloqueo de franja

**Feature Branch**: `001-agenda-citas`
**Created**: 2026-06-20
**Status**: Implemented
**Input**: "Los pacientes reservan citas en línea con un profesional. Una franja
horaria no puede reservarse dos veces para el mismo profesional."

## User Scenarios & Testing

### User Story 1 — Reservar una cita en línea (Priority: P1)

Como paciente, quiero reservar una franja libre con un profesional y recibir
confirmación, para asegurar mi atención.

**Acceptance Scenarios**:

1. **Given** una franja libre del profesional, **When** el paciente la reserva,
   **Then** la reserva se crea y se confirma.
2. **Given** un profesional con varias franjas, **When** el paciente reserva una
   distinta de otra ya tomada, **Then** ambas reservas coexisten.

### User Story 2 — Bloqueo de franja: sin doble reserva (Priority: P1)

Como sistema, debo impedir que una misma franja de un profesional se reserve dos
veces, para no generar choques de agenda.

**Acceptance Scenarios**:

1. **Given** una franja ya reservada, **When** otro paciente intenta reservar esa
   misma franja (de forma secuencial), **Then** la solicitud se rechaza.
2. **Given** una franja libre, **When** **dos** solicitudes para esa misma franja
   llegan **al mismo tiempo**, **Then** solo **una** prospera y la otra se rechaza.

### Edge Cases

- ¿Qué pasa cuando dos pacientes solicitan la **misma** franja en el **mismo
  instante** (concurrencia)? El sistema debe aceptar exactamente una. *(cubierto por
  FR-006)*
- ¿Qué pasa si se reserva una franja en el pasado? (fuera de alcance de esta versión)

## Requirements

### Functional Requirements

- **FR-001**: El sistema MUST permitir reservar una franja libre y devolver una
  confirmación con profesional, franja y paciente.
- **FR-002**: El sistema MUST permitir múltiples reservas en franjas distintas del
  mismo profesional.
- **FR-003**: El sistema MUST rechazar una segunda reserva (secuencial) sobre una
  franja ya ocupada del mismo profesional.
- **FR-004**: El sistema MUST exponer la creación y el listado de reservas vía API REST.
- **FR-005**: El sistema MUST responder con un código de conflicto cuando la franja
  esté ocupada.
- **FR-006**: El sistema MUST garantizar que, ante **solicitudes concurrentes** sobre
  la misma franja, **solo una** prospere (sin doble reserva por condición de carrera).

### Key Entities

- **Reserva**: profesional, franja horaria, paciente.

## Success Criteria

### Measurable Outcomes

- **SC-001**: La cobertura de pruebas del módulo de agenda es ≥ 80%.
- **SC-002**: No existen vulnerabilidades críticas ni secretos en el código.
- **SC-003**: Cada Functional Requirement tiene al menos una prueba que lo verifica,
  incluidos los casos de error y de concurrencia.

## Review & Acceptance Checklist

- [x] Las user stories tienen acceptance scenarios en Given/When/Then.
- [x] Los functional requirements son verificables.
- [x] Los edge cases (incluida la concurrencia) están declarados.
- [ ] Cada FR está cubierto por una prueba.  ← lo verifica el Quality Agent
