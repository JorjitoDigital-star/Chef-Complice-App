import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os

# 1. Configuración de la interfaz
st.set_page_config(page_title="Chef Cómplice 👨‍🍳", page_icon="👨‍🍳")
st.title("👨‍🍳 Chef Cómplice")
st.markdown("---")

# 2. Cargar Biblioteca de PDFs
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
    return texto_total[:500000] 

conocimiento_chef = cargar_biblioteca()

# 3. Configurar Gemini con el nombre exacto de tu lista
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la API Key en Secrets.")
    st.stop()

# USAMOS EL NOMBRE EXACTO DE TU LISTA:
model = genai.GenerativeModel('models/gemini-flash-latest')

# 4. Historial del Chat
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "¡Hola! Soy tu Chef Cómplice! 👨‍🍳 Mis 6 libros están listos. ¿Qué cocinamos hoy?"})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Interacción
if prompt := st.chat_input("Escribe tus ingredientes..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Instrucción maestra
            instrucciones = f"Eres el Chef Cómplice. Usa este conocimiento de mis PDFs: {conocimiento_chef}. Sé entusiasta y breve."
            
            # Generar respuesta
            response = model.generate_content([instrucciones, prompt])
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Error en la cocina: {e}")
