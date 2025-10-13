"""
Visualización del Grafo de Optimización de Ejercicios
Genera visualizaciones y estadísticas del programa de entrenamiento
"""

import json
import matplotlib.pyplot as plt
import networkx as nx
from typing import Dict, List
from collections import defaultdict
import os


class WorkoutVisualizer:
    """Visualiza el grafo de ejercicios y estadísticas del programa"""
    
    def __init__(self, program_path: str):
        self.program_path = program_path
        self.program_data = None
        self._load_program()
    
    def _load_program(self):
        """Carga el programa de entrenamiento desde JSON"""
        with open(self.program_path, 'r') as f:
            self.program_data = json.load(f)
    
    def create_graph_visualization(self, week: int, output_path: str):
        """Crea una visualización del grafo para una semana específica"""
        G = nx.DiGraph()
        week_key = f'week_{week}'
        
        if week_key not in self.program_data:
            print(f"Semana {week} no encontrada")
            return
        
        week_data = self.program_data[week_key]
        
        # Crear nodos y aristas
        previous_day_exercises = []
        
        for day in week_data:
            day_num = day['day']
            exercises = day['exercises']
            
            for exercise in exercises:
                node_id = f"D{day_num}_{exercise['id'][:6]}"
                G.add_node(
                    node_id,
                    label=exercise['name'][:20],
                    day=day_num,
                    cost=exercise['stamina_cost'],
                    body_parts=exercise['body_parts']
                )
                
                # Conectar con ejercicios del día anterior
                for prev_ex in previous_day_exercises:
                    # Conectar si comparten partes del cuerpo (relación de recuperación)
                    if set(exercise['body_parts']) & set(prev_ex['body_parts']):
                        G.add_edge(
                            f"D{day_num-1}_{prev_ex['id'][:6]}",
                            node_id,
                            weight=exercise['stamina_cost']
                        )
            
            previous_day_exercises = exercises
        
        # Configurar layout
        plt.figure(figsize=(16, 10))
        pos = self._hierarchical_layout(G)
        
        # Colorear nodos por día
        colors = []
        for node in G.nodes():
            day = G.nodes[node]['day']
            colors.append(plt.cm.viridis(day / 5))
        
        # Dibujar el grafo
        nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=800, alpha=0.9)
        nx.draw_networkx_edges(G, pos, alpha=0.3, arrows=True, arrowsize=10)
        
        # Etiquetas
        labels = {node: G.nodes[node]['label'] for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=6)
        
        plt.title(f'Grafo de Ejercicios - Semana {week}', fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Grafo guardado en: {output_path}")
        plt.close()
    
    def _hierarchical_layout(self, G: nx.DiGraph) -> Dict:
        """Crea un layout jerárquico por días"""
        pos = {}
        day_counts = defaultdict(int)
        
        for node in G.nodes():
            day = G.nodes[node]['day']
            x = day_counts[day]
            y = -day  # Días hacia abajo
            pos[node] = (x * 2, y * 2)
            day_counts[day] += 1
        
        return pos
    
    def plot_stamina_progression(self, output_path: str):
        """Grafica la progresión de uso de estamina a lo largo del programa"""
        weeks = []
        avg_stamina_costs = []
        
        for week_key in sorted(self.program_data.keys()):
            week_num = int(week_key.split('_')[1])
            week_data = self.program_data[week_key]
            
            total_cost = 0
            exercise_count = 0
            
            for day in week_data:
                for exercise in day['exercises']:
                    total_cost += exercise['stamina_cost']
                    exercise_count += 1
            
            avg_cost = total_cost / exercise_count if exercise_count > 0 else 0
            weeks.append(week_num)
            avg_stamina_costs.append(avg_cost)
        
        plt.figure(figsize=(12, 6))
        plt.plot(weeks, avg_stamina_costs, marker='o', linewidth=2, markersize=8)
        plt.xlabel('Semana', fontsize=12)
        plt.ylabel('Costo Promedio de Estamina', fontsize=12)
        plt.title('Progresión de Intensidad del Programa (8 Semanas)', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Gráfico de progresión guardado en: {output_path}")
        plt.close()
    
    def plot_bodypart_distribution(self, output_path: str):
        """Grafica la distribución de ejercicios por parte del cuerpo"""
        bodypart_counts = defaultdict(int)
        
        for week_key in self.program_data.keys():
            week_data = self.program_data[week_key]
            
            for day in week_data:
                for exercise in day['exercises']:
                    for bodypart in exercise['body_parts']:
                        bodypart_counts[bodypart] += 1
        
        bodyparts = list(bodypart_counts.keys())
        counts = list(bodypart_counts.values())
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(bodyparts, counts, color=plt.cm.Set3(range(len(bodyparts))))
        plt.xlabel('Parte del Cuerpo', fontsize=12)
        plt.ylabel('Número de Ejercicios', fontsize=12)
        plt.title('Distribución de Ejercicios por Parte del Cuerpo (8 Semanas)', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Gráfico de distribución guardado en: {output_path}")
        plt.close()
    
    def generate_weekly_report(self, week: int) -> str:
        """Genera un reporte detallado de una semana"""
        week_key = f'week_{week}'
        
        if week_key not in self.program_data:
            return f"Semana {week} no encontrada"
        
        week_data = self.program_data[week_key]
        
        report = f"\n{'='*80}\n"
        report += f"REPORTE DETALLADO - SEMANA {week}\n"
        report += f"{'='*80}\n\n"
        
        total_exercises = 0
        total_stamina = 0
        bodypart_usage = defaultdict(int)
        muscle_usage = defaultdict(int)
        
        for day in week_data:
            day_num = day['day']
            exercises = day['exercises']
            
            report += f"DÍA {day_num}\n"
            report += f"{'-'*80}\n"
            
            if not exercises:
                report += "  Descanso\n\n"
                continue
            
            for idx, exercise in enumerate(exercises, 1):
                total_exercises += 1
                total_stamina += exercise['stamina_cost']
                
                for bp in exercise['body_parts']:
                    bodypart_usage[bp] += 1
                
                for muscle in exercise['target_muscles']:
                    muscle_usage[muscle] += 1
                
                report += f"  {idx}. {exercise['name'].title()}\n"
                report += f"     ID: {exercise['id']}\n"
                report += f"     Partes: {', '.join(exercise['body_parts'])}\n"
                report += f"     Músculos: {', '.join(exercise['target_muscles'])}\n"
                report += f"     Costo: {exercise['stamina_cost']} estamina\n\n"
        
        report += f"\n{'='*80}\n"
        report += f"RESUMEN DE LA SEMANA\n"
        report += f"{'='*80}\n"
        report += f"Total de ejercicios: {total_exercises}\n"
        report += f"Estamina total utilizada: {total_stamina}\n"
        report += f"Promedio de estamina por ejercicio: {total_stamina / total_exercises:.1f}\n\n"
        
        report += "DISTRIBUCIÓN POR PARTE DEL CUERPO:\n"
        for bp, count in sorted(bodypart_usage.items(), key=lambda x: x[1], reverse=True):
            report += f"  - {bp.title()}: {count} ejercicios\n"
        
        report += "\nTOP 5 MÚSCULOS MÁS TRABAJADOS:\n"
        top_muscles = sorted(muscle_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        for muscle, count in top_muscles:
            report += f"  - {muscle.title()}: {count} ejercicios\n"
        
        return report
    
    def generate_all_visualizations(self, output_dir: str):
        """Genera todas las visualizaciones del programa"""
        os.makedirs(output_dir, exist_ok=True)
        
        print("\nGenerando visualizaciones...")
        print("=" * 80)
        
        # Grafo de las primeras 2 semanas
        for week in [1, 2]:
            output_path = os.path.join(output_dir, f'graph_week_{week}.png')
            self.create_graph_visualization(week, output_path)
        
        # Gráfico de progresión
        progression_path = os.path.join(output_dir, 'stamina_progression.png')
        self.plot_stamina_progression(progression_path)
        
        # Distribución por parte del cuerpo
        distribution_path = os.path.join(output_dir, 'bodypart_distribution.png')
        self.plot_bodypart_distribution(distribution_path)
        
        # Reportes semanales
        for week in [1, 4, 8]:
            report = self.generate_weekly_report(week)
            report_path = os.path.join(output_dir, f'report_week_{week}.txt')
            with open(report_path, 'w') as f:
                f.write(report)
            print(f"Reporte semana {week} guardado en: {report_path}")
        
        print("\n" + "=" * 80)
        print("✓ Todas las visualizaciones han sido generadas")


def main():
    """Función principal"""
    import sys
    
    # Ruta al programa generado
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    program_path = os.path.join(base_path, '..', 'workout_program_8weeks.json')
    
    if not os.path.exists(program_path):
        print(f"Error: No se encontró el archivo {program_path}")
        print("Ejecuta primero workout_graph.py para generar el programa")
        sys.exit(1)
    
    # Crear visualizador
    visualizer = WorkoutVisualizer(program_path)
    
    # Generar todas las visualizaciones
    output_dir = os.path.join(base_path, '..', 'visualizations')
    visualizer.generate_all_visualizations(output_dir)


if __name__ == "__main__":
    main()
