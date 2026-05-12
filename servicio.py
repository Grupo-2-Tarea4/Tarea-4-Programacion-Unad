"""
servicio.py
Clase abstracta Servicio y tres servicios especializados:
  - ReservaSala
  - AlquilerEquipo
  - AsesoriaEspecializada

Aplica: herencia, polimorfismo, métodos sobrescritos y sobrecargados.
"""

from abc import abstractmethod
from cliente import EntidadSistema
from excepciones import (
    ServicioNoDisponibleError,
    ParametroServicioInvalidoError,
    CalculoCostoError,
)
import logger


# ── Clase abstracta Servicio ──────────────────────────────────────────────────

class Servicio(EntidadSistema):
    """
    Clase abstracta que modela un servicio ofrecido por Software FJ.
    Cada subclase debe implementar calcular_costo, describir y validar.
    """

    def __init__(self, id_servicio: str, nombre: str,
                 disponible: bool = True):
        if not id_servicio or not nombre:
            raise ParametroServicioInvalidoError(
                "id_servicio/nombre", "No pueden estar vacíos."
            )
        self._id_servicio = id_servicio
        self._nombre = nombre
        self._disponible = disponible

    # ── Propiedades ───────────────────────────────────────────────────────────

    @property
    def id_servicio(self) -> str:
        return self._id_servicio

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, valor: bool):
        self._disponible = bool(valor)

    # ── Métodos abstractos ────────────────────────────────────────────────────

    @abstractmethod
    def calcular_costo(self, duracion_horas: float,
                       descuento: float = 0.0,
                       aplicar_iva: bool = True) -> float:
        """
        Calcula el costo total del servicio.

        Args:
            duracion_horas: Tiempo de uso en horas.
            descuento:      Porcentaje de descuento (0–100).
            aplicar_iva:    Si True aplica IVA del 19 %.
        """

    @abstractmethod
    def describir(self) -> str:
        """Descripción detallada del servicio."""

    @abstractmethod
    def validar_parametros(self, **kwargs) -> bool:
        """Valida parámetros específicos del servicio antes de reservar."""

    # ── EntidadSistema ────────────────────────────────────────────────────────

    def descripcion(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"
        return f"Servicio[{self._id_servicio}] {self._nombre} | {estado}"

    def validar(self) -> bool:
        return bool(self._id_servicio and self._nombre)

    # ── Utilidad compartida ───────────────────────────────────────────────────

    @staticmethod
    def _aplicar_descuento_e_iva(subtotal: float,
                                  descuento: float,
                                  aplicar_iva: bool) -> float:
        """Aplica descuento (%) e IVA 19 % sobre el subtotal."""
        try:
            if not (0 <= descuento <= 100):
                raise CalculoCostoError(
                    f"Descuento fuera de rango: {descuento}%"
                )
            monto = subtotal * (1 - descuento / 100)
            if aplicar_iva:
                monto *= 1.19
            return round(monto, 2)
        except (TypeError, ValueError) as e:
            raise CalculoCostoError(str(e)) from e

    def _verificar_disponibilidad(self):
        if not self._disponible:
            raise ServicioNoDisponibleError(self._nombre)

    def __str__(self):
        return self.describir()


# ── Servicio 1: Reserva de Sala ───────────────────────────────────────────────

class ReservaSala(Servicio):
    """
    Servicio de reserva de sala de reuniones o capacitación.

    Tarifa base: precio_hora × horas_uso.
    """

    PRECIO_HORA_BASE = 50_000   # COP

    def __init__(self, id_servicio: str, nombre: str,
                 capacidad: int, precio_hora: float = PRECIO_HORA_BASE,
                 disponible: bool = True):
        super().__init__(id_servicio, nombre, disponible)
        if capacidad <= 0:
            raise ParametroServicioInvalidoError(
                "capacidad", "Debe ser un entero positivo."
            )
        if precio_hora <= 0:
            raise ParametroServicioInvalidoError(
                "precio_hora", "Debe ser un valor positivo."
            )
        self._capacidad = int(capacidad)
        self._precio_hora = float(precio_hora)

    @property
    def capacidad(self) -> int:
        return self._capacidad

    @property
    def precio_hora(self) -> float:
        return self._precio_hora

    # Método sobrescrito
    def calcular_costo(self, duracion_horas: float,
                       descuento: float = 0.0,
                       aplicar_iva: bool = True) -> float:
        self._verificar_disponibilidad()
        try:
            if duracion_horas <= 0:
                raise CalculoCostoError(
                    f"Duración inválida para ReservaSala: {duracion_horas}"
                )
            subtotal = self._precio_hora * duracion_horas
            total = self._aplicar_descuento_e_iva(subtotal, descuento, aplicar_iva)
            logger.info(
                f"Costo calculado ReservaSala '{self._nombre}': "
                f"${total:,.2f} ({duracion_horas}h, desc={descuento}%, IVA={aplicar_iva})"
            )
            return total
        except CalculoCostoError:
            logger.error(f"Error calculando costo en ReservaSala '{self._nombre}'")
            raise

    def describir(self) -> str:
        return (f"[SALA] {self._nombre} | Capacidad: {self._capacidad} personas "
                f"| Tarifa: ${self._precio_hora:,.0f}/h")

    def validar_parametros(self, **kwargs) -> bool:
        personas = kwargs.get("personas", 1)
        try:
            personas = int(personas)
            if personas < 1 or personas > self._capacidad:
                raise ParametroServicioInvalidoError(
                    "personas",
                    f"Debe estar entre 1 y {self._capacidad}."
                )
            return True
        except (TypeError, ValueError) as e:
            raise ParametroServicioInvalidoError("personas", str(e)) from e


# ── Servicio 2: Alquiler de Equipo ────────────────────────────────────────────

class AlquilerEquipo(Servicio):
    """
    Servicio de alquiler de equipos tecnológicos (portátiles, proyectores, etc.).

    Tarifa base: precio_dia × días_uso.
    """

    PRECIO_DIA_BASE = 80_000    # COP

    def __init__(self, id_servicio: str, nombre: str,
                 tipo_equipo: str, precio_dia: float = PRECIO_DIA_BASE,
                 stock: int = 1, disponible: bool = True):
        super().__init__(id_servicio, nombre, disponible)
        if not tipo_equipo:
            raise ParametroServicioInvalidoError(
                "tipo_equipo", "No puede estar vacío."
            )
        if precio_dia <= 0:
            raise ParametroServicioInvalidoError(
                "precio_dia", "Debe ser un valor positivo."
            )
        if stock < 0:
            raise ParametroServicioInvalidoError(
                "stock", "No puede ser negativo."
            )
        self._tipo_equipo = tipo_equipo
        self._precio_dia = float(precio_dia)
        self._stock = int(stock)

    @property
    def tipo_equipo(self) -> str:
        return self._tipo_equipo

    @property
    def precio_dia(self) -> float:
        return self._precio_dia

    @property
    def stock(self) -> int:
        return self._stock

    # Método sobrescrito
    def calcular_costo(self, duracion_horas: float,
                       descuento: float = 0.0,
                       aplicar_iva: bool = True) -> float:
        """duracion_horas se interpreta como número de DÍAS para este servicio."""
        self._verificar_disponibilidad()
        try:
            dias = duracion_horas          # semántica: unidad = días
            if dias <= 0:
                raise CalculoCostoError(
                    f"Número de días inválido para AlquilerEquipo: {dias}"
                )
            subtotal = self._precio_dia * dias
            total = self._aplicar_descuento_e_iva(subtotal, descuento, aplicar_iva)
            logger.info(
                f"Costo calculado AlquilerEquipo '{self._nombre}': "
                f"${total:,.2f} ({dias}d, desc={descuento}%, IVA={aplicar_iva})"
            )
            return total
        except CalculoCostoError:
            logger.error(f"Error calculando costo en AlquilerEquipo '{self._nombre}'")
            raise

    def describir(self) -> str:
        return (f"[EQUIPO] {self._nombre} | Tipo: {self._tipo_equipo} "
                f"| Tarifa: ${self._precio_dia:,.0f}/día | Stock: {self._stock}")

    def validar_parametros(self, **kwargs) -> bool:
        cantidad = kwargs.get("cantidad", 1)
        try:
            cantidad = int(cantidad)
            if cantidad < 1:
                raise ParametroServicioInvalidoError(
                    "cantidad", "Debe ser al menos 1."
                )
            if cantidad > self._stock:
                raise ParametroServicioInvalidoError(
                    "cantidad",
                    f"Stock disponible: {self._stock}, solicitado: {cantidad}."
                )
            return True
        except (TypeError, ValueError) as e:
            raise ParametroServicioInvalidoError("cantidad", str(e)) from e


# ── Servicio 3: Asesoría Especializada ───────────────────────────────────────

class AsesoriaEspecializada(Servicio):
    """
    Servicio de asesoría técnica, legal o de negocios.

    Tarifa base: tarifa_hora × horas, con posible recargo por especialidad.
    """

    TARIFA_HORA_BASE = 120_000   # COP

    ESPECIALIDADES_VALIDAS = {
        "tecnologia", "legal", "negocios", "financiero", "rrhh"
    }

    def __init__(self, id_servicio: str, nombre: str,
                 especialidad: str,
                 tarifa_hora: float = TARIFA_HORA_BASE,
                 disponible: bool = True):
        super().__init__(id_servicio, nombre, disponible)
        especialidad = especialidad.lower().strip()
        if especialidad not in self.ESPECIALIDADES_VALIDAS:
            raise ParametroServicioInvalidoError(
                "especialidad",
                f"Debe ser una de: {self.ESPECIALIDADES_VALIDAS}"
            )
        if tarifa_hora <= 0:
            raise ParametroServicioInvalidoError(
                "tarifa_hora", "Debe ser un valor positivo."
            )
        self._especialidad = especialidad
        self._tarifa_hora = float(tarifa_hora)

    @property
    def especialidad(self) -> str:
        return self._especialidad

    @property
    def tarifa_hora(self) -> float:
        return self._tarifa_hora

    # Método sobrescrito
    def calcular_costo(self, duracion_horas: float,
                       descuento: float = 0.0,
                       aplicar_iva: bool = True) -> float:
        self._verificar_disponibilidad()
        try:
            if duracion_horas <= 0:
                raise CalculoCostoError(
                    f"Duración inválida para AsesoriaEspecializada: {duracion_horas}"
                )
            # Recargo del 15 % para especialidades legal y financiero
            recargo = 1.15 if self._especialidad in ("legal", "financiero") else 1.0
            subtotal = self._tarifa_hora * duracion_horas * recargo
            total = self._aplicar_descuento_e_iva(subtotal, descuento, aplicar_iva)
            logger.info(
                f"Costo calculado Asesoria '{self._nombre}': "
                f"${total:,.2f} ({duracion_horas}h, desc={descuento}%, IVA={aplicar_iva})"
            )
            return total
        except CalculoCostoError:
            logger.error(f"Error calculando costo en Asesoria '{self._nombre}'")
            raise

    def describir(self) -> str:
        return (f"[ASESORIA] {self._nombre} | Especialidad: {self._especialidad.upper()} "
                f"| Tarifa: ${self._tarifa_hora:,.0f}/h")

    def validar_parametros(self, **kwargs) -> bool:
        horas = kwargs.get("horas", 1)
        try:
            horas = float(horas)
            if horas < 0.5:
                raise ParametroServicioInvalidoError(
                    "horas", "La asesoría mínima es de 0.5 horas."
                )
            return True
        except (TypeError, ValueError) as e:
            raise ParametroServicioInvalidoError("horas", str(e)) from e


# ── Repositorio de servicios ──────────────────────────────────────────────────

class GestorServicios:
    """Administra el catálogo de servicios en memoria."""

    def __init__(self):
        self._servicios: dict[str, Servicio] = {}

    def agregar(self, servicio: Servicio) -> None:
        try:
            if not servicio.validar():
                raise ParametroServicioInvalidoError(
                    servicio.id_servicio, "El servicio no pasó la validación interna."
                )
            self._servicios[servicio.id_servicio] = servicio
            logger.info(f"Servicio agregado: {servicio.id_servicio} - {servicio.nombre}")
        except ParametroServicioInvalidoError:
            logger.error(f"No se pudo agregar el servicio: {servicio.id_servicio}")
            raise

    def buscar(self, id_servicio: str) -> Servicio:
        from excepciones import ServicioNoEncontradoError
        servicio = self._servicios.get(id_servicio)
        if servicio is None:
            raise ServicioNoEncontradoError(id_servicio)
        return servicio

    def listar(self) -> list[Servicio]:
        return list(self._servicios.values())

    def total(self) -> int:
        return len(self._servicios)
