# baccarat_bot/game_timing_detector.py

"""
Módulo de Detección de Timing y Eventos del Juego
Detecta:
- Tiempos de colocación de cartas del crupier
- Ventana de tiempo para apostar
- Cambio de crupier
- Revolución de cartas (shuffle/reset)
"""

import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from statistics import mean, stdev

logger = logging.getLogger(__name__)

@dataclass
class GameTiming:
    """Estructura para almacenar tiempos del juego"""
    round_start_time: float  # Tiempo de inicio de ronda
    betting_open_time: float  # Tiempo cuando se abre apuestas
    betting_close_time: float  # Tiempo cuando se cierra apuestas
    cards_dealt_time: float  # Tiempo cuando se reparten cartas
    result_time: float  # Tiempo cuando se anuncia resultado
    
    @property
    def betting_duration(self) -> float:
        """Duración total de la ventana de apuestas"""
        return self.betting_close_time - self.betting_open_time
    
    @property
    def time_to_bet(self) -> float:
        """Tiempo restante para apostar desde ahora"""
        return max(0, self.betting_close_time - time.time())


class GameTimingDetector:
    """
    Detector de timing del juego para sincronizar señales
    """
    
    def __init__(self):
        self.timing_history: List[GameTiming] = []
        self.max_history = 50  # Mantener últimas 50 rondas
        
        # Tiempos promedio calculados
        self.avg_betting_window = 25.0  # segundos (ajustable)
        self.avg_card_dealing_time = 15.0  # segundos
        self.avg_round_duration = 50.0  # segundos
        
        # Margen de seguridad para enviar señal
        self.signal_advance_time = 8.0  # Enviar señal 8s antes de cierre
        
        # Detección de eventos
        self.last_shuffle_time: Optional[float] = None
        self.last_dealer_change: Optional[float] = None
        self.current_dealer_id: Optional[str] = None
        
        # Contadores
        self.rounds_since_shuffle = 0
        self.cards_remaining_estimate = 312  # 8 decks = 416 cartas, ajustar
        
        logger.info("🕐 GameTimingDetector inicializado")
    
    def calculate_optimal_signal_time(self) -> Dict[str, float]:
        """
        Calcula el momento óptimo para enviar la señal (apertura de apuestas).
        Ahora recomienda enviar la señal apenas se abre la ventana de apuestas
        (segundo 0-3).
        Returns:
            Dict con timing recomendado
        """
        if len(self.timing_history) >= 3:
            recent_timings = self.timing_history[-10:]
            avg_window = mean([t.betting_duration for t in recent_timings])
        else:
            avg_window = self.avg_betting_window
        # El momento recomendado es el inicio de la ventana de apuestas
        recommended_signal_timing = 0.0
        return {
            'betting_window_avg': avg_window,
            'signal_advance_time': 0.0,
            'recommended_signal_timing': recommended_signal_timing,
            'confidence': min(len(self.timing_history) / 10.0, 1.0)
        }
    
    def should_send_signal_now(self, time_since_round_start: float) -> bool:
        """
        Determina si es el momento óptimo para enviar la señal.
        Ahora la ventana óptima es entre el segundo 0 y 3 tras abrirse la
        ventana de apuestas.
        Args:
            time_since_round_start: Segundos desde que comenzó la ronda
        Returns:
            True si es momento de enviar señal
        """
        # El momento recomendado es el inicio de la ventana de apuestas
        min_time = 0.0
        max_time = 3.0
        is_optimal = min_time <= time_since_round_start <= max_time
        if is_optimal:
            logger.info(
                f"⏰ MOMENTO ÓPTIMO para señal (t={time_since_round_start:.1f}s, "
                f"ventana óptima: {min_time:.1f}-"
                f"{max_time:.1f}s)"
            )
        return is_optimal
    
    def detect_shuffle_event(self, visual_indicators: Dict[str, Any]) -> bool:
        """
        Detecta si se están revolviendo las cartas
        
        Args:
            visual_indicators: Diccionario con indicadores visuales del juego
            
        Returns:
            True si detecta shuffle
        """
        # Indicadores de shuffle:
        # 1. Texto "Shuffle" o "Revolución" visible
        # 2. Tiempo inusualmente largo sin ronda
        # 3. Contador de cartas se resetea
        # 4. Cambio en el zapato/shoe
        
        shuffle_detected = False
        
        if visual_indicators.get('shuffle_text_visible'):
            shuffle_detected = True
            logger.warning("🔀 SHUFFLE DETECTADO - Texto visible")
        
        if visual_indicators.get('shoe_changed'):
            shuffle_detected = True
            logger.warning("🔀 SHUFFLE DETECTADO - Cambio de zapato")
        
        # Tiempo excesivo sin ronda (más de 2 minutos)
        if visual_indicators.get('time_since_last_round', 0) > 120:
            shuffle_detected = True
            logger.warning("🔀 POSIBLE SHUFFLE - Tiempo excesivo sin ronda")
        
        if shuffle_detected:
            self.last_shuffle_time = time.time()
            self.rounds_since_shuffle = 0
            self.cards_remaining_estimate = 312  # Reset
            logger.warning(
                "⚠️ SHUFFLE DETECTADO - Reiniciando conteo de cartas"
            )
            return True
        
        return False
    
    def detect_dealer_change(self, dealer_info: Dict[str, Any]) -> bool:
        """
        Detecta cambio de crupier
        
        Args:
            dealer_info: Información del crupier actual
            
        Returns:
            True si detecta cambio
        """
        current_dealer = dealer_info.get('dealer_id') or \
            dealer_info.get('dealer_name')
        
        if not current_dealer:
            return False
        
        if self.current_dealer_id and current_dealer != self.current_dealer_id:
            logger.warning(
                f"👤 CAMBIO DE CRUPIER DETECTADO: {self.current_dealer_id} → "
                f"{current_dealer}"
            )
            self.last_dealer_change = time.time()
            self.current_dealer_id = current_dealer
            return True
        
        if not self.current_dealer_id:
            self.current_dealer_id = current_dealer
            logger.info(f"👤 Crupier identificado: {current_dealer}")
        
        return False
    
    def update_card_count(self, cards_dealt: int):
        """
        Actualiza estimación de cartas restantes
        
        Args:
            cards_dealt: Número de cartas repartidas en esta ronda
        """
        self.cards_remaining_estimate -= cards_dealt
        
        penetration_pct = (1 - self.cards_remaining_estimate / 312) * 100
        
        if penetration_pct > 75:
            logger.warning(
                f"⚠️ ALTA PENETRACIÓN DEL ZAPATO: {penetration_pct:.1f}% - "
                "Shuffle próximo"
            )
        
        logger.debug(
            f"🃏 Cartas restantes estimadas: {self.cards_remaining_estimate} "
            f"(penetración: {penetration_pct:.1f}%)"
        )
    
    def record_round_timing(self, timing: GameTiming):
        """
        Registra los tiempos de una ronda completa
        
        Args:
            timing: Objeto GameTiming con los tiempos de la ronda
        """
        self.timing_history.append(timing)
        
        # Mantener solo las últimas N rondas
        if len(self.timing_history) > self.max_history:
            self.timing_history.pop(0)
        
        # Actualizar promedios
        if len(self.timing_history) >= 5:
            recent = self.timing_history[-5:]
            self.avg_betting_window = mean([
                t.betting_duration for t in recent
            ])
            self.avg_round_duration = mean([
                t.result_time - t.round_start_time for t in recent
            ])
        
        self.rounds_since_shuffle += 1
        
        logger.info(
            f"⏱️ Ronda registrada | Ventana apuestas: "
            f"{timing.betting_duration:.1f}s | "
            f"Duración total: "
            f"{timing.result_time - timing.round_start_time:.1f}s"
        )
    
    def get_timing_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de timing del juego
        
        Returns:
            Dict con estadísticas
        """
        if not self.timing_history:
            return {
                'status': 'sin_datos',
                'rounds_analyzed': 0
            }
        
        recent = self.timing_history[-20:]
        
        stats = {
            'status': 'ok',
            'rounds_analyzed': len(self.timing_history),
            'avg_betting_window': mean([t.betting_duration for t in recent]),
            'min_betting_window': min([t.betting_duration for t in recent]),
            'max_betting_window': max([t.betting_duration for t in recent]),
            'std_betting_window': (
                stdev([t.betting_duration for t in recent])
                if len(recent) > 1 else 0
            ),
            'avg_round_duration': self.avg_round_duration,
            'rounds_since_shuffle': self.rounds_since_shuffle,
            'cards_remaining_estimate': self.cards_remaining_estimate,
            'last_shuffle': self.last_shuffle_time,
            'last_dealer_change': self.last_dealer_change,
            'current_dealer': self.current_dealer_id,
            'signal_advance_time': self.signal_advance_time
        }
        
        return stats
    
    def simulate_round_timing(self) -> GameTiming:
        """
        Simula timing de una ronda (para testing o cuando no hay datos reales)
        
        Returns:
            GameTiming simulado
        """
        now = time.time()
        
        # Simular tiempos típicos de Baccarat
        betting_window = self.avg_betting_window
        card_dealing = self.avg_card_dealing_time
        
        timing = GameTiming(
            round_start_time=now,
            betting_open_time=now + 2,  # 2s de delay inicial
            betting_close_time=now + 2 + betting_window,
            cards_dealt_time=now + 2 + betting_window + 5,
            result_time=now + 2 + betting_window + card_dealing
        )
        
        return timing
    
    def get_next_signal_timing(self) -> Dict[str, Any]:
        """
        Calcula cuándo enviar la próxima señal
        
        Returns:
            Dict con información de timing
        """
        optimal = self.calculate_optimal_signal_time()
        
        # Estimar tiempo hasta próxima señal
        time_to_next_round = self.avg_round_duration
        time_to_signal = (
            time_to_next_round - optimal['recommended_signal_timing']
        )
        
        return {
            'seconds_to_next_signal': time_to_signal,
            'recommended_signal_point': optimal['recommended_signal_timing'],
            'confidence': optimal['confidence'],
            'betting_window_estimate': optimal['betting_window_avg'],
            'safety_margin': optimal['signal_advance_time']
        }


class RealTimeGameMonitor:
    """
    Monitor en tiempo real del estado del juego
    Integra timing detector con detección de eventos
    """
    
    def __init__(self):
        self.timing_detector = GameTimingDetector()
        self.current_round_start: Optional[float] = None
        self.is_betting_open = False
        self.last_event_time = time.time()
        
        logger.info("🎰 RealTimeGameMonitor inicializado")
    
    def start_new_round(self):
        """Inicia tracking de nueva ronda"""
        self.current_round_start = time.time()
        self.is_betting_open = True
        logger.info("▶️ Nueva ronda iniciada")
    
    def close_betting(self):
        """Marca cierre de apuestas"""
        self.is_betting_open = False
        logger.info("🔒 Apuestas cerradas")
    
    def check_signal_timing(self) -> Dict[str, Any]:
        """
        Verifica si es momento de enviar señal
        
        Returns:
            Dict con decisión y metadata
        """
        if not self.current_round_start:
            return {
                'should_signal': False,
                'reason': 'no_round_active'
            }
        
        time_elapsed = time.time() - self.current_round_start
        
        should_signal = self.timing_detector.should_send_signal_now(
            time_elapsed
        )
        
        optimal_timing = self.timing_detector.calculate_optimal_signal_time()
        
        return {
            'should_signal': should_signal,
            'time_elapsed': time_elapsed,
            'optimal_timing': optimal_timing,
            'is_betting_open': self.is_betting_open,
            'reason': 'optimal_timing' if should_signal else 'waiting'
        }
    
    def get_status_report(self) -> str:
        """
        Genera reporte de estado para logging
        
        Returns:
            String con reporte
        """
        stats = self.timing_detector.get_timing_statistics()
        next_signal = self.timing_detector.get_next_signal_timing()
        
        report = f"""
╔════════════════════════════════════════════════╗
║       ESTADO DEL TIMING DEL JUEGO              ║
╠════════════════════════════════════════════════╣
║ Rondas analizadas: {stats.get('rounds_analyzed', 0):>26} ║
║ Ventana de apuestas promedio: {stats.get('avg_betting_window', 0):>14.1f}s ║
║ Tiempo de antelación señal: {stats.get('signal_advance_time', 0):>16.1f}s ║
║ Confianza del timing: {next_signal.get('confidence', 0)*100:>21.0f}% ║
║ ───────────────────────────────────────────── ║
║ Rondas desde shuffle: {stats.get('rounds_since_shuffle', 0):>22} ║
║ Cartas restantes (est.): {stats.get('cards_remaining_estimate', 0):>19} ║
║ Crupier actual: {str(stats.get('current_dealer', 'N/A'))[:30]:>29} ║
╚════════════════════════════════════════════════╝
        """
        
        return report.strip()
