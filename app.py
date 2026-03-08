import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
import time

st.set_page_config(page_title="Chef Cómplice 👨‍🍳", page_icon="👨‍🍳")
st.title("👨‍🍳 Chef Cómplice")
st.markdown("---")

@st.cache_resource
def cargar_biblioteca():
    texto_total = ""
    archivos_pdf = [f for f in os.listdir('.') if f.endswith('.pdf')]
    for archivo in archivos_pdf:
        try:
            lector = PdfReader(archivo)
            for pagina in lector.pages:
                extraido = pagina.extract_text()
                if extraido:
                    texto_total += extraido + "\n"
        except:
            continue
    # REDUCIMOS EL LÍMITE AQUÍ PARA EVITAR EL ERROR 429
    return texto_total[:100000] 

conocimiento_chef = cargar_biblioteca()

if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la API Key en Secrets.")
    st.stop()

# Usamos el modelo que tu diagnóstico confirmó
model = genai.GenerativeModel('models/gemini-flash-latest')

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "¡Hola! Soy tu Chef Cómplice! 👨‍🍳 Mis libros están listos. ¿Qué cocinamos hoy?"})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Escribe tus ingredientes..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            instrucciones = f"Eres el Chef Cómplice. Usa este conocimiento de mis PDFs: {conocimiento_chef}. Sé breve."
            response = model.generate_content([instrucciones, prompt])
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            if "429" in str(e):
                st.warning("⚠️ ¡El Chef está muy ocupado! Por favor, espera 10 segundos y vuelve a intentar.")
            else:
                st.error(f"Error en la cocina: {e}")
