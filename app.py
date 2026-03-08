import streamlit as st
import google.generativeai as genai

st.title("Prueba de Conexión Final")
api_key = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

if st.button("Probar Conexión"):
    try:
        # La forma más básica de llamar al modelo
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hola")
        st.success(f"¡CONECTADO! Respuesta: {response.text}")
    except Exception as e:
        st.error(f"FALLO CRÍTICO: {e}")
