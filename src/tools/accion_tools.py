# Campos obligatorios segun 03_Proceso_Ventas_CRM.txt (seccion 3, requisitos
# para marcar una oportunidad como "ganada") y 02_Politicas_Comerciales (nivel
# de autorizacion del descuento).

"""
Herramienta de accion para registrar oportunidades en TXT.
Cumple requisitos del CRM: 03_Proceso_Ventas_CRM.txt Seccion 3
"""

from datetime import datetime
from pathlib import Path

from langchain.tools import tool

REGISTRO_PATH = Path("registro_oportunidades.txt")


<<<<<<< HEAD

def _siguiente_id() -> str:
    
    """Genera un ID incremental tipo OPP-0001.

    TODO: mismo patron que la practica (contar lineas no vacias del
    archivo de registro y sumar 1).
    """
    raise NotImplementedError
=======
def _siguiente_id():
    """Genera ID incremental OPP-0001, OPP-0002, etc."""
    if not REGISTRO_PATH.exists():
        n = 0
    else:
        with open(REGISTRO_PATH, "r", encoding="utf-8") as f:
            n = sum(1 for linea in f if linea.strip())
    return f"OPP-{n + 1:04d}"
>>>>>>> 331e33c77a9b3896730468e9c66ccb515e4cb107


@tool
def registrar_oportunidad(
    cliente: str = "",
    producto: str = "",
    cantidad: int = 0,
    precio_con_descuento: float = 0,
    condicion_pago: str = "",
    monto_total: float = 0,
    orden_compra: str = "",
    datos_facturacion: str = "",
    fecha_cierre: str = "",
    fecha_entrega: str = "",
) -> str:
<<<<<<< HEAD


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
=======
>>>>>>> 331e33c77a9b3896730468e9c66ccb515e4cb107
    """
    Registra una oportunidad de venta en TXT.
    Requiere TODOS los datos obligatorios del CRM.
    Si falta alguno, NO registra y devuelve cuales faltan.
    """
    
    faltantes = []
    
    if not cliente:
        faltantes.append("cliente")
    if not producto:
        faltantes.append("producto")
    if cantidad <= 0:
        faltantes.append("cantidad")
    if precio_con_descuento <= 0:
        faltantes.append("precio_con_descuento")
    if not condicion_pago:
        faltantes.append("condicion_pago")
    if monto_total <= 0:
        faltantes.append("monto_total")
    if not orden_compra:
        faltantes.append("orden_compra")
    if not datos_facturacion:
        faltantes.append("datos_facturacion")
    if not fecha_cierre:
        faltantes.append("fecha_cierre")
    if not fecha_entrega:
        faltantes.append("fecha_entrega")
    
    if faltantes:
        return "No se registro. Faltan datos: " + ", ".join(faltantes)
    
    opp_id = _siguiente_id()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    linea = (
        f"{opp_id} | {timestamp} | cliente={cliente} | producto={producto} | "
        f"cantidad={cantidad} | precio_con_descuento={precio_con_descuento} | "
        f"condicion_pago={condicion_pago} | monto_total={monto_total} | "
        f"orden_compra={orden_compra} | datos_facturacion={datos_facturacion} | "
        f"fecha_cierre={fecha_cierre} | fecha_entrega={fecha_entrega} | "
        f"estado=abierta\n"
    )
    
    with open(REGISTRO_PATH, "a", encoding="utf-8") as f:
        f.write(linea)
    
    return f"Oportunidad registrada con ID {opp_id}."


@tool
def obtener_oportunidades(cliente: str = "") -> str:
    """Lee oportunidades del archivo TXT."""
    
    if not REGISTRO_PATH.exists():
        return "No hay oportunidades registradas."
    
    with open(REGISTRO_PATH, "r", encoding="utf-8") as f:
        registros = f.readlines()
    
    if not registros:
        return "No hay oportunidades registradas."
    
    resultado = "Oportunidades:\n"
    for reg in registros:
        if cliente and cliente not in reg:
            continue
        resultado += f"- {reg.strip()}\n"
    
    return resultado


@tool
def actualizar_oportunidad(
    id_oportunidad: str = "",
    nuevo_estado: str = ""
) -> str:
    """
    Actualiza el estado de una oportunidad.
    Estados válidos: abierta, ganada, perdida
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
    
    encontrado = False
    lineas_nuevas = []
    
    for linea in lineas:
        if linea.startswith(id_oportunidad):
            encontrado = True
            linea = linea.replace("estado=abierta", f"estado={nuevo_estado}")
            linea = linea.replace("estado=ganada", f"estado={nuevo_estado}")
            linea = linea.replace("estado=perdida", f"estado={nuevo_estado}")
        
        lineas_nuevas.append(linea)
    
    if not encontrado:
        return f"Oportunidad {id_oportunidad} no encontrada."
    
    with open(REGISTRO_PATH, "w", encoding="utf-8") as f:
        f.writelines(lineas_nuevas)
    
    return f"Oportunidad {id_oportunidad} actualizada a estado: {nuevo_estado}"