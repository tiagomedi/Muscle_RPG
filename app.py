"""
Muscle RPG - Sistema de Optimización de Rutinas de Ejercicio
Aplicación principal que utiliza programación dinámica para crear rutinas óptimas
"""

import os
import sys
from src.optimizer.workout_graph import WorkoutGraph


def print_banner():
    """Imprime el banner de la aplicación"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                       MUSCLE RPG                              ║
    ║          Sistema de Optimización de Entrenamiento            ║
    ║              Usando Programación Dinámica                     ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_menu():
    """Muestra el menú principal"""
    menu = """
    OPCIONES:
    ─────────────────────────────────────────────────────────────────
    1. Generar programa completo de 8 semanas
    2. Generar programa personalizado
    3. Visualizar semana específica
    4. Exportar programa a JSON
    5. Ver estadísticas del programa
    6. Salir
    ─────────────────────────────────────────────────────────────────
    """
    print(menu)


def generate_full_program(graph: WorkoutGraph):
    """Genera un programa completo de 8 semanas"""
    print("\n" + "="*70)
    print("GENERANDO PROGRAMA DE 8 SEMANAS")
    print("="*70 + "\n")
    
    print("Configuración:")
    print("  • Duración: 8 semanas")
    print("  • Días de entrenamiento: 5 por semana")
    print("  • Ejercicios por día: 6")
    print("  • Días de descanso: 2 por semana")
    print()
    
    input("Presiona Enter para comenzar...")
    
    program = graph.generate_8_week_program(
        weeks=8,
        days_per_week=5,
        exercises_per_day=6
    )
    
    # Mostrar resumen
    print("\n" + "="*70)
    print("PROGRAMA GENERADO EXITOSAMENTE")
    print("="*70 + "\n")
    
    total_exercises = sum(
        len(ex) 
        for week in program.values() 
        for day in week 
        for ex in day
    )
    
    print(f"✓ Total de ejercicios programados: {total_exercises}")
    print(f"✓ Promedio por día: {total_exercises / (8 * 5):.1f}")
    
    return program


def generate_custom_program(graph: WorkoutGraph):
    """Genera un programa personalizado"""
    print("\n" + "="*70)
    print("PROGRAMA PERSONALIZADO")
    print("="*70 + "\n")
    
    try:
        weeks = int(input("Número de semanas (1-12): "))
        if weeks < 1 or weeks > 12:
            print("❌ Debe ser entre 1 y 12 semanas")
            return None
        
        days = int(input("Días de entrenamiento por semana (3-6): "))
        if days < 3 or days > 6:
            print("❌ Debe ser entre 3 y 6 días")
            return None
        
        exercises = int(input("Ejercicios por día (4-10): "))
        if exercises < 4 or exercises > 10:
            print("❌ Debe ser entre 4 y 10 ejercicios")
            return None
        
        print(f"\nGenerando programa de {weeks} semanas...")
        program = graph.generate_8_week_program(
            weeks=weeks,
            days_per_week=days,
            exercises_per_day=exercises
        )
        
        print("\n✓ Programa personalizado generado exitosamente")
        return program
        
    except ValueError:
        print("❌ Entrada inválida")
        return None


def view_specific_week(graph: WorkoutGraph, program: dict):
    """Visualiza una semana específica"""
    if not program:
        print("\n❌ Primero debes generar un programa")
        return
    
    try:
        week = int(input(f"\nNúmero de semana (1-{len(program)}): "))
        if week < 1 or week > len(program):
            print(f"❌ Debe ser entre 1 y {len(program)}")
            return
        
        graph.print_schedule(program[week], week)
        
    except ValueError:
        print("❌ Entrada inválida")


def export_program(graph: WorkoutGraph, program: dict):
    """Exporta el programa a JSON"""
    if not program:
        print("\n❌ Primero debes generar un programa")
        return
    
    filename = input("\nNombre del archivo (ej: mi_programa.json): ").strip()
    if not filename.endswith('.json'):
        filename += '.json'
    
    graph.export_to_json(program, filename)
    print(f"\n✓ Programa exportado exitosamente a: {filename}")


def show_statistics(program: dict):
    """Muestra estadísticas del programa"""
    if not program:
        print("\n❌ Primero debes generar un programa")
        return
    
    print("\n" + "="*70)
    print("ESTADÍSTICAS DEL PROGRAMA")
    print("="*70 + "\n")
    
    total_exercises = 0
    total_stamina = 0
    bodypart_count = {}
    muscle_count = {}
    
    for week, schedule in program.items():
        for day in schedule:
            for exercise in day:
                total_exercises += 1
                total_stamina += exercise.calculate_total_cost()
                
                for bp in exercise.body_parts:
                    bodypart_count[bp] = bodypart_count.get(bp, 0) + 1
                
                for muscle in exercise.target_muscles:
                    muscle_count[muscle] = muscle_count.get(muscle, 0) + 1
    
    print(f"Total de ejercicios: {total_exercises}")
    print(f"Estamina total: {total_stamina}")
    print(f"Promedio de estamina por ejercicio: {total_stamina / total_exercises:.1f}")
    print()
    
    print("TOP 5 PARTES DEL CUERPO MÁS TRABAJADAS:")
    top_bodyparts = sorted(bodypart_count.items(), key=lambda x: x[1], reverse=True)[:5]
    for idx, (bp, count) in enumerate(top_bodyparts, 1):
        print(f"  {idx}. {bp.title()}: {count} ejercicios")
    
    print("\nTOP 5 MÚSCULOS MÁS TRABAJADOS:")
    top_muscles = sorted(muscle_count.items(), key=lambda x: x[1], reverse=True)[:5]
    for idx, (muscle, count) in enumerate(top_muscles, 1):
        print(f"  {idx}. {muscle.title()}: {count} ejercicios")
    
    print()


def main():
    """Función principal de la aplicación"""
    print_banner()
    
    # Rutas a los archivos de datos
    base_path = os.path.dirname(os.path.abspath(__file__))
    exercises_path = os.path.join(base_path, 'src', 'data', 'exercises.json')
    bodyparts_path = os.path.join(base_path, 'src', 'data', 'bodyparts.json')
    
    # Verificar que existan los archivos
    if not os.path.exists(exercises_path):
        print(f"❌ Error: No se encontró {exercises_path}")
        sys.exit(1)
    
    if not os.path.exists(bodyparts_path):
        print(f"❌ Error: No se encontró {bodyparts_path}")
        sys.exit(1)
    
    print("Inicializando sistema...")
    try:
        graph = WorkoutGraph(exercises_path, bodyparts_path)
        print(f"✓ Sistema inicializado correctamente")
        print(f"✓ {len(graph.exercises)} ejercicios cargados")
        print(f"✓ {len(graph.body_parts)} partes del cuerpo configuradas")
    except Exception as e:
        print(f"❌ Error al inicializar: {e}")
        sys.exit(1)
    
    # Variables del programa
    current_program = None
    
    # Bucle principal
    while True:
        print_menu()
        
        try:
            choice = input("Selecciona una opción (1-6): ").strip()
            
            if choice == '1':
                current_program = generate_full_program(graph)
            
            elif choice == '2':
                current_program = generate_custom_program(graph)
            
            elif choice == '3':
                view_specific_week(graph, current_program)
            
            elif choice == '4':
                export_program(graph, current_program)
            
            elif choice == '5':
                show_statistics(current_program)
            
            elif choice == '6':
                print("\n¡Hasta luego! 💪")
                break
            
            else:
                print("\n❌ Opción inválida. Por favor elige 1-6")
            
            input("\nPresiona Enter para continuar...")
            print("\n" * 2)
        
        except KeyboardInterrupt:
            print("\n\n¡Hasta luego! 💪")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            input("\nPresiona Enter para continuar...")


if __name__ == "__main__":
    main()
