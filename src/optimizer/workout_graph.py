"""
Sistema de Grafos de Programación Dinámica para Optimización de Rutinas de Ejercicio
Gestiona la estamina por parte del cuerpo y optimiza rutinas semanales durante 2 meses
"""

import json
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import copy


@dataclass
class Exercise:
    """Representa un ejercicio con su costo de estamina"""
    exercise_id: str
    name: str
    target_muscles: List[str]
    body_parts: List[str]
    equipments: List[str]
    secondary_muscles: List[str]
    stamina_cost: int = 15  # Costo base de estamina por ejercicio
    
    def calculate_total_cost(self) -> int:
        """Calcula el costo total considerando músculos objetivo y secundarios"""
        base_cost = self.stamina_cost
        # Ejercicios compuestos (múltiples músculos) cuestan más
        complexity_multiplier = 1 + (len(self.target_muscles) + len(self.secondary_muscles)) * 0.1
        return int(base_cost * complexity_multiplier)


@dataclass
class BodyPartStamina:
    """Gestiona la estamina de una parte del cuerpo"""
    name: str
    max_stamina: int = 100
    current_stamina: int = 100
    recovery_rate: int = 20  # Recuperación por día de descanso
    
    def consume(self, amount: int) -> bool:
        """Consume estamina. Retorna True si hay suficiente"""
        if self.current_stamina >= amount:
            self.current_stamina -= amount
            return True
        return False
    
    def recover(self, days: int = 1):
        """Recupera estamina"""
        self.current_stamina = min(
            self.max_stamina, 
            self.current_stamina + (self.recovery_rate * days)
        )
    
    def is_available(self, cost: int) -> bool:
        """Verifica si hay suficiente estamina"""
        return self.current_stamina >= cost


@dataclass
class WorkoutNode:
    """Nodo del grafo que representa un ejercicio en un día específico"""
    exercise: Exercise
    day: int
    week: int
    stamina_state: Dict[str, int]  # Estado de estamina después del ejercicio
    cumulative_benefit: float = 0.0  # Beneficio acumulado
    parent: 'WorkoutNode' = None
    
    def __hash__(self):
        return hash((self.exercise.exercise_id, self.day, self.week))


class WorkoutGraph:
    """Grafo de programación dinámica para optimización de rutinas"""
    
    def __init__(self, exercises_path: str, bodyparts_path: str):
        self.exercises: List[Exercise] = []
        self.body_parts: Dict[str, BodyPartStamina] = {}
        self.graph: Dict[Tuple[int, int], List[WorkoutNode]] = defaultdict(list)
        self.dp_table: Dict[Tuple[int, int], Dict] = {}
        
        self._load_data(exercises_path, bodyparts_path)
        self._initialize_stamina()
    
    def _load_data(self, exercises_path: str, bodyparts_path: str):
        """Carga los datos de ejercicios y partes del cuerpo"""
        # Cargar ejercicios
        with open(exercises_path, 'r') as f:
            exercises_data = json.load(f)
            for ex in exercises_data[:100]:  # Limitar para ejemplo
                self.exercises.append(Exercise(
                    exercise_id=ex['exerciseId'],
                    name=ex['name'],
                    target_muscles=ex['targetMuscles'],
                    body_parts=ex['bodyParts'],
                    equipments=ex['equipments'],
                    secondary_muscles=ex['secondaryMuscles']
                ))
        
        # Cargar partes del cuerpo
        with open(bodyparts_path, 'r') as f:
            bodyparts_data = json.load(f)
            for bp in bodyparts_data:
                self.body_parts[bp['name']] = BodyPartStamina(name=bp['name'])
    
    def _initialize_stamina(self):
        """Inicializa los valores de estamina para cada parte del cuerpo"""
        stamina_config = {
            'chest': 100,
            'back': 100,
            'shoulders': 90,
            'upper arms': 80,
            'lower arms': 70,
            'upper legs': 110,
            'lower legs': 90,
            'waist': 85,
            'neck': 60,
            'cardio': 120
        }
        
        for name, stamina in stamina_config.items():
            if name in self.body_parts:
                self.body_parts[name].max_stamina = stamina
                self.body_parts[name].current_stamina = stamina
    
    def calculate_exercise_benefit(self, exercise: Exercise, week: int) -> float:
        """Calcula el beneficio de un ejercicio considerando la progresión"""
        # Beneficio base por músculo trabajado
        base_benefit = len(exercise.target_muscles) * 10
        base_benefit += len(exercise.secondary_muscles) * 5
        
        # Bonus por progresión (aumenta con las semanas)
        progression_bonus = 1 + (week * 0.05)
        
        return base_benefit * progression_bonus
    
    def can_perform_exercise(
        self, 
        exercise: Exercise, 
        stamina_state: Dict[str, int]
    ) -> bool:
        """Verifica si un ejercicio puede realizarse dado el estado de estamina"""
        cost = exercise.calculate_total_cost()
        
        for body_part in exercise.body_parts:
            if body_part in stamina_state:
                if stamina_state[body_part] < cost:
                    return False
        return True
    
    def update_stamina_state(
        self, 
        exercise: Exercise, 
        stamina_state: Dict[str, int]
    ) -> Dict[str, int]:
        """Actualiza el estado de estamina después de realizar un ejercicio"""
        new_state = stamina_state.copy()
        cost = exercise.calculate_total_cost()
        
        # Reducir estamina de partes del cuerpo principales
        for body_part in exercise.body_parts:
            if body_part in new_state:
                new_state[body_part] = max(0, new_state[body_part] - cost)
        
        # Reducir estamina menor en músculos secundarios
        for muscle in exercise.secondary_muscles:
            for bp_name, bp in self.body_parts.items():
                if muscle.lower() in bp_name.lower():
                    if bp_name in new_state:
                        new_state[bp_name] = max(0, new_state[bp_name] - (cost // 2))
        
        return new_state
    
    def recover_stamina_state(
        self, 
        stamina_state: Dict[str, int], 
        days: int = 1
    ) -> Dict[str, int]:
        """Recupera estamina después de días de descanso"""
        new_state = stamina_state.copy()
        
        for body_part in new_state:
            if body_part in self.body_parts:
                bp = self.body_parts[body_part]
                recovery = bp.recovery_rate * days
                new_state[body_part] = min(
                    bp.max_stamina, 
                    new_state[body_part] + recovery
                )
        
        return new_state
    
    def build_optimal_week(
        self, 
        week: int, 
        days_per_week: int = 5,
        exercises_per_day: int = 6
    ) -> List[List[Exercise]]:
        """
        Construye una semana óptima de ejercicios usando programación dinámica
        """
        # Estado inicial de estamina
        initial_state = {
            name: bp.max_stamina 
            for name, bp in self.body_parts.items()
        }
        
        # DP table: dp[day][state_hash] = (best_benefit, exercises, state)
        dp = [{} for _ in range(days_per_week + 1)]
        dp[0][self._hash_state(initial_state)] = (0.0, [], initial_state)
        
        # Construir el grafo día por día
        for day in range(days_per_week):
            for state_hash, (benefit, exercises_so_far, stamina_state) in dp[day].items():
                # Intentar agregar ejercicios para este día
                daily_exercises = []
                current_stamina = stamina_state.copy()
                current_benefit = benefit
                
                # Seleccionar los mejores ejercicios para este día
                available_exercises = [
                    ex for ex in self.exercises 
                    if self.can_perform_exercise(ex, current_stamina)
                ]
                
                # Ordenar por beneficio
                available_exercises.sort(
                    key=lambda x: self.calculate_exercise_benefit(x, week), 
                    reverse=True
                )
                
                # Agregar hasta exercises_per_day ejercicios
                for exercise in available_exercises[:exercises_per_day]:
                    if self.can_perform_exercise(exercise, current_stamina):
                        daily_exercises.append(exercise)
                        current_benefit += self.calculate_exercise_benefit(exercise, week)
                        current_stamina = self.update_stamina_state(exercise, current_stamina)
                
                # Recuperar estamina al final del día
                next_stamina = self.recover_stamina_state(current_stamina, days=1)
                next_state_hash = self._hash_state(next_stamina)
                
                # Actualizar DP table si encontramos mejor solución
                next_exercises = exercises_so_far + [daily_exercises]
                
                if (next_state_hash not in dp[day + 1] or 
                    dp[day + 1][next_state_hash][0] < current_benefit):
                    dp[day + 1][next_state_hash] = (
                        current_benefit, 
                        next_exercises, 
                        next_stamina
                    )
        
        # Encontrar la mejor solución final
        best_benefit = -1
        best_schedule = []
        
        for state_hash, (benefit, schedule, _) in dp[days_per_week].items():
            if benefit > best_benefit:
                best_benefit = benefit
                best_schedule = schedule
        
        return best_schedule
    
    def _hash_state(self, state: Dict[str, int]) -> str:
        """Crea un hash del estado de estamina para usar en DP"""
        # Discretizar los valores de estamina en rangos de 10
        discretized = {
            k: (v // 10) * 10 
            for k, v in sorted(state.items())
        }
        return str(discretized)
    
    def generate_8_week_program(
        self, 
        weeks: int = 8,
        days_per_week: int = 5,
        exercises_per_day: int = 6
    ) -> Dict[int, List[List[Exercise]]]:
        """
        Genera un programa completo de 8 semanas con progresión
        """
        program = {}
        
        for week in range(1, weeks + 1):
            print(f"Optimizando semana {week}/{weeks}...")
            week_schedule = self.build_optimal_week(
                week=week,
                days_per_week=days_per_week,
                exercises_per_day=exercises_per_day
            )
            program[week] = week_schedule
            
            # Aumentar dificultad progresivamente
            if week % 2 == 0:  # Cada 2 semanas
                for bp in self.body_parts.values():
                    bp.max_stamina = int(bp.max_stamina * 1.05)  # +5% capacidad
        
        return program
    
    def print_schedule(self, schedule: List[List[Exercise]], week: int):
        """Imprime el programa de una semana de forma legible"""
        print(f"\n{'='*70}")
        print(f"SEMANA {week} - PROGRAMA DE ENTRENAMIENTO")
        print(f"{'='*70}\n")
        
        for day_idx, day_exercises in enumerate(schedule, 1):
            print(f"DÍA {day_idx}:")
            print(f"{'-'*70}")
            
            if not day_exercises:
                print("  Día de descanso\n")
                continue
            
            for idx, exercise in enumerate(day_exercises, 1):
                cost = exercise.calculate_total_cost()
                print(f"  {idx}. {exercise.name.title()}")
                print(f"     Partes: {', '.join(exercise.body_parts)}")
                print(f"     Músculos: {', '.join(exercise.target_muscles)}")
                print(f"     Costo estamina: {cost}")
                print()
        
        print()
    
    def export_to_json(self, program: Dict[int, List[List[Exercise]]], filename: str):
        """Exporta el programa a JSON"""
        export_data = {}
        
        for week, schedule in program.items():
            week_data = []
            for day_idx, day_exercises in enumerate(schedule, 1):
                day_data = {
                    'day': day_idx,
                    'exercises': [
                        {
                            'id': ex.exercise_id,
                            'name': ex.name,
                            'body_parts': ex.body_parts,
                            'target_muscles': ex.target_muscles,
                            'stamina_cost': ex.calculate_total_cost()
                        }
                        for ex in day_exercises
                    ]
                }
                week_data.append(day_data)
            
            export_data[f'week_{week}'] = week_data
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"Programa exportado a: {filename}")


def main():
    """Función principal de demostración"""
    import os
    
    # Rutas a los archivos de datos
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    exercises_path = os.path.join(base_path, 'data', 'exercises.json')
    bodyparts_path = os.path.join(base_path, 'data', 'bodyparts.json')
    
    # Crear el grafo de optimización
    print("Inicializando sistema de optimización...")
    graph = WorkoutGraph(exercises_path, bodyparts_path)
    
    print(f"✓ Cargados {len(graph.exercises)} ejercicios")
    print(f"✓ Configuradas {len(graph.body_parts)} partes del cuerpo")
    print()
    
    # Generar programa de 8 semanas
    program = graph.generate_8_week_program(
        weeks=8,
        days_per_week=5,
        exercises_per_day=6
    )
    
    # Mostrar las primeras 2 semanas como ejemplo
    for week in [1, 2]:
        graph.print_schedule(program[week], week)
    
    # Exportar todo el programa
    output_path = os.path.join(base_path, '..', 'workout_program_8weeks.json')
    graph.export_to_json(program, output_path)
    
    print(f"\n✓ Programa completo de 8 semanas generado exitosamente!")


if __name__ == "__main__":
    main()
