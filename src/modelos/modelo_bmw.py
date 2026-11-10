from typing import List, Optional
from pydantic import BaseModel, Field, model_validator


class ModeloBMW(BaseModel):
    id: str = Field(..., description="Identificador único del modelo (ej. bmw_001)")
    nombre: str = Field(..., description="Nombre del modelo (ej. BMW M3 (E30))")
    modelo: str = Field(..., description="Nombre oficial del modelo BMW")
    era: str = Field(..., description="Era histórica de BMW")
    chasis: Optional[str] = Field(None, description="Código de chasis o plataforma (ej. E30, F87, G80)")
    ano_creacion: int = Field(..., description="Año de lanzamiento o creación")
    tipo: str = Field(..., description="Tipo de carrocería (sedan, deportivo, semideportivo, familiar, compacto)")
    motor: str = Field(..., description="Especificación técnica de motorización")
    caballos_fuerza: Optional[int] = Field(None, description="Potencia en caballos de fuerza (HP / CV)")
    torque_nm: Optional[float] = Field(None, description="Par motor en Newton-Metro (Nm)")
    velocidad_maxima_kmh: Optional[float] = Field(None, description="Velocidad máxima en km/h")
    aceleracion_0_100_kmh_s: Optional[float] = Field(None, description="Aceleración de 0 a 100 km/h en segundos")
    caracteristica: str = Field(..., description="Hito histórico, resumen o detalle técnico")
    fuente: Optional[str] = Field(None, description="Fuente del dato")
    pais: Optional[str] = Field(default="Alemania", description="País de origen")


class CatalogoModelosBMW(BaseModel):
    version: int = Field(default=1, description="Versión del catálogo")
    modelos: List[ModeloBMW] = Field(..., description="Lista de modelos de BMW")

    @model_validator(mode="after")
    def verificar_identificadores_unicos(self):
        ids = [m.id for m in self.modelos]
        if len(ids) != len(set(ids)):
            duplicados = [item for item in ids if ids.count(item) > 1]
            raise ValueError(f"Existen identificadores duplicados en el catálogo de BMW: {set(duplicados)}")
        return self
