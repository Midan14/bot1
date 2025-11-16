# Script para evaluar el modelo ML y mostrar métricas de precisión

from baccarat_bot.ml_integration import evaluar_ml
from baccarat_bot.tables import inicializar_mesas
import random

def generar_historial_simulado(n=100):
    opciones = ['Player', 'Banker', 'Tie']
    # Simula resultados con más frecuencia para Player y Banker
    pesos = [0.45, 0.45, 0.10]
    return random.choices(opciones, weights=pesos, k=n)

if __name__ == "__main__":
    mesas = inicializar_mesas()
    for nombre, mesa_data in mesas.items():
        # Poblar historial con datos simulados si está vacío
        if not mesa_data['historial_resultados']:
            mesa_data['historial_resultados'] = generar_historial_simulado(120)
        historial = mesa_data.get('historial_resultados', [])
        print(f"\n=== Evaluando modelo ML para la mesa: {nombre} ===")
        evaluar_ml(historial)
