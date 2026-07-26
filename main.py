"""
Interfaz REST del sistema. Expone el orquestador via FastAPI para que
n8n, un futuro frontend web o una app de escritorio puedan consumirlo
sin acoplarse a la logica interna de LangChain.
Responsable: Vanessa
"""

import re
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.orquestador import consultar, extraer_texto

app = FastAPI(title="Patito S.A. - Mesa de Ayuda IA para Ventas")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== MODELOS ====================

class ConsultaRequest(BaseModel):
    pregunta: str
    thread_id: Optional[str] = None


class ConsultaResponse(BaseModel):
    respuesta: str
    thread_id: str


class ConsultaImagenRequest(BaseModel):
    imagen_base64: str
    descripcion: str = ""
    thread_id: Optional[str] = None


# ==================== ENDPOINTS ====================

@app.post("/consultar", response_model=ConsultaResponse)
def endpoint_consultar(payload: ConsultaRequest):
    resultado = consultar(payload.pregunta, thread_id=payload.thread_id)
    texto = extraer_texto(resultado["messages"][-1].content)
    thread_id_usado = resultado["thread_id"]

    return ConsultaResponse(
        respuesta=texto,
        thread_id=thread_id_usado
    )


@app.post("/analizar-imagen")
def endpoint_analizar_imagen(payload: ConsultaImagenRequest):
    """Analiza una imagen y, si la pregunta lo requiere, cruza el
    producto identificado con catálogo y/o políticas comerciales.

    Flujo:
    1. analizar_imagen_producto identifica el producto y extrae lo
       impreso en la imagen (precio, disponibilidad segun la imagen).
    2. Si la descripcion del usuario menciona stock/precio vigente,
       se invoca ademas consultar_catalogo con el nombre exacto del
       producto identificado.
    3. Si la descripcion menciona descuento/credito/garantia, se
       invoca tambien consultar_politicas.
    4. Las respuestas de las tools invocadas se concatenan en un solo
       texto final.
    """

    try:
        if not payload.imagen_base64:
            return {
                "error": "No se recibió imagen",
                "respuesta": "",
                "thread_id": payload.thread_id or "sin-imagen"
            }

        from src.tools.imagen_tools import analizar_imagen_producto
        from src.tools.catalogo_tools import consultar_catalogo
        from src.tools.politicas_tools import consultar_politicas

        # 1. Identificar y extraer lo que dice la imagen
        resultado_imagen = analizar_imagen_producto.invoke({
            "imagen_base64": payload.imagen_base64
        })

        respuesta_final = resultado_imagen
        descripcion = (payload.descripcion or "").lower()

        # 2. Extraer el nombre exacto del producto identificado
        match = re.search(r"Nombre del producto:\s*(.+)", resultado_imagen)
        nombre_producto = match.group(1).strip() if match else None

        partes_extra = []

        # 3. Si la pregunta pide precio/stock/disponibilidad -> catálogo
        pide_catalogo = any(
            palabra in descripcion
            for palabra in ["stock", "disponib", "precio de lista", "precio actual", "vigente"]
        )
        if nombre_producto and pide_catalogo:
            resp_catalogo = consultar_catalogo.invoke({
                "pregunta": f"precio de lista y disponibilidad de {nombre_producto}"
            })
            partes_extra.append(f"**Verificación en catálogo:**\n{resp_catalogo}")

        # 4. Si la pregunta pide descuento/crédito -> políticas
        pide_politicas = any(
            palabra in descripcion
            for palabra in ["descuento", "credito", "crédito", "garantia", "garantía", "devolucion", "devolución"]
        )
        if nombre_producto and pide_politicas:
            resp_politicas = consultar_politicas.invoke({
                "pregunta": f"descuentos y condiciones aplicables para {nombre_producto}"
            })
            partes_extra.append(f"**Verificación en políticas comerciales:**\n{resp_politicas}")

        if partes_extra:
            respuesta_final = resultado_imagen + "\n\n" + "\n\n".join(partes_extra)

        return {
            "respuesta": respuesta_final,
            "imagen_guardada": True,
            "thread_id": payload.thread_id or "sesion-imagen"
        }

    except Exception as e:
        print(f"Error en endpoint análisis: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "respuesta": f"Error al procesar imagen: {str(e)}",
            "thread_id": payload.thread_id or "error"
        }


@app.post("/registrar-oportunidad")
def endpoint_registrar(datos: dict):
    """Registra una oportunidad con los datos minimos del registro
    inicial (seccion 2 del Manual de Proceso de Ventas y CRM): cliente,
    producto y cantidad. Los campos de cierre (precio con descuento,
    condicion de pago, orden de compra, etc.) NO son obligatorios aqui
    -- se completan despues, al marcar la oportunidad como ganada."""

    pregunta = (
        f"Registra una oportunidad: cliente {datos.get('cliente')}, "
        f"producto {datos.get('producto')}, cantidad {datos.get('cantidad')}"
    )

    resultado = consultar(pregunta)
    texto = extraer_texto(resultado["messages"][-1].content)

    return {"mensaje": texto}


@app.post("/actualizar-oportunidad")
def endpoint_actualizar_oportunidad(datos: dict):
    """Actualiza el estado de una oportunidad.

    Si nuevo_estado es 'ganada', el payload puede incluir ademas los
    campos de cierre (precio_con_descuento, condicion_pago,
    monto_total, orden_compra, datos_facturacion, fecha_cierre,
    fecha_entrega). La tool valida que, entre lo ya guardado y lo
    recibido en este payload, esten todos completos antes de aprobar
    el cambio (seccion 3 del Manual de Proceso de Ventas y CRM)."""

    id_oportunidad = datos.get("id_oportunidad")
    nuevo_estado = datos.get("nuevo_estado")

    pregunta = f"Actualiza la oportunidad {id_oportunidad} a estado {nuevo_estado}"

    if nuevo_estado == "ganada":
        campos_cierre = [
            "precio_con_descuento", "condicion_pago", "monto_total",
            "orden_compra", "datos_facturacion", "fecha_cierre", "fecha_entrega",
        ]
        partes = [f"{campo} {datos[campo]}" for campo in campos_cierre if datos.get(campo)]
        if partes:
            pregunta += ", " + ", ".join(partes)

    resultado = consultar(pregunta)
    texto = extraer_texto(resultado["messages"][-1].content)

    return {"mensaje": texto}


@app.get("/oportunidades")
def endpoint_obtener_oportunidades():
    """Obtiene todas las oportunidades registradas, tal cual estan en
    el archivo. Se invoca la tool directamente (sin pasar por el LLM)
    para que el frontend reciba el formato exacto que puede parsear,
    sin riesgo de que el modelo lo reformatee en prosa."""

    from src.tools.accion_tools import obtener_oportunidades

    texto = obtener_oportunidades.invoke({})

    return {"oportunidades": texto}



@app.get("/health")
def health():
    return {"status": "ok", "mensaje": "API funcionando correctamente"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)