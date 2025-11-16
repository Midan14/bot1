# baccarat_bot/tables.py

# Configuración de la única mesa a monitorear: XXXTreme Lightning Baccarat
# URL: https://col.1xbet.com/es/casino/game/97446/xxxtreme-lightning-baccarat

BASE_URL = "https://col.1xbet.com/es/casino/game/97446/xxxtreme-lightning-baccarat"
GAME_ID = "97446"
GAME_SLUG = "xxxtreme-lightning-baccarat"

# Solo una mesa
MESA_NOMBRES = [
    "XXXTreme Lightning Baccarat"
]

def generar_slug(nombre_mesa):
    """Genera un slug simple para la URL a partir del nombre de la mesa."""
    slug = nombre_mesa.lower().replace(" ", "-").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
    return slug

def inicializar_mesas():
    """Inicializa la estructura de datos para la mesa única."""
    mesas = {}
    for nombre in MESA_NOMBRES:
        mesas[nombre] = {
            "nombre": nombre,
            "url": BASE_URL,
            "game_id": GAME_ID,  # ID del juego para scraping real
            "game_slug": GAME_SLUG,  # Slug del juego para la URL
            "historial_resultados": [],
            "ultima_senal_enviada": None,
            "ultima_senal_tiempo": None
        }
    return mesas

if __name__ == '__main__':
    # Ejemplo de inicialización y estructura
    mesas_iniciales = inicializar_mesas()
    print(f"Total de mesas inicializadas: {len(mesas_iniciales)}")
    print("\nEstructura de la mesa:")
    print(mesas_iniciales["XXXTreme Lightning Baccarat"])
