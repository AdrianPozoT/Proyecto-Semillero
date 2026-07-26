"""
Script de prueba: compara gemini-2.5-flash vs gemini-3.1-flash-lite
en la tarea de leer imágenes (analizar_imagen_producto).

No modifica config.py -- crea sus propias instancias de LLM aparte,
solo para este experimento.
"""
import time
import base64
from dotenv import load_dotenv  
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()
# 1: Instancias de los modelos
llm_flash = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
llm_flash_lite = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0)

# 2: Lista de imágenes a probar
IMAGENES = [
   "data/imagenes_prueba/cotizacion.png",
"data/imagenes_prueba/lista_precios.png",
"data/imagenes_prueba/producto.png"
]

# 3: Prompt idéntico al de producción
# OJO: Reemplaza este texto si tu prompt real en imagen_tools.py es más largo.
prompt = (
        "Eres un asistente que analiza documentos de Patito S.A. "
        "Primero identifica a que tipo de documento corresponde la imagen: "
        "'PRODUCTO' (ficha individual de un producto), "
        "'COTIZACION' (cotizacion a un cliente) o "
        "'LISTA_PRECIOS' (listado de varios productos con precios). "
        "Analiza SOLO como ese tipo de documento. No mezcles los otros formatos.\n\n"
        "Responde EXACTAMENTE con este formato:\n\n"
        "Tipo de documento: <PRODUCTO / COTIZACION / LISTA_PRECIOS>\n\n"
        "Si es PRODUCTO, incluye unicamente:\n"
        "Nombre del producto: ...\n"
        "SKU: ...\n"
        "Codigo de proveedor: ...\n"
        "Cantidad: ...\n"
        "Precio unitario: ...\n"
        "Precio total: ...\n\n"
        "Si es COTIZACION, incluye unicamente:\n"
        "Nombre del cliente: ...\n"
        "Numero de cotizacion: ...\n"
        "Fecha: ...\n"
        "Vendedor: ...\n"
        "Total: ...\n\n"
        "Si es LISTA_PRECIOS, incluye unicamente, por cada producto encontrado:\n"
        "Nombre del producto: ...\n"
        "Precio unitario: ...\n"
        "Precio total: ...\n\n"
        "No inventes informacion que no este en la imagen. "
        "Si un dato no aparece, escribe 'N/A'. "
        "No incluyas las secciones de los otros tipos de documento."
    )


def analizar_con_modelo(llm, ruta_imagen: str) -> dict:
    """Le manda UNA imagen a UN modelo, mide el tiempo y devuelve resultados."""
    
    # 1. Leer el archivo en base64
    with open(ruta_imagen, "rb") as image_file:
        imagen_data = base64.b64encode(image_file.read()).decode("utf-8")
    
    # 2. Armar el HumanMessage idéntico a producción
    mensaje = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": f"data:image/png;base64,{imagen_data}"}
        ]
    )

    # 3. Anotar hora de inicio
    inicio = time.time()
    
    # 4. Llamar al modelo
    respuesta = llm.invoke([mensaje])
    
    # 5. Anotar hora de fin
    fin = time.time()
    
    # 6. Retornar métricas y datos
    return {
        "modelo": llm.model,
        "imagen": ruta_imagen,
        "tiempo_segundos": fin - inicio,
        "respuesta": respuesta.content,
    }

def main():
    """Ejecuta el benchmark cruzando imágenes y modelos."""
    resultados = []
    modelos = [llm_flash, llm_flash_lite]

    print("Iniciando benchmark de modelos de visión...\n")

    # Ejecutar la prueba: doble for
    for img in IMAGENES:
        for modelo in modelos:
            print(f"Procesando {img} con {modelo.model}...")
            try:
                resultado = analizar_con_modelo(modelo, img)
                resultados.append(resultado)
            except Exception as e:
                print(f"Error procesando {img} con {modelo.model}: {e}")

    # Imprimir resultados agrupados por imagen para facilitar la comparación
    print("\n" + "="*60)
    print("RESULTADOS DEL EXPERIMENTO: FLASH VS FLASH-LITE")
    print("="*60)

    for img in IMAGENES:
        print(f"\n📁 ARCHIVO: {img}")
        print("-" * 60)
        
        # Filtrar los resultados correspondientes a esta imagen
        resultados_imagen = [r for r in resultados if r["imagen"] == img]
        
        for res in resultados_imagen:
            print(f"🤖 Modelo: {res['modelo']}")
            print(f"⏱️ Tiempo: {res['tiempo_segundos']:.2f} segundos")
            print(f"📄 Respuesta:\n{res['respuesta']}")
            print("-" * 30)

if __name__ == "__main__":
    main()