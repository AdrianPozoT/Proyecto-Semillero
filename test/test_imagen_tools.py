import os
from PIL import Image, ImageDraw

CARPETA_IMAGENES = os.path.join(os.path.dirname(__file__), "..", "data", "imagenes_prueba")
os.makedirs(CARPETA_IMAGENES, exist_ok=True)


def crear_producto_demo(ruta):
    img = Image.new("RGB", (440, 280), "white")
    d = ImageDraw.Draw(img)
    lineas = [
        "FICHA DE PRODUCTO",
        "-------------------------------",
        "Nombre: Taladro Percutor 750W",
        "SKU: TP-750-BLK",
        "Codigo Proveedor: PRV-4471",
        "Cantidad: 15",
        "Precio Unitario: 45.00",
        "Precio Total: 675.00",
    ]
    y = 20
    for ln in lineas:
        d.text((20, y), ln, fill="black")
        y += 28
    img.save(ruta)
    return ruta


def crear_cotizacion_demo(ruta):
    img = Image.new("RGB", (440, 300), "white")
    d = ImageDraw.Draw(img)
    lineas = [
        "COTIZACION - PATITO S.A.",
        "-------------------------------",
        "Cliente: Constructora Rios S.A.",
        "N Cotizacion: COT-2026-0143",
        "Fecha: 2026-07-10",
        "Vendedor: Ana Torres",
        "-------------------------------",
        "Taladro Percutor x15    675.00",
        "Sierra Circular x5      450.00",
        "-------------------------------",
        "TOTAL USD              1125.00",
    ]
    y = 20
    for ln in lineas:
        d.text((20, y), ln, fill="black")
        y += 26
    img.save(ruta)
    return ruta


def crear_lista_precios_demo(ruta):
    img = Image.new("RGB", (440, 300), "white")
    d = ImageDraw.Draw(img)
    lineas = [
        "LISTA DE PRECIOS - JULIO 2026",
        "-------------------------------",
        "Taladro Percutor 750W",
        "  Precio Unitario: 45.00",
        "  Precio Total: N/A",
        "-------------------------------",
        "Sierra Circular 1200W",
        "  Precio Unitario: 90.00",
        "  Precio Total: N/A",
        "-------------------------------",
        "Amoladora Angular 900W",
        "  Precio Unitario: 38.50",
        "  Precio Total: N/A",
    ]
    y = 20
    for ln in lineas:
        d.text((20, y), ln, fill="black")
        y += 24
    img.save(ruta)
    return ruta


if __name__ == "__main__":
    ruta_producto = crear_producto_demo(os.path.join(CARPETA_IMAGENES, "producto.png"))
    ruta_cotizacion = crear_cotizacion_demo(os.path.join(CARPETA_IMAGENES, "cotizacion.png"))
    ruta_lista = crear_lista_precios_demo(os.path.join(CARPETA_IMAGENES, "lista_precios.png"))

    print("Producto:", ruta_producto)
    print("Cotizacion:", ruta_cotizacion)
    print("Lista de precios:", ruta_lista)