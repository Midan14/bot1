# 📱 Cómo Configurar tu Bot para Enviar Señales a un Canal o Grupo de Telegram

## Objetivo

Cambiar la configuración del bot para que envíe las señales a un **canal** o **grupo de Telegram** en lugar de a tu chat privado.

---

## 📋 PASO 1: Obtener el ID del Canal o Grupo

### Opción A: Si ya tienes un CANAL creado

1. **Abre tu canal en Telegram**
2. **Haz clic en el nombre del canal** (arriba)
3. **Desplázate hasta encontrar** "Información del canal"
4. **Copia la URL** que aparece (ejemplo: `https://t.me/mi_canal_baccarat`)

El ID del canal es: **`-100` + los números de la URL**

**Ejemplo:**

- URL: `https://t.me/mi_canal_baccarat`
- ID: `-100123456789` (agrupa con -100)

### Opción B: Si ya tienes un GRUPO creado

1. **Abre tu grupo en Telegram**
2. **Copia la URL** del grupo
3. Usa el mismo método que arriba

---

## 🔑 PASO 2: Obtener el CHAT_ID Correcto

### Método Fácil (Recomendado)

1. **En tu canal/grupo**, escribe un mensaje cualquiera
2. **Abre este bot en Telegram**: `@userinfobot`
3. **Reenvía el mensaje** del canal/grupo a este bot
4. **El bot te mostrará el ID exacto** (negativo para canales/grupos)

**Ejemplo de ID:**

- Para chat privado: `631443236` (positivo)
- Para canal: `-1001234567890` (negativo, comienza con -100)
- Para grupo: `-9876543210` (negativo)

---

## ✏️ PASO 3: Actualizar el Archivo .env

**Abre el archivo `.env` en tu carpeta del bot:**

```bash
nano .env
```

**Busca esta línea:**

```
TELEGRAM_CHAT_ID=631443236
```

**Reemplázala con tu CHAT_ID del canal/grupo:**

```
TELEGRAM_CHAT_ID=-1001234567890
```

**Ejemplo real:**

```
TELEGRAM_BOT_TOKEN=8235077057:AAGSHsr_su_TbjlcWehdlIrwr8Kn1XXID6o
TELEGRAM_CHAT_ID=-1001234567890
INTERVALO_MONITOREO=5
```

**Guarda el archivo:**

- Presiona: `Ctrl+X`
- Presiona: `Y`
- Presiona: `Enter`

---

## 👥 PASO 4: Dale Permisos al Bot en el Canal/Grupo

### Para un CANAL

1. Abre tu canal en Telegram
2. Haz clic en **Editar canal** (engranaje)
3. Ve a **Administradores**
4. Haz clic en **Agregar administrador**
5. **Busca tu bot** (el que creaste con @BotFather)
6. **Dale permisos:**
   - ✅ Publicar mensajes
   - ✅ Editar mensajes
   - (Otros permisos opcionales)
7. **Guarda**

### Para un GRUPO

1. Abre tu grupo en Telegram
2. Haz clic en **Editar grupo**
3. Ve a **Administradores**
4. Haz clic en **Agregar administrador**
5. **Selecciona tu bot**
6. **Dale permisos:**
   - ✅ Enviar mensajes
   - ✅ Enviar media
   - (Otros permisos opcionales)
7. **Guarda**

---

## 🚀 PASO 5: Reiniciar el Bot

**En tu terminal:**

```bash
# Detén el bot actual (Ctrl+C)

# Reinicia el bot
python main.py
```

**¡El bot ahora enviará todas las señales al canal/grupo!**

---

## ✅ Verificación: ¿Está Funcionando?

1. **Abre tu canal/grupo en Telegram**
2. **Espera a que el bot detecte una señal**
3. **Deberías ver un mensaje como este:**

```
🚨 ¡SEÑAL DE BACARÁ DETECTADA! 🚨

🎰 Mesa: Japanese Speed Baccarat C
🔗 Enlace: https://col.1xbet.com/es/casino/game/97408/

💙 APUESTA RECOMENDADA:
🔵 JUGADOR 🔵
(Estrategia: StreakStrategy)

⚖️ CONFIDENCIA: 🔵 ALTA
⏱️ Hora de la Señal: 14:30:45
📊 Historial: B, P, P, B
```

✅ **¡Si ves esto, está funcionando!**

---

## 🔄 Cambiar Entre Chat Privado, Canal o Grupo

Es **muy fácil** cambiar entre diferentes destinos:

### Para enviar a tu chat privado

```
TELEGRAM_CHAT_ID=631443236
```

### Para enviar a tu canal

```
TELEGRAM_CHAT_ID=-1001234567890
```

### Para enviar a tu grupo

```
TELEGRAM_CHAT_ID=-9876543210
```

**Solo edita el `.env` y reinicia el bot.** ¡Sin cambiar código!

---

## ❓ Solución de Problemas

### Error: "Bot was blocked by the user"

**Solución:** Verifica que el bot tenga permisos en el canal/grupo

### Error: "CHAT_ID no es válido"

**Solución:** El ID debe ser negativo para canales/grupos

- Incorrecto: `1234567890`
- Correcto: `-1001234567890`

### Error: "Chat not found"

**Solución:** Obtén el ID correcto usando `@userinfobot`

### El bot no envía mensajes

**Solución:**

1. Verifica que el bot sea administrador
2. Verifica que tenga permiso para "Publicar mensajes"
3. Reinicia el bot con: `python main.py`

---

## 📊 Comparación de Opciones

| Opción | Ventaja | Desventaja |
|--------|---------|-----------|
| **Chat Privado** | Solo tú ves las señales | No es compartible |
| **Canal** | Muchas personas pueden ver | Sin interacción |
| **Grupo** | Interacción con otros | Más ruido/spam |

---

## 🎯 Resumen Rápido

```bash
# 1. Obtén el ID del canal/grupo
# (Usa @userinfobot)

# 2. Abre .env
nano .env

# 3. Cambia
TELEGRAM_CHAT_ID=-1001234567890

# 4. Guarda (Ctrl+X, Y, Enter)

# 5. Reinicia
python main.py
```

**¡Listo! Tu bot ahora envía señales al canal/grupo 🚀**

---

## 📞 Verificación Final

Después de configurar:

✅ El bot está corriendo: `python main.py`
✅ El CHAT_ID en `.env` es negativo (comienza con `-100`)
✅ El bot es administrador del canal/grupo
✅ El bot tiene permiso para enviar mensajes

Si todo está ✅, verás las señales aparecer en tu canal/grupo.

---

*Última actualización: 11/11/2025*
