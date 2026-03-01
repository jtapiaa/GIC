# models/cliente_corporativo.py
"""
Subclase ClienteCorporativo: representa empresas con múltiples contactos.
"""
from models.cliente import Cliente


class ClienteCorporativo(Cliente):
    """
    Cliente corporativo que representa a una empresa.
    
    Attributes:
        _empresa (str): Nombre de la empresa.
        _rut_empresa (str): RUT o identificador fiscal de la empresa.
        _contactos (list): Lista de contactos adicionales en la empresa.
        _limite_credito (float): Límite de crédito asignado.
    """

    DESCUENTO_CORPORATIVO = 0.25  # 25%

    def __init__(self, id_cliente: int, nombre: str, email: str,
                 telefono: str, direccion: str,
                 empresa: str, rut_empresa: str,
                 limite_credito: float = 0.0):
        super().__init__(id_cliente, nombre, email, telefono, direccion)
        self._empresa = empresa
        self._rut_empresa = rut_empresa
        self._contactos = []
        self._limite_credito = max(0.0, limite_credito)

    # ──────────────────────────────────────────────
    # GETTERS Y SETTERS
    # ──────────────────────────────────────────────

    @property
    def empresa(self) -> str:
        return self._empresa

    @empresa.setter
    def empresa(self, valor: str):
        if not valor or len(valor.strip()) < 2:
            raise ValueError("El nombre de empresa debe tener al menos 2 caracteres.")
        self._empresa = valor.strip()

    @property
    def rut_empresa(self) -> str:
        return self._rut_empresa

    @property
    def limite_credito(self) -> float:
        return self._limite_credito

    @limite_credito.setter
    def limite_credito(self, valor: float):
        if valor < 0:
            raise ValueError("El límite de crédito no puede ser negativo.")
        self._limite_credito = valor

    @property
    def contactos(self) -> list:
        return self._contactos.copy()

    # ──────────────────────────────────────────────
    # MÉTODOS ESPECÍFICOS
    # ──────────────────────────────────────────────

    def agregar_contacto(self, nombre: str, cargo: str, email: str):
        """Agrega un contacto adicional a la empresa."""
        contacto = {"nombre": nombre, "cargo": cargo, "email": email}
        self._contactos.append(contacto)

    def obtener_contacto_principal(self) -> dict:
        """Retorna el contacto principal (primero registrado)."""
        if self._contactos:
            return self._contactos[0]
        return {"nombre": self._nombre, "cargo": "Principal", "email": self._email}

    # ──────────────────────────────────────────────
    # MÉTODOS POLIMÓRFICOS (override)
    # ──────────────────────────────────────────────

    def obtener_descuento(self) -> float:
        """25% de descuento corporativo fijo."""
        return self.DESCUENTO_CORPORATIVO

    def mostrar_info(self) -> str:
        base = super().mostrar_info()
        extra = (f"  Empresa    : {self._empresa}\n"
                 f"  RUT        : {self._rut_empresa}\n"
                 f"  Crédito    : ${self._limite_credito:,.0f}\n")
        return base.replace("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n", 
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n{extra}", 1)

    # ──────────────────────────────────────────────
    # SERIALIZACIÓN
    # ──────────────────────────────────────────────

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["empresa"] = self._empresa
        d["rut_empresa"] = self._rut_empresa
        d["limite_credito"] = self._limite_credito
        d["contactos"] = self._contactos
        return d

    def __str__(self) -> str:
        return super().__str__() + f" | Empresa: {self._empresa}"
