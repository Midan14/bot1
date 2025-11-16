# baccarat_bot/statistics/analyzer.py

import logging
from typing import Dict, List, Any, Optional
from collections import Counter
from datetime import datetime, timedelta
from database.models import db_manager

logger = logging.getLogger(__name__)


class StatisticsAnalyzer:
    """Analizador de estadísticas y tendencias del baccarat"""
    
    def __init__(self):
        self.db = db_manager
    
    def analizar_tendencias_mesa(self, mesa_nombre: str,
                                dias: int = 7) -> Dict[str, Any]:
        """
        Analiza tendencias de una mesa específica en los últimos días
        
        Args:
            mesa_nombre: Nombre de la mesa
            dias: Número de días para el análisis
            
        Returns:
            Diccionario con análisis de tendencias
        """
        # Obtener historial reciente
        historial = self.db.obtener_historial_resultados(mesa_nombre, dias * 200)
        
        if not historial:
            return {
                'mesa': mesa_nombre,
                'error': 'No hay datos suficientes',
                'total_jugadas': 0
            }
        
        # Análisis básico
        resultados = [h['resultado'] for h in historial]
        contador = Counter(resultados)
        total = len(resultados)
        
        # Detectar patrones
        patrones = self._detectar_patrones(resultados)
        
        # Análisis de rachas
        rachas = self._analizar_rachas(resultados)
        
        # Tendencia actual
        tendencia_actual = self._calcular_tendencia_actual(resultados)
        
        return {
            'mesa': mesa_nombre,
            'total_jugadas': total,
            'distribucion': {
                'banca': contador.get('B', 0),
                'jugador': contador.get('P', 0),
                'empate': contador.get('E', 0),
                'porcentaje_banca': (contador.get('B', 0) / total * 100),
                'porcentaje_jugador': (contador.get('P', 0) / total * 100),
                'porcentaje_empate': (contador.get('E', 0) / total * 100)
            },
            'rachas': rachas,
            'patrones': patrones,
            'tendencia_actual': tendencia_actual,
            'ultima_actualizacion': historial[0]['timestamp'] if historial else None
        }
    
    def _detectar_patrones(self, resultados: List[str]) -> Dict[str, Any]:
        """Detecta patrones en la secuencia de resultados"""
        if len(resultados) < 3:
            return {'patrones_detectados': []}
        
        patrones = []
        
        # Patrón de alternancia (B, P, B, P, ...)
        alternancia = 0
        for i in range(1, len(resultados)):
            if (resultados[i] != resultados[i-1] and
                resultados[i] in ['B', 'P']):
                alternancia += 1
            else:
                break
        
        if alternancia >= 3:
            patrones.append({
                'tipo': 'alternancia',
                'longitud': alternancia,
                'descripcion': f'Alternancia de {alternancia} jugadas'
            })
        
        # Patrón de rachas
        racha_actual = 1
        racha_maxima = 1
        racha_tipo = resultados[0] if resultados else ''
        
        for i in range(1, len(resultados)):
            if resultados[i] == resultados[i-1]:
                racha_actual += 1
                racha_maxima = max(racha_maxima, racha_actual)
            else:
                racha_actual = 1
        
        if racha_maxima >= 3:
            patrones.append({
                'tipo': 'racha',
                'longitud': racha_maxima,
                'tipo_racha': racha_tipo,
                'descripcion': f'Racha de {racha_maxima} {racha_tipo}'
            })
        
        return {
            'patrones_detectados': patrones,
            'racha_maxima': racha_maxima,
            'tipo_racha_maxima': racha_tipo
        }
    
    def _analizar_rachas(self, resultados: List[str]) -> Dict[str, Any]:
        """Analiza las rachas en los resultados"""
        if not resultados:
            return {'rachas_banca': [], 'rachas_jugador': [], 'rachas_empate': []}
        
        rachas_banca = []
        rachas_jugador = []
        rachas_empate = []
        racha_actual = 1
        
        for i in range(1, len(resultados)):
            if resultados[i] == resultados[i-1]:
                racha_actual += 1
            else:
                if resultados[i-1] == 'B' and racha_actual >= 2:
                    rachas_banca.append(racha_actual)
                elif resultados[i-1] == 'P' and racha_actual >= 2:
                    rachas_jugador.append(racha_actual)
                elif resultados[i-1] == 'E' and racha_actual >= 2:
                    rachas_empate.append(racha_actual)
                racha_actual = 1
        
        # No olvidar la última racha
        if racha_actual >= 2:
            if resultados[-1] == 'B':
                rachas_banca.append(racha_actual)
            elif resultados[-1] == 'P':
                rachas_jugador.append(racha_actual)
            elif resultados[-1] == 'E':
                rachas_empate.append(racha_actual)
        
        def calcular_stats(rachas):
            if not rachas:
                return {'cantidad': 0, 'promedio': 0, 'maxima': 0}
            return {
                'cantidad': len(rachas),
                'promedio': sum(rachas) / len(rachas),
                'maxima': max(rachas)
            }
        
        return {
            'rachas_banca': calcular_stats(rachas_banca),
            'rachas_jugador': calcular_stats(rachas_jugador),
            'rachas_empate': calcular_stats(rachas_empate)
        }
    
    def _calcular_tendencia_actual(self, resultados: List[str]) -> Dict[str, Any]:
        """Calcula la tendencia actual basada en los últimos resultados"""
        if len(resultados) < 5:
            return {'tendencia': 'insuficientes_datos'}
        
        ultimos_5 = resultados[-5:]
        contador = Counter(ultimos_5)
        
        # Determinar tendencia
        if contador['B'] >= 3:
            tendencia = 'favor_banca'
        elif contador['P'] >= 3:
            tendencia = 'favor_jugador'
        elif contador['E'] >= 2:
            tendencia = 'muchas_empates'
        else:
            tendencia = 'equilibrado'
        
        return {
            'tendencia': tendencia,
            'ultimos_5': ultimos_5,
            'distribucion_ultimos_5': dict(contador)
        }
    
    def generar_reporte_general(self) -> Dict[str, Any]:
        """Genera un reporte general de todas las mesas"""
        estadisticas = self.db.obtener_todas_las_estadisticas()
        
        if not estadisticas:
            return {'error': 'No hay datos disponibles'}
        
        # Resumen general
        total_jugadas = sum(e['total_jugadas'] for e in estadisticas)
        total_senales = sum(e['senales_generadas'] for e in estadisticas)
        total_aciertos = sum(e['senales_acertadas'] for e in estadisticas)
        
        # Top mesas por actividad
        mesas_mas_activas = sorted(
            estadisticas,
            key=lambda x: x['total_jugadas'],
            reverse=True
        )[:5]
        
        # Top mesas por precisión de señales
        mesas_mejores_senales = [
            e for e in estadisticas if e['senales_generadas'] > 0
        ]
        mesas_mejores_senales = sorted(
            mesas_mejores_senales,
            key=lambda x: x['precision_senales'],
            reverse=True
        )[:5]
        
        return {
            'resumen_general': {
                'total_mesas_monitoreadas': len(estadisticas),
                'total_jugadas': total_jugadas,
                'total_senales_generadas': total_senales,
                'precision_general': (total_aciertos / total_senales * 100)
                if total_senales > 0 else 0
            },
            'distribucion_global': {
                'total_banca': sum(e['banca_victorias'] for e in estadisticas),
                'total_jugador': sum(e['jugador_victorias'] for e in estadisticas),
                'total_empate': sum(e['empates'] for e in estadisticas)
            },
            'top_mesas_activas': mesas_mas_activas,
            'top_mesas_precision': mesas_mejores_senales,
            'fecha_generacion': datetime.now().isoformat()
        }
    
    def generar_alertas(self) -> List[Dict[str, Any]]:
        """Genera alertas basadas en condiciones especiales"""
        alertas = []
        estadisticas = self.db.obtener_todas_las_estadisticas()
        
        for est in estadisticas:
            # Alerta por mala precisión
            if (est['senales_generadas'] > 10 and
                est['precision_senales'] < 30):
                alertas.append({
                    'tipo': 'baja_precision',
                    'mesa': est['mesa'],
                    'precision': est['precision_senales'],
                    'mensaje': f'Baja precisión en {est["mesa"]}: {est["precision_senales"]:.1f}%'
                })
            
            # Alerta por mesa muy activa
            if est['total_jugadas'] > 1000:
                alertas.append({
                    'tipo': 'alta_actividad',
                    'mesa': est['mesa'],
                    'jugadas': est['total_jugadas'],
                    'mensaje': f'Alta actividad en {est["mesa"]}: {est["total_jugadas"]} jugadas'
                })
            
            # Análisis de tendencia
            tendencia = self.analizar_tendencias_mesa(est['mesa'], 1)
            if 'tendencia_actual' in tendencia:
                tend = tendencia['tendencia_actual']['tendencia']
                if tend in ['favor_banca', 'favor_jugador']:
                    alertas.append({
                        'tipo': 'tendencia_fuerte',
                        'mesa': est['mesa'],
                        'tendencia': tend,
                        'mensaje': f'Tendencia fuerte detectada en {est["mesa"]}: {tend}'
                    })
        
        return alertas


# Instancia global del analizador
analyzer = StatisticsAnalyzer()