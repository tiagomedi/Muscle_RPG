# Muscle RPG 🏋🏻‍♂️

## Sistema de Optimización de Entrenamiento con Programación Dinámica

Un sistema avanzado de optimización de rutinas de ejercicio utilizando **Programación Dinámica** y **Teoría de Grafos**.

## 🎯 Características Principales

### 1. **Sistema de Estamina por Parte del Cuerpo**
- Cada parte del cuerpo tiene su propio pool de estamina (100 puntos base)
- La estamina se consume al realizar ejercicios
- Recuperación automática: 20 puntos por día de descanso
- Configuración personalizable por grupo muscular

### 2. **Grafo de Programación Dinámica**
- **Nodos**: Representan ejercicios en días específicos
- **Aristas**: Conexiones entre ejercicios basadas en partes del cuerpo compartidas
- **Pesos**: Costo de estamina de cada ejercicio
- **Optimización**: Maximiza beneficios mientras respeta límites de estamina

### 3. **Generación de Programas**
- Programas de 1 a 12 semanas
- 3-6 días de entrenamiento por semana
- 4-10 ejercicios por día
- Progresión automática (aumenta capacidad cada 2 semanas)

## 🚀 Uso Rápido

### Instalación de Dependencias

```bash
python3 -m venv venv

source venv/bin/activate
```

```bash
pip3 install -r requirements.txt
```

### Ejecución

```bash
python app.py
```

### Uso Programático

```python
from src.optimizer.workout_graph import WorkoutGraph

# Inicializar
graph = WorkoutGraph(
    'src/data/exercises.json',
    'src/data/bodyparts.json'
)

# Generar programa de 8 semanas
program = graph.generate_8_week_program(
    weeks=8,
    days_per_week=5,
    exercises_per_day=6
)

# Ver una semana
graph.print_schedule(program[1], week=1)

# Exportar
graph.export_to_json(program, 'mi_programa.json')
```

## 📊 Sistema de Estamina

Cada parte del cuerpo tiene:
- **Estamina Máxima**: 60-120 puntos según el grupo muscular
- **Recuperación**: 20 puntos por día de descanso
- **Costo por Ejercicio**: 15-30 puntos según complejidad

## 🧮 Algoritmo de Programación Dinámica

```
DP[día][estado_estamina] = max(
    DP[día-1][estado_anterior] + beneficio(ejercicio)
    para todos los ejercicios válidos
)
```

El algoritmo optimiza:
- Máximo beneficio total
- Respetando límites de estamina
- Considerando recuperación
- Con progresión semanal

## 📈 Estructura del Proyecto

```
src/
├── optimizer/
│   ├── workout_graph.py      # Motor de optimización
│   ├── visualizer.py          # Visualizaciones
│   └── __init__.py
├── data/
│   ├── exercises.json         # Base de ejercicios
│   ├── bodyparts.json         # Partes del cuerpo
│   └── muscles.json           # Grupos musculares
app.py                         # Aplicación principal
```

## 🤝 Contribución

¡Las contribuciones son bienvenidas! Por favor abre un issue o pull request.

## 📄 Licencia

MIT License

---

💪 **¡Construye tu mejor versión con Muscle RPG!** 💪