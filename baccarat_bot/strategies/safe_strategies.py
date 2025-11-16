# baccarat_bot/strategies/safe_strategies.py

"""
Estrategias de apuesta conservadoras y seguras para Baccarat.
Enfocadas en minimizar riesgo y maximizar precisión.
"""

from typing import List, Optional, Tuple
from baccarat_bot.strategies.advanced_strategies import BettingStrategy
import logging

logger = logging.getLogger(__name__)


class ConservativeStreakStrategy(BettingStrategy):
    """
    Estrategia conservadora de racha - Solo apuesta en rachas muy largas.
    
    Características:
    - Requiere rachas de 5+ para generar señal
    - Alta confianza (85-95%)
    - Baja frecuencia de señales
    """
    
    def __init__(self, min_streak_length: int = 5):
        super().__init__("Racha Conservadora")
        self.min_streak_length = min_streak_length
    
    def analyze(self, history: List[str]) -> Optional[str]:
        if len(history) < self.min_streak_length:
            return None
        
        last_results = history[-self.min_streak_length:]
        
        # Verificar racha
        if len(set(last_results)) == 1:
            result = last_results[0]
            
            # Contar la longitud real de la racha
            streak_count = 1
            for i in range(len(history) - 1, 0, -1):
                if history[i] == history[i-1]:
                    streak_count += 1
                else:
                    break
            
            # Solo generar señal si la racha es muy larga
            if streak_count >= self.min_streak_length:
                if result == 'B':
                    return 'JUGADOR'
                elif result == 'P':
                    return 'BANCA'
        
        return None
    
    def get_confidence_level(self, history: List[str]) -> int:
        if len(history) < self.min_streak_length:
            return 0
        
        # Contar longitud de racha
        streak_count = 1
        for i in range(len(history) - 1, 0, -1):
            if history[i] == history[i-1]:
                streak_count += 1
            else:
                break
        
        if streak_count >= self.min_streak_length:
            # Confianza base 85%, +2% por cada elemento adicional
            return min(85 + (streak_count - self.min_streak_length) * 2, 95)
        
        return 0


class ConfirmedPatternStrategy(BettingStrategy):
    """
    Estrategia de patrón confirmado - Requiere múltiples confirmaciones.
    
    Características:
    - Detecta patrones repetidos
    - Requiere al menos 2 repeticiones del patrón
    - Alta confianza (80-90%)
    """
    
    def __init__(self, pattern_length: int = 3):
        super().__init__("Patrón Confirmado")
        self.pattern_length = pattern_length
    
    def analyze(self, history: List[str]) -> Optional[str]:
        if len(history) < self.pattern_length * 3:
            return None
        
        # Ignorar empates para análisis de patrones
        clean_history = [r for r in history if r != 'E']
        if len(clean_history) < self.pattern_length * 3:
            return None
        
        # Extraer último patrón
        last_pattern = clean_history[-self.pattern_length:]
        
        # Buscar repeticiones del patrón en el historial
        pattern_count = 0
        for i in range(len(clean_history) - self.pattern_length):
            segment = clean_history[i:i + self.pattern_length]
            if segment == last_pattern:
                pattern_count += 1
        
        # Requiere al menos 2 repeticiones
        if pattern_count >= 2:
            # Predecir siguiente resultado basado en el patrón
            # Buscar qué vino después del patrón anteriormente
            next_results = []
            for i in range(len(clean_history) - self.pattern_length - 1):
                segment = clean_history[i:i + self.pattern_length]
                if segment == last_pattern:
                    next_results.append(clean_history[i + self.pattern_length])
            
            if next_results:
                # Tomar el resultado más común
                most_common = max(set(next_results), key=next_results.count)
                if most_common == 'B':
                    return 'BANCA'
                elif most_common == 'P':
                    return 'JUGADOR'
        
        return None
    
    def get_confidence_level(self, history: List[str]) -> int:
        clean_history = [r for r in history if r != 'E']
        if len(clean_history) < self.pattern_length * 3:
            return 0
        
        last_pattern = clean_history[-self.pattern_length:]
        pattern_count = sum(
            1 for i in range(len(clean_history) - self.pattern_length)
            if clean_history[i:i + self.pattern_length] == last_pattern
        )
        
        if pattern_count >= 2:
            # Confianza base 80%, +5% por cada repetición adicional
            return min(80 + (pattern_count - 2) * 5, 90)
        
        return 0


class StatisticalEdgeStrategy(BettingStrategy):
    """
    Estrategia de ventaja estadística - Basada en desviación significativa.
    
    Características:
    - Analiza desviación de la distribución esperada
    - Requiere muestra grande (30+ resultados)
    - Apuesta hacia el equilibrio estadístico
    - Confianza media-alta (70-85%)
    """
    
    def __init__(self, min_sample_size: int = 30, deviation_threshold: float = 0.15):
        super().__init__("Ventaja Estadística")
        self.min_sample_size = min_sample_size
        self.deviation_threshold = deviation_threshold
    
    def analyze(self, history: List[str]) -> Optional[str]:
        if len(history) < self.min_sample_size:
            return None
        
        # Analizar últimos N resultados
        recent_history = history[-self.min_sample_size:]
        
        # Contar resultados (ignorar empates para el análisis)
        clean_history = [r for r in recent_history if r != 'E']
        if len(clean_history) < self.min_sample_size * 0.8:  # Al menos 80% sin empates
            return None
        
        b_count = clean_history.count('B')
        p_count = clean_history.count('P')
        total = len(clean_history)
        
        # Calcular proporciones
        b_ratio = b_count / total
        p_ratio = p_count / total
        
        # Distribución esperada: 50.68% Banca, 49.32% Jugador (probabilidades reales)
        expected_b_ratio = 0.5068
        expected_p_ratio = 0.4932
        
        # Calcular desviación
        b_deviation = abs(b_ratio - expected_b_ratio)
        p_deviation = abs(p_ratio - expected_p_ratio)
        
        # Si hay desviación significativa, apostar hacia el equilibrio
        if b_deviation > self.deviation_threshold:
            if b_ratio > expected_b_ratio:
                # Muchas Bancas, apostar a Jugador
                return 'JUGADOR'
            else:
                # Pocas Bancas, apostar a Banca
                return 'BANCA'
        elif p_deviation > self.deviation_threshold:
            if p_ratio > expected_p_ratio:
                # Muchos Jugadores, apostar a Banca
                return 'BANCA'
            else:
                # Pocos Jugadores, apostar a Jugador
                return 'JUGADOR'
        
        return None
    
    def get_confidence_level(self, history: List[str]) -> int:
        if len(history) < self.min_sample_size:
            return 0
        
        recent_history = history[-self.min_sample_size:]
        clean_history = [r for r in recent_history if r != 'E']
        
        if len(clean_history) < self.min_sample_size * 0.8:
            return 0
        
        b_count = clean_history.count('B')
        p_count = clean_history.count('P')
        total = len(clean_history)
        
        b_ratio = b_count / total
        p_ratio = p_count / total
        
        # Calcular desviación máxima
        max_deviation = max(
            abs(b_ratio - 0.5068),
            abs(p_ratio - 0.4932)
        )
        
        if max_deviation > self.deviation_threshold:
            # Confianza proporcional a la desviación
            confidence = 70 + min(int(max_deviation * 100), 15)
            return confidence
        
        return 0


class ConsensusStrategy(BettingStrategy):
    """
    Estrategia de consenso - Combina múltiples estrategias.
    
    Características:
    - Requiere acuerdo de al menos 3 estrategias
    - Muy alta confianza (90-98%)
    - Frecuencia muy baja de señales
    - Máxima seguridad
    """
    
    def __init__(self, strategies: List[BettingStrategy] = None):
        super().__init__("Consenso")
        
        if strategies is None:
            # Usar estrategias por defecto
            from baccarat_bot.strategies.advanced_strategies import (
                StreakStrategy,
                ZigZagStrategy,
                TrendAnalysisStrategy
            )
            self.strategies = [
                ConservativeStreakStrategy(min_streak_length=5),
                ConfirmedPatternStrategy(pattern_length=3),
                StatisticalEdgeStrategy(min_sample_size=30),
                StreakStrategy(streak_length=4),
                TrendAnalysisStrategy(short_window=5, long_window=20)
            ]
        else:
            self.strategies = strategies
        
        self.min_consensus = 3  # Mínimo de estrategias que deben coincidir
    
    def analyze(self, history: List[str]) -> Optional[str]:
        if len(history) < 20:  # Requiere historial mínimo
            return None
        
        # Obtener recomendaciones de todas las estrategias
        recommendations = {}
        for strategy in self.strategies:
            try:
                result = strategy.analyze(history)
                if result:
                    confidence = strategy.get_confidence_level(history)
                    if confidence >= 70:  # Solo considerar alta confianza
                        if result not in recommendations:
                            recommendations[result] = []
                        recommendations[result].append({
                            'strategy': strategy.name,
                            'confidence': confidence
                        })
            except Exception as e:
                logger.warning(f"Error en estrategia {strategy.name}: {e}")
                continue
        
        # Verificar consenso
        for result, votes in recommendations.items():
            if len(votes) >= self.min_consensus:
                # Calcular confianza promedio
                avg_confidence = sum(v['confidence'] for v in votes) / len(votes)
                
                if avg_confidence >= 75:
                    logger.info(
                        f"Consenso alcanzado: {result} con {len(votes)} votos, "
                        f"confianza promedio: {avg_confidence:.1f}%"
                    )
                    return result
        
        return None
    
    def get_confidence_level(self, history: List[str]) -> int:
        if len(history) < 20:
            return 0
        
        # Obtener recomendaciones
        recommendations = {}
        for strategy in self.strategies:
            try:
                result = strategy.analyze(history)
                if result:
                    confidence = strategy.get_confidence_level(history)
                    if confidence >= 70:
                        if result not in recommendations:
                            recommendations[result] = []
                        recommendations[result].append(confidence)
            except:
                continue
        
        # Buscar el resultado con más votos
        max_votes = 0
        max_confidence = 0
        
        for result, confidences in recommendations.items():
            if len(confidences) >= self.min_consensus:
                avg_confidence = sum(confidences) / len(confidences)
                vote_bonus = (len(confidences) - self.min_consensus) * 2
                
                total_confidence = min(avg_confidence + vote_bonus, 98)
                
                if len(confidences) > max_votes:
                    max_votes = len(confidences)
                    max_confidence = int(total_confidence)
        
        return max_confidence


class DominanceStrategy(BettingStrategy):
    """
    Estrategia de dominancia clara - Solo apuesta cuando hay dominancia obvia.
    
    Características:
    - Requiere dominancia de 70%+ en últimos 20 resultados
    - Apuesta a favor de la tendencia dominante
    - Alta confianza (80-90%)
    """
    
    def __init__(self, window_size: int = 20, dominance_threshold: float = 0.70):
        super().__init__("Dominancia Clara")
        self.window_size = window_size
        self.dominance_threshold = dominance_threshold
    
    def analyze(self, history: List[str]) -> Optional[str]:
        if len(history) < self.window_size:
            return None
        
        recent = history[-self.window_size:]
        clean_recent = [r for r in recent if r != 'E']
        
        if len(clean_recent) < self.window_size * 0.8:
            return None
        
        b_count = clean_recent.count('B')
        p_count = clean_recent.count('P')
        total = len(clean_recent)
        
        b_ratio = b_count / total
        p_ratio = p_count / total
        
        # Verificar dominancia
        if b_ratio >= self.dominance_threshold:
            return 'BANCA'  # Apostar a favor de la dominancia
        elif p_ratio >= self.dominance_threshold:
            return 'JUGADOR'  # Apostar a favor de la dominancia
        
        return None
    
    def get_confidence_level(self, history: List[str]) -> int:
        if len(history) < self.window_size:
            return 0
        
        recent = history[-self.window_size:]
        clean_recent = [r for r in recent if r != 'E']
        
        if len(clean_recent) < self.window_size * 0.8:
            return 0
        
        b_count = clean_recent.count('B')
        p_count = clean_recent.count('P')
        total = len(clean_recent)
        
        max_ratio = max(b_count / total, p_count / total)
        
        if max_ratio >= self.dominance_threshold:
            # Confianza proporcional a la dominancia
            confidence = 80 + int((max_ratio - self.dominance_threshold) * 100)
            return min(confidence, 90)
        
        return 0


# Función helper para obtener la mejor estrategia segura
def get_safest_signal(history: List[str]) -> Optional[Tuple[str, str, int]]:
    """
    Obtiene la señal más segura analizando con todas las estrategias conservadoras.
    
    Args:
        history: Historial de resultados
        
    Returns:
        Tupla (resultado, estrategia, confianza) o None si no hay señal segura
    """
    strategies = [
        ConservativeStreakStrategy(min_streak_length=5),
        ConfirmedPatternStrategy(pattern_length=3),
        StatisticalEdgeStrategy(min_sample_size=30),
        ConsensusStrategy(),
        DominanceStrategy(window_size=20, dominance_threshold=0.70)
    ]
    
    best_signal = None
    best_confidence = 0
    
    for strategy in strategies:
        try:
            result = strategy.analyze(history)
            if result:
                confidence = strategy.get_confidence_level(history)
                if confidence > best_confidence and confidence >= 80:  # Solo señales muy seguras
                    best_signal = (result, strategy.name, confidence)
                    best_confidence = confidence
        except Exception as e:
            logger.error(f"Error en estrategia {strategy.name}: {e}")
            continue
    
    return best_signal
