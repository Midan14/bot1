# baccarat_bot/utils/metrics.py

"""
Sistema de métricas y monitoreo del bot
Tracking de rendimiento, salud del sistema y estadísticas
"""

import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
from dataclasses import dataclass, field
import logging
import json
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class MetricPoint:
    """Punto individual de métrica"""
    timestamp: float
    value: float
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass  
class PerformanceSnapshot:
    """Snapshot de rendimiento del sistema"""
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    disk_usage_mb: float
    active_threads: int
    timestamp: float

class MetricsCollector:
    """Recolector principal de métricas"""
    
    def __init__(self, retention_hours: int = 24):
        self.retention_hours = retention_hours
        self.start_time = time.time()
        
        # Almacenes de métricas
        self.signals_metrics = defaultdict(deque)  # Por mesa
        self.performance_metrics = deque()  # Performance del sistema
        self.response_time_metrics = deque()  # Tiempos de respuesta
        self.error_metrics = deque()  # Errores por tipo
        
        # Contadores agregados
        self.counters = defaultdict(int)
        self.gauges = defaultdict(float)
        
        # Configuración de thresholds
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'response_time': 5.0,
            'error_rate': 0.05
        }
        
        # Lock para thread safety
        self.lock = threading.RLock()
        
        # Iniciar recolector de performance
        self.performance_thread = None
        self.running = False
        
        logger.info("📊 MetricsCollector inicializado")
    
    def start(self):
        """Inicia el recolector de métricas"""
        if not self.running:
            self.running = True
            self.performance_thread = threading.Thread(
                target=self._performance_collector,
                daemon=True
            )
            self.performance_thread.start()
            logger.info("🔄 Recolector de métricas iniciado")
    
    def stop(self):
        """Detiene el recolector de métricas"""
        self.running = False
        if self.performance_thread:
            self.performance_thread.join(timeout=5)
        logger.info("⏹️ Recolector de métricas detenido")
    
    def _performance_collector(self):
        """Hilo que recolecta métricas de performance cada 30 segundos"""
        while self.running:
            try:
                self.record_performance_snapshot()
                time.sleep(30)
            except Exception as e:
                logger.error(f"Error en recolector de performance: {e}")
                time.sleep(5)
    
    def record_signal_sent(self, mesa: str, success: bool = True, 
                          response_time: float = 0.0):
        """Registra una señal enviada"""
        with self.lock:
            now = time.time()
            
            # Métrica de señal
            metric = MetricPoint(
                timestamp=now,
                value=1.0 if success else 0.0,
                tags={'mesa': mesa, 'type': 'signal_sent'}
            )
            self.signals_metrics[mesa].append(metric)
            
            # Contadores
            self.counters['signals_total'] += 1
            self.counters['signals_success'] += 1 if success else 0
            
            # Tiempo de respuesta
            if response_time > 0:
                self.response_time_metrics.append(
                    MetricPoint(now, response_time, {'operation': 'signal_send'})
                )
            
            # Limpiar métricas antiguas
            self._cleanup_old_metrics(now)
            
    def record_error(self, error_type: str, error_message: str):
        """Registra un error"""
        with self.lock:
            now = time.time()
            
            metric = MetricPoint(
                timestamp=now,
                value=1.0,
                tags={
                    'type': 'error',
                    'error_type': error_type,
                    'message': error_message[:100]  # Truncar mensaje largo
                }
            )
            self.error_metrics.append(metric)
            
            self.counters['errors_total'] += 1
            self.counters[f'errors_{error_type}'] += 1
    
    def record_performance_snapshot(self):
        """Registra snapshot de performance del sistema"""
        try:
            process = psutil.Process()
            
            # Métricas del sistema
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_info = psutil.virtual_memory()
            disk_usage = psutil.disk_usage('/')
            active_threads = threading.active_count()
            
            # Métricas del proceso
            process_memory = process.memory_info()
            process_cpu = process.cpu_percent()
            
            snapshot = PerformanceSnapshot(
                cpu_percent=cpu_percent,
                memory_percent=memory_info.percent,
                memory_mb=process_memory.rss / 1024 / 1024,
                disk_usage_mb=disk_usage.used / 1024 / 1024,
                active_threads=active_threads,
                timestamp=time.time()
            )
            
            with self.lock:
                self.performance_metrics.append(snapshot)
                
                # Actualizar gauges
                self.gauges['cpu_percent'] = cpu_percent
                self.gauges['memory_percent'] = memory_info.percent
                self.gauges['memory_mb'] = process_memory.rss / 1024 / 1024
                
                # Verificar thresholds
                self._check_performance_alerts(snapshot)
                
                # Limpiar métricas antiguas
                self._cleanup_old_metrics(snapshot.timestamp)
                
        except Exception as e:
            logger.error(f"Error registrando performance snapshot: {e}")
    
    def _check_performance_alerts(self, snapshot: PerformanceSnapshot):
        """Verifica si las métricas superan los thresholds"""
        alerts = []
        
        if snapshot.cpu_percent > self.thresholds['cpu_percent']:
            alerts.append(f"CPU alto: {snapshot.cpu_percent:.1f}%")
        
        if snapshot.memory_percent > self.thresholds['memory_percent']:
            alerts.append(f"Memoria alta: {snapshot.memory_percent:.1f}%")
        
        if snapshot.memory_mb > 500:  # 500MB threshold
            alerts.append(f"Uso de memoria alto: {snapshot.memory_mb:.1f}MB")
        
        if alerts:
            logger.warning(f"🚨 Alertas de performance: {', '.join(alerts)}")
    
    def _cleanup_old_metrics(self, current_time: float):
        """Limpia métricas antiguas basado en retention"""
        cutoff_time = current_time - (self.retention_hours * 3600)
        
        # Limpiar performance metrics
        while (self.performance_metrics and 
               self.performance_metrics[0].timestamp < cutoff_time):
            self.performance_metrics.popleft()
        
        # Limpiar response time metrics
        while (self.response_time_metrics and
               self.response_time_metrics[0].timestamp < cutoff_time):
            self.response_time_metrics.popleft()
        
        # Limpiar error metrics
        while (self.error_metrics and
               self.error_metrics[0].timestamp < cutoff_time):
            self.error_metrics.popleft()
        
        # Limpiar signals metrics por mesa
        for mesa in list(self.signals_metrics.keys()):
            mesa_metrics = self.signals_metrics[mesa]
            while (mesa_metrics and mesa_metrics[0].timestamp < cutoff_time):
                mesa_metrics.popleft()
            
            # Remover mesa si no tiene métricas
            if not mesa_metrics:
                del self.signals_metrics[mesa]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Obtiene el estado de salud del sistema"""
        with self.lock:
            now = time.time()
            uptime_hours = (now - self.start_time) / 3600
            
            # Calcular métricas agregadas
            error_rate = self._calculate_error_rate()
            signal_success_rate = self._calculate_signal_success_rate()
            avg_response_time = self._calculate_avg_response_time()
            
            # Performance actual
            latest_performance = self.performance_metrics[-1] if self.performance_metrics else None
            
            # Determinar estado general
            status = self._determine_health_status(
                error_rate, signal_success_rate, latest_performance
            )
            
            return {
                'status': status,
                'uptime_hours': round(uptime_hours, 2),
                'timestamp': now,
                'metrics': {
                    'error_rate': round(error_rate, 3),
                    'signal_success_rate': round(signal_success_rate, 3),
                    'avg_response_time': round(avg_response_time, 2),
                    'cpu_percent': latest_performance.cpu_percent if latest_performance else 0,
                    'memory_percent': latest_performance.memory_percent if latest_performance else 0,
                    'memory_mb': round(latest_performance.memory_mb, 1) if latest_performance else 0,
                },
                'counters': dict(self.counters),
                'gauges': dict(self.gauges)
            }
    
    def _calculate_error_rate(self) -> float:
        """Calcula la tasa de errores"""
        if not self.error_metrics:
            return 0.0
        
        # Errores en la última hora
        one_hour_ago = time.time() - 3600
        recent_errors = sum(
            1 for m in self.error_metrics 
            if m.timestamp >= one_hour_ago
        )
        
        # Total de operaciones en la última hora (aproximado)
        recent_operations = self.counters['signals_total']
        
        return recent_errors / max(1, recent_operations)
    
    def _calculate_signal_success_rate(self) -> float:
        """Calcula la tasa de éxito de señales"""
        if self.counters['signals_total'] == 0:
            return 1.0
        
        return self.counters['signals_success'] / self.counters['signals_total']
    
    def _calculate_avg_response_time(self) -> float:
        """Calcula el tiempo promedio de respuesta"""
        if not self.response_time_metrics:
            return 0.0
        
        recent_times = [m.value for m in self.response_time_metrics[-10:]]
        return sum(recent_times) / len(recent_times)
    
    def _determine_health_status(self, error_rate: float, 
                                success_rate: float,
                                performance: Optional[PerformanceSnapshot]) -> str:
        """Determina el estado de salud general"""
        if error_rate > 0.1 or success_rate < 0.5:
            return "critical"
        elif error_rate > 0.05 or success_rate < 0.7:
            return "degraded"
        elif performance and (
            performance.cpu_percent > 90 or 
            performance.memory_percent > 90
        ):
            return "warning"
        else:
            return "healthy"
    
    def get_performance_metrics(self, hours: int = 1) -> Dict[str, Any]:
        """Obtiene métricas de performance de las últimas N horas"""
        with self.lock:
            cutoff_time = time.time() - (hours * 3600)
            
            # Filtrar métricas recientes
            recent_performance = [
                p for p in self.performance_metrics 
                if p.timestamp >= cutoff_time
            ]
            
            if not recent_performance:
                return {}
            
            # Calcular estadísticas
            cpu_values = [p.cpu_percent for p in recent_performance]
            memory_values = [p.memory_percent for p in recent_performance]
            
            return {
                'period_hours': hours,
                'samples': len(recent_performance),
                'cpu': {
                    'avg': sum(cpu_values) / len(cpu_values),
                    'max': max(cpu_values),
                    'min': min(cpu_values)
                },
                'memory': {
                    'avg': sum(memory_values) / len(memory_values),
                    'max': max(memory_values),
                    'min': min(memory_values)
                },
                'latest': {
                    'cpu_percent': recent_performance[-1].cpu_percent,
                    'memory_percent': recent_performance[-1].memory_percent,
                    'memory_mb': recent_performance[-1].memory_mb,
                    'timestamp': recent_performance[-1].timestamp
                }
            }
    
    def get_signal_statistics(self, mesa: Optional[str] = None) -> Dict[str, Any]:
        """Obtiene estadísticas de señales"""
        with self.lock:
            if mesa:
                metrics = list(self.signals_metrics.get(mesa, []))
            else:
                # Todas las mesas
                metrics = []
                for mesa_metrics in self.signals_metrics.values():
                    metrics.extend(list(mesa_metrics))
            
            if not metrics:
                return {}
            
            # Filtrar últimas 24 horas
            cutoff_time = time.time() - 86400
            recent_metrics = [m for m in metrics if m.timestamp >= cutoff_time]
            
            if not recent_metrics:
                return {}
            
            # Calcular estadísticas
            total_signals = len(recent_metrics)
            successful_signals = sum(1 for m in recent_metrics if m.value == 1.0)
            
            return {
                'total_signals': total_signals,
                'successful_signals': successful_signals,
                'success_rate': successful_signals / total_signals,
                'mesas_activas': len(self.signals_metrics),
                'ultimo_signal': max(m.timestamp for m in recent_metrics)
            }
    
    def export_metrics(self, filepath: str) -> bool:
        """Exporta métricas a archivo JSON"""
        try:
            data = {
                'export_time': time.time(),
                'health_status': self.get_health_status(),
                'performance_1h': self.get_performance_metrics(1),
                'performance_24h': self.get_performance_metrics(24),
                'signal_stats': self.get_signal_statistics(),
                'counters': dict(self.counters),
                'gauges': dict(self.gauges)
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"📁 Métricas exportadas a {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error exportando métricas: {e}")
            return False
    
    def reset_counters(self):
        """Reinicia todos los contadores"""
        with self.lock:
            self.counters.clear()
            self.gauges.clear()
            logger.info("🔄 Contadores de métricas reiniciados")


class DatabaseMetricsStore:
    """Almacén de métricas en base de datos"""
    
    def __init__(self, db_path: str = "metrics.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa la base de datos de métricas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                metric_type TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                tags TEXT,
                mesa TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_metrics_type_time 
            ON metrics (metric_type, timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_metrics_mesa_time 
            ON metrics (mesa, timestamp)
        ''')
        
        conn.commit()
        conn.close()
    
    def store_metric(self, metric_type: str, metric_name: str, value: float,
                    tags: Dict[str, str], mesa: Optional[str] = None):
        """Almacena una métrica en la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO metrics 
            (timestamp, metric_type, metric_name, value, tags, mesa)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            time.time(), metric_type, metric_name, value,
            json.dumps(tags), mesa
        ))
        
        conn.commit()
        conn.close()
    
    def get_metrics(self, metric_type: str, hours: int = 24) -> List[Dict]:
        """Obtiene métricas de los últimos N horas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_time = time.time() - (hours * 3600)
        
        cursor.execute('''
            SELECT timestamp, metric_name, value, tags, mesa
            FROM metrics
            WHERE metric_type = ? AND timestamp >= ?
            ORDER BY timestamp DESC
        ''', (metric_type, cutoff_time))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'timestamp': row[0],
                'metric_name': row[1],
                'value': row[2],
                'tags': json.loads(row[3]) if row[3] else {},
                'mesa': row[4]
            })
        
        conn.close()
        return results


# Instancias globales
metrics_collector = MetricsCollector()
metrics_store = DatabaseMetricsStore()

# Funciones de conveniencia
def record_signal_metric(mesa: str, success: bool, response_time: float = 0.0):
    """Función de conveniencia para registrar métricas de señales"""
    metrics_collector.record_signal_sent(mesa, success, response_time)
    
def record_error_metric(error_type: str, error_message: str):
    """Función de conveniencia para registrar errores"""
    metrics_collector.record_error(error_type, error_message)
    
def get_system_health() -> Dict[str, Any]:
    """Función de conveniencia para obtener salud del sistema"""
    return metrics_collector.get_health_status()

def export_system_metrics(filepath: str = "metrics_export.json") -> bool:
    """Función de conveniencia para exportar métricas"""
    return metrics_collector.export_metrics(filepath)

# Auto-inicializar cuando se importe el módulo
metrics_collector.start()