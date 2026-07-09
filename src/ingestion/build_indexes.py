"""
Ingestion: lee cada documento, lo chunkea por seccion y genera su indice
en Chroma con embeddings de Gemini.

Responsable: Matias. Esto NO es logica nueva -- ya lo construyeron y
probaron en la Fase 1 del proyecto. Aqui solo se porta a la nueva
estructura de carpetas (src/ingestion/, vectorstores/<agente>/).
"""

import re

from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src import config


def chunkear_por_seccion(texto: str) -> list[str]:
    """Divide el texto en un chunk por seccion numerada de nivel 1 (1., 2., ...).

    TODO: portar la funcion que ya tenian funcionando. Recordatorio del
    patron (igual al taller 5 / practica 6):
    - buscar las cabeceras con una regex tipo r"^\\d+\\.\\s" en modo MULTILINE
    - cada chunk va desde una cabecera hasta el inicio de la siguiente
    """
    raise NotImplementedError


def construir_indice(nombre_agente: str, ruta_documento) -> None:
    """Chunkea, embebe y guarda en Chroma el indice de un agente.

    TODO:
    1. Leer el archivo de texto (ruta_documento.read_text(encoding="utf-8")).
    2. chunks = chunkear_por_seccion(texto)
    3. embeddings = GoogleGenerativeAIEmbeddings(model=config.MODELO_EMBEDDING)
    4. Chroma.from_texts(
           texts=chunks,
           embedding=embeddings,
           metadatas=[{"seccion": i, "fuente": ruta_documento.name} for i in range(len(chunks))],
           collection_name=nombre_agente,
           persist_directory=str(config.VECTORSTORE_DIR / nombre_agente),
       )
    5. Imprimir cuantos chunks se generaron (para verificar en consola).
    """
    raise NotImplementedError


def main():
    """Construye el indice de los tres agentes de lectura."""
    for nombre_agente, ruta in config.DOCUMENTOS.items():
        print(f"[{nombre_agente}] Indexando {ruta.name}...")
        construir_indice(nombre_agente, ruta)
    print("Todos los indices generados.")


if __name__ == "__main__":
    main()
