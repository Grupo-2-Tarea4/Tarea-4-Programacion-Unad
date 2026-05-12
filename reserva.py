"""
reserva.py
Clase Reserva que integra Cliente, Servicio, duración y estado.
Implementa confirmación, cancelación y procesamiento con manejo avanzado
de excepciones (try/except, try/except/else, try/except/finally,
encadenamiento de excepciones).
"""

import uuid
from datetime import datetime
from enum import Enum

from cliente import Cliente
from servicio import Servicio
from excepciones import (
    DuracionInvalidaError,
    EstadoReservaInvalidoError,
    ReservaNoEncontradaError,
    ReservaYaCanceladaError,
    ReservaYaConfirmadaError,
    ServicioNoDisponibleError,
    CalculoCostoError,
    ReservaError,
)
import logger


# ── Estado de la reserva ──────────────────────────────────────────────────────

class EstadoReserva(str, Enum):
    PENDIENTE   = "PENDIENTE"
    CONFIRMADA  = "CONFIRMADA"
    CANCELADA   = "CANCELADA"
    PROCESADA   = "PROCESADA"


# ── Clase Reserva ─────────────────────────────────────────────────────────────

class Reserva:
    """
    Representa una reserva de un servicio por parte de un cliente.

    Attributes:
        id_reserva      : Identificador único generado automáticamente.
        cliente         : Objeto Cliente asociado.
        servicio        : Objeto Servicio asociado.
        duracion        : Duración (horas o días según el servicio).
        estado          : EstadoReserva actual.
        fecha_creacion  : Fecha/hora de creación.
        costo_total     : Costo calculado al confirmar.
    """

    def __init__(self, cliente: Cliente, servicio: Servicio,
                 duracion: float, descuento: float = 0.0,
                 aplicar_iva: bool = True):
        try:
            if not isinstance(cliente, Cliente):
                raise ReservaError("El parámetro 'cliente' debe ser una instancia de Cliente.")
            if not isinstance(servicio, Servicio):
                raise ReservaError("El parámetro 'servicio' debe ser una instancia de Servicio.")
            duracion = float(duracion)
            if duracion <= 0:
                raise DuracionInvalidaError(duracion)
            if not (0 <= descuento <= 100):
                raise ReservaError(f"Descuento fuera de rango: {descuento}%")

            self._id_reserva     = str(uuid.uuid4())[:8].upper()
            self._cliente        = cliente
            self._servicio       = servicio
            self._duracion       = duracion
            self._descuento      = descuento
            self._aplicar_iva    = aplicar_iva
            self._estado         = EstadoReserva.PENDIENTE
            self._fecha_creacion = datetime.now()
            self._costo_total    = 0.0

            logger.info(
                f"Reserva creada: {self._id_reserva} | "
                f"Cliente: {cliente.identificacion} | "
                f"Servicio: {servicio.id_servicio} | "
                f"Duración: {duracion}"
            )
        except (DuracionInvalidaError, ReservaError):
            logger.error("Error al crear reserva.")
            raise

    # ── Propiedades (solo lectura) ─────────────────────────────────────────────

    @property
    def id_reserva(self) -> str:
        return self._id_reserva

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def duracion(self) -> float:
        return self._duracion

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def fecha_creacion(self) -> datetime:
        return self._fecha_creacion

    @property
    def costo_total(self) -> float:
        return self._costo_total

    # ── Operaciones principales ───────────────────────────────────────────────

    def confirmar(self) -> float:
        """
        Confirma la reserva y calcula el costo total.

        Raises:
            ReservaYaConfirmadaError : si ya fue confirmada.
            ReservaYaCanceladaError  : si ya fue cancelada.
            ServicioNoDisponibleError: si el servicio no está disponible.
            CalculoCostoError        : si el cálculo falla.

        Returns:
            Costo total de la reserva.
        """
        try:
            if self._estado == EstadoReserva.CONFIRMADA:
                raise ReservaYaConfirmadaError(self._id_reserva)
            if self._estado == EstadoReserva.CANCELADA:
                raise ReservaYaCanceladaError(self._id_reserva)

            costo = self._servicio.calcular_costo(
                self._duracion,
                descuento=self._descuento,
                aplicar_iva=self._aplicar_iva,
            )
        except (ReservaYaConfirmadaError, ReservaYaCanceladaError,
                ServicioNoDisponibleError) as e:
            logger.error(f"No se pudo confirmar reserva {self._id_reserva}: {e}")
            raise
        except CalculoCostoError as e:
            logger.error(f"Error de costo al confirmar {self._id_reserva}: {e}")
            raise ReservaError(
                f"Fallo al calcular costo en reserva {self._id_reserva}."
            ) from e
        else:
            # Bloque else: se ejecuta solo si no hubo excepciones
            self._costo_total = costo
            self._estado = EstadoReserva.CONFIRMADA
            logger.info(
                f"Reserva CONFIRMADA: {self._id_reserva} | "
                f"Costo: ${costo:,.2f}"
            )
            return costo
        finally:
            # Bloque finally: siempre se ejecuta
            logger.info(
                f"Intento de confirmación finalizado para reserva {self._id_reserva} "
                f"| Estado actual: {self._estado.value}"
            )

    def cancelar(self) -> None:
        """
        Cancela la reserva.

        Raises:
            ReservaYaCanceladaError: si ya estaba cancelada.
        """
        try:
            if self._estado == EstadoReserva.CANCELADA:
                raise ReservaYaCanceladaError(self._id_reserva)
            self._estado = EstadoReserva.CANCELADA
        except ReservaYaCanceladaError:
            logger.warning(
                f"Intento de cancelar reserva ya cancelada: {self._id_reserva}"
            )
            raise
        else:
            logger.info(f"Reserva CANCELADA: {self._id_reserva}")
        finally:
            logger.info(
                f"Intento de cancelación finalizado para reserva {self._id_reserva}"
            )

    def procesar(self) -> str:
        """
        Procesa (ejecuta) una reserva confirmada.

        Raises:
            ReservaError: si no está en estado CONFIRMADA.

        Returns:
            Mensaje de procesamiento exitoso.
        """
        try:
            if self._estado != EstadoReserva.CONFIRMADA:
                raise ReservaError(
                    f"Solo se pueden procesar reservas CONFIRMADAS. "
                    f"Estado actual: {self._estado.value}"
                )
            self._estado = EstadoReserva.PROCESADA
        except ReservaError:
            logger.error(
                f"Error al procesar reserva {self._id_reserva}: estado inválido."
            )
            raise
        else:
            msg = (
                f"Reserva {self._id_reserva} PROCESADA exitosamente. "
                f"Servicio: {self._servicio.nombre} | "
                f"Cliente: {self._cliente.nombre} | "
                f"Costo: ${self._costo_total:,.2f}"
            )
            logger.info(msg)
            return msg
        finally:
            logger.info(
                f"Intento de procesamiento finalizado para reserva {self._id_reserva}"
            )

    # ── Representación ────────────────────────────────────────────────────────

    def resumen(self) -> str:
        return (
            f"Reserva [{self._id_reserva}]\n"
            f"  Cliente  : {self._cliente.nombre} ({self._cliente.identificacion})\n"
            f"  Servicio : {self._servicio.nombre}\n"
            f"  Duración : {self._duracion}\n"
            f"  Descuento: {self._descuento}%  |  IVA: {self._aplicar_iva}\n"
            f"  Costo    : ${self._costo_total:,.2f}\n"
            f"  Estado   : {self._estado.value}\n"
            f"  Creada   : {self._fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')}"
        )

    def __str__(self):
        return self.resumen()


# ── Repositorio de reservas ───────────────────────────────────────────────────

class GestorReservas:
    """Administra todas las reservas del sistema en memoria."""

    def __init__(self):
        self._reservas: dict[str, Reserva] = {}

    def agregar(self, reserva: Reserva) -> None:
        self._reservas[reserva.id_reserva] = reserva
        logger.info(f"Reserva registrada en gestor: {reserva.id_reserva}")

    def buscar(self, id_reserva: str) -> Reserva:
        reserva = self._reservas.get(id_reserva)
        if reserva is None:
            raise ReservaNoEncontradaError(id_reserva)
        return reserva

    def listar(self) -> list[Reserva]:
        return list(self._reservas.values())

    def listar_por_estado(self, estado: EstadoReserva) -> list[Reserva]:
        try:
            estado = EstadoReserva(estado)
        except ValueError as e:
            raise EstadoReservaInvalidoError(str(estado)) from e
        return [r for r in self._reservas.values() if r.estado == estado]

    def total(self) -> int:
        return len(self._reservas)
