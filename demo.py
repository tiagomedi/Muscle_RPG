"""
Script de ejemplo rápido para probar el sistema de optimización
"""

import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.optimizer.workout_graph import WorkoutGraph


def quick_demo():
    """Demostración rápida del sistema"""
    print("="*70)
    print("MUSCLE RPG - DEMOSTRACIÓN RÁPIDA")
    print("="*70)
    print()
    
    # Rutas a los datos
    base_path = os.path.dirname(os.path.abspath(__file__))
    exercises_path = os.path.join(base_path, 'src', 'data', 'exercises.json')
    bodyparts_path = os.path.join(base_path, 'src', 'data', 'bodyparts.json')
    
    # Inicializar sistema
    print("1. Inicializando sistema de optimización...")
    graph = WorkoutGraph(exercises_path, bodyparts_path)
    print(f"   ✓ {len(graph.exercises)} ejercicios cargados")
    print(f"   ✓ {len(graph.body_parts)} partes del cuerpo configuradas")
    print()
    
    # Generar programa de 2 semanas como demo
    print("2. Generando programa de 2 semanas (demo)...")
    print("   - 5 días de entrenamiento por semana")
    print("   - 6 ejercicios por día")
    print()
    
    program = graph.generate_8_week_program(
        weeks=2,
        days_per_week=5,
        exercises_per_day=6
    )
    
    # Mostrar semana 1
    print()
    graph.print_schedule(program[1], week=1)
    
    # Exportar
    output_file = 'demo_program.json'
    graph.export_to_json(program, output_file)
    print(f"\n✓ Programa demo exportado a: {output_file}")
    print()
    
    # Estadísticas
    total_exercises = sum(len(ex) for week in program.values() for day in week for ex in day)
    print(f"📊 Total de ejercicios programados: {total_exercises}")
    print(f"📊 Promedio por día: {total_exercises / 10:.1f}")
    print()
    
    print("="*70)
    print("✓ DEMOSTRACIÓN COMPLETADA")
    print("="*70)
    print()
    print("Para usar el sistema completo, ejecuta: python app.py")
    print()


if __name__ == "__main__":
    quick_demo()
