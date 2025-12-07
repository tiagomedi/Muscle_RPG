"""Página de perfil y generación de rutina."""
import streamlit as st
import json
from src import routine_builder
from src.database.db_manager import DatabaseManager
from src.session.session import check_login_state

def init_session_state():
    """Inicializa variables de sesión específicas del perfil."""
    if 'user_level_slider' not in st.session_state:
        st.session_state['user_level_slider'] = 0
    if 'show_level_quiz' not in st.session_state:
        st.session_state['show_level_quiz'] = False
    if 'profile_calculated' not in st.session_state:
        st.session_state['profile_calculated'] = False

def show_profile_page():
    """Muestra la página de perfil y generación de rutina."""
    st.title("Perfil y Generación de Rutina")
    
    # Verificar inicio de sesión
    username = check_login_state()
    
    init_session_state()
    db = DatabaseManager()
    
    # Cargar perfil existente si existe
    user_profile = db.get_profile(username)
    if user_profile and not st.session_state.get('show_level_quiz', False):
        st.session_state['user_profile'] = user_profile
        
        # Mostrar datos actuales del perfil
        with st.expander("👤 Tu perfil actual", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Datos básicos:**")
                st.write(f"- Edad: {user_profile['age']} años")
                st.write(f"- Género: {user_profile['gender']}")
                st.write(f"- Estatura: {user_profile['height_cm']} cm")
                st.write(f"- Peso: {user_profile['weight_kg']} kg")
            with col2:
                st.write("**Datos de entrenamiento:**")
                st.write(f"- Experiencia: {user_profile['years']} años")
                st.write(f"- Sesiones/semana: {user_profile['sessions_per_week']}")
                st.write(f"- Entorno: {user_profile['environment']}")
            
            if st.button("🔄 Actualizar mi perfil"):
                st.session_state['show_level_quiz'] = True
                st.rerun()

    # Formulario de perfil/nivel
    if st.session_state.get('show_level_quiz', False):
        st.markdown("### Perfil de entrenamiento")
        existing_profile = st.session_state.get('user_profile', {})
        with st.form("level_quiz"):
            # Perfil general (constantes y variables)
            age = st.number_input("Edad (años)", 
                                min_value=13, 
                                max_value=100, 
                                value=existing_profile.get('age', 25), 
                                step=1)
            
            gender_options = ["No declarar", "Femenino", "Masculino", "Otro"]
            gender_default = gender_options.index(existing_profile.get('gender', "No declarar"))
            gender = st.selectbox("Género (opcional)", 
                                gender_options, 
                                index=gender_default)
            
            height_cm = st.number_input("Estatura (cm)", 
                                      min_value=100, 
                                      max_value=230, 
                                      value=existing_profile.get('height_cm', 175), 
                                      step=1)
            
            weight_kg = st.number_input("Peso actual (kg)", 
                                      min_value=30.0, 
                                      max_value=300.0, 
                                      value=existing_profile.get('weight_kg', 75.0), 
                                      step=0.5)
            
            env_options = ["Gimnasio", "En casa", "Híbrido"]
            env_default = env_options.index(existing_profile.get('environment', "Híbrido"))
            environment = st.selectbox("Entorno de entrenamiento", 
                                    env_options, 
                                    index=env_default)
            
            # Variables de entrenamiento
            years = st.number_input("¿Cuánto tiempo llevas entrenando consistentemente? (años)", 
                                  min_value=0.0, 
                                  max_value=50.0, 
                                  value=existing_profile.get('years', 1.0), 
                                  step=0.5)
            
            sessions_options = ["1-2", "2-3", "3-4", "4-5", "5-6", "6-7"]
            sessions_default = sessions_options.index(existing_profile.get('sessions_per_week', "4-5"))
            sessions = st.selectbox("Sesiones por semana (rango)", 
                                  sessions_options, 
                                  index=sessions_default)
            
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

            # Scoring heurístico
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

        # Mostrar resultados y botón de aplicar fuera del formulario
        if st.session_state.get('profile_calculated', False):
            recommended = st.session_state['recommended_level']
            label = {0: 'Básico', 1: 'Intermedio'}[recommended]
            st.success(f"Nivel recomendado: {recommended} ({label})")
            
            with st.expander("Ver desglose de puntuación y perfil registrado"):
                st.write({
                    'user_profile': st.session_state['user_profile'], 
                    'scores': st.session_state['profile_scores']
                })
            
            col1, col2 = st.columns([1, 2])
            with col1:
                if st.button("Aplicar nivel recomendado", key='apply_level'):
                    st.session_state['user_level_slider'] = recommended
                    st.session_state['show_level_quiz'] = False
                    st.rerun()

    # Mostrar rutina guardada (si existe)
    routine = db.get_routine(username)
    if not routine:
        st.info("No tienes una rutina guardada. Ve a 'Mi rutina' para generar una.")
    else:
        exercises = routine_builder.load_exercises()
        show_instructions = st.checkbox("Mostrar instrucciones de los ejercicios", value=True)

        # Mostrar rutina
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
                    ex_raw = next((e for e in exercises if e.get("exerciseId") == ex.get("id")), None)
                    cols = st.columns([1, 4])
                    with cols[0]:
                        if ex_raw and ex_raw.get("gifUrl"):
                            st.image(ex_raw.get("gifUrl"), use_container_width=True)
                        else:
                            st.write("")
                    with cols[1]:
                        st.markdown(f"**{ex.get('name')}** — {ex.get('sets')}x{ex.get('reps')} reps — {ex.get('time_min')} min")
                        st.markdown(f"_Músculos:_ {', '.join(ex.get('muscles', []))}")
                        if show_instructions and ex_raw:
                            instr = ex_raw.get("instructions") or []
                            if instr:
                                with st.expander("Ver instrucciones"):
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
            st.download_button(
                label="Descargar rutina (JSON)", 
                data=json_bytes, 
                file_name="routine.json", 
                mime="application/json"
            )

if __name__ == "__main__":
    show_profile_page()