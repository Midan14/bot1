# 🚀 Instalación de Playwright para Web Scraping Real

Este documento explica cómo instalar y configurar Playwright para obtener **datos reales en vivo** de 1xBet.

## 📋 Requisitos Previos

- Python 3.8 o superior
- Entorno virtual activado (`baccarat_env`)
- Conexión a Internet estable

## 🔧 Instalación Paso a Paso

### 1. Activar el Entorno Virtual

```bash
cd baccarat_bot
source ../baccarat_env/bin/activate
```

### 2. Instalar Dependencias de Python

```bash
pip install -r requirements.txt
```

Esto instalará:

- `playwright>=1.40.0` - Framework de automatización de navegadores
- `playwright-stealth>=0.1.5` - Técnicas anti-detección
- `fake-useragent>=1.4.0` - Rotación de user agents
- Y otras dependencias necesarias

### 3. Instalar Navegadores de Playwright

Playwright necesita descargar navegadores específicos. Ejecuta:

```bash
playwright install chromium
```

**Nota:** Si aparece un error de permisos, ejecuta:

```bash
python -m playwright install chromium
```

Para instalar todos los navegadores (opcional):

```bash
playwright install
```

### 4. Verificar Instalación

Ejecuta este comando para verificar que Playwright está correctamente instalado:

```bash
python -c "from playwright.sync_api import sync_playwright; print('✅ Playwright instalado correctamente')"
```

Si ves el mensaje de éxito, ¡estás listo!

## ⚙️ Configuración

### 1. Activar Datos Reales

Edita el archivo `.env` y cambia:

```env
USAR_DATOS_REALES=true
```

### 2. Configurar IDs de Mesas (Opcional)

Para usar datos reales, necesitas los IDs de juego de 1xBet. Actualiza el archivo `tables.py` con los IDs correctos:

```python
MESAS_BACCARAT = {
    "Speed Baccarat 1": {
        "nombre": "Speed Baccarat 1",
        "game_id": "12345",  # ID real del juego en 1xBet
        "historial": []
    },
    # ... más mesas
}
```

## 🎯 Modos de Operación

### Modo SIMULACIÓN (por defecto)

```env
USAR_DATOS_REALES=false
```

- Usa datos simulados con probabilidades reales de Baccarat
- No requiere conexión a 1xBet
- Ideal para pruebas y desarrollo

### Modo DATOS REALES

```env
USAR_DATOS_REALES=true
```

- Obtiene datos en vivo de 1xBet mediante scraping
- Usa Playwright con técnicas anti-bot
- Requiere instalación de Playwright

## 🔍 Técnicas Anti-Bot Implementadas

El scraper incluye múltiples técnicas para evadir detección:

1. **User Agent Rotation** - Rota entre diferentes navegadores reales
2. **Viewport Randomization** - Usa diferentes resoluciones de pantalla
3. **Navigator Overrides** - Oculta `navigator.webdriver`
4. **Geolocation** - Simula ubicación en Bogotá, Colombia
5. **Rate Limiting** - Respeta límites de solicitudes
6. **Cache** - Reduce solicitudes repetitivas
7. **JavaScript Anti-Detection** - Scripts para parecer navegador real

## 🚨 Solución de Problemas

### Error: "Playwright not installed"

```bash
pip install playwright
playwright install chromium
```

### Error: "Permission denied"

En macOS/Linux:

```bash
chmod +x ~/.cache/ms-playwright/chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium
```

### Error: "Browser closed"

El navegador puede cerrarse por:

- Detección de bot por 1xBet
- Timeout de conexión
- Cloudflare bloqueando acceso

**Solución:** El sistema automáticamente cambiará a modo simulación si falla.

### Navegador visible (modo headless=False)

Para depuración, puedes ver el navegador en acción:

En `playwright_scraper.py`, cambia:

```python
await self.init(headless=False)  # Muestra el navegador
```

## 📊 Verificar que Funciona

Ejecuta el bot y verifica los logs:

```bash
python main.py
```

Busca mensajes como:

```
🚀 Iniciando Playwright con modo anti-bot...
✅ Playwright inicializado correctamente
🌐 Obteniendo datos REALES para Speed Baccarat 1
✅ Resultado REAL obtenido para Speed Baccarat 1: B
```

## ⚠️ Consideraciones Legales

- **Términos de Servicio:** Verifica que el scraping no viola los términos de 1xBet
- **Uso Responsable:** No sobrecargues los servidores con demasiadas solicitudes
- **Rate Limiting:** El scraper incluye delays automáticos
- **Proxy (Opcional):** Considera usar proxies para distribución de carga

## 🔄 Modo Fallback

Si el scraping falla, el bot automáticamente:

1. Registra el error en los logs
2. Cambia a modo SIMULACIÓN
3. Continúa funcionando normalmente

Esto garantiza que el bot **siempre funcione**, incluso si hay problemas de conexión.

## 📈 Optimizaciones Recomendadas

### Para Producción

1. **Usar Proxies**
   - Distribuir requests entre múltiples IPs
   - Evitar bloqueos por rate limiting

2. **Aumentar Cache**

   ```python
   self.cache_duration = 60  # segundos
   ```

3. **Reducir Concurrencia**

   ```python
   semaphore = asyncio.Semaphore(3)  # Máximo 3 mesas simultáneas
   ```

4. **Monitorear Errores**
   - Implementar alertas si el scraping falla
   - Logs detallados de errores

## 🎓 Recursos Adicionales

- [Documentación de Playwright](https://playwright.dev/python/)
- [Anti-Detection Techniques](https://www.scrapehero.com/how-to-prevent-getting-blacklisted-while-scraping/)
- [Playwright Stealth](https://github.com/AtuboDad/playwright_stealth)

## 💡 Próximos Pasos

1. Instala Playwright
2. Activa `USAR_DATOS_REALES=true`
3. Configura IDs de mesas reales
4. Ejecuta el bot
5. Monitorea los logs

¡Listo para obtener datos REALES EN VIVO! 🎰🚀
