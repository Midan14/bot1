# baccarat_bot/main_advanced.py

import asyncio
import logging
import signal
import sys
import time
from datetime import datetime
from typing import Dict
from telegram import Bot

# Importar todos los módulos nuevos
from baccarat_bot.config import (
    TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, INTERVALO_MONITOREO, 
    LOG_LEVEL
)
from database.models import db_manager
from stats_module.analyzer import analyzer
from baccarat_bot.tables import inicializar_mesas, MESA_NOMBRES
from data_source import obtener_nuevo_resultado, simular_historial_inicial
from baccarat_bot.signal_logic import actualizar_historial, analizar_y_generar_senales
from telegram_bot.interactive_bot import interactive_bot
from api.server import iniciar_servidor
from utils.bot_state import bot_state
from utils.metrics import record_signal_metric, record_error_metric
from integrations.web_scraper import data_source_manager

# Configurar logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importar sistema de colores (opcional)
try:
    from sistema_colores import monitor_estado
    SISTEMA_COLORES_DISPONIBLE = True
except ImportError:
    class MonitorEstadoSimple:
        def registrar_señal(self, mesa, estado, detalles=None):
            pass
    
    monitor_estado = MonitorEstadoSimple()
    SISTEMA_COLORES_DISPONIBLE = False
    logger.warning("Sistema de colores no disponible, usando implementación simple")

# Validar configuración esencial de Telegram
if not TELEGRAM_TOKEN:
    raise ValueError("El TELEGRAM_TOKEN no está configurado. Por favor, añádelo a tu archivo de configuración.")
if not TELEGRAM_CHAT_ID:
    raise ValueError("El TELEGRAM_CHAT_ID no está configurado. Por favor, añádelo a tu archivo de configuración.")

bot = Bot(token=TELEGRAM_TOKEN)


class AdvancedBaccaratBot:
    """Bot avanzado de Baccarat con múltiples funcionalidades"""
    
    def __init__(self):
        self.mesas = {}
        self.running = False
        self.interactive_bot_task = None
        self.api_server_task = None
        self.main_loop_task = None
        self.state = bot_state
    
    async def enviar_senal_telegram(self, senal_info: Dict, exito: bool = True, mensaje_personalizado: str = None):
        """Envía señal mejorada con información adicional"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Determinar color según el tipo de apuesta
        if senal_info['apuesta'].upper() == 'BANCA':
            color_apuesta = "🟢"
            color_fondo = "💚"
            confianza = "🟢 ALTA"
        elif senal_info['apuesta'].upper() == 'JUGADOR':
            color_apuesta = "🔴"
            color_fondo = "❤️"
            confianza = "🔴 ALTA"
        else:
            color_apuesta = "🟡"
            color_fondo = "💛"
            confianza = "🟡 MEDIA"
        
        # Obtener estadísticas adicionales
        stats = db_manager.obtener_estadisticas_mesa(senal_info['mesa'])
        
        # Formato del mensaje mejorado
        mensaje = f"""🚨 **¡SEÑALES DE BACARÁ DETECTADAS!** 🚨

🎰 **Mesa:** {senal_info['mesa']}
🔗 **Enlace:** {senal_info['url']}

{color_fondo} **SEÑALES DETECTADAS:** 
{mensaje_personalizado if mensaje_personalizado else ''}
📊 **Historial Reciente:** `{', '.join(senal_info['historial_reciente'])}`
⏱️ **Hora de la Señal:** {timestamp}
        """
        
        # Agregar estadísticas si están disponibles
        if stats:
            mensaje += f"""
📈 **Estadísticas de la mesa:**
• Total jugadas: {stats['total_jugadas']}
• Precisión de señales: {stats['precision_senales']:.1f}%
            """
        
        mensaje += f"\n{color_apuesta} **SEÑAL ACTIVA** {color_apuesta}"
        
        try:
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=mensaje,
                parse_mode='Markdown'
            )
            logger.info(f"✅ Señal enviada exitosamente a Telegram para la mesa: {senal_info['mesa']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ ERROR al enviar mensaje a Telegram: {e}")
            return False
    
    async def procesar_mesa(self, nombre_mesa: str, mesa_data: Dict):
        """Procesa una mesa individual usando el gestor de estado centralizado"""
        try:
            # 1. Obtener el nuevo resultado y actualizar historial
            nuevo_resultado = obtener_nuevo_resultado(mesa_data)
            if nuevo_resultado:
                db_manager.registrar_resultado(nombre_mesa, nuevo_resultado)
                actualizar_historial(mesa_data, nuevo_resultado)

            # 2. Analizar y generar todas las señales posibles
            historial = mesa_data['historial_resultados']
            senales = analizar_y_generar_senales(historial)

            if senales:
                # 3. Verificar si se puede enviar la señal usando BotState
                can_send, reason = self.state.can_send_signal(nombre_mesa)
                if can_send:
                    logger.info(f"Señal permitida para {nombre_mesa} por: {reason}")

                    # Preparar mensaje con todas las señales
                    mensaje_senales = ""
                    for idx, (apuesta, estrategia) in enumerate(senales):
                        if idx == 0:
                            mensaje_senales += f"⭐ *Más fuerte*: *{apuesta.upper()}* _(Estrategia: {estrategia})_\n"
                        else:
                            mensaje_senales += f"- {apuesta.upper()} _(Estrategia: {estrategia})_\n"

                    senal_info = {
                        "apuesta": senales[0][0],
                        "estrategia": senales[0][1],
                        "mesa": nombre_mesa,
                        "url": mesa_data.get("url", ""),
                        "historial_reciente": historial[-10:],
                        "mensaje_senales": mensaje_senales
                    }

                    # 4. Enviar la señal y registrarla
                    start_time = time.time()
                    exito = await self.enviar_senal_telegram(senal_info, mensaje_personalizado=mensaje_senales)
                    response_time = time.time() - start_time

                    # Registrar métrica de la señal
                    record_signal_metric(nombre_mesa, success=exito, response_time=response_time)

                    if exito:
                        self.state.register_signal_sent(nombre_mesa)
                        db_manager.registrar_senal(
                            mesa_nombre=nombre_mesa,
                            tipo_senal=senales[0][1],
                            resultado_recomendado=senales[0][0],
                            historial=historial[-5:],
                            exito=True
                        )
                        monitor_estado.registrar_señal(nombre_mesa, 'exito')
                else:
                    logger.debug(f"Señal bloqueada para {nombre_mesa}: {reason}")

            # 5. Generar alertas (si corresponde)
            await self.verificar_alertas(nombre_mesa, mesa_data)

        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Error procesando mesa {nombre_mesa}: {e}")
            self.state.record_error(e)
            record_error_metric(error_type=error_type, error_message=str(e))
    
    async def verificar_alertas(self, nombre_mesa: str, mesa_data: Dict):
        """Verifica y genera alertas para una mesa"""
        try:
            # Análisis de tendencias
            tendencia = analyzer.analizar_tendencias_mesa(nombre_mesa, dias=1)
            
            if 'tendencia_actual' in tendencia:
                tend = tendencia['tendencia_actual']['tendencia']
                
                # Alertar por tendencias fuertes
                if tend in ['favor_banca', 'favor_jugador']:
                    logger.info(f"Tendencia fuerte detectada en {nombre_mesa}: {tend}")
            
            # Verificar precisión de señales
            stats = db_manager.obtener_estadisticas_mesa(nombre_mesa)
            if stats and stats['senales_generadas'] > 10:
                if stats['precision_senales'] < 30:
                    logger.warning(f"Baja precisión en {nombre_mesa}: {stats['precision_senales']:.1f}%")
            
        except Exception as e:
            logger.error(f"Error verificando alertas para {nombre_mesa}: {e}")
    
    async def bucle_monitoreo(self, intervalo_segundos: int = None):
        """Bucle principal de monitoreo mejorado"""
        if intervalo_segundos is None:
            intervalo_segundos = INTERVALO_MONITOREO
            
        logger.info("--- INICIANDO BOT DE MONITOREO DE BACARÁ AVANZADO ---")
        logger.info(f"Monitoreando {len(MESA_NOMBRES)} mesas. Intervalo: {intervalo_segundos}s.")
        logger.info("Funcionalidades activas: Estadísticas, API, Bot interactivo, Estrategias múltiples")
        
        # 1. Inicializar todas las mesas
        self.mesas = inicializar_mesas()
        
        # 2. Registrar mesas en base de datos
        for nombre, data in self.mesas.items():
            db_manager.registrar_mesa(nombre, data['url'])
        
        # 3. Simular historial inicial para cada mesa
        for nombre, data in self.mesas.items():
            data['historial_resultados'] = simular_historial_inicial(longitud=5)
            logger.debug(f"Mesa {nombre} inicializada con historial: {data['historial_resultados']}")
        
        # 4. Bucle de monitoreo continuo
        try:
            while self.running:
                timestamp = datetime.now().strftime('%H:%M:%S')
                logger.info(f"--- Chequeo de Mesas: {timestamp} ---")
                
                # Procesar cada mesa
                tasks = []
                for nombre_mesa, mesa_data in self.mesas.items():
                    task = self.procesar_mesa(nombre_mesa, mesa_data)
                    tasks.append(task)
                
                # Ejecutar todas las tareas en paralelo
                await asyncio.gather(*tasks, return_exceptions=True)
                
                # Esperar el intervalo antes del siguiente chequeo
                await asyncio.sleep(intervalo_segundos)
        
        except KeyboardInterrupt:
            logger.info("--- Bot de Monitoreo Detenido por el Usuario ---")
        except Exception as e:
            logger.error(f"--- ERROR CRÍTICO EN EL BUCLE PRINCIPAL ---")
            logger.error(f"Error: {e}")
            raise
    
    async def iniciar_api_server(self):
        """Inicia el servidor API en segundo plano"""
        from config_enhanced import API_CONFIG
        host = API_CONFIG.get('host', '0.0.0.0')
        port = API_CONFIG.get('port', 8000)
        debug = API_CONFIG.get('debug', False)
        
        try:
            logger.info(f"Iniciando servidor API en {host}:{port}...")
            # Ejecutar en un hilo separado para no bloquear el loop principal
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, iniciar_servidor, host, port, debug)
        except Exception as e:
            logger.error(f"Error iniciando servidor API: {e}")
    
    async def iniciar_bot_interactivo(self):
        """Inicia el bot interactivo de Telegram"""
        try:
            logger.info("Iniciando bot interactivo de Telegram...")
            await interactive_bot.run()
        except Exception as e:
            logger.error(f"Error iniciando bot interactivo: {e}")
    
    async def generar_reporte_diario(self):
        """Genera y envía reporte diario"""
        try:
            logger.info("Generando reporte diario...")
            reporte = analyzer.generar_reporte_general()
            
            if 'error' not in reporte:
                # Guardar en base de datos o enviar por email
                logger.info("Reporte diario generado exitosamente")
                
                # Enviar resumen por Telegram si hay actividad
                if reporte['resumen_general']['total_jugadas'] > 0:
                    mensaje = f"""
📊 **REPORTE DIARIO** 📊

**Resumen del día:**
• Mesas activas: {reporte['resumen_general']['total_mesas_monitoreadas']}
• Total jugadas: {reporte['resumen_general']['total_jugadas']:,}
• Señales generadas: {reporte['resumen_general']['total_senales_generadas']}
• Precisión general: {reporte['resumen_general']['precision_general']:.1f}%

📅 {datetime.now().strftime('%d/%m/%Y')}
                    """
                    
                    try:
                        await bot.send_message(
                            chat_id=TELEGRAM_CHAT_ID,
                            text=mensaje,
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logger.error(f"Error enviando reporte diario: {e}")
        
        except Exception as e:
            logger.error(f"Error generando reporte diario: {e}")
    
    async def start(self):
        """Inicia todos los servicios del bot"""
        self.running = True
        
        try:
            # Inicializar conexiones
            await data_source_manager.init()
            
            # Programar tareas
            tasks = []
            
            # Tarea principal de monitoreo
            tasks.append(asyncio.create_task(self.bucle_monitoreo()))
            
            # Tarea del bot interactivo (si está configurado)
            if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
                tasks.append(asyncio.create_task(self.iniciar_bot_interactivo()))
            
            # Tarea del servidor API (reactivada)
            tasks.append(asyncio.create_task(self.iniciar_api_server()))
            
            # Tarea de reporte diario (ejecutar a medianoche)
            # tasks.append(asyncio.create_task(self.programar_reporte_diario()))
            
            # Esperar a que terminen todas las tareas
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except KeyboardInterrupt:
            logger.info("Bot detenido por el usuario")
        except Exception as e:
            logger.error(f"Error crítico en el bot: {e}")
        finally:
            await self.stop()
    
    async def stop(self):
        """Detiene todos los servicios"""
        logger.info("Deteniendo bot avanzado...")
        self.running = False
        
        # Cerrar conexiones
        await data_source_manager.close()
        
        logger.info("Bot avanzado detenido exitosamente")


def signal_handler(signum, frame):
    """Manejador de señales para cierre graceful"""
    logger.info(f"Señal {signum} recibida, cerrando graceful...")
    sys.exit(0)


async def main():
    """Función principal"""
    # Registrar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        logger.info("Iniciando Bot de Baccarat Avanzado...")
        
        # Crear e iniciar el bot
        advanced_bot = AdvancedBaccaratBot()
        await advanced_bot.start()
        
    except KeyboardInterrupt:
        logger.info("Bot detenido por el usuario")
    except Exception as e:
        logger.error(f"Error crítico en main(): {e}")
        raise


if __name__ == '__main__':
    asyncio.run(main())
