# baccarat_bot/main_enhanced.py

"""
Bot de Baccarat mejorado con todas las optimizaciones integradas:
- Anti-detección avanzada
- Sincronización en tiempo real
- Estrategias conservadoras
- Validación de datos
- Logging estructurado
- Manejo robusto de errores
"""

import asyncio
import signal
import sys
from datetime import datetime
from typing import Dict, Optional
from telegram import Bot

# Importar configuración unificada
from baccarat_bot.config_unified import config

# Importar módulos mejorados
from baccarat_bot.integrations.enhanced_scraper import enhanced_scraper
from baccarat_bot.integrations.realtime_sync import GameState
from baccarat_bot.strategies.safe_strategies import get_safest_signal
from baccarat_bot.database.models import db_manager
from baccarat_bot.stats_module.analyzer import analyzer
from baccarat_bot.utils.bot_state import bot_state
from baccarat_bot.utils.logging_config import setup_logging, get_structured_logger
from baccarat_bot.utils.validators import validar_senal
from baccarat_bot.utils.error_handler import ErrorContext

# Configurar logging estructurado
setup_logging(
    log_level=config.logging.level,
    log_file=config.logging.file,
    use_json=False,  # Cambiar a True para producción
    use_colors=True
)

logger = get_structured_logger(__name__)

# Validar configuración
try:
    config.validate_all()
except ValueError as e:
    logger.critical(f"Error en configuración: {e}")
    sys.exit(1)

# Inicializar bot de Telegram
bot = Bot(token=config.telegram.token)


class EnhancedBaccaratBot:
    """
    Bot mejorado de Baccarat con todas las optimizaciones.
    
    Características:
    - Scraping con anti-detección avanzada
    - Sincronización en tiempo real con las mesas
    - Estrategias de apuesta conservadoras y seguras
    - Validación automática de datos
    - Logging estructurado
    - Manejo robusto de errores
    """
    
    def __init__(self):
        self.mesas = {}
        self.running = False
        self.state = bot_state
        
        # Configuración de mesas
        self.mesa_configs = [
            {
                'name': 'XXXtreme Lightning Baccarat',
                'url': f"{config.scraper.base_url}XXXtreme-Lightning-Baccarat",
                'game_id': '97411' # Nuevo ID para la mesa
            },
            {
                'name': 'Speed Baccarat 1',
                'url': f"{config.scraper.base_url}speed-baccarat-1",
                'game_id': '97408'
            },
            {
                'name': 'Speed Baccarat 2',
                'url': f"{config.scraper.base_url}speed-baccarat-2",
                'game_id': '97409'
            },
        ]
    
    async def enviar_senal_telegram(
        self,
        mesa: str,
        apuesta: str,
        estrategia: str,
        confianza: int,
        historial: list,
        tiempo_restante: Optional[int] = None
    ) -> bool:
        """
        Envía señal optimizada a Telegram con información completa.
        
        Args:
            mesa: Nombre de la mesa
            apuesta: Resultado recomendado (BANCA, JUGADOR, EMPATE)
            estrategia: Nombre de la estrategia
            confianza: Nivel de confianza (0-100)
            historial: Historial de resultados
            tiempo_restante: Segundos restantes para apostar
            
        Returns:
            True si se envió correctamente
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Emojis según la apuesta
        emoji_map = {
            'BANCA': '🟢',
            'JUGADOR': '🔴',
            'EMPATE': '🟡'
        }
        emoji = emoji_map.get(apuesta.upper(), '⚪')
        
        # Construir mensaje
        mensaje = f"""
🎰 **SEÑAL DE BACCARAT** {emoji}

📍 **Mesa:** {mesa}
{emoji} **Apostar a:** {apuesta.upper()}
📊 **Estrategia:** {estrategia}
🎯 **Confianza:** {confianza}% {'🔥' if confianza >= 90 else '✅' if confianza >= 80 else '⚠️'}

📈 **Historial reciente:** `{', '.join(historial[-10:])}`
"""
        
        if tiempo_restante:
            mensaje += f"⏱️ **Tiempo restante:** {tiempo_restante} segundos\n"
        
        # Estadísticas de la mesa
        stats = db_manager.obtener_estadisticas_mesa(mesa)
        if stats:
            mensaje += f"""
📊 **Estadísticas de la mesa:**
• Total jugadas: {stats['total_jugadas']}
• Precisión: {stats['precision_senales']:.1f}%
• Señales generadas: {stats['senales_generadas']}
"""
        
        mensaje += f"\n⏰ **Hora:** {timestamp}"
        
        try:
            await bot.send_message(
                chat_id=config.telegram.chat_id,
                text=mensaje,
                parse_mode='Markdown'
            )
            
            logger.log_signal(
                mesa=mesa,
                estrategia=estrategia,
                resultado=apuesta,
                confianza=confianza
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error enviando señal a Telegram: {e}", exc_info=True)
            return False
    
    async def procesar_mesa(self, mesa_config: Dict):
        """
        Procesa una mesa individual con todas las optimizaciones.
        
        Args:
            mesa_config: Configuración de la mesa
        """
        mesa_nombre = mesa_config['name']
        
        with ErrorContext(
            operation='procesar_mesa',
            context_data={'mesa': mesa_nombre},
            raise_on_error=False
        ):
            # Realizar scraping con anti-detección
            datos_mesa = await enhanced_scraper.scrape_table(
                table_name=mesa_nombre,
                table_url=mesa_config['url'],
                game_id=mesa_config['game_id']
            )
            
            if not datos_mesa:
                logger.warning(f"No se pudieron obtener datos de {mesa_nombre}")
                return
            
            # Verificar estado del juego
            estado = datos_mesa.get('state')
            if estado == GameState.SHUFFLING.value:
                logger.info(f"Mesa {mesa_nombre} está barajando, esperando...")
                return
            
            # Obtener historial
            historial = datos_mesa.get('history', [])
            if len(historial) < 20:
                logger.debug(f"Historial insuficiente para {mesa_nombre}: {len(historial)} resultados")
                return
            
            # Registrar último resultado si es nuevo
            ultimo_resultado = datos_mesa.get('last_result')
            if ultimo_resultado:
                db_manager.registrar_resultado(mesa_nombre, ultimo_resultado)
            
            # Analizar con estrategias seguras
            senal = get_safest_signal(historial)
            
            if not senal:
                logger.debug(f"No hay señal segura para {mesa_nombre}")
                return
            
            apuesta, estrategia, confianza = senal
            
            # Verificar si se puede enviar señal
            can_send, reason = self.state.can_send_signal(mesa_nombre)
            if not can_send:
                logger.debug(f"Señal bloqueada para {mesa_nombre}: {reason}")
                return
            
            # Verificar timing óptimo
            should_send = datos_mesa.get('should_send_signal', False)
            if not should_send:
                logger.debug(f"Timing no óptimo para {mesa_nombre}")
                return
            
            # Validar señal antes de enviar
            try:
                validar_senal(
                    mesa=mesa_nombre,
                    tipo_senal=estrategia,
                    resultado_recomendado=apuesta,
                    historial=historial[-5:],
                    confianza=confianza
                )
            except Exception as e:
                logger.error(f"Señal inválida: {e}")
                return
            
            # Enviar señal
            tiempo_restante = datos_mesa.get('time_remaining')
            exito = await self.enviar_senal_telegram(
                mesa=mesa_nombre,
                apuesta=apuesta,
                estrategia=estrategia,
                confianza=confianza,
                historial=historial,
                tiempo_restante=tiempo_restante
            )
            
            if exito:
                # Registrar señal en base de datos
                self.state.register_signal_sent(mesa_nombre)
                db_manager.registrar_senal(
                    mesa_nombre=mesa_nombre,
                    tipo_senal=estrategia,
                    resultado_recomendado=apuesta,
                    historial=historial[-5:],
                    exito=True
                )
                
                logger.info(
                    f"✅ Señal enviada: {mesa_nombre} -> {apuesta} "
                    f"({estrategia}, {confianza}%)"
                )
    
    async def bucle_monitoreo(self):
        """Bucle principal de monitoreo mejorado"""
        logger.info("🚀 Iniciando bot mejorado de Baccarat...")
        logger.info(f"Monitoreando {len(self.mesa_configs)} mesas")
        logger.info(f"Intervalo: {config.monitoring.intervalo_monitoreo}s")
        logger.info("Características: Anti-detección, Sincronización RT, Estrategias seguras")
        
        # Inicializar scraper
        await enhanced_scraper.init(headless=True)
        
        # Registrar mesas en base de datos
        for mesa_config in self.mesa_configs:
            db_manager.registrar_mesa(mesa_config['name'], mesa_config['url'])
        
        try:
            ciclo = 0
            while self.running:
                ciclo += 1
                timestamp = datetime.now().strftime('%H:%M:%S')
                logger.info(f"--- Ciclo {ciclo}: {timestamp} ---")
                
                # Procesar mesas en paralelo
                tasks = [
                    self.procesar_mesa(mesa_config)
                    for mesa_config in self.mesa_configs
                ]
                await asyncio.gather(*tasks, return_exceptions=True)
                
                # Mostrar estadísticas del PagePool cada 10 ciclos
                if ciclo % 10 == 0:
                    stats = enhanced_scraper.get_pool_stats()
                    logger.info(f"PagePool: {stats}")
                
                # Rotar identidad cada 50 ciclos para evitar detección
                if ciclo % 50 == 0:
                    logger.info("Rotando identidad del navegador...")
                    await enhanced_scraper.rotate_identity()
                
                # Esperar antes del siguiente ciclo
                await asyncio.sleep(config.monitoring.intervalo_monitoreo)
        
        except KeyboardInterrupt:
            logger.info("Bot detenido por el usuario")
        except Exception as e:
            logger.error(f"Error crítico en bucle principal: {e}", exc_info=True)
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Limpia recursos al finalizar"""
        logger.info("Limpiando recursos...")
        
        try:
            # Cerrar scraper
            await enhanced_scraper.close()
            
            logger.info("✅ Recursos liberados correctamente")
        except Exception as e:
            logger.error(f"Error en cleanup: {e}")
    
    async def start(self):
        """Inicia el bot"""
        self.running = True
        
        # Manejar señales de sistema
        def signal_handler(sig, frame):
            logger.info(f"Señal {sig} recibida, deteniendo bot...")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Iniciar bucle de monitoreo
        await self.bucle_monitoreo()
    
    async def stop(self):
        """Detiene el bot"""
        logger.info("Deteniendo bot...")
        self.running = False
        await self.cleanup()


async def main():
    """Función principal"""
    bot = EnhancedBaccaratBot()
    
    try:
        await bot.start()
    except Exception as e:
        logger.critical(f"Error fatal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
