"""
Pruebas del orquestador.
TODO: pensar 3-4 casos minimos:
1. Pregunta de catalogo -> debe usar la tool consultar_catalogo.
2. Pregunta de politicas -> debe usar consultar_politicas.
3. Pregunta mixta (catalogo + politicas + CRM) -> debe encadenar varias tools.
4. Pregunta fuera de alcance -> debe responder que no tiene informacion,
   sin inventar.

Pista para verificar que tool se uso: revisar
resultado["messages"][i].tool_calls, igual que _imprimir_pasos en la
practica 6.
"""

from src.orquestador import consultar


def test_pregunta_catalogo():
    raise NotImplementedError


def test_pregunta_fuera_de_alcance():
    raise NotImplementedError


if __name__ == "__main__":
    test_pregunta_catalogo()
    test_pregunta_fuera_de_alcance()
    print("Pruebas de orquestador OK")
