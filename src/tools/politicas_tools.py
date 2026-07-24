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


embedding = GoogleGenerativeAIEmbeddings(model=config.MODELO_EMBEDDING)
vectorstore = Chroma(
    persist_directory=str(config.VECTORSTORE_DIR / "politicas"),
    embedding_function=embedding,
    collection_name="politicas",
)
retriever = vectorstore.as_retriever(search_kwargs={"k": config.TOP_K})
llm = ChatGoogleGenerativeAI(model=config.MODELO_LLM, temperature=0)


SYSTEM_PROMPT = """Eres el Agente de Políticas Comerciales, Crédito y Cobranzas de Patito S.A.

Tu función es responder consultas sobre:
- Descuentos por nivel de autorización (Nivel 1 a Nivel 5).
- Condiciones de crédito y plazos de pago.
- Proceso de cobranzas y morosidad.
- Devoluciones y garantías.

Reglas de respuesta:
- Cita siempre la sección del documento de donde proviene la información.
- No inventes precios, descuentos ni condiciones que no estén explícitos en el contexto.
- Si la información no está en el contexto, responde textualmente:
  "No encontré información suficiente en la base documental proporcionada."
- Sé conciso y técnico. Evita lenguaje comercial o de venta.
"""


@tool
def consultar_politicas(pregunta: str) -> str:
    """Responde preguntas sobre descuentos autorizados, condiciones de
    credito, garantias y devoluciones de Patito S.A."""
    docs = retriever.invoke(pregunta)
    
    if not docs:
        return "No encontré información suficiente en la base documental proporcionada."
    
    contexto = "\n\n".join(d.page_content for d in docs)
    
    mensajes = [
        ("system", SYSTEM_PROMPT),
        ("user", f"CONTEXTO:\n{contexto}\n\nPREGUNTA: {pregunta}"),
    ]
    
    respuesta = llm.invoke(mensajes)
    return respuesta.content

