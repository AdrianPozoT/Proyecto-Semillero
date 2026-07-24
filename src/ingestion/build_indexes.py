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
    """Divide el texto en un chunk por seccion numerada de nivel 1 (1., 2., ...)."""
    patron = re.compile(r"^\d+\.\s", re.MULTILINE)
    posiciones = [m.start() for m in patron.finditer(texto)]
    
    if not posiciones: 
        return [texto.shrip()]  # Si no hay secciones numeradas, devolvemos el texto completo como un solo chunk.
    
    chunks = []
    for i, inicio in enumerate(posiciones):
        fin = posiciones[i + 1] if i + 1 < len(posiciones) else len(texto)
        chunk = texto[inicio:fin].strip()
        if chunk:  # Solo agregamos el chunk si no está vacío
            chunks.append(chunk)
    return chunks
    

def construir_indice(nombre_agente: str, ruta_documento) -> None:
    """Chunkea, embebe y guarda en Chroma el indice de un agente."""
    
    texto = ruta_documento.read_text(encoding="utf-8")
    chunks = chunkear_por_seccion(texto)
    embeddings = GoogleGenerativeAIEmbeddings(model=config.MODELO_EMBEDDING)

    metadatas = []
    for chunk in chunks:
        titulo_seccion = chunk.split("\n")[0].strip()
        metadatas.append({"seccion": titulo_seccion, "fuente": ruta_documento.name})

    Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        metadatas=metadatas,
        collection_name=nombre_agente,
        persist_directory=str(config.VECTORSTORE_DIR / nombre_agente),
    )
    print(f"  -> {len(chunks)} chunks generados para '{nombre_agente}'.")


def main():
    """Construye el indice de los tres agentes de lectura."""
    for nombre_agente, ruta in config.DOCUMENTOS.items():
        print(f"[{nombre_agente}] Indexando {ruta.name}...")
        construir_indice(nombre_agente, ruta)
    print("Todos los indices generados.")


if __name__ == "__main__":
    main()
