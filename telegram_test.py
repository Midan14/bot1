import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path="baccarat_bot/.env")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MENSAJE = "Prueba de conexión desde telegram_test.py"

if not TOKEN or not CHAT_ID:
    raise ValueError("Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID en el entorno")

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
data = {"chat_id": CHAT_ID, "text": MENSAJE}

try:
    response = requests.post(url, data=data, timeout=60)
    print("Status:", response.status_code)
    print("Respuesta:", response.text)
except Exception as e:
    print("Error al enviar mensaje:", e)