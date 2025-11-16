# 🤖 Bot de Baccarat Avanzado

Un bot inteligente de monitoreo y análisis para mesas de Baccarat con múltiples estrategias de apuesta, estadísticas en tiempo real, panel web interactivo y bot de Telegram.

## 🌟 Características Principales

### 📊 Estadísticas y Análisis
- **Base de datos SQLite** para almacenar resultados históricos
- **Análisis de tendencias** por mesa con patrones de rachas y alternancias
- **Estadísticas detalladas** con win rates y precisión de señales
- **Reportes automáticos** diarios y semanales

### 🎯 Estrategias de Apuesta
- **Estrategia de Racha** (original): Apuesta contra rachas de 3+
- **Martingale Adaptado**: Sistema de progresión con límites de seguridad
- **Patrón de Alternancia**: Detecta patrones B-P-B-P
- **Secuencia Fibonacci**: Basado en la famosa secuencia matemática
- **Análisis de Tendencias**: Corto y largo plazo con ventanas deslizantes

### 🌐 Panel Web Interactivo
- **Dashboard en tiempo real** con gráficos y estadísticas
- **API REST completa** para integraciones
- **Visualización con Chart.js** de distribución de resultados
- **Tablas dinámicas** con estado de todas las mesas
- **Sistema de alertas** automáticas

### 🤖 Bot de Telegram Interactivo
- **Comandos interactivos**: `/start`, `/stats`, `/mesas`, `/tendencia`, `/historial`
- **Botones inline** para navegación rápida
- **Reportes automáticos** con estadísticas detalladas
- **Alertas personalizadas** basadas en condiciones específicas

### 🔌 Integración con Datos Reales
- **Web scraper para 1xBet** con manejo de rate limiting
- **Sistema de fallback** a simulación si falla
- **Caché de resultados** para optimizar rendimiento
- **Múltiples mesas simultáneas** con procesamiento paralelo

## 🚀 Instalación Rápida

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/baccarat-bot.git
cd baccarat-bot

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales
```

## ⚙️ Configuración

Edita el archivo `.env` con tus credenciales:

```env
# === CREDENCIALES DE TELEGRAM ===
TELEGRAM_BOT_TOKEN=tu_token_aqui
TELEGRAM_CHAT_ID=tu_chat_id_aqui

# === CONFIGURACIÓN DEL MONITOREO ===
INTERVALO_MONITOREO=120
LONGITUD_RACHA=3

# === CONFIGURACIÓN DE LOGGING ===
LOG_LEVEL=INFO

# === CONFIGURACIÓN DE DATOS ===
USAR_DATOS_REALES=false
```

## 📱 Uso

### Opción 1: Bot Básico (Original)
```bash
python main.py
```

### Opción 2: Bot Avanzado (Recomendado)
```bash
python main_advanced.py
```

### Opción 3: Solo API Server
```bash
python api/server.py
```

### Opción 4: Solo Bot Interactivo
```bash
python telegram_bot/interactive_bot.py
```

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

## 📊 API REST

El servidor API proporciona endpoints para acceder a los datos:

### Endpoints Principales

- `GET /` - Dashboard web interactivo
- `GET /api/estadisticas` - Estadísticas de todas las mesas
- `GET /api/estadisticas/{mesa}` - Estadísticas de una mesa específica
- `GET /api/tendencias/{mesa}` - Análisis de tendencias
- `GET /api/reporte-general` - Reporte general completo
- `GET /api/alertas` - Alertas activas
- `GET /api/mesas` - Lista de mesas
- `GET /api/historial/{mesa}` - Historial de resultados
- `POST /api/senales` - Registrar una señal
- `POST /api/resultado` - Registrar un resultado
- `GET /api/health` - Verificación de salud

### Ejemplo de uso
```bash
# Obtener estadísticas
curl http://localhost:5000/api/estadisticas

# Obtener tendencias de una mesa
curl http://localhost:5000/api/tendencias/Speed%20Baccarat%201

# Registrar un resultado
curl -X POST http://localhost:5000/api/resultado \
  -H "Content-Type: application/json" \
  -d '{"mesa": "Speed Baccarat 1", "resultado": "B"}'
```

## 🎯 Estrategias de Apuesta

### 1. Racha de 3 (Por defecto)
- **Descripción**: Apuesta contra la racha después de 3 victorias consecutivas
- **Señal**: Si hay 3 bancas seguidas → apuesta a Jugador
- **Señal**: Si hay 3 jugadores seguidos → apuesta a Banca
- **Confianza**: 70-80%

### 2. Martingale Adaptado
- **Descripción**: Sistema de progresión con límites de seguridad
- **Señal**: Después de pérdidas consecutivas, aumenta la apuesta
- **Límite**: Máximo 5 progresiones
- **Confianza**: 60%

### 3. Patrón de Alternancia
- **Descripción**: Detecta patrones B-P-B-P
- **Señal**: Predice el siguiente resultado en la alternancia
- **Confianza**: 75%

### 4. Secuencia Fibonacci
- **Descripción**: Basado en la secuencia matemática
- **Señal**: Identifica patrones de repetición
- **Confianza**: 65%

### 5. Análisis de Tendencias
- **Descripción**: Análisis de corto y largo plazo
- **Señal**: Confirma tendencias en múltiples ventanas de tiempo
- **Confianza**: 70-85%

## 🗄️ Base de Datos

La base de datos SQLite almacena:

### Tablas principales:
- **mesas**: Información de las mesas monitoreadas
- **resultados**: Historial de resultados por mesa
- **senales**: Registro de señales generadas
- **estadisticas**: Estadísticas agregadas por mesa
- **estrategias**: Configuración de estrategias

### Consultas útiles:
```sql
-- Top 5 mesas más activas
SELECT m.nombre, e.total_jugadas, e.senales_generadas
FROM estadisticas e
JOIN mesas m ON e.mesa_id = m.id
ORDER BY e.total_jugadas DESC
LIMIT 5;

-- Precisión de señales por mesa
SELECT m.nombre, 
       e.senales_generadas,
       e.senales_acertadas,
       (e.senales_acertadas * 100.0 / e.senales_generadas) as precision
FROM estadisticas e
JOIN mesas m ON e.mesa_id = m.id
WHERE e.senales_generadas > 10
ORDER BY precision DESC;
```

## 🔧 Desarrollo y Personalización

### Agregar una nueva estrategia
```python
from strategies.advanced_strategies import BettingStrategy

class MiEstrategia(BettingStrategy):
    def analyze(self, history):
        # Tu lógica de análisis
        pass
    
    def get_confidence_level(self, history):
        # Calcular nivel de confianza
        pass

# Registrar la estrategia
strategy_manager.strategies['mi_estrategia'] = MiEstrategia()
```

### Personalizar el dashboard web
Edita el template HTML en `api/server.py` o crea un archivo separado.

### Integrar con otros casinos
Modifica `integrations/web_scraper.py` para adaptar a otros sitios web.

## 🧪 Testing

```bash
# Ejecutar pruebas (si están implementadas)
python -m pytest tests/

# Probar el scraper individualmente
python -c "from integrations.web_scraper import data_source_manager; import asyncio; asyncio.run(data_source_manager.init()); print('Scraper funcionando')"
```

## 📈 Monitoreo y Logs

Los logs se guardan en `baccarat_bot.log` con niveles configurables:
- `DEBUG`: Información detallada de desarrollo
- `INFO`: Información general de operación
- `WARNING`: Advertencias de posibles problemas
- `ERROR`: Errores que requieren atención

## 🔒 Seguridad

- **Tokens seguros**: Almacenados en variables de entorno
- **Rate limiting**: En requests al casino
- **Validación de datos**: Entrada y salida de APIs
- **Logs sin datos sensibles**: Tokens y credenciales ofuscados

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## ⚠️ Disclaimer

Este bot es para fines educativos y de entretenimiento. El juego puede ser adictivo. Por favor, juega responsablemente y nunca apuestes más de lo que puedas permitirte perder.

## 🆘 Soporte

Si tienes problemas o preguntas:
1. Revisa los logs en `baccarat_bot.log`
2. Verifica tu configuración en `.env`
3. Asegúrate de tener todas las dependencias instaladas
4. Crea un issue en el repositorio

---

**¡Disfruta de tu Bot de Baccarat Avanzado! 🎰🤖**