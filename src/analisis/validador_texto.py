from typing import Tuple


def validar_longitud_opinion(texto: str) -> Tuple[bool, str]:
    """
    Valida que el texto de la opinión cumpla con la regla de 5 a 1000 caracteres
    después de eliminar espacios exteriores.
    Retorna (es_valido, texto_limpio_o_mensaje_error).
    """
    if not texto:
        return False, "La opinión no puede estar vacía."

    texto_limpio = texto.strip()
    longitud = len(texto_limpio)

    if longitud < 5:
        return False, f"La opinión es demasiado corta ({longitud} caracteres). Debe tener al menos 5 caracteres."

    if longitud > 1000:
        return False, f"La opinión excede el límite permitido ({longitud} caracteres). El máximo es 1000 caracteres."

    return True, texto_limpio

