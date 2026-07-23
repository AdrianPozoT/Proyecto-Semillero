"""
Pruebas para la tool de accion (registrar_oportunidad).
Casos:
1. Faltan datos obligatorios -> no escribe nada, devuelve cuales faltan.
2. Datos completos -> escribe la linea y devuelve el ID asignado (OPP-0001).
3. Segundo registro -> el ID se incrementa (OPP-0002).
"""


from pathlib import Path

from src.tools import accion_tools

REGISTRO_PATH = Path("registro_oportunidades.txt")


def test_faltan_datos_no_registra():
    """Intenta registrar SIN cliente."""
    
    resultado = accion_tools.registrar_oportunidad.invoke({
        "cliente": "",
        "producto": "Patito Pro",
        "cantidad": 5,
        "precio_con_descuento": 1169.1,
        "condicion_pago": "30 dias",
        "monto_total": 5845.5,
        "orden_compra": "OC-2026-001",
        "datos_facturacion": "NIT 12345",
        "fecha_cierre": "2026-07-30",
        "fecha_entrega": "2026-08-05",
    })
    
    assert "No se registro" in resultado
    assert "cliente" in resultado
    print("✅ Test 1: Rechaza datos incompletos")


def test_datos_completos_registra_con_id():
    """Registra con todos los datos."""
    
    if REGISTRO_PATH.exists():
        REGISTRO_PATH.unlink()
    
    resultado = accion_tools.registrar_oportunidad.invoke({
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
    })
    
    assert "OPP-0001" in resultado
    assert REGISTRO_PATH.exists()
    
    contenido = REGISTRO_PATH.read_text(encoding="utf-8")
    assert "OPP-0001" in contenido
    assert "cliente=Acme" in contenido
    
    print("✅ Test 2: Registra con ID OPP-0001")


def test_segundo_registro_incrementa_id():
    """El segundo registro tiene ID OPP-0002."""
    
    if REGISTRO_PATH.exists():
        REGISTRO_PATH.unlink()
    
    accion_tools.registrar_oportunidad.invoke({
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
    })
    
    resultado2 = accion_tools.registrar_oportunidad.invoke({
        "cliente": "TechCorp",
        "producto": "Patito Lite",
        "cantidad": 10,
        "precio_con_descuento": 584.1,
        "condicion_pago": "contado",
        "monto_total": 5841.0,
        "orden_compra": "OC-2026-002",
        "datos_facturacion": "NIT 67890",
        "fecha_cierre": "2026-07-25",
        "fecha_entrega": "2026-08-01",
    })
    
    assert "OPP-0002" in resultado2
    print("✅ Test 3: Incrementa ID a OPP-0002")


def test_actualizar_estado():
    """Actualiza estado de abierta a ganada."""
    
    if REGISTRO_PATH.exists():
        REGISTRO_PATH.unlink()
    
    accion_tools.registrar_oportunidad.invoke({
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
    })
    
    resultado = accion_tools.actualizar_oportunidad.invoke({
        "id_oportunidad": "OPP-0001",
        "nuevo_estado": "ganada"
    })
    
    assert "ganada" in resultado
    
    contenido = REGISTRO_PATH.read_text(encoding="utf-8")
    assert "estado=ganada" in contenido
    
    print("✅ Test 4: Actualiza estado correctamente")


if __name__ == "__main__":
    print("🧪 Pruebas de accion_tools")
    print("="*70)
    
    try:
        test_faltan_datos_no_registra()
        test_datos_completos_registra_con_id()
        test_segundo_registro_incrementa_id()
        test_actualizar_estado()
        
        print("="*70)
        print("✅ TODAS LAS PRUEBAS PASARON")
        
        if REGISTRO_PATH.exists():
            print(f"\n📁 Archivo: {REGISTRO_PATH.absolute()}")
            print("\n📋 Contenido:")
            print(REGISTRO_PATH.read_text(encoding="utf-8"))
        
    except AssertionError as e:
        print(f"❌ FALLÓ: {e}")
        import traceback
        traceback.print_exc()