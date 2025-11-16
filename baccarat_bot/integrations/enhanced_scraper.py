# baccarat_bot/integrations/enhanced_scraper.py

"""
Scraper mejorado con todas las integraciones:
- Anti-detección avanzada
- PagePool para gestión de memoria
- Sincronización en tiempo real
- Validación de datos
- Logging estructurado
- Manejo robusto de errores
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime

from playwright.async_api import async_playwright, Browser, BrowserContext, Page

# Importar nuestras mejoras
from baccarat_bot.integrations.anti_detection import anti_detection
from baccarat_bot.integrations.realtime_sync import realtime_sync, GameState
from baccarat_bot.utils.page_pool import PagePool
from baccarat_bot.utils.validators import validar_mesa_data, MesaData
from baccarat_bot.utils.logging_config import get_structured_logger
from baccarat_bot.utils.error_handler import retry_on_error, RetryConfig, ErrorContext

logger = get_structured_logger(__name__)


class EnhancedBaccaratScraper:
    """
    Scraper mejorado de Baccarat con todas las optimizaciones integradas.
    
    Características:
    - Sistema anti-detección avanzado
    - Gestión eficiente de memoria con PagePool
    - Sincronización en tiempo real con las mesas
    - Validación automática de datos
    - Logging estructurado
    - Manejo robusto de errores con reintentos
    """
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page_pool: Optional[PagePool] = None
        self.initialized = False
        
        # URLs de fallback
        self.base_urls = [
            "https://col.1xbet.com",
            "https://1xbet.com",
            "https://www.1xbet.com",
        ]
        self.current_url_index = 0
        
        # Caché de resultados
        self.last_results: Dict[str, Dict] = {}
        self.cache_duration = 10  # segundos
    
    @retry_on_error(RetryConfig(
        max_retries=3,
        initial_delay=2.0,
        exceptions=(Exception,)
    ))
    async def init(self, headless: bool = True):
        """
        Inicializa el scraper con todas las optimizaciones.
        
        Args:
            headless: Si debe ejecutarse en modo headless
        """
        if self.initialized:
            logger.info("Scraper ya inicializado")
            return
        
        try:
            logger.info("🚀 Iniciando scraper mejorado con anti-detección avanzada...")
            
            # Iniciar Playwright
            self.playwright = await async_playwright().start()
            
            # Lanzar navegador con configuración anti-detección
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-gpu',
                    '--disable-extensions',
                    '--disable-infobars',
                    '--disable-notifications',
                    '--disable-popup-blocking',
                ]
            )
            
            # Crear contexto con anti-detección
            self.context = await anti_detection.create_stealth_context(self.browser)
            
            # Inicializar PagePool
            self.page_pool = PagePool(
                browser=self.browser,
                max_pages=10,
                idle_timeout_minutes=5,
                cleanup_interval_seconds=60
            )
            await self.page_pool.start()
            
            self.initialized = True
            logger.info("✅ Scraper mejorado inicializado correctamente")
            
        except Exception as e:
            logger.error(f"❌ Error inicializando scraper: {e}", exc_info=True)
            await self.close()
            raise
    
    async def scrape_table(
        self,
        table_name: str,
        table_url: str,
        game_id: str
    ) -> Optional[Dict]:
        """
        Realiza scraping de una mesa con todas las optimizaciones.
        
        Args:
            table_name: Nombre de la mesa
            table_url: URL de la mesa
            game_id: ID del juego
            
        Returns:
            Diccionario con datos de la mesa o None si falla
        """
        if not self.initialized:
            logger.warning("Scraper no inicializado, inicializando...")
            await self.init()
        
        # Verificar caché
        cache_key = f"{table_name}_{game_id}"
        if cache_key in self.last_results:
            cached = self.last_results[cache_key]
            age = (datetime.now() - cached['timestamp']).total_seconds()
            if age < self.cache_duration:
                logger.debug(f"Usando resultado cacheado para {table_name} (edad: {age:.1f}s)")
                return cached['data']
        
        with ErrorContext(
            operation='scrape_table',
            context_data={'table': table_name, 'url': table_url},
            raise_on_error=False
        ):
            # Obtener página del pool
            page = await self.page_pool.get_page(table_name, table_url)
            
            # Aplicar scripts anti-detección
            await anti_detection.apply_stealth_scripts(page)
            
            # Esperar a que cargue la página
            await anti_detection.wait_for_page_load(page)
            
            # Manejar Cloudflare si aparece
            await anti_detection.handle_cloudflare(page)
            
            # Simular comportamiento humano
            await anti_detection.simulate_human_behavior(page)
            
            # Sincronizar con el estado de la mesa
            game_round = await realtime_sync.sync_table(page, table_name)
            
            if not game_round:
                logger.warning(f"No se pudo sincronizar la mesa {table_name}")
                return None
            
            # Extraer datos adicionales
            result_data = {
                'table_name': table_name,
                'game_id': game_id,
                'url': table_url,
                'state': game_round.state.value,
                'time_remaining': game_round.time_remaining,
                'last_result': game_round.last_result,
                'history': game_round.history,
                'round_number': game_round.round_number,
                'timestamp': datetime.now(),
                'is_betting_open': game_round.is_betting_open(),
                'should_send_signal': game_round.should_send_signal()
            }
            
            # Validar datos antes de retornar
            try:
                mesa_data = {
                    'nombre': table_name,
                    'url': table_url,
                    'game_id': game_id,
                    'historial_resultados': game_round.history
                }
                validar_mesa_data(mesa_data)
            except Exception as e:
                logger.error(f"Datos inválidos para {table_name}: {e}")
                return None
            
            # Guardar en caché
            self.last_results[cache_key] = {
                'data': result_data,
                'timestamp': datetime.now()
            }
            
            logger.log_performance(
                operation=f'scrape_table_{table_name}',
                duration_seconds=0.5,  # Placeholder
                success=True,
                state=game_round.state.value,
                history_length=len(game_round.history)
            )
            
            return result_data
    
    async def wait_for_betting_window(
        self,
        table_name: str,
        table_url: str,
        max_wait_seconds: int = 60
    ) -> bool:
        """
        Espera hasta que se abra la ventana de apuestas.
        
        Args:
            table_name: Nombre de la mesa
            table_url: URL de la mesa
            max_wait_seconds: Tiempo máximo de espera
            
        Returns:
            True si se abrió la ventana, False si timeout
        """
        if not self.initialized:
            await self.init()
        
        page = await self.page_pool.get_page(table_name, table_url)
        
        return await realtime_sync.wait_for_optimal_timing(
            page,
            table_name,
            max_wait_seconds
        )
    
    async def get_current_game_state(self, table_name: str) -> Optional[GameState]:
        """
        Obtiene el estado actual del juego de una mesa.
        
        Args:
            table_name: Nombre de la mesa
            
        Returns:
            GameState actual o None
        """
        game_round = realtime_sync.get_current_round(table_name)
        if game_round:
            return game_round.state
        return None
    
    async def scrape_multiple_tables(
        self,
        tables: List[Dict[str, str]]
    ) -> Dict[str, Optional[Dict]]:
        """
        Realiza scraping de múltiples mesas en paralelo.
        
        Args:
            tables: Lista de diccionarios con 'name', 'url', 'game_id'
            
        Returns:
            Diccionario con resultados por mesa
        """
        if not self.initialized:
            await self.init()
        
        tasks = []
        for table in tables:
            task = self.scrape_table(
                table['name'],
                table['url'],
                table['game_id']
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Mapear resultados
        table_results = {}
        for table, result in zip(tables, results):
            if isinstance(result, Exception):
                logger.error(f"Error en mesa {table['name']}: {result}")
                table_results[table['name']] = None
            else:
                table_results[table['name']] = result
        
        return table_results
    
    async def rotate_identity(self):
        """Rota la identidad del navegador para evitar detección"""
        logger.info("Rotando identidad del navegador...")
        
        # Rotar identidad en anti_detection
        await anti_detection.rotate_identity()
        
        # Recrear contexto
        if self.context:
            await self.context.close()
        
        self.context = await anti_detection.create_stealth_context(self.browser)
        
        logger.info("✅ Identidad rotada correctamente")
    
    async def close(self):
        """Cierra el scraper y libera recursos"""
        logger.info("Cerrando scraper mejorado...")
        
        try:
            # Detener PagePool
            if self.page_pool:
                await self.page_pool.stop()
            
            # Cerrar contexto
            if self.context:
                await self.context.close()
            
            # Cerrar navegador
            if self.browser:
                await self.browser.close()
            
            # Detener Playwright
            if self.playwright:
                await self.playwright.stop()
            
            self.initialized = False
            logger.info("✅ Scraper cerrado correctamente")
            
        except Exception as e:
            logger.error(f"Error cerrando scraper: {e}")
    
    def get_pool_stats(self) -> Dict:
        """Obtiene estadísticas del PagePool"""
        if self.page_pool:
            return self.page_pool.get_stats()
        return {}


# Instancia global del scraper mejorado
enhanced_scraper = EnhancedBaccaratScraper()
