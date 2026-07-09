"""
Tool de RAG para el dominio de proceso de ventas y uso del CRM.
Responsable: Vanessa

Mismo patron que catalogo_tools.py: retriever sobre la coleccion
"proceso_crm" -> contexto -> llm con reglas estrictas de no inventar.
"""

from langchain.tools import tool
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from src import config

# TODO: instanciar embeddings, vectorstore (collection_name="proceso_crm"),
# retriever y llm, igual que en catalogo_tools.py.

SYSTEM_PROMPT = """TODO: reglas estrictas para el agente de proceso de
venta y CRM (etapas del embudo, registro en CRM, requisitos para marcar
una oportunidad como ganada). No inventar, citar seccion, decir cuando no
hay informacion suficiente.
"""


@tool
def consultar_proceso_crm(pregunta: str) -> str:
    """Responde preguntas sobre etapas del embudo, registro en el CRM y
    requisitos para cerrar una venta en Patito S.A.

    TODO: mismo pipeline que consultar_catalogo en catalogo_tools.py.
    """
    raise NotImplementedError
