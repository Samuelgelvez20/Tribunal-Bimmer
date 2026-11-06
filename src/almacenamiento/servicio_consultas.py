from typing import Dict, List, Optional
from src.modelos.registro_opinion import RegistroOpinion


def consultar_opiniones(
    registros: List[RegistroOpinion],
    jugador_id: Optional[str] = None,
    sentimiento: Optional[str] = None,
) -> List[RegistroOpinion]:
    """
    Filtra la lista de opiniones por jugador y/o sentimiento sin invocar al modelo.
    Admite 'todos' o None como comodín de no filtrado.
    """
    resultado = registros

    if jugador_id and jugador_id.lower() != "todos":
        resultado = [op for op in resultado if op.jugador_id == jugador_id]

    if sentimiento and sentimiento.lower() != "todos":
        sentimiento_limpio = sentimiento.lower().strip()
        resultado = [op for op in resultado if op.sentimiento.lower() == sentimiento_limpio]

    return resultado


def calcular_metricas(registros: List[RegistroOpinion]) -> Dict[str, object]:
    """
    Calcula los totales y distribución por sentimiento de un conjunto de registros.
    """
    conteo_sentimientos = {
        "positivo": 0,
        "negativo": 0,
        "neutro": 0,
        "mixto": 0,
    }

    conteo_jugadores: Dict[str, int] = {}

    for op in registros:
        sent = op.sentimiento.lower()
        if sent in conteo_sentimientos:
            conteo_sentimientos[sent] += 1
        conteo_jugadores[op.jugador_nombre] = conteo_jugadores.get(op.jugador_nombre, 0) + 1

    return {
        "total": len(registros),
        "por_sentimiento": conteo_sentimientos,
        "por_jugador": conteo_jugadores,
    }

