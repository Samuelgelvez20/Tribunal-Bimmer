import json
import pytest
import tempfile
from pathlib import Path
from src.config import RUTA_MODELOS_BMW, RUTA_JUGADORES
from src.almacenamiento.lector_catalogo import cargar_modelos_bmw, cargar_jugadores
from src.almacenamiento.repositorio_opiniones import (
    cargar_opiniones,
    crear_registro,
    guardar_opinion,
    guardar_base_completa,
)
from src.almacenamiento.servicio_consultas import consultar_opiniones, calcular_metricas
from src.analisis.validador_texto import validar_longitud_opinion
from src.modelos.modelo_bmw import ModeloBMW
from src.modelos.analisis_opinion import AnalisisOpinion
from src.modelos.registro_opinion import RegistroOpinion, BaseOpiniones


def test_catalogo_modelos_bmw_y_unicidad():
    """Verifica que el catálogo tenga modelos de BMW y sus IDs sean únicos."""
    modelos = cargar_modelos_bmw(RUTA_MODELOS_BMW)
    assert len(modelos) >= 49, f"Se esperaban al menos 49 modelos, encontrados {len(modelos)}"
    ids = [m.id for m in modelos]
    assert len(ids) == len(set(ids)), "Se detectaron IDs duplicados en el catálogo"
    # Verificar campos requeridos en cada modelo
    for m in modelos:
        assert m.modelo, "Cada modelo debe tener nombre de modelo"
        assert m.ano_creacion >= 1920, f"Año inválido para {m.modelo}: {m.ano_creacion}"
        assert m.tipo in ["sedan", "deportivo", "semideportivo", "familiar", "compacto"], f"Tipo inválido: {m.tipo}"


def test_validacion_longitud_opinion():
    """Valida la regla de negocio de longitud de opinión (5 a 1000 caracteres sin espacios)."""
    # Menos de 5 caracteres
    valido, _ = validar_longitud_opinion("   bmw   ")
    assert valido is False

    # Vacío
    valido, _ = validar_longitud_opinion("    ")
    assert valido is False

    # Válido (entre 5 y 1000)
    valido, limpio = validar_longitud_opinion("  El chasis del M3 es insuperable  ")
    assert valido is True
    assert limpio == "El chasis del M3 es insuperable"

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

        # Crear y guardar registro de BMW
        modelo_bmw = ModeloBMW(
            id="bmw_001",
            nombre="BMW M3 (E30)",
            modelo="BMW M3 (E30)",
            era="Era de oro moderna",
            chasis="E30",
            ano_creacion=1986,
            tipo="deportivo",
            motor="2.3 L I4 (S14)",
            caracteristica="Homologación para Grupo A / DTM.",
        )
        analisis = AnalisisOpinion(
            es_pertinente=True,
            sentimiento="positivo",
            razon="Excelente dinamismo y ligereza en pista.",
        )
        registro = crear_registro(
            jugador=modelo_bmw,
            texto_opinion="Excelente dinamismo y ligereza en pista.",
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
    """Verifica el filtrado por modelo y sentimiento y el cálculo de métricas sin invocar IA."""
    r1 = RegistroOpinion(
        id="1",
        fecha_utc="2026-11-06T10:00:00Z",
        jugador_id="bmw_001",
        jugador_nombre="BMW M3 (E30)",
        modelo_id="bmw_001",
        modelo_nombre="BMW M3 (E30)",
        opinion_original="El mejor chasis histórico.",
        sentimiento="positivo",
        razon="Elogia el comportamiento dinámico.",
        modelo="test",
    )
    r2 = RegistroOpinion(
        id="2",
        fecha_utc="2026-11-06T10:05:00Z",
        jugador_id="bmw_002",
        jugador_nombre="BMW M5 (E60)",
        modelo_id="bmw_002",
        modelo_nombre="BMW M5 (E60)",
        opinion_original="Caja SMG problemática.",
        sentimiento="negativo",
        razon="Critica la fiabilidad de la transmisión.",
        modelo="test",
    )
    r3 = RegistroOpinion(
        id="3",
        fecha_utc="2026-11-06T10:10:00Z",
        jugador_id="bmw_001",
        jugador_nombre="BMW M3 (E30)",
        modelo_id="bmw_001",
        modelo_nombre="BMW M3 (E30)",
        opinion_original="Motor 4 cilindros de 2.3 litros.",
        sentimiento="neutro",
        razon="Aporta datos técnicos sin valorar.",
        modelo="test",
    )

    registros = [r1, r2, r3]

    # Filtrar por modelo
    filtro_m1 = consultar_opiniones(registros, modelo_id="bmw_001")
    assert len(filtro_m1) == 2

    # Filtrar por sentimiento
    filtro_neg = consultar_opiniones(registros, sentimiento="negativo")
    assert len(filtro_neg) == 1
    assert filtro_neg[0].id == "2"

    # Filtrar cruzado
    filtro_cruzado = consultar_opiniones(registros, modelo_id="bmw_001", sentimiento="positivo")
    assert len(filtro_cruzado) == 1
    assert filtro_cruzado[0].id == "1"

    # Métricas
    metricas = calcular_metricas(registros)
    assert metricas["total"] == 3
    assert metricas["por_sentimiento"]["positivo"] == 1
    assert metricas["por_sentimiento"]["negativo"] == 1
    assert metricas["por_sentimiento"]["neutro"] == 1
    assert metricas["por_sentimiento"]["mixto"] == 0
