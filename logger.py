"""
logger.py
Módulo de registro de eventos y errores para Software FJ.
Escribe en logs/logs.txt con marca de tiempo y nivel de severidad.
"""

import os
import traceback
from datetime import datetime

# Ruta del archivo de logs (relativa al directorio del proyecto)
_LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
_LOG_FILE = os.path.join(_LOGS_DIR, "logs.txt")

# Niveles disponibles
INFO = "INFO"
WARNING = "WARNING"
ERROR = "ERROR"
CRITICAL = "CRITICAL"


def _asegurar_directorio():
    """Crea el directorio de logs si no existe."""
    os.makedirs(_LOGS_DIR, exist_ok=True)


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def registrar(nivel: str, mensaje: str, excepcion: Exception = None) -> None:
    """
    Escribe una entrada en el archivo de logs.

    Args:
        nivel:     Nivel de severidad (INFO, WARNING, ERROR, CRITICAL).
        mensaje:   Descripción del evento o error.
        excepcion: Objeto excepción opcional; se añade el traceback completo.
    """
    _asegurar_directorio()
    lineas = [f"[{_timestamp()}] [{nivel}] {mensaje}"]
    if excepcion is not None:
        tb = traceback.format_exc()
        if tb and tb.strip() != "NoneType: None":
            lineas.append(tb.rstrip())
    lineas.append("")          # línea en blanco separadora
    entrada = "\n".join(lineas) + "\n"

    try:
        with open(_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entrada)
        # También imprime en consola para visibilidad inmediata
        print(f"  [{nivel}] {mensaje}")
    except OSError as e:
        # Último recurso: no podemos fallar en el logger
        print(f"  [LOGGER_FAIL] No se pudo escribir en logs.txt: {e}")


# Atajos por nivel
def info(mensaje: str) -> None:
    registrar(INFO, mensaje)


def warning(mensaje: str, excepcion: Exception = None) -> None:
    registrar(WARNING, mensaje, excepcion)


def error(mensaje: str, excepcion: Exception = None) -> None:
    registrar(ERROR, mensaje, excepcion)


def critical(mensaje: str, excepcion: Exception = None) -> None:
    registrar(CRITICAL, mensaje, excepcion)
