"""
Tool de RAG para el dominio de catalogo y precios.
Responsable: Matias

Patron (igual al "Agente 1 - Conocimiento" de la practica 6):
retriever.invoke(pregunta) -> construir contexto -> llm.invoke() con un
system prompt que prohibe inventar y pide citar la seccion.
"""

from langchain.tools import tool
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from src import config

# TODO: instanciar aqui, a nivel de modulo (se carga una sola vez al importar):
# embeddings = GoogleGenerativeAIEmbeddings(model=config.MODELO_EMBEDDING)
# vectorstore = Chroma(
#     persist_directory=str(config.VECTORSTORE_DIR / "catalogo"),
#     embedding_function=embeddings,
#     collection_name="catalogo",
# )
# retriever = vectorstore.as_retriever(search_kwargs={"k": config.TOP_K})
# llm = ChatGoogleGenerativeAI(model=config.MODELO_LLM, temperature=0)

SYSTEM_PROMPT = """TODO: escribe las reglas estrictas para este agente.
Pistas (mira el PROMPT_CONOCIMIENTO de la practica 6):
- responder UNICAMENTE con base en el CONTEXTO entregado
- citar la seccion cuando sea posible
- que responder exactamente cuando la info no este en el contexto
- ser breve, no inventar datos
"""


@tool
def consultar_catalogo(pregunta: str) -> str:
    """Responde preguntas sobre productos, especificaciones, disponibilidad
    y precios de lista del catalogo de Patito S.A.

    TODO:
    1. docs = retriever.invoke(pregunta)
    2. contexto = unir el contenido de los docs recuperados (d.page_content)
    3. armar los mensajes: system=SYSTEM_PROMPT, user=f"CONTEXTO:\\n{contexto}\\n\\nPREGUNTA: {pregunta}"
    4. return llm.invoke([...]).content

    Pregunta para pensar antes de escribir el prompt: ¿que deberia
    devolver esta funcion si el retriever no encuentra nada relevante?
    """
    raise NotImplementedError
