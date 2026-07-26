"""
Tool de RAG para el dominio de catalogo y precios.

Recupera los chunks mas relevantes del indice de catalogo, arma un
contexto con ellos y le pide al LLM que responda unicamente a partir de
ese contexto, citando la seccion de origen y sin inventar datos.
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
def consultar_catalogo(pregunta: str) -> str:
    """Responde preguntas sobre productos, especificaciones, disponibilidad
    y precios de lista del catalogo de Patito S.A."""

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

    return respuesta_llm