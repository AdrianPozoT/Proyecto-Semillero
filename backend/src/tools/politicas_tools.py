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

    respuesta_llm = _aplanar_content(llm.invoke(mensajes).content)

    secciones_unicas = set(d.metadata.get("seccion", "Desconocida") for d in docs)
    texto_secciones = ", ".join(str(s) for s in secciones_unicas)

    return f"{respuesta_llm}\n\n[Fuente: Políticas | Secciones: {texto_secciones}]"