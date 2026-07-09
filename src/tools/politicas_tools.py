"""
Tool de RAG para el dominio de politicas comerciales, descuentos y credito.
Responsable: Pozo

Mismo patron que catalogo_tools.py: retriever sobre la coleccion
"politicas" -> contexto -> llm con reglas estrictas de no inventar.
"""

from langchain.tools import tool
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from src import config

# TODO: instanciar embeddings, vectorstore (collection_name="politicas"),
# retriever y llm, igual que en catalogo_tools.py.

SYSTEM_PROMPT = """TODO: reglas estrictas para el agente de politicas
comerciales (descuentos por nivel de autorizacion, condiciones de credito,
garantias, devoluciones). No inventar, citar seccion, decir cuando no hay
informacion suficiente.
"""


@tool
def consultar_politicas(pregunta: str) -> str:
    """Responde preguntas sobre descuentos autorizados, condiciones de
    credito, garantias y devoluciones de Patito S.A.

    TODO: mismo pipeline que consultar_catalogo en catalogo_tools.py.
    """
    raise NotImplementedError
