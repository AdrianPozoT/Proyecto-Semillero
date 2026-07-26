"""
Test: Analiza imágenes generadas y reales del proyecto.
"""

import base64
from pathlib import Path

from src.tools.imagen_tools import analizar_imagen_producto


def analizar_imagen(ruta: Path):
    """Analiza una imagen desde archivo."""
    
    if not ruta.exists():
        print(f"❌ Archivo no encontrado: {ruta}")
        return
    
    with open(ruta, "rb") as f:
        imagen_bytes = f.read()
    
    imagen_base64 = base64.b64encode(imagen_bytes).decode()
    
    print(f"\n📸 Imagen: {ruta.name}")
    print(f"✓ Tamaño: {len(imagen_bytes)} bytes")
    print(f"🔄 Analizando...\n")
    
    resultado = analizar_imagen_producto.invoke({
        "imagen_base64": imagen_base64
    })
    
    print("="*70)
    print(resultado)
    print("="*70)


if __name__ == "__main__":
    
    print("\n" + "="*70)
    print("PRUEBA: ANÁLISIS DE IMÁGENES (GENERADAS Y REALES)")
    print("="*70)
    
    # Imágenes a analizar (generadas + reales)
    imagenes = [

        #! Descomentar si se ejecuta antes el test_imagen_generator
        #Path("data/imagenes_prueba/producto.png"),                      # Generada
        #Path("data/imagenes_prueba/cotizacion.png"),                    # Generada
        #Path("data/imagenes_prueba/lista_precios.png"),                 # Generada
        Path("data/imagenes_prueba/lista_de_precios_patito_s.a.png"),   # Real
        Path("data/imagenes_prueba/cotizacion_patito_s.a.png"),         # Real
    ]
    
    # Analizar cada imagen
    for ruta in imagenes:
        analizar_imagen(ruta)
    
    print("\n" + "="*70)
    print("✅ PRUEBAS COMPLETADAS")
    print("="*70 + "\n")