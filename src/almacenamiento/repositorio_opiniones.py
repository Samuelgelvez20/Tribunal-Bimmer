import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Union
from src.modelos.jugador import Jugador
from src.modelos.analisis_opinion import AnalisisOpinion
from src.modelos.registro_opinion import RegistroOpinion, BaseOpiniones


def cargar_opiniones(ruta: Union[str, Path]) -> BaseOpiniones:
    """
    Lee el archivo persistente de opiniones.
    - Si no existe, inicializa la estructura vacía y la guarda.
    - Si contiene JSON inválido o esquema corrupto, lanza excepción y PRESERVA el archivo.
    """
    ruta_path = Path(ruta)
    if not ruta_path.exists():
        # Inicializar estructura vacía
        base_vacia = BaseOpiniones(version=1, opiniones=[])
        guardar_base_completa(ruta_path, base_vacia)
        return base_vacia

    try:
        with open(ruta_path, "r", encoding="utf-8") as f:
            contenido = f.read().strip()
            if not contenido:
                base_vacia = BaseOpiniones(version=1, opiniones=[])
                return base_vacia
            datos_raw = json.loads(contenido)
    except json.JSONDecodeError as e:
        # No sobreescribir silenciosamente; preservar archivo corrupto para inspección
        raise ValueError(f"El archivo de opiniones en {ruta_path} contiene JSON inválido: {e}")

    try:
        return BaseOpiniones(**datos_raw)
    except Exception as e:
        raise ValueError(f"El esquema de opiniones en {ruta_path} es inválido o incompatible: {e}")


def crear_registro(
    jugador: Jugador,
    texto_opinion: str,
    analisis: AnalisisOpinion,
    modelo: str,
    version_prompt: str = "1.0",
) -> RegistroOpinion:
    """
    Crea un nuevo registro de opinión con UUID, fecha UTC y metadatos.
    """
    if not analisis.es_pertinente or analisis.sentimiento is None:
        raise ValueError("No se puede crear un registro para una opinión no pertinente o sin sentimiento.")

    return RegistroOpinion(
        id=str(uuid.uuid4()),
        fecha_utc=datetime.now(timezone.utc).isoformat(),
        jugador_id=jugador.id,
        jugador_nombre=jugador.nombre,
        opinion_original=texto_opinion.strip(),
        sentimiento=analisis.sentimiento,
        razon=analisis.razon.strip(),
        modelo=modelo,
        version_prompt=version_prompt,
    )


def guardar_base_completa(ruta: Union[str, Path], base: BaseOpiniones) -> None:
    """
    Guarda la base de opiniones completa de forma atómica en disco usando archivo temporal.
    """
    ruta_path = Path(ruta)
    directorio = ruta_path.parent
    directorio.mkdir(parents=True, exist_ok=True)

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            dir=directorio,
            delete=False,
            encoding="utf-8",
            prefix=".opiniones_tmp_",
            suffix=".json",
        ) as tmp:
            temp_path = Path(tmp.name)
            # Volcar datos con UTF-8 e indentación
            json.dump(base.model_dump(), tmp, ensure_ascii=False, indent=2)
            tmp.flush()
            os.fsync(tmp.fileno())

        # Reemplazo atómico
        os.replace(temp_path, ruta_path)
    except Exception as e:
        if temp_path and temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass
        raise IOError(f"Error durante la escritura atómica en {ruta_path}: {e}")


def guardar_opinion(ruta: Union[str, Path], registro: RegistroOpinion) -> BaseOpiniones:
    """
    Agrega un registro a la base persistente sin perder los anteriores.
    Previene duplicados por ID (idempotencia en reintentos).
    """
    base = cargar_opiniones(ruta)

    # Comprobar si el ID ya existe
    if any(op.id == registro.id for op in base.opiniones):
        return base

    base.opiniones.append(registro)
    guardar_base_completa(ruta, base)
    return base

