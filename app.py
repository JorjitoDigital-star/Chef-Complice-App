import streamlit as st
import google.generativeai as genai
import os

# CONFIGURACIÓN BÁSICA
st.set_page_config(page_title="Chefcito 👨‍🍳")
st.title("👨‍🍳 Chefcito")

# 1. CONEXIÓN SEGURA
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la API Key en Secrets.")
    st.stop()

# 2. INICIALIZACIÓN DEL MODELO
# Usamos el nombre más genérico para evitar el 404
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Error al cargar el modelo: {e}")

# 3. CHAT SIMPLIFICADO
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "¡Hola! Soy Chefcito. 👨‍🍳 ¿Qué vamos a cocinar hoy?"})

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Instrucciones directas
    contexto = "Actúa como Chefcito, experto culinario profesional. Usa gramática perfecta y no seas cursi. Responde: "
    
    try:
        response = model.generate_content(contexto + prompt)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.chat_message("assistant").write(response.text)
    except Exception as e:
        st.error(f"Fallo en la respuesta: {e}")
