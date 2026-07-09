"""
Interfaz REST del sistema. Expone el orquestador via FastAPI para que
n8n, un futuro frontend web o una app de escritorio puedan consumirlo
sin acoplarse a la logica interna de LangChain.
Responsable: Vanessa

Diseno pensado a futuro:
- Web: cualquier frontend (React, etc.) consume este mismo endpoint.
- Desktop: un wrapper (Electron/Tauri) o un cliente Python puede llamar
  a esta misma API en localhost, o empaquetarla junto al backend.
Regla: nada de logica de negocio aqui, solo I/O HTTP. Toda la logica
vive en src/orquestador.py y src/tools/.
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
    # TODO: agregar trazabilidad -> tools usadas, fuentes citadas
    # (revisar resultado["messages"] para extraer tool_calls, como en
    # _imprimir_pasos de la practica 6)


@app.post("/consultar", response_model=ConsultaResponse)
def endpoint_consultar(payload: ConsultaRequest):
    """TODO:
    1. resultado = consultar(payload.pregunta, payload.thread_id)
    2. texto = extraer_texto(resultado["messages"][-1].content)
    3. thread_id_usado = ... (el que se uso o genero en consultar())
    4. return ConsultaResponse(respuesta=texto, thread_id=thread_id_usado)
    """
    raise NotImplementedError


@app.get("/health")
def health():
    return {"status": "ok"}
