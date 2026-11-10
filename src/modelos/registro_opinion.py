from typing import List, Literal, Optional
from pydantic import BaseModel, Field, model_validator


class RegistroOpinion(BaseModel):
    id: str = Field(..., description="UUID único generado para la opinión")
    fecha_utc: str = Field(..., description="Marca temporal en formato ISO 8601 con zona horaria UTC")
    jugador_id: str = Field(..., description="Identificador inmutable del modelo BMW")
    jugador_nombre: str = Field(..., description="Nombre del modelo BMW evaluado")
    modelo_id: Optional[str] = Field(None, description="Identificador del modelo BMW")
    modelo_nombre: Optional[str] = Field(None, description="Nombre del modelo BMW")
    opinion_original: str = Field(..., description="Texto original proporcionado por el usuario")
    sentimiento: Literal["positivo", "negativo", "neutro", "mixto"] = Field(
        ..., description="Sentimiento asignado por el análisis"
    )
    razon: str = Field(..., description="Justificación en tercera persona")
    modelo: str = Field(..., description="Nombre del modelo LLM utilizado")
    version_prompt: str = Field(default="1.0", description="Versión del prompt de clasificación")

    @model_validator(mode="before")
    @classmethod
    def sincronizar_campos(cls, data):
        if isinstance(data, dict):
            # Sincronizar entre jugador_id/modelo_id y jugador_nombre/modelo_nombre
            m_id = data.get("modelo_id") or data.get("jugador_id")
            m_nom = data.get("modelo_nombre") or data.get("jugador_nombre")
            data["jugador_id"] = m_id
            data["modelo_id"] = m_id
            data["jugador_nombre"] = m_nom
            data["modelo_nombre"] = m_nom
        return data


class BaseOpiniones(BaseModel):
    version: int = Field(default=1, description="Versión del esquema de persistencia")
    opiniones: List[RegistroOpinion] = Field(default_factory=list, description="Lista de opiniones almacenadas")
