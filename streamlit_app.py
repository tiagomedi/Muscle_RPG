import streamlit as st
from src.database.db_manager import DatabaseManager

def init_session_state():
    """Inicializa variables de sesión."""
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = None

def main():
    st.set_page_config(
        page_title="Muscle RPG",
        page_icon="💪",
        layout="centered",
        initial_sidebar_state="auto",
    )

    # Mostrar estado de sesión en la barra lateral
    with st.sidebar:
        if st.session_state.get('logged_in', False):
            st.markdown(f"👤 **{st.session_state['username']}**")
            if st.button("🚪 Cerrar sesión", key='sidebar_logout'):
                st.session_state['logged_in'] = False
                st.session_state['username'] = None
                st.rerun()
        else:
            st.info("No has iniciado sesión")

    st.title("Muscle RPG")
    st.caption("Tu entrenador personal gamificado")
    
    init_session_state()
    db = DatabaseManager()
    
    if st.session_state['logged_in']:
        st.success(f"¡Bienvenido, {st.session_state['username']}! 🎉")
        st.markdown("""
        👈 **Usa el menú lateral para navegar entre secciones:**
        
        1. **Perfil**: 
           - Configura tu nivel
           - Genera tu rutina personalizada
           - Actualiza tus preferencias
        
        2. **Seguimiento**: 
           - Registra tu progreso diario
           - Marca ejercicios completados
           - Anota tu rendimiento
           
        ¡Comienza tu viaje de transformación! 💪
        """)
        return

    tab1, tab2 = st.tabs(["Iniciar sesión", "Registrarse"])
    
    with tab1:
        with st.form("login_form"):
            st.subheader("🔑 Iniciar sesión")
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Iniciar sesión")
            
            if submit:
                if db.validate_login(username, password):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.balloons()
                    st.success("¡Inicio de sesión exitoso!")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
    
    with tab2:
        with st.form("register_form"):
            st.subheader("📝 Registro nuevo")
            new_username = st.text_input("Usuario nuevo")
            new_password = st.text_input("Contraseña nueva", type="password")
            confirm_password = st.text_input("Confirmar contraseña", type="password")
            submit = st.form_submit_button("Registrarse")
            
            if submit:
                if not new_username or not new_password:
                    st.error("❌ Por favor completa todos los campos")
                elif new_password != confirm_password:
                    st.error("❌ Las contraseñas no coinciden")
                else:
                    if db.register_user(new_username, new_password):
                        st.success("✅ ¡Registro exitoso! Ahora puedes iniciar sesión")
                    else:
                        st.error("❌ El usuario ya existe")

    st.markdown("---")
    with st.expander("ℹ️ Acerca del proyecto"):
        st.markdown(
            """
            **Muscle RPG** es un sistema de entrenamiento gamificado que adapta tus rutinas según tu progreso.
            
            ### Características principales:

            🎯 **Enfoque en hipertrofia**
            - Optimizado para el crecimiento muscular
            - Planificación inteligente de volumen e intensidad
            
            🎮 **Sistema de niveles**
            - Progresión similar a un videojuego RPG
            - Dos niveles de experiencia: Básico e Intermedio
            
            📊 **Seguimiento detallado**
            - Registra tu progreso día a día
            - Analiza tu rendimiento por ejercicio
            
            🔄 **Ciclos trimestrales**
            - Actualización de rutinas cada 3 meses
            - Evaluación continua de progreso
            
            ⌚ **Sesiones de 2 horas**
            - Diseñado para entrenamientos completos
            - Estructura optimizada
            
            ### Para comenzar:
            1. 📝 Regístrate o inicia sesión
            2. 👤 Completa tu perfil
            3. 💪 Genera tu rutina personalizada
            4. ✅ ¡Comienza a entrenar y registra tu progreso!
            """
        )

if __name__ == "__main__":
    main()