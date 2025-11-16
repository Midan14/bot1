# baccarat_bot/simulations/simulator.py

import random
from typing import List, Tuple, Dict
from collections import deque
from datetime import datetime

# Constantes de Baccarat (probabilidades aproximadas)
# Banker: 45.86%
# Player: 44.62%
# Tie: 9.52%
# Ajustamos para que la suma sea 100%
BANKER_PROB = 45.86
PLAYER_PROB = 44.62
TIE_PROB = 9.52

class BaccaratSimulator:
    """
    Simulador de rondas de Baccarat para probar estrategias.
    Genera resultados con una distribución estadística realista.
    """

    def __init__(self, num_decks: int = 8):
        self.num_decks = num_decks
        self.history: List[str] = []
        self.stats: Dict[str, int] = {'B': 0, 'P': 0, 'E': 0}

    def _generate_result(self) -> str:
        """Genera un resultado de Baccarat basado en probabilidades."""
        rand_val = random.uniform(0, 100)
        
        if rand_val < BANKER_PROB:
            result = 'B'
        elif rand_val < BANKER_PROB + PLAYER_PROB:
            result = 'P'
        else:
            result = 'E'
            
        self.stats[result] += 1
        return result

    def run_round(self) -> str:
        """Ejecuta una sola ronda y actualiza el historial."""
        result = self._generate_result()
        self.history.append(result)
        return result

    def run_simulation(self, num_rounds: int) -> List[str]:
        """Ejecuta una simulación de N rondas."""
        for _ in range(num_rounds):
            self.run_round()
        return self.history

    def get_history(self) -> List[str]:
        """Retorna el historial completo de la simulación."""
        return self.history

    def get_stats(self) -> Dict[str, int]:
        """Retorna las estadísticas de resultados."""
        return self.stats

class StrategyTester:
    """
    Clase para probar las estrategias seguras contra un historial simulado.
    """
    
    def __init__(self, strategies_module):
        self.strategies_module = strategies_module
        self.test_results: List[Dict] = []
        self.signal_stats: Dict[str, Dict] = {}

    def test_strategies(self, history: List[str], table_name: str):
        """
        Prueba las estrategias en cada punto del historial.
        
        Args:
            history: Historial completo de resultados.
            table_name: Nombre de la mesa para el reporte.
        """
        
        # Inicializar estadísticas
        self.signal_stats = {
            'total_rounds': len(history),
            'total_signals': 0,
            'correct_signals': 0,
            'incorrect_signals': 0,
            'accuracy': 0.0,
            'table_name': table_name,
            'strategy_breakdown': {}
        }
        
        # Iterar sobre el historial para simular el juego
        for i in range(1, len(history)):
            # Historial disponible para la estrategia (hasta la ronda anterior)
            current_history = history[:i]
            # Resultado real de la ronda actual
            actual_result = history[i]
            
            # Obtener la señal más segura
            safest_signal = self.strategies_module.get_safest_signal(current_history)
            
            if safest_signal:
                apuesta, estrategia, confianza = safest_signal
                
                # Registrar señal
                self.signal_stats['total_signals'] += 1
                
                # Verificar si la apuesta fue correcta
                is_correct = (apuesta[0] == actual_result)
                
                if is_correct:
                    self.signal_stats['correct_signals'] += 1
                else:
                    self.signal_stats['incorrect_signals'] += 1
                    
                # Registrar por estrategia
                if estrategia not in self.signal_stats['strategy_breakdown']:
                    self.signal_stats['strategy_breakdown'][estrategia] = {'total': 0, 'correct': 0}
                
                self.signal_stats['strategy_breakdown'][estrategia]['total'] += 1
                if is_correct:
                    self.signal_stats['strategy_breakdown'][estrategia]['correct'] += 1
                
                # Guardar resultado detallado
                self.test_results.append({
                    'round': i + 1,
                    'history_before': current_history[-10:],
                    'actual_result': actual_result,
                    'signal': apuesta,
                    'strategy': estrategia,
                    'confidence': confianza,
                    'is_correct': is_correct
                })

        # Calcular precisión
        if self.signal_stats['total_signals'] > 0:
            self.signal_stats['accuracy'] = (
                self.signal_stats['correct_signals'] / self.signal_stats['total_signals']
            ) * 100
            
        # Calcular precisión por estrategia
        for strategy, data in self.signal_stats['strategy_breakdown'].items():
            if data['total'] > 0:
                data['accuracy'] = (data['correct'] / data['total']) * 100
            else:
                data['accuracy'] = 0.0

    def get_report(self) -> Dict:
        """Retorna el reporte de estadísticas."""
        return self.signal_stats

    def get_detailed_results(self) -> List[Dict]:
        """Retorna los resultados detallados por ronda."""
        return self.test_results

def generate_simulation_report(num_rounds: int, table_name: str) -> Dict:
    """
    Función principal para generar el reporte de simulación.
    """
    from baccarat_bot.strategies import safe_strategies
    
    # 1. Ejecutar simulación de Baccarat
    simulator = BaccaratSimulator()
    history = simulator.run_simulation(num_rounds)
    
    # 2. Probar estrategias
    tester = StrategyTester(safe_strategies)
    tester.test_strategies(history, table_name)
    
    # 3. Consolidar reporte
    report = {
        'simulation_details': {
            'table_name': table_name,
            'num_rounds': num_rounds,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        'baccarat_stats': simulator.get_stats(),
        'strategy_report': tester.get_report(),
        'detailed_results': tester.get_detailed_results()
    }
    
    return report

if __name__ == '__main__':
    # Ejemplo de uso
    report = generate_simulation_report(num_rounds=100, table_name='XXXtreme Lightning Baccarat')
    
    print("\n--- REPORTE DE SIMULACIÓN ---")
    print(f"Mesa: {report['simulation_details']['table_name']}")
    print(f"Rondas Simuladas: {report['simulation_details']['num_rounds']}")
    print(f"Fecha: {report['simulation_details']['date']}")
    
    print("\n--- Estadísticas de Baccarat (Simulado) ---")
    print(f"Banca (B): {report['baccarat_stats']['B']}")
    print(f"Jugador (P): {report['baccarat_stats']['P']}")
    print(f"Empate (E): {report['baccarat_stats']['E']}")
    
    print("\n--- Reporte de Estrategias ---")
    print(f"Rondas Totales: {report['strategy_report']['total_rounds']}")
    print(f"Señales Generadas: {report['strategy_report']['total_signals']}")
    print(f"Señales Correctas: {report['strategy_report']['correct_signals']}")
    print(f"Precisión General: {report['strategy_report']['accuracy']:.2f}%")
    
    print("\n--- Desglose por Estrategia ---")
    for strategy, data in report['strategy_report']['strategy_breakdown'].items():
        print(f"  {strategy}: Total={data['total']}, Correctas={data['correct']}, Precisión={data['accuracy']:.2f}%")
