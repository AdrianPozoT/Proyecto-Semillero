"""
Interfaz REST del sistema. Expone el orquestador via FastAPI para que
n8n, un futuro frontend web o una app de escritorio puedan consumirlo
sin acoplarse a la logica interna de LangChain.
Responsable: Vanessa
"""

from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from src.orquestador import consultar, extraer_texto

app = FastAPI(title="Patito S.A. - Mesa de Ayuda IA para Ventas")


class ConsultaRequest(BaseModel):
    pregunta: str
    thread_id: Optional[str] = None


class ConsultaResponse(BaseModel):
    respuesta: str
    thread_id: str


@app.post("/consultar", response_model=ConsultaResponse)
def endpoint_consultar(payload: ConsultaRequest):
    resultado = consultar(payload.pregunta, payload.thread_id)
    texto = extraer_texto(resultado["messages"][-1].content)
    thread_id_usado = resultado["thread_id"]
    
    return ConsultaResponse(
        respuesta=texto,
        thread_id=thread_id_usado
    )


@app.post("/registrar-oportunidad")
def endpoint_registrar(datos: dict):
    """Registra una oportunidad a través del orquestador."""
    pregunta = (
        f"Registra: cliente {datos.get('cliente')}, "
        f"{datos.get('producto')}, {datos.get('cantidad')} un., "
        f"{datos.get('precio_con_descuento')}, {datos.get('condicion_pago')}, "
        f"{datos.get('monto_total')}, {datos.get('orden_compra')}, "
        f"{datos.get('datos_facturacion')}, {datos.get('fecha_cierre')}, "
        f"{datos.get('fecha_entrega')}"
    )
    
    resultado = consultar(pregunta)
    texto = extraer_texto(resultado["messages"][-1].content)
    
    return {"mensaje": texto}


@app.get("/oportunidades")
def endpoint_obtener_oportunidades():
    """Obtiene todas las oportunidades registradas."""
    resultado = consultar("Muestra todas las oportunidades registradas")
    texto = extraer_texto(resultado["messages"][-1].content)
    
    return {"oportunidades": texto}


@app.get("/health")
def health():
    return {"status": "ok", "mensaje": "API funcionando correctamente"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)