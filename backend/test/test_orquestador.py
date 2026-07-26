"""
Pruebas del orquestador.
"""

from src.orquestador import consultar, extraer_texto

def test_pregunta_catalogo():
    # 1: Llama a consultar() con una pregunta real sobre el catálogo
    resultado = consultar("¿Cuál es el precio del Patito Pro 2026?")

    # 2: Extrae el texto de la respuesta final del último mensaje
    ultimo_mensaje = resultado["messages"][-1]
    respuesta = extraer_texto(ultimo_mensaje)

    # 3: Verifica con assert que no esté vacía y contenga palabras clave
    assert respuesta.strip() != "", "La respuesta del orquestador está vacía."
    assert "precio" in respuesta.lower() or "patito" in respuesta.lower(), "La respuesta no menciona el precio ni el producto esperado."

    # 4: Imprime confirmación visual
    print("✅ test_pregunta_catalogo OK")
    print(f"   Respuesta obtenida: {respuesta}\n")


def test_pregunta_fuera_de_alcance():
    # 1: Llama a consultar() con una pregunta fuera de dominio
    resultado = consultar("¿Cuál es la capital de Francia?")

    # 2: Extrae el texto de la respuesta final
    ultimo_mensaje = resultado["messages"][-1]
    respuesta = extraer_texto(ultimo_mensaje)

    # 3: Verifica que la respuesta contenga la regla de rechazo
    # Reemplaza "patito" por la palabra exacta que hayas puesto en tu SYSTEM_PROMPT
    palabra_clave_rechazo = "patito" 
    assert palabra_clave_rechazo in respuesta.lower(), f"El bot no rechazó correctamente la pregunta. Respondió: {respuesta}"

    # Imprime confirmación visual
    print("✅ test_pregunta_fuera_de_alcance OK")
    print(f"   Respuesta de rechazo obtenida: {respuesta}\n")


if __name__ == "__main__":
    print("Iniciando pruebas...\n" + "="*30)
    test_pregunta_catalogo()
    test_pregunta_fuera_de_alcance()
    print("="*30 + "\nTodas las pruebas del orquestador pasaron con éxito. 🚀")