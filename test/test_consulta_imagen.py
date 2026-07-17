import os
from src.tools.imagen_tools import analizar_imagen_producto

CARPETA_IMAGENES = os.path.join(os.path.dirname(__file__), "..", "data", "imagenes_prueba")

ruta = os.path.join(CARPETA_IMAGENES, "producto.png")
resultado = analizar_imagen_producto.invoke(ruta)
print("------RESULTADO PRODUCTO------\n")
print(resultado)
print("------FIN RESULTADO PRODUCTO------\n\n")

ruta = os.path.join(CARPETA_IMAGENES, "cotizacion.png")
resultado = analizar_imagen_producto.invoke(ruta)
print("------RESULTADO COTIZACION------\n")
print(resultado)
print("------FIN RESULTADO COTIZACION------\n\n")

ruta = os.path.join(CARPETA_IMAGENES, "lista_precios.png")
resultado = analizar_imagen_producto.invoke(ruta)
print("------RESULTADO LISTA DE PRECIOS------\n")
print(resultado)
print("------FIN RESULTADO LISTA DE PRECIOS------\n\n")