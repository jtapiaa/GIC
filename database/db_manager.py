# database/db_manager.py
"""
Gestor de base de datos SQLite para el sistema GIC.
Aplica patrón Context Manager para manejo seguro de conexiones.
"""
import sqlite3
import json
import os
from utils.logger import logger
from utils.validaciones import ClienteNoEncontradoError, BaseDatosError, EmailDuplicadoError


class DatabaseManager:
    """
    Gestiona todas las operaciones CRUD sobre la base de datos SQLite.
    
    Attributes:
        db_path (str): Ruta al archivo .db de SQLite.
    """

    def __init__(self, db_path: str = "data/clientes.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._inicializar_db()

    # ──────────────────────────────────────────────
    # CONEXIÓN (Context Manager)
    # ──────────────────────────────────────────────

    def _conectar(self) -> sqlite3.Connection:
        """Crea y retorna una conexión con configuración optimizada."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row   # Permite acceso por nombre de columna
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # ──────────────────────────────────────────────
    # INICIALIZACIÓN
    # ──────────────────────────────────────────────

    def _inicializar_db(self):
        """Crea las tablas si no existen."""
        try:
            with self._conectar() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS clientes (
                        id              INTEGER PRIMARY KEY,
                        tipo            TEXT    NOT NULL,
                        nombre          TEXT    NOT NULL,
                        email           TEXT    UNIQUE NOT NULL,
                        telefono        TEXT    NOT NULL,
                        direccion       TEXT,
                        fecha_registro  TEXT,
                        activo          INTEGER DEFAULT 1,
                        datos_extra     TEXT    DEFAULT '{}'
                    )
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS actividad_log (
                        id          INTEGER PRIMARY KEY AUTOINCREMENT,
                        accion      TEXT NOT NULL,
                        descripcion TEXT,
                        timestamp   TEXT DEFAULT (datetime('now','localtime'))
                    )
                """)
            logger.info("Base de datos inicializada correctamente.")
        except sqlite3.Error as e:
            raise BaseDatosError(str(e))

    # ──────────────────────────────────────────────
    # OPERACIONES CRUD
    # ──────────────────────────────────────────────

    def insertar_cliente(self, cliente_dict: dict) -> bool:
        """
        Inserta un nuevo cliente en la base de datos.
        
        Args:
            cliente_dict: Diccionario con los datos del cliente (desde to_dict()).
        
        Raises:
            EmailDuplicadoError: Si el email ya existe.
            BaseDatosError: Si ocurre otro error en la BD.
        """
        # Separar campos base de campos específicos del tipo
        campos_base = {"id", "tipo", "nombre", "email", "telefono",
                       "direccion", "fecha_registro", "activo"}
        datos_extra = {k: v for k, v in cliente_dict.items()
                       if k not in campos_base}

        try:
            with self._conectar() as conn:
                conn.execute("""
                    INSERT INTO clientes 
                    (id, tipo, nombre, email, telefono, direccion, fecha_registro, activo, datos_extra)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    cliente_dict["id"],
                    cliente_dict["tipo"],
                    cliente_dict["nombre"],
                    cliente_dict["email"],
                    cliente_dict["telefono"],
                    cliente_dict.get("direccion", ""),
                    cliente_dict.get("fecha_registro"),
                    int(cliente_dict.get("activo", True)),
                    json.dumps(datos_extra, ensure_ascii=False)
                ))
                self._registrar_actividad(conn, "INSERT",
                    f"Cliente creado: {cliente_dict['nombre']} ({cliente_dict['tipo']})")
            logger.info(f"Cliente insertado: [{cliente_dict['tipo']}] {cliente_dict['nombre']}")
            return True

        except sqlite3.IntegrityError:
            raise EmailDuplicadoError(cliente_dict["email"])
        except sqlite3.Error as e:
            raise BaseDatosError(str(e))

    def obtener_todos(self, solo_activos: bool = True) -> list:
        """
        Retorna todos los clientes de la base de datos.
        
        Args:
            solo_activos: Si True, solo retorna clientes con activo=1.
        """
        try:
            with self._conectar() as conn:
                if solo_activos:
                    cursor = conn.execute(
                        "SELECT * FROM clientes WHERE activo = 1 ORDER BY nombre"
                    )
                else:
                    cursor = conn.execute("SELECT * FROM clientes ORDER BY nombre")
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise BaseDatosError(str(e))

    def obtener_por_id(self, id_cliente: int) -> dict:
        """
        Busca y retorna un cliente por su ID.
        
        Raises:
            ClienteNoEncontradoError: Si no existe el cliente.
        """
        try:
            with self._conectar() as conn:
                cursor = conn.execute(
                    "SELECT * FROM clientes WHERE id = ?", (id_cliente,)
                )
                fila = cursor.fetchone()
                if not fila:
                    raise ClienteNoEncontradoError(id_cliente)
                return dict(fila)
        except sqlite3.Error as e:
            raise BaseDatosError(str(e))

    def obtener_por_email(self, email: str) -> dict:
        """Busca un cliente por email."""
        try:
            with self._conectar() as conn:
                cursor = conn.execute(
                    "SELECT * FROM clientes WHERE email = ?", (email.lower(),)
                )
                fila = cursor.fetchone()
                if not fila:
                    raise ClienteNoEncontradoError(email)
                return dict(fila)
        except sqlite3.Error as e:
            raise BaseDatosError(str(e))

    def actualizar_cliente(self, id_cliente: int, datos: dict) -> bool:
        """
        Actualiza los datos de un cliente existente.
        
        Args:
            id_cliente: ID del cliente a actualizar.
            datos: Diccionario con los campos a modificar.
        """
        campos_permitidos = {"nombre", "email", "telefono", "direccion"}
        campos_actualizar = {k: v for k, v in datos.items() if k in campos_permitidos}

        if not campos_actualizar:
            logger.warning("No hay campos válidos para actualizar.")
            return False

        try:
            set_clause = ", ".join(f"{k} = ?" for k in campos_actualizar)
            valores = list(campos_actualizar.values()) + [id_cliente]

            with self._conectar() as conn:
                rows = conn.execute(
                    f"UPDATE clientes SET {set_clause} WHERE id = ?", valores
                ).rowcount

                if rows == 0:
                    raise ClienteNoEncontradoError(id_cliente)

                self._registrar_actividad(conn, "UPDATE",
                    f"Cliente ID {id_cliente} actualizado: {list(campos_actualizar.keys())}")

            logger.info(f"Cliente ID {id_cliente} actualizado.")
            return True
        except sqlite3.Error as e:
            raise BaseDatosError(str(e))

    def eliminar_cliente(self, id_cliente: int, baja_logica: bool = True) -> bool:
        """
        Elimina (lógica o física) un cliente.
        
        Args:
            id_cliente: ID del cliente.
            baja_logica: Si True, marca como inactivo. Si False, elimina físicamente.
        """
        try:
            with self._conectar() as conn:
                if baja_logica:
                    rows = conn.execute(
                        "UPDATE clientes SET activo = 0 WHERE id = ?", (id_cliente,)
                    ).rowcount
                else:
                    rows = conn.execute(
                        "DELETE FROM clientes WHERE id = ?", (id_cliente,)
                    ).rowcount

                if rows == 0:
                    raise ClienteNoEncontradoError(id_cliente)

                accion = "DEACTIVATE" if baja_logica else "DELETE"
                self._registrar_actividad(conn, accion,
                    f"Cliente ID {id_cliente} {'desactivado' if baja_logica else 'eliminado'}")

            logger.info(f"Cliente ID {id_cliente} {'desactivado' if baja_logica else 'eliminado'}.")
            return True
        except sqlite3.Error as e:
            raise BaseDatosError(str(e))

    def buscar_clientes(self, termino: str) -> list:
        """Busca clientes por nombre o email (búsqueda parcial)."""
        try:
            with self._conectar() as conn:
                cursor = conn.execute("""
                    SELECT * FROM clientes
                    WHERE activo = 1 AND (
                        nombre LIKE ? OR email LIKE ?
                    )
                    ORDER BY nombre
                """, (f"%{termino}%", f"%{termino}%"))
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise BaseDatosError(str(e))

    def obtener_estadisticas(self) -> dict:
        """Retorna estadísticas generales del sistema."""
        try:
            with self._conectar() as conn:
                total = conn.execute("SELECT COUNT(*) FROM clientes WHERE activo=1").fetchone()[0]
                por_tipo = conn.execute("""
                    SELECT tipo, COUNT(*) as cantidad
                    FROM clientes WHERE activo=1
                    GROUP BY tipo
                """).fetchall()
            return {
                "total_activos": total,
                "por_tipo": {row[0]: row[1] for row in por_tipo}
            }
        except sqlite3.Error as e:
            raise BaseDatosError(str(e))

    # ──────────────────────────────────────────────
    # REGISTRO DE ACTIVIDAD
    # ──────────────────────────────────────────────

    def _registrar_actividad(self, conn: sqlite3.Connection, accion: str, descripcion: str):
        """Inserta un registro en la tabla de actividad (log interno)."""
        conn.execute(
            "INSERT INTO actividad_log (accion, descripcion) VALUES (?, ?)",
            (accion, descripcion)
        )

    def obtener_log_actividad(self, limite: int = 50) -> list:
        """Retorna los últimos N registros de actividad."""
        with self._conectar() as conn:
            cursor = conn.execute(
                "SELECT * FROM actividad_log ORDER BY id DESC LIMIT ?", (limite,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def obtener_siguiente_id(self) -> int:
        """Retorna el siguiente ID disponible para un nuevo cliente."""
        with self._conectar() as conn:
            cursor = conn.execute("SELECT MAX(id) FROM clientes")
            resultado = cursor.fetchone()[0]
            return (resultado or 0) + 1
