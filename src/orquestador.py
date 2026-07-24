"""
Orquestador del sistema: un unico agente LangChain (create_agent) que
decide, segun la pregunta del usuario, que tool(s) invocar.

No hay clasificador propio ni grafo manual: el ruteo vive en
SYSTEM_PROMPT y en las docstrings de cada tool (el LLM las lee para
decidir). Responsable: Matias
"""

import uuid
from types import SimpleNamespace   

from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

from src import config
from src.tools.catalogo_tools import consultar_catalogo
from src.tools.politicas_tools import consultar_politicas
from src.tools.proceso_crm_tools import consultar_proceso_crm
from src.tools.imagen_tools import analizar_imagen_producto
from src.tools.accion_tools import registrar_oportunidad, obtener_oportunidades, actualizar_oportunidad

TOOLS = [
    consultar_catalogo,
    consultar_politicas,
    consultar_proceso_crm,
    analizar_imagen_producto,
    registrar_oportunidad,
    obtener_oportunidades,
    actualizar_oportunidad,
]

SYSTEM_PROMPT = """Eres el Agente Orquestador de Patito S.A. Tu objetivo es analizar las consultas de los usuarios, recuperar información usando herramientas especializadas y sintetizar una respuesta completa y precisa.

### 1. SELECCIÓN DE HERRAMIENTAS
Evalúa la consulta y usa las herramientas según estas reglas:

* **Catálogo/Precios:** Para detalles de productos, especificaciones, precios o stock.
* **Políticas/Descuentos:** Para niveles de descuento, crédito, plazos, garantías o devoluciones.
* **Proceso de Ventas/CRM:** Para procedimientos internos, cómo registrar ventas o uso del CRM.
* **Análisis de Imagen:** Úsala EXCLUSIVAMENTE si el usuario proporciona una ruta de imagen o pide identificar un producto visualmente.
* **Registrar Oportunidad:** Úsala cuando el usuario quiera registrar una venta. Requiere TODOS estos datos: cliente, producto, cantidad, precio_con_descuento, condicion_pago, monto_total, orden_compra, datos_facturacion, fecha_cierre, fecha_entrega.
* **Obtener Oportunidades:** Úsala para ver oportunidades registradas.
* **Actualizar Oportunidad:** Úsala para cambiar estado de una oportunidad.

### 2. CONSULTAS COMPUESTAS
Si el usuario hace una pregunta que abarca múltiples dominios, DEBES invocar TODAS las herramientas necesarias.

### 3. RECHAZO FUERA DE DOMINIO
Si la consulta no tiene relación con productos, políticas, procesos o registro de ventas, NO uses herramientas.

### 4. TRAZABILIDAD
Agrupa las fuentes consultadas al final con formato: [Fuente: NOMBRE | Secciones: X, Y]
"""


llm = ChatGoogleGenerativeAI(model=config.MODELO_LLM, temperature=0)
memoria = InMemorySaver()


orquestador = create_agent(
    model=llm,
    tools=TOOLS,
    system_prompt=SYSTEM_PROMPT,
    checkpointer=memoria,
)


def extraer_texto(content) -> str:
    """Gemini a veces devuelve el content como una lista de bloques
    (texto + firmas de 'thinking'). Aplanar a texto plano.
    """
    if isinstance(content, str):
        return content
    
    if isinstance(content, list):
        texto_plano = ""
        for bloque in content:
            if isinstance(bloque, dict) and "text" in bloque:
                texto_plano += bloque["text"]
            elif isinstance(bloque, str):
                texto_plano += bloque
        return texto_plano
        
    return str(content)


def consultar(pregunta: str, ruta_imagen: str | None = None, thread_id: str | None = None) -> dict:
    """Invoca al orquestador para una consulta."""
    thread_id = thread_id or f"sesion-{uuid.uuid4().hex[:8]}"
    cfg = {"configurable": {"thread_id": thread_id}}
    
    mensaje_usuario = pregunta
    if ruta_imagen:
        mensaje_usuario = f"{pregunta}\n\n[NOTA DEL SISTEMA: El usuario ha adjuntado una imagen ubicada en la ruta: {ruta_imagen}]"
        
    try:
        resultado = orquestador.invoke(
            {"messages": [{"role": "user", "content": mensaje_usuario}]}, cfg
        )
        resultado["thread_id"] = thread_id 
        return resultado
    except Exception as e:
        error_msg = f"Lo siento, estoy experimentando problemas técnicos temporales para procesar tu consulta. (Detalle técnico: {str(e)})"
    
        mensaje_simulado = SimpleNamespace(content=error_msg)
        return {
            "messages": [mensaje_simulado],
            "thread_id": thread_id  
        }


if __name__ == "__main__":
    print("--- PRUEBA 1: Consulta de Catálogo ---")
    res_1 = consultar("¿Cuál es el precio del Patito Pro 2026?")
    print(extraer_texto(res_1["messages"][-1].content))
    print("\n" + "="*50 + "\n")