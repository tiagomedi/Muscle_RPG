"""Página 'Mi rutina' - muestra resumen de la rutina generada para el usuario."""
import streamlit as st
import json
from src.database.db_manager import DatabaseManager
from src.utils.session import check_login_state
from src import routine_builder


def _ensure_session_keys():
    if 'user_level_slider' not in st.session_state:
        st.session_state['user_level_slider'] = 0
    if 'show_level_quiz' not in st.session_state:
        st.session_state['show_level_quiz'] = False
    if 'profile_calculated' not in st.session_state:
        st.session_state['profile_calculated'] = False


def show_my_routine():
    st.title("Mi rutina")

    # Verificar inicio de sesión
    username = check_login_state()

    db = DatabaseManager()

    _ensure_session_keys()

    # Parámetros moved from Perfil -> aquí
    st.subheader("Parámetros")
    cols = st.columns([2, 1, 1])
    with cols[0]:
        days = st.selectbox("Días por semana", [3, 4, 5], index=1)
        st.markdown("**Tiempo por sesión:** 120 minutos (fijo)")
    with cols[1]:
        level = st.slider(
            "Nivel del usuario", min_value=0, max_value=1,
            value=st.session_state['user_level_slider'], key='user_level_slider'
        )
    with cols[2]:
        if st.button("¿Cuál es mi nivel? / No sé mi nivel"):
            st.session_state['show_level_quiz'] = True
            st.session_state['profile_calculated'] = False
            st.rerun()

    show_instructions = st.checkbox("Mostrar instrucciones de los ejercicios", value=True)
    generate = st.button("Generar rutina")

    # Generar rutina cuando el usuario pulsa el botón
    if generate:
        with st.spinner("Generando rutina..."):
            # usar nivel guardado en session state en caso de cambio
            user_level = st.session_state.get('user_level_slider', 0)
            routine = routine_builder.generate_routine(days, time_per_session=120, user_level=user_level)
            db.save_routine(username, routine)
        st.success("Rutina generada y guardada en tu perfil")
        # recargar la página para mostrar la nueva rutina
        st.rerun()

    # Nivel quiz (copiado de Perfil) - se muestra aquí cuando corresponde
    if st.session_state.get('show_level_quiz', False):
        st.markdown("### Perfil de entrenamiento")
        existing_profile = db.get_profile(username) or st.session_state.get('user_profile', {})
        with st.form("level_quiz_mi_rutina"):
            age = st.number_input("Edad (años)", min_value=13, max_value=100, value=existing_profile.get('age', 25), step=1)
            gender_options = ["No declarar", "Femenino", "Masculino", "Otro"]
            gender_default = gender_options.index(existing_profile.get('gender', "No declarar"))
            gender = st.selectbox("Género (opcional)", gender_options, index=gender_default)
            height_cm = st.number_input("Estatura (cm)", min_value=100, max_value=230, value=existing_profile.get('height_cm', 175), step=1)
            weight_kg = st.number_input("Peso actual (kg)", min_value=30.0, max_value=300.0, value=existing_profile.get('weight_kg', 75.0), step=0.5)
            env_options = ["Gimnasio", "En casa", "Híbrido"]
            env_default = env_options.index(existing_profile.get('environment', "Híbrido"))
            environment = st.selectbox("Entorno de entrenamiento", env_options, index=env_default)
            years = st.number_input("¿Cuánto tiempo llevas entrenando consistentemente? (años)", min_value=0.0, max_value=50.0, value=existing_profile.get('years', 1.0), step=0.5)
            sessions_options = ["1-2", "2-3", "3-4", "4-5", "5-6", "6-7"]
            sessions_default = sessions_options.index(existing_profile.get('sessions_per_week', "4-5"))
            sessions = st.selectbox("Sesiones por semana (rango)", sessions_options, index=sessions_default)
            submitted = st.form_submit_button("Calcular nivel recomendado")

        if submitted:
            user_profile = {
                'age': age,
                'gender': gender,
                'height_cm': height_cm,
                'weight_kg': weight_kg,
                'environment': environment,
                'years': years,
                'sessions_per_week': sessions,
            }
            st.session_state['user_profile'] = user_profile
            st.session_state['profile_calculated'] = True

            # Scoring heurístico (misma lógica que Perfil)
            if years < 0.5:
                years_score = 0
            elif years < 1.5:
                years_score = 1
            elif years < 3:
                years_score = 2
            else:
                years_score = 3

            sessions_map = {'1-2': 0, '2-3': 1, '3-4': 2, '4-5': 3, '5-6': 4, '6-7': 4}
            sess_score = sessions_map.get(sessions, 2)
            env_score = 1 if environment == 'Gimnasio' else 0

            total = years_score + sess_score + env_score
            max_possible = 8
            normalized = max(0, min(total, max_possible))
            recommended = 1 if normalized > (max_possible / 2) else 0
            st.session_state['recommended_level'] = recommended
            st.session_state['profile_scores'] = {
                'years_score': years_score,
                'sessions_score': sess_score,
                'environment_score': env_score,
                'total_raw': total,
                'recommended_level': recommended,
            }

            # Guardar perfil en la base de datos
            db.save_profile(username, user_profile)
            st.rerun()

        if st.session_state.get('profile_calculated', False):
            recommended = st.session_state['recommended_level']
            label = {0: 'Básico', 1: 'Intermedio'}[recommended]
            st.success(f"Nivel recomendado: {recommended} ({label})")
            with st.expander("Ver desglose de puntuación y perfil registrado"):
                st.write({'user_profile': st.session_state['user_profile'], 'scores': st.session_state['profile_scores']})
            col1a, col2a = st.columns([1, 2])
            with col1a:
                if st.button("Aplicar nivel recomendado", key='apply_level_mi_rutina'):
                    st.session_state['user_level_slider'] = recommended
                    st.session_state['show_level_quiz'] = False
                    st.rerun()
            with col2a:
                st.write("")

    routine = db.get_routine(username)
    if not routine:
        st.info("Aún no tienes una rutina guardada. Usa los parámetros arriba y pulsa 'Generar rutina'.")
        return

    schedule = routine.get('schedule', {})

    st.subheader("Resumen semanal")
    # Mostrar por cada día ordenado
    day_keys = [k for k in schedule.keys() if not k.endswith('_meta')]
    # ordenar por número de día si posible
    def day_sort_key(k):
        import re
        m = re.search(r"(\d+)", k)
        return int(m.group(1)) if m else k

    for day_key in sorted(day_keys, key=day_sort_key):
        meta = schedule.get(day_key + '_meta', {})
        st.markdown(f"### {day_key.replace('_', ' ').title()} — Tiempo total: {meta.get('total_time_min', 0)} min")
        items = schedule.get(day_key, [])
        if not items:
            st.write("(Sin ejercicios para este día)")
            continue

        for ex in items:
            # algunos generadores usan 'time_min' o 'time'
            time_min = ex.get('time_min') or ex.get('time') or ex.get('duration') or 0
            reps = ex.get('reps') or ex.get('target_reps') or 10
            sets = ex.get('sets') or 3
            name = ex.get('name') or ex.get('id')
            muscles = ex.get('muscles') or ex.get('targetMuscles') or []

            cols = st.columns([3, 1, 1, 2])
            with cols[0]:
                st.markdown(f"**{name}**")
                st.markdown(f"_Músculos:_ {', '.join(muscles)}")
            with cols[1]:
                st.markdown(f"**{sets}x**")
            with cols[2]:
                st.markdown(f"**{reps}** reps")
            with cols[3]:
                st.markdown(f"{time_min} min")

        st.write("---")

    # Resumen y descarga
    st.subheader("Exportar rutina")
    json_bytes = json.dumps(routine, ensure_ascii=False, indent=2).encode('utf-8')
    st.download_button(label="Descargar rutina (JSON)", data=json_bytes, file_name="my_routine.json", mime="application/json")


if __name__ == '__main__':
    show_my_routine()
