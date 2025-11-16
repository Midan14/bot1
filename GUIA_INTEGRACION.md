# 📘 Guía de Integración de Mejoras - Bot de Baccarat

## Objetivo
Esta guía proporciona instrucciones paso a paso para integrar las mejoras implementadas en el código existente del bot de Baccarat.

---

## 📋 Pre-requisitos

1. ✅ Backup del código actual
2. ✅ Entorno virtual de Python configurado
3. ✅ Git instalado para control de versiones

---

## 🚀 Paso 1: Instalar Dependencias

### 1.1 Instalar todas las dependencias

```bash
# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Instalar Playwright
playwright install chromium
```

### 1.2 Verificar instalación

```bash
# Verificar pytest
pytest --version

# Verificar pydantic
python -c "import pydantic; print(pydantic.__version__)"
```

---

## 🔧 Paso 2: Integrar Validadores

### 2.1 Importar validadores en database/models.py

```python
# Agregar al inicio del archivo
from baccarat_bot.utils.validators import (
    validar_mesa_data,
    validar_resultado,
    validar_senal
)

# En la función registrar_resultado
def registrar_resultado(self, mesa_nombre: str, resultado: str):
    # Validar antes de registrar
    resultado_validado = validar_resultado(mesa_nombre, resultado)
    
    # Continuar con lógica existente...
```

### 2.2 Validar datos de mesas al inicializar

```python
# En tables.py o donde se inicializan las mesas
from baccarat_bot.utils.validators import validar_mesa_data

def inicializar_mesas():
    mesas = {}
    for nombre in MESA_NOMBRES:
        mesa_data = {
            'nombre': nombre,
            'url': f"{BASE_URL}{nombre}",
            'game_id': extraer_game_id(nombre),
            'historial_resultados': []
        }
        
        # Validar antes de agregar
        try:
            mesa_validada = validar_mesa_data(mesa_data)
            mesas[nombre] = mesa_validada.dict()
        except ValidationError as e:
            logger.error(f"Mesa inválida {nombre}: {e}")
            continue
    
    return mesas
```

---

## 🧠 Paso 3: Integrar PagePool

### 3.1 Modificar integrations/playwright_scraper.py

```python
# Agregar importación
from baccarat_bot.utils.page_pool import PagePool

class PlaywrightScraper:
    def __init__(self):
        self.browser = None
        self.page_pool = None  # Nuevo
    
    async def init(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        
        # Inicializar PagePool
        self.page_pool = PagePool(
            browser=self.browser,
            max_pages=10,
            idle_timeout_minutes=5
        )
        await self.page_pool.start()
    
    async def scrape_table(self, table_id: str, url: str):
        # Obtener página del pool (en lugar de crear nueva)
        page = await self.page_pool.get_page(table_id, url)
        
        try:
            # Lógica de scraping existente...
            result = await extract_data(page)
            return result
        finally:
            # No cerrar la página, el pool la reutilizará
            pass
    
    async def close(self):
        # Detener el pool antes de cerrar el navegador
        if self.page_pool:
            await self.page_pool.stop()
        
        if self.browser:
            await self.browser.close()
        
        if self.playwright:
            await self.playwright.stop()
```

---

## ⚙️ Paso 4: Migrar a Configuración Unificada

### 4.1 Actualizar imports en archivos principales

```python
# Reemplazar:
# from baccarat_bot.config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, ...

# Por:
from baccarat_bot.config_unified import (
    config,
    TELEGRAM_TOKEN,
    TELEGRAM_CHAT_ID,
    INTERVALO_MONITOREO,
    # ... otros
)

# O usar directamente el objeto config:
telegram_token = config.telegram.token
intervalo = config.monitoring.intervalo_monitoreo
```

### 4.2 Validar configuración al inicio

```python
# En main_advanced.py o main.py, al inicio
from baccarat_bot.config_unified import config

def main():
    try:
        # Validar toda la configuración
        config.validate_all()
        logger.info("✅ Configuración validada correctamente")
    except ValueError as e:
        logger.critical(f"❌ Error en configuración: {e}")
        sys.exit(1)
    
    # Continuar con inicialización...
```

---

## 🛡️ Paso 5: Agregar Manejo de Errores

### 5.1 Decorar funciones críticas con @retry_on_error

```python
from baccarat_bot.utils.error_handler import retry_on_error, RetryConfig

# En funciones de scraping
@retry_on_error(RetryConfig(
    max_retries=3,
    initial_delay=2.0,
    exceptions=(TimeoutError, ConnectionError)
))
async def scrape_table_data(url: str):
    # Lógica de scraping...
    pass

# En funciones de Telegram
@retry_on_error(RetryConfig(
    max_retries=2,
    initial_delay=1.0,
    exceptions=(TelegramError,)
))
async def send_telegram_message(message: str):
    # Lógica de envío...
    pass
```

### 5.2 Usar ErrorContext para operaciones críticas

```python
from baccarat_bot.utils.error_handler import ErrorContext

async def procesar_mesa(nombre_mesa: str, mesa_data: dict):
    with ErrorContext(
        operation='procesar_mesa',
        context_data={'mesa': nombre_mesa},
        raise_on_error=False  # No detener el bot por un error
    ):
        # Lógica de procesamiento...
        resultado = await obtener_resultado(mesa_data)
        await analizar_señales(resultado)
```

### 5.3 Implementar Circuit Breaker para scraping

```python
from baccarat_bot.utils.error_handler import CircuitBreaker

# Crear circuit breaker global
scraping_circuit = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60.0
)

async def scrape_with_circuit_breaker(url: str):
    try:
        result = await scraping_circuit.call_async(
            scrape_function,
            url
        )
        return result
    except Exception as e:
        logger.error(f"Circuit breaker abierto: {e}")
        # Usar datos simulados como fallback
        return simulate_data()
```

---

## 📝 Paso 6: Implementar Logging Estructurado

### 6.1 Configurar logging al inicio

```python
# En main_advanced.py o main.py
from baccarat_bot.utils.logging_config import setup_logging

def main():
    # Configurar logging estructurado
    setup_logging(
        log_level='INFO',
        log_file='baccarat_bot.log',
        use_json=True,  # JSON para producción
        use_colors=True  # Colores para desarrollo
    )
    
    # Continuar con inicialización...
```

### 6.2 Usar StructuredLogger en módulos

```python
# En cualquier módulo
from baccarat_bot.utils.logging_config import get_structured_logger

logger = get_structured_logger(__name__)

# Log con datos estructurados
logger.info(
    'Procesando mesa',
    mesa='Speed Baccarat 1',
    jugadas=100,
    señales=5
)

# Log especializado de señal
logger.log_signal(
    mesa='Speed Baccarat 1',
    estrategia='Racha',
    resultado='BANCA',
    confianza=85
)

# Log de error con contexto
try:
    result = risky_operation()
except Exception as e:
    logger.log_error_with_context(
        error=e,
        operation='risky_operation',
        context={'param1': value1}
    )
```

---

## ✅ Paso 7: Ejecutar Tests

### 7.1 Ejecutar todos los tests

```bash
# Tests completos
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=baccarat_bot --cov-report=html

# Ver reporte de cobertura
open htmlcov/index.html  # Linux/Mac
# o
start htmlcov/index.html  # Windows
```

### 7.2 Agregar tests para nuevo código

```python
# tests/test_mi_modulo.py
import pytest
from baccarat_bot.mi_modulo import mi_funcion

def test_mi_funcion():
    result = mi_funcion('input')
    assert result == 'expected_output'
```

---

## 🔄 Paso 8: Actualizar Código Existente Gradualmente

### Prioridad Alta
1. ✅ Integrar PagePool en scraping
2. ✅ Agregar validadores en puntos de entrada de datos
3. ✅ Decorar funciones críticas con @retry_on_error

### Prioridad Media
4. ✅ Migrar a config_unified.py
5. ✅ Implementar logging estructurado
6. ✅ Agregar tests para módulos existentes

### Prioridad Baja
7. ✅ Refactorizar código antiguo
8. ✅ Optimizar queries de base de datos
9. ✅ Mejorar documentación inline

---

## 🧪 Paso 9: Verificación Final

### 9.1 Checklist de integración

- [ ] Todas las dependencias instaladas
- [ ] Validadores integrados en puntos críticos
- [ ] PagePool funcionando en scraping
- [ ] Configuración unificada en uso
- [ ] Manejo de errores implementado
- [ ] Logging estructurado configurado
- [ ] Tests pasando (45/45)
- [ ] Documentación actualizada

### 9.2 Prueba de integración completa

```bash
# 1. Verificar sintaxis
python -m py_compile baccarat_bot/**/*.py

# 2. Ejecutar tests
pytest tests/ -v

# 3. Ejecutar bot en modo de prueba
python baccarat_bot/main_advanced.py --test-mode

# 4. Verificar logs
tail -f baccarat_bot.log
```

---

## 🚨 Solución de Problemas

### Problema: ImportError al importar validadores

**Solución:**
```bash
# Verificar que pydantic esté instalado
pip install pydantic

# Verificar estructura de directorios
ls -la baccarat_bot/utils/validators.py
```

### Problema: Tests fallan con ModuleNotFoundError

**Solución:**
```bash
# Agregar directorio raíz al PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# O ejecutar desde el directorio raíz
cd /path/to/bot1
pytest tests/
```

### Problema: PagePool no cierra páginas

**Solución:**
```python
# Asegurarse de llamar a stop() al finalizar
try:
    await page_pool.start()
    # ... usar el pool ...
finally:
    await page_pool.stop()
```

---

## 📚 Recursos Adicionales

- **Documentación de Pydantic:** https://docs.pydantic.dev/
- **Documentación de Pytest:** https://docs.pytest.org/
- **Documentación de Playwright:** https://playwright.dev/python/

---

## 🎯 Próximos Pasos

1. **Monitorear en producción**
   - Revisar logs estructurados
   - Verificar uso de memoria
   - Analizar métricas de rendimiento

2. **Optimizar según datos reales**
   - Ajustar timeouts
   - Afinar configuración de PagePool
   - Optimizar estrategias

3. **Expandir funcionalidad**
   - Agregar más tests
   - Implementar caché con Redis
   - Mejorar dashboard web

---

**¡Integración exitosa! 🎉**

*Guía creada por Manus AI*  
*Fecha: 16 de Noviembre de 2025*
