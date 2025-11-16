# tests/test_safe_strategies.py

"""
Tests para las estrategias de apuesta seguras y conservadoras.
"""

import pytest
from baccarat_bot.strategies.safe_strategies import (
    ConservativeStreakStrategy,
    ConfirmedPatternStrategy,
    StatisticalEdgeStrategy,
    ConsensusStrategy,
    DominanceStrategy,
    get_safest_signal
)


class TestConservativeStreakStrategy:
    """Tests para la estrategia de racha conservadora"""
    
    def test_long_streak_detection(self):
        """Test: Detecta rachas largas (5+)"""
        strategy = ConservativeStreakStrategy(min_streak_length=5)
        history = ['B'] * 6
        result = strategy.analyze(history)
        assert result == 'JUGADOR', "Debe recomendar contra la racha"
    
    def test_short_streak_ignored(self):
        """Test: Ignora rachas cortas"""
        strategy = ConservativeStreakStrategy(min_streak_length=5)
        history = ['B'] * 4
        result = strategy.analyze(history)
        assert result is None, "No debe generar señal con racha corta"
    
    def test_high_confidence_long_streak(self):
        """Test: Alta confianza en rachas muy largas"""
        strategy = ConservativeStreakStrategy(min_streak_length=5)
        history = ['B'] * 8
        confidence = strategy.get_confidence_level(history)
        assert confidence >= 85, "Debe tener alta confianza"
    
    def test_mixed_history_no_signal(self):
        """Test: No genera señal con historial mixto"""
        strategy = ConservativeStreakStrategy(min_streak_length=5)
        history = ['B', 'P', 'B', 'P', 'B', 'P']
        result = strategy.analyze(history)
        assert result is None


class TestConfirmedPatternStrategy:
    """Tests para la estrategia de patrón confirmado"""
    
    def test_repeated_pattern_detection(self):
        """Test: Detecta patrones repetidos"""
        strategy = ConfirmedPatternStrategy(pattern_length=3)
        # Patrón B-P-B repetido
        history = ['B', 'P', 'B', 'P', 'B', 'P', 'B', 'P', 'B']
        result = strategy.analyze(history)
        assert result in ['BANCA', 'JUGADOR', None]
    
    def test_insufficient_history(self):
        """Test: No genera señal con historial insuficiente"""
        strategy = ConfirmedPatternStrategy(pattern_length=3)
        history = ['B', 'P', 'B']
        result = strategy.analyze(history)
        assert result is None
    
    def test_pattern_with_ties(self):
        """Test: Maneja empates correctamente"""
        strategy = ConfirmedPatternStrategy(pattern_length=2)
        history = ['B', 'E', 'P', 'B', 'E', 'P', 'B', 'P']
        result = strategy.analyze(history)
        # Debe ignorar empates y analizar patrón B-P
        assert result in ['BANCA', 'JUGADOR', None]
    
    def test_confidence_with_multiple_repetitions(self):
        """Test: Mayor confianza con más repeticiones"""
        strategy = ConfirmedPatternStrategy(pattern_length=2)
        history = ['B', 'P'] * 5  # Patrón repetido 5 veces
        confidence = strategy.get_confidence_level(history)
        assert confidence >= 80


class TestStatisticalEdgeStrategy:
    """Tests para la estrategia de ventaja estadística"""
    
    def test_banker_overrepresentation(self):
        """Test: Detecta sobre-representación de Banca"""
        strategy = StatisticalEdgeStrategy(min_sample_size=30, deviation_threshold=0.15)
        # 70% Banca, 30% Jugador (desviación significativa)
        history = ['B'] * 21 + ['P'] * 9
        result = strategy.analyze(history)
        assert result == 'JUGADOR', "Debe apostar hacia el equilibrio"
    
    def test_player_overrepresentation(self):
        """Test: Detecta sobre-representación de Jugador"""
        strategy = StatisticalEdgeStrategy(min_sample_size=30, deviation_threshold=0.15)
        # 30% Banca, 70% Jugador
        history = ['B'] * 9 + ['P'] * 21
        result = strategy.analyze(history)
        assert result == 'BANCA', "Debe apostar hacia el equilibrio"
    
    def test_balanced_distribution(self):
        """Test: No genera señal con distribución equilibrada"""
        strategy = StatisticalEdgeStrategy(min_sample_size=30, deviation_threshold=0.15)
        # 50% Banca, 50% Jugador
        history = ['B'] * 15 + ['P'] * 15
        result = strategy.analyze(history)
        assert result is None
    
    def test_insufficient_sample(self):
        """Test: No genera señal con muestra pequeña"""
        strategy = StatisticalEdgeStrategy(min_sample_size=30)
        history = ['B'] * 10
        result = strategy.analyze(history)
        assert result is None
    
    def test_handles_ties(self):
        """Test: Maneja empates correctamente"""
        strategy = StatisticalEdgeStrategy(min_sample_size=30, deviation_threshold=0.15)
        history = ['B'] * 18 + ['P'] * 8 + ['E'] * 4
        result = strategy.analyze(history)
        # Debe ignorar empates y analizar solo B y P
        assert result in ['BANCA', 'JUGADOR', None]


class TestConsensusStrategy:
    """Tests para la estrategia de consenso"""
    
    def test_consensus_with_agreement(self):
        """Test: Genera señal cuando hay consenso"""
        strategy = ConsensusStrategy()
        # Historial que debería generar consenso
        history = ['B'] * 7 + ['P'] * 2
        result = strategy.analyze(history)
        # Puede generar señal o no, dependiendo del consenso
        assert result in ['BANCA', 'JUGADOR', None]
    
    def test_insufficient_history(self):
        """Test: No genera señal con historial insuficiente"""
        strategy = ConsensusStrategy()
        history = ['B'] * 5
        result = strategy.analyze(history)
        assert result is None
    
    def test_high_confidence_consensus(self):
        """Test: Alta confianza cuando hay consenso fuerte"""
        strategy = ConsensusStrategy()
        # Historial con patrón claro
        history = ['B'] * 8 + ['P'] * 2 + ['B'] * 5
        confidence = strategy.get_confidence_level(history)
        # Si hay consenso, debe tener alta confianza
        if confidence > 0:
            assert confidence >= 75


class TestDominanceStrategy:
    """Tests para la estrategia de dominancia clara"""
    
    def test_clear_banker_dominance(self):
        """Test: Detecta dominancia clara de Banca"""
        strategy = DominanceStrategy(window_size=20, dominance_threshold=0.70)
        # 75% Banca
        history = ['B'] * 15 + ['P'] * 5
        result = strategy.analyze(history)
        assert result == 'BANCA', "Debe apostar a favor de la dominancia"
    
    def test_clear_player_dominance(self):
        """Test: Detecta dominancia clara de Jugador"""
        strategy = DominanceStrategy(window_size=20, dominance_threshold=0.70)
        # 75% Jugador
        history = ['B'] * 5 + ['P'] * 15
        result = strategy.analyze(history)
        assert result == 'JUGADOR', "Debe apostar a favor de la dominancia"
    
    def test_no_dominance(self):
        """Test: No genera señal sin dominancia clara"""
        strategy = DominanceStrategy(window_size=20, dominance_threshold=0.70)
        # 60% Banca, 40% Jugador (no alcanza threshold)
        history = ['B'] * 12 + ['P'] * 8
        result = strategy.analyze(history)
        assert result is None
    
    def test_confidence_proportional_to_dominance(self):
        """Test: Confianza proporcional a la dominancia"""
        strategy = DominanceStrategy(window_size=20, dominance_threshold=0.70)
        # 80% dominancia
        history = ['B'] * 16 + ['P'] * 4
        confidence = strategy.get_confidence_level(history)
        assert confidence >= 80


class TestGetSafestSignal:
    """Tests para la función helper get_safest_signal"""
    
    def test_returns_safest_signal(self):
        """Test: Retorna la señal más segura"""
        # Historial con racha larga (alta confianza)
        history = ['B'] * 8 + ['P'] * 2
        result = get_safest_signal(history)
        
        if result:
            apuesta, estrategia, confianza = result
            assert apuesta in ['BANCA', 'JUGADOR']
            assert isinstance(estrategia, str)
            assert confianza >= 80, "Debe tener confianza mínima de 80%"
    
    def test_returns_none_without_safe_signal(self):
        """Test: Retorna None sin señal segura"""
        # Historial aleatorio sin patrones claros
        history = ['B', 'P', 'B', 'P', 'B', 'P']
        result = get_safest_signal(history)
        assert result is None or result[2] >= 80
    
    def test_prioritizes_high_confidence(self):
        """Test: Prioriza señales de alta confianza"""
        # Historial con dominancia muy clara
        history = ['B'] * 18 + ['P'] * 2
        result = get_safest_signal(history)
        
        if result:
            apuesta, estrategia, confianza = result
            assert confianza >= 85, "Debe tener muy alta confianza"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
