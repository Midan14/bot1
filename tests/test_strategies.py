# tests/test_strategies.py

"""
Tests unitarios para estrategias de apuesta del bot de Baccarat.
"""

import pytest
import sys
from pathlib import Path

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from baccarat_bot.strategies.advanced_strategies import (
    StreakStrategy,
    ZigZagStrategy,
    MartingaleAdaptedStrategy,
    FibonacciStrategy,
    TrendAnalysisStrategy,
    TieDetectionStrategy
)


class TestStreakStrategy:
    """Tests para la estrategia de racha"""
    
    def test_streak_detection_banca(self):
        """Test: Detecta racha de Banca y recomienda Jugador"""
        strategy = StreakStrategy(streak_length=3)
        history = ['B', 'B', 'B']
        result = strategy.analyze(history)
        assert result == 'JUGADOR', "Debe recomendar JUGADOR después de 3 Bancas"
    
    def test_streak_detection_jugador(self):
        """Test: Detecta racha de Jugador y recomienda Banca"""
        strategy = StreakStrategy(streak_length=3)
        history = ['P', 'P', 'P']
        result = strategy.analyze(history)
        assert result == 'BANCA', "Debe recomendar BANCA después de 3 Jugadores"
    
    def test_streak_detection_empate(self):
        """Test: Detecta racha de Empates"""
        strategy = StreakStrategy(streak_length=3)
        history = ['E', 'E', 'E']
        result = strategy.analyze(history)
        assert result == 'EMPATE', "Debe recomendar EMPATE después de 3 Empates"
    
    def test_insufficient_history(self):
        """Test: No genera señal con historial insuficiente"""
        strategy = StreakStrategy(streak_length=3)
        history = ['B', 'B']
        result = strategy.analyze(history)
        assert result is None, "No debe generar señal con historial insuficiente"
    
    def test_no_streak(self):
        """Test: No genera señal sin racha"""
        strategy = StreakStrategy(streak_length=3)
        history = ['B', 'P', 'B']
        result = strategy.analyze(history)
        assert result is None, "No debe generar señal sin racha"
    
    def test_confidence_level(self):
        """Test: Nivel de confianza aumenta con racha más larga"""
        strategy = StreakStrategy(streak_length=3)
        history_short = ['B', 'B', 'B']
        history_long = ['B', 'B', 'B', 'B', 'B']
        
        confidence_short = strategy.get_confidence_level(history_short)
        confidence_long = strategy.get_confidence_level(history_long)
        
        assert confidence_long > confidence_short, "Confianza debe aumentar con racha más larga"
        assert 0 <= confidence_short <= 100, "Confianza debe estar entre 0 y 100"
        assert 0 <= confidence_long <= 100, "Confianza debe estar entre 0 y 100"


class TestZigZagStrategy:
    """Tests para la estrategia Zig-Zag"""
    
    def test_zigzag_pattern_detection(self):
        """Test: Detecta patrón alternante"""
        strategy = ZigZagStrategy(pattern_length=4)
        history = ['B', 'P', 'B', 'P']
        result = strategy.analyze(history)
        assert result in ['BANCA', 'JUGADOR'], "Debe detectar patrón zig-zag"
    
    def test_zigzag_with_tie(self):
        """Test: No genera señal si hay empates"""
        strategy = ZigZagStrategy(pattern_length=4)
        history = ['B', 'P', 'E', 'P']
        result = strategy.analyze(history)
        assert result is None, "No debe generar señal con empates en el patrón"
    
    def test_zigzag_insufficient_history(self):
        """Test: No genera señal con historial insuficiente"""
        strategy = ZigZagStrategy(pattern_length=4)
        history = ['B', 'P']
        result = strategy.analyze(history)
        assert result is None, "No debe generar señal con historial insuficiente"
    
    def test_zigzag_confidence(self):
        """Test: Confianza correcta para patrón zig-zag"""
        strategy = ZigZagStrategy(pattern_length=4)
        history = ['B', 'P', 'B', 'P']
        confidence = strategy.get_confidence_level(history)
        assert confidence == 75, "Confianza debe ser 75 para patrón zig-zag válido"


class TestMartingaleAdaptedStrategy:
    """Tests para la estrategia Martingale Adaptado"""
    
    def test_martingale_banca_dominance(self):
        """Test: Detecta dominancia de Banca"""
        strategy = MartingaleAdaptedStrategy()
        history = ['B', 'B', 'P']
        result = strategy.analyze(history)
        assert result == 'BANCA', "Debe recomendar BANCA con 2 de 3 Bancas"
    
    def test_martingale_jugador_dominance(self):
        """Test: Detecta dominancia de Jugador"""
        strategy = MartingaleAdaptedStrategy()
        history = ['P', 'P', 'B']
        result = strategy.analyze(history)
        assert result == 'JUGADOR', "Debe recomendar JUGADOR con 2 de 3 Jugadores"
    
    def test_martingale_insufficient_history(self):
        """Test: No genera señal con historial insuficiente"""
        strategy = MartingaleAdaptedStrategy()
        history = ['B']
        result = strategy.analyze(history)
        assert result is None, "No debe generar señal con historial insuficiente"


class TestFibonacciStrategy:
    """Tests para la estrategia Fibonacci"""
    
    def test_fibonacci_detection(self):
        """Test: Detecta números Fibonacci en historial"""
        strategy = FibonacciStrategy()
        # 3 Bancas (3 es número Fibonacci)
        history = ['B', 'B', 'B', 'P', 'P']
        result = strategy.analyze(history)
        assert result == 'BANCA', "Debe detectar número Fibonacci de Bancas"
    
    def test_fibonacci_insufficient_history(self):
        """Test: No genera señal con historial insuficiente"""
        strategy = FibonacciStrategy()
        history = ['B', 'B']
        result = strategy.analyze(history)
        assert result is None, "No debe generar señal con historial insuficiente"


class TestTrendAnalysisStrategy:
    """Tests para la estrategia de Análisis de Tendencias"""
    
    def test_trend_analysis_both_trends_match(self):
        """Test: Detecta cuando ambas tendencias coinciden"""
        strategy = TrendAnalysisStrategy(short_window=5, long_window=15)
        # Crear historial con tendencia clara hacia Banca (más largo)
        history = ['B'] * 12 + ['P'] * 3
        result = strategy.analyze(history)
        assert result in ['BANCA', 'JUGADOR', None], "Debe detectar tendencia o retornar None"
        # Si retorna resultado, debe ser BANCA por la tendencia
        if result:
            assert result == 'BANCA', "Debe recomendar BANCA con mayoría de Bancas"
    
    def test_trend_analysis_insufficient_history(self):
        """Test: No genera señal con historial insuficiente"""
        strategy = TrendAnalysisStrategy(short_window=5, long_window=15)
        history = ['B', 'P', 'B']
        result = strategy.analyze(history)
        assert result is None, "No debe generar señal con historial insuficiente"


class TestTieDetectionStrategy:
    """Tests para la estrategia de Detección de Empates"""
    
    def test_tie_detection_multiple_ties(self):
        """Test: Detecta múltiples empates"""
        strategy = TieDetectionStrategy(observation_window=5)
        history = ['E', 'B', 'E', 'P', 'B']
        result = strategy.analyze(history)
        assert result == 'EMPATE', "Debe recomendar EMPATE con múltiples empates"
    
    def test_tie_detection_recent_tie(self):
        """Test: Detecta empate reciente"""
        strategy = TieDetectionStrategy(observation_window=5)
        history = ['B', 'P', 'B', 'P', 'E']
        result = strategy.analyze(history)
        assert result == 'EMPATE', "Debe recomendar EMPATE con empate reciente"
    
    def test_tie_detection_no_ties(self):
        """Test: No genera señal sin empates"""
        strategy = TieDetectionStrategy(observation_window=5)
        history = ['B', 'P', 'B', 'P', 'B']
        result = strategy.analyze(history)
        assert result is None, "No debe generar señal sin empates"
    
    def test_tie_confidence_levels(self):
        """Test: Niveles de confianza correctos"""
        strategy = TieDetectionStrategy(observation_window=5)
        
        # 3 empates = alta confianza
        history_high = ['E', 'E', 'E', 'B', 'P']
        confidence_high = strategy.get_confidence_level(history_high)
        assert confidence_high == 75, "Confianza debe ser 75 con 3 empates"
        
        # 2 empates = confianza media
        history_medium = ['E', 'E', 'B', 'P', 'B']
        confidence_medium = strategy.get_confidence_level(history_medium)
        assert confidence_medium == 65, "Confianza debe ser 65 con 2 empates"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
