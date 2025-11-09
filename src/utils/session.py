"""Utilidades para manejo de sesión."""
import streamlit as st

def check_login_state():
    """Verifica el estado de la sesión y retorna al inicio si no hay sesión."""
    if not st.session_state.get('logged_in', False):
        st.warning("⚠️ Debes iniciar sesión primero")
        st.markdown("[Ir a inicio](/) para iniciar sesión")
        st.stop()
    return st.session_state.get('username')