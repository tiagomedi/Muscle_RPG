# Muscle RPG — Método de resolución por Programación Dinámica (DP)

Este documento describe en detalle el método de resolución basado en Programación Dinámica utilizado por el componente de optimización de rutinas de este proyecto. Está escrito para desarrolladores y estudiantes que quieran entender la formulación, el estado, la recurrencia, las decisiones de diseño y cómo integrar y probar el algoritmo en el código existente.

## Resumen

El objetivo es generar una rutina de ejercicios (secuencia de ejercicios por día) optimizada para maximizar la cobertura y el beneficio sobre un conjunto de músculos objetivo, respetando restricciones prácticas: tiempo disponible por sesión, disponibilidad de equipamiento y límites de estamina (fatiga) por músculo.

Para modelar el problema usamos:

- Un grafo dirigido de ejercicios (`exercise_graph`) donde cada nodo es un ejercicio y las aristas representan transiciones válidas (con pesos que reflejan la compatibilidad: overlap muscular y continuidad de equipamiento).
- Una formulación de Programación Dinámica que explora secuencias respetando tiempo total y fatiga muscular, y hace backtracking para reconstruir la secuencia óptima.

El implemento principal se encuentra en `src/optimizer/routine_optimizer.py`.

## Contrato (inputs / outputs)

- Inputs principales:
  - time_available: entero (minutos) — tiempo disponible para la sesión.
  - user_level: entero (nivel usado para heurísticas de sets/reps).
  - target_muscles: lista de cadenas — músculos que queremos priorizar.
  - equipment_available: conjunto de cadenas — equipamiento disponible del usuario.
  - stamina: diccionario {musculo: float} — factor de frescura / fatiga por músculo.

- Output:
  - Una lista ordenada de ejercicios (rutina) con metadatos: id, nombre, sets, reps, tiempo y músculos trabajados.

## Modelado del estado (DP)

Definimos una función valor óptimo:

$$V(t, M, last)$$

donde:

- $t$ = tiempo restante (minutos)
- $M$ = conjunto de músculos ya trabajados (estado de cobertura)
- $last$ = id del último ejercicio realizado (usado para validar transiciones por el grafo)

La idea: desde el estado $(t, M, last)$, elegir un ejercicio $e$ que quepa en $t$, sea compatible con la transición desde $last$, y maximice

$$ value(e, M) + V(t - time(e), M \cup muscles(e), e) $$

donde $value(e, M)$ es una heurística que valora cuán útil es ejecutar $e$ dado los músculos ya trabajados y la frescura (stamina).

Condiciones base:

- Si $t < t_{min}$ (tiempo mínimo para un ejercicio), $V(t, M, last) = 0$.

Almacenamos los resultados de subproblemas en un diccionario `dp[(t, frozenset(M), last)]` para memoización y un `backtrack` que guarda la elección tomada.

## Recurrencia (detalles prácticos)

Para cada ejercicio candidato $e$ (filtrado por equipamiento y tiempo):

1. Comprobar si existe arista $(last \to e)$ en el grafo (si `last` no es None). Si no existe, saltar.
2. Calcular $v = value(e, M)$ — suma de contribuciones por cada músculo objetivo del ejercicio, ponderada por la frescura `stamina[muscle]` y por si el músculo ya fue trabajado recientemente.
3. Calcular $future = V(t - time(e), M \cup muscles(e), e)$ (recursiva, memoizada).
4. $total = v + future$. Si $total$ es mayor que el mejor conocido, guardar $e$ como la mejor elección.

Al final, $V(t, M, last)$ será el mejor valor encontrado, y `backtrack[(t, M, last)]` apuntará al ejercicio elegido.

## Pseudocódigo

El siguiente pseudocódigo resume la implementación:

```
def solve_dp(t, M, last):
    if t < t_min: return 0
    if (t, M, last) in dp: return dp[(t,M,last)]

    best = 0
    best_ex = None
    for e in available_exercises:
        if time(e) > t: continue
        if last and not graph.has_edge(last, e.id): continue
        v = value(e, M)
        if v <= 0: continue
        newM = M union muscles(e)
        future = solve_dp(t - time(e), newM, e.id)
        if v + future > best:
            best = v + future
            best_ex = e

    dp[(t,M,last)] = best
    backtrack[(t,M,last)] = best_ex
    return best

# reconstrucción
t = time_available
M = empty set
last = None
routine = []
while t >= t_min:
    ex = backtrack.get((t, frozenset(M), last))
    if not ex: break
    routine.append(ex)
    t -= time(ex)
    M = M union muscles(ex)
    last = ex.id

return routine
```

## Función de valor (heurística)

La función `value(e, M)` combina:

- Cobertura muscular: más alto si `e` trabaja músculos en `target_muscles` que aún no están suficientemente trabajados.
- Frescura / staminas: multiplica la contribución por `stamina[muscle]` para preferir músculos descansados.
- Penalización por repetir demasiado el mismo músculo: si el músculo ya está en $M$, reducir su contribución.
- Bonus por continuidad de equipamiento (en la construcción del grafo se prefieren transiciones con mismo equipamiento).

Esta heurística es flexible y puede modificarse para priorizar intensidad, variedad o minimizar transiciones de equipamiento.

## Podas y optimizaciones

- Filtrado inicial de ejercicios por equipamiento disponible.
- Umbral mínimo para considerar una transición (por ejemplo, peso mínimo de arista en el grafo).
- Uso de `frozenset` para representar `M` en las claves de memoización.
- Se evita generar estados con tiempos continuos: el tiempo se trata en minutos (entero) para mantener el espacio finito.

## Complejidad

Sea $T$ el tiempo máximo (en minutos) y $E$ el número de ejercicios candidatos. En el peor caso el número de estados es O(T * 2^{m} * E) si modelásemos exactamente conjuntos de músculos (con $m$ músculos posibles). En la implementación práctica:

- Representamos $M$ como frozenset con sólo los músculos que aparecen: el factor exponencial en $m$ es la principal fuente de crecimiento.
- El coste real depende mucho de la cardinalidad de músculos por ejercicio y del filtrado por equipamiento.

Por eso esta solución es una heurística/DP con memoización y podas prácticas para casos reales (no pretende resolver conjuntos muy grandes de músculos exhaustivamente sin mejoras adicionales).

## Edge cases / Casos especiales

- Si `time_available` es menor que el tiempo mínimo por ejercicio (p. ej. 15 min), la rutina será vacía.
- Si no existen ejercicios compatibles con el equipamiento, se devuelve lista vacía y se muestra una advertencia.
- Si la función `value` devuelve 0 para todos los ejercicios (ej. objetivos cumplidos), DP terminará sin seleccionar más ejercicios.

## Integración con el código existente

- `src/optimizer/routine_optimizer.py` implementa `RoutineOptimizer` y la lógica DP descrita. Es el punto de entrada para usar la optimización basada en grafos + DP.
- `src/routine_builder.py` genera rutinas usando una heurística knapsack por día (estrategia más simple). El optimizador es una ruta alternativa/más avanzada y puede reemplazar o completar `routine_builder` para generar rutinas por sesión.

Para invocar el optimizador desde la app Streamlit (ejemplo):

```python
from src.optimizer.routine_optimizer import RoutineOptimizer

opt = RoutineOptimizer(data_path="src/data")
routine = opt.optimize_workout(
    time_available=120,
    user_level=2,
    target_muscles=['pectorals', 'lats'],
    equipment_available={'barbell','dumbbell'},
    stamina={'pectorals':1.0,'lats':0.9}
)
```

## Cómo probar y validar

1. Genera una rutina de prueba usando `routine_builder.generate_routine` o la clase `RoutineOptimizer`.
2. Guarda la rutina mediante `DatabaseManager.save_routine(username, routine)`.
3. Abre la página `Mi rutina` o `Seguimiento` en la app Streamlit y verifica que los ejercicios y metas aparecen.
4. Para pruebas unitarias, crea rutinas pequeñas (2-4 ejercicios) y comprueba que la reconstrucción desde `backtrack` genera una secuencia que no viola tiempo ni estamina y que mejora la métrica objetivo.

## Limitaciones y mejoras futuras

- Estado: el uso de conjuntos de músculos en la clave de DP explota combinatoria; una mejora posible es agrupar músculos por macrógupos o usar un vector de contadores discretizados para convertir el espacio en polinomial.
- Planificación multi-día: actualmente la DP resuelve una sesión; extender a planificación semanal/global requiere otro nivel de DP o programación por etapas (jerárquica).
- Optimización multi-objetivo: incluir intensidad, variedad, y preferencia del usuario.

---

Si quieres, puedo añadir un ejemplo de test unitario en `tests/test_routine_optimizer.py` que verifique la solución para un caso pequeño y rápido.

## Ejecutar con Docker (opcional)

He añadido un `Dockerfile` y `docker-compose.yml` para que puedas ejecutar la aplicación fácilmente y que tu profesor la abra en su navegador.

Pasos rápidos (PowerShell):

```powershell
# Construir y levantar el contenedor en background
docker compose up --build -d

# Ver logs (opcional)
docker compose logs -f

# Parar y remover contenedores
docker compose down
```

Después de levantar, abre http://localhost:8501 en el navegador. El servicio ejecuta `streamlit_app.py` como entrada.

Notas:
- El `docker-compose.yml` hace un bind-mount del directorio del proyecto dentro del contenedor para facilitar desarrollo; si prefieres un contenedor inmutable, elimina la sección `volumes` del servicio antes de distribuir.
- Si tu profesor no tiene Docker, puedo preparar una imagen y subirla a Docker Hub (necesitarías darme permiso para empujar o yo te doy instrucciones para hacerlo localmente).

