import json
import os
from typing import List, Dict, Any, Tuple

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_exercises(path: str = None) -> List[Dict[str, Any]]:
    p = path or os.path.join(DATA_DIR, "exercises.json")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def is_compound(ex: Dict[str, Any]) -> bool:
    # Heurística: movimientos que trabajan grandes grupos musculares y usan barras/mancuernas/kettlebell/olympic
    large = {"glutes", "quads", "pectorals", "lats", "upper back", "quads", "hamstrings"}
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


def build_items(exercises: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    items = []
    for ex in exercises:
        sets, time = estimate_sets_and_time(ex)
        items.append({
            "id": ex.get("exerciseId"),
            "name": ex.get("name"),
            "muscles": ex.get("targetMuscles", []),
            "sets": sets,
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
    """
    Genera una rutina semanal distribuida en `num_days` días.
    Estrategia:
      - Objetivo semanal por músculo: 10 sets (heurística para hipertrofia)
      - Para cada día, resolvemos una mochila (knapsack) que maximiza la contribución a los sets faltantes
        por minuto de entrenamiento.
    Devuelve un diccionario con la lista de ejercicios por día y métricas.
    """
    exercises = load_exercises(exercises_path)
    items = build_items(exercises)

    # weekly target sets por músculo (hipertrofia)
    target_per_muscle = 10
    # construir lista de músculos presentes
    muscles = set()
    for it in items:
        muscles.update(it["muscles"])
    remaining = {m: target_per_muscle for m in muscles}

    # Estamina semanal por músculo según nivel (user_level pasado como parámetro)
    # calcular límite por músculo
    stamina_limit_per_muscle = {m: default_level_stamina_limit(user_level) for m in muscles}
    stamina_remaining = stamina_limit_per_muscle.copy()

    # calcular consumo de estamina por ejercicio (distribuido entre músculos objetivo)
    # fórmula: consumo_total = sets * reps(level) * intensidad
    # intensidad: 1.5 para compuestos, 1.0 para aislados
    reps = REPS_BY_LEVEL.get(user_level, 10)
    item_stamina_costs: List[Dict[str, int]] = []
    for it in items:
        intensity = 1.5 if is_compound(it["raw"]) else 1.0
        total_cost = int(it["sets"] * reps * intensity)
        muscles_target = it["muscles"] or []
        costs = {}
        if muscles_target:
            per_m = max(1, total_cost // len(muscles_target))
            for m in muscles_target:
                costs[m] = per_m
        item_stamina_costs.append(costs)

    schedule = {f"day_{i+1}": [] for i in range(num_days)}

    for d in range(num_days):
        # calcular valor heurístico de cada item según remaining required sets
        values = []
        for it in items:
            v = 0
            for m in it["muscles"]:
                if remaining.get(m, 0) > 0:
                    v += min(it["sets"], remaining[m])
            # si no contribuye a remaining, dar un pequeño valor para variedad
            if v == 0:
                v = 0  # preferimos no seleccionar inútiles; permitirá llenar tiempo con primeros compuestos
            values.append(v)
        # filter out zero-value items to speed DP; but keep some if nothing remains
        candidate_indices = [i for i, val in enumerate(values) if val > 0]
        # además filtrar por estamina restante: eliminar items que excedan stamina_remaining en cualquier músculo
        filtered = []
        for i in candidate_indices:
            costs = item_stamina_costs[i]
            ok = True
            for m, cost in costs.items():
                if cost > stamina_remaining.get(m, 0):
                    ok = False
                    break
            if ok:
                filtered.append(i)
        candidate_indices = filtered
        if not candidate_indices:
            # si no quedan candidatos que aporten o que cumplan estamina, intentamos buscar ejercicios compuestos
            candidate_indices = []
            for i in range(len(items)):
                costs = item_stamina_costs[i]
                # incluir solo si no excede estamina
                ok = True
                for m, cost in costs.items():
                    if cost > stamina_remaining.get(m, 0):
                        ok = False
                        break
                if ok and is_compound(items[i]["raw"]):
                    candidate_indices.append(i)
            # si aun así está vacío, no podemos llenar más este día (estamina/semanal cumplida)
            if not candidate_indices:
                # marcar día vacío y continuar
                schedule[f"day_{d+1}" + "_meta"] = {"total_time_min": 0}
                continue

        # Build candidate list
        candidates = [items[i] for i in candidate_indices]
        # valores para los candidatos (siempre tomamos desde la lista `values` original)
        cand_values = [values[i] for i in candidate_indices]

        selected_local = knapsack_max_value(candidates, time_per_session, cand_values)
        # map back indices
        selected = [candidate_indices[i] for i in selected_local]

        total_time = 0
        for idx in selected:
            it = items[idx]
            schedule[f"day_{d+1}"].append({
                "id": it["id"],
                "name": it["name"],
                "sets": it["sets"],
                "reps": reps,
                "time_min": it["time"],
                "muscles": it["muscles"],
                "stamina_costs": item_stamina_costs[idx],
            })
            total_time += it["time"]
            # reducir remaining
            for m in it["muscles"]:
                if remaining.get(m, 0) > 0:
                    remaining[m] = max(0, remaining[m] - it["sets"])
            # reducir estamina restante
            for m, cost in item_stamina_costs[idx].items():
                stamina_remaining[m] = max(0, stamina_remaining.get(m, 0) - cost)

        schedule[f"day_{d+1}" + "_meta"] = {"total_time_min": total_time}

    # resumen semanal
    done = {m: (target_per_muscle - remaining[m]) for m in muscles}
    # incluir resumen de estamina usada y restante
    stamina_used = {m: stamina_limit_per_muscle[m] - stamina_remaining.get(m, 0) for m in muscles}
    return {"schedule": schedule, "weekly_sets_done": done, "weekly_target_per_muscle": target_per_muscle,
        "stamina_limit_per_muscle": stamina_limit_per_muscle, "stamina_used": stamina_used,
        "stamina_remaining": stamina_remaining}


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
