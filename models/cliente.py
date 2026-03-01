# models/cliente.py
"""
Clase base abstracta para todos los tipos de clientes del sistema Gestion Integral Clientes.
Aplica encapsulación mediante properties y validaciones en setters.
"""
import re
from datetime import datetime


class Cliente:
    """
    Clase base que representa un cliente genérico en el sistema GIC.
    
    Attributes:
        _id_cliente (int): Identificador único del cliente.
        _nombre (str): Nombre completo del cliente.
        _email (str): Correo electrónico validado.
        _telefono (str): Número de teléfono validado.
        _direccion (str): Dirección del cliente.
        _fecha_registro (str): Fecha y hora de registro automática.
        _activo (bool): Estado del cliente (activo/inactivo).
    """

    _contador_id = 1  # Contador global para IDs automáticos

    def __init__(self, id_cliente: int, nombre: str, email: str,
                 telefono: str, direccion: str):
        self._id_cliente = id_cliente
        self.nombre = nombre        # Usa el setter con validación
        self.email = email          # Usa el setter con validación
        self.telefono = telefono    # Usa el setter con validación
        self._direccion = direccion
        self._fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._activo = True

    # ──────────────────────────────────────────────
    # GETTERS Y SETTERS (Encapsulación)
    # ──────────────────────────────────────────────

    @property
    def id_cliente(self) -> int:
        return self._id_cliente

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or len(valor.strip()) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres.")
        self._nombre = valor.strip().title()

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, valor: str):
        patron = r'^[\w\.\-]+@[\w\.\-]+\.\w{2,}$'
        if not re.match(patron, valor):
            raise ValueError(f"Email inválido: '{valor}'")
        self._email = valor.lower().strip()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str):
        patron = r'^\+?[\d\s\-]{7,15}$'
        if not re.match(patron, str(valor)):
            raise ValueError(f"Teléfono inválido: '{valor}'")
        self._telefono = valor

    @property
    def direccion(self) -> str:
        return self._direccion

    @direccion.setter
    def direccion(self, valor: str):
        self._direccion = valor

    @property
    def fecha_registro(self) -> str:
        return self._fecha_registro

    @property
    def activo(self) -> bool:
        return self._activo

    @activo.setter
    def activo(self, valor: bool):
        self._activo = valor

    # ──────────────────────────────────────────────
    # MÉTODOS ESPECIALES
    # ──────────────────────────────────────────────

    def __str__(self) -> str:
        estado = "✓ Activo" if self._activo else "✗ Inactivo"
        return (f"[{self.__class__.__name__}] "
                f"ID: {self._id_cliente} | "
                f"Nombre: {self._nombre} | "
                f"Email: {self._email} | "
                f"Estado: {estado}")

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}("
                f"id={self._id_cliente}, "
                f"nombre='{self._nombre}', "
                f"email='{self._email}')")

    def __eq__(self, otro) -> bool:
        if not isinstance(otro, Cliente):
            return False
        return self._id_cliente == otro._id_cliente

    def __hash__(self) -> int:
        return hash(self._id_cliente)

    # ──────────────────────────────────────────────
    # MÉTODOS POLIMÓRFICOS (se sobreescriben en subclases)
    # ──────────────────────────────────────────────

    def obtener_descuento(self) -> float:
        """Retorna el porcentaje de descuento aplicable al cliente."""
        return 0.0

    def obtener_tipo(self) -> str:
        """Retorna el tipo de cliente como string."""
        return self.__class__.__name__

    def mostrar_info(self) -> str:
        """Retorna información detallada del cliente."""
        return (f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"  Tipo       : {self.obtener_tipo()}\n"
                f"  ID         : {self._id_cliente}\n"
                f"  Nombre     : {self._nombre}\n"
                f"  Email      : {self._email}\n"
                f"  Teléfono   : {self._telefono}\n"
                f"  Dirección  : {self._direccion}\n"
                f"  Descuento  : {self.obtener_descuento() * 100:.0f}%\n"
                f"  Registrado : {self._fecha_registro}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    def to_dict(self) -> dict:
        """Serializa el objeto a diccionario para persistencia."""
        return {
            "id": self._id_cliente,
            "tipo": self.__class__.__name__,
            "nombre": self._nombre,
            "email": self._email,
            "telefono": self._telefono,
            "direccion": self._direccion,
            "fecha_registro": self._fecha_registro,
            "activo": self._activo
        }
