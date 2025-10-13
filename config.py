# Configuración del Sistema de Optimización de Ejercicios

## Configuración de Estamina por Parte del Cuerpo

# Formato: nombre_parte: (estamina_máxima, tasa_recuperación)
STAMINA_CONFIG = {
    'chest': {
        'max_stamina': 100,
        'recovery_rate': 20,
        'description': 'Pecho y pectorales'
    },
    'back': {
        'max_stamina': 100,
        'recovery_rate': 20,
        'description': 'Espalda y dorsales'
    },
    'shoulders': {
        'max_stamina': 90,
        'recovery_rate': 20,
        'description': 'Hombros y deltoides'
    },
    'upper arms': {
        'max_stamina': 80,
        'recovery_rate': 20,
        'description': 'Brazos superiores (bíceps y tríceps)'
    },
    'lower arms': {
        'max_stamina': 70,
        'recovery_rate': 20,
        'description': 'Antebrazos'
    },
    'upper legs': {
        'max_stamina': 110,
        'recovery_rate': 20,
        'description': 'Piernas superiores (cuádriceps y femoral)'
    },
    'lower legs': {
        'max_stamina': 90,
        'recovery_rate': 20,
        'description': 'Pantorrillas y tibiales'
    },
    'waist': {
        'max_stamina': 85,
        'recovery_rate': 20,
        'description': 'Abdomen y core'
    },
    'neck': {
        'max_stamina': 60,
        'recovery_rate': 20,
        'description': 'Cuello y trapecios'
    },
    'cardio': {
        'max_stamina': 120,
        'recovery_rate': 20,
        'description': 'Sistema cardiovascular'
    }
}

## Configuración de Ejercicios

# Costo base de estamina por ejercicio
BASE_STAMINA_COST = 15

# Multiplicador de complejidad
# costo_final = base_cost * (1 + (músculos_target + músculos_secundarios) * multiplicador)
COMPLEXITY_MULTIPLIER = 0.1

## Configuración de Beneficios

# Puntos por músculo objetivo
TARGET_MUSCLE_POINTS = 10

# Puntos por músculo secundario
SECONDARY_MUSCLE_POINTS = 5

# Bonus de progresión por semana
PROGRESSION_BONUS_PER_WEEK = 0.05

## Configuración de Progresión

# Cada cuántas semanas aumentar capacidad
PROGRESSION_INTERVAL_WEEKS = 2

# Porcentaje de aumento de capacidad
CAPACITY_INCREASE_PERCENT = 0.05  # 5%

## Configuración por Defecto de Programas

DEFAULT_WEEKS = 8
DEFAULT_DAYS_PER_WEEK = 5
DEFAULT_EXERCISES_PER_DAY = 6

## Límites del Sistema

MIN_WEEKS = 1
MAX_WEEKS = 12
MIN_DAYS_PER_WEEK = 3
MAX_DAYS_PER_WEEK = 6
MIN_EXERCISES_PER_DAY = 4
MAX_EXERCISES_PER_DAY = 10

## Configuración de Optimización

# Número máximo de ejercicios a procesar (para rendimiento)
MAX_EXERCISES_TO_PROCESS = 100

# Discretización de estamina para estados (agrupación en rangos)
STAMINA_DISCRETIZATION = 10  # Agrupar en rangos de 10

## Configuración de Exportación

DEFAULT_EXPORT_FILENAME = 'workout_program_8weeks.json'
VISUALIZATIONS_DIR = 'visualizations'

## Perfiles Predefinidos

PROFILES = {
    'beginner': {
        'weeks': 4,
        'days_per_week': 3,
        'exercises_per_day': 4,
        'stamina_multiplier': 0.8,  # 80% de capacidad
        'recovery_multiplier': 1.2,  # 20% más recuperación
        'description': 'Principiante - Baja intensidad, enfoque en técnica'
    },
    'intermediate': {
        'weeks': 8,
        'days_per_week': 5,
        'exercises_per_day': 6,
        'stamina_multiplier': 1.0,  # 100% capacidad normal
        'recovery_multiplier': 1.0,  # Recuperación normal
        'description': 'Intermedio - Intensidad media, construcción muscular'
    },
    'advanced': {
        'weeks': 12,
        'days_per_week': 6,
        'exercises_per_day': 8,
        'stamina_multiplier': 1.2,  # 120% de capacidad
        'recovery_multiplier': 0.9,  # 10% menos recuperación (más desafío)
        'description': 'Avanzado - Alta intensidad, maximización'
    },
    'athlete': {
        'weeks': 12,
        'days_per_week': 6,
        'exercises_per_day': 10,
        'stamina_multiplier': 1.5,  # 150% de capacidad
        'recovery_multiplier': 1.1,  # 10% más recuperación
        'description': 'Atleta - Muy alta intensidad, rendimiento competitivo'
    }
}

## Configuración de Visualización

VISUALIZATION_CONFIG = {
    'graph': {
        'figure_size': (16, 10),
        'node_size': 800,
        'font_size': 6,
        'dpi': 300,
        'alpha': 0.9
    },
    'progression': {
        'figure_size': (12, 6),
        'marker': 'o',
        'linewidth': 2,
        'markersize': 8
    },
    'distribution': {
        'figure_size': (12, 6),
        'rotation': 45
    }
}
