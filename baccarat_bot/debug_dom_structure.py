#!/usr/bin/env python3
"""
Script de debug para inspeccionar la estructura del DOM del juego
Ayuda a identificar los selectores CSS correctos para extraer resultados
"""

import asyncio
import logging
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_game_structure():
    """Inspecciona la estructura del juego y exporta el HTML"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Visible para ver qué está pasando
        page = await browser.new_page()
        
        # Navegar al juego
        url = "https://col.1xbet.com/es/casino/game/97408/speed-baccarat-b"
        logger.info(f"🌐 Navegando a {url}...")
        await page.goto(url, wait_until='domcontentloaded', timeout=60000)
        
        # Esperar a que cargue
        await asyncio.sleep(8)
        
        logger.info("📄 Inspeccionando frames...")
        frames = page.frames
        logger.info(f"📺 Encontrados {len(frames)} frames")
        
        for i, frame in enumerate(frames):
            frame_name = frame.name or f"frame-{i}"
            logger.info(f"\n{'='*60}")
            logger.info(f"Frame #{i}: {frame_name}")
            logger.info(f"{'='*60}")
            
            try:
                # Obtener el HTML del frame
                html = await frame.content()
                
                # Guardar en archivo
                filename = f"frame_{i}_{frame_name}_debug.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html)
                logger.info(f"✅ HTML guardado en: {filename}")
                
                # Buscar palabras clave
                keywords = ['banker', 'player', 'tie', 'baccarat', 'result', 'history', 'roadmap', 'bead', 'game']
                for keyword in keywords:
                    count = html.lower().count(keyword)
                    if count > 0:
                        logger.info(f"🔍 Encontradas {count} menciones de '{keyword}'")
                
                # Listar todos los elementos con clases
                logger.info(f"\n📋 Buscando elementos con atributos clave...")
                
                # Buscar elementos con data attributes
                data_elements = await frame.query_selector_all('[data-*]')
                if data_elements:
                    logger.info(f"   - {len(data_elements)} elementos con data-* attributes")
                
                # Buscar elementos con clases que contengan palabras clave
                for keyword in ['result', 'history', 'roadmap', 'bead', 'game', 'table']:
                    elements = await frame.query_selector_all(f'[class*="{keyword}"]')
                    if elements:
                        logger.info(f"   - {len(elements)} elementos con clase contiene '{keyword}'")
                        # Mostrar primeros 3
                        for j, elem in enumerate(elements[:3]):
                            classes = await elem.get_attribute('class')
                            text = await elem.text_content()
                            text_preview = (text[:50] + '...') if text and len(text) > 50 else text
                            logger.info(f"       [{j+1}] class='{classes}' text='{text_preview}'")
                
            except Exception as e:
                logger.error(f"❌ Error inspeccionando frame {frame_name}: {e}")
        
        logger.info("\n✅ Debug completado. Revisa los archivos HTML generados.")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_game_structure())
