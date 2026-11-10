import json
from pathlib import Path
from typing import List, Union
from src.modelos.modelo_bmw import ModeloBMW, CatalogoModelosBMW
from src.modelos.jugador import CatalogoJugadores


def cargar_modelos_bmw(ruta: Union[str, Path]) -> List[ModeloBMW]:
    """
    Carga y valida el catálogo de modelos BMW desde un archivo JSON.
    Verifica que el archivo exista, sea sintácticamente válido y no contenga IDs repetidos.
    """
    ruta_path = Path(ruta)
    if not ruta_path.exists():
        raise FileNotFoundError(f"El catálogo de modelos BMW no fue encontrado en: {ruta_path}")

    try:
        with open(ruta_path, "r", encoding="utf-8") as f:
            datos_raw = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error de sintaxis JSON en el catálogo de modelos BMW: {e}")

    try:
        if "modelos" in datos_raw:
            catalogo = CatalogoModelosBMW(**datos_raw)
            return catalogo.modelos
        elif "jugadores" in datos_raw:
            catalogo = CatalogoJugadores(**datos_raw)
            return catalogo.jugadores or catalogo.modelos or []
        else:
            raise ValueError("El catálogo no contiene la clave 'modelos' ni 'jugadores'.")
    except Exception as e:
        raise ValueError(f"Error de validación del catálogo de modelos BMW: {e}")


def cargar_jugadores(ruta: Union[str, Path]) -> List[ModeloBMW]:
    """Alias retrocompatible para cargar_modelos_bmw."""
    return cargar_modelos_bmw(ruta)
