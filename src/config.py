"""
Configuracion global del proyecto Patito S.A.
Carga variables de entorno y define rutas y modelos usados por todo el sistema.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Rutas base 
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
VECTORSTORE_DIR = BASE_DIR / "vectorstores"

# Modelos Gemini 
MODELO_LLM = "gemini-3.1-flash-lite"

#API Key 
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError(
        "Falta GOOGLE_API_KEY. Copia .env.example a .env y pega tu key de "
        "https://aistudio.google.com/apikey"
    )

# Documentos y colecciones (uno por agente de lectura) ---
DOCUMENTOS = {
    "catalogo": DATA_DIR / "01_Catalogo_Productos_Precios.txt",
    "politicas": DATA_DIR / "02_Politicas_Comerciales_Descuentos_Credito.txt",
    "proceso_crm": DATA_DIR / "03_Proceso_Ventas_CRM.txt",
}

TOP_K = 3  
