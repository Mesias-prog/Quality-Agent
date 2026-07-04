package ec.citasalud.agenda;

import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

@Service
public class AgendaService {

    // Seguimos usando ArrayList, pero ahora está protegido por los métodos sincronizados
    private final List<Reserva> reservas = new ArrayList<>();

    // 'synchronized' convierte este método en una operación atómica.
    // Ningún otro hilo puede ejecutar este método ni listar() mientras uno esté dentro.
    public synchronized Reserva reservar(String profesionalId, LocalDateTime franja, String pacienteId) {
        boolean ocupada = reservas.stream()
                .anyMatch(r -> r.profesionalId().equals(profesionalId)
                        && r.franja().equals(franja));
        
        if (ocupada) {
            throw new FranjaOcupadaException(profesionalId, franja);
        }
        
        // Ahora es seguro: ningún otro hilo puede insertar o modificar la lista 
        // hasta que este método termine.
        Reserva nueva = new Reserva(profesionalId, franja, pacienteId);
        reservas.add(nueva);
        return nueva;
    }

    // También debe ser 'synchronized' para garantizar que no lea 
    // mientras otro hilo está escribiendo (evita inconsistencias).
    public synchronized List<Reserva> listar() {
        return List.copyOf(reservas);
    }
}