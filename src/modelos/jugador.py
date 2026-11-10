from typing import List, Optional
from pydantic import BaseModel, Field, model_validator
from src.modelos.modelo_bmw import ModeloBMW, CatalogoModelosBMW


class Jugador(ModeloBMW):
    """Alias compatible de ModeloBMW para preservar contratos de la aplicación."""
    pass


class CatalogoJugadores(BaseModel):
    version: int = Field(default=1, description="Versión del catálogo")
    jugadores: Optional[List[ModeloBMW]] = Field(default=None, description="Lista de modelos de BMW")
    modelos: Optional[List[ModeloBMW]] = Field(default=None, description="Lista de modelos de BMW")

    @model_validator(mode="before")
    @classmethod
    def normalizar_datos(cls, data):
        if isinstance(data, dict):
            if "modelos" in data and "jugadores" not in data:
                data["jugadores"] = data["modelos"]
            elif "jugadores" in data and "modelos" not in data:
                data["modelos"] = data["jugadores"]
        return data

    @model_validator(mode="after")
    def verificar_identificadores_unicos(self):
        items = self.jugadores or self.modelos or []
        ids = [j.id for j in items]
        if len(ids) != len(set(ids)):
            duplicados = [item for item in ids if ids.count(item) > 1]
            raise ValueError(f"Existen identificadores duplicados en el catálogo: {set(duplicados)}")
        return self
