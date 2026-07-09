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
    raise NotImplementedError
