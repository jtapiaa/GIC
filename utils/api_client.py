# utils/api_client.py
"""
Módulo de integración con APIs externas.
- Validación de email vía Abstract API (gratuita).
- Simulación de envío de email de bienvenida.
"""
import re
from utils.logger import logger

try:
    import requests
    REQUESTS_DISPONIBLE = True
except ImportError:
    REQUESTS_DISPONIBLE = False


# ──────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ──────────────────────────────────────────────────────────────

# Obtén tu API Key gratuita en: https://www.abstractapi.com/
ABSTRACT_API_KEY = "TU_API_KEY_AQUI"
ABSTRACT_EMAIL_URL = "https://emailvalidation.abstractapi.com/v1/"


# ──────────────────────────────────────────────────────────────
# FUNCIONES DE INTEGRACIÓN
# ──────────────────────────────────────────────────────────────

def validar_email_api(email: str) -> dict:
    """
    Valida un email usando Abstract API.
    Si la API no está disponible, aplica validación local como fallback.
    
    Args:
        email: Dirección de correo a validar.
    
    Returns:
        dict con keys: 'valido' (bool), 'fuente' (str), 'detalle' (str).
    """
    # ── Fallback: validación local ──
    patron = r'^[\w\.\-]+@[\w\.\-]+\.\w{2,}$'
    valido_local = bool(re.match(patron, email))

    if not REQUESTS_DISPONIBLE or ABSTRACT_API_KEY == "TU_API_KEY_AQUI":
        logger.warning("API externa no configurada. Usando validación local.")
        return {
            "valido": valido_local,
            "fuente": "local",
            "detalle": "Validación por expresión regular"
        }

    # ── Llamada a la API ──
    try:
        resp = requests.get(
            ABSTRACT_EMAIL_URL,
            params={"api_key": ABSTRACT_API_KEY, "email": email},
            timeout=5
        )
        resp.raise_for_status()
        data = resp.json()

        valido_api = (
            data.get("is_valid_format", {}).get("value", False) and
            not data.get("is_disposable_email", {}).get("value", False)
        )

        logger.info(f"Email validado via API: {email} → {'✓' if valido_api else '✗'}")
        return {
            "valido": valido_api,
            "fuente": "abstractapi",
            "detalle": data.get("deliverability", "UNKNOWN")
        }

    except Exception as e:
        logger.warning(f"Error al llamar API externa: {e}. Usando validación local.")
        return {
            "valido": valido_local,
            "fuente": "local (fallback)",
            "detalle": str(e)
        }


def enviar_email_bienvenida(email: str, nombre: str, tipo_cliente: str) -> bool:
    """
    Simula el envío de un email de bienvenida al nuevo cliente.
    En producción, integrar con SendGrid, Mailgun u otro servicio SMTP.
    
    Args:
        email: Destinatario.
        nombre: Nombre del cliente.
        tipo_cliente: Tipo de membresía (Regular, Premium, Corporativo).
    
    Returns:
        bool: True si el envío fue exitoso (o simulado).
    """
    asunto = f"¡Bienvenido/a a SolutionTech, {nombre}!"
    cuerpo = (
        f"Estimado/a {nombre},\n\n"
        f"Tu cuenta como cliente {tipo_cliente} ha sido creada exitosamente.\n"
        f"Puedes acceder al sistema GIC para gestionar tus datos.\n\n"
        f"Saludos,\nEquipo SolutionTech"
    )

    # Simulación (log en lugar de envío real)
    logger.info(f"📧 EMAIL BIENVENIDA → Para: {email} | Asunto: {asunto}")
    print(f"\n{'='*50}")
    print(f"  📧 Email de bienvenida enviado")
    print(f"  Para   : {email}")
    print(f"  Asunto : {asunto}")
    print(f"{'='*50}\n")

    return True


def verificar_identidad(nombre: str, rut: str) -> dict:
    """
    Simula verificación de identidad de un cliente corporativo.
    En producción, integrar con SII u otro servicio de verificación.
    
    Args:
        nombre: Nombre de la empresa.
        rut: RUT de la empresa.
    
    Returns:
        dict con resultado de la verificación.
    """
    logger.info(f"Verificando identidad: {nombre} / {rut}")
    
    # Simulación: siempre aprueba si el RUT tiene formato válido
    rut_limpio = rut.replace(".", "").replace(" ", "")
    formato_valido = len(rut_limpio) >= 8 and "-" in rut_limpio

    return {
        "verificado": formato_valido,
        "empresa": nombre,
        "rut": rut,
        "fuente": "simulado",
        "mensaje": "Empresa verificada exitosamente" if formato_valido else "RUT con formato inválido"
    }
