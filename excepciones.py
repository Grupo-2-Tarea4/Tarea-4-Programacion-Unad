"""
excepciones.py
Excepciones personalizadas para el sistema Software FJ.
"""


class SoftwareFJError(Exception):
    """Excepción base del sistema Software FJ."""
    def __init__(self, mensaje: str, codigo: str = "ERR_GENERAL"):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo

    def __str__(self):
        return f"[{self.codigo}] {self.mensaje}"


# ── Cliente ──────────────────────────────────────────────────────────────────

class ClienteError(SoftwareFJError):
    """Error relacionado con la entidad Cliente."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_CLIENTE")


class ClienteYaExisteError(ClienteError):
    def __init__(self, identificacion: str):
        super().__init__(f"El cliente con identificación '{identificacion}' ya está registrado.")


class ClienteNoEncontradoError(ClienteError):
    def __init__(self, identificacion: str):
        super().__init__(f"No se encontró ningún cliente con identificación '{identificacion}'.")


class DatoClienteInvalidoError(ClienteError):
    def __init__(self, campo: str, valor):
        super().__init__(f"Valor inválido para el campo '{campo}': '{valor}'.")


# ── Servicio ──────────────────────────────────────────────────────────────────

class ServicioError(SoftwareFJError):
    """Error relacionado con la entidad Servicio."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_SERVICIO")


class ServicioNoDisponibleError(ServicioError):
    def __init__(self, nombre_servicio: str):
        super().__init__(f"El servicio '{nombre_servicio}' no está disponible en este momento.")


class ServicioNoEncontradoError(ServicioError):
    def __init__(self, id_servicio: str):
        super().__init__(f"No se encontró el servicio con ID '{id_servicio}'.")


class ParametroServicioInvalidoError(ServicioError):
    def __init__(self, parametro: str, detalle: str = ""):
        msg = f"Parámetro de servicio inválido: '{parametro}'."
        if detalle:
            msg += f" {detalle}"
        super().__init__(msg)


class CalculoCostoError(ServicioError):
    def __init__(self, detalle: str):
        super().__init__(f"Error al calcular el costo del servicio: {detalle}")


# ── Reserva ───────────────────────────────────────────────────────────────────

class ReservaError(SoftwareFJError):
    """Error relacionado con la entidad Reserva."""
    def __init__(self, mensaje: str):
        super().__init__(mensaje, "ERR_RESERVA")


class ReservaNoEncontradaError(ReservaError):
    def __init__(self, id_reserva: str):
        super().__init__(f"No se encontró la reserva con ID '{id_reserva}'.")


class ReservaYaCanceladaError(ReservaError):
    def __init__(self, id_reserva: str):
        super().__init__(f"La reserva '{id_reserva}' ya fue cancelada anteriormente.")


class ReservaYaConfirmadaError(ReservaError):
    def __init__(self, id_reserva: str):
        super().__init__(f"La reserva '{id_reserva}' ya se encuentra confirmada.")


class DuracionInvalidaError(ReservaError):
    def __init__(self, duracion):
        super().__init__(f"La duración '{duracion}' no es válida. Debe ser un número positivo.")


class EstadoReservaInvalidoError(ReservaError):
    def __init__(self, estado: str):
        super().__init__(f"El estado de reserva '{estado}' no es reconocido.")
