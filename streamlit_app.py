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

# Descripción del proyecto (adaptada a la especificación solicitada)
st.markdown(
    """
    **Resumen del proyecto**

    La planificación de rutinas de entrenamiento suele ser genérica y poco adaptable al progreso
    individual del usuario, lo que limita la eficiencia de los resultados. Este proyecto propone
    modelar los ejercicios de hipertrofia muscular y su progresión mediante un grafo que representa
    posibles caminos de entrenamiento, permitiendo identificar rutas que maximicen las ganancias
    musculares de forma progresiva y estructurada.

    A diferencia de otros enfoques que abarcan múltiples objetivos (fuerza, resistencia o potencia),
    este trabajo se centrará exclusivamente en la hipertrofia, es decir, el aumento del tamaño del
    músculo a través de una planificación inteligente del volumen, la intensidad y la frecuencia de
    entrenamiento.

    El modelo propuesto busca integrar la planificación de ejercicios en un entorno gamificado,
    donde el usuario “sube de nivel” al completar ciclos de entrenamiento trimestrales (cada 3 meses),
    momento en que el sistema evalúa su progreso, ajusta la rutina y aumenta gradualmente la
    dificultad. Cada sesión de entrenamiento tendrá una duración constante de 2 horas diarias,
    parámetro fijo que facilita el modelamiento y la comparación entre ciclos. De esta forma, el
    sistema puede estructurar rutinas trimestrales personalizadas, maximizando el crecimiento muscular
    y garantizando la adherencia del usuario mediante retroalimentación continua y una sensación de
    progreso similar a la de un videojuego RPG.
    """
)

with st.sidebar:
    st.header("Parámetros")
    days = st.selectbox("Días por semana", [3, 4, 5], index=1)
    # Tiempo por sesión fijo: 2 horas (120 minutos) según especificación
    time_per_session = 120
    st.markdown("**Tiempo por sesión:** 120 minutos (fijo)")
    # Usar session_state para que podamos aplicar recomendaciones desde el cuestionario
    if 'user_level_slider' not in st.session_state:
        st.session_state['user_level_slider'] = 2
    level = st.slider("Nivel del usuario (0=principiante, 4=pro)", min_value=0, max_value=4, value=st.session_state['user_level_slider'], key='user_level_slider')
    # Botón para abrir cuestionario que estima el nivel
    if st.button("¿Cuál es mi nivel? / No sé mi nivel"):
        st.session_state['show_level_quiz'] = True
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

# Mostrar cuestionario para estimar nivel si el usuario lo solicitó
if st.session_state.get('show_level_quiz', False):
    st.markdown("### Cuestionario técnico y de perfil para estimar tu nivel")
    with st.form("level_quiz"):
        # Perfil general (constantes y variables)
        age = st.number_input("Edad (años)", min_value=13, max_value=100, value=25, step=1)
        gender = st.selectbox("Género (opcional)", ["No declarar", "Femenino", "Masculino", "Otro"], index=0)
        height_cm = st.number_input("Estatura (cm)", min_value=100, max_value=230, value=175, step=1)
        weight_kg = st.number_input("Peso actual (kg)", min_value=30.0, max_value=300.0, value=75.0, step=0.5)
        environment = st.selectbox("Entorno de entrenamiento", ["Gimnasio", "En casa", "Híbrido"], index=2)
        # Variables de entrenamiento
        years = st.number_input("¿Cuánto tiempo llevas entrenando consistentemente? (años)", min_value=0.0, max_value=50.0, value=1.0, step=0.5)
        sessions = st.selectbox("Sesiones por semana (promedio)", [1, 2, 3, 4, 5, 6, 7], index=3)
        compounds = st.radio("¿Realizas habitualmente ejercicios compuestos (sentadillas, peso muerto, press banca)?", ["Sí", "No"], index=0)
        stamina_self = st.selectbox("Capacidad de recuperación / 'stamina' (auto-evaluación)", ["Baja", "Media", "Alta"], index=1)
        # Preguntas técnicas (hipertrofia)
        pullups = st.selectbox("Máximo número de dominadas (pull-ups) que puedes hacer seguidas", [0, 1, 3, 5, 10], index=2)
        bench_ratio = st.selectbox("Tu 1RM en press banca en relación a tu peso corporal (aprox)", ["<0.5x", "0.5-0.75x", "0.75-1.0x", ">=1.0x"], index=1)
        weekly_sets = st.selectbox("Promedio de sets semanales por músculo principal", ["<6", "6-10", "11-15", ">15"], index=1)
        periodization = st.radio("¿Sueles planificar periodización (mesociclos/meses)?", ["Sí", "No"], index=1)
        recent_progress = st.radio("En los últimos 3 meses, tu fuerza/volumen ha:", ["Mejorado", "Igual", "Empeorado"], index=0)
        quarter_updates = st.radio("¿Sueles actualizar tus rutinas cada ~3 meses (ciclo trimestral)?", ["Sí", "No"], index=0)
        can_two_hours = st.radio("¿Te sientes cómodo completando sesiones intensas de ~2 horas?", ["Sí", "No"], index=0)
        submitted = st.form_submit_button("Calcular nivel recomendado")

    if submitted:
        # Construir perfil y guardarlo
        user_profile = {
            'age': age,
            'gender': gender,
            'height_cm': height_cm,
            'weight_kg': weight_kg,
            'environment': environment,
            'years': years,
            'sessions_per_week': sessions,
            'uses_compounds': compounds,
            'stamina_self': stamina_self,
            'pullups': pullups,
            'bench_ratio': bench_ratio,
            'weekly_sets': weekly_sets,
            'periodization': periodization,
            'recent_progress': recent_progress,
            'quarter_updates': quarter_updates,
            'can_two_hours': can_two_hours,
        }
        st.session_state['user_profile'] = user_profile

        # Scoring heurístico ampliado (max total aproximado = 24)
        # años (0..3) -> penalizar edad avanzada para recuperación
        if years < 0.5:
            years_score = 0
        elif years < 1.5:
            years_score = 1
        elif years < 3:
            years_score = 2
        else:
            years_score = 3
        # sesiones (0..4)
        if sessions <= 2:
            sess_score = 0
        elif sessions == 3:
            sess_score = 1
        elif sessions == 4:
            sess_score = 2
        elif sessions == 5:
            sess_score = 3
        else:
            sess_score = 4
        comp_score = 1 if compounds == "Sí" else 0
        twoh_score = 1 if can_two_hours == "Sí" else 0
        # stamina self (penaliza o beneficia) ( -1,0,1 )
        stamina_map = {'Baja': -1, 'Media': 0, 'Alta': 1}
        stamina_score = stamina_map.get(stamina_self, 0)
        # dominadas (0..3)
        if pullups == 0:
            pullups_score = 0
        elif pullups == 1:
            pullups_score = 1
        elif pullups == 3:
            pullups_score = 2
        else:
            pullups_score = 3
        # bench ratio (0..3)
        if bench_ratio == "<0.5x":
            bench_score = 0
        elif bench_ratio == "0.5-0.75x":
            bench_score = 1
        elif bench_ratio == "0.75-1.0x":
            bench_score = 2
        else:
            bench_score = 3
        # weekly sets (0..3)
        if weekly_sets == "<6":
            sets_score = 0
        elif weekly_sets == "6-10":
            sets_score = 1
        elif weekly_sets == "11-15":
            sets_score = 2
        else:
            sets_score = 3
        period_score = 1 if periodization == "Sí" else 0
        progress_score = 1 if recent_progress == "Mejorado" else 0
        env_score = 1 if environment == 'Gimnasio' else 0
        quarter_score = 1 if quarter_updates == "Sí" else 0

        total = (years_score + sess_score + comp_score + twoh_score + stamina_score + pullups_score + bench_score + sets_score + period_score + progress_score + env_score + quarter_score)
        # máximo teorico aproximado = 23
        max_possible = 23
        normalized = max(0, min(total, max_possible))
        recommended = int(round((normalized / max_possible) * 4))
        recommended = max(0, min(4, recommended))
        st.session_state['recommended_level'] = recommended
        label = {0: 'Principiante', 1: 'Básico', 2: 'Intermedio', 3: 'Avanzado', 4: 'Profesional'}[recommended]
        st.success(f"Nivel recomendado: {recommended} ({label})")
        with st.expander("Ver desglose de puntuación y perfil registrado"):
            st.write({'user_profile': user_profile, 'scores': {
                'years_score': years_score,
                'sessions_score': sess_score,
                'compounds': comp_score,
                'two_hour_tolerance': twoh_score,
                'stamina_score': stamina_score,
                'pullups_score': pullups_score,
                'bench_score': bench_score,
                'weekly_sets_score': sets_score,
                'periodization': period_score,
                'recent_progress': progress_score,
                'environment_score': env_score,
                'quarter_update_score': quarter_score,
                'total_raw': total,
                'recommended_level': recommended,
            }})
        if st.button("Aplicar nivel recomendado"):
            st.session_state['user_level_slider'] = recommended
            st.session_state['show_level_quiz'] = False
            st.experimental_rerun()
