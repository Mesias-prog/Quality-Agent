package ec.citasalud.agenda;

import java.time.LocalDateTime;

/** Una reserva de cita para un profesional en una franja horaria. */
public record Reserva(String profesionalId, LocalDateTime franja, String pacienteId) {
}
