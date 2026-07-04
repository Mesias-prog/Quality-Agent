package ec.citasalud.agenda;

import java.time.LocalDateTime;

/** Se lanza cuando se intenta reservar una franja que ya está ocupada. */
public class FranjaOcupadaException extends RuntimeException {
    public FranjaOcupadaException(String profesionalId, LocalDateTime franja) {
        super("La franja " + franja + " del profesional " + profesionalId + " ya está ocupada");
    }
}
