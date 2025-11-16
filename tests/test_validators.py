# tests/test_validators.py

"""
Tests unitarios para el módulo de validación de datos.
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from baccarat_bot.utils.validators import (
    MesaData,
    ResultadoData,
    SenalData,
    ConfiguracionBot,
    EstadisticasMesa,
    validar_mesa_data,
    validar_resultado,
    validar_senal
)
from pydantic import ValidationError


class TestMesaData:
    """Tests para validación de datos de mesa"""
    
    def test_mesa_data_valid(self):
        """Test: Datos de mesa válidos"""
        mesa = MesaData(
            nombre="Speed Baccarat 1",
            url="https://col.1xbet.com/es/casino/game/97408/",
            game_id="97408",
            historial_resultados=['B', 'P', 'B']
        )
        assert mesa.nombre == "Speed Baccarat 1"
        assert mesa.game_id == "97408"
    
    def test_mesa_data_invalid_url(self):
        """Test: URL inválida debe fallar"""
        with pytest.raises(ValidationError):
            MesaData(
                nombre="Test Mesa",
                url="invalid-url",
                game_id="12345"
            )
    
    def test_mesa_data_invalid_game_id(self):
        """Test: Game ID no numérico debe fallar"""
        with pytest.raises(ValidationError):
            MesaData(
                nombre="Test Mesa",
                url="https://col.1xbet.com/es/casino/game/97408/",
                game_id="abc123"
            )
    
    def test_mesa_data_invalid_historial(self):
        """Test: Historial con valores inválidos debe fallar"""
        with pytest.raises(ValidationError):
            MesaData(
                nombre="Test Mesa",
                url="https://col.1xbet.com/es/casino/game/97408/",
                game_id="97408",
                historial_resultados=['B', 'P', 'X']  # 'X' es inválido
            )
    
    def test_mesa_data_empty_name(self):
        """Test: Nombre vacío debe fallar"""
        with pytest.raises(ValidationError):
            MesaData(
                nombre="",
                url="https://col.1xbet.com/es/casino/game/97408/",
                game_id="97408"
            )


class TestResultadoData:
    """Tests para validación de resultados"""
    
    def test_resultado_valid_banca(self):
        """Test: Resultado válido Banca"""
        resultado = ResultadoData(
            mesa="Speed Baccarat 1",
            resultado="B"
        )
        assert resultado.resultado == "B"
        assert isinstance(resultado.timestamp, datetime)
    
    def test_resultado_valid_jugador(self):
        """Test: Resultado válido Jugador"""
        resultado = ResultadoData(
            mesa="Speed Baccarat 1",
            resultado="P"
        )
        assert resultado.resultado == "P"
    
    def test_resultado_valid_empate(self):
        """Test: Resultado válido Empate"""
        resultado = ResultadoData(
            mesa="Speed Baccarat 1",
            resultado="E"
        )
        assert resultado.resultado == "E"
    
    def test_resultado_invalid(self):
        """Test: Resultado inválido debe fallar"""
        with pytest.raises(ValidationError):
            ResultadoData(
                mesa="Speed Baccarat 1",
                resultado="X"  # Inválido
            )


class TestSenalData:
    """Tests para validación de señales"""
    
    def test_senal_valid(self):
        """Test: Señal válida"""
        senal = SenalData(
            mesa="Speed Baccarat 1",
            tipo_senal="Racha",
            resultado_recomendado="BANCA",
            historial=['B', 'P', 'B'],
            confianza=75
        )
        assert senal.confianza == 75
        assert senal.resultado_recomendado == "BANCA"
    
    def test_senal_invalid_confianza_low(self):
        """Test: Confianza negativa debe fallar"""
        with pytest.raises(ValidationError):
            SenalData(
                mesa="Speed Baccarat 1",
                tipo_senal="Racha",
                resultado_recomendado="BANCA",
                historial=['B', 'P', 'B'],
                confianza=-10
            )
    
    def test_senal_invalid_confianza_high(self):
        """Test: Confianza mayor a 100 debe fallar"""
        with pytest.raises(ValidationError):
            SenalData(
                mesa="Speed Baccarat 1",
                tipo_senal="Racha",
                resultado_recomendado="BANCA",
                historial=['B', 'P', 'B'],
                confianza=150
            )
    
    def test_senal_invalid_historial(self):
        """Test: Historial con valores inválidos debe fallar"""
        with pytest.raises(ValidationError):
            SenalData(
                mesa="Speed Baccarat 1",
                tipo_senal="Racha",
                resultado_recomendado="BANCA",
                historial=['B', 'P', 'X'],  # 'X' inválido
                confianza=75
            )
    
    def test_senal_empty_historial(self):
        """Test: Historial vacío debe fallar"""
        with pytest.raises(ValidationError):
            SenalData(
                mesa="Speed Baccarat 1",
                tipo_senal="Racha",
                resultado_recomendado="BANCA",
                historial=[],  # Vacío
                confianza=75
            )


class TestConfiguracionBot:
    """Tests para validación de configuración"""
    
    def test_configuracion_valid(self):
        """Test: Configuración válida"""
        config = ConfiguracionBot(
            telegram_token="123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
            telegram_chat_id="123456789",
            intervalo_monitoreo=120,
            longitud_racha=3
        )
        assert config.intervalo_monitoreo == 120
        assert config.longitud_racha == 3
    
    def test_configuracion_invalid_token(self):
        """Test: Token sin ':' debe fallar"""
        with pytest.raises(ValidationError):
            ConfiguracionBot(
                telegram_token="invalid_token_without_colon",
                telegram_chat_id="123456789"
            )
    
    def test_configuracion_invalid_intervalo_low(self):
        """Test: Intervalo muy bajo debe fallar"""
        with pytest.raises(ValidationError):
            ConfiguracionBot(
                telegram_token="123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
                telegram_chat_id="123456789",
                intervalo_monitoreo=10  # Menor a 30
            )
    
    def test_configuracion_invalid_intervalo_high(self):
        """Test: Intervalo muy alto debe fallar"""
        with pytest.raises(ValidationError):
            ConfiguracionBot(
                telegram_token="123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
                telegram_chat_id="123456789",
                intervalo_monitoreo=700  # Mayor a 600
            )


class TestEstadisticasMesa:
    """Tests para validación de estadísticas"""
    
    def test_estadisticas_valid(self):
        """Test: Estadísticas válidas"""
        stats = EstadisticasMesa(
            mesa="Speed Baccarat 1",
            total_jugadas=100,
            senales_generadas=20,
            senales_acertadas=15,
            precision_senales=75.0
        )
        assert stats.precision_senales == 75.0
    
    def test_estadisticas_senales_acertadas_exceed(self):
        """Test: Señales acertadas no puede superar generadas"""
        with pytest.raises(ValidationError):
            EstadisticasMesa(
                mesa="Speed Baccarat 1",
                total_jugadas=100,
                senales_generadas=20,
                senales_acertadas=25,  # Mayor que generadas
                precision_senales=75.0
            )
    
    def test_estadisticas_negative_values(self):
        """Test: Valores negativos deben fallar"""
        with pytest.raises(ValidationError):
            EstadisticasMesa(
                mesa="Speed Baccarat 1",
                total_jugadas=-10,  # Negativo
                senales_generadas=20
            )


class TestValidationFunctions:
    """Tests para funciones de validación"""
    
    def test_validar_mesa_data(self):
        """Test: Función validar_mesa_data"""
        data = {
            'nombre': 'Speed Baccarat 1',
            'url': 'https://col.1xbet.com/es/casino/game/97408/',
            'game_id': '97408',
            'historial_resultados': ['B', 'P']
        }
        mesa = validar_mesa_data(data)
        assert isinstance(mesa, MesaData)
        assert mesa.nombre == 'Speed Baccarat 1'
    
    def test_validar_resultado(self):
        """Test: Función validar_resultado"""
        resultado = validar_resultado('Speed Baccarat 1', 'B')
        assert isinstance(resultado, ResultadoData)
        assert resultado.resultado == 'B'
    
    def test_validar_senal(self):
        """Test: Función validar_senal"""
        senal = validar_senal(
            mesa='Speed Baccarat 1',
            tipo_senal='Racha',
            resultado_recomendado='BANCA',
            historial=['B', 'P', 'B'],
            confianza=75
        )
        assert isinstance(senal, SenalData)
        assert senal.confianza == 75


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
