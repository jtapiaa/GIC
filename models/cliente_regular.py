# models/cliente_regular.py
"""
Subclase ClienteRegular: hereda de Cliente y agrega sistema de puntos.
"""
from models.cliente import Cliente


class ClienteRegular(Cliente):
    """
    Cliente estándar con sistema de acumulación de puntos.
    
    Attributes:
        _puntos (int): Puntos acumulados por compras.
    """

    DESCUENTO_BASE = 0.05  # 5%
    PUNTOS_POR_PESO = 1    # 1 punto por cada unidad monetaria

    def __init__(self, id_cliente: int, nombre: str, email: str,
                 telefono: str, direccion: str, puntos: int = 0):
        super().__init__(id_cliente, nombre, email, telefono, direccion)
        self._puntos = max(0, puntos)  # No puede ser negativo

    # ──────────────────────────────────────────────
    # GETTERS Y SETTERS
    # ──────────────────────────────────────────────

    @property
    def puntos(self) -> int:
        return self._puntos

    # ──────────────────────────────────────────────
    # MÉTODOS ESPECÍFICOS
    # ──────────────────────────────────────────────

    def agregar_puntos(self, cantidad: int):
        """Suma puntos al saldo del cliente."""
        if cantidad <= 0:
            raise ValueError("La cantidad de puntos debe ser positiva.")
        self._puntos += cantidad

    def canjear_puntos(self, cantidad: int):
        """Descuenta puntos del saldo disponible."""
        if cantidad <= 0:
            raise ValueError("La cantidad a canjear debe ser positiva.")
        if cantidad > self._puntos:
            raise ValueError(f"Puntos insuficientes. Disponible: {self._puntos}")
        self._puntos -= cantidad

    # ──────────────────────────────────────────────
    # MÉTODOS POLIMÓRFICOS (override)
    # ──────────────────────────────────────────────

    def obtener_descuento(self) -> float:
        """5% de descuento base para clientes regulares."""
        return self.DESCUENTO_BASE

    def mostrar_info(self) -> str:
        base = super().mostrar_info()
        extra = f"  Puntos     : {self._puntos}\n"
        return base.replace("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n", 
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n{extra}", 1)

    # ──────────────────────────────────────────────
    # SERIALIZACIÓN
    # ──────────────────────────────────────────────

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["puntos"] = self._puntos
        return d

    def __str__(self) -> str:
        return super().__str__() + f" | Puntos: {self._puntos}"
