#!/usr/bin/env python3
"""Prototipo Streamlit para generar y visualizar la rutina.

Interfaz mínima:
 - Selección de días (3/4/5)
 - Tiempo por sesión (minutos)
 - Nivel de usuario (0..4)
 - Botón para generar
 - Visualización por día con gifs e instrucciones
 - Botón para descargar la rutina en JSON
"""
import streamlit as st
import json
from src import routine_builder


st.set_page_config(page_title="Muscle RPG - Prototipo", layout="wide")

st.title("Muscle RPG — Prototipo de generador de rutinas")

with st.sidebar:
    st.header("Parámetros")
    days = st.selectbox("Días por semana", [3, 4, 5], index=1)
    time_per_session = st.slider("Tiempo por sesión (minutos)", min_value=30, max_value=240, value=120, step=10)
    level = st.slider("Nivel del usuario (0=principiante, 4=pro)", min_value=0, max_value=4, value=2)
    show_instructions = st.checkbox("Mostrar instrucciones de los ejercicios", value=True)
    generate = st.button("Generar rutina")


def find_exercise_by_id(exercises, ex_id):
    for e in exercises:
        if e.get("exerciseId") == ex_id:
            return e
    return None


if generate:
    with st.spinner("Generando rutina..."):
        # Generar rutina usando la lógica existente
        routine = routine_builder.generate_routine(days, time_per_session=time_per_session, user_level=level)
        exercises = routine_builder.load_exercises()

    st.success("Rutina generada")

    # Mostrar resumen
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Plan semanal")
        schedule = routine.get("schedule", {})
        for day_key in sorted(k for k in schedule.keys() if not k.endswith("_meta")):
            meta = schedule.get(day_key + "_meta", {})
            st.markdown(f"### {day_key.replace('_', ' ').title()} — Tiempo total: {meta.get('total_time_min', 0)} min")
            items = schedule.get(day_key, [])
            if not items:
                st.write("(Sin ejercicios para este día)")
            for ex in items:
                ex_raw = find_exercise_by_id(exercises, ex.get("id"))
                cols = st.columns([1, 4])
                with cols[0]:
                    if ex_raw and ex_raw.get("gifUrl"):
                        st.image(ex_raw.get("gifUrl"), use_column_width=True)
                    else:
                        st.write("")
                with cols[1]:
                    st.markdown(f"**{ex.get('name')}** — {ex.get('sets')}x{ex.get('reps')} reps — {ex.get('time_min')} min")
                    st.markdown(f"_Músculos:_ {', '.join(ex.get('muscles', []))}")
                    if show_instructions and ex_raw:
                        instr = ex_raw.get("instructions") or []
                        if instr:
                            st.markdown("**Instrucciones:**")
                            for step in instr:
                                st.write(step)
                    st.write("---")

    with col2:
        st.subheader("Resumen semanal")
        done = routine.get("weekly_sets_done", {})
        target = routine.get("weekly_target_per_muscle", 0)
        st.write("Sets por músculo (hecho / objetivo):")
        for m, v in done.items():
            st.write(f"- {m}: {v}/{target}")

        st.write("")
        st.subheader("Estamina")
        limits = routine.get("stamina_limit_per_muscle", {})
        used = routine.get("stamina_used", {})
        rem = routine.get("stamina_remaining", {})
        for m in sorted(limits.keys()):
            st.write(f"- {m}: usado {used.get(m,0)} / límite {limits.get(m,0)} (rem: {rem.get(m,0)})")

        st.write("")
        st.subheader("Exportar")
        json_bytes = json.dumps(routine, ensure_ascii=False, indent=2).encode("utf-8")
        st.download_button(label="Descargar rutina (JSON)", data=json_bytes, file_name="routine.json", mime="application/json")

    st.sidebar.markdown("---")
    st.sidebar.caption("Prototipo: usa la lógica en `src/routine_builder.py`")

else:
    st.info("Configura parámetros a la izquierda y pulsa 'Generar rutina' para crear un prototipo interactivo.")
