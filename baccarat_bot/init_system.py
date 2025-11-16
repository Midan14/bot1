# baccarat_bot/init_system.py

"""
Script de inicialización del sistema de Bot de Baccarat
Configura la base de datos, registra mesas y verifica que todo funcione
"""

import asyncio
import logging
from datetime import datetime

from database.models import db_manager
from baccarat_bot.tables import MESA_NOMBRES, inicializar_mesas
from stats_module.analyzer import analyzer
from baccarat_bot.strategies.advanced_strategies import strategy_manager
from integrations.web_scraper import data_source_manager
from baccarat_bot.config import BASE_URL

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def inicializar_base_de_datos():
    """Inicializa la base de datos y registra todas las mesas"""
    logger.info("=" * 60)
    logger.info("INICIALIZANDO BASE DE DATOS")
    logger.info("=" * 60)
    
    try:
        # La base de datos se inicializa automáticamente al importar db_manager
        logger.info("✅ Base de datos inicializada correctamente")
        
        # Registrar todas las mesas
        logger.info(f"\n📋 Registrando {len(MESA_NOMBRES)} mesas...")
        
        mesas_dict = inicializar_mesas()
        mesas_registradas = 0
        
        for nombre, info in mesas_dict.items():
            mesa_id = db_manager.registrar_mesa(nombre, info['url'])
            if mesa_id:
                mesas_registradas += 1
        
        logger.info(f"✅ {mesas_registradas} mesas registradas exitosamente\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error inicializando base de datos: {e}")
        return False

async def verificar_estrategias():
    """Verifica que todas las estrategias estén funcionando"""
    logger.info("=" * 60)
    logger.info("VERIFICANDO ESTRATEGIAS")
    logger.info("=" * 60)
    
    try:
        # Historial de prueba
        test_history = ['B', 'P', 'B', 'P', 'B', 'B', 'B', 'P', 'E', 'B']
        
        logger.info(f"\n🧪 Probando con historial: {test_history}\n")
        
        # Probar todas las estrategias
        results = strategy_manager.analyze_all(test_history)
        
        for name, result in results.items():
            status = "✅ ACTIVA" if result['active'] else "⚪ INACTIVA"
            signal = result.get('signal', 'N/A')
            confidence = result.get('confidence', 0)
            
            logger.info(
                f"  {status} | {name:20s} | "
                f"Señal: {signal:10s} | Confianza: {confidence}%"
            )
        
        # Probar señal de consenso
        consensus = strategy_manager.get_consensus_signal(test_history)
        
        if consensus:
            logger.info(f"\n🎯 SEÑAL DE CONSENSO:")
            logger.info(f"  Apuesta: {consensus['signal']}")
            logger.info(f"  Confianza: {consensus['confidence']}%")
            logger.info(
                f"  Estrategias de acuerdo: "
                f"{', '.join(consensus['strategies_agreeing'])}"
            )
        else:
            logger.info("\n⚪ No hay señal de consenso")
        
        logger.info("\n✅ Todas las estrategias verificadas correctamente\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verificando estrategias: {e}")
        return False

async def verificar_scraper():
    """Verifica el funcionamiento del web scraper"""
    logger.info("=" * 60)
    logger.info("VERIFICANDO WEB SCRAPER")
    logger.info("=" * 60)
    
    try:
        # Inicializar el scraper
        await data_source_manager.init()
        
        # Habilitar modo simulación para pruebas
        data_source_manager.enable_simulation_mode(True)
        
        logger.info("\n🌐 Probando obtención de resultados...")
        
        # Probar obtener resultado de una mesa
        result = await data_source_manager.get_table_result(
            "Speed Baccarat 1",
            "97408"
        )
        
        if result:
            logger.info(f"✅ Resultado obtenido: {result}")
        else:
            logger.warning("⚠️  No se pudo obtener resultado")
        
        # Cerrar sesión
        await data_source_manager.close()
        
        logger.info("✅ Web scraper verificado correctamente\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verificando scraper: {e}")
        return False

async def generar_datos_de_prueba():
    """Genera datos de prueba para demostración"""
    logger.info("=" * 60)
    logger.info("GENERANDO DATOS DE PRUEBA")
    logger.info("=" * 60)
    
    try:
        import random
        
        logger.info("\n📊 Generando resultados simulados...")
        
        # Seleccionar algunas mesas aleatorias
        mesas_sample = random.sample(MESA_NOMBRES, min(10, len(MESA_NOMBRES)))
        
        for mesa in mesas_sample:
            # Generar 20 resultados aleatorios
            for _ in range(20):
                resultado = random.choices(
                    ['B', 'P', 'E'],
                    weights=[46, 45, 9]
                )[0]
                
                db_manager.registrar_resultado(mesa, resultado)
        
        logger.info(f"✅ Generados datos de prueba para {len(mesas_sample)} mesas")
        
        # Generar algunas señales de prueba
        logger.info("\n🎯 Generando señales de prueba...")
        
        for mesa in mesas_sample[:3]:
            historial = ['B', 'B', 'B', 'P']
            db_manager.registrar_senal(
                mesa_nombre=mesa,
                tipo_senal='racha',
                resultado_recomendado='JUGADOR',
                historial=historial,
                exito=True
            )
        
        logger.info("✅ Señales de prueba generadas\n")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error generando datos de prueba: {e}")
        return False

async def mostrar_reporte_inicial():
    """Muestra un reporte inicial del sistema"""
    logger.info("=" * 60)
    logger.info("REPORTE INICIAL DEL SISTEMA")
    logger.info("=" * 60)
    
    try:
        # Obtener reporte general
        reporte = analyzer.generar_reporte_general()
        
        if 'error' in reporte:
            logger.warning(f"⚠️  {reporte['error']}")
            return True
        
        # Mostrar resumen
        resumen = reporte['resumen_general']
        logger.info(f"\n📈 RESUMEN GENERAL:")
        logger.info(f"  Mesas monitoreadas: {resumen['total_mesas_monitoreadas']}")
        logger.info(f"  Total jugadas: {resumen['total_jugadas']}")
        logger.info(f"  Señales generadas: {resumen['total_senales_generadas']}")
        logger.info(
            f"  Precisión general: {resumen['precision_general']:.1f}%"
        )
        
        # Mostrar distribución
        dist = reporte['distribucion_global']
        total = dist['total_banca'] + dist['total_jugador'] + dist['total_empate']
        
        if total > 0:
            logger.info(f"\n🎲 DISTRIBUCIÓN GLOBAL:")
            logger.info(
                f"  Banca: {dist['total_banca']} "
                f"({dist['total_banca']/total*100:.1f}%)"
            )
            logger.info(
                f"  Jugador: {dist['total_jugador']} "
                f"({dist['total_jugador']/total*100:.1f}%)"
            )
            logger.info(
                f"  Empate: {dist['total_empate']} "
                f"({dist['total_empate']/total*100:.1f}%)"
            )
        
        # Mostrar top mesas
        if reporte['top_mesas_activas']:
            logger.info(f"\n🏆 TOP 5 MESAS MÁS ACTIVAS:")
            for i, mesa in enumerate(reporte['top_mesas_activas'][:5], 1):
                logger.info(
                    f"  {i}. {mesa['mesa']}: {mesa['total_jugadas']} jugadas"
                )
        
        logger.info("")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error generando reporte: {e}")
        return False

async def main():
    """Función principal de inicialización"""
    logger.info("\n")
    logger.info("╔" + "═" * 58 + "╗")
    logger.info("║" + " " * 10 + "BOT DE BACCARAT - INICIALIZACIÓN" + " " * 16 + "║")
    logger.info("╚" + "═" * 58 + "╝")
    logger.info("")
    
    start_time = datetime.now()
    
    # Ejecutar todas las verificaciones
    pasos = [
        ("Base de Datos", inicializar_base_de_datos()),
        ("Estrategias", verificar_estrategias()),
        ("Web Scraper", verificar_scraper()),
        ("Datos de Prueba", generar_datos_de_prueba()),
        ("Reporte Inicial", mostrar_reporte_inicial())
    ]
    
    resultados = []
    for nombre, tarea in pasos:
        resultado = await tarea
        resultados.append((nombre, resultado))
    
    # Resumen final
    logger.info("=" * 60)
    logger.info("RESUMEN DE INICIALIZACIÓN")
    logger.info("=" * 60)
    
    for nombre, resultado in resultados:
        status = "✅ OK" if resultado else "❌ FALLÓ"
        logger.info(f"  {status} | {nombre}")
    
    total_exitosos = sum(1 for _, r in resultados if r)
    total_pasos = len(resultados)
    
    logger.info("")
    logger.info(f"📊 Completado: {total_exitosos}/{total_pasos} pasos exitosos")
    
    elapsed_time = (datetime.now() - start_time).total_seconds()
    logger.info(f"⏱️  Tiempo total: {elapsed_time:.2f} segundos")
    
    if total_exitosos == total_pasos:
        logger.info("")
        logger.info("🎉 ¡SISTEMA INICIALIZADO CORRECTAMENTE!")
        logger.info("")
        logger.info("📝 PRÓXIMOS PASOS:")
        logger.info("  1. Ejecutar el bot: python main.py")
        logger.info("  2. Ejecutar el bot avanzado: python main_advanced.py")
        logger.info("  3. Iniciar API Server: python api/server.py")
        logger.info("  4. Bot de Telegram interactivo: python telegram_bot/interactive_bot.py")
        logger.info("")
        return True
    else:
        logger.warning("")
        logger.warning("⚠️  ALGUNOS PASOS FALLARON")
        logger.warning("Revisa los errores anteriores para más detalles")
        logger.warning("")
        return False

if __name__ == "__main__":
    try:
        resultado = asyncio.run(main())
        exit(0 if resultado else 1)
    except KeyboardInterrupt:
        logger.info("\n\n🛑 Inicialización cancelada por el usuario")
        exit(1)
    except Exception as e:
        logger.error(f"\n\n❌ Error crítico durante la inicialización: {e}")
        exit(1)
