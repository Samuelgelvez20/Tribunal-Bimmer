from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Optional, List

from src.config import RUTA_JUGADORES, RUTA_OPINIONES, DEFAULT_MODEL
from src.almacenamiento import (
    cargar_jugadores,
    cargar_opiniones,
    crear_registro,
    guardar_opinion,
    consultar_opiniones,
    calcular_metricas,
)
from src.analisis import ClasificadorOpiniones
from src.modelos import Jugador, RegistroOpinion, AnalisisOpinion

app = FastAPI(
    title="Tribuna Global API",
    description="API REST para análisis y registro de percepciones sobre futbolistas",
    version="1.0.0",
)

# Permitir CORS para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Catálogo en memoria precargado y validado
JUGADORES_CATALOGO = cargar_jugadores(RUTA_JUGADORES)
JUGADORES_DICT = {j.id: j for j in JUGADORES_CATALOGO}


class SolicitudAnalisis(BaseModel):
    jugador_id: str = Field(..., description="ID del jugador (ej. j001)")
    texto_opinion: str = Field(..., description="Texto de la crítica u opinión (5 a 1000 caracteres)")
    api_key: Optional[str] = Field(None, description="API Key opcional (usa .env por defecto)")
    modelo: Optional[str] = Field(None, description="Modelo de lenguaje opcional")


class RespuestaAnalisis(BaseModel):
    es_pertinente: bool
    sentimiento: Optional[str] = None
    razon: str
    guardado: bool
    registro: Optional[RegistroOpinion] = None


@app.get("/api/jugadores", response_model=List[Jugador])
def listar_jugadores():
    """Retorna el catálogo inmutable de 20 futbolistas."""
    return JUGADORES_CATALOGO


@app.get("/api/opiniones")
def obtener_opiniones(
    jugador_id: Optional[str] = Query(None, description="ID del jugador o 'todos'"),
    sentimiento: Optional[str] = Query(None, description="Sentimiento o 'todos'"),
):
    """Retorna las opiniones filtradas y las métricas de resumen."""
    base = cargar_opiniones(RUTA_OPINIONES)
    filtradas = consultar_opiniones(base.opiniones, jugador_id=jugador_id, sentimiento=sentimiento)
    metricas = calcular_metricas(filtradas)
    metricas_globales = calcular_metricas(base.opiniones)
    return {
        "opiniones": filtradas,
        "metricas_filtradas": metricas,
        "metricas_globales": metricas_globales,
    }


@app.post("/api/opiniones/analizar", response_model=RespuestaAnalisis)
def analizar_y_guardar(solicitud: SolicitudAnalisis):
    """
    Analiza una opinión con LangChain.
    - Si es pertinente: se clasifica, se crea registro con UUID y se guarda atómicamente en disco.
    - Si NO es pertinente: se devuelve el motivo y NO se guarda en disco.
    """
    jugador = JUGADORES_DICT.get(solicitud.jugador_id)
    if not jugador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Jugador con ID '{solicitud.jugador_id}' no encontrado en el catálogo.",
        )

    try:
        clasificador = ClasificadorOpiniones(
            api_key=solicitud.api_key,
            model_name=solicitud.modelo or DEFAULT_MODEL,
        )
        analisis: AnalisisOpinion = clasificador.analizar(
            nombre_jugador=jugador.nombre,
            texto_opinion=solicitud.texto_opinion,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante el análisis del modelo de IA: {str(e)}",
        )

    if not analisis.es_pertinente:
        return RespuestaAnalisis(
            es_pertinente=False,
            sentimiento=None,
            razon=analisis.razon,
            guardado=False,
            registro=None,
        )

    # Crear y guardar registro atómicamente
    try:
        registro = crear_registro(
            jugador=jugador,
            texto_opinion=solicitud.texto_opinion,
            analisis=analisis,
            modelo=solicitud.modelo or DEFAULT_MODEL,
        )
        guardar_opinion(RUTA_OPINIONES, registro)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al persistir la opinión en disco: {str(e)}",
        )

    return RespuestaAnalisis(
        es_pertinente=True,
        sentimiento=analisis.sentimiento,
        razon=analisis.razon,
        guardado=True,
        registro=registro,
    )


# Servir Frontend en React cuando esté compilado (en /app/frontend/dist)
RUTA_FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if RUTA_FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=RUTA_FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def servir_spa(full_path: str):
        archivo = RUTA_FRONTEND_DIST / full_path
        if archivo.is_file():
            return FileResponse(archivo)
        return FileResponse(RUTA_FRONTEND_DIST / "index.html")
