from pydantic import BaseModel, Field, model_validator
from typing import List


class Jugador(BaseModel):
    id: str = Field(..., description="Identificador único del jugador (ej. j001)")
    nombre: str = Field(..., description="Nombre completo o deportivo del jugador")
    pais: str = Field(..., description="País de origen o nacionalidad deportiva")


class CatalogoJugadores(BaseModel):
    version: int = Field(default=1, description="Versión del catálogo")
    jugadores: List[Jugador] = Field(..., description="Lista de jugadores disponibles")

    @model_validator(mode="after")
    def verificar_identificadores_unicos(self):
        ids = [j.id for j in self.jugadores]
        if len(ids) != len(set(ids)):
            duplicados = [item for item in ids if ids.count(item) > 1]
            raise ValueError(f"Existen identificadores duplicados en el catálogo: {set(duplicados)}")
        return self

