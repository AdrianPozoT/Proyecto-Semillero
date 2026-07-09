"""
Orquestador del sistema: un unico agente LangChain (create_agent) que
decide, segun la pregunta del usuario, que tool(s) invocar.

No hay clasificador propio ni grafo manual: el ruteo vive en
SYSTEM_PROMPT y en las docstrings de cada tool (el LLM las lee para
decidir). Responsable: Matias
"""

import uuid

from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

from src import config
from src.tools.catalogo_tools import consultar_catalogo
from src.tools.politicas_tools import consultar_politicas
from src.tools.proceso_crm_tools import consultar_proceso_crm
from src.tools.imagen_tools import analizar_imagen_producto

# from src.tools.accion_tools import registrar_oportunidad  # descomentar si la implementan

TOOLS = [
    consultar_catalogo,
    consultar_politicas,
    consultar_proceso_crm,
    analizar_imagen_producto,
    # registrar_oportunidad,
]

SYSTEM_PROMPT = """TODO: escribe las reglas de ruteo en lenguaje natural.
Guiate por el SYSTEM_PROMPT del asistente de gastos en la practica 6:
- explica para que sirve cada tool y cuando usarla
- que hacer si falta informacion para una tool
- nunca inventar datos; si no hay informacion, decirlo
"""

# TODO:
# llm = ChatGoogleGenerativeAI(model=config.MODELO_LLM, temperature=0)
# memoria = InMemorySaver()
# orquestador = create_agent(
#     model=llm,
#     tools=TOOLS,
#     system_prompt=SYSTEM_PROMPT,
#     checkpointer=memoria,
# )


def extraer_texto(content) -> str:
    """Gemini a veces devuelve el content como una lista de bloques
    (texto + firmas de 'thinking'). Aplanar a texto plano.

    TODO: portar la funcion tal cual la vieron en la practica 6.
    """
    raise NotImplementedError


def consultar(pregunta: str, thread_id: str | None = None) -> dict:
    """Invoca al orquestador para una consulta. Pensada para ser llamada
    tanto desde una CLI de pruebas como desde app/main.py (FastAPI) --
    asi la interfaz que se agregue despues (web, desktop) no toca esta
    funcion, solo la importa.

    TODO:
    1. thread_id = thread_id or f"sesion-{uuid.uuid4().hex[:8]}"
    2. cfg = {"configurable": {"thread_id": thread_id}}
    3. resultado = orquestador.invoke(
           {"messages": [{"role": "user", "content": pregunta}]}, cfg
       )
    4. return resultado
    """
    raise NotImplementedError


if __name__ == "__main__":
    # TODO: prueba manual rapida, ej.
    # print(extraer_texto(consultar("Cual es el precio del Patito Pro 2026?")["messages"][-1].content))
    pass
