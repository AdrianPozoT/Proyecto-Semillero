import base64
from datetime import datetime
from pathlib import Path
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src import config

llm = ChatGoogleGenerativeAI(model=config.MODELO_LLM, temperature=0)

IMAGENES_DIR = Path("data/imagenes_consultadas")
IMAGENES_DIR.mkdir(parents=True, exist_ok=True)

HISTORIAL_PATH = Path("imagenes_historial.txt")


@tool
def analizar_imagen_producto(imagen_base64: str) -> str:
    """Identifica y extrae la informacion IMPRESA en una imagen de
    producto, cotizacion o lista de precios de Patito S.A. usando
    Gemini Vision. Guarda la imagen y registra en historial.

    Esta tool NO verifica precio de lista ni disponibilidad vigentes:
    solo reporta lo que aparece en la imagen. Si el usuario pide
    ademas confirmar precio de lista o disponibilidad actual, el
    orquestador debe invocar tambien consultar_catalogo con el nombre
    de producto identificado aqui.

    Args:
        imagen_base64: String con imagen codificada en base64
    """

    if not imagen_base64:
        return "Error: No se recibió imagen"

    try:
        imagen_bytes = base64.b64decode(imagen_base64)
    except Exception as e:
        return f"Error al decodificar imagen: {str(e)}"

    prompt = (
        "Eres un asistente que analiza documentos de Patito S.A. "
        "Identifica el tipo de documento: "
        "'PRODUCTO' (ficha individual), "
        "'COTIZACION' (cotización a cliente) o "
        "'LISTA_PRECIOS' (listado de productos). "
        "\n\n"
        "Responde EXACTAMENTE con este formato:\n\n"
        "Tipo de documento: <PRODUCTO / COTIZACION / LISTA_PRECIOS>\n\n"
        "Si es PRODUCTO:\n"
        "Nombre del producto: ...\n"
        "SKU: ...\n"
        "Código de proveedor: ...\n"
        "Cantidad: ...\n"
        "Precio unitario (según imagen): ...\n"
        "Precio total (según imagen): ...\n\n"
        "Si es COTIZACION:\n"
        "Cliente: ...\n"
        "Número de cotización: ...\n"
        "Fecha: ...\n"
        "Vendedor: ...\n"
        "Productos incluidos: ...\n"
        "Total (según imagen): ...\n\n"
        "Si es LISTA_PRECIOS:\n"
        "Por cada producto:\n"
        "Nombre del producto: ...\n"
        "Precio unitario (según imagen): ...\n"
        "Disponibilidad (según imagen): ...\n\n"
        "IMPORTANTE: el nombre de cada producto debe escribirse EXACTAMENTE "
        "como aparece impreso (ej. 'Patito Pro 2026'), sin abreviar ni "
        "traducir, para que pueda buscarse luego en el catálogo oficial. "
        "No inventes datos. Si falta información, escribe 'N/A'. "
        "Aclara que los precios reportados son 'según la imagen', no una "
        "confirmación de precio de lista vigente."
    )

    mensaje = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{imagen_base64}"
                }
            }
        ]
    )

    try:
        resultado = llm.invoke([mensaje]).content
    except Exception as e:
        return f"Error al analizar imagen: {str(e)}"

    # CONVERTIR RESULTADO A STRING (Gemini a veces retorna lista)
    if isinstance(resultado, list):
        resultado_str = ""
        for bloque in resultado:
            if isinstance(bloque, dict) and "text" in bloque:
                resultado_str += bloque["text"]
            elif isinstance(bloque, str):
                resultado_str += bloque
        resultado = resultado_str
    else:
        resultado = str(resultado)

    # GUARDAR IMAGEN CON TIMESTAMP
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"imagen_{timestamp}.png"
    ruta_guardada = IMAGENES_DIR / nombre_archivo

    try:
        with open(ruta_guardada, "wb") as f:
            f.write(imagen_bytes)
        print(f"✓ Imagen guardada: {ruta_guardada}")
    except Exception as e:
        print(f"✗ Error al guardar imagen: {e}")

    # REGISTRAR EN HISTORIAL
    resumen = resultado[:100] if len(resultado) > 100 else resultado
    resumen_limpio = resumen.replace('\n', ' ').replace('|', '-')
    registro = f"{timestamp} | {nombre_archivo} | {resumen_limpio}...\n"

    try:
        with open(HISTORIAL_PATH, "a", encoding="utf-8") as f:
            f.write(registro)
        print(f"✓ Historial actualizado")
    except Exception as e:
        print(f"✗ Error al guardar historial: {e}")

    return resultado