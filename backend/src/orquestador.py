"""
Orquestador del sistema Patito S.A.

Es un unico agente de LangChain (create_agent) que recibe la pregunta del
usuario y decide que herramienta(s) invocar: consultas RAG (catalogo,
politicas, proceso CRM), analisis de imagen, o registro/actualizacion de
oportunidades de venta. El ruteo no esta programado a mano: vive en el
SYSTEM_PROMPT y en las docstrings de cada tool, que el LLM lee para
decidir cual usar. Al final, agrupa las etiquetas de fuente de cada tool
de consulta en un bloque de trazabilidad.
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
* **Análisis de Imagen:** Úsala EXCLUSIVAMENTE si el mensaje del usuario indica que hay una imagen adjunta (base64) para analizar.
* **Registrar Oportunidad:** Úsala cuando el usuario quiera registrar una nueva oportunidad de venta. Solo requiere cliente, producto y cantidad. NO exijas precio, descuento, condición de pago, orden de compra ni fechas en este paso — esos datos se completan después, al marcar la oportunidad como ganada.
* **Obtener Oportunidades:** Úsala para ver oportunidades registradas. Opcional: filtrar por cliente.
* **Actualizar Oportunidad:** Úsala para cambiar estado de una oportunidad (abierta, ganada, perdida). Si el usuario pide marcarla como "ganada" y en su mensaje incluye datos de cierre (precio con descuento, condición de pago, monto total, orden de compra, datos de facturación, fecha de cierre, fecha de entrega), pásaselos todos a la tool en la misma invocación.

### 2. CONSULTAS COMPUESTAS
Si el usuario hace una pregunta que abarca múltiples dominios (ej. precio Y política Y registro en CRM), DEBES invocar TODAS las herramientas necesarias para recopilar el contexto completo ANTES de generar tu respuesta final.

REGLA CRÍTICA: a cada herramienta pásale ÚNICAMENTE la sub-pregunta correspondiente a
su dominio, NO la pregunta completa del usuario tal cual la escribió. Extrae el nombre
exacto del producto o concepto relevante y formula una sub-pregunta específica para
cada tool.

Ejemplo — pregunta del usuario: "Un cliente nuevo quiere 50 unidades del Patito Pro
2026 a crédito con descuento especial, ¿cuál es el precio, el descuento, las
condiciones de crédito y qué debo registrar en el CRM?"

Invocaciones correctas:
  consultar_catalogo("precio de lista y disponibilidad del Patito Pro 2026")
  consultar_politicas("descuento máximo autorizado y condiciones de crédito para un cliente nuevo")
  consultar_proceso_crm("qué datos se deben registrar en el CRM al crear una oportunidad de venta")

NUNCA pases la pregunta completa y sin recortar a las tres herramientas: eso degrada
la búsqueda semántica de cada una.

### 3. FLUJO DE REGISTRO Y CIERRE DE OPORTUNIDAD
Este flujo tiene dos momentos distintos, según la sección 2 y la sección 3 del Manual
de Proceso de Ventas y CRM:

**Registro inicial (sección 2):** cuando el usuario quiere crear una nueva
oportunidad, invoca registrar_oportunidad solo con cliente, producto y cantidad.
No pidas ni exijas precio, descuento, condición de pago, orden de compra, datos de
facturación ni fechas en este paso — son opcionales al registrar.

**Cierre como ganada (sección 3):** cuando el usuario quiera marcar una oportunidad
existente como "ganada", invoca actualizar_oportunidad con id_oportunidad,
nuevo_estado="ganada", y todos los datos de cierre que el usuario haya
proporcionado (precio_con_descuento, condicion_pago, monto_total, orden_compra,
datos_facturacion, fecha_cierre, fecha_entrega). La tool validará internamente si
faltan datos y te lo indicará — en ese caso, pide al usuario que complete
específicamente los campos que la tool señale como faltantes, sin inventarlos.

Si el usuario quiere confirmar producto y precio antes de registrar o cerrar,
puedes consultar catálogo; si quiere validar el nivel de autorización de un
descuento, puedes consultar políticas.

### 4. RECHAZO FUERA DE DOMINIO
Si la consulta no tiene relación con productos, políticas, procesos o registro de ventas de Patito S.A., NO uses herramientas. Responde exactamente: "Lo siento, mi alcance se limita exclusivamente a los productos, políticas, procesos comerciales y registro de oportunidades de Patito S.A."

### 5. TRAZABILIDAD OBLIGATORIA (FUENTES Y SECCIONES)
Las herramientas de consulta (RAG) — catálogo, políticas y proceso CRM — incluirán automáticamente al final de su respuesta una etiqueta de metadatos con el formato exacto: `[Fuente: NOMBRE_FUENTE | Secciones: X, Y]`. Las herramientas de acción (registrar, obtener o actualizar oportunidades) NO consultan la base documental y por lo tanto no incluyen esta etiqueta — es correcto que no la tengan.

Tu obligación estricta es localizar estas etiquetas dentro de las respuestas que te devuelvan las herramientas de consulta que hayas usado, y agruparlas al final de tu respuesta definitiva en un bloque con el siguiente formato exacto:

**Fuentes consultadas:**
- NOMBRE_FUENTE_1 | Secciones: X, Y
- NOMBRE_FUENTE_2 | Secciones: X, Y

Si solo usaste una herramienta de consulta, el bloque debe tener una sola línea. Si no usaste ninguna herramienta de consulta (por ejemplo, si respondiste directamente por estar fuera de dominio, o si solo usaste una herramienta de acción), omite el bloque de fuentes por completo. No inventes, omitas ni alteres las secciones o fuentes indicadas por las herramientas.
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


def consultar(pregunta: str, thread_id: str | None = None) -> dict:
    """Invoca al orquestador para una consulta.

    El analisis de imagen ya NO pasa por aqui: el endpoint /analizar-imagen
    en main.py llama directamente a analizar_imagen_producto.invoke(...).
    Esta funcion solo maneja preguntas de texto.
    """
    thread_id = thread_id or f"sesion-{uuid.uuid4().hex[:8]}"
    cfg = {"configurable": {"thread_id": thread_id}}

    try:
        resultado = orquestador.invoke(
            {"messages": [{"role": "user", "content": pregunta}]}, cfg
        )
        resultado["thread_id"] = thread_id
        return resultado
    except Exception as e:
        error_msg = f"Error técnico: {str(e)}"
        return {
            "messages": [SimpleNamespace(content=error_msg)],
            "thread_id": thread_id
        }