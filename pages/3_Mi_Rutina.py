"""Página 'Mi rutina' - muestra resumen de la rutina generada para el usuario."""
import streamlit as st
import json
from src.database.db_manager import DatabaseManager
from src.utils.session import check_login_state


def show_my_routine():
    st.title("Mi rutina")

    # Verificar inicio de sesión
    username = check_login_state()

    db = DatabaseManager()

    routine = db.get_routine(username)
    if not routine:
        st.info("Aún no tienes una rutina guardada. Ve a la sección 'Perfil' y genera una rutina.")
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
