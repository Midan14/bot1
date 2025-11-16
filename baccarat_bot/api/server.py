# baccarat_bot/api/server.py

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import logging
from datetime import datetime
import json
from typing import Dict, Any

from database.models import db_manager
from stats_module.analyzer import analyzer
from tables import MESA_NOMBRES

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Dashboard HTML template
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Baccarat Bot Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
        .table-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
        }
        .status-active { background-color: #28a745; }
        .status-inactive { background-color: #dc3545; }
        .alert {
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
        }
        .alert-warning {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
        }
        .alert-info {
            background-color: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎰 Baccarat Bot Dashboard</h1>
            <p>Monitoreo en tiempo real de mesas de Baccarat</p>
        </div>
        
        <div id="alerts"></div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="total-mesas">0</div>
                <div class="stat-label">Mesas Monitoreadas</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="total-jugadas">0</div>
                <div class="stat-label">Total Jugadas</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="total-senales">0</div>
                <div class="stat-label">Señales Generadas</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="precision-general">0%</div>
                <div class="stat-label">Precisión General</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h2>Distribución de Resultados</h2>
            <canvas id="distribucion-chart" width="400" height="200"></canvas>
        </div>
        
        <div class="table-container">
            <h2>Estadísticas por Mesa</h2>
            <table id="mesas-table">
                <thead>
                    <tr>
                        <th>Mesa</th>
                        <th>Jugadas</th>
                        <th>Banca</th>
                        <th>Jugador</th>
                        <th>Empate</th>
                        <th>Señales</th>
                        <th>Precisión</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody id="mesas-tbody">
                </tbody>
            </table>
        </div>
        
        <div class="chart-container">
            <h2>Top 5 Mesas Más Activas</h2>
            <canvas id="top-mesas-chart" width="400" height="200"></canvas>
        </div>
    </div>

    <script>
        let distribucionChart, topMesasChart;
        
        function actualizarDashboard() {
            Promise.all([
                fetch('/api/estadisticas').then(r => r.json()),
                fetch('/api/reporte-general').then(r => r.json()),
                fetch('/api/alertas').then(r => r.json())
            ]).then(([estadisticas, reporte, alertas]) => {
                actualizarResumen(reporte);
                actualizarTabla(estadisticas);
                actualizarGraficos(reporte);
                actualizarAlertas(alertas);
            }).catch(error => {
                console.error('Error actualizando dashboard:', error);
            });
        }
        
        function actualizarResumen(reporte) {
            document.getElementById('total-mesas').textContent = reporte.resumen_general.total_mesas_monitoreadas;
            document.getElementById('total-jugadas').textContent = reporte.resumen_general.total_jugadas;
            document.getElementById('total-senales').textContent = reporte.resumen_general.total_senales_generadas;
            document.getElementById('precision-general').textContent = reporte.resumen_general.precision_general.toFixed(1) + '%';
        }
        
        function actualizarTabla(estadisticas) {
            const tbody = document.getElementById('mesas-tbody');
            tbody.innerHTML = '';
            
            estadisticas.forEach(mesa => {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${mesa.mesa}</td>
                    <td>${mesa.total_jugadas}</td>
                    <td>${mesa.banca_victorias} (${mesa.win_rate_banca.toFixed(1)}%)</td>
                    <td>${mesa.jugador_victorias} (${mesa.win_rate_jugador.toFixed(1)}%)</td>
                    <td>${mesa.empates}</td>
                    <td>${mesa.senales_generadas}</td>
                    <td>${mesa.precision_senales.toFixed(1)}%</td>
                    <td>
                        <span class="status-indicator ${mesa.total_jugadas > 0 ? 'status-active' : 'status-inactive'}"></span>
                        ${mesa.total_jugadas > 0 ? 'Activa' : 'Inactiva'}
                    </td>
                `;
            });
        }
        
        function actualizarGraficos(reporte) {
            // Gráfico de distribución
            const distribucionCtx = document.getElementById('distribucion-chart').getContext('2d');
            if (distribucionChart) distribucionChart.destroy();
            
            distribucionChart = new Chart(distribucionCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Banca', 'Jugador', 'Empate'],
                    datasets: [{
                        data: [
                            reporte.distribucion_global.total_banca,
                            reporte.distribucion_global.total_jugador,
                            reporte.distribucion_global.total_empate
                        ],
                        backgroundColor: ['#28a745', '#dc3545', '#ffc107']
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
            
            // Gráfico de top mesas
            const topMesasCtx = document.getElementById('top-mesas-chart').getContext('2d');
            if (topMesasChart) topMesasChart.destroy();
            
            const topMesas = reporte.top_mesas_activas.slice(0, 5);
            topMesasChart = new Chart(topMesasCtx, {
                type: 'bar',
                data: {
                    labels: topMesas.map(m => m.mesa),
                    datasets: [{
                        label: 'Jugadas',
                        data: topMesas.map(m => m.total_jugadas),
                        backgroundColor: '#667eea'
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
        
        function actualizarAlertas(alertas) {
            const alertsDiv = document.getElementById('alerts');
            alertsDiv.innerHTML = '';
            
            if (alertas.length === 0) {
                alertsDiv.innerHTML = '<div class="alert alert-info">No hay alertas activas</div>';
                return;
            }
            
            alertas.forEach(alerta => {
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert alert-warning';
                alertDiv.textContent = alerta.mensaje;
                alertsDiv.appendChild(alertDiv);
            });
        }
        
        // Actualizar cada 30 segundos
        actualizarDashboard();
        setInterval(actualizarDashboard, 30000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    """Renderiza el dashboard principal"""
    return render_template_string(DASHBOARD_TEMPLATE)

@app.route('/api/estadisticas')
def get_estadisticas():
    """Obtiene estadísticas de todas las mesas"""
    try:
        estadisticas = db_manager.obtener_todas_las_estadisticas()
        return jsonify(estadisticas)
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/estadisticas/<mesa_nombre>')
def get_estadisticas_mesa(mesa_nombre):
    """Obtiene estadísticas de una mesa específica"""
    try:
        estadisticas = db_manager.obtener_estadisticas_mesa(mesa_nombre)
        if not estadisticas:
            return jsonify({'error': 'Mesa no encontrada'}), 404
        return jsonify(estadisticas)
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas de mesa: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tendencias/<mesa_nombre>')
def get_tendencias_mesa(mesa_nombre):
    """Obtiene análisis de tendencias de una mesa"""
    try:
        dias = request.args.get('dias', 7, type=int)
        tendencias = analyzer.analizar_tendencias_mesa(mesa_nombre, dias)
        return jsonify(tendencias)
    except Exception as e:
        logger.error(f"Error obteniendo tendencias: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reporte-general')
def get_reporte_general():
    """Obtiene reporte general de todas las mesas"""
    try:
        reporte = analyzer.generar_reporte_general()
        return jsonify(reporte)
    except Exception as e:
        logger.error(f"Error obteniendo reporte general: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/alertas')
def get_alertas():
    """Obtiene alertas activas"""
    try:
        alertas = analyzer.generar_alertas()
        return jsonify(alertas)
    except Exception as e:
        logger.error(f"Error obteniendo alertas: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/mesas')
def get_mesas():
    """Obtiene lista de todas las mesas"""
    try:
        mesas = [{'nombre': nombre} for nombre in MESA_NOMBRES]
        return jsonify(mesas)
    except Exception as e:
        logger.error(f"Error obteniendo mesas: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/historial/<mesa_nombre>')
def get_historial(mesa_nombre):
    """Obtiene historial de resultados de una mesa"""
    try:
        limite = request.args.get('limite', 100, type=int)
        historial = db_manager.obtener_historial_resultados(mesa_nombre, limite)
        return jsonify(historial)
    except Exception as e:
        logger.error(f"Error obteniendo historial: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/senales', methods=['POST'])
def registrar_senal():
    """Registra una nueva señal"""
    try:
        data = request.get_json()
        
        required_fields = ['mesa', 'tipo_senal', 'resultado_recomendado', 'historial']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Faltan campos requeridos'}), 400
        
        exito = db_manager.registrar_senal(
            mesa_nombre=data['mesa'],
            tipo_senal=data['tipo_senal'],
            resultado_recomendado=data['resultado_recomendado'],
            historial=data['historial'],
            exito=data.get('exito', True)
        )
        
        return jsonify({'exito': exito})
    except Exception as e:
        logger.error(f"Error registrando señal: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/resultado', methods=['POST'])
def registrar_resultado():
    """Registra un nuevo resultado"""
    try:
        data = request.get_json()
        
        if 'mesa' not in data or 'resultado' not in data:
            return jsonify({'error': 'Faltan campos requeridos'}), 400
        
        exito = db_manager.registrar_resultado(
            mesa_nombre=data['mesa'],
            resultado=data['resultado']
        )
        
        return jsonify({'exito': exito})
    except Exception as e:
        logger.error(f"Error registrando resultado: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Verificación de salud del servicio"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

def iniciar_servidor(host='0.0.0.0', port=5000, debug=False):
    """Inicia el servidor Flask"""
    logger.info(f"Iniciando servidor API en {host}:{port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    iniciar_servidor(debug=True)