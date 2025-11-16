import aiohttp
from typing import Dict, Optional
import os
import logging
import random
import asyncio

logger = logging.getLogger(__name__)

RESULTADOS_PROBABILIDADES = {
    'B': 46,
    'P': 45,
    'E': 9
}
RESULTADOS_SIMULACION = [
    resultado for resultado, prob in RESULTADOS_PROBABILIDADES.items() for _ in range(prob)
]

_playwright_scraper = None
_scraper_initialized = False

def _usar_datos_reales() -> bool:
    usar_reales = os.getenv('USAR_DATOS_REALES', 'false').lower()
    return usar_reales in ['true', '1', 'yes', 'si', 'sí']

async def _init_playwright_scraper():
    global _playwright_scraper, _scraper_initialized
    if not _usar_datos_reales():
        logger.info("📊 Modo SIMULACIÓN activado (USAR_DATOS_REALES=false)")
        return None
    if _scraper_initialized and _playwright_scraper:
        return _playwright_scraper
    try:
        logger.info("🚀 Inicializando scraper de Playwright para datos REALES...")
        from baccarat_bot.integrations.playwright_scraper import Playwright1xBetScraper
        _playwright_scraper = Playwright1xBetScraper()
        await _playwright_scraper.init(headless=False)
        _scraper_initialized = True
        logger.info("✅ Scraper de Playwright inicializado correctamente")
        return _playwright_scraper
    except ImportError as e:
        logger.error(f"❌ Error: Playwright no está instalado. Ejecuta: pip install playwright && playwright install chromium")
        logger.error(f"Detalles: {e}")
        logger.warning("⚠️ Cambiando a modo SIMULACIÓN...")
        return None
    except Exception as e:
        logger.error(f"❌ Error inicializando Playwright: {e}")
        logger.warning("⚠️ Cambiando a modo SIMULACIÓN...")
        return None

async def obtener_nuevo_resultado_async(mesa_data: Dict, game_id: Optional[str] = None) -> str:
    global _playwright_scraper
    if _usar_datos_reales():
        try:
            if not _scraper_initialized:
                scraper = await _init_playwright_scraper()
                if not scraper:
                    raise Exception("No se pudo inicializar Playwright")
            if _playwright_scraper and game_id:
                table_name = mesa_data.get('nombre', 'Unknown')
                game_slug = mesa_data.get('game_slug', '')
                logger.info(f"🌐 Obteniendo datos REALES para {table_name} (ID: {game_id})")
                resultado = await _playwright_scraper.get_table_result(table_name, game_id, game_slug)
                if resultado:
                    logger.info(f"✅ Resultado REAL obtenido para {table_name}: {resultado}")
                    return resultado
                else:
                    logger.warning(f"⚠️ No se pudo obtener resultado real para {table_name}, intentando con Puppeteer")
                    # Intentar con Puppeteer
                    html = await obtener_resultado_puppeteer_async(mesa_data, game_id)
                    if html:
                        # Parser mejorado: buscar resultados en selectores comunes de Baccarat
                        from bs4 import BeautifulSoup
                        soup = BeautifulSoup(html, "html.parser")
                        # Buscar por clases típicas de resultado
                        # Buscar por color de punto (rojo = Banca, azul = Jugador)
                        punto = None
                        for el in soup.find_all(True):
                            clases_attr = el.get("class")
                            if isinstance(clases_attr, list):
                                clases = " ".join(clases_attr).lower()
                            elif isinstance(clases_attr, str):
                                clases = clases_attr.lower()
                            else:
                                clases = ""
                            style = el.get("style", "")
                            style = style.lower() if isinstance(style, str) else ""
                            if "red" in clases or "banca" in clases or "background-color:red" in style:
                                punto = "B"
                            elif "blue" in clases or "jugador" in clases or "background-color:blue" in style:
                                punto = "P"
                        if punto:
                            logger.info(f"✅ Resultado por color detectado con Puppeteer para {table_name}: {punto}")
                            return punto
                        logger.warning(f"⚠️ Puppeteer no encontró resultado por color, usando simulación")
                        return _obtener_resultado_simulado()
                    else:
                        logger.warning(f"⚠️ Puppeteer no devolvió HTML, usando simulación")
                        return _obtener_resultado_simulado()
            else:
                logger.warning(f"⚠️ Scraper no disponible o game_id no proporcionado, intentando con Puppeteer")
                html = await obtener_resultado_puppeteer_async(mesa_data, game_id)
                if html:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html, "html.parser")
                    # Buscar por color de punto (rojo = Banca, azul = Jugador)
                    punto = None
                    for el in soup.find_all(True):
                        clases_attr = el.get("class")
                        if isinstance(clases_attr, list):
                            clases = " ".join(clases_attr).lower()
                        elif isinstance(clases_attr, str):
                            clases = clases_attr.lower()
                        else:
                            clases = ""
                        style = el.get("style", "")
                        style = style.lower() if isinstance(style, str) else ""
                        if "red" in clases or "banca" in clases or "background-color:red" in style:
                            punto = "B"
                        elif "blue" in clases or "jugador" in clases or "background-color:blue" in style:
                            punto = "P"
                    if punto:
                        logger.info(f"✅ Resultado por color detectado con Puppeteer: {punto}")
                        return punto
                    logger.warning(f"⚠️ Puppeteer no encontró resultado por color, usando simulación")
                    return _obtener_resultado_simulado()
                else:
                    logger.warning(f"⚠️ Puppeteer no devolvió HTML, usando simulación")
                    return _obtener_resultado_simulado()
        except Exception as e:
            logger.error(f"❌ Error obteniendo datos reales: {e}")
            logger.info("📊 Usando simulación como fallback...")
            return _obtener_resultado_simulado()
    return _obtener_resultado_simulado()

def _obtener_resultado_simulado() -> str:
    return random.choice(RESULTADOS_SIMULACION)

async def obtener_resultado_puppeteer_async(mesa_data: Dict, game_id: Optional[str] = None) -> str:
    url = mesa_data.get("url")
    if not url:
        logger.warning("No se encontró URL en mesa_data para Puppeteer.")
        return ""
    puppeteer_endpoint = os.getenv("PUPPETEER_ENDPOINT", "http://localhost:3001/scrape")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(puppeteer_endpoint, json={"url": url}) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    html = data.get("html", "")
                    logger.info(f"✅ HTML obtenido de Puppeteer para {mesa_data.get('nombre', '')}")
                    return html
                else:
                    logger.warning(f"❌ Error {resp.status} al consultar Puppeteer: {await resp.text()}")
                    return ""
    except Exception as e:
        logger.error(f"❌ Error consultando Puppeteer: {e}")
        return ""
