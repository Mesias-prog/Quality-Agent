package ec.citasalud.agenda;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/api/reservas")
public class ReservaController {

    private final AgendaService agenda;

    public ReservaController(AgendaService agenda) {
        this.agenda = agenda;
    }

    @PostMapping
    public ResponseEntity<Reserva> crear(@RequestBody CrearReservaRequest req) {
        Reserva r = agenda.reservar(req.profesionalId(), req.franja(), req.pacienteId());
        return ResponseEntity.status(HttpStatus.CREATED).body(r);
    }

    @GetMapping
    public List<Reserva> listar() {
        return agenda.listar();
    }

    @ExceptionHandler(FranjaOcupadaException.class)
    public ResponseEntity<String> manejarOcupada(FranjaOcupadaException ex) {
        return ResponseEntity.status(HttpStatus.CONFLICT).body(ex.getMessage());
    }

    public record CrearReservaRequest(String profesionalId, LocalDateTime franja, String pacienteId) {
    }
}
