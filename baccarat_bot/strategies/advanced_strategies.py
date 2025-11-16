# baccarat_bot/strategies/advanced_strategies.py

from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class BettingStrategy(ABC):
    """Clase base abstracta para todas las estrategias de apuesta"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def analyze(self, history: List[str]) -> Optional[str]:
        """
        Analiza el historial y retorna una recomendación de apuesta
        
        Args:
            history: Lista de resultados previos ('B', 'P', 'E')
            
        Returns:
            'BANCA', 'JUGADOR', 'EMPATE' o None si no hay señal
        """
        pass
    
    @abstractmethod
    def get_confidence_level(self, history: List[str]) -> int:
        """
        Retorna el nivel de confianza de la señal (0-100)
        
        Args:
            history: Lista de resultados previos
            
        Returns:
            Nivel de confianza de 0 a 100
        """
        pass


class StreakStrategy(BettingStrategy):
    """Estrategia 1: Racha de N - Apuesta contra rachas largas"""
    
    def __init__(self, streak_length: int = 3):
        super().__init__("Racha")
        self.streak_length = streak_length
    
    def analyze(self, history: List[str]) -> Optional[str]:
        if len(history) < self.streak_length:
            return None
        
        last_results = history[-self.streak_length:]
        
        # Verificar si todos son iguales
        if len(set(last_results)) == 1:
            result = last_results[0]
            # Apostar contra la racha, o a favor si es empate
            if result == 'B':
                return 'JUGADOR'
            elif result == 'P':
                return 'BANCA'
            elif result == 'E':
                # Si hay racha de empates, apostar a EMPATE (continuación de patrón)
                return 'EMPATE'
        
        return None
    
    def get_confidence_level(self, history: List[str]) -> int:
        if len(history) < self.streak_length:
            return 0
        
        last_results = history[-self.streak_length:]
        if len(set(last_results)) == 1:
            # Más confianza con rachas más largas
            streak_count = 1
            for i in range(len(history) - 1, 0, -1):
                if history[i] == history[i-1]:
                    streak_count += 1
                else:
                    break
            
            # Confianza base 70%, +5% por cada elemento adicional en la racha
            return min(70 + (streak_count - self.streak_length) * 5, 95)
        
        return 0


class TieDetectionStrategy(BettingStrategy):
    """Estrategia: Detección de Empates - Identifica cuando es probable un empate"""
    
    def __init__(self, observation_window: int = 5):
        super().__init__("Detección de Empates")
        self.observation_window = observation_window
    
    def analyze(self, history: List[str]) -> Optional[str]:
        if len(history) < self.observation_window:
            return None
        
        recent = history[-self.observation_window:]
        tie_count = recent.count('E')
        
        # Si hay al menos 1 empate en las últimas N rondas, puede haber más
        if tie_count >= 1:
            # Si hay múltiples empates, es una buena señal
            if tie_count >= 2:
                return 'EMPATE'
            # Con un solo empate reciente, también puede recomendarse
            elif recent[-1] == 'E' or recent[-2] == 'E':
                return 'EMPATE'
        
        return None
    
    def get_confidence_level(self, history: List[str]) -> int:
        if len(history) < self.observation_window:
            return 0
        
        recent = history[-self.observation_window:]
        tie_count = recent.count('E')
        
        # Confianza basada en frecuencia de empates
        if tie_count >= 3:
            return 75
        elif tie_count == 2:
            return 65
        elif tie_count == 1 and (recent[-1] == 'E' or recent[-2] == 'E'):
            return 50
        
        return 0

class ZigZagStrategy(BettingStrategy):
    """Estrategia 2: Patrón Zig-Zag - Detecta alternancias"""
    
    def __init__(self, pattern_length: int = 4):
        super().__init__("Zig-Zag")
        self.pattern_length = pattern_length
    
    def analyze(self, history: List[str]) -> Optional[str]:
        if len(history) < self.pattern_length:
            return None
        
        last_results = history[-self.pattern_length:]
        
        # Ignorar si hay empates
        if 'E' in last_results:
            return None
        
        # Verificar patrón alternante
        is_zigzag = all(
            last_results[i] != last_results[i + 1]
            for i in range(self.pattern_length - 1)
        )
        
        if is_zigzag:
            # Continuar el patrón
            next_bet = last_results[-2]
            if next_bet == 'B':
                return 'BANCA'
            elif next_bet == 'P':
                return 'JUGADOR'
        
        return None
    
    def get_confidence_level(self, history: List[str]) -> int:
        if len(history) < self.pattern_length:
            return 0
        
        last_results = history[-self.pattern_length:]
        if 'E' not in last_results:
            is_zigzag = all(
                last_results[i] != last_results[i + 1]
                for i in range(self.pattern_length - 1)
            )
            if is_zigzag:
                return 75
        
        return 0


class MartingaleAdaptedStrategy(BettingStrategy):
    """Estrategia 3: Martingale Adaptado - Sistema de progresión"""
    
    def __init__(self, max_progression: int = 5):
        super().__init__("Martingale Adaptado")
        self.max_progression = max_progression
    
    def analyze(self, history: List[str]) -> Optional[str]:
        if len(history) < 2:
            return None
        
        # Contar pérdidas consecutivas (simuladas)
        # En un escenario real, necesitarías rastrear apuestas reales
        last_3 = history[-3:] if len(history) >= 3 else history
        
        # Si hay un patrón dominante, apostar a favor
        if last_3.count('B') >= 2:
            return 'BANCA'
        elif last_3.count('P') >= 2:
            return 'JUGADOR'
        
        return None
    
    def get_confidence_level(self, history: List[str]) -> int:
        if len(history) < 2:
            return 0
        
        last_3 = history[-3:] if len(history) >= 3 else history
        b_count = last_3.count('B')
        p_count = last_3.count('P')
        
        if b_count >= 2 or p_count >= 2:
            return 60
        
        return 0


class FibonacciStrategy(BettingStrategy):
    """Estrategia 4: Secuencia Fibonacci - Basada en patrones matemáticos"""
    
    def __init__(self):
        super().__init__("Fibonacci")
        self.fibonacci = [1, 1, 2, 3, 5, 8, 13, 21]
    
    def analyze(self, history: List[str]) -> Optional[str]:
        if len(history) < 5:
            return None
        
        # Buscar patrones de repetición basados en secuencia Fibonacci
        last_5 = history[-5:]
        
        # Contar apariciones
        b_count = last_5.count('B')
        p_count = last_5.count('P')
        
        # Si hay un número Fibonacci de apariciones, apostar a favor
        if b_count in self.fibonacci:
            return 'BANCA'
        elif p_count in self.fibonacci:
            return 'JUGADOR'
        
        return None
    
    def get_confidence_level(self, history: List[str]) -> int:
        if len(history) < 5:
            return 0
        
        last_5 = history[-5:]
        b_count = last_5.count('B')
        p_count = last_5.count('P')
        
        if b_count in self.fibonacci or p_count in self.fibonacci:
            return 65
        
        return 0


class TrendAnalysisStrategy(BettingStrategy):
    """Estrategia 5: Análisis de Tendencias - Corto y largo plazo"""
    
    def __init__(self, short_window: int = 5, long_window: int = 15):
        super().__init__("Análisis de Tendencias")
        self.short_window = short_window
        self.long_window = long_window
    
    def analyze(self, history: List[str]) -> Optional[str]:
        if len(history) < self.long_window:
            return None
        
        # Análisis a corto plazo
        short_history = history[-self.short_window:]
        short_b = short_history.count('B')
        short_p = short_history.count('P')
        
        # Análisis a largo plazo
        long_history = history[-self.long_window:]
        long_b = long_history.count('B')
        long_p = long_history.count('P')
        
        # Tendencia de corto plazo
        short_trend = 'B' if short_b > short_p else 'P' if short_p > short_b else None
        
        # Tendencia de largo plazo
        long_trend = 'B' if long_b > long_p else 'P' if long_p > long_b else None
        
        # Si ambas tendencias coinciden, señal fuerte
        if short_trend == long_trend and short_trend:
            if short_trend == 'B':
                return 'BANCA'
            else:
                return 'JUGADOR'
        
        return None
    
    def get_confidence_level(self, history: List[str]) -> int:
        if len(history) < self.long_window:
            return 0
        
        short_history = history[-self.short_window:]
        long_history = history[-self.long_window:]
        
        short_b = short_history.count('B')
        short_p = short_history.count('P')
        long_b = long_history.count('B')
        long_p = long_history.count('P')
        
        short_trend = 'B' if short_b > short_p else 'P' if short_p > short_b else None
        long_trend = 'B' if long_b > long_p else 'P' if long_p > long_b else None
        
        if short_trend == long_trend and short_trend:
            # Calcular diferencia porcentual
            short_diff = abs(short_b - short_p) / self.short_window * 100
            long_diff = abs(long_b - long_p) / self.long_window * 100
            
            # Confianza basada en la fuerza de la tendencia
            confidence = min(70 + int((short_diff + long_diff) / 2), 85)
            return confidence
        
        return 0


class StrategyManager:
    """Gestor de estrategias - Ejecuta y combina múltiples estrategias"""
    
    def __init__(self):
        self.strategies: Dict[str, BettingStrategy] = {
            'racha': StreakStrategy(3),
            'empates': TieDetectionStrategy(5),
            'zigzag': ZigZagStrategy(4),
            'martingale': MartingaleAdaptedStrategy(5),
            'fibonacci': FibonacciStrategy(),
            'tendencias': TrendAnalysisStrategy(5, 15)
        }
    
    def analyze_all(self, history: List[str]) -> Dict[str, Any]:
        """
        Ejecuta todas las estrategias y retorna un análisis combinado
        
        Args:
            history: Lista de resultados históricos
            
        Returns:
            Diccionario con resultados de todas las estrategias
        """
        results = {}
        
        for name, strategy in self.strategies.items():
            signal = strategy.analyze(history)
            confidence = strategy.get_confidence_level(history)
            
            results[name] = {
                'signal': signal,
                'confidence': confidence,
                'active': signal is not None
            }
        
        return results
    
    def analyze_with_all_strategies(self, history: List[str]) -> List[Dict[str, Any]]:
        """
        Alias de analyze_all que retorna una lista de recomendaciones
        Compatible con main_advanced.py
        
        Args:
            history: Lista de resultados históricos
            
        Returns:
            Lista de diccionarios con recomendaciones de cada estrategia
        """
        results = self.analyze_all(history)
        recommendations = []
        
        for name, result in results.items():
            if result['active'] and result['signal']:
                recommendations.append({
                    'strategy': name,
                    'signal': result['signal'],
                    'confidence': result['confidence']
                })
        
        return recommendations
    
    def get_consensus_signal(self, history: List[str]) -> Optional[Dict[str, Any]]:
        """
        Obtiene una señal de consenso basada en múltiples estrategias
        
        Args:
            history: Lista de resultados históricos
            
        Returns:
            Señal de consenso con detalles
        """
        results = self.analyze_all(history)
        
        # Contar votos ponderados por confianza
        votes = {'BANCA': 0, 'JUGADOR': 0, 'EMPATE': 0}
        total_confidence = 0
        active_strategies = []
        
        for name, result in results.items():
            if result['active'] and result['signal']:
                votes[result['signal']] += result['confidence']
                total_confidence += result['confidence']
                active_strategies.append(name)
        
        # Si no hay estrategias activas, no hay señal
        if not active_strategies:
            return None
        
        # Encontrar el voto ganador
        winner = max(votes, key=votes.get)
        winner_votes = votes[winner]
        
        # Solo retornar señal si hay suficiente confianza
        if winner_votes > 0 and total_confidence > 0:
            consensus_confidence = int(winner_votes / len(active_strategies))
            
            if consensus_confidence >= 50:  # Umbral mínimo
                return {
                    'signal': winner,
                    'confidence': consensus_confidence,
                    'strategies_agreeing': active_strategies,
                    'total_strategies_active': len(active_strategies),
                    'votes': votes
                }
        
        return None
    
    def add_strategy(self, name: str, strategy: BettingStrategy):
        """Agrega una nueva estrategia al gestor"""
        self.strategies[name] = strategy
        logger.info(f"Estrategia '{name}' agregada al gestor")
    
    def remove_strategy(self, name: str):
        """Elimina una estrategia del gestor"""
        if name in self.strategies:
            del self.strategies[name]
            logger.info(f"Estrategia '{name}' eliminada del gestor")


# Instancia global del gestor de estrategias
strategy_manager = StrategyManager()


# Funciones de compatibilidad con código anterior
def estrategia_racha(historial: List[str], longitud_racha: int = 3) -> Optional[str]:
    """Función de compatibilidad con código anterior"""
    strategy = StreakStrategy(longitud_racha)
    result = strategy.analyze(historial)
    
    # Convertir de formato nuevo a antiguo
    if result == 'BANCA':
        return 'Banca'
    elif result == 'JUGADOR':
        return 'Jugador'
    elif result == 'EMPATE':
        return 'Empate'
    return None


def estrategia_zigzag(historial: List[str], longitud_patron: int = 4) -> Optional[str]:
    """Función de compatibilidad con código anterior"""
    strategy = ZigZagStrategy(longitud_patron)
    result = strategy.analyze(historial)
    
    # Convertir de formato nuevo a antiguo
    if result == 'BANCA':
        return 'Banca'
    elif result == 'JUGADOR':
        return 'Jugador'
    return None
