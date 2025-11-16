# baccarat_bot/config.py

import os
from dotenv import load_dotenv
from baccarat_bot.tables import MESA_NOMBRES, inicializar_mesas  # noqa: F401

# Cargar variables de entorno desde archivo .env
load_dotenv()

# Configuración del Bot
# **IMPORTANTE:** Cargar las credenciales desde variables de entorno
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Configuración de Monitoreo
# Aumentado a 120 segundos (2 minutos) para reducir frecuencia de señales
INTERVALO_MONITOREO = int(os.getenv('INTERVALO_MONITOREO', '120'))
LONGITUD_RACHA = int(os.getenv('LONGITUD_RACHA', '3'))

# Validación de credenciales
if not TELEGRAM_TOKEN:
    raise ValueError(
        "TELEGRAM_BOT_TOKEN no está configurado en las variables de entorno"
    )
    
if not TELEGRAM_CHAT_ID:
    raise ValueError(
        "TELEGRAM_CHAT_ID no está configurado en las variables de entorno"
    )

# Configuración de URLs
BASE_URL = "https://col.1xbet.com/es/casino/game/97408/"

# Configuración de Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'baccarat_bot.log')

# Configuración de Simulación
USAR_DATOS_REALES = os.getenv('USAR_DATOS_REALES', 'false').lower() == 'true'

# Configuración de Anti-Spam
# 10 minutos entre señales de la misma mesa para mayor control
MINIMO_TIEMPO_ENTRE_SENALES = int(
    os.getenv('MINIMO_TIEMPO_ENTRE_SENALES', '600')
)
