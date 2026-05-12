"""
    ServicioNoDisponibleError,
    ReservaYaCanceladaError,
    ReservaYaConfirmadaError,
    ReservaError,
)


# ── Helpers de presentación ───────────────────────────────────────────────────

def seccion(titulo: str) -> None:
    separador = "=" * 60
    print(f"\n{separador}")
    print(f"  {titulo}")
    print(separador)


def ok(msg: str) -> None:
    print(f"  ✔  {msg}")


def fallo(msg: str) -> None:
    print(f"  ✘  {msg}")


# ── Gestores globales ─────────────────────────────────────────────────────────

gestorC = GestorClientes()
gestorS = GestorServicios()
gestorR = GestorReservas()


# ══════════════════════════════════════════════════════════════════════════════
# BLOQUE 1 – Registro de clientes
# ══════════════════════════════════════════════════════════════════════════════

def demo_clientes():
    seccion("BLOQUE 1 – Registro de clientes")

    # Operación 1 – Cliente válido
    try:
        c1 = Cliente("1001", "Ana Torres", "ana@correo.com", "3001234567")
        gestorC.registrar(c1)
        ok(f"Cliente registrado: {c1.descripcion()}")
    except SoftwareFJError as e:
        fallo(f"Error inesperado: {e}")

    # Operación 2 – Otro cliente válido
    try:
        c2 = Cliente("1002", "Luis Pérez", "luis@empresa.co", "6017654321")
        gestorC.registrar(c2)
        ok(f"Cliente registrado: {c2.descripcion()}")
    except SoftwareFJError as e:
        fallo(f"Error inesperado: {e}")

    # Operación 3 – Email inválido (excepción esperada)
    try:
        c_bad = Cliente("1003", "Pedro Mal", "correo-sin-arroba", "3109876543")
        gestorC.registrar(c_bad)
    except DatoClienteInvalidoError as e:
        fallo(f"[ESPERADO] {e}")

    # Operación 4 – Nombre demasiado corto (excepción esperada)
    try:
        c_bad2 = Cliente("1004", "Al", "al@ok.com", "3211111111")
        gestorC.registrar(c_bad2)
    except DatoClienteInvalidoError as e:
        fallo(f"[ESPERADO] {e}")

    # Operación 5 – Registro duplicado (excepción esperada)
    try:
        c_dup = Cliente("1001", "Ana Duplicada", "otra@correo.com", "3009999999")
        gestorC.registrar(c_dup)
    except ClienteYaExisteError as e:
        fallo(f"[ESPERADO] {e}")

    print(f"\n  Clientes registrados exitosamente: {gestorC.total()}")


# ══════════════════════════════════════════════════════════════════════════════
# BLOQUE 2 – Creación de servicios
# ══════════════════════════════════════════════════════════════════════════════

def demo_servicios():
    seccion("BLOQUE 2 – Creación de servicios")

    # Operación 6 – Sala válida
    try:
        sala = ReservaSala("S01", "Sala Innovación", capacidad=20,
                           precio_hora=60_000)
        gestorS.agregar(sala)
        ok(f"Servicio agregado: {sala.describir()}")
    except SoftwareFJError as e:
        fallo(f"Error inesperado: {e}")

    # Operación 7 – Equipo válido
    try:
        equipo = AlquilerEquipo("E01", "Portátil HP ProBook",
                                tipo_equipo="Portátil",
                                precio_dia=90_000, stock=5)
        gestorS.agregar(equipo)
        ok(f"Servicio agregado: {equipo.describir()}")
    except SoftwareFJError as e:
        fallo(f"Error inesperado: {e}")

    # Operación 8 – Asesoría válida
    try:
        asesoria = AsesoriaEspecializada("A01", "Consultoría Legal Empresarial",
                                          especialidad="legal",
                                          tarifa_hora=150_000)
        gestorS.agregar(asesoria)
        ok(f"Servicio agregado: {asesoria.describir()}")
    except SoftwareFJError as e:
        fallo(f"Error inesperado: {e}")

    # Operación 9 – Capacidad de sala inválida (excepción esperada)
    try:
        sala_bad = ReservaSala("S02", "Sala Rota", capacidad=-5)
        gestorS.agregar(sala_bad)
    except ParametroServicioInvalidoError as e:
        fallo(f"[ESPERADO] {e}")

    # Operación 10 – Especialidad inexistente (excepción esperada)
    try:
        asesoria_bad = AsesoriaEspecializada("A02", "Asesoría Mágica",
                                              especialidad="magia")
        gestorS.agregar(asesoria_bad)
    except ParametroServicioInvalidoError as e:
        fallo(f"[ESPERADO] {e}")

    print(f"\n  Servicios registrados exitosamente: {gestorS.total()}")


# ══════════════════════════════════════════════════════════════════════════════
# BLOQUE 3 – Reservas
# ══════════════════════════════════════════════════════════════════════════════

def demo_reservas():
    seccion("BLOQUE 3 – Reservas (creación, confirmación, cancelación)")

    try:
        c1 = gestorC.buscar("1001")
        c2 = gestorC.buscar("1002")
        sala   = gestorS.buscar("S01")
        equipo = gestorS.buscar("E01")
        asesoria = gestorS.buscar("A01")
    except SoftwareFJError as e:
        logger.critical("No se pudieron obtener entidades base para reservas.", e)
        fallo(f"Error crítico: {e}")
        return

    # Operación 11 – Reserva válida de sala → confirmar → procesar
    try:
        r1 = Reserva(c1, sala, duracion=3, descuento=10, aplicar_iva=True)
        gestorR.agregar(r1)
        costo = r1.confirmar()
        ok(f"Reserva confirmada | Costo: ${costo:,.2f}")
        msg = r1.procesar()
        ok(msg)
    except SoftwareFJError as e:
        fallo(f"Error en reserva sala: {e}")

    # Operación 12 – Reserva válida de equipo → confirmar → cancelar
    try:
        r2 = Reserva(c2, equipo, duracion=2, descuento=0, aplicar_iva=True)
        gestorR.agregar(r2)
        r2.confirmar()
        ok(f"Reserva de equipo confirmada: {r2.id_reserva}")
        r2.cancelar()
        ok(f"Reserva cancelada: {r2.id_reserva}")
    except SoftwareFJError as e:
        fallo(f"Error en reserva equipo: {e}")

    # Operación 13 – Reserva de asesoría (con encadenamiento de excepciones)
    try:
        r3 = Reserva(c1, asesoria, duracion=2.5, descuento=5, aplicar_iva=True)
        gestorR.agregar(r3)
        costo = r3.confirmar()
        ok(f"Asesoría confirmada | Costo: ${costo:,.2f}")
    except SoftwareFJError as e:
        fallo(f"Error en reserva asesoría: {e}")

    # Operación 14 – Intentar confirmar reserva ya confirmada (esperado)
    try:
        r3.confirmar()
    except ReservaYaConfirmadaError as e:
        fallo(f"[ESPERADO] {e}")

    # Operación 15 – Intentar cancelar reserva ya cancelada (esperado)
    try:
        r2.cancelar()
    except ReservaYaCanceladaError as e:
        fallo(f"[ESPERADO] {e}")

    # Operación 16 – Duración inválida (esperado)
    try:
        r_bad = Reserva(c1, sala, duracion=-1)
        gestorR.agregar(r_bad)
    except SoftwareFJError as e:
        fallo(f"[ESPERADO] {e}")

    # Operación 17 – Servicio no disponible (esperado)
    try:
        sala.disponible = False
        r_no_disp = Reserva(c1, sala, duracion=1)
        gestorR.agregar(r_no_disp)
        r_no_disp.confirmar()
    except ServicioNoDisponibleError as e:
        fallo(f"[ESPERADO] {e}")
    finally:
        sala.disponible = True   # restaurar para no afectar otras demos

    print(f"\n  Total reservas registradas: {gestorR.total()}")


# ══════════════════════════════════════════════════════════════════════════════
# BLOQUE 4 – Resumen final
# ══════════════════════════════════════════════════════════════════════════════

def resumen_final():
    seccion("RESUMEN FINAL DEL SISTEMA")

    print("\n  --- Clientes ---")
    for c in gestorC.listar():
        print(f"    {c.descripcion()}")

    print("\n  --- Servicios ---")
    for s in gestorS.listar():
        print(f"    {s.describir()}")

    print("\n  --- Reservas ---")
    for r in gestorR.listar():
        print()
        for linea in r.resumen().splitlines():
            print(f"    {linea}")

    confirmadas = gestorR.listar_por_estado(EstadoReserva.CONFIRMADA)
    procesadas  = gestorR.listar_por_estado(EstadoReserva.PROCESADA)
    canceladas  = gestorR.listar_por_estado(EstadoReserva.CANCELADA)

    print(f"\n  Confirmadas : {len(confirmadas)}")
    print(f"  Procesadas  : {len(procesadas)}")
    print(f"  Canceladas  : {len(canceladas)}")
    print("\n  Revise logs/logs.txt para el historial completo de eventos.")


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logger.info("══════════════════════════════════════════════")
    logger.info("  Sistema Software FJ — Inicio de ejecución   ")
    logger.info("══════════════════════════════════════════════")

    print("\n╔══════════════════════════════════════════╗")
    print("║   SISTEMA SOFTWARE FJ — Fase 4          ║")
    print("╚══════════════════════════════════════════╝")

    demo_clientes()
    demo_servicios()
    demo_reservas()
    resumen_final()

    logger.info("Sistema Software FJ — Ejecución completada sin interrupciones.")
    print("\n  [FIN] Sistema ejecutado sin interrupciones.")
