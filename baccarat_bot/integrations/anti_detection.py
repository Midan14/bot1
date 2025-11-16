# baccarat_bot/integrations/anti_detection.py

"""
Sistema avanzado anti-detección para web scraping.
Implementa técnicas sofisticadas para evitar la detección de bots.
"""

import random
import asyncio
import logging
from typing import Optional, List, Dict
from playwright.async_api import Page, Browser, BrowserContext

logger = logging.getLogger(__name__)


class AntiDetectionSystem:
    """
    Sistema completo anti-detección para scraping con Playwright.
    
    Técnicas implementadas:
    - Rotación de User-Agents realistas
    - Fingerprinting de navegador modificado
    - Comportamiento humano simulado (movimientos de mouse, scrolls)
    - Headers HTTP realistas
    - Tiempos de espera aleatorios
    - Cookies y localStorage persistentes
    - WebRTC leak prevention
    - Canvas fingerprinting evasion
    - WebGL fingerprinting evasion
    - Audio fingerprinting evasion
    """
    
    # User-Agents realistas de navegadores modernos
    USER_AGENTS = [
        # Chrome en Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        # Chrome en macOS
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        # Edge en Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        # Firefox en Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        # Safari en macOS
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    ]
    
    # Viewports realistas
    VIEWPORTS = [
        {'width': 1920, 'height': 1080},  # Full HD
        {'width': 1366, 'height': 768},   # Laptop común
        {'width': 1536, 'height': 864},   # Laptop HD+
        {'width': 1440, 'height': 900},   # MacBook
        {'width': 2560, 'height': 1440},  # 2K
    ]
    
    # Idiomas realistas
    LANGUAGES = [
        'es-ES,es;q=0.9,en;q=0.8',
        'es-CO,es;q=0.9,en;q=0.8',
        'es-MX,es;q=0.9,en;q=0.8',
        'es-AR,es;q=0.9,en;q=0.8',
        'en-US,en;q=0.9,es;q=0.8',
    ]
    
    # Timezones realistas para Latinoamérica
    TIMEZONES = [
        'America/Bogota',
        'America/Mexico_City',
        'America/Buenos_Aires',
        'America/Lima',
        'America/Santiago',
    ]
    
    def __init__(self):
        self.current_user_agent = random.choice(self.USER_AGENTS)
        self.current_viewport = random.choice(self.VIEWPORTS)
        self.current_language = random.choice(self.LANGUAGES)
        self.current_timezone = random.choice(self.TIMEZONES)
    
    async def create_stealth_context(self, browser: Browser) -> BrowserContext:
        """
        Crea un contexto de navegador con configuración anti-detección.
        
        Args:
            browser: Instancia del navegador
            
        Returns:
            Contexto configurado con técnicas anti-detección
        """
        # Configuración del contexto
        context = await browser.new_context(
            user_agent=self.current_user_agent,
            viewport=self.current_viewport,
            locale='es-ES',
            timezone_id=self.current_timezone,
            geolocation={'latitude': 4.7110, 'longitude': -74.0721},  # Bogotá
            permissions=['geolocation'],
            color_scheme='light',
            device_scale_factor=1,
            has_touch=False,
            is_mobile=False,
            # Headers adicionales
            extra_http_headers={
                'Accept-Language': self.current_language,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            }
        )
        
        logger.info(
            f"Contexto stealth creado: UA={self.current_user_agent[:50]}..., "
            f"Viewport={self.current_viewport}"
        )
        
        return context
    
    async def apply_stealth_scripts(self, page: Page):
        """
        Aplica scripts de evasión de detección a una página.
        
        Args:
            page: Página de Playwright
        """
        # Script para modificar navigator properties
        await page.add_init_script("""
            // Ocultar webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Modificar plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [
                    {
                        0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                        description: "Portable Document Format",
                        filename: "internal-pdf-viewer",
                        length: 1,
                        name: "Chrome PDF Plugin"
                    },
                    {
                        0: {type: "application/pdf", suffixes: "pdf", description: "Portable Document Format"},
                        description: "Portable Document Format",
                        filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                        length: 1,
                        name: "Chrome PDF Viewer"
                    }
                ]
            });
            
            // Modificar languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['es-ES', 'es', 'en-US', 'en']
            });
            
            // Modificar platform
            Object.defineProperty(navigator, 'platform', {
                get: () => 'Win32'
            });
            
            // Modificar hardwareConcurrency (núcleos de CPU)
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 8
            });
            
            // Modificar deviceMemory
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8
            });
            
            // Modificar maxTouchPoints
            Object.defineProperty(navigator, 'maxTouchPoints', {
                get: () => 0
            });
            
            // Evasión de Chrome detection
            window.chrome = {
                runtime: {},
                loadTimes: function() {},
                csi: function() {},
                app: {}
            };
            
            // Evasión de Permissions API
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            
            // Evasión de WebGL fingerprinting
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel Iris OpenGL Engine';
                }
                return getParameter.apply(this, arguments);
            };
            
            // Evasión de Canvas fingerprinting
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function() {
                // Agregar ruido mínimo al canvas
                const context = this.getContext('2d');
                const imageData = context.getImageData(0, 0, this.width, this.height);
                for (let i = 0; i < imageData.data.length; i += 4) {
                    imageData.data[i] += Math.floor(Math.random() * 2);
                }
                context.putImageData(imageData, 0, 0);
                return originalToDataURL.apply(this, arguments);
            };
            
            // Evasión de Audio fingerprinting
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (AudioContext) {
                const originalCreateAnalyser = AudioContext.prototype.createAnalyser;
                AudioContext.prototype.createAnalyser = function() {
                    const analyser = originalCreateAnalyser.apply(this, arguments);
                    const originalGetFloatFrequencyData = analyser.getFloatFrequencyData;
                    analyser.getFloatFrequencyData = function() {
                        const data = originalGetFloatFrequencyData.apply(this, arguments);
                        // Agregar ruido mínimo
                        for (let i = 0; i < arguments[0].length; i++) {
                            arguments[0][i] += Math.random() * 0.01;
                        }
                        return data;
                    };
                    return analyser;
                };
            }
            
            // Evasión de WebRTC leak
            const originalGetUserMedia = navigator.mediaDevices.getUserMedia;
            navigator.mediaDevices.getUserMedia = function() {
                return originalGetUserMedia.apply(this, arguments).catch(() => {
                    throw new DOMException('Permission denied', 'NotAllowedError');
                });
            };
        """)
        
        logger.debug("Scripts anti-detección aplicados a la página")
    
    async def simulate_human_behavior(self, page: Page):
        """
        Simula comportamiento humano en la página.
        
        Args:
            page: Página de Playwright
        """
        try:
            # Movimiento aleatorio del mouse
            for _ in range(random.randint(2, 5)):
                x = random.randint(100, 800)
                y = random.randint(100, 600)
                await page.mouse.move(x, y, steps=random.randint(5, 15))
                await asyncio.sleep(random.uniform(0.1, 0.3))
            
            # Scroll aleatorio
            scroll_amount = random.randint(100, 500)
            await page.evaluate(f'window.scrollBy(0, {scroll_amount})')
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Volver arriba
            await page.evaluate('window.scrollTo(0, 0)')
            await asyncio.sleep(random.uniform(0.3, 0.8))
            
            logger.debug("Comportamiento humano simulado")
            
        except Exception as e:
            logger.warning(f"Error simulando comportamiento humano: {e}")
    
    async def random_delay(self, min_seconds: float = 0.5, max_seconds: float = 2.0):
        """
        Espera un tiempo aleatorio para simular comportamiento humano.
        
        Args:
            min_seconds: Tiempo mínimo de espera
            max_seconds: Tiempo máximo de espera
        """
        delay = random.uniform(min_seconds, max_seconds)
        await asyncio.sleep(delay)
    
    async def wait_for_page_load(self, page: Page, timeout: int = 30000):
        """
        Espera a que la página cargue completamente con verificaciones adicionales.
        
        Args:
            page: Página de Playwright
            timeout: Timeout en milisegundos
        """
        try:
            # Esperar a que la página esté en estado 'load'
            await page.wait_for_load_state('load', timeout=timeout)
            
            # Esperar a que no haya requests de red pendientes
            await page.wait_for_load_state('networkidle', timeout=timeout)
            
            # Esperar adicional aleatorio
            await self.random_delay(0.5, 1.5)
            
            logger.debug("Página cargada completamente")
            
        except Exception as e:
            logger.warning(f"Timeout esperando carga de página: {e}")
    
    async def handle_cloudflare(self, page: Page) -> bool:
        """
        Detecta y maneja desafíos de Cloudflare.
        
        Args:
            page: Página de Playwright
            
        Returns:
            True si se detectó y manejó Cloudflare, False en caso contrario
        """
        try:
            # Detectar página de desafío de Cloudflare
            cloudflare_selectors = [
                'div#challenge-running',
                'div.cf-browser-verification',
                'div#cf-wrapper',
                'div.ray_id'
            ]
            
            for selector in cloudflare_selectors:
                if await page.locator(selector).count() > 0:
                    logger.warning("Desafío de Cloudflare detectado, esperando...")
                    
                    # Esperar hasta 30 segundos para que se resuelva
                    for _ in range(30):
                        await asyncio.sleep(1)
                        
                        # Verificar si ya pasó el desafío
                        if await page.locator(selector).count() == 0:
                            logger.info("Desafío de Cloudflare superado")
                            await self.random_delay(1, 2)
                            return True
                    
                    logger.error("No se pudo superar el desafío de Cloudflare")
                    return False
            
            return False
            
        except Exception as e:
            logger.error(f"Error manejando Cloudflare: {e}")
            return False
    
    async def rotate_identity(self):
        """
        Rota la identidad del navegador (User-Agent, viewport, etc.)
        """
        self.current_user_agent = random.choice(self.USER_AGENTS)
        self.current_viewport = random.choice(self.VIEWPORTS)
        self.current_language = random.choice(self.LANGUAGES)
        self.current_timezone = random.choice(self.TIMEZONES)
        
        logger.info("Identidad del navegador rotada")
    
    def get_random_headers(self) -> Dict[str, str]:
        """
        Genera headers HTTP aleatorios pero realistas.
        
        Returns:
            Diccionario de headers
        """
        return {
            'User-Agent': self.current_user_agent,
            'Accept-Language': self.current_language,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
        }


# Instancia global del sistema anti-detección
anti_detection = AntiDetectionSystem()
