# baccarat_bot/utils/page_pool.py

"""
Pool de páginas de Playwright para gestión eficiente de memoria.
Reutiliza páginas del navegador y cierra las inactivas automáticamente.
"""

import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from playwright.async_api import Page, Browser

logger = logging.getLogger(__name__)


class PagePool:
    """
    Pool de páginas de Playwright con gestión automática de memoria.
    
    Características:
    - Reutilización de páginas para reducir overhead
    - Cierre automático de páginas inactivas
    - Límite máximo de páginas abiertas
    - Limpieza periódica de recursos
    """
    
    def __init__(
        self,
        browser: Browser,
        max_pages: int = 10,
        idle_timeout_minutes: int = 5,
        cleanup_interval_seconds: int = 60
    ):
        """
        Inicializa el pool de páginas
        
        Args:
            browser: Instancia del navegador de Playwright
            max_pages: Número máximo de páginas abiertas simultáneamente
            idle_timeout_minutes: Minutos de inactividad antes de cerrar una página
            cleanup_interval_seconds: Intervalo de limpieza automática
        """
        self.browser = browser
        self.max_pages = max_pages
        self.idle_timeout = timedelta(minutes=idle_timeout_minutes)
        self.cleanup_interval = cleanup_interval_seconds
        
        # Diccionario de páginas activas: table_id -> (page, last_used_time)
        self.active_pages: Dict[str, tuple[Page, datetime]] = {}
        
        # Cola de páginas disponibles para reutilización
        self.available_pages: asyncio.Queue = asyncio.Queue(maxsize=max_pages)
        
        # Tarea de limpieza en segundo plano
        self.cleanup_task: Optional[asyncio.Task] = None
        self.running = False
        
        logger.info(
            f"PagePool inicializado: max_pages={max_pages}, "
            f"idle_timeout={idle_timeout_minutes}min"
        )
    
    async def start(self):
        """Inicia el pool y la tarea de limpieza automática"""
        if not self.running:
            self.running = True
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("PagePool iniciado con limpieza automática")
    
    async def stop(self):
        """Detiene el pool y cierra todas las páginas"""
        self.running = False
        
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Cerrar todas las páginas activas
        for table_id, (page, _) in list(self.active_pages.items()):
            try:
                await page.close()
                logger.debug(f"Página cerrada para {table_id}")
            except Exception as e:
                logger.error(f"Error cerrando página para {table_id}: {e}")
        
        self.active_pages.clear()
        
        # Cerrar páginas disponibles
        while not self.available_pages.empty():
            try:
                page = self.available_pages.get_nowait()
                await page.close()
            except Exception as e:
                logger.error(f"Error cerrando página disponible: {e}")
        
        logger.info("PagePool detenido y todas las páginas cerradas")
    
    async def get_page(self, table_id: str, url: str) -> Page:
        """
        Obtiene una página para una mesa específica.
        Reutiliza páginas existentes o crea nuevas si es necesario.
        
        Args:
            table_id: Identificador único de la mesa
            url: URL a navegar
            
        Returns:
            Página de Playwright lista para usar
        """
        # Si ya existe una página activa para esta mesa, actualizarla
        if table_id in self.active_pages:
            page, _ = self.active_pages[table_id]
            self.active_pages[table_id] = (page, datetime.now())
            logger.debug(f"Reutilizando página existente para {table_id}")
            return page
        
        # Si hay páginas disponibles en el pool, reutilizar una
        if not self.available_pages.empty():
            try:
                page = self.available_pages.get_nowait()
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                self.active_pages[table_id] = (page, datetime.now())
                logger.debug(f"Página del pool reutilizada para {table_id}")
                return page
            except Exception as e:
                logger.warning(f"Error reutilizando página del pool: {e}")
        
        # Si no se alcanzó el límite, crear nueva página
        if len(self.active_pages) < self.max_pages:
            try:
                page = await self.browser.new_page()
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                self.active_pages[table_id] = (page, datetime.now())
                logger.info(
                    f"Nueva página creada para {table_id} "
                    f"({len(self.active_pages)}/{self.max_pages})"
                )
                return page
            except Exception as e:
                logger.error(f"Error creando nueva página para {table_id}: {e}")
                raise
        
        # Si se alcanzó el límite, esperar a que se libere una página
        logger.warning(
            f"Límite de páginas alcanzado ({self.max_pages}), "
            f"esperando página disponible..."
        )
        page = await self.available_pages.get()
        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        self.active_pages[table_id] = (page, datetime.now())
        return page
    
    async def release_page(self, table_id: str):
        """
        Libera una página para que pueda ser reutilizada
        
        Args:
            table_id: Identificador de la mesa
        """
        if table_id in self.active_pages:
            page, _ = self.active_pages.pop(table_id)
            
            # Si el pool no está lleno, agregar a páginas disponibles
            if self.available_pages.qsize() < self.max_pages:
                try:
                    self.available_pages.put_nowait(page)
                    logger.debug(f"Página liberada para reutilización: {table_id}")
                except asyncio.QueueFull:
                    await page.close()
                    logger.debug(f"Pool lleno, página cerrada: {table_id}")
            else:
                await page.close()
                logger.debug(f"Página cerrada: {table_id}")
    
    async def _cleanup_loop(self):
        """Loop de limpieza automática de páginas inactivas"""
        while self.running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self._cleanup_idle_pages()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error en loop de limpieza: {e}")
    
    async def _cleanup_idle_pages(self):
        """Cierra páginas que han estado inactivas por mucho tiempo"""
        now = datetime.now()
        idle_tables = []
        
        # Identificar páginas inactivas
        for table_id, (page, last_used) in self.active_pages.items():
            if now - last_used > self.idle_timeout:
                idle_tables.append(table_id)
        
        # Cerrar páginas inactivas
        for table_id in idle_tables:
            page, last_used = self.active_pages.pop(table_id)
            try:
                await page.close()
                idle_minutes = (now - last_used).total_seconds() / 60
                logger.info(
                    f"Página inactiva cerrada: {table_id} "
                    f"(inactiva por {idle_minutes:.1f} min)"
                )
            except Exception as e:
                logger.error(f"Error cerrando página inactiva {table_id}: {e}")
        
        if idle_tables:
            logger.info(
                f"Limpieza completada: {len(idle_tables)} páginas cerradas, "
                f"{len(self.active_pages)} activas"
            )
    
    def get_stats(self) -> Dict:
        """
        Obtiene estadísticas del pool
        
        Returns:
            Diccionario con estadísticas del pool
        """
        return {
            'active_pages': len(self.active_pages),
            'available_pages': self.available_pages.qsize(),
            'max_pages': self.max_pages,
            'running': self.running,
            'active_tables': list(self.active_pages.keys())
        }
