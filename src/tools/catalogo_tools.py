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


embeddings = GoogleGenerativeAIEmbeddings(model=config.MODELO_EMBEDDING)
vectorstore = Chroma(
persist_directory=str(config.VECTORSTORE_DIR / "catalogo"),
embedding_function=embeddings,
collection_name="catalogo",
)
retriever = vectorstore.as_retriever(search_kwargs={"k": config.TOP_K})
llm = ChatGoogleGenerativeAI(model=config.MODELO_LLM, temperature=0)

SYSTEM_PROMPT = """Eres el Agente de Catálogo y Precios de Patito S.A.

Reglas estrictas:
- Responde ÚNICAMENTE con base en el CONTEXTO entregado. No uses conocimiento externo.
- Si el CONTEXTO no contiene información suficiente para responder, di exactamente:
  "No encontré información suficiente en la base documental proporcionada."
- Cuando cites un dato (precio, disponibilidad, característica), indica de qué
  sección o línea de producto proviene (ej. "según Línea Patito Pro").
- Sé breve y directo. No agregues opiniones ni recomendaciones de venta.
- No inventes precios, modelos ni condiciones que no aparezcan en el CONTEXTO.
"""


@tool
def consultar_catalogo(pregunta: str) -> str:
    """Responde preguntas sobre productos, especificaciones, disponibilidad
    y precios de lista del catalogo de Patito S.A."""


    docs = retriever.invoke(pregunta)
    #Guardia en código por siu docs está vacio, cortamos aqui: 
    if not docs:
        return "No encontré información suficiente en la base documental proporcionada."    
    
    #Caso en que el retriever devuelve documentos, construimos el contexto y llamamos al LLM
    contexto = "\n\n".join(d.page_content for d in docs)
    
    mensajes = [
        ("system", SYSTEM_PROMPT),
        ("user", f"CONTEXTO:\n{contexto}\n\nPREGUNTA: {pregunta}"),
    ]
    
    respuesta = llm.invoke(mensajes)
    return respuesta.content

