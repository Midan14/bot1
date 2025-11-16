# baccarat_bot/utils/bot_state.py

"""
Gestión centralizada de estados del bot
Centraliza todas las variables globales dispersas
"""

import time
from typing import Dict, Optional, Any
from dataclasses import dataclass
import logging

from config_enhanced import TIMING_CONFIG

logger = logging.getLogger(__name__)

@dataclass
class RoundInfo:
    """Información de una ronda en curso"""
    mesa_nombre: str
    round_start_time: float
    betting_opened: bool = False
    betting_closed: bool = False
    signal_sent: bool = False
    resultado_final: Optional[str] = None
    
    @property
    def duration(self) -> float:
        """Duración de la ronda en segundos"""
        return time.time() - self.round_start_time
    
    @property
    def time_to_bet_close(self) -> float:
        """Tiempo estimado para cierre de apuestas"""
        # Estimación basada en timing promedio
        estimated_total = 50.0  # 50 segundos promedio
        return max(0, estimated_total - self.duration)


class BotState:
    """Gestor centralizado de estados del bot"""
    
    def __init__(self):
        # Estados de señales
        self.last_signal_time: Dict[str, float] = {}
        self.signal_frequency_tracker: Dict[str, list] = {}
        
        # Predicciones pendientes
        self.predicciones_pendientes: Dict[str, Dict] = {}
        
        # Estados de rondas
        self.active_rounds: Dict[str, RoundInfo] = {}
        self.round_start_times: Dict[str, Optional[float]] = {}
        
        # Cargar configuración de timing
        self.timing_config = TIMING_CONFIG
        self.min_signal_interval = self.timing_config['signal_cooldown']['max_frequency']
        self.max_signals_per_hour = self.timing_config['frecuencia_limites']['max_por_hora']
        
        # Estadísticas de sesión
        self.session_stats = {
            'start_time': time.time(),
            'signals_sent': 0,
            'signals_successful': 0,
            'rounds_processed': 0,
            'errors_count': 0,
            'last_error': None
        }
        
        logger.info("🤖 BotState inicializado correctamente")
    
    def can_send_signal(self, mesa_nombre: str) -> tuple[bool, str]:
        """
        Verifica si se puede enviar una señal para una mesa específica
        
        Returns:
            (can_send, reason)
        """
        current_time = time.time()
        
        # Verificar cooldown básico
        if mesa_nombre in self.last_signal_time:
            time_since_last = current_time - self.last_signal_time[mesa_nombre]
            if time_since_last < self.min_signal_interval:
                return False, f"Cooldown activo ({time_since_last:.1f}s < {self.min_signal_interval}s)"
        
        # Verificar frecuencia por hora
        if mesa_nombre in self.signal_frequency_tracker:
            recent_signals = [
                timestamp for timestamp in self.signal_frequency_tracker[mesa_nombre]
                if current_time - timestamp < 3600  # Última hora
            ]
            
            if len(recent_signals) >= self.max_signals_per_hour:
                return False, f"Límite de señales por hora alcanzado ({self.max_signals_per_hour})"
        
        # Verificar si hay ronda activa
        if mesa_nombre in self.active_rounds:
            round_info = self.active_rounds[mesa_nombre]
            if not round_info.betting_closed:
                # Está en ventana de apuestas, permitir señal
                return True, "Ronda activa en ventana de apuestas"
        
        return True, "OK - Señal permitida"
    
    def register_signal_sent(self, mesa_nombre: str) -> None:
        """Registra que se envió una señal para una mesa"""
        current_time = time.time()
        self.last_signal_time[mesa_nombre] = current_time
        
        # Actualizar tracker de frecuencia
        if mesa_nombre not in self.signal_frequency_tracker:
            self.signal_frequency_tracker[mesa_nombre] = []
        
        self.signal_frequency_tracker[mesa_nombre].append(current_time)
        
        # Limpiar señales antiguas (más de 1 hora)
        self.signal_frequency_tracker[mesa_nombre] = [
            ts for ts in self.signal_frequency_tracker[mesa_nombre]
            if current_time - ts < 3600
        ]
        
        # Actualizar estadísticas
        self.session_stats['signals_sent'] += 1
        
        logger.debug(f"📤 Señal registrada para {mesa_nombre}")
    
    def start_round(self, mesa_nombre: str) -> RoundInfo:
        """Inicia el tracking de una nueva ronda"""
        round_info = RoundInfo(
            mesa_nombre=mesa_nombre,
            round_start_time=time.time()
        )
        
        self.active_rounds[mesa_nombre] = round_info
        self.round_start_times[mesa_nombre] = round_info.round_start_time
        
        logger.info(f"🎲 Nueva ronda iniciada en {mesa_nombre}")
        return round_info
    
    def close_round(self, mesa_nombre: str, resultado: str) -> bool:
        """Cierra una ronda y actualiza estadísticas"""
        if mesa_nombre not in self.active_rounds:
            logger.warning(f"⚠️ Intento de cerrar ronda inexistente: {mesa_nombre}")
            return False
        
        round_info = self.active_rounds[mesa_nombre]
        round_info.betting_closed = True
        round_info.resultado_final = resultado
        
        # Actualizar estadísticas
        self.session_stats['rounds_processed'] += 1
        
        logger.info(f"🏁 Ronda cerrada en {mesa_nombre}: {resultado}")
        
        # Limpiar ronda antigua (mantener solo por 5 minutos para referencias)
        def cleanup_round():
            if mesa_nombre in self.active_rounds:
                del self.active_rounds[mesa_nombre]
        
        # Programar limpieza en 5 minutos
        import threading
        timer = threading.Timer(300, cleanup_round)  # 5 minutos
        timer.start()
        
        return True
    
    def get_round_info(self, mesa_nombre: str) -> Optional[RoundInfo]:
        """Obtiene información de la ronda actual de una mesa"""
        return self.active_rounds.get(mesa_nombre)
    
    def is_betting_open(self, mesa_nombre: str) -> bool:
        """Verifica si las apuestas están abiertas para una mesa"""
        round_info = self.active_rounds.get(mesa_nombre)
        return round_info is not None and not round_info.betting_closed
    
    def add_pending_prediction(self, mesa_nombre: str, apuesta: str) -> None:
        """Agrega una predicción pendiente para seguimiento"""
        self.predicciones_pendientes[mesa_nombre] = {
            'apuesta': apuesta,
            'timestamp': time.time(),
            'round_start': self.round_start_times.get(mesa_nombre)
        }
        
        logger.debug(f"📋 Predicción pendiente agregada para {mesa_nombre}: {apuesta}")
    
    def get_pending_prediction(self, mesa_nombre: str) -> Optional[Dict]:
        """Obtiene y remueve una predicción pendiente"""
        return self.predicciones_pendientes.pop(mesa_nombre, None)
    
    def has_pending_prediction(self, mesa_nombre: str) -> bool:
        """Verifica si hay predicción pendiente para una mesa"""
        return mesa_nombre in self.predicciones_pendientes
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la sesión actual"""
        current_time = time.time()
        session_duration = current_time - self.session_stats['start_time']
        
        stats = self.session_stats.copy()
        stats.update({
            'session_duration_hours': session_duration / 3600,
            'signals_per_hour': (stats['signals_sent'] / session_duration * 3600) if session_duration > 0 else 0,
            'active_rounds': len(self.active_rounds),
            'pending_predictions': len(self.predicciones_pendientes),
            'mesas_with_recent_signals': len([
                mesa for mesa, last_time in self.last_signal_time.items()
                if current_time - last_time < 3600  # Última hora
            ])
        })
        
        return stats
    
    def record_error(self, error: Exception) -> None:
        """Registra un error en las estadísticas"""
        self.session_stats['errors_count'] += 1
        self.session_stats['last_error'] = {
            'type': type(error).__name__,
            'message': str(error),
            'timestamp': time.time()
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Obtiene el estado de salud del bot"""
        stats = self.get_session_stats()
        
        # Calcular métricas de salud
        error_rate = stats['errors_count'] / max(1, stats['rounds_processed'])
        signal_success_rate = (
            stats['signals_successful'] / max(1, stats['signals_sent'])
            if stats['signals_sent'] > 0 else 0
        )
        
        # Determinar estado general
        if error_rate > 0.1:  # Más del 10% de errores
            health_status = "critical"
        elif error_rate > 0.05 or signal_success_rate < 0.5:  # 5% errores o <50% éxito
            health_status = "degraded"
        else:
            health_status = "healthy"
        
        return {
            'status': health_status,
            'uptime_hours': stats['session_duration_hours'],
            'error_rate': error_rate,
            'signal_success_rate': signal_success_rate,
            'signals_per_hour': stats['signals_per_hour'],
            'active_components': {
                'active_rounds': stats['active_rounds'],
                'pending_predictions': stats['pending_predictions'],
                'recent_signals': stats['mesas_with_recent_signals']
            },
            'last_error': stats.get('last_error')
        }
    
    def reset_session_stats(self) -> None:
        """Reinicia las estadísticas de la sesión"""
        self.session_stats = {
            'start_time': time.time(),
            'signals_sent': 0,
            'signals_successful': 0,
            'rounds_processed': 0,
            'errors_count': 0,
            'last_error': None
        }
        
        # Limpiar trackers de frecuencia
        self.signal_frequency_tracker.clear()
        
        logger.info("🔄 Estadísticas de sesión reiniciadas")
    
    def cleanup_old_data(self) -> None:
        """Limpia datos antiguos para mantener rendimiento"""
        current_time = time.time()
        
        # Limpiar señales antiguas (más de 2 horas)
        for mesa in list(self.signal_frequency_tracker.keys()):
            self.signal_frequency_tracker[mesa] = [
                ts for ts in self.signal_frequency_tracker[mesa]
                if current_time - ts < 7200  # 2 horas
            ]
            
            # Remover mesa si no tiene señales recientes
            if not self.signal_frequency_tracker[mesa]:
                del self.signal_frequency_tracker[mesa]
        
        # Limpiar tiempos de última señal antiguos
        for mesa in list(self.last_signal_time.keys()):
            if current_time - self.last_signal_time[mesa] > 7200:  # 2 horas
                del self.last_signal_time[mesa]
        
        logger.debug("🧹 Limpieza de datos antiguos completada")


# Instancia global del estado del bot
bot_state = BotState()
