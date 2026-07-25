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

embeddings = GoogleGenerativeAIEmbeddings(model=config.MODELO_EMBEDDING)
vectorstore = Chroma(
    persist_directory=str(config.VECTORSTORE_DIR / "proceso_crm"),
    embedding_function=embeddings,
    collection_name="proceso_crm",
)
retriever = vectorstore.as_retriever(search_kwargs={"k": config.TOP_K})
llm = ChatGoogleGenerativeAI(model=config.MODELO_LLM, temperature=0)

SYSTEM_PROMPT = """Eres el Agente de Proceso de Venta y CRM de Patito S.A.

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
def consultar_proceso_crm(pregunta: str) -> str:
    """Responde preguntas sobre etapas del embudo, registro en el CRM y
    requisitos para cerrar una venta en Patito S.A.
    """
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
    


