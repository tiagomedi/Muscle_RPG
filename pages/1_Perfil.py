"""Página de perfil y generación de rutina."""
import streamlit as st
import json
from src import routine_builder
from src.database.db_manager import DatabaseManager
from src.utils.session import check_login_state

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
    
    # Descripción del proyecto
    with st.expander("Acerca del proyecto", expanded=False):
        st.markdown(
            """
            **Resumen del proyecto**

            La planificación de rutinas de entrenamiento suele ser genérica y poco adaptable al progreso
            individual del usuario, lo que limita la eficiencia de los resultados. Este proyecto propone
            modelar los ejercicios de hipertrofia muscular y su progresión mediante un grafo que representa
            posibles caminos de entrenamiento, permitiendo identificar rutas que maximicen las ganancias
            musculares de forma progresiva y estructurada.

            Este trabajo se centra exclusivamente en la hipertrofia, buscando el aumento del tamaño muscular
            a través de una planificación inteligente del volumen, intensidad y frecuencia de entrenamiento.
            """
        )

    # Parámetros de la rutina
    with st.sidebar:
        st.header("Parámetros")
        days = st.selectbox("Días por semana", [3, 4, 5], index=1)
        time_per_session = 120  # Fijo en 2 horas
        st.markdown("**Tiempo por sesión:** 120 minutos (fijo)")
        
        level = st.slider(
            "Nivel del usuario", 
            min_value=0, 
            max_value=1, 
            value=st.session_state['user_level_slider'], 
            key='user_level_slider', 
            help="0 = Básico, 1 = Intermedio"
        )
        
        if st.button("¿Cuál es mi nivel? / No sé mi nivel"):
            st.session_state['show_level_quiz'] = True
            st.session_state['profile_calculated'] = False
            st.rerun()
        
        show_instructions = st.checkbox("Mostrar instrucciones de los ejercicios", value=True)
        generate = st.button("Generar rutina")

    # Formulario de perfil/nivel
    if st.session_state.get('show_level_quiz', False):
        st.markdown("### Perfil de entrenamiento")
        with st.form("level_quiz"):
            # Perfil general (constantes y variables)
            age = st.number_input("Edad (años)", min_value=13, max_value=100, value=25, step=1)
            gender = st.selectbox("Género (opcional)", ["No declarar", "Femenino", "Masculino", "Otro"], index=0)
            height_cm = st.number_input("Estatura (cm)", min_value=100, max_value=230, value=175, step=1)
            weight_kg = st.number_input("Peso actual (kg)", min_value=30.0, max_value=300.0, value=75.0, step=0.5)
            environment = st.selectbox("Entorno de entrenamiento", ["Gimnasio", "En casa", "Híbrido"], index=2)
            
            # Variables de entrenamiento
            years = st.number_input("¿Cuánto tiempo llevas entrenando consistentemente? (años)", 
                                  min_value=0.0, max_value=50.0, value=1.0, step=0.5)
            sessions = st.selectbox("Sesiones por semana (rango)", 
                                  ["1-2", "2-3", "3-4", "4-5", "5-6", "6-7"], index=3)
            
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

    # Generación y visualización de rutina
    if generate:
        with st.spinner("Generando rutina..."):
            routine = routine_builder.generate_routine(
                days, time_per_session=time_per_session, user_level=level)
            exercises = routine_builder.load_exercises()

        st.success("Rutina generada")
        
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
                            st.image(ex_raw.get("gifUrl"), use_column_width=True)
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