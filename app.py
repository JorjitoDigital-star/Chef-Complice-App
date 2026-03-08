import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Diagnóstico Chef", page_icon="👨‍🍳")
st.title("👨‍🍳 Diagnóstico del Chef")

# 1. Verificar la Llave
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("❌ No encontré la llave en Secrets.")
    st.stop()

try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # 2. Intentamos listar los modelos disponibles para tu cuenta
    st.write("Buscando modelos compatibles...")
    modelos = [m.name for m in genai.list_models()]
    st.success(f"¡Conexión exitosa! Modelos encontrados: {modelos}")
    
    # 3. Usamos el primero que funcione de la lista oficial
    # Si 'gemini-1.5-flash' no está, usará 'gemini-pro'
    nombre_modelo = 'gemini-1.5-flash' if 'models/gemini-1.5-flash' in modelos else 'gemini-pro'
    
    st.info(f"Usando modelo: {nombre_modelo}")
    model = genai.GenerativeModel(nombre_modelo)
    
    # Prueba rápida de respuesta
    response = model.generate_content("Hola, ¿estás listo?")
    st.write("Respuesta de prueba:", response.text)

except Exception as e:
    st.error(f"Error técnico real: {e}")
    st.warning("Si el error persiste, intenta generar una API KEY NUEVA en Google AI Studio.")
