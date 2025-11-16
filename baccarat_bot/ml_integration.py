# baccarat_bot/ml_integration.py
"""
Módulo para integrar el predictor ML en la lógica de señales.
"""
from baccarat_bot.ml_predictor import BaccaratMLPredictor
import logging

ml_predictor = BaccaratMLPredictor()

logger = logging.getLogger(__name__)

def entrenar_ml_si_posible(historial):
    
    
    try:
        ml_predictor.train(historial)
        if ml_predictor.is_trained:
            logger.info("Modelo ML entrenado con %d jugadas", len(historial))
    except Exception as e:
        logger.warning(f"Error entrenando modelo ML: {e}")

    
def obtener_prediccion_ml(historial):
    
    try:
        if ml_predictor.is_trained:
            pred = ml_predictor.predict_next(historial)
            if pred:
                return pred
    except Exception as e:
        logger.warning(f"Error en predicción ML: {e}")
    return None


def evaluar_ml(historial):
    """
    Evalúa el modelo ML con el historial dado y muestra métricas de precisión.
    """
    if not ml_predictor.is_trained:
        print("[ML] El modelo no está entrenado. Entrenando primero...")
        ml_predictor.train(historial)
    if ml_predictor.is_trained:
        ml_predictor.evaluate(historial)
    else:
        print("[ML] No se pudo entrenar el modelo para evaluar.")
