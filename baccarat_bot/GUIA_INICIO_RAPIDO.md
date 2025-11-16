# 🚀 Guía de Inicio Rápido - Bot de Baccarat

## ✅ Sistema Completamente Implementado

Tu bot de Baccarat ahora incluye **todas las 4 fases principales**:

### ✨ Funcionalidades Implementadas

#### 📊 **Fase 1: Fundamentos y Estadísticas**

- ✅ Base de datos SQLite completa
- ✅ Sistema de estadísticas detalladas por mesa
- ✅ Análisis de tendencias y patrones
- ✅ Detección automática de rachas
- ✅ Reportes automáticos

#### 🌐 **Fase 2: Panel de Control Web**

- ✅ API REST completa con Flask
- ✅ Dashboard interactivo en tiempo real
- ✅ Gráficos con Chart.js
- ✅ Endpoints para todas las funcionalidades
- ✅ Sistema de alertas automáticas

#### 🎯 **Fase 3: Estrategias Avanzadas**

- ✅ 5 estrategias de apuesta implementadas:
  1. **Racha de N** - Apuesta contra rachas largas
  2. **Zig-Zag** - Detecta alternancias B-P-B-P
  3. **Martingale Adaptado** - Sistema de progresión
  4. **Fibonacci** - Basado en secuencia matemática
  5. **Análisis de Tendencias** - Corto y largo plazo
- ✅ Sistema de consenso entre estrategias
- ✅ Niveles de confianza por señal
- ✅ Gestor de estrategias extensible

#### 🔌 **Fase 4: Integración de Datos Reales**

- ✅ Web scraper para 1xBet
- ✅ Manejo de rate limiting
- ✅ Sistema de caché inteligente
- ✅ Fallback automático a simulación
- ✅ Soporte para múltiples mesas

---

## 🛠️ Instalación y Configuración

### 1. Verificar Dependencias Instaladas

Todas las dependencias ya fueron instaladas:

```bash
✅ python-telegram-bot (22.5)
✅ python-dotenv (1.2.1)
✅ beautifulsoup4 (4.14.2)
✅ flask
✅ flask-cors
✅ numpy
✅ requests
✅ aiohttp
✅ lxml
```

### 2. Configuración del .env

Tu archivo `.env` ya está configurado con:

```env
TELEGRAM_BOT_TOKEN=8235077057:AAGSHsr_su_TbjlcWehdlIrwr8Kn1XXID6o
TELEGRAM_CHAT_ID=631443236
INTERVALO_MONITOREO=120
LONGITUD_RACHA=3
MINIMO_TIEMPO_ENTRE_SENALES=600
LOG_LEVEL=INFO
LOG_FILE=baccarat_bot.log
USAR_DATOS_REALES=false
```

### 3. Inicializar el Sistema

Ejecuta el script de inicialización para configurar todo:

```bash
cd baccarat_bot
python init_system.py
```

Este script:

- ✅ Inicializa la base de datos SQLite
- ✅ Registra todas las 60 mesas de Baccarat
- ✅ Verifica que las 5 estrategias funcionen
- ✅ Prueba el web scraper
- ✅ Genera datos de prueba
- ✅ Muestra un reporte inicial

---

## 🎮 Formas de Ejecutar el Bot

### Opción 1: Bot Básico (Original)

```bash
python main.py
```

- Monitoreo simple de mesas
- Estrategia de racha básica
- Envío de señales a Telegram

### Opción 2: Bot Avanzado (Recomendado) ⭐

```bash
python main_advanced.py
```

- Todas las 5 estrategias activas
- Sistema de consenso
- Estadísticas avanzadas
- Base de datos integrada

### Opción 3: Panel Web Interactivo 🌐

```bash
python api/server.py
```

Luego abre en tu navegador: <http://localhost:5000>

**Dashboard incluye:**

- 📊 Estadísticas en tiempo real
- 📈 Gráficos de distribución
- 🏆 Top mesas más activas
- ⚠️ Sistema de alertas
- 📋 Tablas con todas las mesas

### Opción 4: Bot de Telegram Interactivo 🤖

```bash
python telegram_bot/interactive_bot.py
```

**Comandos disponibles:**

- `/start` - Inicia el bot
- `/stats` - Estadísticas generales
- `/mesas` - Lista de mesas
- `/tendencia [mesa]` - Análisis de tendencias
- `/historial [mesa]` - Historial de resultados
- `/alertas` - Alertas activas
- `/reporte` - Reporte completo

---

## 📡 API REST Endpoints

### Endpoints Principales

**Estadísticas**

```bash
GET /api/estadisticas              # Todas las mesas
GET /api/estadisticas/{mesa}       # Mesa específica
GET /api/reporte-general           # Reporte completo
```

**Análisis**

```bash
GET /api/tendencias/{mesa}         # Tendencias de una mesa
GET /api/alertas                   # Alertas activas
GET /api/historial/{mesa}          # Historial de resultados
```

**Gestión**

```bash
GET /api/mesas                     # Lista de mesas
POST /api/resultado                # Registrar resultado
POST /api/senales                  # Registrar señal
GET /api/health                    # Estado del servicio
```

### Ejemplos de Uso

```bash
# Obtener estadísticas generales
curl http://localhost:5000/api/estadisticas

# Obtener tendencias de una mesa
curl http://localhost:5000/api/tendencias/Speed%20Baccarat%201

# Registrar un resultado
curl -X POST http://localhost:5000/api/resultado \
  -H "Content-Type: application/json" \
  -d '{"mesa": "Speed Baccarat 1", "resultado": "B"}'

# Obtener reporte general
curl http://localhost:5000/api/reporte-general
```

---

## 🔍 Verificar que Todo Funciona

### Test Rápido

```bash
# Probar el bot por 5 segundos
python test_startup.py
```

### Ver Logs

```bash
# Ver logs en tiempo real
tail -f baccarat_bot.log
```

### Consultar Base de Datos

```bash
# Abrir base de datos
sqlite3 baccarat_data.db

# Consultas útiles
SELECT COUNT(*) FROM mesas;
SELECT COUNT(*) FROM resultados;
SELECT * FROM estadisticas LIMIT 5;
```

---

## 📊 Estructura de Archivos Actualizada

```
baccarat_bot/
├── main.py                      # Bot básico
├── main_advanced.py             # Bot avanzado ⭐
├── init_system.py               # Script de inicialización ✨
├── config.py                    # Configuración (actualizado) ✅
├── tables.py                    # 60 mesas configuradas
├── signal_logic.py              # Lógica de señales
├── data_source.py               # Fuente de datos
├── test_startup.py              # Test de arranque
├── baccarat_data.db             # Base de datos SQLite
├── .env                         # Variables de entorno ✅
├── requirements.txt             # Dependencias
├── README.md                    # Documentación completa
├── ROADMAP.md                   # Hoja de ruta
├── GUIA_INICIO_RAPIDO.md        # Esta guía ✨
│
├── database/
│   ├── __init__.py
│   └── models.py                # Modelos de BD (completo) ✅
│
├── statistics/
│   ├── __init__.py
│   └── analyzer.py              # Análisis estadístico (completo) ✅
│
├── strategies/
│   ├── __init__.py
│   └── advanced_strategies.py   # 5 estrategias (completo) ✅
│
├── integrations/
│   ├── __init__.py
│   └── web_scraper.py           # Scraper 1xBet (completo) ✅
│
├── api/
│   ├── __init__.py
│   └── server.py                # API REST + Dashboard (completo) ✅
│
└── telegram_bot/
    ├── __init__.py
    └── interactive_bot.py       # Bot interactivo
```

---

## 🎯 Estrategias Implementadas - Detalles

### 1. Racha de N (Streak Strategy)

- **Descripción**: Apuesta contra rachas de 3+ resultados iguales
- **Señal**: Si hay BBB → Apuesta a JUGADOR
- **Confianza**: 70-95% (aumenta con rachas más largas)

### 2. Zig-Zag

- **Descripción**: Detecta patrones B-P-B-P
- **Señal**: Continúa el patrón alternante
- **Confianza**: 75%

### 3. Martingale Adaptado

- **Descripción**: Sistema de progresión con límites
- **Señal**: Apuesta a favor de tendencia dominante
- **Confianza**: 60%

### 4. Fibonacci

- **Descripción**: Basado en secuencia matemática
- **Señal**: Identifica patrones de repetición
- **Confianza**: 65%

### 5. Análisis de Tendencias

- **Descripción**: Analiza corto (5) y largo plazo (15)
- **Señal**: Cuando ambas tendencias coinciden
- **Confianza**: 70-85%

### Sistema de Consenso

- Combina las 5 estrategias
- Vota ponderado por confianza
- Solo genera señal si ≥50% confianza
- Indica cuántas estrategias están de acuerdo

---

## 🐛 Solución de Problemas

### Error: "TELEGRAM_BOT_TOKEN no está configurado"

```bash
# Verifica que el archivo .env exista y tenga el token correcto
cat .env
```

### Error: "No module named 'flask'"

```bash
# Reinstala las dependencias
pip install -r requirements.txt
```

### Error: Base de datos bloqueada

```bash
# Cierra todos los procesos que usen la BD
pkill -f python
# O reinicia el sistema
```

### El bot no envía mensajes

1. Verifica el token de Telegram
2. Asegúrate de que el chat_id es correcto
3. Revisa los logs: `tail -f baccarat_bot.log`

---

## 📈 Próximas Mejoras Sugeridas

- [ ] Implementar tests automatizados
- [ ] Agregar autenticación al API
- [ ] Integrar WebSockets para actualización en tiempo real
- [ ] Implementar sistema de backtesting
- [ ] Agregar más estrategias personalizadas
- [ ] Mejorar scraper con Selenium/Playwright
- [ ] Sistema de notificaciones por email
- [ ] Panel de administración avanzado

---

## 📝 Notas Importantes

⚠️ **Disclaimer**: Este bot es para fines educativos. El juego puede ser adictivo. Juega responsablemente.

✅ **Estado Actual**: Sistema completamente funcional con las 4 fases implementadas

🔧 **Modo Actual**: Simulación (USAR_DATOS_REALES=false)

- Para usar datos reales, cambia en .env: `USAR_DATOS_REALES=true`
- Ten en cuenta que el scraping de 1xBet puede requerir ajustes según su estructura

---

## 🆘 Soporte

Si tienes problemas:

1. Revisa los logs: `baccarat_bot.log`
2. Verifica la configuración en `.env`
3. Ejecuta `python init_system.py` para verificar el sistema
4. Consulta el README.md completo

---

**¡Tu Bot de Baccarat está listo para usar! 🎉**
