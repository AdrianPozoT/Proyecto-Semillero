"""
Pruebas del API.
Ejecutar con: pytest test/test_api.py -v
"""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health():
    """Verifica que el servidor está activo."""
    response = client.get("/health")
    
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    print("✅ Test 1: Health check OK")


def test_consultar_catalogo():
    """Consulta sobre catálogo."""
    payload = {
        "pregunta": "¿Cuál es el precio del Patito Pro?",
        "thread_id": None
    }
    
    response = client.post("/consultar", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "respuesta" in data
    assert "thread_id" in data
    assert len(data["respuesta"]) > 0
    
    print("✅ Test 2: Consultar catálogo OK")


def test_obtener_oportunidades():
    """Obtiene oportunidades."""
    response = client.get("/oportunidades")
    
    assert response.status_code == 200
    data = response.json()
    assert "oportunidades" in data
    
    print("✅ Test 3: Obtener oportunidades OK")


def test_registrar_oportunidad():
    """Registra una oportunidad."""
    payload = {
        "cliente": "Acme",
        "producto": "Patito Pro",
        "cantidad": 5,
        "precio_con_descuento": 1169.1,
        "condicion_pago": "30 dias",
        "monto_total": 5845.5,
        "orden_compra": "OC-2026-001",
        "datos_facturacion": "NIT 12345",
        "fecha_cierre": "2026-07-30",
        "fecha_entrega": "2026-08-05",
    }
    
    response = client.post("/registrar-oportunidad", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "mensaje" in data
    
    print("✅ Test 4: Registrar oportunidad OK")


if __name__ == "__main__":
    print("🧪 Pruebas del API")
    print("="*70)
    
    test_health()
    test_consultar_catalogo()
    test_obtener_oportunidades()
    test_registrar_oportunidad()
    
    print("="*70)
    print("✅ TODAS LAS PRUEBAS PASARON")