# 🚀 Guía de Inicio Rápido - Bot de Baccarat Mejorado

## ⚡ Instalación en 5 Minutos

### 1. Preparar Entorno

```bash
# Clonar repositorio
cd /home/ubuntu/bot1

# Crear entorno virtual
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar navegadores
playwright install chromium
```

### 2. Configurar Credenciales

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar con tus credenciales
nano .env
```

**Contenido de .env:**
```bash
TELEGRAM_TOKEN=tu_token_de_telegram_aqui
TELEGRAM_CHAT_ID=tu_chat_id_aqui
```

### 3. Ejecutar Bot

```bash
# Ejecutar bot mejorado
python baccarat_bot/main_enhanced.py
```

---

## 🎯 Características Principales

### ✅ Anti-Detección Avanzada
- Evita bloqueos de sitios web
- Simula comportamiento humano
- Rotación automática de identidad

### ✅ Sincronización en Tiempo Real
- Detecta estado del juego
- Timing perfecto (15-25s restantes)
- Actualización cada 2 segundos

### ✅ Estrategias Ultra-Seguras
- Confianza mínima: 80%
- 5 estrategias conservadoras
- Consenso de múltiples análisis

### ✅ Gestión Eficiente
- PagePool para memoria
- Caché inteligente
- Limpieza automática

---

## 📊 Verificar Funcionamiento

### Ejecutar Tests

```bash
# Todos los tests (80 tests)
pytest tests/ -v

# Solo estrategias seguras (23 tests)
pytest tests/test_safe_strategies.py -v

# Solo integraciones (12 tests)
pytest tests/test_integrations.py -v
```

**Resultado Esperado:** ✅ 80/80 tests pasados

---

## 🔧 Configuración Rápida

### Ajustar Intervalo de Monitoreo

```python
# En config_unified.py
class MonitoringConfig:
    intervalo_monitoreo: int = 30  # Cambiar a 60 para menos frecuencia
```

### Cambiar Mesas Monitoreadas

```python
# En main_enhanced.py
self.mesa_configs = [
    {
        'name': 'Speed Baccarat 1',
        'url': 'https://col.1xbet.com/speed-baccarat-1',
        'game_id': '97408'
    },
    # Agregar más mesas aquí
]
```

### Ajustar Confianza Mínima

```python
# En main_enhanced.py, método procesar_mesa()
if confianza >= 85:  # Cambiar de 80 a 85 para más seguridad
    # Enviar señal
```

---

## 📱 Formato de Señales

Las señales enviadas incluyen:

```
🎰 **SEÑAL DE BACCARAT** 🟢

📍 **Mesa:** Speed Baccarat 1
🟢 **Apostar a:** BANCA
📊 **Estrategia:** Consenso
🎯 **Confianza:** 92% 🔥

📈 **Historial reciente:** B, P, B, B, B, P, B, B, B, B
⏱️ **Tiempo restante:** 20 segundos

📊 **Estadísticas de la mesa:**
• Total jugadas: 150
• Precisión: 87.5%
• Señales generadas: 8

⏰ **Hora:** 14:35:22
```

---

## 🛠️ Comandos Útiles

### Ver Logs en Tiempo Real

```bash
# Seguir logs
tail -f baccarat_bot.log

# Ver solo errores
tail -f baccarat_bot.log | grep ERROR

# Ver solo señales
tail -f baccarat_bot.log | grep "Señal enviada"
```

### Detener Bot

```bash
# Ctrl+C en la terminal
# O enviar señal SIGTERM
kill -TERM $(pgrep -f main_enhanced)
```

### Reiniciar Bot

```bash
# Detener y reiniciar
pkill -f main_enhanced && python baccarat_bot/main_enhanced.py
```

---

## 📈 Monitorear Rendimiento

### Ver Estadísticas del PagePool

```python
# El bot muestra automáticamente cada 10 ciclos:
# PagePool: {'active': 3, 'idle': 2, 'total': 5}
```

### Ver Precisión de Señales

```python
# En la base de datos
from baccarat_bot.database.models import db_manager

stats = db_manager.obtener_estadisticas_mesa('Speed Baccarat 1')
print(f"Precisión: {stats['precision_senales']:.1f}%")
```

---

## 🐛 Solución Rápida de Problemas

### Problema: ModuleNotFoundError

```bash
# Instalar dependencias faltantes
pip install -r requirements.txt
```

### Problema: Playwright no encuentra navegador

```bash
# Reinstalar navegadores
playwright install chromium
```

### Problema: Error de permisos

```bash
# Dar permisos de ejecución
chmod +x baccarat_bot/main_enhanced.py
```

### Problema: Bot no envía señales

**Verificar:**
1. ✅ Credenciales de Telegram correctas
2. ✅ Historial suficiente (20+ resultados)
3. ✅ Timing óptimo (15-25s restantes)
4. ✅ Confianza ≥80%

---

## 📚 Documentación Completa

- **README_MEJORADO.md** - Documentación general
- **MEJORAS_IMPLEMENTADAS.md** - Mejoras básicas (7 mejoras)
- **MEJORAS_AVANZADAS_COMPLETAS.md** - Mejoras avanzadas (12 mejoras)
- **GUIA_INTEGRACION.md** - Guía de integración detallada
- **INICIO_RAPIDO.md** - Esta guía

---

## 🎯 Próximos Pasos

### Después de Iniciar

1. **Monitorear logs** para verificar funcionamiento
2. **Revisar señales** enviadas a Telegram
3. **Ajustar configuración** según necesidades
4. **Analizar estadísticas** después de 24 horas

### Optimizaciones Opcionales

1. Ajustar intervalo de monitoreo
2. Modificar confianza mínima
3. Agregar más mesas
4. Personalizar estrategias

---

## ✅ Checklist de Inicio

- [ ] Entorno virtual creado
- [ ] Dependencias instaladas
- [ ] Playwright instalado
- [ ] Credenciales configuradas
- [ ] Tests ejecutados (80/80)
- [ ] Bot iniciado
- [ ] Primera señal recibida
- [ ] Logs monitoreados

---

## 🆘 Soporte

Si tienes problemas:

1. Revisa los logs: `tail -f baccarat_bot.log`
2. Ejecuta tests: `pytest tests/ -v`
3. Verifica configuración: `python -c "from baccarat_bot.config_unified import config; config.validate_all()"`

---

**¡Listo para comenzar! 🚀**

*Guía creada por Manus AI*  
*Versión: 3.0*
