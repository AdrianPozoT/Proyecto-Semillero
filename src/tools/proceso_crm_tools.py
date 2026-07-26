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
- Cuando cites un dato (etapa del embudo, requisito, campo del CRM), indica de qué
  sección del manual proviene (ej. "según sección 3. Requisitos para marcar como Ganada").
- Sé breve y directo. No agregues opiniones ni recomendaciones de venta.
- No inventes etapas, campos ni requisitos que no aparezcan en el CONTEXTO.
"""


def _aplanar_content(content) -> str:
    """Gemini a veces devuelve content como lista de bloques
    ({'type': 'text', 'text': ..., 'extras': {...}}) en vez de un
    string plano. Aplanar antes de usarlo, para no incrustar el repr
    crudo de la lista en la respuesta final (por ejemplo cuando esta
    tool se invoca directamente desde main.py fuera del orquestador).
    """
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        texto = ""
        for bloque in content:
            if isinstance(bloque, dict) and "text" in bloque:
                texto += bloque["text"]
            elif isinstance(bloque, str):
                texto += bloque
        return texto

    return str(content)


@tool
def consultar_proceso_crm(pregunta: str) -> str:
    """Responde preguntas sobre etapas del embudo, registro en el CRM y
    requisitos para cerrar una venta en Patito S.A.
    """
    docs = retriever.invoke(pregunta)

    # Guardia en código por si docs está vacío, cortamos aquí:
    if not docs:
        return "No encontré información suficiente en la base documental proporcionada."

    # Caso en que el retriever devuelve documentos, construimos el contexto y llamamos al LLM
    contexto = "\n\n".join(d.page_content for d in docs)

    mensajes = [
        ("system", SYSTEM_PROMPT),
        ("user", f"CONTEXTO:\n{contexto}\n\nPREGUNTA: {pregunta}"),
    ]

    respuesta_llm = _aplanar_content(llm.invoke(mensajes).content)

    secciones_unicas = set(d.metadata.get("seccion", "Desconocida") for d in docs)
    texto_secciones = ", ".join(str(s) for s in secciones_unicas)

    return f"{respuesta_llm}\n\n[Fuente: Proceso CRM | Secciones: {texto_secciones}]"