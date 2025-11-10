import json
import os
from typing import List, Dict, Any, Tuple, Union
from src.optimizer.routine_dp import optimize_weekly_routine

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_exercises(path: str = None) -> List[Dict[str, Any]]:
    p = path or os.path.join(DATA_DIR, "exercises.json")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def is_compound(ex: Dict[str, Any]) -> bool:
    # Heurística: movimientos que trabajan grandes grupos musculares y usan barras/mancuernas/kettlebell/olympic
    large = {"glutes", "quads", "pectorals", "lats", "upper back", "hamstrings"}
    equip_compounds = {"barbell", "dumbbell", "kettlebell", "olympic barbell", "smith machine", "leverage machine", "trap bar"}
    if any(m in large for m in ex.get("targetMuscles", [])):
        return True
    if any(eq in equip_compounds for eq in ex.get("equipments", [])):
        return True
    return False


def estimate_sets_and_time(ex: Dict[str, Any]) -> Tuple[int, int]:
    """
    Return (sets, time_minutes) estimate for an exercise.
    - Compound: 4 sets, isolation: 3 sets
    - Time per set incl. rest: 3.5 minutes (approx). We round up to int minutes.
    """
    compound = is_compound(ex)
    sets = 4 if compound else 3
    time_per_set = 4  # minutos por serie incluyendo descansos y montaje
    total_time = sets * time_per_set
    return sets, total_time


def _parse_user_profile(user_profile_or_level: Union[int, Dict[str, Any], None]) -> Dict[str, Any]:
    """Normaliza el perfil de usuario.

    Soporta pasar simplemente un entero (user_level) para compatibilidad.
    Campos soportados en el dict de perfil:
      - level: int (0-4)
      - goal: 'strength'|'hypertrophy'|'endurance'
      - age: int
      - injuries: list of muscle names to evitar
      - equipments: list of available equipments (si None, asumimos todo disponible)
    """
    if user_profile_or_level is None:
        return {"level": 2, "goal": "hypertrophy", "age": 30, "injuries": [], "equipments": None}
    if isinstance(user_profile_or_level, int):
        return {"level": user_profile_or_level, "goal": "hypertrophy", "age": 30, "injuries": [], "equipments": None}
    # ya es un dict
    p = dict(user_profile_or_level)
    return {
        "level": int(p.get("level", 2)),
        "goal": p.get("goal", "hypertrophy"),
        "age": int(p.get("age", 30)),
        "injuries": p.get("injuries", []) or [],
        "equipments": p.get("equipments", None),
    }


GOAL_PARAMS = {
    "strength": {"reps_range": (3, 6), "set_multiplier": 1.25},
    "hypertrophy": {"reps_range": (6, 12), "set_multiplier": 1.0},
    "endurance": {"reps_range": (12, 20), "set_multiplier": 0.8},
}


def _choose_reps_sets_for_exercise(is_cmp: bool, level: int, goal: str) -> Tuple[int, int]:
    """Devuelve (sets, reps) recomendable para un ejercicio según tipo, nivel y objetivo."""
    params = GOAL_PARAMS.get(goal, GOAL_PARAMS["hypertrophy"])
    rmin, rmax = params["reps_range"]
    # escalar reps según nivel: nivel 0->rmin, nivel 4->rmax
    reps = int(round(rmin + (rmax - rmin) * (min(max(level, 0), 4) / 4)))

    # base sets: compuesto -> 4, aislado -> 3
    base_sets = 4 if is_cmp else 3
    sets = int(round(base_sets * params.get("set_multiplier", 1.0) * (1 + level * 0.05)))
    # clamp sets razonable
    sets = max(2, min(6, sets))
    return sets, reps


def build_items(exercises: List[Dict[str, Any]], user_profile_or_level: Union[int, Dict[str, Any], None] = None) -> List[Dict[str, Any]]:
    """Construye la lista de items con sets/reps/time ajustados al perfil del usuario.

    Filtra ejercicios por lesiones y por equipamiento disponible.
    """
    profile = _parse_user_profile(user_profile_or_level)
    level = profile["level"]
    goal = profile["goal"]
    injuries = set([m.lower() for m in profile.get("injuries", [])])
    equipments_avail = profile.get("equipments")

    items = []
    for ex in exercises:
        muscles = [m.lower() for m in ex.get("targetMuscles", [])]
        # Si alguna muscle objetivo está en lesiones, saltar ejercicio
        if any(m in injuries for m in muscles):
            continue

        # Filtrar por equipamiento si se indicó disponibilidad
        if equipments_avail is not None:
            # si el ejercicio requiere un equipamiento que no está en la lista, saltarlo
            eqs = [e.lower() for e in ex.get("equipments", [])]
            if eqs and not any(e in equipments_avail for e in eqs):
                # si todos los equipamientos necesarios no están disponibles, saltar
                continue

        is_cmp = is_compound(ex)
        _, time = estimate_sets_and_time(ex)
        # override sets/reps basados en perfil
        computed_sets, computed_reps = _choose_reps_sets_for_exercise(is_cmp, level, goal)

        items.append({
            "id": ex.get("exerciseId"),
            "name": ex.get("name"),
            "muscles": ex.get("targetMuscles", []),
            "sets": computed_sets,
            "reps": computed_reps,
            "time": time,
            "raw": ex,
        })
    return items


# Reps por nivel (heurística). Se usan para calcular consumo de estamina.
REPS_BY_LEVEL = {
    0: 8,   # principiante
    1: 8,   # básico
    2: 10,  # intermedio
    3: 12,  # avanzado
    4: 12,  # profesional
}

# Aqui estan los niveles de estamina por niveles de usuario -> CAMBIAR \ CORREGIR
def default_level_stamina_limit(level: int) -> int:
    """Devuelve el límite de estamina por músculo para un nivel dado (unidad arbitraria semanal)."""
    mapping = {0: 80, 1: 110, 2: 140, 3: 180, 4: 220}
    return mapping.get(level, 140)


def knapsack_max_value(items: List[Dict[str, Any]], capacity: int, values: List[int]) -> List[int]:
    """
    Solve 0/1 knapsack returning selected indices. capacity in minutes.
    values aligned with items.
    """
    n = len(items)
    # DP table: dp[t] = max value achievable with capacity t
    dp = [0] * (capacity + 1)
    # keep choice by remembering last taken index for each t (store -1 or index)
    pick = [[False] * n for _ in range(capacity + 1)]

    for i in range(n):
        w = items[i]["time"]
        v = values[i]
        # iterate backwards for 0/1 knapsack
        for t in range(capacity, w - 1, -1):
            if dp[t - w] + v > dp[t]:
                dp[t] = dp[t - w] + v
                # copy previous picks
                pick[t] = pick[t - w].copy()
                pick[t][i] = True

    # find best t
    best_t = max(range(capacity + 1), key=lambda x: dp[x])
    selected = [i for i, chosen in enumerate(pick[best_t]) if chosen]
    return selected


def generate_routine(num_days: int, time_per_session: int = 120, exercises_path: str = None, user_level: int = 2) -> Dict[str, Any]:
    """Wrapper que construye los items y delega la optimización al módulo `optimizer`.

    Mantiene la firma y compatibilidad con la versión previa.
    """
    user_profile_or_level = user_level
    exercises = load_exercises(exercises_path)
    items = build_items(exercises, user_profile_or_level)
    return optimize_weekly_routine(items, num_days=num_days, time_per_session=time_per_session, user_level=user_level)


def pretty_print_routine(routine: Dict[str, Any]):
    print("Rutina generada:\n")
    for day, items in routine["schedule"].items():
        if day.endswith("_meta"):
            continue
        meta = routine["schedule"].get(day + "_meta", {})
        print(f"{day}: total_time_min={meta.get('total_time_min', 0)}")
        for ex in items:
            reps = ex.get('reps')
            stamina = ex.get('stamina_costs', {})
            stamina_str = ", ".join(f"{m}: {c}" for m, c in stamina.items()) if stamina else ""
            print(f"  - {ex['name']} ({ex['sets']}x{reps} reps, {ex['time_min']} min) -> {', '.join(ex['muscles'])} {stamina_str}")
        print("")
    print("Resumen semanal de sets por músculo (hecho / objetivo):")
    for m, done in routine["weekly_sets_done"].items():
        print(f"  - {m}: {done}/{routine['weekly_target_per_muscle']}")
    print("\nResumen de estamina por músculo (usado / límite / restante):")
    limits = routine.get('stamina_limit_per_muscle', {})
    used = routine.get('stamina_used', {})
    rem = routine.get('stamina_remaining', {})
    for m in sorted(limits.keys()):
        print(f"  - {m}: {used.get(m,0)}/{limits.get(m,0)} (rem: {rem.get(m,0)})")


if __name__ == "__main__":
    # pequeño test local
    r = generate_routine(4)
    pretty_print_routine(r)
