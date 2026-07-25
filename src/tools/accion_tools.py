"""
Tool de accion: registra una oportunidad/cotizacion en un archivo de
texto, con validacion de datos obligatorios antes de escribir.
Responsable: Vanessa (opcional -- solo si implementan la Opcion B del
enunciado, ademas o en vez del agente multimodal)

Patron (igual al "Agente 3 - Accion" de la practica 6): validar primero,
generar ID unico + timestamp, escribir solo si todo esta completo.
"""

from datetime import datetime
from pathlib import Path

from langchain.tools import tool

REGISTRO_PATH = Path("registro_oportunidades.txt")

# TODO: definir los campos obligatorios segun 02_Politicas_Comerciales...
# y 03_Proceso_Ventas_CRM.txt (cliente y contacto, producto, cantidad,
# precio con descuento aplicado y su autorizacion si supera el 10%,
# condicion de pago, monto total).
CAMPOS_OBLIGATORIOS: list[str] = []


def _siguiente_id() -> str:
    
    """Genera un ID incremental tipo OPP-0001.

    TODO: mismo patron que la practica (contar lineas no vacias del
    archivo de registro y sumar 1).
    """
    raise NotImplementedError


@tool
def registrar_oportunidad(
    cliente: str = "",
    producto: str = "",
    cantidad: int = 0,
    precio_con_descuento: float = 0,
    condicion_pago: str = "",
    monto_total: float = 0,
) -> str:


    """Registra una oportunidad de venta en el archivo de texto. Requiere
    TODOS los datos obligatorios; si falta alguno, NO registra y devuelve
    cuales faltan.

    TODO:
    1. Revisar si esta firma de parametros cubre lo que pide el enunciado
       (seccion 3.5 del caso practico) -- ajustala si falta algo.
    2. Validar contra CAMPOS_OBLIGATORIOS.
    3. Si falta algo: return "No se registro. Faltan datos: ..."
    4. Si esta completo: generar id + timestamp, escribir la linea,
       devolver confirmacion con el ID asignado.
    """
    raise NotImplementedError
