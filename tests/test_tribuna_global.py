import json
import pytest
import tempfile
from pathlib import Path
from src.config import RUTA_JUGADORES
from src.almacenamiento.lector_catalogo import cargar_jugadores
from src.almacenamiento.repositorio_opiniones import (
    cargar_opiniones,
    crear_registro,
    guardar_opinion,
    guardar_base_completa,
)
from src.almacenamiento.servicio_consultas import consultar_opiniones, calcular_metricas
from src.analisis.validador_texto import validar_longitud_opinion
from src.modelos.jugador import Jugador
from src.modelos.analisis_opinion import AnalisisOpinion
from src.modelos.registro_opinion import RegistroOpinion, BaseOpiniones


def test_catalogo_20_jugadores_y_unicidad():
    """Verifica que el catálogo tenga exactamente 20 jugadores y sus IDs sean únicos."""
    jugadores = cargar_jugadores(RUTA_JUGADORES)
    assert len(jugadores) == 20
    ids = [j.id for j in jugadores]
    assert len(ids) == len(set(ids)), "Se detectaron IDs duplicados en el catálogo"


def test_validacion_longitud_opinion():
    """Valida la regla de negocio de longitud de opinión (5 a 1000 caracteres sin espacios)."""
    # Menos de 5 caracteres
    valido, _ = validar_longitud_opinion("   hola   ")
    assert valido is False

    # Vacío
    valido, _ = validar_longitud_opinion("    ")
    assert valido is False

    # Válido (entre 5 y 1000)
    valido, limpio = validar_longitud_opinion("  Es un gran jugador  ")
    assert valido is True
    assert limpio == "Es un gran jugador"

    # Más de 1000 caracteres
    valido, _ = validar_longitud_opinion("a" * 1001)
    assert valido is False


def test_coherencia_pydantic_pertinencia():
    """Verifica la validación cruzada entre es_pertinente y sentimiento en AnalisisOpinion."""
    # Pertinente sin sentimiento debe fallar
    with pytest.raises(Exception):
        AnalisisOpinion(es_pertinente=True, sentimiento=None, razon="Prueba")

    # No pertinente debe normalizar sentimiento a None
    analisis_no_pert = AnalisisOpinion(
        es_pertinente=False, sentimiento="positivo", razon="Comentario ajeno"
    )
    assert analisis_no_pert.sentimiento is None


def test_persistencia_atomica():
    """Comprueba que la escritura atómica cree y guarde registros sin corrupción."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = Path(temp_dir) / "opiniones_test.json"

        # Cargar inicializa base vacía
        base = cargar_opiniones(temp_file)
        assert len(base.opiniones) == 0

        # Crear y guardar registro
        jugador = Jugador(id="j001", nombre="Lionel Messi", pais="Argentina")
        analisis = AnalisisOpinion(
            es_pertinente=True,
            sentimiento="positivo",
            razon="Excelente visión de juego.",
        )
        registro = crear_registro(
            jugador=jugador,
            texto_opinion="Excelente visión de juego.",
            analisis=analisis,
            modelo="test-model",
        )

        base_actualizada = guardar_opinion(temp_file, registro)
        assert len(base_actualizada.opiniones) == 1

        # Idempotencia: no duplicar el mismo ID
        base_reintento = guardar_opinion(temp_file, registro)
        assert len(base_reintento.opiniones) == 1

        # Cargar de disco tras reapertura
        base_reabierta = cargar_opiniones(temp_file)
        assert len(base_reabierta.opiniones) == 1
        assert base_reabierta.opiniones[0].id == registro.id


def test_consultas_y_metricas_en_memoria():
    """Verifica el filtrado por jugador y sentimiento y el cálculo de métricas sin invocar IA."""
    r1 = RegistroOpinion(
        id="1",
        fecha_utc="2026-11-06T10:00:00Z",
        jugador_id="j001",
        jugador_nombre="Lionel Messi",
        opinion_original="Crack total",
        sentimiento="positivo",
        razon="Elogio",
        modelo="m",
    )
    r2 = RegistroOpinion(
        id="2",
        fecha_utc="2026-11-06T10:01:00Z",
        jugador_id="j001",
        jugador_nombre="Lionel Messi",
        opinion_original="Mal partido",
        sentimiento="negativo",
        razon="Crítica",
        modelo="m",
    )
    r3 = RegistroOpinion(
        id="3",
        fecha_utc="2026-11-06T10:02:00Z",
        jugador_id="j002",
        jugador_nombre="Cristiano Ronaldo",
        opinion_original="Goleador",
        sentimiento="positivo",
        razon="Elogio",
        modelo="m",
    )

    lista = [r1, r2, r3]

    # Filtrar por jugador
    filtrados_messi = consultar_opiniones(lista, jugador_id="j001")
    assert len(filtrados_messi) == 2

    # Filtrar por sentimiento
    filtrados_pos = consultar_opiniones(lista, sentimiento="positivo")
    assert len(filtrados_pos) == 2

    # Métricas
    metricas = calcular_metricas(lista)
    assert metricas["total"] == 3
    assert metricas["por_sentimiento"]["positivo"] == 2
    assert metricas["por_sentimiento"]["negativo"] == 1
    assert metricas["por_sentimiento"]["neutro"] == 0


def test_resiliencia_archivo_corrupto():
    """Comprueba que un archivo JSON corrupto no se sobrescriba silenciosamente y lance error."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = Path(temp_dir) / "corrupto.json"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write("{ json_invalido: 123 ")

        # Debe lanzar ValueError y NO borrar el archivo
        with pytest.raises(ValueError):
            cargar_opiniones(temp_file)

        assert temp_file.exists(), "El archivo corrupto debe preservarse para auditoría"

