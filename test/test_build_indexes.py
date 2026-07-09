"""
Pruebas para el modulo de ingestion.
TODO: verificar, para cada documento en config.DOCUMENTOS, que:
1. chunkear_por_seccion() devuelve al menos 1 chunk.
2. construir_indice() crea la carpeta del vectorstore correspondiente.
Mismo patron que usaron en test/ingestion/test_build_indexes.py antes.
"""

from src.ingestion.build_indexes import chunkear_por_seccion, construir_indice
from src import config


def test_chunkear_por_seccion():
    raise NotImplementedError


def test_construir_indice_crea_vectorstore():
    raise NotImplementedError


if __name__ == "__main__":
    test_chunkear_por_seccion()
    test_construir_indice_crea_vectorstore()
    print("Pruebas de ingestion OK")
