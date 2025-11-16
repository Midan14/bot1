# baccarat_bot/test_startup.py

import asyncio
from main import bucle_monitoreo


async def test_bot_startup():
    """Prueba el arranque del bot por unos segundos."""
    print("🧪 INICIANDO PRUEBA DE ARRANQUE DEL BOT")
    print("=" * 50)
    
    try:
        # Ejecutar por 5 segundos con un intervalo muy corto para prueba
        await asyncio.wait_for(
            bucle_monitoreo(intervalo_segundos=1),
            timeout=5.0
        )
    except asyncio.TimeoutError:
        print("✅ Bot ejecutándose correctamente durante 5 segundos")
        print("🛑 Prueba completada - Bot detenido")
        return True
    except Exception as e:
        print(f"❌ Error en el bot: {e}")
        return False
    
    return True


if __name__ == "__main__":
    result = asyncio.run(test_bot_startup())
    if result:
        print("\n🎉 ¡PRUEBA EXITOSA! El bot está listo para funcionar.")
    else:
        print("\n💥 ¡PRUEBA FALLIDA! Revisar errores arriba.")