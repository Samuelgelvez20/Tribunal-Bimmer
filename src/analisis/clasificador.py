from typing import Optional
from langchain_openai import ChatOpenAI
from src.config import DEFAULT_MODEL, DEFAULT_API_KEY, TEMPERATURE
from src.modelos.analisis_opinion import AnalisisOpinion
from src.analisis.prompts import PROMPT_CLASIFICACION
from src.analisis.validador_texto import validar_longitud_opinion

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except Exception:
    ChatGoogleGenerativeAI = None


class ClasificadorOpiniones:
    """
    Servicio de clasificación de opiniones mediante cadenas LCEL y salida estructurada Pydantic.
    Admite modelos OpenAI y Google Gemini según configuración y claves disponibles.
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

    def _obtener_cadena(self):
        if not self.api_key:
            raise ValueError(
                "No se encontró una API Key válida configurada. Define OPENAI_API_KEY o GOOGLE_API_KEY en .env."
            )

        es_gemini = self.model_name.startswith("gemini") or self.api_key.startswith("AQ.") or self.api_key.startswith("AIza")

        if es_gemini:
            if ChatGoogleGenerativeAI is None:
                raise ImportError("Para usar modelos Gemini debes tener instalado langchain-google-genai.")
            
            modelo_real = self.model_name if self.model_name.startswith("gemini") else "gemini-3.8-flash"
            llm = ChatGoogleGenerativeAI(
                model=modelo_real,
                temperature=self.temperature,
                google_api_key=self.api_key,
            )
        else:
            llm = ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                api_key=self.api_key,
            )

        # Salida estructurada garantizada con Pydantic
        modelo_estructurado = llm.with_structured_output(AnalisisOpinion)
        return PROMPT_CLASIFICACION | modelo_estructurado

    def analizar(self, nombre_jugador: str, texto_opinion: str) -> AnalisisOpinion:
        """
        Ejecuta la clasificación sobre una opinión. Valida la longitud antes de llamar al LLM.
        """
        es_valido, texto_o_error = validar_longitud_opinion(texto_opinion)
        if not es_valido:
            raise ValueError(texto_o_error)

        cadena = self._obtener_cadena()

        resultado = cadena.invoke({
            "jugador": nombre_jugador,
            "opinion": texto_o_error,
        })

        if not isinstance(resultado, AnalisisOpinion):
            resultado = AnalisisOpinion(**dict(resultado))

        return resultado
