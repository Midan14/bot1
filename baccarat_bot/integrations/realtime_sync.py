# baccarat_bot/integrations/realtime_sync.py

"""
Sistema de sincronización en tiempo real con las mesas de Baccarat.
Detecta el estado actual del juego y sincroniza las señales con el timing exacto.
"""

import asyncio
import logging
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from playwright.async_api import Page

logger = logging.getLogger(__name__)


class GameState(Enum):
    """Estados del juego"""
    WAITING_FOR_BETS = "waiting_for_bets"  # Esperando apuestas
    BETTING_CLOSED = "betting_closed"      # Apuestas cerradas
    DEALING = "dealing"                    # Repartiendo cartas
    REVEALING = "revealing"                # Revelando resultado
    FINISHED = "finished"                  # Ronda terminada
    SHUFFLING = "shuffling"                # Barajando cartas
    UNKNOWN = "unknown"                    # Estado desconocido


@dataclass
class GameRound:
    """Información de una ronda de juego"""
    round_number: int
    state: GameState
    time_remaining: Optional[int]  # Segundos restantes para apostar
    last_result: Optional[str]     # Último resultado (B, P, E)
    history: List[str]             # Historial de resultados
    timestamp: datetime
    
    def is_betting_open(self) -> bool:
        """Verifica si las apuestas están abiertas"""
        return self.state == GameState.WAITING_FOR_BETS and (
            self.time_remaining is None or self.time_remaining > 5
        )
    
    def should_send_signal(self) -> bool:
        """Verifica si es el momento óptimo para enviar señal"""
        # Enviar señal solo cuando quedan entre 15 y 25 segundos
        return (
            self.state == GameState.WAITING_FOR_BETS and
            self.time_remaining is not None and
            15 <= self.time_remaining <= 25
        )


class RealtimeSynchronizer:
    """
    Sincronizador en tiempo real con las mesas de Baccarat.
    
    Características:
    - Detección del estado actual del juego
    - Extracción del tiempo restante para apostar
    - Sincronización de señales con el timing óptimo
    - Detección de cambios de crupier y barajado
    - Historial en tiempo real
    """
    
    def __init__(self):
        self.current_rounds: Dict[str, GameRound] = {}
        self.last_sync_time: Dict[str, datetime] = {}
        self.sync_interval = 2  # Segundos entre sincronizaciones
    
    async def detect_game_state(self, page: Page, table_id: str) -> GameState:
        """
        Detecta el estado actual del juego en la mesa.
        
        Args:
            page: Página de Playwright
            table_id: ID de la mesa
            
        Returns:
            Estado actual del juego
        """
        try:
            # Selectores para detectar estados (ajustar según el sitio real)
            state_selectors = {
                GameState.WAITING_FOR_BETS: [
                    '[data-testid="game-status-text"]:has-text("Place your bets")',
                    '[data-testid="game-status-text"]:has-text("Haga sus apuestas")',
                    '.status-text:has-text("Place your bets")',
                    '.status-text:has-text("Haga sus apuestas")'
                ],
                GameState.BETTING_CLOSED: [
                    '[data-testid="game-status-text"]:has-text("No more bets")',
                    '[data-testid="game-status-text"]:has-text("No más apuestas")',
                    '.status-text:has-text("No more bets")',
                    '.status-text:has-text("No más apuestas")'
                ],
                GameState.DEALING: [
                    '[data-testid="game-status-text"]:has-text("Dealing")',
                    '[data-testid="game-status-text"]:has-text("Repartiendo")',
                    '.status-text:has-text("Dealing")'
                ],
                GameState.SHUFFLING: [
                    '[data-testid="game-status-text"]:has-text("Shuffling")',
                    '[data-testid="game-status-text"]:has-text("Barajando")',
                    '.status-text:has-text("Shuffling")'
                ]
            }
            
            # Intentar detectar cada estado
            for state, selectors in state_selectors.items():
                for selector in selectors:
                    try:
                        if await page.locator(selector).count() > 0:
                            logger.debug(f"Estado detectado para {table_id}: {state.value}")
                            return state
                    except:
                        continue
            
            # Si no se detecta ningún estado específico, asumir UNKNOWN
            return GameState.UNKNOWN
            
        except Exception as e:
            logger.error(f"Error detectando estado del juego: {e}")
            return GameState.UNKNOWN
    
    async def extract_timer(self, page: Page) -> Optional[int]:
        """
        Extrae el tiempo restante del temporizador de apuestas.
        
        Args:
            page: Página de Playwright
            
        Returns:
            Segundos restantes o None si no se encuentra
        """
        try:
            # Selectores comunes para temporizadores
            timer_selectors = [
                '[data-testid="game-timer"]',
                '.timer-value',
                '.game-timer__value'
            ]
            
            for selector in timer_selectors:
                try:
                    timer_element = page.locator(selector).first
                    if await timer_element.count() > 0:
                        timer_text = await timer_element.inner_text()
                        
                        # Extraer número del texto
                        import re
                        numbers = re.findall(r'\d+', timer_text)
                        if numbers:
                            seconds = int(numbers[0])
                            logger.debug(f"Tiempo restante detectado: {seconds}s")
                            return seconds
                except:
                    continue
            
            # Intentar extraer mediante JavaScript
            timer_value = await page.evaluate("""
                () => {
                    // Buscar elementos con texto numérico
                    const elements = document.querySelectorAll('*');
                    for (let el of elements) {
                        const text = el.textContent.trim();
                        if (/^\\d{1,2}$/.test(text)) {
                            const num = parseInt(text);
                            if (num > 0 && num <= 60) {
                                return num;
                            }
                        }
                    }
                    return null;
                }
            """)
            
            if timer_value:
                logger.debug(f"Tiempo restante (JS): {timer_value}s")
                return timer_value
            
            return None
            
        except Exception as e:
            logger.warning(f"Error extrayendo temporizador: {e}")
            return None
    
    async def extract_last_result(self, page: Page) -> Optional[str]:
        """
        Extrae el último resultado de la mesa.
        
        Args:
            page: Página de Playwright
            
        Returns:
            'B', 'P', 'E' o None
        """
        try:
            # Selectores para resultados
            result_selectors = [
                '[data-testid="last-result-text"]',
                '.last-result__text',
                '.game-result__winner'
            ]
            
            for selector in result_selectors:
                try:
                    result_element = page.locator(selector).first
                    if await result_element.count() > 0:
                        result_text = await result_element.inner_text()
                        result_text = result_text.upper()
                        
                        # Mapear texto a resultado
                        if 'BANKER' in result_text or 'BANCA' in result_text or 'B' == result_text:
                            return 'B'
                        elif 'PLAYER' in result_text or 'JUGADOR' in result_text or 'P' == result_text:
                            return 'P'
                        elif 'TIE' in result_text or 'EMPATE' in result_text or 'E' == result_text:
                            return 'E'
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.warning(f"Error extrayendo último resultado: {e}")
            return None
    
    async def extract_history(self, page: Page, max_results: int = 20) -> List[str]:
        """
        Extrae el historial de resultados de la mesa.
        
        Args:
            page: Página de Playwright
            max_results: Número máximo de resultados a extraer
            
        Returns:
            Lista de resultados ['B', 'P', 'E', ...]
        """
        try:
            # Selectores para historial
            history_selectors = [
                '[data-testid="bead-road-history"]',
                '.bead-road__container',
                '.history-grid'
            ]
            
            for selector in history_selectors:
                try:
                    history_container = page.locator(selector).first
                    if await history_container.count() > 0:
                        # Extraer elementos individuales
                        result_elements = await history_container.locator('*').all()
                        
                        history = []
                        for element in result_elements[:max_results]:
                            try:
                                # Intentar por clases CSS
                                classes = await element.get_attribute('class') or ''
                                classes = classes.lower()
                                
                                if 'banker' in classes or 'banca' in classes or 'red' in classes:
                                    history.append('B')
                                elif 'player' in classes or 'jugador' in classes or 'blue' in classes:
                                    history.append('P')
                                elif 'tie' in classes or 'empate' in classes or 'green' in classes:
                                    history.append('E')
                                else:
                                    # Intentar por texto
                                    text = await element.inner_text()
                                    text = text.strip().upper()
                                    if text in ['B', 'P', 'E']:
                                        history.append(text)
                            except:
                                continue
                        
                        if history:
                            logger.debug(f"Historial extraído: {history[:10]}...")
                            return history
                except:
                    continue
            
            # Intentar mediante JavaScript
            history_js = await page.evaluate("""
                () => {
                    const results = [];
                    // Buscar elementos con clases específicas
                    const elements = document.querySelectorAll('[class*="result"], [class*="history"]');
                    for (let el of elements) {
                        const classes = el.className.toLowerCase();
                        if (classes.includes('banker') || classes.includes('banca')) {
                            results.push('B');
                        } else if (classes.includes('player') || classes.includes('jugador')) {
                            results.push('P');
                        } else if (classes.includes('tie') || classes.includes('empate')) {
                            results.push('E');
                        }
                    }
                    return results.slice(0, 20);
                }
            """)
            
            if history_js:
                logger.debug(f"Historial extraído (JS): {history_js[:10]}...")
                return history_js
            
            return []
            
        except Exception as e:
            logger.warning(f"Error extrayendo historial: {e}")
            return []
    
    async def sync_table(self, page: Page, table_id: str) -> Optional[GameRound]:
        """
        Sincroniza el estado completo de una mesa.
        
        Args:
            page: Página de Playwright
            table_id: ID de la mesa
            
        Returns:
            GameRound con información actualizada o None
        """
        try:
            # Detectar estado del juego
            state = await self.detect_game_state(page, table_id)
            
            # Extraer tiempo restante
            time_remaining = await self.extract_timer(page)
            
            # Extraer último resultado
            last_result = await self.extract_last_result(page)
            
            # Extraer historial
            history = await self.extract_history(page)
            
            # Obtener número de ronda (incrementar si cambió el resultado)
            previous_round = self.current_rounds.get(table_id)
            round_number = 1
            if previous_round:
                if last_result and last_result != previous_round.last_result:
                    round_number = previous_round.round_number + 1
                else:
                    round_number = previous_round.round_number
            
            # Crear GameRound
            game_round = GameRound(
                round_number=round_number,
                state=state,
                time_remaining=time_remaining,
                last_result=last_result,
                history=history,
                timestamp=datetime.now()
            )
            
            # Guardar en caché
            self.current_rounds[table_id] = game_round
            self.last_sync_time[table_id] = datetime.now()
            
            logger.info(
                f"Mesa {table_id} sincronizada: estado={state.value}, "
                f"tiempo={time_remaining}s, último={last_result}"
            )
            
            return game_round
            
        except Exception as e:
            logger.error(f"Error sincronizando mesa {table_id}: {e}")
            return None
    
    async def wait_for_optimal_timing(
        self,
        page: Page,
        table_id: str,
        max_wait_seconds: int = 60
    ) -> bool:
        """
        Espera hasta el momento óptimo para enviar una señal.
        
        Args:
            page: Página de Playwright
            table_id: ID de la mesa
            max_wait_seconds: Tiempo máximo de espera
            
        Returns:
            True si se alcanzó el timing óptimo, False si timeout
        """
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < max_wait_seconds:
            # Sincronizar estado
            game_round = await self.sync_table(page, table_id)
            
            if game_round and game_round.should_send_signal():
                logger.info(
                    f"Timing óptimo alcanzado para {table_id}: "
                    f"{game_round.time_remaining}s restantes"
                )
                return True
            
            # Esperar antes de la siguiente verificación
            await asyncio.sleep(self.sync_interval)
        
        logger.warning(f"Timeout esperando timing óptimo para {table_id}")
        return False
    
    def get_current_round(self, table_id: str) -> Optional[GameRound]:
        """
        Obtiene la información de la ronda actual de una mesa.
        
        Args:
            table_id: ID de la mesa
            
        Returns:
            GameRound actual o None
        """
        return self.current_rounds.get(table_id)
    
    def is_sync_needed(self, table_id: str) -> bool:
        """
        Verifica si es necesario sincronizar una mesa.
        
        Args:
            table_id: ID de la mesa
            
        Returns:
            True si necesita sincronización
        """
        last_sync = self.last_sync_time.get(table_id)
        if not last_sync:
            return True
        
        elapsed = (datetime.now() - last_sync).total_seconds()
        return elapsed >= self.sync_interval


# Instancia global del sincronizador
realtime_sync = RealtimeSynchronizer()
