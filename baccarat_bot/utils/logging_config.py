# baccarat_bot/utils/logging_config.py

"""
Configuración de logging estructurado para el bot de Baccarat.
Proporciona logging en formato JSON y con colores para mejor análisis.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Formateador de logs en formato JSON para análisis estructurado"""
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Formatea un registro de log como JSON
        
        Args:
            record: Registro de log
            
        Returns:
            String JSON con la información del log
        """
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Agregar información de excepción si existe
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Agregar campos extra si existen
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data
        
        return json.dumps(log_data, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """Formateador de logs con colores para terminal"""
    
    # Códigos de color ANSI
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Verde
        'WARNING': '\033[33m',    # Amarillo
        'ERROR': '\033[31m',      # Rojo
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Formatea un registro de log con colores
        
        Args:
            record: Registro de log
            
        Returns:
            String formateado con colores ANSI
        """
        # Obtener color según el nivel
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Formatear el mensaje base
        formatted = super().format(record)
        
        # Aplicar color al nivel
        formatted = formatted.replace(
            record.levelname,
            f"{color}{record.levelname}{reset}"
        )
        
        return formatted


def setup_logging(
    log_level: str = 'INFO',
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
    use_json: bool = False,
    use_colors: bool = True
) -> logging.Logger:
    """
    Configura el sistema de logging del bot
    
    Args:
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Ruta del archivo de log (None para solo consola)
        max_bytes: Tamaño máximo del archivo de log antes de rotar
        backup_count: Número de archivos de backup a mantener
        use_json: Si debe usar formato JSON en archivo
        use_colors: Si debe usar colores en consola
        
    Returns:
        Logger configurado
    """
    # Obtener logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Limpiar handlers existentes
    root_logger.handlers.clear()
    
    # Formato base para logs
    base_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Handler para consola con colores
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    if use_colors and sys.stdout.isatty():
        console_formatter = ColoredFormatter(base_format, datefmt=date_format)
    else:
        console_formatter = logging.Formatter(base_format, datefmt=date_format)
    
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Handler para archivo si se especifica
    if log_file:
        # Crear directorio si no existe
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Handler con rotación
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        
        # Usar formato JSON o texto según configuración
        if use_json:
            file_formatter = JSONFormatter()
        else:
            file_formatter = logging.Formatter(base_format, datefmt=date_format)
        
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    # Reducir verbosidad de librerías externas
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('telegram').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('playwright').setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"✅ Sistema de logging configurado: nivel={log_level}, archivo={log_file}")
    
    return root_logger


class StructuredLogger:
    """
    Logger estructurado que facilita el logging con datos adicionales
    """
    
    def __init__(self, name: str):
        """
        Args:
            name: Nombre del logger
        """
        self.logger = logging.getLogger(name)
    
    def _log_with_data(self, level: int, message: str, **kwargs):
        """
        Registra un mensaje con datos estructurados adicionales
        
        Args:
            level: Nivel de logging
            message: Mensaje a registrar
            **kwargs: Datos adicionales
        """
        extra = {'extra_data': kwargs} if kwargs else {}
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        """Log nivel DEBUG con datos adicionales"""
        self._log_with_data(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log nivel INFO con datos adicionales"""
        self._log_with_data(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log nivel WARNING con datos adicionales"""
        self._log_with_data(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log nivel ERROR con datos adicionales"""
        self._log_with_data(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log nivel CRITICAL con datos adicionales"""
        self._log_with_data(logging.CRITICAL, message, **kwargs)
    
    def log_signal(self, mesa: str, estrategia: str, resultado: str, confianza: int):
        """
        Log especializado para señales de apuesta
        
        Args:
            mesa: Nombre de la mesa
            estrategia: Estrategia utilizada
            resultado: Resultado recomendado
            confianza: Nivel de confianza
        """
        self.info(
            f"🎯 Señal generada: {resultado}",
            mesa=mesa,
            estrategia=estrategia,
            resultado=resultado,
            confianza=confianza,
            tipo='signal'
        )
    
    def log_error_with_context(
        self,
        error: Exception,
        operation: str,
        context: dict
    ):
        """
        Log especializado para errores con contexto
        
        Args:
            error: Excepción capturada
            operation: Operación que falló
            context: Contexto adicional
        """
        self.error(
            f"❌ Error en {operation}: {str(error)}",
            operation=operation,
            error_type=type(error).__name__,
            error_message=str(error),
            context=context,
            tipo='error'
        )
    
    def log_performance(
        self,
        operation: str,
        duration_seconds: float,
        success: bool = True,
        **kwargs
    ):
        """
        Log especializado para métricas de rendimiento
        
        Args:
            operation: Operación ejecutada
            duration_seconds: Duración en segundos
            success: Si la operación fue exitosa
            **kwargs: Datos adicionales
        """
        status = "✅" if success else "❌"
        self.info(
            f"{status} {operation} completado en {duration_seconds:.2f}s",
            operation=operation,
            duration=duration_seconds,
            success=success,
            tipo='performance',
            **kwargs
        )


def get_structured_logger(name: str) -> StructuredLogger:
    """
    Obtiene un logger estructurado
    
    Args:
        name: Nombre del logger
        
    Returns:
        StructuredLogger configurado
    """
    return StructuredLogger(name)
