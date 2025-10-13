# Guía de Inicio Rápido - Muscle RPG

## 📦 Instalación

### Opción 1: Instalación Automática (Recomendada)

```bash
chmod +x install.sh
./install.sh
```

### Opción 2: Instalación Manual

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Verificar instalación
python3 demo.py
```

## 🚀 Uso Básico

### Aplicación Interactiva

```bash
python3 app.py
```

Menú disponible:
1. **Generar programa completo de 8 semanas** - Programa estándar preconfigurado
2. **Generar programa personalizado** - Personaliza semanas, días y ejercicios
3. **Visualizar semana específica** - Ver detalles de una semana
4. **Exportar programa a JSON** - Guardar programa para uso posterior
5. **Ver estadísticas** - Análisis del programa generado

### Demo Rápida

```bash
python3 demo.py
```

Genera un programa de 2 semanas como demostración.

## 💻 Uso Programático

### Ejemplo Básico

```python
from src.optimizer.workout_graph import WorkoutGraph

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

# Ver semana 1
graph.print_schedule(program[1], week=1)

# Exportar
graph.export_to_json(program, 'my_program.json')
```

### Personalización Avanzada

```python
# Modificar estamina de una parte del cuerpo
graph.body_parts['chest'].max_stamina = 120
graph.body_parts['chest'].recovery_rate = 25

# Cambiar costo de un ejercicio específico
for exercise in graph.exercises:
    if exercise.name == 'push-ups':
        exercise.stamina_cost = 20

# Generar programa personalizado
program = graph.generate_8_week_program(
    weeks=12,              # 12 semanas
    days_per_week=6,       # 6 días de entrenamiento
    exercises_per_day=8    # 8 ejercicios por día
)
```

## 📊 Generar Visualizaciones

```bash
# Primero genera un programa
python3 app.py
# Selecciona opción 1 o 2 y exporta a 'workout_program_8weeks.json'

# Luego genera visualizaciones
python3 -m src.optimizer.visualizer
```

Esto creará:
- `visualizations/graph_week_1.png` - Grafo de ejercicios semana 1
- `visualizations/graph_week_2.png` - Grafo de ejercicios semana 2
- `visualizations/stamina_progression.png` - Progresión de intensidad
- `visualizations/bodypart_distribution.png` - Distribución por grupo muscular
- `visualizations/report_week_*.txt` - Reportes detallados

## 🎯 Ejemplos de Uso

### Caso 1: Principiante (Baja Intensidad)

```python
program = graph.generate_8_week_program(
    weeks=4,
    days_per_week=3,
    exercises_per_day=4
)
```

### Caso 2: Intermedio (Intensidad Media)

```python
program = graph.generate_8_week_program(
    weeks=8,
    days_per_week=5,
    exercises_per_day=6
)
```

### Caso 3: Avanzado (Alta Intensidad)

```python
program = graph.generate_8_week_program(
    weeks=12,
    days_per_week=6,
    exercises_per_day=8
)
```

## 🔧 Configuración del Sistema de Estamina

### Ver Configuración Actual

```python
for name, bp in graph.body_parts.items():
    print(f"{name}: {bp.max_stamina} / {bp.recovery_rate}")
```

### Modificar Configuración

```python
# Aumentar capacidad general
for bp in graph.body_parts.values():
    bp.max_stamina = int(bp.max_stamina * 1.2)  # +20%
    bp.recovery_rate = int(bp.recovery_rate * 1.5)  # +50%
```

## 📈 Interpretar el Programa Generado

### Formato de Salida

```
DÍA 1:
──────────────────────────────────────────────────────────────────────
  1. Push-Ups
     Partes: chest
     Músculos: pectorals
     Costo estamina: 20
```

**Interpretación**:
- **Nombre**: Ejercicio a realizar
- **Partes**: Grupos musculares principales
- **Músculos**: Músculos específicos trabajados
- **Costo**: Estamina consumida (importante para planificación)

### Archivo JSON Exportado

```json
{
  "week_1": [
    {
      "day": 1,
      "exercises": [
        {
          "id": "abc123",
          "name": "push-ups",
          "body_parts": ["chest"],
          "target_muscles": ["pectorals"],
          "stamina_cost": 20
        }
      ]
    }
  ]
}
```

## ❓ Solución de Problemas

### Error: "No se encontró el archivo exercises.json"

```bash
# Verifica que la estructura sea correcta
ls src/data/
# Deberías ver: exercises.json, bodyparts.json, muscles.json
```

### Error: "ModuleNotFoundError: No module named 'matplotlib'"

```bash
pip install matplotlib networkx
```

### Error: "No hay ejercicios válidos para este día"

Esto significa que la estamina es insuficiente. Soluciones:
- Reducir `exercises_per_day`
- Aumentar `recovery_rate`
- Aumentar `max_stamina`

### El programa genera ejercicios repetidos

Normal en programas cortos. Para mayor variedad:
- Aumentar el número de semanas
- Reducir `exercises_per_day`
- El algoritmo prioriza óptimos, no variedad

## 📚 Documentación Adicional

- **README.md** - Documentación general del proyecto
- **TECHNICAL_DOC.md** - Detalles técnicos del algoritmo
- Código fuente con comentarios extensivos

## 🤝 Soporte

Si encuentras problemas:
1. Revisa esta guía
2. Consulta TECHNICAL_DOC.md
3. Revisa el código en `src/optimizer/workout_graph.py`
4. Abre un issue en GitHub

## 💪 ¡A Entrenar!

Ya estás listo para generar tu programa de entrenamiento óptimo. ¡Buena suerte!
