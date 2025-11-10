"""Optimizer module: construye el grafo/estado y aplica programación dinámica (mochila por sesión)

Este módulo ofrece una función de contrato simple:
  optimize_weekly_routine(items, num_days, time_per_session, user_level)

Donde `items` es la lista producida por `routine_builder.build_items` (cada item contiene
  keys: id, name, muscles, sets, reps, time, raw)

La intención es separar la lógica de optimización del builder para que sea fácil de
probar y extender siguiendo el informe proporcionado.
"""
from typing import List, Dict, Any


def _is_compound_from_raw(raw: Dict[str, Any]) -> bool:
    """Heurística local para determinar si un ejercicio es compuesto usando el raw dict."""
    large = {"glutes", "quads", "pectorals", "lats", "upper back", "hamstrings"}
    equip_compounds = {"barbell", "dumbbell", "kettlebell", "olympic barbell", "smith machine", "leverage machine", "trap bar"}
    if not raw:
        return False
    muscles = set(m.lower() for m in raw.get("targetMuscles", []) or [])
    if muscles & large:
        return True
    eqs = set(e.lower() for e in raw.get("equipments", []) or [])
    if eqs & equip_compounds:
        return True
    return False


def _knapsack_max_value(items: List[Dict[str, Any]], capacity: int, values: List[int]) -> List[int]:
    """0/1 knapsack returning indices from `items` (relative to items list).
    capacity and weights are integers (minutes)
    """
    n = len(items)
    dp = [0] * (capacity + 1)
    pick = [[False] * n for _ in range(capacity + 1)]

    for i in range(n):
        w = items[i]["time"]
        v = values[i]
        if w > capacity:
            continue
        for t in range(capacity, w - 1, -1):
            if dp[t - w] + v > dp[t]:
                dp[t] = dp[t - w] + v
                pick[t] = pick[t - w].copy()
                pick[t][i] = True

    best_t = max(range(capacity + 1), key=lambda x: dp[x])
    selected = [i for i, chosen in enumerate(pick[best_t]) if chosen]
    return selected


def optimize_weekly_routine(items: List[Dict[str, Any]], num_days: int, time_per_session: int = 120, user_level: int = 2) -> Dict[str, Any]:
    """Optimiza la rutina semanal.

    Objetivo (informal, inspirado en el informe): maximizar la contribución a los sets
    semanales por músculo (priorizar llenar el objetivo por músculo) sujeto a límites de
    estamina por músculo y tiempo por sesión.

    Entrada:
      - items: lista preprocesada (ver contract en la cabecera del módulo)
      - num_days: número de días por semana
      - time_per_session: minutos disponibles por sesión
      - user_level: entero [0..4] (solo 0/1 usado por la UI ahora)

    Salida: dict con la misma forma que devolvía `routine_builder.generate_routine`.
    """
    # parámetros heurísticos
    target_per_muscle = 10  # sets objetivo por semana
    # stamina mapping (unidad arbitraria)
    stamina_map = {0: 80, 1: 110, 2: 140, 3: 180, 4: 220}
    level = int(user_level or 2)

    muscles = set()
    for it in items:
        muscles.update([m for m in it.get("muscles", [])])

    remaining_sets = {m: target_per_muscle for m in muscles}
    stamina_limit = {m: stamina_map.get(level, 140) for m in muscles}
    stamina_remaining = stamina_limit.copy()

    # calcular coste de estamina por item distribuido entre músculos objetivo
    REPS_BY_LEVEL = {0: 8, 1: 8, 2: 10, 3: 12, 4: 12}
    item_stamina_costs: List[Dict[str, int]] = []
    for it in items:
        intensity = 1.5 if _is_compound_from_raw(it.get("raw")) else 1.0
        reps_for_item = it.get("reps") or REPS_BY_LEVEL.get(level, 10)
        total_cost = int(it["sets"] * reps_for_item * intensity)
        muscles_target = it.get("muscles", []) or []
        costs = {}
        if muscles_target:
            per_m = max(1, total_cost // len(muscles_target))
            for m in muscles_target:
                costs[m] = per_m
        item_stamina_costs.append(costs)

    schedule = {f"day_{i+1}": [] for i in range(num_days)}

    for d in range(num_days):
        # calcular valor heurístico de cada item: contribución a remaining_sets
        values = []
        for it in items:
            v = 0
            for m in it.get("muscles", []):
                if remaining_sets.get(m, 0) > 0:
                    v += min(it["sets"], remaining_sets[m])
            values.append(v)

        # candidatos que aportan valor y cumplen estamina
        candidate_indices = [i for i, val in enumerate(values) if val > 0]
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
            # intentar compuestos para llenar tiempo si no hay candidatos que aporten
            for i in range(len(items)):
                costs = item_stamina_costs[i]
                ok = all(cost <= stamina_remaining.get(m, 0) for m, cost in costs.items())
                if ok and _is_compound_from_raw(items[i].get("raw")):
                    candidate_indices.append(i)
            if not candidate_indices:
                schedule[f"day_{d+1}" + "_meta"] = {"total_time_min": 0}
                continue

        candidates = [items[i] for i in candidate_indices]
        cand_values = [values[i] for i in candidate_indices]

        selected_local = _knapsack_max_value(candidates, time_per_session, cand_values)
        selected = [candidate_indices[i] for i in selected_local]

        total_time = 0
        for idx in selected:
            it = items[idx]
            schedule[f"day_{d+1}"].append({
                "id": it["id"],
                "name": it["name"],
                "sets": it["sets"],
                "reps": it.get("reps"),
                "time_min": it["time"],
                "muscles": it.get("muscles", []),
                "stamina_costs": item_stamina_costs[idx],
            })
            total_time += it["time"]
            for m in it.get("muscles", []):
                if remaining_sets.get(m, 0) > 0:
                    remaining_sets[m] = max(0, remaining_sets[m] - it["sets"])
            for m, cost in item_stamina_costs[idx].items():
                stamina_remaining[m] = max(0, stamina_remaining.get(m, 0) - cost)

        schedule[f"day_{d+1}" + "_meta"] = {"total_time_min": total_time}

    done = {m: (target_per_muscle - remaining_sets[m]) for m in muscles}
    stamina_used = {m: stamina_limit[m] - stamina_remaining.get(m, 0) for m in muscles}

    return {
        "schedule": schedule,
        "weekly_sets_done": done,
        "weekly_target_per_muscle": target_per_muscle,
        "stamina_limit_per_muscle": stamina_limit,
        "stamina_used": stamina_used,
        "stamina_remaining": stamina_remaining,
    }
