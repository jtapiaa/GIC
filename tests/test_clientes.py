# tests/test_clientes.py
"""
Pruebas unitarias para el sistema Gestion Integral de Clientes.
Cubre modelos, validaciones y operaciones de base de datos.

Cómo ejecutar:
    python -m pytest tests/ -v
    # o
    python -m unittest discover tests/
"""
import unittest
import os
import sys

# Asegurar que la raíz del proyecto esté en el path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../Gestor-de-Clientes-Inteligentes")))

from models.cliente import Cliente
from models.cliente_regular import ClienteRegular
from models.cliente_premium import ClientePremium
from models.cliente_corporativo import ClienteCorporativo
from utils.validaciones import (
    ClienteNoEncontradoError, EmailDuplicadoError, validar_email, validar_telefono
)
from database.db_manager import DatabaseManager


# ──────────────────────────────────────────────────────────────
# TESTS: MODELOS
# ──────────────────────────────────────────────────────────────

class TestClienteBase(unittest.TestCase):
    """Pruebas sobre la clase base Cliente."""

    def setUp(self):
        self.cliente = ClienteRegular(1, "Ana López", "ana@test.com", "+56912345678", "Calle 1")

    def test_nombre_se_almacena_correctamente(self):
        self.assertEqual(self.cliente.nombre, "Ana López")

    def test_email_se_normaliza_a_minusculas(self):
        c = ClienteRegular(2, "Test", "TEST@EMAIL.COM", "+56912345678", "Dir")
        self.assertEqual(c.email, "test@email.com")

    def test_nombre_muy_corto_lanza_error(self):
        with self.assertRaises(ValueError):
            ClienteRegular(3, "A", "test@test.com", "123456789", "Dir")

    def test_email_invalido_lanza_error(self):
        with self.assertRaises(ValueError):
            ClienteRegular(4, "Test User", "correo-sin-arroba", "123456789", "Dir")

    def test_telefono_invalido_lanza_error(self):
        with self.assertRaises(ValueError):
            ClienteRegular(5, "Test User", "test@test.com", "abc", "Dir")

    def test_igualdad_por_id(self):
        otro = ClienteRegular(1, "Otro Nombre", "otro@test.com", "987654321", "Calle 2")
        self.assertEqual(self.cliente, otro)

    def test_desigualdad_distinto_id(self):
        otro = ClienteRegular(99, "Ana López", "ana@test.com", "+56912345678", "Calle 1")
        self.assertNotEqual(self.cliente, otro)

    def test_str_contiene_nombre(self):
        self.assertIn("Ana López", str(self.cliente))

    def test_to_dict_contiene_campos_base(self):
        d = self.cliente.to_dict()
        for campo in ["id", "tipo", "nombre", "email", "telefono", "activo"]:
            self.assertIn(campo, d)

    def test_activo_por_defecto(self):
        self.assertTrue(self.cliente.activo)


class TestClienteRegular(unittest.TestCase):
    """Pruebas específicas de ClienteRegular."""

    def setUp(self):
        self.cliente = ClienteRegular(1, "Ana López", "ana@test.com", "+56912345678", "Calle 1")

    def test_descuento_es_5_porciento(self):
        self.assertEqual(self.cliente.obtener_descuento(), 0.05)

    def test_puntos_iniciales_son_cero(self):
        self.assertEqual(self.cliente.puntos, 0)

    def test_agregar_puntos(self):
        self.cliente.agregar_puntos(100)
        self.assertEqual(self.cliente.puntos, 100)

    def test_agregar_puntos_negativos_lanza_error(self):
        with self.assertRaises(ValueError):
            self.cliente.agregar_puntos(-10)

    def test_canjear_puntos(self):
        self.cliente.agregar_puntos(200)
        self.cliente.canjear_puntos(50)
        self.assertEqual(self.cliente.puntos, 150)

    def test_canjear_mas_puntos_de_los_disponibles(self):
        with self.assertRaises(ValueError):
            self.cliente.canjear_puntos(999)

    def test_tipo_es_cliente_regular(self):
        self.assertEqual(self.cliente.obtener_tipo(), "ClienteRegular")


class TestClientePremium(unittest.TestCase):
    """Pruebas específicas de ClientePremium."""

    def setUp(self):
        self.plata   = ClientePremium(1, "Carlos Ruiz", "carlos@test.com", "+56911111111", "Dir", nivel_premium=1)
        self.oro     = ClientePremium(2, "María Díaz", "maria@test.com",   "+56922222222", "Dir", nivel_premium=2)
        self.platino = ClientePremium(3, "Pedro Soto", "pedro@test.com",   "+56933333333", "Dir", nivel_premium=3)

    def test_descuento_plata(self):
        self.assertEqual(self.plata.obtener_descuento(), 0.10)

    def test_descuento_oro(self):
        self.assertEqual(self.oro.obtener_descuento(), 0.15)

    def test_descuento_platino(self):
        self.assertEqual(self.platino.obtener_descuento(), 0.20)

    def test_nivel_invalido_lanza_error(self):
        with self.assertRaises(ValueError):
            ClientePremium(4, "Test", "test@test.com", "123456789", "Dir", nivel_premium=5)

    def test_subir_nivel(self):
        self.plata.subir_nivel()
        self.assertEqual(self.plata.nivel_premium, 2)

    def test_subir_nivel_maximo_lanza_error(self):
        with self.assertRaises(ValueError):
            self.platino.subir_nivel()

    def test_nombre_nivel(self):
        self.assertEqual(self.plata.nombre_nivel,   "Plata")
        self.assertEqual(self.oro.nombre_nivel,     "Oro")
        self.assertEqual(self.platino.nombre_nivel, "Platino")


class TestClienteCorporativo(unittest.TestCase):
    """Pruebas específicas de ClienteCorporativo."""

    def setUp(self):
        self.cliente = ClienteCorporativo(
            1, "Juan Pérez", "juan@empresa.com", "+56944444444", "Av. Principal 123",
            empresa="TechCorp SA", rut_empresa="12345678-9", limite_credito=500000
        )

    def test_descuento_es_25_porciento(self):
        self.assertEqual(self.cliente.obtener_descuento(), 0.25)

    def test_agregar_contacto(self):
        self.cliente.agregar_contacto("Laura", "Gerenta", "laura@empresa.com")
        self.assertEqual(len(self.cliente.contactos), 1)

    def test_limite_credito_negativo_lanza_error(self):
        with self.assertRaises(ValueError):
            self.cliente.limite_credito = -1000

    def test_to_dict_incluye_empresa(self):
        d = self.cliente.to_dict()
        self.assertIn("empresa", d)
        self.assertEqual(d["empresa"], "TechCorp SA")


# ──────────────────────────────────────────────────────────────
# TESTS: VALIDACIONES
# ──────────────────────────────────────────────────────────────

class TestValidaciones(unittest.TestCase):
    """Pruebas de funciones de validación."""

    def test_email_valido(self):
        self.assertTrue(validar_email("usuario@dominio.com"))
        self.assertTrue(validar_email("user.name+tag@example.co.uk"))

    def test_email_invalido(self):
        self.assertFalse(validar_email("sin-arroba"))
        self.assertFalse(validar_email("@sin-usuario.com"))
        self.assertFalse(validar_email("usuario@"))

    def test_telefono_valido(self):
        self.assertTrue(validar_telefono("+56912345678"))
        self.assertTrue(validar_telefono("12345678"))

    def test_telefono_invalido(self):
        self.assertFalse(validar_telefono("abc"))
        self.assertFalse(validar_telefono("123"))


# ──────────────────────────────────────────────────────────────
# TESTS: BASE DE DATOS
# ──────────────────────────────────────────────────────────────

class TestDatabaseManager(unittest.TestCase):
    """Pruebas de integración con SQLite usando BD en memoria."""

    def setUp(self):
        # Base de datos temporal para pruebas
        self.db = DatabaseManager(db_path="data/test_temp.db")
        self.cliente = ClienteRegular(
            1, "Test User", "test@test.com", "+56900000001", "Dir Test"
        )

    def tearDown(self):
        # Limpiar BD de prueba
        if os.path.exists("data/test_temp.db"):
            os.remove("data/test_temp.db")

    def test_insertar_y_recuperar_cliente(self):
        self.db.insertar_cliente(self.cliente.to_dict())
        clientes = self.db.obtener_todos()
        self.assertEqual(len(clientes), 1)
        self.assertEqual(clientes[0]["nombre"], "Test User")

    def test_email_duplicado_lanza_error(self):
        self.db.insertar_cliente(self.cliente.to_dict())
        cliente2 = ClienteRegular(2, "Otro User", "test@test.com", "+56900000002", "Dir 2")
        with self.assertRaises(EmailDuplicadoError):
            self.db.insertar_cliente(cliente2.to_dict())

    def test_eliminar_cliente(self):
        self.db.insertar_cliente(self.cliente.to_dict())
        self.db.eliminar_cliente(1)
        clientes = self.db.obtener_todos(solo_activos=True)
        self.assertEqual(len(clientes), 0)

    def test_eliminar_cliente_inexistente(self):
        with self.assertRaises(ClienteNoEncontradoError):
            self.db.eliminar_cliente(9999)

    def test_obtener_por_id(self):
        self.db.insertar_cliente(self.cliente.to_dict())
        datos = self.db.obtener_por_id(1)
        self.assertEqual(datos["email"], "test@test.com")

    def test_estadisticas(self):
        self.db.insertar_cliente(self.cliente.to_dict())
        stats = self.db.obtener_estadisticas()
        self.assertEqual(stats["total_activos"], 1)

    def test_buscar_por_nombre(self):
        self.db.insertar_cliente(self.cliente.to_dict())
        resultados = self.db.buscar_clientes("Test")
        self.assertEqual(len(resultados), 1)

    def test_siguiente_id(self):
        self.assertEqual(self.db.obtener_siguiente_id(), 1)
        self.db.insertar_cliente(self.cliente.to_dict())
        self.assertEqual(self.db.obtener_siguiente_id(), 2)


# ──────────────────────────────────────────────────────────────
# TESTS: POLIMORFISMO
# ──────────────────────────────────────────────────────────────

class TestPolimorfismo(unittest.TestCase):
    """Verifica que el polimorfismo funciona correctamente."""

    def setUp(self):
        self.clientes = [
            ClienteRegular(1,    "Ana",   "ana@t.com",   "+56911111111", "Dir"),
            ClientePremium(2,    "Ben",   "ben@t.com",   "+56922222222", "Dir", nivel_premium=2),
            ClienteCorporativo(3,"Carl",  "carl@t.com",  "+56933333333", "Dir", "Corp SA", "1234-5"),
        ]

    def test_cada_tipo_tiene_descuento_distinto(self):
        descuentos = [c.obtener_descuento() for c in self.clientes]
        self.assertEqual(descuentos[0], 0.05)
        self.assertEqual(descuentos[1], 0.15)
        self.assertEqual(descuentos[2], 0.25)

    def test_todos_son_instancias_de_cliente(self):
        for c in self.clientes:
            self.assertIsInstance(c, Cliente)

    def test_todos_implementan_to_dict(self):
        for c in self.clientes:
            d = c.to_dict()
            self.assertIsInstance(d, dict)
            self.assertIn("tipo", d)


# ──────────────────────────────────────────────────────────────
# PUNTO DE ENTRADA
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    unittest.main(verbosity=2)
