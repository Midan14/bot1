# baccarat_bot/config_enhanced.py

"""
Configuración centralizada y mejorada del bot
Reemplaza config.py con configuraciones estructuradas
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any

# Cargar variables de entorno
load_dotenv()

# ============================================================================
# CONFIGURACIÓN DE BOT TELEGRAM
# ============================================================================

TELEGRAM_CONFIG = {
    'token': os.getenv('TELEGRAM_BOT_TOKEN'),
    'chat_id': os.getenv('TELEGRAM_CHAT_ID'),
    'parse_mode': 'Markdown',
    'timeout': 60
}

# Validación de credenciales
if not TELEGRAM_CONFIG['token']:
    raise ValueError("TELEGRAM_BOT_TOKEN no configurado en variables de entorno")

if not TELEGRAM_CONFIG['chat_id']:
    raise ValueError("TELEGRAM_CHAT_ID no configurado en variables de entorno")

# ============================================================================
# CONFIGURACIÓN DE TIMING Y CONTROL
# ============================================================================

TIMING_CONFIG = {
    'monitoreo': {
        'intervalo_segundos': int(os.getenv('INTERVALO_MONITOREO', '120')),
        'longitud_racha': int(os.getenv('LONGITUD_RACHA', '3')),
    },
    'signal_cooldown': {
        'default': int(os.getenv('SEÑAL_COOLDOWN_DEFAULT', '300')),  # 5 minutos
        'emergency': int(os.getenv('SEÑAL_COOLDOWN_EMERGENCY', '180')),  # 3 minutos
        'max_frequency': int(os.getenv('SEÑAL_FRECUENCIA_MAXIMA', '30')),  # 30 segundos mínimo
    },
    'frecuencia_limites': {
        'max_por_hora': int(os.getenv('MAX_SENALES_POR_HORA', '12')),
        'max_por_dia': int(os.getenv('MAX_SENALES_POR_DIA', '200')),
        'ventana_minutos': 60,
    },
    'timing_detection': {
        'min_samples_for_confidence': int(
            os.getenv('MIN_SAMPLES_CONFIANZA', '5')
        ),
        'max_timing_variance': float(os.getenv('MAX_VARIANZA_TIMING', '5.0')),
        'safety_margin_multiplier': float(
            os.getenv('MARGEN_SEGURIDAD_MULTIPLICADOR', '1.2')
        ),
        'signal_advance_time': float(os.getenv('TIEMPO_ADELANTO_SENAL', '8.0')),
    }
}

# ============================================================================
# CONFIGURACIÓN DE SCRAPING
# ============================================================================

SCRAPING_CONFIG = {
    'modo': 'simulation',  # 'real' o 'simulation'
    'usar_datos_reales': os.getenv('USAR_DATOS_REALES', 'false').lower() == 'true',
    'playwright': {
        'headless': True,
        'timeout': 30000,  # 30 segundos
        'user_agents_rotation': True,
        'viewport_sizes': [
            {'width': 1920, 'height': 1080},
            {'width': 1366, 'height': 768},
            {'width': 1536, 'height': 864},
        ],
        'cache_duration': 30,  # segundos
    },
    'urls': {
        'base': [
            "https://col.1xbet.com",
            "https://1xbet.com",
            "https://www.1xbet.com",
            "https://co.1xbet.com",
            "https://1xbet.co",
        ],
        'patterns': [
            "/es/casino/game/{game_id}/{game_name}",
            "/es/casino/game/{game_id}",
            "/casino/game/{game_id}/{game_name}",
            "/casino/game/{game_id}",
            "/es/livecasino/game/{game_id}/{game_name}",
            "/es/livecasino/game/{game_id}",
            "/livecasino/{game_id}",
            "/es/allgamesentrance/game/{game_id}",
        ]
    },
    'anti_detection': {
        'stealth_mode': True,
        'random_delays': True,
        'proxy_rotation': False,  # Para implementación futura
        'cookies_persistence': True,
    }
}

# ============================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# ============================================================================

DATABASE_CONFIG = {
    'path': os.getenv('DB_PATH', 'baccarat_data.db'),
    'backup_enabled': os.getenv('DB_BACKUP_ENABLED', 'true').lower() == 'true',
    'backup_interval_hours': int(os.getenv('DB_BACKUP_INTERVAL', '24')),
    'cleanup_days': int(os.getenv('DB_CLEANUP_DAYS', '30')),
    'vacuum_frequency': int(os.getenv('DB_VACUUM_FREQUENCY', '168')),  # Semanal
}

# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================

LOGGING_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO').upper(),
    'file': os.getenv('LOG_FILE', 'baccarat_bot.log'),
    'max_size_mb': int(os.getenv('LOG_MAX_SIZE_MB', '100')),
    'backup_count': int(os.getenv('LOG_BACKUP_COUNT', '5')),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'structured': os.getenv('LOG_STRUCTURED', 'false').lower() == 'true',
}

# ============================================================================
# CONFIGURACIÓN DE ESTRATEGIAS
# ============================================================================

STRATEGY_CONFIG = {
    'racha': {
        'longitud_default': int(os.getenv('RACHA_LONGITUD_DEFAULT', '3')),
        'min_confianza': int(os.getenv('RACHA_MIN_CONFIANZA', '70')),
        'max_longitud': int(os.getenv('RACHA_MAX_LONGITUD', '8')),
    },
    'zigzag': {
        'patron_longitud': int(os.getenv('ZIGZAG_PATRON_LONGITUD', '4')),
        'min_confianza': int(os.getenv('ZIGZAG_MIN_CONFIANZA', '75')),
    },
    'empates': {
        'ventana_observacion': int(os.getenv('EMPATES_VENTANA_OBSERVACION', '5')),
        'min_empates': int(os.getenv('EMPATES_MIN_EMPATES', '1')),
        'max_confianza': int(os.getenv('EMPATES_MAX_CONFIANZA', '65')),
    },
    'tendencias': {
        'ventana_corto_plazo': int(os.getenv('TENDENCIAS_VENTANA_CORTO', '5')),
        'ventana_largo_plazo': int(os.getenv('TENDENCIAS_VENTANA_LARGO', '15')),
        'min_confianza': int(os.getenv('TENDENCIAS_MIN_CONFIANZA', '50')),
    }
}

# ============================================================================
# CONFIGURACIÓN DE API
# ============================================================================

API_CONFIG = {
    'host': os.getenv('API_HOST', '0.0.0.0'),
    'port': int(os.getenv('API_PORT', '8000')),
    'debug': os.getenv('API_DEBUG', 'false').lower() == 'true',
    'cors_enabled': os.getenv('API_CORS', 'true').lower() == 'true',
    'rate_limit': {
        'requests_per_minute': int(os.getenv('API_RATE_LIMIT_MIN', '60')),
        'burst_size': int(os.getenv('API_RATE_LIMIT_BURST', '10')),
    },
    'endpoints': {
        'health_check': True,
        'metrics': True,
        'config': True,
        'strategies': True,
    }
}

# ============================================================================
# CONFIGURACIÓN DE NOTIFICACIONES
# ============================================================================

NOTIFICATION_CONFIG = {
    'email': {
        'enabled': os.getenv('EMAIL_ENABLED', 'false').lower() == 'true',
        'smtp_server': os.getenv('EMAIL_SMTP_SERVER'),
        'smtp_port': int(os.getenv('EMAIL_SMTP_PORT', '587')),
        'username': os.getenv('EMAIL_USERNAME'),
        'password': os.getenv('EMAIL_PASSWORD'),
        'from_address': os.getenv('EMAIL_FROM'),
        'to_addresses': os.getenv('EMAIL_TO', '').split(','),
    },
    'slack': {
        'enabled': os.getenv('SLACK_ENABLED', 'false').lower() == 'true',
        'webhook_url': os.getenv('SLACK_WEBHOOK_URL'),
        'channel': os.getenv('SLACK_CHANNEL', '#baccarat'),
    },
    'discord': {
        'enabled': os.getenv('DISCORD_ENABLED', 'false').lower() == 'true',
        'webhook_url': os.getenv('DISCORD_WEBHOOK_URL'),
    }
}

# ============================================================================
# CONFIGURACIÓN DE MÉTRICAS Y MONITOREO
# ============================================================================

MONITORING_CONFIG = {
    'health_check_interval': int(os.getenv('HEALTH_CHECK_INTERVAL', '60')),  # 1 minuto
    'metrics_retention_days': int(os.getenv('METRICS_RETENTION_DAYS', '7')),
    'alert_thresholds': {
        'error_rate': float(os.getenv('ALERT_ERROR_RATE', '0.05')),  # 5%
        'signal_success_rate': float(os.getenv('ALERT_SIGNAL_SUCCESS', '0.5')),  # 50%
        'memory_usage_mb': int(os.getenv('ALERT_MEMORY_MB', '500')),
        'response_time_seconds': float(os.getenv('ALERT_RESPONSE_TIME', '5.0')),
    },
    'performance_tracking': {
        'enabled': True,
        'detailed_timing': os.getenv('DETAILED_TIMING', 'false').lower() == 'true',
        'database_queries': os.getenv('TRACK_DB_QUERIES', 'false').lower() == 'true',
    }
}

# ============================================================================
# CONFIGURACIÓN DE DESARROLLO Y DEBUG
# ============================================================================

DEV_CONFIG = {
    'debug_mode': os.getenv('DEBUG_MODE', 'false').lower() == 'true',
    'verbose_logging': os.getenv('VERBOSE_LOGGING', 'false').lower() == 'true',
    'mock_mode': os.getenv('MOCK_MODE', 'false').lower() == 'true',
    'test_data': {
        'enabled': os.getenv('TEST_DATA_ENABLED', 'false').lower() == 'true',
        'preserve_real': os.getenv('PRESERVE_REAL_DATA', 'true').lower() == 'true',
    }
}

# ============================================================================
# VALIDACIONES Y CONSTANTES
# ============================================================================

# URLs y configuraciones de mesa
BASE_URL = "https://col.1xbet.com/es/casino/game/97408/"
GAME_ID = "97408"
GAME_SLUG = "speed-baccarat-b"

# Probabilidades de Baccarat (deben sumar 100%)
BACCARAT_PROBABILIDADES = {
    'B': 45.8,  # Banca
    'P': 44.6,  # Jugador  
    'E': 9.6    # Empate
}

# Validar que las probabilidades sumen ~100%
total_prob = sum(BACCARAT_PROBABILIDADES.values())
if abs(total_prob - 100.0) > 0.1:
    raise ValueError(f"Las probabilidades de Baccarat no suman 100%: {total_prob}%")

# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def get_config(section: str) -> Dict[str, Any]:
    """Obtiene configuración de una sección específica"""
    configs = {
        'telegram': TELEGRAM_CONFIG,
        'timing': TIMING_CONFIG,
        'scraping': SCRAPING_CONFIG,
        'database': DATABASE_CONFIG,
        'logging': LOGGING_CONFIG,
        'strategy': STRATEGY_CONFIG,
        'api': API_CONFIG,
        'notification': NOTIFICATION_CONFIG,
        'monitoring': MONITORING_CONFIG,
        'dev': DEV_CONFIG,
    }
    
    if section not in configs:
        raise ValueError(f"Sección de configuración '{section}' no existe")
    
    return configs[section]

def update_config(section: str, key: str, value: Any) -> bool:
    """Actualiza una configuración específica en runtime"""
    try:
        config_section = get_config(section)
        
        # Navegar por claves anidadas si es necesario
        keys = key.split('.')
        target = config_section
        
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        
        target[keys[-1]] = value
        return True
        
    except Exception as e:
        import logging
        logging.error(f"Error actualizando configuración {section}.{key}: {e}")
        return False

def get_monitoring_config() -> Dict[str, Any]:
    """Obtiene configuración específica de monitoreo"""
    return MONITORING_CONFIG

def is_production_mode() -> bool:
    """Verifica si el bot está en modo producción"""
    return not DEV_CONFIG['debug_mode']

def should_use_real_data() -> bool:
    """Verifica si debe usar datos reales"""
    return SCRAPING_CONFIG['usar_datos_reales']

# ============================================================================
# EXPORTACIONES PRINCIPALES
# ============================================================================

# Para compatibilidad con código existente
TELEGRAM_TOKEN = TELEGRAM_CONFIG['token']
TELEGRAM_CHAT_ID = TELEGRAM_CONFIG['chat_id']
INTERVALO_MONITOREO = TIMING_CONFIG['monitoreo']['intervalo_segundos']
LONGITUD_RACHA = TIMING_CONFIG['monitoreo']['longitud_racha']

# Configuración legacy para compatibilidad
MINIMO_TIEMPO_ENTRE_SENALES = TIMING_CONFIG['signal_cooldown']['default']
LOG_LEVEL = LOGGING_CONFIG['level']
LOG_FILE = LOGGING_CONFIG['file']
USAR_DATOS_REALES = SCRAPING_CONFIG['usar_datos_reales']