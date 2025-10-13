# Documentación Técnica - Sistema de Grafos con Programación Dinámica

## 1. Introducción

Este documento describe la arquitectura y algoritmos del sistema de optimización de rutinas de ejercicio basado en **Programación Dinámica** y **Teoría de Grafos**.

## 2. Modelo del Problema

### 2.1 Definiciones

**Estado del Sistema (S)**:
```
S = {s₁, s₂, ..., sₙ}
donde sᵢ = estamina actual de la parte del cuerpo i
```

**Ejercicio (E)**:
```
E = (id, name, target_muscles, body_parts, cost)
cost = base_cost × (1 + complexity × 0.1)
complexity = |target_muscles| + |secondary_muscles|
```

**Transición de Estado**:
```
S' = T(S, E) = {s'₁, s'₂, ..., s'ₙ}
donde s'ᵢ = max(0, sᵢ - cost) si i ∈ body_parts(E)
```

**Función de Recuperación**:
```
R(S) = {min(maxᵢ, sᵢ + recovery_rate) para todo i}
```

### 2.2 Función Objetivo

Maximizar el beneficio total del programa:

```
maximize: ∑∑∑ B(e, w)
          w d e

donde:
- w = semana (1 a W)
- d = día (1 a D)
- e = ejercicio
- B(e, w) = beneficio del ejercicio e en la semana w
```

**Función de Beneficio**:
```
B(e, w) = (|target_muscles(e)| × 10 + |secondary_muscles(e)| × 5) × (1 + w × 0.05)
```

### 2.3 Restricciones

1. **Estamina**: `sᵢ ≥ cost(e)` para todo `i ∈ body_parts(e)`
2. **Ejercicios por día**: `|exercises_day| ≤ max_exercises`
3. **No negatividad**: `sᵢ ≥ 0` para todo `i`
4. **Capacidad**: `0 ≤ sᵢ ≤ maxᵢ` para todo `i`

## 3. Estructura del Grafo

### 3.1 Definición del Grafo

```
G = (V, E, W)

V = {nodos de ejercicios}
E = {aristas de transición}
W = {pesos de las aristas}
```

**Nodo (v ∈ V)**:
```
v = (exercise, day, week, stamina_state, benefit)
```

**Arista (e ∈ E)**:
```
e = (vᵢ, vⱼ) existe si:
  1. day(vⱼ) = day(vᵢ) + 1, o
  2. day(vᵢ) = day(vⱼ) y sᵢ es suficiente para vⱼ
```

**Peso (w ∈ W)**:
```
w(vᵢ, vⱼ) = -cost(exercise(vⱼ))
```

### 3.2 Propiedades del Grafo

1. **Dirigido Acíclico (DAG)**: Por la naturaleza temporal
2. **Ponderado**: Pesos representan costos de estamina
3. **Multi-capa**: Una capa por día
4. **Densamente conectado**: Dentro de cada capa

## 4. Algoritmo de Programación Dinámica

### 4.1 Tabla DP

```
DP[d][h] = (max_benefit, exercises[], state)

donde:
- d = día (0 a D)
- h = hash del estado de estamina
- max_benefit = beneficio máximo alcanzable
- exercises = secuencia de ejercicios
- state = estado de estamina resultante
```

### 4.2 Inicialización

```
DP[0][h₀] = (0, [], S₀)

donde:
- h₀ = hash(S₀)
- S₀ = estado inicial con estamina máxima
```

### 4.3 Recurrencia

Para cada día `d` de 0 a D-1:
```
Para cada estado (h, (benefit, exercises, state)) en DP[d]:
    1. Filtrar ejercicios válidos:
       E_valid = {e | can_perform(e, state)}
    
    2. Ordenar por beneficio:
       E_sorted = sort(E_valid, key=λe: B(e, w), reverse=True)
    
    3. Seleccionar mejores N ejercicios:
       E_selected = E_sorted[:N]
    
    4. Calcular nuevo estado:
       state' = state
       benefit' = benefit
       
       Para cada e en E_selected:
           state' = T(state', e)
           benefit' += B(e, w)
    
    5. Aplicar recuperación:
       state'' = R(state')
    
    6. Actualizar DP:
       h' = hash(state'')
       Si DP[d+1][h'] no existe o DP[d+1][h'][0] < benefit':
           DP[d+1][h'] = (benefit', exercises + [E_selected], state'')
```

### 4.4 Solución Óptima

```
solution = argmax_{h ∈ DP[D]} DP[D][h][0]
```

### 4.5 Pseudocódigo Completo

```python
def build_optimal_week(graph, week, days, exercises_per_day):
    # Inicialización
    DP = [{} for _ in range(days + 1)]
    S_initial = initial_stamina_state()
    DP[0][hash(S_initial)] = (0, [], S_initial)
    
    # Programación dinámica
    for d in range(days):
        for h, (benefit, ex_history, state) in DP[d].items():
            # Filtrar ejercicios válidos
            valid_exercises = filter_valid(graph.exercises, state)
            
            # Ordenar por beneficio
            valid_exercises.sort(
                key=lambda e: calculate_benefit(e, week),
                reverse=True
            )
            
            # Seleccionar mejores N ejercicios
            selected = valid_exercises[:exercises_per_day]
            
            # Calcular nuevo estado
            new_state = state.copy()
            new_benefit = benefit
            
            for exercise in selected:
                new_state = transition(new_state, exercise)
                new_benefit += calculate_benefit(exercise, week)
            
            # Recuperación
            new_state = recover(new_state)
            new_hash = hash(new_state)
            
            # Actualizar DP table
            new_history = ex_history + [selected]
            if (new_hash not in DP[d+1] or 
                DP[d+1][new_hash][0] < new_benefit):
                DP[d+1][new_hash] = (new_benefit, new_history, new_state)
    
    # Extraer solución óptima
    best_benefit = -1
    best_schedule = []
    
    for h, (benefit, schedule, _) in DP[days].items():
        if benefit > best_benefit:
            best_benefit = benefit
            best_schedule = schedule
    
    return best_schedule
```

## 5. Análisis de Complejidad

### 5.1 Complejidad Temporal

**Por Semana**:
```
O(D × S × E × log(E) × N)

donde:
- D = días por semana
- S = número de estados únicos (discretizados)
- E = número total de ejercicios
- N = ejercicios por día
```

**Factores de complejidad**:
1. Iteración por días: `O(D)`
2. Estados en DP table: `O(S)`
3. Filtrado de ejercicios: `O(E)`
4. Ordenamiento: `O(E log E)`
5. Selección de N ejercicios: `O(N)`

**Programa Completo** (W semanas):
```
O(W × D × S × E × log(E) × N)
```

### 5.2 Optimizaciones Implementadas

1. **Discretización de Estados**:
   ```python
   discretized_state[k] = (v // 10) * 10
   ```
   Reduce S de `∏ᵢ maxᵢ` a `∏ᵢ (maxᵢ / 10)`

2. **Limitación de Ejercicios**:
   Solo se procesan los primeros 100 ejercicios por defecto

3. **Early Pruning**:
   Ejercicios inválidos se filtran antes del ordenamiento

4. **Hash Caching**:
   Los hashes de estado se calculan una sola vez

### 5.3 Complejidad Espacial

```
O(D × S + E)

donde:
- D × S = tamaño de la tabla DP
- E = almacenamiento de ejercicios
```

## 6. Estrategias de Optimización

### 6.1 Greedy Component

Dentro de cada estado, se usa un enfoque greedy:
```
Seleccionar ejercicios con máximo beneficio/costo
```

Esto es óptimo localmente pero la DP garantiza optimalidad global.

### 6.2 Memoización

```python
# Cache de estados visitados
visited_states = {}

def get_or_compute(state):
    h = hash(state)
    if h not in visited_states:
        visited_states[h] = compute(state)
    return visited_states[h]
```

### 6.3 Progresión Adaptativa

```python
if week % 2 == 0:
    for bodypart in bodyparts:
        bodypart.max_stamina *= 1.05  # +5% capacidad
```

Simula adaptación muscular al entrenamiento.

## 7. Casos Especiales

### 7.1 Estado Sin Ejercicios Válidos

```python
if len(valid_exercises) == 0:
    # Día de descanso forzado
    DP[d+1][hash(R(state))] = (benefit, exercises + [[]], R(state))
```

### 7.2 Múltiples Óptimos

Si existen múltiples programas con el mismo beneficio:
```python
# Se selecciona el primero encontrado
# Posible mejora: usar criterios de desempate
```

### 7.3 Semanas con Progresión

```python
benefit_multiplier = 1 + (week * 0.05)
B(e, w) = base_benefit(e) × benefit_multiplier
```

## 8. Validación y Testing

### 8.1 Invariantes

1. **Estamina no negativa**: `assert all(s >= 0 for s in state.values())`
2. **Estamina no excede máximo**: `assert all(s <= max_s for s, max_s in ...)`
3. **Beneficio creciente**: `assert DP[d+1][h][0] >= DP[d][h'][0]` para algún h'

### 8.2 Pruebas Unitarias

```python
def test_stamina_consumption():
    """Verifica que la estamina se consume correctamente"""
    state = {'chest': 100}
    exercise = Exercise(..., body_parts=['chest'], stamina_cost=30)
    new_state = update_stamina_state(exercise, state)
    assert new_state['chest'] == 70

def test_recovery():
    """Verifica la recuperación de estamina"""
    state = {'chest': 50}
    recovered = recover_stamina_state(state, days=1)
    assert recovered['chest'] == 70  # +20

def test_benefit_calculation():
    """Verifica el cálculo de beneficios"""
    exercise = Exercise(target_muscles=['pecs'], secondary_muscles=['triceps'])
    benefit = calculate_exercise_benefit(exercise, week=1)
    assert benefit == (1 * 10 + 1 * 5) * 1.05
```

## 9. Extensiones Futuras

### 9.1 Multi-objetivo

Optimizar múltiples objetivos simultáneamente:
```
maximize: α × benefit + β × variety - γ × fatigue
```

### 9.2 Aprendizaje

Ajustar parámetros basándose en feedback:
```
stamina_cost' = stamina_cost × (1 - learning_rate × performance)
```

### 9.3 Restricciones Adicionales

- Equipamiento disponible
- Tiempo disponible por sesión
- Preferencias del usuario
- Lesiones o limitaciones

### 9.4 Algoritmos Alternativos

- **Branch and Bound**: Para soluciones exactas
- **Simulated Annealing**: Para espacios de búsqueda grandes
- **Algoritmos Genéticos**: Para personalización extrema

## 10. Referencias

1. Bellman, R. (1957). "Dynamic Programming"
2. Cormen, T. H., et al. (2009). "Introduction to Algorithms"
3. Kleinberg, J., & Tardos, É. (2005). "Algorithm Design"
4. Papadimitriou, C. H., & Steiglitz, K. (1998). "Combinatorial Optimization"

---

**Última actualización**: Octubre 2025
**Versión**: 1.0
