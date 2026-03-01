# utils/logger.py
"""
Configuración del sistema de logging para el sistema GIC.
Registra eventos en archivo y consola simultáneamente.
"""
import logging
import os
from datetime import datetime


def configurar_logger(nombre: str = "GIC") -> logging.Logger:
    """
    Configura y retorna un logger con handlers para archivo y consola.
    
    Args:
        nombre: Nombre del logger (por defecto 'GIC').
    
    Returns:
        logging.Logger: Logger configurado.
    """
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger(nombre)
    logger.setLevel(logging.DEBUG)

    # Evitar duplicar handlers si el logger ya existe
    if logger.handlers:
        return logger

    # ── Handler para archivo (DEBUG y superiores) ──
    nombre_archivo = f"logs/gic_{datetime.now().strftime('%Y%m%d')}.log"
    fh = logging.FileHandler(nombre_archivo, encoding="utf-8")
    fh.setLevel(logging.DEBUG)

    # ── Handler para consola (INFO y superiores) ──
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # ── Formato ──
    fmt_archivo  = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(module)-20s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    fmt_consola = logging.Formatter("%(levelname)-8s | %(message)s")

    fh.setFormatter(fmt_archivo)
    ch.setFormatter(fmt_consola)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


# Logger global del sistema
logger = configurar_logger()
