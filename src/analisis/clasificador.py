from typing import Optional
import logging
from langchain_openai import ChatOpenAI
from src.config import DEFAULT_MODEL, DEFAULT_API_KEY, TEMPERATURE
from src.modelos.analisis_opinion import AnalisisOpinion
from src.analisis.prompts import PROMPT_CLASIFICACION
from src.analisis.validador_texto import validar_longitud_opinion

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except Exception:
    ChatGoogleGenerativeAI = None

logger = logging.getLogger("clasificador")


class ClasificadorOpiniones:
    """
    Servicio de clasificación de opiniones mediante cadenas LCEL y salida estructurada Pydantic.
    Admite modelos OpenAI y Google Gemini según configuración y claves disponibles, con
    conmutación por error (fallback) automática ante cuotas agotadas (429/RESOURCE_EXHAUSTED).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = TEMPERATURE,
    ):
        self.model_name = model_name or DEFAULT_MODEL
        self.api_key = api_key or DEFAULT_API_KEY
        self.temperature = temperature

    def _obtener_cadena(self, nombre_modelo: Optional[str] = None):
        if not self.api_key:
            raise ValueError(
                "No se encontró una API Key válida configurada. Define OPENAI_API_KEY o GOOGLE_API_KEY en .env."
            )

        modelo = nombre_modelo or self.model_name
        es_gemini = modelo.startswith("gemini") or self.api_key.startswith("AQ.") or self.api_key.startswith("AIza")

        if es_gemini:
            if ChatGoogleGenerativeAI is None:
                raise ImportError("Para usar modelos Gemini debes tener instalado langchain-google-genai.")
            
            modelo_real = modelo if modelo.startswith("gemini") else "gemini-3.5-flash-lite"
            llm = ChatGoogleGenerativeAI(
                model=modelo_real,
                temperature=self.temperature,
                google_api_key=self.api_key,
                request_timeout=20,
                max_retries=1,
            )
        else:
            llm = ChatOpenAI(
                model=modelo,
                temperature=self.temperature,
                api_key=self.api_key,
                request_timeout=20,
                max_retries=1,
            )

        # Salida estructurada garantizada con Pydantic
        modelo_estructurado = llm.with_structured_output(AnalisisOpinion)
        return PROMPT_CLASIFICACION | modelo_estructurado

    def analizar(
        self,
        nombre_jugador: Optional[str] = None,
        texto_opinion: str = "",
        nombre_modelo: Optional[str] = None,
    ) -> AnalisisOpinion:
        """
        Ejecuta la clasificación sobre una opinión de un modelo de BMW. Valida la longitud antes de llamar al LLM.
        Incluye conmutación por error automática ante cuota excedida (429).
        """
        nombre_objetivo = nombre_modelo or nombre_jugador or "BMW"
        es_valido, texto_o_error = validar_longitud_opinion(texto_opinion)
        if not es_valido:
            raise ValueError(texto_o_error)

        cadena = self._obtener_cadena(self.model_name)

        try:
            resultado = cadena.invoke({
                "jugador": nombre_objetivo,
                "opinion": texto_o_error,
            })
        except Exception as e:
            err_str = str(e)
            # Detección de límite de cuota (429 / RESOURCE_EXHAUSTED / 503) y conmutación a modelo liviano disponible
            if any(term in err_str for term in ["RESOURCE_EXHAUSTED", "429", "503", "high demand"]) and self.model_name != "gemini-3.5-flash-lite":
                logger.warning(
                    f"Modelo '{self.model_name}' reportó límite de cuota o indisponibilidad temporal. "
                    "Conmutando automáticamente a 'gemini-3.5-flash-lite'..."
                )
                cadena_fallback = self._obtener_cadena("gemini-3.5-flash-lite")
                resultado = cadena_fallback.invoke({
                    "jugador": nombre_objetivo,
                    "opinion": texto_o_error,
                })
            else:
                raise e

        if not isinstance(resultado, AnalisisOpinion):
            resultado = AnalisisOpinion(**dict(resultado))

        return resultado
