"""Página de seguimiento diario."""
import streamlit as st
from datetime import datetime, timedelta
from src.database.db_manager import DatabaseManager
from src.utils.session import check_login_state

def get_day_exercises(db: DatabaseManager, username: str, day_index: int):
    """Obtiene los ejercicios del día desde la rutina guardada."""
    return db.get_current_day_exercises(username, day_index)

def show_tracking_page():
    """Muestra la página de seguimiento diario."""
    st.title("Seguimiento Diario")
    
    # Verificar inicio de sesión
    username = check_login_state()
    
    db = DatabaseManager()
    
    # Selector de día (invertido para mostrar más reciente primero)
    today = datetime.now()
    days = []
    for i in range(7):
        date = today - timedelta(days=i)
        days.append({
            'index': i,
            'date': date,
            'label': date.strftime('%d-%m-%Y')
        })
    
    selected_day = st.selectbox(
        "Seleccionar día",
        options=days,
        format_func=lambda x: x['label'],
        index=0,
        help="0 = Hoy, 1 = Ayer, etc."
    )
    
    st.write(f"📅 Fecha seleccionada: {selected_day['label']}")
    
    # Obtener ejercicios del día
    exercises = get_day_exercises(db, username, selected_day['index'])
    
    if not exercises:
        st.warning("⚠️ No hay una rutina guardada para este día. Por favor, genera primero una rutina en la sección de Perfil.")
        return
    
    # Formulario de seguimiento
    with st.form(key=f"tracking_form_{selected_day['index']}"):
        st.subheader("📝 Registro de entrenamiento")
        
        # Duración total
        duration = st.slider(
            "⌚ Duración total del entrenamiento (minutos)",
            30, 180, 120, step=5,
            help="Tiempo total de la sesión, incluyendo descansos"
        )
        
        # Estado general
        energy = st.select_slider(
            "🔋 Nivel de energía",
            options=["Muy bajo", "Bajo", "Normal", "Alto", "Muy alto"],
            value="Normal",
            help="¿Cómo te sentiste durante el entrenamiento?"
        )
        
        # Seguimiento por ejercicio
        st.subheader("💪 Ejercicios completados")
        exercise_tracking = {}
        
        for i, ex in enumerate(exercises):
            st.markdown(f"#### {ex['name']}")
            cols = st.columns([1, 1, 1])
            
            with cols[0]:
                completed_sets = st.number_input(
                    f"Sets completados (de {ex['sets']})",
                    0, ex['sets'], ex['sets'],
                    key=f"sets_{selected_day['index']}_{i}"
                )
            
            with cols[1]:
                avg_reps = st.number_input(
                    f"Reps promedio (objetivo: {ex['reps']})",
                    0, ex['reps'] * 2, ex['reps'],
                    key=f"reps_{selected_day['index']}_{i}"
                )
            
            with cols[2]:
                difficulty = st.select_slider(
                    "Dificultad percibida",
                    options=["Muy fácil", "Fácil", "Moderado", "Difícil", "Muy difícil"],
                    value="Moderado",
                    key=f"diff_{selected_day['index']}_{i}"
                )
            
            exercise_tracking[ex['name']] = {
                'sets_completed': completed_sets,
                'avg_reps': avg_reps,
                'difficulty': difficulty,
                'target_sets': ex['sets'],
                'target_reps': ex['reps']
            }
        
        # Notas adicionales
        notes = st.text_area(
            "📝 Notas adicionales (opcional)",
            placeholder="Escribe aquí cualquier observación...",
            key=f"notes_{selected_day['index']}"
        )
        
        # Botón de submit
        submitted = st.form_submit_button("💾 Guardar seguimiento")
        
        if submitted:
            tracking_data = {
                'date': selected_day['date'].isoformat(),
                'duration': duration,
                'energy_level': energy,
                'exercises': exercise_tracking,
                'notes': notes,
            }
            
            if db.save_tracking(username, selected_day['index'], tracking_data):
                st.success("✅ Seguimiento guardado exitosamente")
                
                # Mostrar resumen
                st.subheader("📊 Resumen del entrenamiento")
                cols = st.columns(2)
                
                with cols[0]:
                    completion_rate = sum(ex['sets_completed'] for ex in exercise_tracking.values()) / \
                                    sum(ex['target_sets'] for ex in exercise_tracking.values()) * 100
                    
                    st.metric(
                        "Completado",
                        f"{completion_rate:.1f}%",
                        help="Porcentaje de sets completados vs programados"
                    )
                
                with cols[1]:
                    st.metric(
                        "Duración",
                        f"{duration} min",
                        delta=f"{duration - 120} min" if duration != 120 else None,
                        help="Duración vs tiempo programado (120 min)"
                    )
                
                st.caption(f"Nivel de energía: {energy}")
                if notes:
                    st.caption(f"Notas: {notes}")

if __name__ == "__main__":
    show_tracking_page()