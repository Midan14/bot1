# baccarat_bot/utils/validators.py

"""
Módulo de validación de datos usando Pydantic.
Proporciona modelos de datos tipados y validados para garantizar la integridad.
"""

from pydantic import BaseModel, Field, validator, HttpUrl
from typing import List, Optional, Literal
from datetime import datetime


class MesaData(BaseModel):
    """Modelo de validación para datos de mesa"""
    nombre: str = Field(..., min_length=1, max_length=100)
    url: str = Field(..., description="URL de la mesa")
    game_id: str = Field(..., pattern=r'^\d+$', description="ID numérico del juego")
    historial_resultados: List[str] = Field(default_factory=list)
    
    @validator('url')
    def validate_url(cls, v):
        """Valida que la URL sea válida y use HTTPS"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL debe comenzar con http:// o https://')
        if '1xbet.com' not in v:
            raise ValueError('URL debe ser de 1xbet.com')
        return v
    
    @validator('historial_resultados')
    def validate_historial(cls, v):
        """Valida que el historial contenga solo valores válidos"""
        valid_results = {'B', 'P', 'E'}
        for result in v:
            if result not in valid_results:
                raise ValueError(f'Resultado inválido: {result}. Debe ser B, P o E')
        return v
    
    class Config:
        validate_assignment = True


class ResultadoData(BaseModel):
    """Modelo de validación para resultados de juego"""
    mesa: str = Field(..., min_length=1)
    resultado: Literal['B', 'P', 'E'] = Field(..., description="Resultado: B (Banca), P (Jugador), E (Empate)")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)
    
    class Config:
        validate_assignment = True


class SenalData(BaseModel):
    """Modelo de validación para señales de apuesta"""
    mesa: str = Field(..., min_length=1)
    tipo_senal: str = Field(..., min_length=1)
    resultado_recomendado: Literal['BANCA', 'JUGADOR', 'EMPATE']
    historial: List[str] = Field(..., min_items=1)
    confianza: int = Field(..., ge=0, le=100, description="Nivel de confianza 0-100")
    exito: Optional[bool] = None
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)
    
    @validator('historial')
    def validate_historial(cls, v):
        """Valida que el historial contenga solo valores válidos"""
        valid_results = {'B', 'P', 'E'}
        for result in v:
            if result not in valid_results:
                raise ValueError(f'Resultado inválido en historial: {result}')
        return v
    
    class Config:
        validate_assignment = True


class ConfiguracionBot(BaseModel):
    """Modelo de validación para configuración del bot"""
    telegram_token: str = Field(..., min_length=30)
    telegram_chat_id: str = Field(..., pattern=r'^-?\d+$')
    intervalo_monitoreo: int = Field(default=120, ge=30, le=600)
    longitud_racha: int = Field(default=3, ge=2, le=10)
    minimo_tiempo_entre_senales: int = Field(default=600, ge=60, le=3600)
    usar_datos_reales: bool = Field(default=False)
    log_level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = Field(default='INFO')
    
    @validator('telegram_token')
    def validate_token(cls, v):
        """Valida formato básico del token de Telegram"""
        if ':' not in v:
            raise ValueError('Token de Telegram debe contener ":"')
        return v
    
    class Config:
        validate_assignment = True


class EstadisticasMesa(BaseModel):
    """Modelo de validación para estadísticas de mesa"""
    mesa: str = Field(..., min_length=1)
    total_jugadas: int = Field(default=0, ge=0)
    senales_generadas: int = Field(default=0, ge=0)
    senales_acertadas: int = Field(default=0, ge=0)
    precision_senales: float = Field(default=0.0, ge=0.0, le=100.0)
    
    @validator('senales_acertadas')
    def validate_senales_acertadas(cls, v, values):
        """Valida que señales acertadas no supere señales generadas"""
        if 'senales_generadas' in values and v > values['senales_generadas']:
            raise ValueError('Señales acertadas no puede superar señales generadas')
        return v
    
    class Config:
        validate_assignment = True


def validar_mesa_data(data: dict) -> MesaData:
    """
    Valida y convierte un diccionario a MesaData
    
    Args:
        data: Diccionario con datos de mesa
        
    Returns:
        MesaData validado
        
    Raises:
        ValidationError: Si los datos no son válidos
    """
    return MesaData(**data)


def validar_resultado(mesa: str, resultado: str) -> ResultadoData:
    """
    Valida un resultado de juego
    
    Args:
        mesa: Nombre de la mesa
        resultado: Resultado del juego (B, P, E)
        
    Returns:
        ResultadoData validado
        
    Raises:
        ValidationError: Si los datos no son válidos
    """
    return ResultadoData(mesa=mesa, resultado=resultado)


def validar_senal(
    mesa: str,
    tipo_senal: str,
    resultado_recomendado: str,
    historial: List[str],
    confianza: int,
    exito: Optional[bool] = None
) -> SenalData:
    """
    Valida una señal de apuesta
    
    Args:
        mesa: Nombre de la mesa
        tipo_senal: Tipo de estrategia
        resultado_recomendado: Resultado recomendado
        historial: Historial de resultados
        confianza: Nivel de confianza (0-100)
        exito: Si la señal fue exitosa (opcional)
        
    Returns:
        SenalData validado
        
    Raises:
        ValidationError: Si los datos no son válidos
    """
    return SenalData(
        mesa=mesa,
        tipo_senal=tipo_senal,
        resultado_recomendado=resultado_recomendado,
        historial=historial,
        confianza=confianza,
        exito=exito
    )
