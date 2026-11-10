import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Union
from src.modelos.modelo_bmw import ModeloBMW
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
    jugador: Optional[Union[ModeloBMW, Jugador]] = None,
    texto_opinion: str = "",
    analisis: Optional[AnalisisOpinion] = None,
    modelo: str = "default",
    version_prompt: str = "1.0",
    modelo_bmw: Optional[Union[ModeloBMW, Jugador]] = None,
) -> RegistroOpinion:
    """
    Crea un nuevo registro de opinión con UUID, fecha UTC y metadatos.
    """
    target = modelo_bmw or jugador
    if target is None:
        raise ValueError("Se debe proporcionar el modelo de BMW evaluado.")

    if analisis is None or not analisis.es_pertinente or analisis.sentimiento is None:
        raise ValueError("No se puede crear un registro para una opinión no pertinente o sin sentimiento.")

    target_nombre = getattr(target, "modelo", None) or getattr(target, "nombre", str(target))

    return RegistroOpinion(
        id=str(uuid.uuid4()),
        fecha_utc=datetime.now(timezone.utc).isoformat(),
        jugador_id=target.id,
        jugador_nombre=target_nombre,
        modelo_id=target.id,
        modelo_nombre=target_nombre,
        opinion_original=texto_opinion.strip(),
        sentimiento=analisis.sentimiento,
        razon=analisis.razon.strip(),
        modelo=modelo,
        version_prompt=version_prompt,
    )


def guardar_base_completa(ruta: Union[str, Path], base: BaseOpiniones) -> None:
    """
    Escribe atómicamente la base completa en disco mediante archivo temporal y os.replace.
    """
    ruta_path = Path(ruta)
    directorio_padre = ruta_path.parent
    directorio_padre.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile("w", dir=directorio_padre, delete=False, encoding="utf-8") as temp_file:
        nombre_temporal = temp_file.name
        temp_file.write(base.model_dump_json(indent=2))
        temp_file.flush()
        os.fsync(temp_file.fileno())

    # Asegurar permisos accesibles en el host y contenedor
    try:
        os.chmod(nombre_temporal, 0o666)
    except Exception:
        pass

    # Reemplazo atómico garantizado por el sistema operativo
    os.replace(nombre_temporal, ruta_path)


def guardar_opinion(ruta: Union[str, Path], registro: RegistroOpinion) -> BaseOpiniones:
    """
    Carga la base existente, añade el nuevo registro garantizando idempotencia por ID,
    y persiste la base de manera atómica.
    """
    base = cargar_opiniones(ruta)

    # Idempotencia: si ya existe el ID, no lo duplica
    if any(op.id == registro.id for op in base.opiniones):
        return base

    base.opiniones.append(registro)
    guardar_base_completa(ruta, base)
    return base
