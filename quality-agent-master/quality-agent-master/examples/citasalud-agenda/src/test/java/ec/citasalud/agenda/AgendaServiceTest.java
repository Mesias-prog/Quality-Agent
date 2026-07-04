package ec.citasalud.agenda;

import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.*;

class AgendaServiceTest {

    private final AgendaService agenda = new AgendaService();
    private static final LocalDateTime FRANJA = LocalDateTime.of(2026, 7, 1, 9, 0);

    @Test
    void reservaFranjaLibre_ok() {
        Reserva r = agenda.reservar("prof-1", FRANJA, "pac-1");
        assertEquals("prof-1", r.profesionalId());
        assertEquals(FRANJA, r.franja());
        assertEquals(1, agenda.listar().size());
    }

    @Test
    void reservaFranjaOcupada_secuencial_rechaza() {
        agenda.reservar("prof-1", FRANJA, "pac-1");
        assertThrows(FranjaOcupadaException.class,
                () -> agenda.reservar("prof-1", FRANJA, "pac-2"));
        assertEquals(1, agenda.listar().size());
    }

    @Test
    void reservaOtraFranja_ok() {
        agenda.reservar("prof-1", FRANJA, "pac-1");
        Reserva otra = agenda.reservar("prof-1", FRANJA.plusHours(1), "pac-2");
        assertNotNull(otra);
        assertEquals(2, agenda.listar().size());
    }

    @Test
    void reservaFranjaOcupada_concurrente_rechaza() throws InterruptedException {
        // Configuramos dos hilos que intentarán reservar la misma franja al mismo tiempo
        int threads = 2;
        ExecutorService service = Executors.newFixedThreadPool(threads);
        CountDownLatch latch = new CountDownLatch(1); // El "disparador" para sincronizar inicio
        AtomicInteger successCount = new AtomicInteger(0);
        AtomicInteger failureCount = new AtomicInteger(0);

        Runnable task = () -> {
            try {
                latch.await(); // Todos los hilos esperan aquí hasta que se libere el latch
                agenda.reservar("prof-1", FRANJA, "pac-1");
                successCount.incrementAndGet();
            } catch (FranjaOcupadaException e) {
                failureCount.incrementAndGet();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        };

        service.submit(task);
        service.submit(task);

        latch.countDown(); // ¡Fuego! Ambos hilos intentan reservar a la vez
        service.shutdown();
        service.awaitTermination(5, TimeUnit.SECONDS);

        // Verificamos que, a pesar de la concurrencia, solo uno logró reservar
        assertEquals(1, successCount.get(), "Solo una reserva debió ser exitosa");
        assertEquals(1, failureCount.get(), "La segunda reserva debió ser rechazada por concurrencia");
        assertEquals(1, agenda.listar().size(), "La agenda final solo debe tener una reserva");
    }
}