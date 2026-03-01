# utils/validaciones.py
"""
Excepciones personalizadas y funciones de validación para el sistema GIC.
"""
import re


# ──────────────────────────────────────────────────────────────
# EXCEPCIONES PERSONALIZADAS
# ──────────────────────────────────────────────────────────────

class GICError(Exception):
    """Excepción base del sistema GIC."""
    def __init__(self, mensaje: str, codigo: int = 0):
        super().__init__(mensaje)
        self.codigo = codigo
        self.mensaje = mensaje

    def __str__(self):
        return f"[Error {self.codigo}] {self.mensaje}"


class ClienteNoEncontradoError(GICError):
    """Se lanza cuando no se encuentra un cliente en el sistema."""
    def __init__(self, id_cliente):
        super().__init__(f"No se encontró ningún cliente con ID '{id_cliente}'.", codigo=404)


class EmailDuplicadoError(GICError):
    """Se lanza cuando se intenta registrar un email ya existente."""
    def __init__(self, email: str):
        super().__init__(f"El email '{email}' ya está registrado en el sistema.", codigo=409)


class DatosInvalidosError(GICError):
    """Se lanza cuando los datos ingresados no pasan la validación."""
    def __init__(self, campo: str, detalle: str):
        super().__init__(f"Dato inválido en '{campo}': {detalle}", codigo=400)


class BaseDatosError(GICError):
    """Se lanza cuando ocurre un error en la conexión o consulta a la base de datos."""
    def __init__(self, detalle: str):
        super().__init__(f"Error en base de datos: {detalle}", codigo=500)


class OperacionNoPermitidaError(GICError):
    """Se lanza cuando se intenta una operación no permitida."""
    def __init__(self, operacion: str):
        super().__init__(f"Operación no permitida: '{operacion}'", codigo=403)


# ──────────────────────────────────────────────────────────────
# FUNCIONES DE VALIDACIÓN
# ──────────────────────────────────────────────────────────────

def validar_email(email: str) -> bool:
    """Valida formato de email con expresión regular."""
    patron = r'^[\w\.\-\+]+@[\w\.\-]+\.\w{2,}$'
    return bool(re.match(patron, email))


def validar_telefono(telefono: str) -> bool:
    """Valida que el teléfono tenga entre 7 y 15 dígitos (con espacios, guiones o +)."""
    patron = r'^\+?[\d\s\-]{7,15}$'
    return bool(re.match(patron, str(telefono)))


def validar_nombre(nombre: str) -> bool:
    """Valida que el nombre tenga al menos 2 caracteres no numéricos."""
    return bool(nombre and len(nombre.strip()) >= 2 and not nombre.strip().isdigit())


def validar_rut(rut: str) -> bool:
    """Validación básica de formato RUT chileno (xxxxxxxx-x)."""
    patron = r'^\d{7,8}-[\dkK]$'
    return bool(re.match(patron, rut.replace(".", "")))
