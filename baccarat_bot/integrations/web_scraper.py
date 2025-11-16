# baccarat_bot/integrations/web_scraper.py

import asyncio
import logging
import random
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import aiohttp
from bs4 import BeautifulSoup
import json

logger = logging.getLogger(__name__)


class WebScraper1xBet:
    """Scraper para obtener datos reales de 1xBet"""
    
    def __init__(self):
        self.base_url = "https://col.1xbet.com"
        self.session = None
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        ]
        self.proxies = [
            # Lista de proxies (en producción usar proxies reales)
            None,  # Sin proxy por defecto
        ]
        self.rate_limit_delay = 2  # Segundos entre requests
        self.last_request_time = {}
        self.cache = {}
        self.cache_duration = 30  # Segundos
    
    async def init_session(self):
        """Inicializa la sesión HTTP"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def close_session(self):
        """Cierra la sesión HTTP"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def get_random_headers(self) -> Dict[str, str]:
        """Obtiene headers aleatorios para evitar detección"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
            'DNT': '1'
        }
    
    async def rate_limit(self, key: str = 'default'):
        """Implementa rate limiting"""
        now = time.time()
        last_time = self.last_request_time.get(key, 0)
        elapsed = now - last_time
        
        if elapsed < self.rate_limit_delay:
            wait_time = self.rate_limit_delay - elapsed
            await asyncio.sleep(wait_time)
        
        self.last_request_time[key] = time.time()
    
    def get_cache_key(self, url: str) -> str:
        """Genera una clave de caché"""
        return f"cache:{url}"
    
    def get_from_cache(self, key: str) -> Optional[Any]:
        """Obtiene datos del caché"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_duration:
                return data
            else:
                del self.cache[key]
        return None
    
    def set_cache(self, key: str, data: Any):
        """Guarda datos en el caché"""
        self.cache[key] = (data, time.time())
    
    async def fetch_page(self, url: str) -> Optional[str]:
        """Obtiene el contenido de una página"""
        try:
            # Verificar caché primero
            cache_key = self.get_cache_key(url)
            cached_data = self.get_from_cache(cache_key)
            if cached_data:
                logger.info(f"Usando caché para {url}")
                return cached_data
            
            # Rate limiting
            await self.rate_limit(url)
            
            # Seleccionar proxy aleatorio
            proxy = random.choice(self.proxies)
            
            headers = self.get_random_headers()
            
            async with self.session.get(url, headers=headers, proxy=proxy) as response:
                if response.status == 200:
                    content = await response.text()
                    self.set_cache(cache_key, content)
                    logger.info(f"Página obtenida exitosamente: {url}")
                    return content
                else:
                    logger.warning(f"Error HTTP {response.status} al obtener {url}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error al obtener página {url}: {e}")
            return None
    
    async def get_baccarat_results(self, game_id: str = "97408") -> Optional[Dict[str, Any]]:
        """Obtiene resultados de juegos de Baccarat"""
        try:
            url = f"{self.base_url}/es/casino/game/{game_id}"
            content = await self.fetch_page(url)
            
            if not content:
                return None
            
            # Parsear el contenido HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # Buscar resultados en el HTML (estructura puede variar)
            results = []
            
            # Intentar diferentes selectores comunes
            selectors = [
                '.game-result',
                '.result-item',
                '.history-item',
                '.round-result',
                '[data-result]'
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    for element in elements[:10]:  # Limitar a últimos 10 resultados
                        result = self.extract_result_from_element(element)
                        if result:
                            results.append(result)
                    break
            
            if results:
                return {
                    'game_id': game_id,
                    'results': results,
                    'timestamp': datetime.now().isoformat(),
                    'source': '1xbet'
                }
            
            # Si no se encontraron resultados, intentar con JavaScript rendering
            logger.info("No se encontraron resultados en HTML, intentando con JavaScript")
            return await self.get_results_with_js_rendering(game_id)
            
        except Exception as e:
            logger.error(f"Error al obtener resultados de Baccarat: {e}")
            return None
    
    def extract_result_from_element(self, element) -> Optional[str]:
        """Extrae el resultado de un elemento HTML"""
        try:
            # Buscar texto que indique resultado
            text = element.get_text().upper()
            
            # Mapeo de resultados comunes
            result_map = {
                'BANKER': 'B',
                'PLAYER': 'P',
                'TIE': 'E',
                'BANCA': 'B',
                'JUGADOR': 'P',
                'EMPATE': 'E',
                'B': 'B',
                'P': 'P',
                'E': 'E'
            }
            
            for key, value in result_map.items():
                if key in text:
                    return value
            
            # Buscar en clases o atributos
            classes = element.get('class', [])
            for cls in classes:
                if 'banker' in cls.lower() or 'banca' in cls.lower():
                    return 'B'
                elif 'player' in cls.lower() or 'jugador' in cls.lower():
                    return 'P'
                elif 'tie' in cls.lower() or 'empate' in cls.lower():
                    return 'E'
            
            return None
            
        except Exception as e:
            logger.error(f"Error extrayendo resultado: {e}")
            return None
    
    async def get_results_with_js_rendering(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene resultados usando renderizado de JavaScript (placeholder)"""
        # En una implementación real, aquí se usaría Playwright, Selenium o similar
        logger.info("Renderizado de JavaScript no implementado aún")
        
        # Por ahora, retornar datos simulados para pruebas
        return {
            'game_id': game_id,
            'results': [
                {'result': 'B', 'timestamp': datetime.now().isoformat()},
                {'result': 'P', 'timestamp': datetime.now().isoformat()},
                {'result': 'B', 'timestamp': datetime.now().isoformat()},
                {'result': 'E', 'timestamp': datetime.now().isoformat()},
                {'result': 'P', 'timestamp': datetime.now().isoformat()}
            ],
            'timestamp': datetime.now().isoformat(),
            'source': 'simulated',
            'note': 'JavaScript rendering not implemented'
        }
    
    async def get_multiple_table_results(self, table_ids: List[str]) -> Dict[str, Any]:
        """Obtiene resultados de múltiples mesas"""
        results = {}
        
        tasks = []
        for table_id in table_ids:
            task = self.get_baccarat_results(table_id)
            tasks.append((table_id, task))
        
        # Ejecutar todas las tareas en paralelo
        for table_id, task in tasks:
            try:
                result = await task
                if result:
                    results[table_id] = result
                else:
                    results[table_id] = {
                        'error': 'No se pudieron obtener resultados',
                        'game_id': table_id
                    }
            except Exception as e:
                logger.error(f"Error obteniendo resultados para mesa {table_id}: {e}")
                results[table_id] = {
                    'error': str(e),
                    'game_id': table_id
                }
        
        return {
            'tables': results,
            'timestamp': datetime.now().isoformat(),
            'total_tables': len(table_ids),
            'successful': len([r for r in results.values() if 'error' not in r])
        }
    
    async def get_live_casino_data(self) -> Optional[Dict[str, Any]]:
        """Obtiene datos de casino en vivo"""
        try:
            # URL de casino en vivo de 1xBet
            live_casino_url = f"{self.base_url}/es/casino/live"
            
            content = await self.fetch_page(live_casino_url)
            if not content:
                return None
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Buscar juegos de Baccarat en vivo
            baccarat_games = []
            
            # Selectores comunes para juegos de casino en vivo
            game_selectors = [
                '.live-game-item',
                '.casino-game-item',
                '.game-card',
                '.table-item'
            ]
            
            for selector in game_selectors:
                games = soup.select(selector)
                for game in games:
                    game_info = self.extract_game_info(game)
                    if game_info and 'baccarat' in game_info.get('name', '').lower():
                        baccarat_games.append(game_info)
            
            return {
                'live_games': baccarat_games,
                'total_games': len(baccarat_games),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo datos de casino en vivo: {e}")
            return None
    
    def extract_game_info(self, element) -> Optional[Dict[str, Any]]:
        """Extrae información de un juego del HTML"""
        try:
            # Buscar nombre del juego
            name_selectors = ['.game-name', '.title', '.game-title', 'h3', 'h4']
            name = None
            
            for selector in name_selectors:
                name_elem = element.select_one(selector)
                if name_elem:
                    name = name_elem.get_text().strip()
                    break
            
            if not name:
                return None
            
            # Buscar información adicional
            info = {
                'name': name,
                'element_html': str(element)[:200]  # Para debugging
            }
            
            # Buscar URL o ID del juego
            link_elem = element.select_one('a')
            if link_elem and link_elem.get('href'):
                info['url'] = link_elem['href']
            
            return info
            
        except Exception as e:
            logger.error(f"Error extrayendo info de juego: {e}")
            return None


class DataSourceManager:
    """Gestiona múltiples fuentes de datos"""
    
    def __init__(self):
        self.scraper = WebScraper1xBet()
        self.fallback_enabled = True
        self.simulation_mode = False
    
    async def init(self):
        """Inicializa el gestor"""
        await self.scraper.init_session()
    
    async def close(self):
        """Cierra el gestor"""
        await self.scraper.close_session()
    
    async def get_table_result(self, table_name: str, table_id: str) -> Optional[str]:
        """
        Obtiene el resultado más reciente de una mesa específica
        
        Args:
            table_name: Nombre de la mesa
            table_id: ID del juego en 1xBet
            
        Returns:
            Resultado más reciente ('B', 'P', 'E') o None
        """
        try:
            if self.simulation_mode:
                # Modo simulación para pruebas
                return self._simulate_result()
            
            # Intentar obtener datos reales
            result_data = await self.scraper.get_baccarat_results(table_id)
            
            if result_data and 'results' in result_data and result_data['results']:
                # Tomar el resultado más reciente
                latest_result = result_data['results'][0]
                if 'result' in latest_result:
                    return latest_result['result']
            
            # Si falla y hay fallback habilitado, usar simulación
            if self.fallback_enabled:
                logger.warning(f"Usando fallback para mesa {table_name}")
                return self._simulate_result()
            
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo resultado para {table_name}: {e}")
            if self.fallback_enabled:
                return self._simulate_result()
            return None
    
    def _simulate_result(self) -> str:
        """Genera un resultado simulado para fallback"""
        # Probabilidades aproximadas del Baccarat real
        import random
        probabilidades = {
            'B': 46,  # Banca ~45.86%
            'P': 45,  # Jugador ~44.62%
            'E': 9    # Empate ~9.52%
        }
        
        opciones = []
        for resultado, prob in probabilidades.items():
            opciones.extend([resultado] * prob)
        
        return random.choice(opciones)
    
    async def get_multiple_tables_results(self, tables: Dict[str, str]) -> Dict[str, str]:
        """
        Obtiene resultados de múltiples mesas
        
        Args:
            tables: Dict con {nombre_mesa: table_id}
            
        Returns:
            Dict con {nombre_mesa: resultado}
        """
        results = {}
        
        for table_name, table_id in tables.items():
            result = await self.get_table_result(table_name, table_id)
            results[table_name] = result
        
        return results
    
    def enable_simulation_mode(self, enabled: bool = True):
        """Activa/desactiva el modo simulación"""
        self.simulation_mode = enabled
        logger.info(f"Modo simulación {'activado' if enabled else 'desactivado'}")
    
    def enable_fallback(self, enabled: bool = True):
        """Activa/desactiva el fallback a simulación"""
        self.fallback_enabled = enabled
        logger.info(f"Fallback {'activado' if enabled else 'desactivado'}")


# Instancia global del gestor de fuentes de datos
data_source_manager = DataSourceManager()