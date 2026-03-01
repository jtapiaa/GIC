# utils/json_manager.py
"""
Gestión de persistencia en archivos JSON y CSV.
"""
import json
import csv
import os
from utils.logger import logger


class JsonManager:
    """Maneja la exportación e importación de clientes en formato JSON."""

    def __init__(self, path: str = "data/clientes.json"):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def exportar(self, lista_dicts: list) -> bool:
        """Guarda la lista de clientes en el archivo JSON."""
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(lista_dicts, f, indent=4, ensure_ascii=False)
            logger.info(f"JSON exportado: {len(lista_dicts)} clientes → {self.path}")
            return True
        except IOError as e:
            logger.error(f"Error al exportar JSON: {e}")
            return False

    def importar(self) -> list:
        """Carga los clientes desde el archivo JSON."""
        if not os.path.exists(self.path):
            logger.warning(f"Archivo JSON no encontrado: {self.path}")
            return []
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                datos = json.load(f)
            logger.info(f"JSON importado: {len(datos)} clientes desde {self.path}")
            return datos
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error al importar JSON: {e}")
            return []


class CsvManager:
    """Maneja la exportación e importación de clientes en formato CSV."""

    COLUMNAS = ["id", "tipo", "nombre", "email", "telefono", "direccion", "fecha_registro", "activo"]

    def __init__(self, path: str = "data/clientes.csv"):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def exportar(self, lista_dicts: list) -> bool:
        """Guarda la lista de clientes en el archivo CSV."""
        try:
            with open(self.path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.COLUMNAS, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(lista_dicts)
            logger.info(f"CSV exportado: {len(lista_dicts)} clientes → {self.path}")
            return True
        except IOError as e:
            logger.error(f"Error al exportar CSV: {e}")
            return False

    def importar(self) -> list:
        """Carga los clientes desde el archivo CSV."""
        if not os.path.exists(self.path):
            logger.warning(f"Archivo CSV no encontrado: {self.path}")
            return []
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                datos = list(reader)
            logger.info(f"CSV importado: {len(datos)} registros desde {self.path}")
            return datos
        except IOError as e:
            logger.error(f"Error al importar CSV: {e}")
            return []
