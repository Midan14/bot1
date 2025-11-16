# baccarat_bot/telegram_bot/interactive_bot.py

import logging
import asyncio
from datetime import datetime
from typing import Dict, Any
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from database.models import db_manager
from stats_module.analyzer import analyzer
from tables import MESA_NOMBRES

logger = logging.getLogger(__name__)


class InteractiveTelegramBot:
    """Bot de Telegram interactivo con comandos y respuestas"""
    
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Configura los manejadores de comandos"""
        # Comandos básicos
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("mesas", self.mesas_command))
        self.application.add_handler(CommandHandler("alertas", self.alertas_command))
        self.application.add_handler(CommandHandler("reporte", self.reporte_command))
        
        # Comandos de análisis
        self.application.add_handler(CommandHandler("tendencia", self.tendencia_command))
        self.application.add_handler(CommandHandler("historial", self.historial_command))
        
        # Manejador de callbacks para botones inline
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /start"""
        mensaje = """
🎰 **Baccarat Bot Interactivo** 🎰

¡Bienvenido! Soy tu asistente para el monitoreo de mesas de Baccarat.

📋 **Comandos disponibles:**
• /help - Muestra esta ayuda
• /status - Estado general del bot
• /stats - Estadísticas generales
• /mesas - Lista de mesas monitoreadas
• /alertas - Alertas activas
• /reporte - Reporte completo
• /tendencia [mesa] - Análisis de tendencias
• /historial [mesa] - Historial de resultados

🔔 *El bot está monitoreando continuamente las mesas en busca de señales.*
        """
        
        await update.message.reply_text(mensaje, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /help"""
        await self.start_command(update, context)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /status - Estado del bot"""
        try:
            # Obtener estadísticas generales
            estadisticas = db_manager.obtener_todas_las_estadisticas()
            
            total_mesas = len([e for e in estadisticas if e['total_jugadas'] > 0])
            total_jugadas = sum(e['total_jugadas'] for e in estadisticas)
            total_senales = sum(e['senales_generadas'] for e in estadisticas)
            
            mensaje = f"""
📊 **ESTADO DEL BOT** 📊

✅ **Bot activo y monitoreando**
🕐 Última actualización: {datetime.now().strftime('%H:%M:%S')}

📈 **Resumen de actividad:**
• Mesas activas: {total_mesas}
• Total jugadas registradas: {total_jugadas}
• Señales generadas: {total_senales}
• Mesas monitoreadas: {len(MESA_NOMBRES)}
            """
            
            await update.message.reply_text(mensaje, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error en comando status: {e}")
            await update.message.reply_text("❌ Error al obtener el estado del bot")
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /stats - Estadísticas generales"""
        try:
            reporte = analyzer.generar_reporte_general()
            
            if 'error' in reporte:
                await update.message.reply_text("❌ No hay datos disponibles aún")
                return
            
            resumen = reporte['resumen_general']
            
            mensaje = f"""
📈 **ESTADÍSTICAS GENERALES** 📈

🔢 **Resumen:**
• Total de mesas: {resumen['total_mesas_monitoreadas']}
• Jugadas registradas: {resumen['total_jugadas']}
• Señales generadas: {resumen['total_senales_generadas']}
• Precisión general: {resumen['precision_general']:.1f}%

📊 **Distribución global:**
• Victorias Banca: {reporte['distribucion_global']['total_banca']}
• Victorias Jugador: {reporte['distribucion_global']['total_jugador']}
• Empates: {reporte['distribucion_global']['total_empate']}
            """
            
            await update.message.reply_text(mensaje, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error en comando stats: {e}")
            await update.message.reply_text("❌ Error al obtener estadísticas")
    
    async def mesas_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /mesas - Lista de mesas"""
        try:
            estadisticas = db_manager.obtener_todas_las_estadisticas()
            
            # Crear mensaje con mesas activas
            mensaje = "🎰 **MESAS MONITOREADAS** 🎰\n\n"
            mensaje += "📊 **Mesas con actividad reciente:**\n"
            
            mesas_activas = [e for e in estadisticas if e['total_jugadas'] > 0]
            mesas_activas.sort(key=lambda x: x['total_jugadas'], reverse=True)
            
            for i, mesa in enumerate(mesas_activas[:10], 1):
                mensaje += f"{i}. **{mesa['mesa']}** - {mesa['total_jugadas']} jugadas\n"
            
            mensaje += f"\n📋 Total de mesas monitoreadas: {len(MESA_NOMBRES)}\n"
            mensaje += f"✅ Mesas activas: {len(mesas_activas)}"
            
            # Agregar botones para ver más detalles
            keyboard = []
            for mesa in mesas_activas[:5]:
                keyboard.append([InlineKeyboardButton(
                    f"📊 {mesa['mesa']}",
                    callback_data=f"detalle_mesa:{mesa['mesa']}"
                )])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                mensaje, 
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error en comando mesas: {e}")
            await update.message.reply_text("❌ Error al obtener lista de mesas")
    
    async def alertas_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /alertas - Alertas activas"""
        try:
            alertas = analyzer.generar_alertas()
            
            if not alertas:
                await update.message.reply_text("✅ No hay alertas activas en este momento")
                return
            
            mensaje = "🚨 **ALERTAS ACTIVAS** 🚨\n\n"
            
            for alerta in alertas:
                mensaje += f"• {alerta['mensaje']}\n"
            
            await update.message.reply_text(mensaje, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error en comando alertas: {e}")
            await update.message.reply_text("❌ Error al obtener alertas")
    
    async def reporte_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /reporte - Reporte completo"""
        try:
            reporte = analyzer.generar_reporte_general()
            
            if 'error' in reporte:
                await update.message.reply_text("❌ No hay datos suficientes para generar el reporte")
                return
            
            mensaje = f"""
📊 **REPORTE COMPLETO** 📊

**Resumen General:**
• Mesas monitoreadas: {reporte['resumen_general']['total_mesas_monitoreadas']}
• Total jugadas: {reporte['resumen_general']['total_jugadas']:,}
• Señales generadas: {reporte['resumen_general']['total_senales_generadas']}
• Precisión: {reporte['resumen_general']['precision_general']:.1f}%

**Top 3 Mesas Más Activas:**
"""
            
            for i, mesa in enumerate(reporte['top_mesas_activas'][:3], 1):
                mensaje += f"{i}. **{mesa['mesa']}**: {mesa['total_jugadas']} jugadas\n"
            
            mensaje += "\n**Top 3 Mejores Precisión:**"
            for i, mesa in enumerate(reporte['top_mesas_precision'][:3], 1):
                mensaje += f"{i}. **{mesa['mesa']}**: {mesa['precision_senales']:.1f}%\n"
            
            mensaje += f"\n📅 Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            
            await update.message.reply_text(mensaje, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error en comando reporte: {e}")
            await update.message.reply_text("❌ Error al generar el reporte")
    
    async def tendencia_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /tendencia [nombre_mesa]"""
        try:
            if not context.args:
                # Mostrar lista de mesas disponibles
                keyboard = []
                for nombre in MESA_NOMBRES[:10]:  # Limitar a 10 para no saturar
                    keyboard.append([InlineKeyboardButton(
                        f"📊 {nombre}",
                        callback_data=f"tendencia:{nombre}"
                    )])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    "📊 **ANÁLISIS DE TENDENCIAS** 📊\n\n"
                    "Selecciona una mesa para ver su análisis de tendencias:",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                return
            
            mesa_nombre = ' '.join(context.args)
            tendencia = analyzer.analizar_tendencias_mesa(mesa_nombre)
            
            if 'error' in tendencia:
                await update.message.reply_text(f"❌ No hay datos suficientes para {mesa_nombre}")
                return
            
            mensaje = f"""
📈 **ANÁLISIS DE TENDENCIAS** 📈
**Mesa:** {tendencia['mesa']}

📊 **Distribución:**
• Banca: {tendencia['distribucion']['banca']} ({tendencia['distribucion']['porcentaje_banca']:.1f}%)
• Jugador: {tendencia['distribucion']['jugador']} ({tendencia['distribucion']['porcentaje_jugador']:.1f}%)
• Empate: {tendencia['distribucion']['empate']} ({tendencia['distribucion']['porcentaje_empate']:.1f}%)

🔥 **Rachas detectadas:**
• Máxima racha Banca: {tendencia['rachas']['rachas_banca']['maxima']}
• Máxima racha Jugador: {tendencia['rachas']['rachas_jugador']['maxima']}

📈 **Tendencia actual:** {tendencia['tendencia_actual']['tendencia']}
            """
            
            await update.message.reply_text(mensaje, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error en comando tendencia: {e}")
            await update.message.reply_text("❌ Error al analizar tendencias")
    
    async def historial_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja el comando /historial [nombre_mesa]"""
        try:
            if not context.args:
                await update.message.reply_text(
                    "❌ Por favor especifica el nombre de la mesa.\n"
                    "Ejemplo: `/historial Speed Baccarat 1`",
                    parse_mode='Markdown'
                )
                return
            
            mesa_nombre = ' '.join(context.args)
            historial = db_manager.obtener_historial_resultados(mesa_nombre, 20)
            
            if not historial:
                await update.message.reply_text(f"❌ No hay historial disponible para {mesa_nombre}")
                return
            
            mensaje = f"""
📋 **HISTORIAL DE RESULTADOS** 📋
**Mesa:** {mesa_nombre}

**Últimos 20 resultados:**
"""
            
            for i, resultado in enumerate(historial, 1):
                emoji = {'B': '🟢', 'P': '🔴', 'E': '🟡'}.get(resultado['resultado'], '⚪')
                fecha = datetime.fromisoformat(resultado['timestamp']).strftime('%H:%M:%S')
                mensaje += f"{i:2d}. {emoji} {resultado['resultado']} - {fecha}\n"
            
            await update.message.reply_text(mensaje, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error en comando historial: {e}")
            await update.message.reply_text("❌ Error al obtener el historial")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja los callbacks de botones inline"""
        query = update.callback_query
        await query.answer()
        
        try:
            data = query.data
            parts = data.split(':', 1)
            
            if parts[0] == 'detalle_mesa':
                mesa_nombre = parts[1]
                estadisticas = db_manager.obtener_estadisticas_mesa(mesa_nombre)
                
                if not estadisticas:
                    await query.edit_message_text("❌ No hay datos para esta mesa")
                    return
                
                mensaje = f"""
📊 **DETALLES DE MESA** 📊
**{mesa_nombre}**

📈 **Estadísticas:**
• Total jugadas: {estadisticas['total_jugadas']}
• Victorias Banca: {estadisticas['banca_victorias']} ({estadisticas['win_rate_banca']:.1f}%)
• Victorias Jugador: {estadisticas['jugador_victorias']} ({estadisticas['win_rate_jugador']:.1f}%)
• Empates: {estadisticas['empates']} ({estadisticas['win_rate_empates']:.1f}%)

📡 **Señales:**
• Generadas: {estadisticas['senales_generadas']}
• Aciertos: {estadisticas['senales_acertadas']}
• Precisión: {estadisticas['precision_senales']:.1f}%
                """
                
                await query.edit_message_text(mensaje, parse_mode='Markdown')
            
            elif parts[0] == 'tendencia':
                mesa_nombre = parts[1]
                tendencia = analyzer.analizar_tendencias_mesa(mesa_nombre, 3)
                
                if 'error' in tendencia:
                    await query.edit_message_text("❌ No hay datos suficientes")
                    return
                
                mensaje = f"""
📈 **TENDENCIAS** 📈
**{mesa_nombre}**

📊 **Últimas 3 jugadas:**
{tendencia['tendencia_actual']['ultimos_5']}

🔥 **Tendencia actual:** {tendencia['tendencia_actual']['tendencia']}
                """
                
                await query.edit_message_text(mensaje, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"Error en callback: {e}")
            await query.edit_message_text("❌ Error al procesar la acción")
    
    async def run(self):
        """Ejecuta el bot"""
        logger.info("Iniciando bot interactivo de Telegram...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        # Mantener el bot ejecutándose
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Bot interactivo detenido por el usuario")
        finally:
            await self.application.stop()

# Instancia global del bot interactivo
interactive_bot = InteractiveTelegramBot(TELEGRAM_TOKEN)

async def iniciar_bot_interactivo():
    """Función para iniciar el bot interactivo"""
    await interactive_bot.run()

if __name__ == '__main__':
    asyncio.run(iniciar_bot_interactivo())