# baccarat_bot/config_unified.py

"""
Configuración unificada y centralizada del bot de Baccarat.
Consolida config.py y config_enhanced.py en una sola fuente de verdad.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List
from dotenv import load_dotenv
import logging

# Cargar variables de entorno
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class TelegramConfig:
    """Configuración de Telegram"""
    token: str = field(default_factory=lambda: os.getenv('TELEGRAM_BOT_TOKEN', ''))
    chat_id: str = field(default_factory=lambda: os.getenv('TELEGRAM_CHAT_ID', ''))
    
    def validate(self) -> bool:
        """Valida que la configuración de Telegram sea correcta"""
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN no está configurado")
        if not self.chat_id:
            raise ValueError("TELEGRAM_CHAT_ID no está configurado")
        if ':' not in self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN tiene formato inválido")
        return True


@dataclass
class MonitoringConfig:
    """Configuración de monitoreo"""
    intervalo_monitoreo: int = field(
        default_factory=lambda: int(os.getenv('INTERVALO_MONITOREO', '120'))
    )
    longitud_racha: int = field(
        default_factory=lambda: int(os.getenv('LONGITUD_RACHA', '3'))
    )
    minimo_tiempo_entre_senales: int = field(
        default_factory=lambda: int(os.getenv('MINIMO_TIEMPO_ENTRE_SENALES', '600'))
    )
    usar_datos_reales: bool = field(
        default_factory=lambda: os.getenv('USAR_DATOS_REALES', 'false').lower() == 'true'
    )
    
    def validate(self) -> bool:
        """Valida que la configuración de monitoreo sea correcta"""
        if self.intervalo_monitoreo < 30:
            raise ValueError("INTERVALO_MONITOREO debe ser al menos 30 segundos")
        if self.intervalo_monitoreo > 600:
            logger.warning("INTERVALO_MONITOREO muy alto (>10 min), puede perder señales")
        if self.longitud_racha < 2:
            raise ValueError("LONGITUD_RACHA debe ser al menos 2")
        if self.minimo_tiempo_entre_senales < 60:
            raise ValueError("MINIMO_TIEMPO_ENTRE_SENALES debe ser al menos 60 segundos")
        return True


@dataclass
class TimingConfig:
    """Configuración de detección de timing"""
    signal_cooldown_default: int = 300  # 5 minutos
    signal_cooldown_emergency: int = 180  # 3 minutos
    max_frequency: int = 30  # 30 segundos mínimo
    min_samples_for_confidence: int = 5
    max_timing_variance: float = 5.0
    safety_margin_multiplier: float = 1.2
    
    def validate(self) -> bool:
        """Valida que la configuración de timing sea correcta"""
        if self.signal_cooldown_default < self.max_frequency:
            raise ValueError("signal_cooldown_default debe ser mayor que max_frequency")
        if self.safety_margin_multiplier < 1.0:
            raise ValueError("safety_margin_multiplier debe ser al menos 1.0")
        return True


@dataclass
class APIConfig:
    """Configuración del servidor API"""
    host: str = field(default_factory=lambda: os.getenv('API_HOST', '0.0.0.0'))
    port: int = field(default_factory=lambda: int(os.getenv('API_PORT', '8000')))
    debug: bool = field(default_factory=lambda: os.getenv('API_DEBUG', 'false').lower() == 'true')
    enable_cors: bool = True
    
    def validate(self) -> bool:
        """Valida que la configuración de API sea correcta"""
        if self.port < 1024 or self.port > 65535:
            raise ValueError("API_PORT debe estar entre 1024 y 65535")
        return True


@dataclass
class DatabaseConfig:
    """Configuración de base de datos"""
    db_path: str = field(default_factory=lambda: os.getenv('DB_PATH', 'baccarat_bot.db'))
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    cleanup_days: int = 30  # Días de retención de datos antiguos
    
    def validate(self) -> bool:
        """Valida que la configuración de base de datos sea correcta"""
        if self.cleanup_days < 1:
            raise ValueError("cleanup_days debe ser al menos 1")
        return True


@dataclass
class LoggingConfig:
    """Configuración de logging"""
    level: str = field(default_factory=lambda: os.getenv('LOG_LEVEL', 'INFO'))
    file: str = field(default_factory=lambda: os.getenv('LOG_FILE', 'baccarat_bot.log'))
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    max_bytes: int = 10 * 1024 * 1024  # 10 MB
    backup_count: int = 5
    
    def validate(self) -> bool:
        """Valida que la configuración de logging sea correcta"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.level.upper() not in valid_levels:
            raise ValueError(f"LOG_LEVEL debe ser uno de: {', '.join(valid_levels)}")
        return True


@dataclass
class ScraperConfig:
    """Configuración del web scraper"""
    base_url: str = "https://col.1xbet.com/es/casino/game/97408/"
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: int = 5
    headless: bool = True
    max_pages: int = 10
    page_idle_timeout_minutes: int = 5
    
    def validate(self) -> bool:
        """Valida que la configuración del scraper sea correcta"""
        if self.timeout_seconds < 10:
            raise ValueError("timeout_seconds debe ser al menos 10")
        if self.max_retries < 1:
            raise ValueError("max_retries debe ser al menos 1")
        if self.max_pages < 1:
            raise ValueError("max_pages debe ser al menos 1")
        return True


@dataclass
class StrategyConfig:
    """Configuración de estrategias de apuesta"""
    enabled_strategies: List[str] = field(default_factory=lambda: [
        'streak',
        'zigzag',
        'martingale',
        'fibonacci',
        'trend_analysis',
        'tie_detection'
    ])
    min_confidence: int = 50  # Confianza mínima para generar señal
    consensus_threshold: int = 2  # Número mínimo de estrategias que deben coincidir
    
    def validate(self) -> bool:
        """Valida que la configuración de estrategias sea correcta"""
        if self.min_confidence < 0 or self.min_confidence > 100:
            raise ValueError("min_confidence debe estar entre 0 y 100")
        if self.consensus_threshold < 1:
            raise ValueError("consensus_threshold debe ser al menos 1")
        return True


@dataclass
class BotConfig:
    """Configuración completa del bot"""
    telegram: TelegramConfig = field(default_factory=TelegramConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    timing: TimingConfig = field(default_factory=TimingConfig)
    api: APIConfig = field(default_factory=APIConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    scraper: ScraperConfig = field(default_factory=ScraperConfig)
    strategy: StrategyConfig = field(default_factory=StrategyConfig)
    
    def validate_all(self) -> bool:
        """Valida todas las configuraciones"""
        try:
            self.telegram.validate()
            self.monitoring.validate()
            self.timing.validate()
            self.api.validate()
            self.database.validate()
            self.logging.validate()
            self.scraper.validate()
            self.strategy.validate()
            logger.info("✅ Todas las configuraciones validadas correctamente")
            return True
        except ValueError as e:
            logger.error(f"❌ Error de validación de configuración: {e}")
            raise
    
    def to_dict(self) -> Dict:
        """Convierte la configuración a diccionario"""
        return {
            'telegram': self.telegram.__dict__,
            'monitoring': self.monitoring.__dict__,
            'timing': self.timing.__dict__,
            'api': self.api.__dict__,
            'database': self.database.__dict__,
            'logging': self.logging.__dict__,
            'scraper': self.scraper.__dict__,
            'strategy': self.strategy.__dict__
        }


# Instancia global de configuración
config = BotConfig()

# Validar configuración al importar
try:
    config.validate_all()
except ValueError as e:
    logger.critical(f"Error crítico en configuración: {e}")
    raise


# Exportar configuraciones individuales para compatibilidad con código existente
TELEGRAM_TOKEN = config.telegram.token
TELEGRAM_CHAT_ID = config.telegram.chat_id
INTERVALO_MONITOREO = config.monitoring.intervalo_monitoreo
LONGITUD_RACHA = config.monitoring.longitud_racha
MINIMO_TIEMPO_ENTRE_SENALES = config.monitoring.minimo_tiempo_entre_senales
USAR_DATOS_REALES = config.monitoring.usar_datos_reales
BASE_URL = config.scraper.base_url
LOG_LEVEL = config.logging.level
LOG_FILE = config.logging.file
API_CONFIG = config.api.__dict__
TIMING_CONFIG = config.timing.__dict__
