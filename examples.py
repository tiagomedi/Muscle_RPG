"""
Ejemplos Prácticos - Muscle RPG
Casos de uso comunes y código de ejemplo
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.optimizer.workout_graph import WorkoutGraph


# ============================================================================
# EJEMPLO 1: Uso Básico - Generar Programa Estándar
# ============================================================================

def ejemplo_basico():
    """Genera un programa estándar de 8 semanas"""
    print("\n" + "="*70)
    print("EJEMPLO 1: PROGRAMA ESTÁNDAR DE 8 SEMANAS")
    print("="*70 + "\n")
    
    # Inicializar
    graph = WorkoutGraph(
        'src/data/exercises.json',
        'src/data/bodyparts.json'
    )
    
    # Generar programa
    program = graph.generate_8_week_program(
        weeks=8,
        days_per_week=5,
        exercises_per_day=6
    )
    
    # Ver primera semana
    graph.print_schedule(program[1], week=1)
    
    # Exportar
    graph.export_to_json(program, 'programa_estandar.json')
    
    print("\n✓ Programa estándar generado y exportado")


# ============================================================================
# EJEMPLO 2: Programa para Principiantes
# ============================================================================

def ejemplo_principiante():
    """Programa adaptado para principiantes"""
    print("\n" + "="*70)
    print("EJEMPLO 2: PROGRAMA PARA PRINCIPIANTES")
    print("="*70 + "\n")
    
    graph = WorkoutGraph(
        'src/data/exercises.json',
        'src/data/bodyparts.json'
    )
    
    # Reducir capacidad y aumentar recuperación para principiantes
    for bodypart in graph.body_parts.values():
        bodypart.max_stamina = int(bodypart.max_stamina * 0.8)  # 80% capacidad
        bodypart.recovery_rate = int(bodypart.recovery_rate * 1.2)  # +20% recuperación
    
    # Programa más suave
    program = graph.generate_8_week_program(
        weeks=4,              # Solo 4 semanas para empezar
        days_per_week=3,      # 3 días de entrenamiento
        exercises_per_day=4   # Pocos ejercicios por sesión
    )
    
    graph.print_schedule(program[1], week=1)
    graph.export_to_json(program, 'programa_principiante.json')
    
    print("\n✓ Programa para principiantes generado")
    print("Características:")
    print("  • Baja intensidad (80% capacidad)")
    print("  • Mayor recuperación (+20%)")
    print("  • 3 días por semana")
    print("  • 4 ejercicios por sesión")


# ============================================================================
# EJEMPLO 3: Programa Avanzado de Alta Intensidad
# ============================================================================

def ejemplo_avanzado():
    """Programa de alta intensidad para atletas avanzados"""
    print("\n" + "="*70)
    print("EJEMPLO 3: PROGRAMA AVANZADO DE ALTA INTENSIDAD")
    print("="*70 + "\n")
    
    graph = WorkoutGraph(
        'src/data/exercises.json',
        'src/data/bodyparts.json'
    )
    
    # Aumentar capacidad para atletas avanzados
    for bodypart in graph.body_parts.values():
        bodypart.max_stamina = int(bodypart.max_stamina * 1.3)  # +30% capacidad
        bodypart.recovery_rate = int(bodypart.recovery_rate * 1.1)  # +10% recuperación
    
    # Programa intensivo
    program = graph.generate_8_week_program(
        weeks=12,             # Programa largo
        days_per_week=6,      # 6 días de entrenamiento
        exercises_per_day=8   # Muchos ejercicios por sesión
    )
    
    # Mostrar semana 1 y semana 12 para comparar
    print("\nSEMANA 1:")
    graph.print_schedule(program[1], week=1)
    
    print("\nSEMANA 12 (Final):")
    graph.print_schedule(program[12], week=12)
    
    graph.export_to_json(program, 'programa_avanzado.json')
    
    print("\n✓ Programa avanzado generado")
    print("Características:")
    print("  • Alta intensidad (+30% capacidad)")
    print("  • 6 días por semana (1 descanso)")
    print("  • 8 ejercicios por sesión")
    print("  • 12 semanas de progresión")


# ============================================================================
# EJEMPLO 4: Enfoque Específico en Parte del Cuerpo
# ============================================================================

def ejemplo_enfoque_especifico():
    """Programa con énfasis en pecho y brazos"""
    print("\n" + "="*70)
    print("EJEMPLO 4: ENFOQUE EN PECHO Y BRAZOS")
    print("="*70 + "\n")
    
    graph = WorkoutGraph(
        'src/data/exercises.json',
        'src/data/bodyparts.json'
    )
    
    # Aumentar capacidad de partes objetivo
    graph.body_parts['chest'].max_stamina = 150
    graph.body_parts['upper arms'].max_stamina = 130
    
    # Reducir otras partes para forzar más ejercicios de objetivo
    for name in ['back', 'lower legs', 'waist']:
        if name in graph.body_parts:
            graph.body_parts[name].max_stamina = 60
    
    program = graph.generate_8_week_program(
        weeks=6,
        days_per_week=4,
        exercises_per_day=6
    )
    
    # Analizar distribución
    chest_exercises = 0
    arms_exercises = 0
    total_exercises = 0
    
    for week_schedule in program.values():
        for day_exercises in week_schedule:
            for exercise in day_exercises:
                total_exercises += 1
                if 'chest' in exercise.body_parts:
                    chest_exercises += 1
                if 'upper arms' in exercise.body_parts:
                    arms_exercises += 1
    
    graph.print_schedule(program[1], week=1)
    graph.export_to_json(program, 'programa_pecho_brazos.json')
    
    print("\n✓ Programa con enfoque específico generado")
    print(f"\nDistribución:")
    print(f"  • Total de ejercicios: {total_exercises}")
    print(f"  • Ejercicios de pecho: {chest_exercises} ({chest_exercises/total_exercises*100:.1f}%)")
    print(f"  • Ejercicios de brazos: {arms_exercises} ({arms_exercises/total_exercises*100:.1f}%)")


# ============================================================================
# EJEMPLO 5: Análisis de Estadísticas
# ============================================================================

def ejemplo_estadisticas():
    """Genera un programa y analiza estadísticas detalladas"""
    print("\n" + "="*70)
    print("EJEMPLO 5: ANÁLISIS DETALLADO DE ESTADÍSTICAS")
    print("="*70 + "\n")
    
    graph = WorkoutGraph(
        'src/data/exercises.json',
        'src/data/bodyparts.json'
    )
    
    program = graph.generate_8_week_program(weeks=8)
    
    # Recolectar estadísticas
    stats = {
        'total_exercises': 0,
        'total_stamina': 0,
        'bodypart_count': {},
        'muscle_count': {},
        'weekly_exercises': {},
        'weekly_stamina': {}
    }
    
    for week, schedule in program.items():
        week_exercises = 0
        week_stamina = 0
        
        for day_exercises in schedule:
            for exercise in day_exercises:
                stats['total_exercises'] += 1
                cost = exercise.calculate_total_cost()
                stats['total_stamina'] += cost
                
                week_exercises += 1
                week_stamina += cost
                
                # Contar partes del cuerpo
                for bp in exercise.body_parts:
                    stats['bodypart_count'][bp] = stats['bodypart_count'].get(bp, 0) + 1
                
                # Contar músculos
                for muscle in exercise.target_muscles:
                    stats['muscle_count'][muscle] = stats['muscle_count'].get(muscle, 0) + 1
        
        stats['weekly_exercises'][week] = week_exercises
        stats['weekly_stamina'][week] = week_stamina
    
    # Imprimir estadísticas
    print("ESTADÍSTICAS GENERALES:")
    print(f"  • Total de ejercicios: {stats['total_exercises']}")
    print(f"  • Estamina total: {stats['total_stamina']}")
    print(f"  • Promedio por ejercicio: {stats['total_stamina']/stats['total_exercises']:.1f}")
    
    print("\nPARTES DEL CUERPO MÁS TRABAJADAS:")
    top_bodyparts = sorted(stats['bodypart_count'].items(), key=lambda x: x[1], reverse=True)[:5]
    for idx, (bp, count) in enumerate(top_bodyparts, 1):
        percentage = (count / stats['total_exercises']) * 100
        print(f"  {idx}. {bp.title()}: {count} ejercicios ({percentage:.1f}%)")
    
    print("\nMÚSCULOS MÁS TRABAJADOS:")
    top_muscles = sorted(stats['muscle_count'].items(), key=lambda x: x[1], reverse=True)[:5]
    for idx, (muscle, count) in enumerate(top_muscles, 1):
        percentage = (count / stats['total_exercises']) * 100
        print(f"  {idx}. {muscle.title()}: {count} ejercicios ({percentage:.1f}%)")
    
    print("\nPROGRESIÓN SEMANAL:")
    for week in range(1, 9):
        exercises = stats['weekly_exercises'][week]
        stamina = stats['weekly_stamina'][week]
        print(f"  Semana {week}: {exercises} ejercicios, {stamina} estamina total")
    
    graph.export_to_json(program, 'programa_analizado.json')
    print("\n✓ Análisis completado y programa exportado")


# ============================================================================
# EJEMPLO 6: Programa con Equipamiento Limitado
# ============================================================================

def ejemplo_equipamiento_limitado():
    """Programa usando solo peso corporal y bandas"""
    print("\n" + "="*70)
    print("EJEMPLO 6: ENTRENAMIENTO EN CASA (SIN GIMNASIO)")
    print("="*70 + "\n")
    
    graph = WorkoutGraph(
        'src/data/exercises.json',
        'src/data/bodyparts.json'
    )
    
    # Filtrar solo ejercicios con peso corporal o bandas
    equipos_permitidos = {'body weight', 'band', 'resistance band'}
    graph.exercises = [
        ex for ex in graph.exercises 
        if any(equip.lower() in equipos_permitidos for equip in ex.equipments)
    ]
    
    print(f"Ejercicios disponibles con equipamiento limitado: {len(graph.exercises)}")
    
    program = graph.generate_8_week_program(
        weeks=8,
        days_per_week=5,
        exercises_per_day=6
    )
    
    graph.print_schedule(program[1], week=1)
    graph.export_to_json(program, 'programa_casa.json')
    
    print("\n✓ Programa para casa generado")
    print("Equipamiento necesario:")
    print("  • Peso corporal")
    print("  • Bandas de resistencia (opcional)")


# ============================================================================
# EJEMPLO 7: Recuperación Rápida vs Lenta
# ============================================================================

def ejemplo_recuperacion():
    """Compara programas con diferentes tasas de recuperación"""
    print("\n" + "="*70)
    print("EJEMPLO 7: COMPARACIÓN DE TASAS DE RECUPERACIÓN")
    print("="*70 + "\n")
    
    # Programa con recuperación rápida
    print("A) RECUPERACIÓN RÁPIDA (Genética favorable / Joven)")
    graph_rapida = WorkoutGraph(
        'src/data/exercises.json',
        'src/data/bodyparts.json'
    )
    
    for bp in graph_rapida.body_parts.values():
        bp.recovery_rate = 30  # +50% recuperación
    
    program_rapida = graph_rapida.generate_8_week_program(weeks=4)
    
    # Contar ejercicios
    total_rapida = sum(
        len(ex) for week in program_rapida.values() 
        for day in week for ex in day
    )
    
    print(f"  • Total de ejercicios posibles: {total_rapida}")
    print(f"  • Promedio por semana: {total_rapida / 4:.1f}")
    
    # Programa con recuperación lenta
    print("\nB) RECUPERACIÓN LENTA (Edad avanzada / Principiante)")
    graph_lenta = WorkoutGraph(
        'src/data/exercises.json',
        'src/data/bodyparts.json'
    )
    
    for bp in graph_lenta.body_parts.values():
        bp.recovery_rate = 15  # -25% recuperación
    
    program_lenta = graph_lenta.generate_8_week_program(weeks=4)
    
    total_lenta = sum(
        len(ex) for week in program_lenta.values() 
        for day in week for ex in day
    )
    
    print(f"  • Total de ejercicios posibles: {total_lenta}")
    print(f"  • Promedio por semana: {total_lenta / 4:.1f}")
    
    print(f"\nDIFERENCIA:")
    print(f"  • Ejercicios adicionales con recuperación rápida: {total_rapida - total_lenta}")
    print(f"  • Aumento porcentual: {((total_rapida - total_lenta) / total_lenta * 100):.1f}%")
    
    graph_rapida.export_to_json(program_rapida, 'programa_recuperacion_rapida.json')
    graph_lenta.export_to_json(program_lenta, 'programa_recuperacion_lenta.json')
    
    print("\n✓ Ambos programas generados y exportados")


# ============================================================================
# MENÚ PRINCIPAL
# ============================================================================

def menu():
    """Menú interactivo de ejemplos"""
    print("\n" + "="*70)
    print("MUSCLE RPG - EJEMPLOS PRÁCTICOS")
    print("="*70)
    
    ejemplos = {
        '1': ('Programa estándar de 8 semanas', ejemplo_basico),
        '2': ('Programa para principiantes', ejemplo_principiante),
        '3': ('Programa avanzado de alta intensidad', ejemplo_avanzado),
        '4': ('Enfoque específico (pecho y brazos)', ejemplo_enfoque_especifico),
        '5': ('Análisis detallado de estadísticas', ejemplo_estadisticas),
        '6': ('Programa en casa (sin gimnasio)', ejemplo_equipamiento_limitado),
        '7': ('Comparación de recuperación', ejemplo_recuperacion),
        '8': ('Ejecutar todos los ejemplos', None)
    }
    
    print("\nEjemplos disponibles:")
    for key, (desc, _) in ejemplos.items():
        print(f"  {key}. {desc}")
    print("  0. Salir")
    
    while True:
        print()
        choice = input("Selecciona un ejemplo (0-8): ").strip()
        
        if choice == '0':
            print("\n¡Hasta luego! 💪")
            break
        
        elif choice == '8':
            for key, (desc, func) in ejemplos.items():
                if key != '8' and func:
                    print(f"\n{'='*70}")
                    print(f"Ejecutando: {desc}")
                    print('='*70)
                    func()
                    input("\nPresiona Enter para continuar...")
            print("\n✓ Todos los ejemplos ejecutados")
            break
        
        elif choice in ejemplos and ejemplos[choice][1]:
            ejemplos[choice][1]()
            input("\nPresiona Enter para continuar...")
        
        else:
            print("❌ Opción inválida")


if __name__ == "__main__":
    menu()
