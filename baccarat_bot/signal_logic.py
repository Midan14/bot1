# baccarat_bot/signal_logic.py

import logging
from typing import Dict, List, Optional

from baccarat_bot.config import LONGITUD_RACHA
from baccarat_bot.strategies.advanced_strategies import (
    estrategia_racha,
    estrategia_zigzag
)

logger = logging.getLogger(__name__)

RESULTADOS_VALIDOS = {'B', 'P', 'E'}  # Banca, Jugador, Empate

# Lista de estrategias a ejecutar en orden de prioridad
ESTRATEGIAS = [
    {"funcion": estrategia_racha, "nombre": "Racha de 3"},
    {"funcion": estrategia_zigzag, "nombre": "Patrón Zig-Zag"},
]


def analizar_y_generar_senales(
    historial: List[str],
) -> list[tuple[str, str]]:
    """
    Itera sobre todas las estrategias y devuelve todas las señales encontradas.

    Args:
        historial: Lista de resultados de la mesa.

    Returns:
        Lista de tuplas (apuesta, nombre_de_la_estrategia).
    """
    senales = []
    for estrategia in ESTRATEGIAS:
        # Pasar parámetros específicos si es necesario
        if estrategia["funcion"] == estrategia_racha:
            senal = estrategia["funcion"](
                historial, longitud_racha=LONGITUD_RACHA
            )
        else:
            senal = estrategia["funcion"](historial)

        if senal:
            senales.append((senal, estrategia["nombre"]))

    return senales


def actualizar_historial(mesa_data: Dict, nuevo_resultado: str):
    """
    Actualiza el historial de resultados de una mesa con el nuevo resultado.
    """
    if nuevo_resultado not in RESULTADOS_VALIDOS:
        raise ValueError(
            f"Resultado inválido: {nuevo_resultado}. Debe ser 'B', 'P' o 'E'."
        )

    mesa_data['historial_resultados'].append(nuevo_resultado)
