# baccarat_bot/utils/error_handler.py

"""
Módulo de manejo robusto de errores con reintentos y logging detallado.
"""

import asyncio
import logging
import functools
from typing import Callable, Any, Optional, Type, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class RetryConfig:
    """Configuración para reintentos"""
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        exceptions: Tuple[Type[Exception], ...] = (Exception,)
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.exceptions = exceptions


def retry_on_error(config: Optional[RetryConfig] = None):
    """
    Decorador para reintentar funciones que fallan con backoff exponencial.
    
    Args:
        config: Configuración de reintentos (usa valores por defecto si es None)
        
    Example:
        @retry_on_error(RetryConfig(max_retries=3, initial_delay=1.0))
        async def fetch_data():
            # código que puede fallar
            pass
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except config.exceptions as e:
                    last_exception = e
                    
                    if attempt == config.max_retries:
                        logger.error(
                            f"❌ {func.__name__} falló después de {config.max_retries} reintentos: {e}",
                            exc_info=True
                        )
                        raise
                    
                    # Calcular delay con backoff exponencial
                    delay = min(
                        config.initial_delay * (config.exponential_base ** attempt),
                        config.max_delay
                    )
                    
                    logger.warning(
                        f"⚠️ {func.__name__} falló (intento {attempt + 1}/{config.max_retries}), "
                        f"reintentando en {delay:.1f}s: {e}"
                    )
                    
                    await asyncio.sleep(delay)
            
            # Este punto no debería alcanzarse, pero por seguridad
            if last_exception:
                raise last_exception
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except config.exceptions as e:
                    last_exception = e
                    
                    if attempt == config.max_retries:
                        logger.error(
                            f"❌ {func.__name__} falló después de {config.max_retries} reintentos: {e}",
                            exc_info=True
                        )
                        raise
                    
                    # Calcular delay con backoff exponencial
                    delay = min(
                        config.initial_delay * (config.exponential_base ** attempt),
                        config.max_delay
                    )
                    
                    logger.warning(
                        f"⚠️ {func.__name__} falló (intento {attempt + 1}/{config.max_retries}), "
                        f"reintentando en {delay:.1f}s: {e}"
                    )
                    
                    import time
                    time.sleep(delay)
            
            if last_exception:
                raise last_exception
        
        # Retornar el wrapper apropiado según si la función es async o no
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class ErrorContext:
    """Contexto para capturar y registrar errores con información adicional"""
    
    def __init__(
        self,
        operation: str,
        context_data: Optional[dict] = None,
        raise_on_error: bool = True,
        log_level: int = logging.ERROR
    ):
        """
        Args:
            operation: Nombre de la operación que se está ejecutando
            context_data: Datos adicionales de contexto
            raise_on_error: Si debe re-lanzar la excepción
            log_level: Nivel de logging para el error
        """
        self.operation = operation
        self.context_data = context_data or {}
        self.raise_on_error = raise_on_error
        self.log_level = log_level
        self.start_time = None
        self.exception = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.exception = exc_val
            duration = (datetime.now() - self.start_time).total_seconds()
            
            error_info = {
                'operation': self.operation,
                'error_type': exc_type.__name__,
                'error_message': str(exc_val),
                'duration_seconds': duration,
                'context': self.context_data
            }
            
            logger.log(
                self.log_level,
                f"Error en {self.operation}: {exc_val}",
                extra=error_info,
                exc_info=True
            )
            
            # Si no debe re-lanzar, suprimir la excepción
            if not self.raise_on_error:
                return True
        
        return False


async def safe_execute(
    func: Callable,
    *args,
    default_value: Any = None,
    operation_name: Optional[str] = None,
    **kwargs
) -> Any:
    """
    Ejecuta una función de forma segura, capturando errores y retornando un valor por defecto.
    
    Args:
        func: Función a ejecutar
        *args: Argumentos posicionales para la función
        default_value: Valor a retornar si hay error
        operation_name: Nombre de la operación para logging
        **kwargs: Argumentos nombrados para la función
        
    Returns:
        Resultado de la función o default_value si hay error
    """
    operation = operation_name or func.__name__
    
    try:
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        else:
            return func(*args, **kwargs)
    except Exception as e:
        logger.error(
            f"Error en {operation}: {e}",
            exc_info=True
        )
        return default_value


class CircuitBreaker:
    """
    Implementación de patrón Circuit Breaker para prevenir cascadas de fallos.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Type[Exception] = Exception
    ):
        """
        Args:
            failure_threshold: Número de fallos antes de abrir el circuito
            recovery_timeout: Segundos antes de intentar recuperación
            expected_exception: Tipo de excepción a contar como fallo
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half_open
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Ejecuta una función a través del circuit breaker
        
        Args:
            func: Función a ejecutar
            *args: Argumentos posicionales
            **kwargs: Argumentos nombrados
            
        Returns:
            Resultado de la función
            
        Raises:
            Exception: Si el circuito está abierto o la función falla
        """
        if self.state == 'open':
            if self._should_attempt_reset():
                self.state = 'half_open'
                logger.info(f"Circuit breaker en estado half_open, intentando recuperación")
            else:
                raise Exception(
                    f"Circuit breaker abierto, esperando recuperación "
                    f"(fallos: {self.failure_count})"
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    async def call_async(self, func: Callable, *args, **kwargs) -> Any:
        """Versión asíncrona de call"""
        if self.state == 'open':
            if self._should_attempt_reset():
                self.state = 'half_open'
                logger.info(f"Circuit breaker en estado half_open, intentando recuperación")
            else:
                raise Exception(
                    f"Circuit breaker abierto, esperando recuperación "
                    f"(fallos: {self.failure_count})"
                )
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Verifica si debe intentar resetear el circuito"""
        if self.last_failure_time is None:
            return True
        
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout
    
    def _on_success(self):
        """Maneja ejecución exitosa"""
        if self.state == 'half_open':
            logger.info("Circuit breaker recuperado, cerrando circuito")
        
        self.failure_count = 0
        self.state = 'closed'
    
    def _on_failure(self):
        """Maneja fallo de ejecución"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'open'
            logger.error(
                f"Circuit breaker abierto después de {self.failure_count} fallos"
            )
