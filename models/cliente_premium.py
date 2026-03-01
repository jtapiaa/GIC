# models/cliente_premium.py
"""
Subclase ClientePremium: clientes con beneficios especiales y niveles de membresía.
"""
from models.cliente import Cliente


class ClientePremium(Cliente):
    """
    Cliente premium con niveles de membresía y descuentos progresivos.
    
    Attributes:
        _nivel_premium (int): Nivel de membresía (1=Plata, 2=Oro, 3=Platino).
        _beneficios (list): Lista de beneficios activos.
    """

    NIVELES = {
        1: {"nombre": "Plata",   "descuento": 0.10},
        2: {"nombre": "Oro",     "descuento": 0.15},
        3: {"nombre": "Platino", "descuento": 0.20},
    }

    def __init__(self, id_cliente: int, nombre: str, email: str,
                 telefono: str, direccion: str, nivel_premium: int = 1):
        super().__init__(id_cliente, nombre, email, telefono, direccion)
        self.nivel_premium = nivel_premium  # Usa el setter
        self._beneficios = []

    # ──────────────────────────────────────────────
    # GETTERS Y SETTERS
    # ──────────────────────────────────────────────

    @property
    def nivel_premium(self) -> int:
        return self._nivel_premium

    @nivel_premium.setter
    def nivel_premium(self, valor: int):
        if valor not in self.NIVELES:
            raise ValueError(f"Nivel inválido. Opciones: {list(self.NIVELES.keys())}")
        self._nivel_premium = valor

    @property
    def nombre_nivel(self) -> str:
        return self.NIVELES[self._nivel_premium]["nombre"]

    @property
    def beneficios(self) -> list:
        return self._beneficios.copy()

    # ──────────────────────────────────────────────
    # MÉTODOS ESPECÍFICOS
    # ──────────────────────────────────────────────

    def agregar_beneficio(self, beneficio: str):
        if beneficio not in self._beneficios:
            self._beneficios.append(beneficio)

    def subir_nivel(self):
        """Incrementa el nivel premium si es posible."""
        if self._nivel_premium < 3:
            self._nivel_premium += 1
        else:
            raise ValueError("El cliente ya está en el nivel máximo (Platino).")

    # ──────────────────────────────────────────────
    # MÉTODOS POLIMÓRFICOS (override)
    # ──────────────────────────────────────────────

    def obtener_descuento(self) -> float:
        """Descuento progresivo según nivel: 10%, 15% o 20%."""
        return self.NIVELES[self._nivel_premium]["descuento"]

    def mostrar_info(self) -> str:
        base = super().mostrar_info()
        extra = f"  Nivel      : {self.nombre_nivel} (Nivel {self._nivel_premium})\n"
        return base.replace("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n", 
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n{extra}", 1)

    # ──────────────────────────────────────────────
    # SERIALIZACIÓN
    # ──────────────────────────────────────────────

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["nivel_premium"] = self._nivel_premium
        d["nombre_nivel"] = self.nombre_nivel
        d["beneficios"] = self._beneficios
        return d

    def __str__(self) -> str:
        return super().__str__() + f" | Nivel: {self.nombre_nivel}"
