# Bot de Señales de Baccarat para 1xBet (Arquitectura Robusta)

Este documento describe la arquitectura y el código fuente del bot de Telegram diseñado para monitorear múltiples mesas de Baccarat de 1xBet y emitir señales de apuesta basadas en una estrategia predefinida.

## 1. Arquitectura del Sistema

El bot sigue un diseño modular para facilitar el mantenimiento y la futura integración de datos reales.

| Módulo | Archivo | Descripción |
| :--- | :--- | :--- |
| **Definiciones** | `tables.py` | Contiene la lista de las 58 mesas de Baccarat de 1xBet y la estructura de datos para su monitoreo. |
| **Lógica de Señales** | `signal_logic.py` | Implementa la estrategia de "Racha de 3" para generar señales de apuesta (`Banca` o `Jugador`). |
| **Fuente de Datos** | `data_source.py` | **Módulo de Simulación** que genera resultados aleatorios de Baccarat. Este es el punto de integración para datos reales. |
| **Orquestación** | `main.py` | Contiene el bucle principal de monitoreo, la lógica de integración con Telegram y la configuración de las credenciales. |

## 2. Estrategia de Señales Implementada

La estrategia por defecto implementada es la **"Estrategia de Racha de 3"**:

> **Señal de Apuesta:** Si el mismo resultado (Jugador o Banca) ocurre **3 veces consecutivas**, la señal para la siguiente ronda será apostar a ese **mismo resultado**.

*   **Ejemplo:** Historial `[P, B, B, B]` -> Señal: **Banca**
*   **Ejemplo:** Historial `[B, P, P, P]` -> Señal: **Jugador**

## 3. Configuración y Ejecución

### Requisitos

*   Python 3.8+
*   Librería `python-telegram-bot`

### Credenciales

Las credenciales de Telegram han sido configuradas directamente en `main.py` para la ejecución inmediata:

| Variable | Valor |
| :--- | :--- |
| `TOKEN` | `8235077057:AAGSHsr_su_TbjlcWehdlIrwr8Kn1XXID6o` |
| `CHAT_ID` | `631443236` |

### Ejecución

Para ejecutar el bot (asumiendo que está en el entorno virtual `venv`):

```bash
# Activar el entorno virtual (si no está activo)
source venv/bin/activate

# Ejecutar el bot
python baccarat_bot/main.py
```

El bot comenzará a simular resultados y enviará señales a su chat de Telegram cada vez que detecte el patrón de racha.

## 4. Integración con Datos Reales (Futuro)

Para convertir este bot de simulación a un bot real, debe modificar el archivo `data_source.py`.

La función a modificar es `obtener_nuevo_resultado(mesa_data)`. Debe reemplazar la lógica de simulación (`random.choice`) con código que:

1.  Se conecte a la fuente de datos de 1xBet (API, Web Scraper, etc.).
2.  Recupere el último resultado de la ronda para la mesa especificada en `mesa_data['nombre']`.
3.  Devuelva el resultado como `'B'`, `'P'`, o `'E'`.

**Nota:** La implementación de un Web Scraper para un casino en vivo es compleja y puede violar los términos de servicio. Se recomienda buscar una API de datos si es posible.
