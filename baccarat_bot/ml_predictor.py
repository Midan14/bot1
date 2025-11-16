from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle



class BaccaratMLPredictor:
    def __init__(self):
        self.model = None
        self.is_trained = False
        self.window = 12  # Aumenta la ventana de historial para más contexto

    def evaluate(self, history):
        """
        Evalúa el modelo ML con el historial dado y muestra métricas de precisión.
        """
        X, y = self.prepare_features(history)
        if not self.is_trained or len(X) == 0:
            print(
                "[ML] El modelo no está entrenado o no hay suficientes datos para evaluar."
            )
            return None
        y_pred = self.model.predict(X)
        acc = accuracy_score(y, y_pred)
        print("[ML] Precisión global: {:.2f}%".format(acc * 100))
        print("[ML] Matriz de confusión:")
        print(confusion_matrix(y, y_pred))
        print("[ML] Reporte de clasificación:")
        print(
            classification_report(
                y, y_pred, target_names=['Player', 'Banker', 'Tie']
            )
        )
        return acc

    def prepare_features(self, history, window=None):
        """
        Convierte el historial de resultados en una matriz de características para ML.
        Cada fila representa una secuencia de 'window' jugadas previas.
        history: lista de strings ['Player', 'Banker', 'Tie', ...]
        """
        if window is None:
            window = self.window
        mapping = {
            'Player': 0, 'Banker': 1, 'Tie': 2,
            'P': 0, 'B': 1, 'E': 2
        }
        X, y = [], []
        for i in range(window, len(history)):
            seq = [mapping.get(h, 2) for h in history[i - window:i]]
            target = mapping.get(history[i], 2)
            X.append(seq)
            y.append(target)
        return np.array(X), np.array(y)

    def train(self, history):
        X, y = self.prepare_features(history)
        if len(X) < 30:
            self.is_trained = False
            return
        # Ajuste de hiperparámetros para mayor precisión y balanceo de clases
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=8,
            min_samples_split=3,
            min_samples_leaf=2,
            class_weight='balanced',
            max_features='sqrt',
            random_state=42
        )
        self.model.fit(X, y)
        self.is_trained = True

    def predict_next(self, history):
        if not self.is_trained or len(history) < self.window:
            return None
        mapping = {0: 'Player', 1: 'Banker', 2: 'Tie'}
        mapping_inv = {
            'Player': 0, 'Banker': 1, 'Tie': 2,
            'P': 0, 'B': 1, 'E': 2
        }
        seq = [mapping_inv.get(h, 2) for h in history[-self.window:]]
        X = np.array(seq).reshape(1, -1)
        # Usar probabilidades para mayor confianza
        proba = self.model.predict_proba(X)[0]
        pred = np.argmax(proba)
        # Solo predecir si la probabilidad es razonable (>40%)
        if proba[pred] < 0.4:
            return None
        # Asegurar que la clave es int para evitar errores de tipado
        pred_int = int(pred)
        return mapping.get(pred_int, 'Tie')

    def save(self, path):
        if self.model:
            with open(path, 'wb') as f:
                pickle.dump(self.model, f)

    def load(self, path):
        try:
            with open(path, 'rb') as f:
                self.model = pickle.load(f)
                self.is_trained = True
        except Exception:
            self.is_trained = False
