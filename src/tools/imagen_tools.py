"""
Tool multimodal: analiza una imagen de producto, cotizacion o lista de
precios usando la capacidad de vision de Gemini.
Responsable: Pozo

Patron (igual al "Agente 2 - Multimodal" de la practica 6): leer la
imagen en base64 y mandarla en un HumanMessage junto con el prompt de
extraccion.
"""

import base64

from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src import config

# TODO: llm = ChatGoogleGenerativeAI(model=config.MODELO_LLM, temperature=0)
llm = ChatGoogleGenerativeAI(model=config.MODELO_LLM, temperature=0)

@tool
def analizar_imagen_producto(ruta_imagen: str) -> str:
    """Analiza la imagen de un producto, cotizacion o lista de precios y
    extrae la informacion relevante para relacionarla con el catalogo.
    Recibe la RUTA del archivo de imagen.

    TODO:
    1. Leer el archivo y codificarlo en base64 (manejar FileNotFoundError).
    2. Armar el HumanMessage con un bloque de texto (prompt) + un bloque
       de imagen (data:image/png;base64,...).
    3. return llm.invoke([mensaje]).content
    """
    try:
      with open(ruta_imagen, "rb") as image_file:
        b64 = base64.b64encode(image_file.read()).decode()
    except FileNotFoundError:
        return f"No se encontro el archivo: {ruta_imagen}"


    prompt = (
        "Eres un asistente que analiza documentos de Patito S.A. "
        "Primero identifica a que tipo de documento corresponde la imagen: "
        "'PRODUCTO' (ficha individual de un producto), "
        "'COTIZACION' (cotizacion a un cliente) o "
        "'LISTA_PRECIOS' (listado de varios productos con precios). "
        "Analiza SOLO como ese tipo de documento. No mezcles los otros formatos.\n\n"
        "Responde EXACTAMENTE con este formato:\n\n"
        "Tipo de documento: <PRODUCTO / COTIZACION / LISTA_PRECIOS>\n\n"
        "Si es PRODUCTO, incluye unicamente:\n"
        "Nombre del producto: ...\n"
        "SKU: ...\n"
        "Codigo de proveedor: ...\n"
        "Cantidad: ...\n"
        "Precio unitario: ...\n"
        "Precio total: ...\n\n"
        "Si es COTIZACION, incluye unicamente:\n"
        "Nombre del cliente: ...\n"
        "Numero de cotizacion: ...\n"
        "Fecha: ...\n"
        "Vendedor: ...\n"
        "Total: ...\n\n"
        "Si es LISTA_PRECIOS, incluye unicamente, por cada producto encontrado:\n"
        "Nombre del producto: ...\n"
        "Precio unitario: ...\n"
        "Precio total: ...\n\n"
        "No inventes informacion que no este en la imagen. "
        "Si un dato no aparece, escribe 'N/A'. "
        "No incluyas las secciones de los otros tipos de documento."
    )

    mensaje = HumanMessage(
        content=[
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": f"data:image/png;base64,{b64}"}
        ])
    return llm.invoke([mensaje]).content

