#!/usr/bin/env python3
# baccarat_bot/bot_control.py

"""
Script de control del Bot de Baccarat
Permite iniciar, detener, reiniciar y verificar el estado del bot
"""

import os
import sys
import signal
import subprocess
import time
import psutil
from pathlib import Path

# Colores para la terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header():
    """Imprime el encabezado del script"""
    print("\n" + "=" * 60)
    print(f"{Colors.BOLD}{Colors.BLUE}🎰 BOT DE BACCARAT - CONTROL{Colors.END}")
    print("=" * 60 + "\n")

def get_bot_processes():
    """Obtiene todos los procesos del bot que están corriendo"""
    bot_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and 'python' in cmdline[0].lower():
                cmdline_str = ' '.join(cmdline)
                if any(keyword in cmdline_str for keyword in [
                    'main.py', 'main_advanced.py', 'server.py', 
                    'interactive_bot.py', 'init_system.py'
                ]):
                    bot_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    return bot_processes

def stop_bot():
    """Detiene todos los procesos del bot"""
    print(f"{Colors.YELLOW}🛑 Deteniendo el bot...{Colors.END}\n")
    
    processes = get_bot_processes()
    
    if not processes:
        print(f"{Colors.GREEN}✅ No hay procesos del bot ejecutándose{Colors.END}\n")
        return True
    
    for proc in processes:
        try:
            cmdline = ' '.join(proc.cmdline())
            print(f"  Deteniendo PID {proc.pid}: {cmdline}")
            proc.terminate()
        except Exception as e:
            print(f"{Colors.RED}  Error deteniendo proceso {proc.pid}: {e}{Colors.END}")
    
    # Esperar a que los procesos terminen
    time.sleep(2)
    
    # Verificar si quedan procesos
    remaining = get_bot_processes()
    if remaining:
        print(f"\n{Colors.YELLOW}⚠️  Algunos procesos no se detuvieron, forzando...{Colors.END}")
        for proc in remaining:
            try:
                proc.kill()
            except:
                pass
        time.sleep(1)
    
    final_check = get_bot_processes()
    if not final_check:
        print(f"\n{Colors.GREEN}✅ Todos los procesos del bot han sido detenidos{Colors.END}\n")
        return True
    else:
        print(f"\n{Colors.RED}❌ Algunos procesos no pudieron ser detenidos{Colors.END}\n")
        return False

def start_bot(mode='advanced'):
    """Inicia el bot en el modo especificado"""
    print(f"{Colors.GREEN}🚀 Iniciando el bot...{Colors.END}\n")
    
    # Primero detener cualquier instancia previa
    stop_bot()
    
    # Mapeo de modos a archivos
    modes = {
        'basic': 'main.py',
        'advanced': 'main_advanced.py',
        'api': 'api/server.py',
        'telegram': 'telegram_bot/interactive_bot.py'
    }
    
    if mode not in modes:
        print(f"{Colors.RED}❌ Modo inválido: {mode}{Colors.END}")
        print(f"Modos disponibles: {', '.join(modes.keys())}")
        return False
    
    script = modes[mode]
    
    try:
        # Iniciar el bot en segundo plano
        process = subprocess.Popen(
            ['python', script],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        time.sleep(2)
        
        # Verificar si el proceso sigue corriendo
        if process.poll() is None:
            print(f"{Colors.GREEN}✅ Bot iniciado exitosamente (PID: {process.pid}){Colors.END}")
            print(f"{Colors.BLUE}📝 Modo: {mode}{Colors.END}")
            print(f"{Colors.BLUE}📄 Script: {script}{Colors.END}\n")
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"{Colors.RED}❌ El bot no pudo iniciarse{Colors.END}")
            if stderr:
                print(f"\nError: {stderr.decode()}")
            return False
            
    except Exception as e:
        print(f"{Colors.RED}❌ Error al iniciar el bot: {e}{Colors.END}\n")
        return False

def restart_bot(mode='advanced'):
    """Reinicia el bot"""
    print(f"{Colors.YELLOW}🔄 Reiniciando el bot...{Colors.END}\n")
    stop_bot()
    time.sleep(1)
    return start_bot(mode)

def status_bot():
    """Muestra el estado actual del bot"""
    print(f"{Colors.BLUE}📊 Estado del Bot{Colors.END}\n")
    
    processes = get_bot_processes()
    
    if not processes:
        print(f"{Colors.RED}⚪ El bot NO está ejecutándose{Colors.END}\n")
        return False
    
    print(f"{Colors.GREEN}✅ El bot ESTÁ ejecutándose{Colors.END}\n")
    print(f"{Colors.BOLD}Procesos activos:{Colors.END}")
    
    for proc in processes:
        try:
            cmdline = ' '.join(proc.cmdline())
            cpu = proc.cpu_percent()
            mem = proc.memory_info().rss / 1024 / 1024  # MB
            
            print(f"\n  PID: {proc.pid}")
            print(f"  Comando: {cmdline}")
            print(f"  CPU: {cpu:.1f}%")
            print(f"  Memoria: {mem:.1f} MB")
        except:
            pass
    
    print()
    return True

def show_menu():
    """Muestra el menú interactivo"""
    print_header()
    print(f"{Colors.BOLD}Opciones disponibles:{Colors.END}\n")
    print("  1. 🚀 Iniciar bot (modo avanzado)")
    print("  2. 🎮 Iniciar bot (modo básico)")
    print("  3. 🌐 Iniciar API Server")
    print("  4. 🤖 Iniciar bot de Telegram")
    print("  5. 🛑 Detener bot")
    print("  6. 🔄 Reiniciar bot")
    print("  7. 📊 Ver estado")
    print("  8. 🚪 Salir")
    print()

def main():
    """Función principal"""
    if len(sys.argv) > 1:
        # Modo línea de comandos
        command = sys.argv[1].lower()
        
        if command in ['start', 'iniciar']:
            mode = sys.argv[2] if len(sys.argv) > 2 else 'advanced'
            start_bot(mode)
        elif command in ['stop', 'detener']:
            stop_bot()
        elif command in ['restart', 'reiniciar']:
            mode = sys.argv[2] if len(sys.argv) > 2 else 'advanced'
            restart_bot(mode)
        elif command in ['status', 'estado']:
            status_bot()
        else:
            print(f"\n{Colors.RED}Comando no reconocido: {command}{Colors.END}\n")
            print("Comandos disponibles:")
            print("  python bot_control.py start [mode]    - Iniciar bot")
            print("  python bot_control.py stop            - Detener bot")
            print("  python bot_control.py restart [mode]  - Reiniciar bot")
            print("  python bot_control.py status          - Ver estado")
            print("\nModos: basic, advanced, api, telegram")
            print()
    else:
        # Modo interactivo
        while True:
            show_menu()
            
            try:
                opcion = input(f"{Colors.BOLD}Selecciona una opción (1-8): {Colors.END}").strip()
                print()
                
                if opcion == '1':
                    start_bot('advanced')
                elif opcion == '2':
                    start_bot('basic')
                elif opcion == '3':
                    start_bot('api')
                elif opcion == '4':
                    start_bot('telegram')
                elif opcion == '5':
                    stop_bot()
                elif opcion == '6':
                    mode = input("Modo (basic/advanced/api/telegram) [advanced]: ").strip() or 'advanced'
                    restart_bot(mode)
                elif opcion == '7':
                    status_bot()
                elif opcion == '8':
                    print(f"{Colors.GREEN}👋 ¡Hasta luego!{Colors.END}\n")
                    break
                else:
                    print(f"{Colors.RED}❌ Opción inválida{Colors.END}\n")
                
                if opcion != '8':
                    input(f"\n{Colors.BOLD}Presiona Enter para continuar...{Colors.END}")
                    print("\n" * 2)
                    
            except KeyboardInterrupt:
                print(f"\n\n{Colors.YELLOW}🛑 Operación cancelada{Colors.END}\n")
                break
            except Exception as e:
                print(f"\n{Colors.RED}❌ Error: {e}{Colors.END}\n")

if __name__ == "__main__":
    main()
