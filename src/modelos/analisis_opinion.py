from typing import Literal, Optional
from pydantic import BaseModel, Field, model_validator


class AnalisisOpinion(BaseModel):
    es_pertinente: bool = Field(
        description="Indica si el texto constituye una opinión sobre el jugador seleccionado"
    )
    sentimiento: Optional[Literal["positivo", "negativo", "neutro", "mixto"]] = Field(
        default=None,
        description="Categoría de la opinión (positivo, negativo, neutro o mixto); null cuando no es pertinente"
    )
    razon: str = Field(
        min_length=1,
        max_length=300,
        description="Justificación breve de la clasificación redactada en tercera persona"
    )

    @model_validator(mode="after")
    def validar_coherencia_pertinencia_sentimiento(self):
        if not self.es_pertinente:
            if self.sentimiento is not None:
                # Normalizar si el LLM asignó un valor a pesar de no ser pertinente
                self.sentimiento = None
        else:
            if self.sentimiento is None:
                raise ValueError("Una opinión clasificada como pertinente debe tener un sentimiento asignado.")
        return self

