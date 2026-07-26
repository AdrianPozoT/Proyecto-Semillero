"""
Herramienta de accion para registrar oportunidades en TXT.
Cumple requisitos del CRM: 03_Proceso_Ventas_CRM.txt Seccion 2 (registro
inicial) y Seccion 3 (requisitos para marcar como ganada).
"""

from datetime import datetime
from pathlib import Path

from langchain.tools import tool

REGISTRO_PATH = Path("registro_oportunidades.txt")

# Campos minimos para registrar la oportunidad (seccion 2 del manual):
# datos del cliente, producto de interes, monto estimado, etapa,
# proxima accion.
CAMPOS_REQUERIDOS_REGISTRO = ["cliente", "producto", "cantidad"]

# Campos adicionales que exige la seccion 3 SOLO para marcar como
# "ganada". No son obligatorios al registrar la oportunidad.
CAMPOS_REQUERIDOS_GANADA = [
    "orden_compra",
    "datos_facturacion",
    "precio_con_descuento",
    "condicion_pago",
    "monto_total",
    "fecha_cierre",
    "fecha_entrega",
]


def _siguiente_id():
    if not REGISTRO_PATH.exists():
        n = 0
    else:
        with open(REGISTRO_PATH, "r", encoding="utf-8") as f:
            n = sum(1 for linea in f if linea.strip())
    return f"OPP-{n + 1:04d}"


def _extraer_campo(linea: str, campo: str) -> str:
    """Extrae el valor de un campo campo=valor dentro de una linea
    separada por '|'. Devuelve '' si el campo no aparece o esta N/A."""
    for parte in linea.split("|"):
        parte = parte.strip()
        if parte.startswith(f"{campo}="):
            valor = parte.split("=", 1)[1].strip()
            return "" if valor in ("", "N/A") else valor
    return ""


@tool
def registrar_oportunidad(
    cliente: str = "",
    producto: str = "",
    cantidad: int = 0,
    etapa: str = "Prospecto",
    proxima_accion: str = "",
    precio_con_descuento: float = 0,
    condicion_pago: str = "",
    monto_total: float = 0,
    orden_compra: str = "",
    datos_facturacion: str = "",
    fecha_cierre: str = "",
    fecha_entrega: str = "",
) -> str:
    """
    Registra una oportunidad de venta en TXT.

    Requiere solo los datos minimos del registro inicial (seccion 2
    del Manual de Proceso de Ventas y CRM): cliente, producto y
    cantidad. Los demas campos (precio_con_descuento, condicion_pago,
    monto_total, orden_compra, datos_facturacion, fecha_cierre,
    fecha_entrega) son opcionales en este paso -- se completan despues,
    y son obligatorios recien cuando se quiera marcar la oportunidad
    como "ganada" (ver actualizar_oportunidad).
    """

    faltantes = []
    if not cliente:
        faltantes.append("cliente")
    if not producto:
        faltantes.append("producto")
    if cantidad <= 0:
        faltantes.append("cantidad")

    if faltantes:
        return "No se registro. Faltan datos obligatorios: " + ", ".join(faltantes)

    opp_id = _siguiente_id()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Los campos opcionales se guardan como N/A si no llegaron, para
    # que _extraer_campo() los detecte como faltantes mas adelante.
    linea = (
        f"{opp_id} | {timestamp} | cliente={cliente} | producto={producto} | "
        f"cantidad={cantidad} | etapa={etapa or 'Prospecto'} | "
        f"proxima_accion={proxima_accion or 'N/A'} | "
        f"precio_con_descuento={precio_con_descuento or 'N/A'} | "
        f"condicion_pago={condicion_pago or 'N/A'} | "
        f"monto_total={monto_total or 'N/A'} | "
        f"orden_compra={orden_compra or 'N/A'} | "
        f"datos_facturacion={datos_facturacion or 'N/A'} | "
        f"fecha_cierre={fecha_cierre or 'N/A'} | "
        f"fecha_entrega={fecha_entrega or 'N/A'} | "
        f"estado=abierta\n"
    )

    with open(REGISTRO_PATH, "a", encoding="utf-8") as f:
        f.write(linea)

    return f"Oportunidad registrada con ID {opp_id}."


@tool
def obtener_oportunidades() -> str:
    """Obtiene todas las oportunidades registradas.

    Retorna el contenido del archivo de registro tal cual está,
    sin reformatear, para que el frontend pueda parsearlo correctamente.
    """
    if not REGISTRO_PATH.exists():
        return "No hay oportunidades registradas"

    try:
        with open(REGISTRO_PATH, 'r', encoding='utf-8') as f:
            contenido = f.read().strip()

        if not contenido:
            return "No hay oportunidades registradas"

        return contenido

    except Exception as e:
        return f"Error al leer oportunidades: {str(e)}"


@tool
def actualizar_oportunidad(
    id_oportunidad: str = "",
    nuevo_estado: str = "",
    precio_con_descuento: float = 0,
    condicion_pago: str = "",
    monto_total: float = 0,
    orden_compra: str = "",
    datos_facturacion: str = "",
    fecha_cierre: str = "",
    fecha_entrega: str = "",
) -> str:
    """
    Actualiza el estado de una oportunidad. Estados validos: abierta,
    ganada, perdida.

    Si nuevo_estado es 'ganada', exige que la oportunidad tenga (ya
    guardados o entregados en esta misma llamada) todos los campos de
    la seccion 3 del Manual de Proceso de Ventas y CRM: orden de
    compra, datos de facturacion, precio con descuento, condicion de
    pago, monto total, fecha de cierre y fecha de entrega. Si falta
    alguno, NO cambia el estado y lo indica. Marcar como 'perdida' o
    'abierta' no requiere estos datos.
    """

    if not id_oportunidad:
        return "Falta el ID de la oportunidad."
    if not nuevo_estado:
        return "Falta el nuevo estado."
    if nuevo_estado not in ["abierta", "ganada", "perdida"]:
        return "Estado inválido. Usa: abierta, ganada, perdida"
    if not REGISTRO_PATH.exists():
        return f"Oportunidad {id_oportunidad} no encontrada."

    with open(REGISTRO_PATH, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    linea_objetivo = None
    for linea in lineas:
        if linea.startswith(id_oportunidad):
            linea_objetivo = linea
            break

    if linea_objetivo is None:
        return f"Oportunidad {id_oportunidad} no encontrada."

    # Datos entregados junto con esta llamada (por si se completan
    # justo al momento de marcar como ganada), o los ya guardados.
    valores_actuales = {
        "precio_con_descuento": str(precio_con_descuento) if precio_con_descuento else _extraer_campo(linea_objetivo, "precio_con_descuento"),
        "condicion_pago": condicion_pago or _extraer_campo(linea_objetivo, "condicion_pago"),
        "monto_total": str(monto_total) if monto_total else _extraer_campo(linea_objetivo, "monto_total"),
        "orden_compra": orden_compra or _extraer_campo(linea_objetivo, "orden_compra"),
        "datos_facturacion": datos_facturacion or _extraer_campo(linea_objetivo, "datos_facturacion"),
        "fecha_cierre": fecha_cierre or _extraer_campo(linea_objetivo, "fecha_cierre"),
        "fecha_entrega": fecha_entrega or _extraer_campo(linea_objetivo, "fecha_entrega"),
    }

    if nuevo_estado == "ganada":
        faltantes = [campo for campo, valor in valores_actuales.items() if not valor]
        if faltantes:
            return (
                f"No se puede marcar {id_oportunidad} como ganada. "
                f"Faltan estos datos obligatorios segun el Manual del Proceso "
                f"de Ventas y CRM (sección 3): {', '.join(faltantes)}."
            )

    lineas_nuevas = []
    for linea in lineas:
        if linea.startswith(id_oportunidad):
            # Actualizar estado
            linea = linea.replace("estado=abierta", f"estado={nuevo_estado}")
            linea = linea.replace("estado=ganada", f"estado={nuevo_estado}")
            linea = linea.replace("estado=perdida", f"estado={nuevo_estado}")

            # Si se marca como ganada y se entregaron datos nuevos en
            # esta llamada, actualizarlos tambien en la linea
            if nuevo_estado == "ganada":
                for campo, valor in valores_actuales.items():
                    import re
                    linea = re.sub(
                        rf"{campo}=[^|]*",
                        f"{campo}={valor}",
                        linea
                    )
        lineas_nuevas.append(linea)

    with open(REGISTRO_PATH, "w", encoding="utf-8") as f:
        f.writelines(lineas_nuevas)

    return f"Oportunidad {id_oportunidad} actualizada a estado: {nuevo_estado}"