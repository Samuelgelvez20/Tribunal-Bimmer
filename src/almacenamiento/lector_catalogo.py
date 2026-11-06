import json
from pathlib import Path
from typing import List, Union
from src.modelos.jugador import Jugador, CatalogoJugadores


def cargar_jugadores(ruta: Union[str, Path]) -> List[Jugador]:
    """
    Carga y valida el catálogo de jugadores desde un archivo JSON.
    Verifica que el archivo exista, sea sintácticamente válido y no contenga IDs repetidos.
    """
    ruta_path = Path(ruta)
    if not ruta_path.exists():
        raise FileNotFoundError(f"El catálogo de jugadores no fue encontrado en: {ruta_path}")

    try:
        with open(ruta_path, "r", encoding="utf-8") as f:
            datos_raw = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error de sintaxis JSON en el catálogo de jugadores: {e}")

    try:
        catalogo = CatalogoJugadores(**datos_raw)
    except Exception as e:
        raise ValueError(f"Error de validación del catálogo de jugadores: {e}")

    return catalogo.jugadores

