"""
cliente.py
Clase abstracta EntidadSistema y clase concreta Cliente para Software FJ.
Aplica: abstracción, encapsulación, validaciones robustas.
"""

import re
from abc import ABC, abstractmethod
from excepciones import (
    DatoClienteInvalidoError,
    ClienteYaExisteError,
    ClienteNoEncontradoError,
)
import logger


# ── Clase abstracta base ──────────────────────────────────────────────────────

class EntidadSistema(ABC):
    """
    Clase abstracta que representa cualquier entidad gestionada por el sistema.
    Obliga a implementar descripcion() y validar() en todas las subclases.
    """

    @abstractmethod
    def descripcion(self) -> str:
        """Devuelve una descripción legible de la entidad."""

    @abstractmethod
    def validar(self) -> bool:
        """Valida la integridad interna de la entidad."""

    def __repr__(self):
        return self.descripcion()


# ── Clase Cliente ─────────────────────────────────────────────────────────────

class Cliente(EntidadSistema):
    """
    Representa un cliente de Software FJ.

    Atributos privados con propiedades para encapsulación:
        _identificacion : str  — Cédula / NIT único del cliente.
        _nombre         : str  — Nombre completo.
        _email          : str  — Correo electrónico válido.
        _telefono       : str  — Número telefónico (solo dígitos, 7-15 chars).
    """

    _PATRON_EMAIL = re.compile(r"^[\w.\-+]+@[\w\-]+\.[a-zA-Z]{2,}$")
    _PATRON_TELEFONO = re.compile(r"^\d{7,15}$")

    def __init__(self, identificacion: str, nombre: str,
                 email: str, telefono: str):
        # Usamos los setters para que las validaciones se ejecuten al crear
        self.identificacion = identificacion
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        logger.info(f"Cliente creado: {self._identificacion} - {self._nombre}")

    # ── Propiedades ───────────────────────────────────────────────────────────

    @property
    def identificacion(self) -> str:
        return self._identificacion

    @identificacion.setter
    def identificacion(self, valor: str):
        valor = str(valor).strip()
        if not valor:
            raise DatoClienteInvalidoError("identificacion", valor)
        self._identificacion = valor

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        valor = str(valor).strip()
        if len(valor) < 3:
            raise DatoClienteInvalidoError(
                "nombre", valor,
            )
        self._nombre = valor

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, valor: str):
        valor = str(valor).strip().lower()
        if not self._PATRON_EMAIL.match(valor):
            raise DatoClienteInvalidoError("email", valor)
        self._email = valor

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str):
        valor = str(valor).strip().replace(" ", "").replace("-", "")
        if not self._PATRON_TELEFONO.match(valor):
            raise DatoClienteInvalidoError("telefono", valor)
        self._telefono = valor

    # ── EntidadSistema ────────────────────────────────────────────────────────

    def descripcion(self) -> str:
        return (f"Cliente[{self._identificacion}] "
                f"{self._nombre} | {self._email} | Tel: {self._telefono}")

    def validar(self) -> bool:
        return bool(
            self._identificacion
            and len(self._nombre) >= 3
            and self._PATRON_EMAIL.match(self._email)
            and self._PATRON_TELEFONO.match(self._telefono)
        )

    def __eq__(self, other):
        if isinstance(other, Cliente):
            return self._identificacion == other._identificacion
        return False

    def __hash__(self):
        return hash(self._identificacion)


# ── Repositorio de clientes (en memoria) ──────────────────────────────────────

class GestorClientes:
    """
    Administra la colección de clientes registrados.
    No usa base de datos; trabaja con un dict en memoria.
    """

    def __init__(self):
        self._clientes: dict[str, Cliente] = {}

    def registrar(self, cliente: Cliente) -> None:
        """
        Registra un nuevo cliente.

        Raises:
            ClienteYaExisteError: si la identificación ya está registrada.
        """
        try:
            if cliente.identificacion in self._clientes:
                raise ClienteYaExisteError(cliente.identificacion)
            self._clientes[cliente.identificacion] = cliente
            logger.info(f"Cliente registrado exitosamente: {cliente.identificacion}")
        except ClienteYaExisteError:
            logger.error(f"Intento de registro duplicado: {cliente.identificacion}")
            raise

    def buscar(self, identificacion: str) -> Cliente:
        """
        Busca y devuelve un cliente por identificación.

        Raises:
            ClienteNoEncontradoError: si no existe.
        """
        try:
            cliente = self._clientes.get(identificacion)
            if cliente is None:
                raise ClienteNoEncontradoError(identificacion)
            return cliente
        except ClienteNoEncontradoError:
            logger.warning(f"Cliente no encontrado: {identificacion}")
            raise

    def listar(self) -> list[Cliente]:
        """Devuelve todos los clientes registrados."""
        return list(self._clientes.values())

    def eliminar(self, identificacion: str) -> None:
        """Elimina un cliente del registro."""
        self.buscar(identificacion)          # lanza error si no existe
        del self._clientes[identificacion]
        logger.info(f"Cliente eliminado: {identificacion}")

    def total(self) -> int:
        return len(self._clientes)
