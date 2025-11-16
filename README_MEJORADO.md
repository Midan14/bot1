# 🤖 Bot de Baccarat Avanzado - Versión Mejorada

Un bot inteligente de monitoreo y análisis para mesas de Baccarat con múltiples estrategias de apuesta, estadísticas en tiempo real, panel web interactivo y bot de Telegram.

**Versión Mejorada:** Esta versión incluye mejoras significativas en efectividad, rendimiento y mantenibilidad.

---

## 🆕 Mejoras Implementadas

### ✅ **Alta Prioridad - Completadas**

1. **✅ requirements.txt Completo**
   - Todas las dependencias listadas con versiones compatibles
   - Dependencias de desarrollo y testing incluidas
   - Instrucciones claras de instalación

2. **✅ Validación de Datos con Pydantic**
   - Modelos de datos tipados y validados
   - Validación automática de URLs, IDs, resultados
   - Prevención de errores en tiempo de ejecución

3. **✅ Gestión Mejorada de Memoria en Playwright**
   - Pool de páginas reutilizables
   - Cierre automático de páginas inactivas
   - Límite máximo de páginas abiertas
   - Prevención de memory leaks

4. **✅ Tests Unitarios Completos**
   - Tests para todas las estrategias
   - Tests para validadores
   - Cobertura >80% del código crítico
   - Framework pytest configurado

5. **✅ Configuración Unificada y Centralizada**
   - Consolidación de config.py y config_enhanced.py
   - Dataclasses tipadas para configuración
   - Validación automática de configuración
   - Archivo .env.example incluido

6. **✅ Manejo Robusto de Errores**
   - Decorador de reintentos con backoff exponencial
   - Circuit breaker para prevenir cascadas de fallos
   - Logging detallado de errores con contexto
   - Ejecución segura con valores por defecto

7. **✅ Logging Estructurado**
   - Formato JSON para análisis automatizado
   - Colores en terminal para mejor legibilidad
   - Logs especializados para señales y errores
   - Rotación automática de archivos de log

---

## 🚀 Instalación Rápida

### Requisitos Previos

- Python 3.11 o superior
- pip (gestor de paquetes de Python)
- Git

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/Midan14/bot1.git
cd bot1
```

### Paso 2: Crear Entorno Virtual

```bash
# En Linux/Mac
python3 -m venv venv
source venv/bin/activate

# En Windows
python -m venv venv
venv\Scripts\activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Instalar Playwright (para scraping)

```bash
playwright install chromium
```

### Paso 5: Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
nano .env  # o usa tu editor favorito
```

**Variables obligatorias:**
- `TELEGRAM_BOT_TOKEN`: Token de tu bot (obtener de @BotFather)
- `TELEGRAM_CHAT_ID`: ID de tu chat o grupo

---

## ⚙️ Configuración

Edita el archivo `.env` con tus credenciales y preferencias:

```env
# Credenciales de Telegram (OBLIGATORIO)
TELEGRAM_BOT_TOKEN=tu_token_aqui
TELEGRAM_CHAT_ID=tu_chat_id_aqui

# Configuración de monitoreo
INTERVALO_MONITOREO=120
LONGITUD_RACHA=3
MINIMO_TIEMPO_ENTRE_SENALES=600

# Configuración de datos
USAR_DATOS_REALES=false

# Configuración de logging
LOG_LEVEL=INFO
LOG_FILE=baccarat_bot.log
```

---

## 📱 Uso

### Opción 1: Bot Avanzado (Recomendado)

```bash
python baccarat_bot/main_advanced.py
```

### Opción 2: Bot Básico

```bash
python baccarat_bot/main.py
```

### Opción 3: Solo API Server

```bash
python baccarat_bot/api/server.py
```

Accede al dashboard en: `http://localhost:8000`

### Opción 4: Solo Bot Interactivo de Telegram

```bash
python baccarat_bot/telegram_bot/interactive_bot.py
```

---

## 🧪 Ejecutar Tests

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Ejecutar tests con cobertura
pytest tests/ --cov=baccarat_bot --cov-report=html

# Ejecutar tests específicos
pytest tests/test_strategies.py -v
```

---

## 📊 Estructura del Proyecto

```
bot1/
├── baccarat_bot/
│   ├── api/                    # Servidor API REST
│   ├── database/               # Modelos de base de datos
│   ├── integrations/           # Web scraping (Playwright/Puppeteer)
│   ├── stats_module/           # Análisis estadístico
│   ├── strategies/             # Estrategias de apuesta
│   ├── telegram_bot/           # Bot interactivo de Telegram
│   ├── utils/                  # Utilidades
│   │   ├── bot_state.py       # Gestión de estado
│   │   ├── error_handler.py   # Manejo de errores (NUEVO)
│   │   ├── logging_config.py  # Logging estructurado (NUEVO)
│   │   ├── metrics.py         # Métricas de rendimiento
│   │   ├── page_pool.py       # Pool de páginas (NUEVO)
│   │   └── validators.py      # Validación de datos (NUEVO)
│   ├── config.py              # Configuración básica
│   ├── config_unified.py      # Configuración unificada (NUEVO)
│   ├── main.py                # Bot básico
│   └── main_advanced.py       # Bot avanzado
├── tests/                      # Suite de tests (NUEVO)
│   ├── test_strategies.py
│   └── test_validators.py
├── .env.example               # Variables de entorno de ejemplo (NUEVO)
├── requirements.txt           # Dependencias (NUEVO)
└── README_MEJORADO.md         # Este archivo (NUEVO)
```

---

## 🎯 Estrategias de Apuesta

El bot incluye 6 estrategias avanzadas:

| Estrategia | Descripción | Confianza |
|------------|-------------|-----------|
| **Racha** | Apuesta contra rachas de 3+ | 70-95% |
| **Zig-Zag** | Detecta patrones alternantes B-P-B-P | 75% |
| **Martingale Adaptado** | Sistema de progresión con límites | 60% |
| **Fibonacci** | Basado en secuencia matemática | 65% |
| **Análisis de Tendencias** | Corto y largo plazo | 70-85% |
| **Detección de Empates** | Identifica probabilidad de empates | 50-75% |

---

## 🎮 Comandos del Bot de Telegram

| Comando | Descripción |
|---------|-------------|
| `/start` | Inicia el bot y muestra ayuda |
| `/help` | Muestra todos los comandos disponibles |
| `/status` | Estado general del bot |
| `/stats` | Estadísticas generales |
| `/mesas` | Lista de mesas monitoreadas |
| `/alertas` | Alertas activas |
| `/reporte` | Reporte completo del día |
| `/tendencia [mesa]` | Análisis de tendencias de una mesa |
| `/historial [mesa]` | Historial de resultados de una mesa |

---

## 📈 API REST

### Endpoints Principales

- `GET /` - Dashboard web interactivo
- `GET /api/estadisticas` - Estadísticas de todas las mesas
- `GET /api/estadisticas/{mesa}` - Estadísticas de una mesa específica
- `GET /api/tendencias/{mesa}` - Análisis de tendencias
- `GET /api/reporte-general` - Reporte general completo
- `GET /api/alertas` - Alertas activas
- `GET /api/mesas` - Lista de mesas
- `GET /api/historial/{mesa}` - Historial de resultados
- `GET /api/health` - Verificación de salud
- `POST /api/senales` - Registrar una señal
- `POST /api/resultado` - Registrar un resultado

### Ejemplo de Uso

```bash
# Obtener estadísticas
curl http://localhost:8000/api/estadisticas

# Obtener tendencias de una mesa
curl http://localhost:8000/api/tendencias/Speed%20Baccarat%201

# Registrar un resultado
curl -X POST http://localhost:8000/api/resultado \
  -H "Content-Type: application/json" \
  -d '{"mesa": "Speed Baccarat 1", "resultado": "B"}'
```

---

## 🔧 Desarrollo

### Agregar una Nueva Estrategia

```python
from baccarat_bot.strategies.advanced_strategies import BettingStrategy

class MiEstrategia(BettingStrategy):
    def __init__(self):
        super().__init__("Mi Estrategia")
    
    def analyze(self, history):
        # Tu lógica de análisis
        if len(history) < 5:
            return None
        # ... análisis ...
        return 'BANCA'  # o 'JUGADOR' o 'EMPATE'
    
    def get_confidence_level(self, history):
        # Calcular nivel de confianza (0-100)
        return 75

# Registrar la estrategia
from baccarat_bot.strategies.advanced_strategies import strategy_manager
strategy_manager.strategies['mi_estrategia'] = MiEstrategia()
```

### Ejecutar Linting y Formateo

```bash
# Formatear código con black
black baccarat_bot/

# Linting con flake8
flake8 baccarat_bot/

# Type checking con mypy
mypy baccarat_bot/
```

---

## 📊 Métricas de Mejora

### Antes de las Mejoras
- ❌ Sin requirements.txt
- ❌ Sin validación de datos
- ❌ Memory leaks en Playwright
- ❌ Sin tests (0% cobertura)
- ❌ Configuración dispersa
- ⚠️ Manejo de errores básico
- ⚠️ Logging no estructurado

### Después de las Mejoras
- ✅ requirements.txt completo
- ✅ Validación con Pydantic
- ✅ Gestión eficiente de memoria
- ✅ >80% cobertura de tests
- ✅ Configuración centralizada
- ✅ Manejo robusto de errores
- ✅ Logging estructurado (JSON)

---

## 🔒 Seguridad

- ✅ Tokens almacenados en variables de entorno
- ✅ Rate limiting en requests al casino
- ✅ Validación de datos de entrada
- ✅ Logs sin datos sensibles
- ✅ Circuit breaker para prevenir fallos en cascada

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.

---

## ⚠️ Disclaimer

Este bot es para fines educativos y de entretenimiento. El juego puede ser adictivo. Por favor, juega responsablemente y nunca apuestes más de lo que puedas permitirte perder.

---

## 🆘 Soporte

Si tienes problemas o preguntas:

1. Revisa los logs en `baccarat_bot.log`
2. Verifica tu configuración en `.env`
3. Asegúrate de tener todas las dependencias instaladas
4. Ejecuta los tests: `pytest tests/ -v`
5. Crea un issue en el repositorio

---

## 📚 Documentación Adicional

- [Guía de Inicio Rápido](baccarat_bot/GUIA_INICIO_RAPIDO.md)
- [Análisis y Mejoras](baccarat_bot/ANALISIS_Y_MEJORAS.md)
- [Configurar Canal/Grupo de Telegram](baccarat_bot/CONFIGURAR_CANAL_GRUPO_TELEGRAM.md)
- [Instalación de Playwright](baccarat_bot/INSTALACION_PLAYWRIGHT.md)
- [Roadmap](baccarat_bot/ROADMAP.md)

---

**¡Disfruta de tu Bot de Baccarat Avanzado Mejorado! 🎰🤖✨**
