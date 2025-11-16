# baccarat_bot/database/models.py

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import sqlite3
import json
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gestor de base de datos para almacenar resultados y estadísticas"""
    
    def __init__(self, db_path: str = "baccarat_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa la base de datos con las tablas necesarias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de mesas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mesas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                url TEXT NOT NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de resultados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resultados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mesa_id INTEGER,
                resultado TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mesa_id) REFERENCES mesas (id)
            )
        ''')
        
        # Tabla de señales enviadas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS senales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mesa_id INTEGER,
                tipo_senal TEXT NOT NULL,
                resultado_recomendado TEXT NOT NULL,
                historial_json TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                exito BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (mesa_id) REFERENCES mesas (id)
            )
        ''')
        
        # Tabla de estadísticas por mesa
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estadisticas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mesa_id INTEGER UNIQUE,
                total_jugadas INTEGER DEFAULT 0,
                banca_victorias INTEGER DEFAULT 0,
                jugador_victorias INTEGER DEFAULT 0,
                empates INTEGER DEFAULT 0,
                senales_generadas INTEGER DEFAULT 0,
                senales_acertadas INTEGER DEFAULT 0,
                ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mesa_id) REFERENCES mesas (id)
            )
        ''')
        
        # Tabla de configuración de estrategias
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estrategias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                configuracion_json TEXT NOT NULL,
                activa BOOLEAN DEFAULT TRUE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Base de datos inicializada correctamente")
    
    def registrar_mesa(self, nombre: str, url: str) -> int:
        """Registra una nueva mesa o retorna el ID si ya existe"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO mesas (nombre, url) VALUES (?, ?)",
                (nombre, url)
            )
            cursor.execute("SELECT id FROM mesas WHERE nombre = ?", (nombre,))
            mesa_id = cursor.fetchone()[0]
            conn.commit()
            return mesa_id
        finally:
            conn.close()
    
    def registrar_resultado(self, mesa_nombre: str, resultado: str) -> bool:
        """Registra un nuevo resultado para una mesa"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Obtener ID de la mesa
            cursor.execute(
                "SELECT id FROM mesas WHERE nombre = ?",
                (mesa_nombre,)
            )
            mesa_row = cursor.fetchone()
            
            if not mesa_row:
                logger.error(f"Mesa no encontrada: {mesa_nombre}")
                return False
            
            mesa_id = mesa_row[0]
            
            # Insertar resultado
            cursor.execute(
                "INSERT INTO resultados (mesa_id, resultado) VALUES (?, ?)",
                (mesa_id, resultado)
            )
            
            # Actualizar estadísticas
            self._actualizar_estadisticas(cursor, mesa_id, resultado)
            
            conn.commit()
            logger.info(f"Resultado registrado: {mesa_nombre} -> {resultado}")
            return True
            
        except Exception as e:
            logger.error(f"Error al registrar resultado: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def _actualizar_estadisticas(self, cursor, mesa_id: int, resultado: str):
        """Actualiza las estadísticas de una mesa"""
        cursor.execute(
            """INSERT INTO estadisticas 
               (mesa_id, total_jugadas, banca_victorias, jugador_victorias, empates)
               VALUES (?, 1, 0, 0, 0)
               ON CONFLICT(mesa_id) DO UPDATE SET
               total_jugadas = total_jugadas + 1,
               banca_victorias = banca_victorias + 
                   CASE WHEN ? = 'B' THEN 1 ELSE 0 END,
               jugador_victorias = jugador_victorias + 
                   CASE WHEN ? = 'P' THEN 1 ELSE 0 END,
               empates = empates + CASE WHEN ? = 'E' THEN 1 ELSE 0 END,
               ultima_actualizacion = CURRENT_TIMESTAMP""",
            (mesa_id, resultado, resultado, resultado)
        )
    
    def registrar_senal(self, mesa_nombre: str, tipo_senal: str,
                       resultado_recomendado: str, historial: list,
                       exito: bool = True) -> bool:
        """Registra una señal enviada"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Obtener ID de la mesa
            cursor.execute(
                "SELECT id FROM mesas WHERE nombre = ?",
                (mesa_nombre,)
            )
            mesa_row = cursor.fetchone()
            
            if not mesa_row:
                logger.error(f"Mesa no encontrada: {mesa_nombre}")
                return False
            
            mesa_id = mesa_row[0]
            
            # Insertar señal
            cursor.execute(
                """INSERT INTO senales 
                   (mesa_id, tipo_senal, resultado_recomendado, 
                    historial_json, exito)
                   VALUES (?, ?, ?, ?, ?)""",
                (mesa_id, tipo_senal, resultado_recomendado,
                 json.dumps(historial), exito)
            )
            
            # Actualizar contador de señales en estadísticas
            cursor.execute(
                """UPDATE estadisticas 
                   SET senales_generadas = senales_generadas + 1,
                       senales_acertadas = senales_acertadas + 
                           CASE WHEN ? THEN 1 ELSE 0 END
                   WHERE mesa_id = ?""",
                (exito, mesa_id)
            )
            
            conn.commit()
            logger.info(f"Señal registrada: {mesa_nombre} -> {tipo_senal}")
            return True
            
        except Exception as e:
            logger.error(f"Error al registrar señal: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def obtener_estadisticas_mesa(self, mesa_nombre: str) -> Optional[Dict[str, Any]]:
        """Obtiene estadísticas de una mesa específica"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """SELECT e.total_jugadas, e.banca_victorias, 
                          e.jugador_victorias, e.empates, e.senales_generadas,
                          e.senales_acertadas, m.url, e.ultima_actualizacion
                   FROM estadisticas e
                   JOIN mesas m ON e.mesa_id = m.id
                   WHERE m.nombre = ?""",
                (mesa_nombre,)
            )
            
            row = cursor.fetchone()
            if not row:
                return None
            
            return {
                'mesa': mesa_nombre,
                'total_jugadas': row[0],
                'banca_victorias': row[1],
                'jugador_victorias': row[2],
                'empates': row[3],
                'senales_generadas': row[4],
                'senales_acertadas': row[5],
                'url': row[6],
                'ultima_actualizacion': row[7],
                'win_rate_banca': (row[1] / row[0] * 100) if row[0] > 0 else 0,
                'win_rate_jugador': (row[2] / row[0] * 100) if row[0] > 0 else 0,
                'win_rate_empates': (row[3] / row[0] * 100) if row[0] > 0 else 0,
                'precision_senales': (row[5] / row[4] * 100) if row[4] > 0 else 0
            }
            
        finally:
            conn.close()
    
    def obtener_historial_resultados(self, mesa_nombre: str,
                                    limite: int = 100) -> list:
        """Obtiene el historial de resultados de una mesa"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """SELECT r.resultado, r.timestamp
                   FROM resultados r
                   JOIN mesas m ON r.mesa_id = m.id
                   WHERE m.nombre = ?
                   ORDER BY r.timestamp DESC
                   LIMIT ?""",
                (mesa_nombre, limite)
            )
            
            return [{'resultado': row[0], 'timestamp': row[1]}
                    for row in cursor.fetchall()]
            
        finally:
            conn.close()
    
    def obtener_todas_las_estadisticas(self) -> list:
        """Obtiene estadísticas de todas las mesas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                """SELECT m.nombre, e.total_jugadas, e.banca_victorias,
                          e.jugador_victorias, e.empates, e.senales_generadas,
                          e.senales_acertadas, e.ultima_actualizacion
                   FROM mesas m
                   LEFT JOIN estadisticas e ON m.id = e.mesa_id
                   ORDER BY m.nombre"""
            )
            
            resultados = []
            for row in cursor.fetchall():
                total = row[1] or 0
                resultados.append({
                    'mesa': row[0],
                    'total_jugadas': total,
                    'banca_victorias': row[2] or 0,
                    'jugador_victorias': row[3] or 0,
                    'empates': row[4] or 0,
                    'senales_generadas': row[5] or 0,
                    'senales_acertadas': row[6] or 0,
                    'ultima_actualizacion': row[7],
                    'win_rate_banca': (row[2] / total * 100) if total > 0 else 0,
                    'win_rate_jugador': (row[3] / total * 100) if total > 0 else 0,
                    'precision_senales': (row[6] / row[5] * 100)
                    if row[5] and row[5] > 0 else 0
                })
            
            return resultados
            
        finally:
            conn.close()
    
    def limpiar_datos_antiguos(self, dias: int = 30):
        """Limpia datos antiguos para mantener la base de datos optimizada"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            fecha_limite = datetime.now() - timedelta(days=dias)
            
            # Eliminar resultados antiguos
            cursor.execute(
                "DELETE FROM resultados WHERE timestamp < ?",
                (fecha_limite,)
            )
            
            # Eliminar señales antiguas
            cursor.execute(
                "DELETE FROM senales WHERE timestamp < ?",
                (fecha_limite,)
            )
            
            conn.commit()
            logger.info(f"Datos antiguos eliminados (más de {dias} días)")
            
        except Exception as e:
            logger.error(f"Error al limpiar datos antiguos: {e}")
            conn.rollback()
        finally:
            conn.close()


# Instancia global del gestor de base de datos
db_manager = DatabaseManager()
