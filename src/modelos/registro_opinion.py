from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class RegistroOpinion(BaseModel):
    id: str = Field(..., description="UUID único generado para la opinión")
    fecha_utc: str = Field(..., description="Marca temporal en formato ISO 8601 con zona horaria UTC")
    jugador_id: str = Field(..., description="Identificador inmutable del jugador (ej. j001)")
    jugador_nombre: str = Field(..., description="Nombre del futbolista evaluado")
    opinion_original: str = Field(..., description="Texto original proporcionado por el usuario")
    sentimiento: Literal["positivo", "negativo", "neutro", "mixto"] = Field(
        ..., description="Sentimiento asignado por el análisis"
    )
    razon: str = Field(..., description="Justificación en tercera persona")
    modelo: str = Field(..., description="Nombre del modelo LLM utilizado")
    version_prompt: str = Field(default="1.0", description="Versión del prompt de clasificación")


class BaseOpiniones(BaseModel):
    version: int = Field(default=1, description="Versión del esquema de persistencia")
    opiniones: List[RegistroOpinion] = Field(default_factory=list, description="Lista de opiniones almacenadas")

