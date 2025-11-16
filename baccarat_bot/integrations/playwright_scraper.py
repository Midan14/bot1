# baccarat_bot/integrations/playwright_scraper.py

import asyncio
import logging
import random
from typing import Dict, List, Optional, Any
from datetime import datetime
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeout

logger = logging.getLogger(__name__)

class Playwright1xBetScraper:
    """Scraper agresivo con Playwright para obtener datos reales de 1xBet con evasión anti-bot"""
    
    def __init__(self):
        # Probar diferentes URLs base de 1xBet
        self.base_urls = [
            "https://col.1xbet.com",
            "https://1xbet.com",
            "https://www.1xbet.com",
            "https://co.1xbet.com",
            "https://1xbet.co",
        ]
        self.base_url = self.base_urls[0]  # Empezar con col.1xbet.com
        self.current_url_index = 0
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.pages: Dict[str, Page] = {}
        
        # User agents para rotación
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        ]
        
        self.viewport_sizes = [
            {'width': 1920, 'height': 1080},
            {'width': 1366, 'height': 768},
            {'width': 1536, 'height': 864},
            {'width': 1440, 'height': 900},
        ]
        
        self.initialized = False
        self.last_results = {}
        self.cache_duration = 30  # segundos
    
    async def init(self, headless: bool = True):
        """Inicializa Playwright con configuración anti-detección reforzada"""
        try:
            logger.info("🚀 Iniciando Playwright con modo anti-bot reforzado...")
            self.playwright = await async_playwright().start()

            # Elegir user-agent y viewport consistentes para contexto y navegador
            user_agent = random.choice(self.user_agents)
            viewport = random.choice(self.viewport_sizes)

            # Configuración anti-detección
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-gpu',
                    '--disable-software-rasterizer',
                    '--disable-extensions',
                    f'--user-agent={user_agent}',
                    '--window-size=' + f"{viewport['width']},{viewport['height']}"
                ]
            )

            self.context = await self.browser.new_context(
                viewport=viewport,
                user_agent=user_agent,
                locale='es-ES',
                timezone_id='America/Bogota',
                permissions=['geolocation'],
                geolocation={'latitude': 4.7110, 'longitude': -74.0721},  # Bogotá
                color_scheme='dark',
                device_scale_factor=1,
                has_touch=False,
                is_mobile=False,
                java_script_enabled=True,
            )

            # Refuerzo de técnicas anti-bot: más propiedades y evasión de headless
            await self.context.add_init_script("""
                // Evasión de webdriver
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                // Plugins
                Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
                // Languages
                Object.defineProperty(navigator, 'languages', {get: () => ['es-ES', 'es', 'en-US', 'en']});
                // Chrome runtime
                window.chrome = { runtime: {} };
                // Permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                // Evasión de headless: userAgent y propiedades
                Object.defineProperty(navigator, 'userAgent', {get: () => window.navigator.userAgent.replace('HeadlessChrome', 'Chrome')});
                Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
                Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
                Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
                // Evasión de screen
                Object.defineProperty(window, 'outerWidth', {get: () => window.innerWidth});
                Object.defineProperty(window, 'outerHeight', {get: () => window.innerHeight});
                // Evasión de touch
                Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 0});
                // Evasión de WebGL
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    // Vendor spoof
                    if (parameter === 37445) return 'Intel Inc.';
                    if (parameter === 37446) return 'Intel Iris OpenGL Engine';
                    return getParameter(parameter);
                };
            """)

            # Simulación básica de interacción humana al abrir cada página
            original_new_page = self.context.new_page
            async def new_page_with_human_sim():
                page = await original_new_page()
                # Simular movimiento de mouse y scroll inicial
                await page.mouse.move(random.randint(100, 500), random.randint(100, 500))
                await page.mouse.move(random.randint(500, 900), random.randint(100, 700))
                await page.evaluate("window.scrollBy(0, Math.floor(Math.random()*200))")
                return page
            self.context.new_page = new_page_with_human_sim

            self.initialized = True
            logger.info("✅ Playwright inicializado correctamente con evasión anti-bot reforzada")
        except Exception as e:
            logger.error(f"❌ Error inicializando Playwright: {e}")
            raise
    
    async def close(self):
        """Cierra todas las páginas y el navegador"""
        try:
            if self.pages:
                for page in self.pages.values():
                    await page.close()
                self.pages = {}
            
            if self.context:
                await self.context.close()
            
            if self.browser:
                await self.browser.close()
            
            if self.playwright:
                await self.playwright.stop()
            
            self.initialized = False
            logger.info("🔒 Playwright cerrado correctamente")
            
        except Exception as e:
            logger.error(f"Error cerrando Playwright: {e}")
    
    async def get_or_create_page(self, table_id: str) -> Page:
        """Obtiene o crea una página para una mesa específica"""
        if table_id not in self.pages:
            page = await self.context.new_page()
            
            # Configurar timeouts
            page.set_default_timeout(30000)  # 30 segundos
            
            self.pages[table_id] = page
            logger.info(f"📄 Nueva página creada para mesa {table_id}")
        
        return self.pages[table_id]
    
    async def navigate_to_game(self, page: Page, game_id: str, retries: int = 3, game_name: str = "") -> bool:
        """Navega a un juego específico con reintentos y diferentes URLs"""
        
        # Probar diferentes formatos de URL
        url_patterns = [
            f"{self.base_url}/es/casino/game/{game_id}/{game_name}",
            f"{self.base_url}/es/casino/game/{game_id}",
            f"{self.base_url}/casino/game/{game_id}/{game_name}",
            f"{self.base_url}/casino/game/{game_id}",
            f"{self.base_url}/es/livecasino/game/{game_id}/{game_name}",
            f"{self.base_url}/es/livecasino/game/{game_id}",
            f"{self.base_url}/livecasino/{game_id}",
            f"{self.base_url}/es/allgamesentrance/game/{game_id}",
        ]
        
        for url_pattern in url_patterns:
            for attempt in range(retries):
                try:
                    logger.info(f"🌐 Probando URL: {url_pattern} (intento {attempt + 1}/{retries})")
                    
                    # Navegar con wait until
                    response = await page.goto(url_pattern, wait_until='domcontentloaded', timeout=30000)
                    
                    if response and response.status == 200:
                        # Esperar un poco para que cargue el contenido dinámico
                        await asyncio.sleep(random.uniform(2, 4))
                        logger.info(f"✅ Navegación exitosa a mesa {game_id} con URL: {url_pattern}")
                        self.base_url = url_pattern.split('/es/')[0] if '/es/' in url_pattern else url_pattern.split('/casino/')[0]
                        return True
                    elif response and response.status == 404:
                        logger.debug(f"⚠️ HTTP 404 con {url_pattern}, probando siguiente patrón...")
                        break  # Salir del bucle de reintentos y probar siguiente patrón
                    else:
                        logger.warning(f"⚠️ Respuesta HTTP {response.status if response else 'None'}")
                    
                except PlaywrightTimeout:
                    logger.warning(f"⏱️ Timeout navegando a {url_pattern}")
                    
                except Exception as e:
                    logger.error(f"❌ Error navegando a {url_pattern}: {e}")
                
                if attempt < retries - 1:
                    wait_time = random.uniform(2, 4)
                    logger.debug(f"⏳ Esperando {wait_time:.1f}s antes de reintentar...")
                    await asyncio.sleep(wait_time)
        
        logger.error(f"❌ No se pudo encontrar una URL válida para el juego {game_id}")
        return False
    
    async def extract_baccarat_results(self, page: Page, game_id: str) -> Optional[List[str]]:
        """Extrae los resultados de Baccarat de la página"""
        try:
            # PASO 1: Esperar a que cargue la página
            await asyncio.sleep(5)  # Dar tiempo para que cargue el iframe
            
            # PASO 2: Buscar iframes en la página
            logger.info(f"🔍 Buscando iframes en la página para mesa {game_id}...")
            frames = page.frames
            logger.info(f"📺 Encontrados {len(frames)} frames en total")
            
            # PASO 3: Intentar extraer desde cada frame
            results = None
            
            # Primero intentar en el frame principal
            results = await self.try_extract_from_frame(page.main_frame, game_id, "main frame")
            
            if results:
                return results
            
            # Si no funciona, intentar en cada iframe
            for i, frame in enumerate(frames):
                if frame == page.main_frame:
                    continue
                
                frame_name = frame.name or f"iframe-{i}"
                logger.info(f"🔍 Intentando extracción desde frame: {frame_name}")
                
                results = await self.try_extract_from_frame(frame, game_id, frame_name)
                
                if results:
                    return results
            
            # PASO 4: Si nada funcionó, intentar con evaluación de JavaScript global
            logger.info("🔎 Intentando extracción con JavaScript desde todos los frames...")
            js_results = await self.extract_results_with_js_all_frames(page)
            
            if js_results:
                return js_results
            
            logger.warning(f"⚠️ No se encontraron resultados para mesa {game_id}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo resultados de Baccarat: {e}")
            return None
    
    async def try_extract_from_frame(self, frame, game_id: str, frame_name: str) -> Optional[List[str]]:
        """Intenta extraer resultados de un frame específico"""
        try:
            # Selectores comunes para resultados de Baccarat
            selectors = [
                # Evolution Gaming (proveedor común)
                '.roadmap-results .result',
                '.history-results .result-item',
                '.game-history .result',
                '[class*="result"][class*="history"]',
                '[class*="roadmap"] [class*="result"]',
                
                # Selectores genéricos
                '.bead-road .bead',
                '.big-road .result',
                '[data-result]',
                '.result-b, .result-p, .result-t',
                
                # Selectores alternativos
                'div[class*="banker"], div[class*="player"], div[class*="tie"]',
                
                # Selectores Evolution Gaming específicos
                '.beadRoad--beadRoad .bead--bead',
                '.bigRoad--bigRoad .result--result',
                '[class*="beadRoad"] [class*="bead"]',
                '[class*="bigRoad"] [class*="result"]',
                '.statistics-table .result',
                '[data-role="roadmap"] [data-result]',
            ]
            
            results = []
            
            for selector in selectors:
                try:
                    # Esperar a que aparezcan los elementos
                    await frame.wait_for_selector(selector, timeout=3000)
                    
                    # Obtener elementos
                    elements = await frame.query_selector_all(selector)
                    
                    if elements:
                        logger.info(f"🔍 Encontrados {len(elements)} elementos con selector '{selector}' en {frame_name}")
                        
                        for element in elements[:20]:  # Limitar a últimos 20 resultados
                            # Intentar obtener el resultado del elemento
                            result = await self.extract_result_from_element(element)
                            if result:
                                results.append(result)
                        
                        if results:
                            logger.info(f"✅ Extraídos {len(results)} resultados desde {frame_name}: {results[:5]}...")
                            return results
                            
                except Exception as e:
                    continue
            
            # Si no funcionó con selectores, intentar JavaScript en este frame
            js_results = await self.extract_results_with_js_in_frame(frame)
            if js_results:
                logger.info(f"✅ Extraídos {len(js_results)} resultados con JS desde {frame_name}")
                return js_results
            
            return None
            
        except Exception as e:
            logger.debug(f"Error extrayendo desde {frame_name}: {e}")
            return None
    
    async def extract_results_with_js_in_frame(self, frame) -> Optional[List[str]]:
        """Extrae resultados usando JavaScript en un frame específico"""
        try:
            js_code = """
                () => {
                    const results = [];
                    
                    // Buscar elementos que puedan contener resultados
                    const keywords = ['result', 'history', 'roadmap', 'bead', 'banker', 'player', 'tie', 'road'];
                    
                    for (const keyword of keywords) {
                        const elements = document.querySelectorAll(`[class*="${keyword}"]`);
                        
                        for (const el of elements) {
                            const text = el.textContent?.toUpperCase() || '';
                            const classes = el.className?.toLowerCase() || '';
                            const dataResult = el.getAttribute('data-result')?.toUpperCase() || '';
                            
                            if (text.includes('BANKER') || classes.includes('banker') || classes.includes('banca') || dataResult.includes('B')) {
                                results.push('B');
                            } else if (text.includes('PLAYER') || classes.includes('player') || classes.includes('jugador') || dataResult.includes('P')) {
                                results.push('P');
                            } else if (text.includes('TIE') || classes.includes('tie') || classes.includes('empate') || dataResult.includes('T') || dataResult.includes('E')) {
                                results.push('E');
                            }
                        }
                        
                        if (results.length > 0) break;
                    }
                    
                    return results.slice(0, 20);
                }
            """
            
            results = await frame.evaluate(js_code)
            
            if results and len(results) > 0:
                return results
            
            return None
            
        except Exception as e:
            return None
    
    async def extract_results_with_js_all_frames(self, page: Page) -> Optional[List[str]]:
        """Extrae resultados usando JavaScript desde todos los frames"""
        try:
            for frame in page.frames:
                results = await self.extract_results_with_js_in_frame(frame)
                if results:
                    return results
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo resultados: {e}")
            return None
    
    async def extract_result_from_element(self, element) -> Optional[str]:
        """Extrae el resultado de un elemento HTML"""
        try:
            # Intentar obtener texto
            text = await element.text_content()
            if text:
                text_upper = text.strip().upper()
                
                # Mapeo de resultados
                if any(x in text_upper for x in ['BANKER', 'BANCA', 'B']):
                    return 'B'
                elif any(x in text_upper for x in ['PLAYER', 'JUGADOR', 'P']):
                    return 'P'
                elif any(x in text_upper for x in ['TIE', 'EMPATE', 'T', 'E']):
                    return 'E'
            
            # Intentar obtener de clases
            classes = await element.get_attribute('class')
            if classes:
                classes_lower = classes.lower()
                if 'banker' in classes_lower or 'banca' in classes_lower:
                    return 'B'
                elif 'player' in classes_lower or 'jugador' in classes_lower:
                    return 'P'
                elif 'tie' in classes_lower or 'empate' in classes_lower:
                    return 'E'
            
            # Intentar obtener de data attributes
            data_result = await element.get_attribute('data-result')
            if data_result:
                data_upper = data_result.upper()
                if data_upper in ['B', 'BANKER', 'BANCA']:
                    return 'B'
                elif data_upper in ['P', 'PLAYER', 'JUGADOR']:
                    return 'P'
                elif data_upper in ['T', 'E', 'TIE', 'EMPATE']:
                    return 'E'
            
            return None
            
        except Exception as e:
            return None
    
    async def extract_results_with_js(self, page: Page) -> Optional[List[str]]:
        """Extrae resultados usando evaluación de JavaScript"""
        try:
            js_code = """
                () => {
                    const results = [];
                    
                    // Buscar elementos que puedan contener resultados
                    const keywords = ['result', 'history', 'roadmap', 'bead', 'banker', 'player', 'tie'];
                    
                    for (const keyword of keywords) {
                        const elements = document.querySelectorAll(`[class*="${keyword}"]`);
                        
                        for (const el of elements) {
                            const text = el.textContent?.toUpperCase() || '';
                            const classes = el.className?.toLowerCase() || '';
                            
                            if (text.includes('BANKER') || classes.includes('banker') || classes.includes('banca')) {
                                results.push('B');
                            } else if (text.includes('PLAYER') || classes.includes('player') || classes.includes('jugador')) {
                                results.push('P');
                            } else if (text.includes('TIE') || classes.includes('tie') || classes.includes('empate')) {
                                results.push('E');
                            }
                        }
                        
                        if (results.length > 0) break;
                    }
                    
                    return results.slice(0, 20);
                }
            """
            
            results = await page.evaluate(js_code)
            
            if results and len(results) > 0:
                logger.info(f"✅ Extraídos {len(results)} resultados con JavaScript")
                return results
            
            return None
            
        except Exception as e:
            logger.error(f"Error en extracción JavaScript: {e}")
            return None
    
    async def get_table_result(self, table_name: str, game_id: str, game_slug: str = "") -> Optional[str]:
        """Obtiene el último resultado de una mesa"""
        try:
            if not self.initialized:
                logger.warning("⚠️ Playwright no inicializado, llamando a init()...")
                await self.init()
            
            # Verificar caché
            cache_key = f"{game_id}_result"
            if cache_key in self.last_results:
                cached_data, timestamp = self.last_results[cache_key]
                if (datetime.now() - timestamp).total_seconds() < self.cache_duration:
                    logger.info(f"📦 Usando resultado en caché para {table_name}")
                    return cached_data
            
            # Obtener o crear página para esta mesa
            page = await self.get_or_create_page(game_id)
            
            # Navegar al juego
            if not await self.navigate_to_game(page, game_id, game_name=game_slug):
                logger.error(f"❌ No se pudo navegar a la mesa {table_name}")
                return None
            
            # Extraer resultados
            results = await self.extract_baccarat_results(page, game_id)
            
            if results and len(results) > 0:
                # Tomar el resultado más reciente
                latest_result = results[0]
                
                # Guardar en caché
                self.last_results[cache_key] = (latest_result, datetime.now())
                
                logger.info(f"✅ Resultado obtenido para {table_name}: {latest_result}")
                return latest_result
            
            logger.warning(f"⚠️ No se obtuvieron resultados para {table_name}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo resultado de {table_name}: {e}")
            return None
    
    async def get_multiple_tables_results(self, tables: Dict[str, str]) -> Dict[str, Optional[str]]:
        """Obtiene resultados de múltiples mesas en paralelo"""
        results = {}
        
        # Crear tareas para todas las mesas
        tasks = []
        for table_name, game_id in tables.items():
            task = self.get_table_result(table_name, game_id)
            tasks.append((table_name, task))
        
        # Ejecutar con límite de concurrencia para no sobrecargar
        semaphore = asyncio.Semaphore(5)  # Máximo 5 mesas simultáneas
        
        async def limited_task(table_name, task):
            async with semaphore:
                return table_name, await task
        
        # Ejecutar todas las tareas
        completed_tasks = await asyncio.gather(
            *[limited_task(name, task) for name, task in tasks],
            return_exceptions=True
        )
        
        # Procesar resultados
        for item in completed_tasks:
            if isinstance(item, tuple):
                table_name, result = item
                results[table_name] = result
            else:
                logger.error(f"Error en tarea: {item}")
        
        logger.info(f"📊 Resultados obtenidos: {len([r for r in results.values() if r])} de {len(tables)} mesas")
        
        return results
