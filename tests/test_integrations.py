# tests/test_integrations.py

"""
Tests para las integraciones: anti-detección, sincronización en tiempo real, etc.
"""

import pytest
from datetime import datetime
from baccarat_bot.integrations.realtime_sync import (
    GameState,
    GameRound,
    RealtimeSynchronizer
)


class TestGameRound:
    """Tests para la clase GameRound"""
    
    def test_is_betting_open_with_time(self):
        """Test: Detecta cuando las apuestas están abiertas"""
        game_round = GameRound(
            round_number=1,
            state=GameState.WAITING_FOR_BETS,
            time_remaining=20,
            last_result='B',
            history=['B', 'P', 'B'],
            timestamp=datetime.now()
        )
        assert game_round.is_betting_open() is True
    
    def test_is_betting_closed(self):
        """Test: Detecta cuando las apuestas están cerradas"""
        game_round = GameRound(
            round_number=1,
            state=GameState.BETTING_CLOSED,
            time_remaining=0,
            last_result='B',
            history=['B', 'P', 'B'],
            timestamp=datetime.now()
        )
        assert game_round.is_betting_open() is False
    
    def test_is_betting_open_low_time(self):
        """Test: No considera abierto con poco tiempo"""
        game_round = GameRound(
            round_number=1,
            state=GameState.WAITING_FOR_BETS,
            time_remaining=3,
            last_result='B',
            history=['B', 'P', 'B'],
            timestamp=datetime.now()
        )
        assert game_round.is_betting_open() is False
    
    def test_should_send_signal_optimal_timing(self):
        """Test: Detecta timing óptimo para señal"""
        game_round = GameRound(
            round_number=1,
            state=GameState.WAITING_FOR_BETS,
            time_remaining=20,
            last_result='B',
            history=['B', 'P', 'B'],
            timestamp=datetime.now()
        )
        assert game_round.should_send_signal() is True
    
    def test_should_send_signal_too_early(self):
        """Test: No envía señal muy temprano"""
        game_round = GameRound(
            round_number=1,
            state=GameState.WAITING_FOR_BETS,
            time_remaining=30,
            last_result='B',
            history=['B', 'P', 'B'],
            timestamp=datetime.now()
        )
        assert game_round.should_send_signal() is False
    
    def test_should_send_signal_too_late(self):
        """Test: No envía señal muy tarde"""
        game_round = GameRound(
            round_number=1,
            state=GameState.WAITING_FOR_BETS,
            time_remaining=10,
            last_result='B',
            history=['B', 'P', 'B'],
            timestamp=datetime.now()
        )
        assert game_round.should_send_signal() is False


class TestRealtimeSynchronizer:
    """Tests para el sincronizador en tiempo real"""
    
    def test_initialization(self):
        """Test: Inicialización correcta"""
        sync = RealtimeSynchronizer()
        assert sync.sync_interval == 2
        assert len(sync.current_rounds) == 0
    
    def test_get_current_round_none(self):
        """Test: Retorna None si no hay ronda"""
        sync = RealtimeSynchronizer()
        result = sync.get_current_round('mesa_test')
        assert result is None
    
    def test_is_sync_needed_first_time(self):
        """Test: Necesita sync la primera vez"""
        sync = RealtimeSynchronizer()
        assert sync.is_sync_needed('mesa_test') is True
    
    def test_store_and_retrieve_round(self):
        """Test: Almacena y recupera ronda correctamente"""
        sync = RealtimeSynchronizer()
        
        game_round = GameRound(
            round_number=1,
            state=GameState.WAITING_FOR_BETS,
            time_remaining=20,
            last_result='B',
            history=['B', 'P', 'B'],
            timestamp=datetime.now()
        )
        
        # Almacenar
        sync.current_rounds['mesa_test'] = game_round
        sync.last_sync_time['mesa_test'] = datetime.now()
        
        # Recuperar
        retrieved = sync.get_current_round('mesa_test')
        assert retrieved is not None
        assert retrieved.round_number == 1
        assert retrieved.state == GameState.WAITING_FOR_BETS


class TestGameState:
    """Tests para el enum GameState"""
    
    def test_all_states_exist(self):
        """Test: Todos los estados existen"""
        states = [
            GameState.WAITING_FOR_BETS,
            GameState.BETTING_CLOSED,
            GameState.DEALING,
            GameState.REVEALING,
            GameState.FINISHED,
            GameState.SHUFFLING,
            GameState.UNKNOWN
        ]
        assert len(states) == 7
    
    def test_state_values(self):
        """Test: Valores de estados son correctos"""
        assert GameState.WAITING_FOR_BETS.value == "waiting_for_bets"
        assert GameState.BETTING_CLOSED.value == "betting_closed"
        assert GameState.DEALING.value == "dealing"
        assert GameState.SHUFFLING.value == "shuffling"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
