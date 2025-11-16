

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Optional
from telegram import Bot
from telegram.error import TelegramError
from baccarat_bot.config import (
    TELEGRAM_TOKEN,
    TELEGRAM_CHAT_ID,
    INTERVALO_MONITOREO
)
from baccarat_bot.tables import inicializar_mesas, MESA_NOMBRES
from baccarat_bot.signal_logic import analizar_y_generar_senales
from baccarat_bot.ml_integration import entrenar_ml_si_posible, obtener_prediccion_ml
from baccarat_bot.data_source import obtener_nuevo_resultado_async, _init_playwright_scraper
from baccarat_bot.game_timing_detector import GameTimingDetector, RealTimeGameMonitor



async def _inicializar_historiales(mesas):
    for mesa_data in mesas.values():
        game_id = mesa_data.get('game_id')
        for _ in range(5):
            resultado_simulado = await obtener_nuevo_resultado_async(
                mesa_data, game_id
            )
            mesa_data['historial_resultados'].append(resultado_simulado)


def _procesar_prediccion_pendiente(mesa_nombre, nuevo_resultado):
    if mesa_nombre in predicciones_pendientes:
        pred = predicciones_pendientes[mesa_nombre]
        # Esperar un poco para asegurar que se procesó
        asyncio.run(asyncio.sleep(1))
        # Enviar resultado
        asyncio.run(enviar_resultado_apuesta(
            mesa_nombre,
            pred['apuesta'],
            nuevo_resultado
        ))
        # Limpiar predicción
        del predicciones_pendientes[mesa_nombre]


def _actualizar_historial(mesa_data, nuevo_resultado):
    mesa_data['historial_resultados'].append(nuevo_resultado)
    if len(mesa_data['historial_resultados']) > 50:
        mesa_data['historial_resultados'] = (
            mesa_data['historial_resultados'][-50:]
        )


async def _analizar_y_enviar_senal(mesa_nombre, mesa_data):
    historial = mesa_data.get('historial_resultados', [])
    # Usar solo historial hasta la ronda anterior (no incluir resultado actual si la ronda está en curso)
    historial_para_prediccion = historial[:-1] if mesa_data.get('ronda_en_curso', False) and len(historial) > 1 else historial[:]

    # Entrenar modelo ML solo con historial válido
    entrenar_ml_si_posible(historial_para_prediccion)

    # Señal ML prioritaria si está disponible
    senal_ml = obtener_prediccion_ml(historial_para_prediccion)
    if senal_ml:
        senal_info = {
            'mesa': mesa_nombre,
            'apuesta': senal_ml,
            'estrategia': 'ML Predictor',
            'url': mesa_data.get('url', ''),
            'historial_reciente': (
                historial_para_prediccion[-10:]
                if len(historial_para_prediccion) > 10 else historial_para_prediccion
            )
        }
        logger.info(
            "🤖 SEÑAL ML DETECTADA para %s [MOMENTO ÓPTIMO]",
            mesa_nombre
        )
        signal_sent = await enviar_senal_telegram(
            senal_info, mesa_data
        )
        if signal_sent:
            timing_simulator = (
                timing_detector.simulate_round_timing()
            )
            timing_detector.record_round_timing(
                timing_simulator
            )
        return

    # Señales tradicionales
    senales = analizar_y_generar_senales(historial)
    for senal, estrategia in senales:
        senal_info = {
            'mesa': mesa_nombre,
            'apuesta': senal,
            'estrategia': estrategia,
            'url': mesa_data.get('url', ''),
            'historial_reciente': (
                historial[-10:]
                if len(historial) > 10 else historial
            )
        }
        logger.info(
            "🎯 SEÑAL DETECTADA para %s (%s) [MOMENTO ÓPTIMO]",
            mesa_nombre, estrategia
        )
        signal_sent = await enviar_senal_telegram(
            senal_info, mesa_data
        )
        if signal_sent:
            timing_simulator = (
                timing_detector.simulate_round_timing()
            )
            timing_detector.record_round_timing(
                timing_simulator
            )


def _mapear_colores_apuesta(apuesta_upper):
    if apuesta_upper in ['BANCA', 'B', 'BANKER']:
        return {
            'color_apuesta': "🔴",
            'color_fondo': "❤️",
            'emoji_destacado': "🎯",
            'confianza': "🔴 ALTA",
            'nombre_apuesta': "BANCA"
        }
    elif apuesta_upper in ['JUGADOR', 'P', 'PLAYER']:
        return {
            'color_apuesta': "🔵",
            'color_fondo': "💙",
            'emoji_destacado': "🎯",
            'confianza': "🔵 ALTA",
            'nombre_apuesta': "JUGADOR"
        }
    elif apuesta_upper in ['EMPATE', 'E', 'TIE']:
        return {
            'color_apuesta': "🟢",
            'color_fondo': "💚",
            'emoji_destacado': "⚖️",
            'confianza': "🟢 MEDIA",
            'nombre_apuesta': "EMPATE"
        }
    else:
        return {
            'color_apuesta': "⚪",
            'color_fondo': "⚪",
            'emoji_destacado': "⚠️",
            'confianza': "⚪ BAJA",
            'nombre_apuesta': apuesta_upper
        }


def _resultado_a_emoji(r):
    if r == "B":
        return "🔴"
    elif r == "P":
        return "🔵"
    elif r == "E":
        return "🟢"
    else:
        return "⚪"


def _generar_historial_emojis(historial):
    return [_resultado_a_emoji(x) for x in historial]

  
def _detectar_seguidilla(historial, min_racha=3):
    if not historial:
        return None
    racha = 1
    max_racha = 1
    valor_racha = historial[0]
    for i in range(1, len(historial)):
        if historial[i] == historial[i-1]:
            racha += 1
            if racha > max_racha:
                max_racha = racha
                valor_racha = historial[i]
        else:
            racha = 1
    if max_racha >= min_racha:
        return valor_racha, max_racha
    return None


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicializar el bot de Telegram
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN no está configurado")
if not TELEGRAM_CHAT_ID:
    raise ValueError("TELEGRAM_CHAT_ID no está configurado")

bot = Bot(token=TELEGRAM_TOKEN)

# Inicializar detector de timing del juego
timing_detector = GameTimingDetector()
game_monitor = RealTimeGameMonitor()

# Control de frecuencia de señales (evitar flood)
last_signal_time: Dict[str, float] = {}
MIN_SIGNAL_INTERVAL = 30.0  # Mínimo 30 segundos entre señales de la misma mesa

# Rastreo de predicciones para mostrar resultados
predicciones_pendientes: Dict[str, Dict] = {}
# mesa_nombre -> {apuesta, resultado_anterior}


async def enviar_resultado_apuesta(mesa_nombre: str, apuesta_predicha: str,
                                   resultado_actual: str) -> None:
    """
    Envía el resultado de la apuesta a Telegram con ✅ o ❌
    
    Args:
        mesa_nombre: Nombre de la mesa
        apuesta_predicha: La apuesta que se predijo (BANCA, JUGADOR, EMPATE)
        resultado_actual: El resultado actual (B, P, E)
    """
    # Mapeo de resultados
    resultado_nombre = {
        'B': 'BANCA',
        'P': 'JUGADOR',
        'E': 'EMPATE'
    }.get(resultado_actual, 'DESCONOCIDO')
    
    # Verificar si la predicción fue correcta
    apuesta_predicha_upper = apuesta_predicha.upper()
    fue_correcta = (
        (apuesta_predicha_upper == 'BANCA' and resultado_actual == 'B') or
        (apuesta_predicha_upper == 'JUGADOR' and resultado_actual == 'P') or
        (apuesta_predicha_upper == 'EMPATE' and resultado_actual == 'E')
    )
    
    # Crear mensaje con resultado
    if fue_correcta:
        emoji_resultado = "✅"  # Verde para ganar
        titulo = "¡APUESTA GANADA!"
        simbolo = "✅ GANANCIA ✅"
    else:
        emoji_resultado = "❌"  # Rojo para perder
        titulo = "Apuesta Perdida"
        simbolo = "❌ PÉRDIDA ❌"

    timestamp = datetime.now().strftime("%H:%M:%S")

    mensaje = (
        f"{emoji_resultado} **{titulo}** {emoji_resultado}\n\n"
        f"🎰 **Mesa:** {mesa_nombre}\n"
        f"🎯 **Apuesta Predicha:** {apuesta_predicha_upper}\n"
        f"🎲 **Resultado Real:** {resultado_nombre}\n"
        f"⏱️ **Hora:** {timestamp}\n\n"
        f"{simbolo}"
    )
    
    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=mensaje,
            parse_mode='Markdown'
        )
        logger.info(
            "📊 Resultado enviado para %s: %s",
            mesa_nombre, emoji_resultado
        )
    except TelegramError as e:
        logger.error("❌ Error enviando resultado: %s", e)


async def enviar_senal_telegram(senal_info: Dict, mesa_data: Dict) -> bool:

    current_time = time.time()
    mesa_nombre = senal_info.get('mesa', None)
    if not mesa_nombre:
        logger.error("No se encontró el nombre de la mesa en la señal.")
        return False
    if mesa_nombre in last_signal_time:
        time_since_last = current_time - last_signal_time[mesa_nombre]
        if time_since_last < MIN_SIGNAL_INTERVAL:
            logger.warning(
                "⏸️ Señal bloqueada para %s: muy pronto desde última señal "
                "(%.1fs < %ss)",
                mesa_nombre, time_since_last, MIN_SIGNAL_INTERVAL
            )
            return False

    timestamp = datetime.now().strftime("%H:%M:%S")
    apuesta_upper = senal_info['apuesta'].upper()
    colores = _mapear_colores_apuesta(apuesta_upper)
    color_apuesta = colores['color_apuesta']
    color_fondo = colores['color_fondo']
    emoji_destacado = colores['emoji_destacado']
    confianza = colores['confianza']
    nombre_apuesta = colores['nombre_apuesta']

    historial_completo = (
        mesa_data['historial_resultados']
        if 'historial_resultados' in mesa_data
        else senal_info.get('historial_completo', [])
    )
    historial_reciente = senal_info.get('historial_reciente', [])
    historial_completo_emojis = _generar_historial_emojis(historial_completo)
    historial_reciente_emojis = _generar_historial_emojis(historial_reciente)

    mensaje = (
        f"🚨 **¡SEÑAL DE BACARÁ DETECTADA!** 🚨\n\n"
        f"🎰 **Mesa:** {senal_info['mesa']}\n"
        f"🔗 **Enlace:** {senal_info['url']}\n\n"
        f"{color_fondo} **APUESTA RECOMENDADA:**\n"
        f"**{color_apuesta} {nombre_apuesta} {color_apuesta}**\n"
        f"(Estrategia: {senal_info['estrategia']})\n\n"
        f"{emoji_destacado} **CONFIDENCIA:** **{confianza}**\n"
        f"⏱️ **Hora de la Señal:** {timestamp}\n"
        f"📊 **Historial reciente:** "
        f"`{''.join(historial_reciente_emojis)}`\n"
        f"📜 **Historial completo:**\n"
        f"`{''.join(historial_completo_emojis)}`\n\n"
        f"{color_apuesta} **SEÑAL ACTIVA** {color_apuesta}"
    )

    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=mensaje,
            parse_mode='Markdown'
        )

        seguidilla = _detectar_seguidilla(historial_completo)
        if seguidilla:
            valor, cantidad = seguidilla
            mensaje_racha = (
                f"⚡ ¡Seguidilla detectada! {cantidad} veces seguidas: {valor}"
            )
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=mensaje_racha
            )

        last_signal_time[mesa_nombre] = current_time
        predicciones_pendientes[mesa_nombre] = {
            'apuesta': nombre_apuesta,
            'timestamp': current_time
        }
        logger.info("✅ Señal enviada para la mesa: %s", senal_info['mesa'])
        return True

    except TelegramError as e:
        logger.error("❌ ERROR al enviar mensaje a Telegram: %s", e)
        if "Flood control" in str(e) or "Too Many Requests" in str(e):
            logger.error("🚫 FLOOD CONTROL DETECTADO")
            last_signal_time[mesa_nombre] = current_time
        return False

  
# --- Bucle Principal de Monitoreo ---
async def bucle_monitoreo(intervalo_segundos: int | None = None):
    """
    Bucle principal que monitorea todas las mesas y genera señales
    usando detección de timing óptimo.
    """

    if intervalo_segundos is None:
        intervalo_segundos = INTERVALO_MONITOREO

    logger.info("--- INICIANDO BOT DE MONITOREO DE BACARÁ ---")
    logger.info(
        "Monitoreando %d mesas. Intervalo de chequeo: %d segundos.",
        len(MESA_NOMBRES), intervalo_segundos
    )
    logger.info("⏰ Sistema de timing inteligente activado")

    mesas = inicializar_mesas()
    await _init_playwright_scraper()

    await _inicializar_historiales(mesas)
    logger.info("✅ Historial inicial cargado para todas las mesas.")
    logger.info(game_monitor.get_status_report())

    round_start_times: Dict[str, Optional[float]] = dict.fromkeys(
        mesas.keys(), None
    )

    iteration_count = 0
    while True:
        iteration_count += 1
        for mesa_nombre, mesa_data in mesas.items():
            try:
                game_id = mesa_data.get('game_id')
                nuevo_resultado = (
                    await obtener_nuevo_resultado_async(mesa_data, game_id)
                )
                historial = mesa_data['historial_resultados']
                if len(historial) > 0 and historial[-1] != nuevo_resultado:
                    round_start_times[mesa_nombre] = time.time()
                    game_monitor.start_new_round()
                    logger.debug("🎲 Nueva ronda detectada en %s", mesa_nombre)
                    _procesar_prediccion_pendiente(
                        mesa_nombre,
                        nuevo_resultado
                    )

                # Actualizar historial y reportar inmediatamente
                _actualizar_historial(mesa_data, nuevo_resultado)
                logger.info(game_monitor.get_status_report())

                timing_check = game_monitor.check_signal_timing()
                if timing_check['should_signal']:
                    await _analizar_y_enviar_senal(mesa_nombre, mesa_data)

            except BaseException as exc:
                logger.error("❌ Error procesando %s: %s", mesa_nombre, exc)
                raise

        if iteration_count % 10 == 0:
            logger.info(game_monitor.get_status_report())

        await asyncio.sleep(intervalo_segundos)


if __name__ == "__main__":
    try:
        asyncio.run(bucle_monitoreo())
    except KeyboardInterrupt:
        logger.info("\n🛑 Bot detenido por el usuario.")
    except BaseException as exc:
        logger.error("❌ Error crítico: %s", exc)
        raise
