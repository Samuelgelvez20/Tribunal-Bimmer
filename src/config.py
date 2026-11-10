import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
RUTA_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_ENV = RUTA_PROYECTO / ".env"
load_dotenv(RUTA_ENV)

# Rutas estándar del proyecto
RUTA_DATOS = RUTA_PROYECTO / "datos"
RUTA_MODELOS_BMW = RUTA_DATOS / "modelos_bmw.json"
# RUTA_JUGADORES apunta al catálogo de modelos de BMW para compatibilidad retroactiva
RUTA_JUGADORES = RUTA_MODELOS_BMW
RUTA_OPINIONES = RUTA_DATOS / "opiniones.json"

# Detección inteligente de proveedor y claves
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY", "")

# Si la clave de OPENAI_API_KEY tiene prefijo de Google (AQ. o AIza)
if not GOOGLE_KEY and (OPENAI_KEY.startswith("AQ.") or OPENAI_KEY.startswith("AIza")):
    GOOGLE_KEY = OPENAI_KEY

# Proveedor por defecto según claves disponibles
if GOOGLE_KEY and not OPENAI_KEY.startswith("sk-"):
    DEFAULT_PROVIDER = "google"
    DEFAULT_MODEL = os.getenv("LLM_MODEL", "gemini-3.5-flash-lite")
    DEFAULT_API_KEY = GOOGLE_KEY
else:
    DEFAULT_PROVIDER = "openai"
    DEFAULT_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
    DEFAULT_API_KEY = OPENAI_KEY

TEMPERATURE = float(os.getenv("TEMPERATURE", "0.0"))
VERSION_PROMPT = "1.0"
