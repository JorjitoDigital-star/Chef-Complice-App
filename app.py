import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os

# 1. Configuración visual
st.set_page_config(page_title="Chef Cómplice 👨‍🍳", page_icon="👨‍🍳")
st.title("👨‍🍳 Chef Cómplice")
st.markdown("---")

# 2. LEER TODOS LOS PDFS (Con límite de seguridad)
@st.cache_resource
def get_all_pdfs_text():
    full_text = ""
    files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    for file in files:
        try:
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
        except Exception as e:
            st.warning(f"No pude leer el archivo {file}: {e}")
    # Limitamos a 500k caracteres para no saturar el modelo gratuito
    return full_text[:500000] 

contexto_biblioteca = get_all_pdfs_text()

# 3. Configurar Gemini con el nombre de modelo correcto
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la configuración de la API Key en Secrets.")

# Cambiamos el nombre del modelo a la ruta completa por seguridad
model = genai.GenerativeModel('models/gemini-1.5-flash')

# 4. Lógica del Chat
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "¡Hola! Soy tu Chef Cómplice! 👨‍🍳 Tengo mis 6 libros listos. Dime de dónde me escribes y qué tienes en la refri."})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Escribe tus ingredientes aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Enviamos el contexto de forma separada para mayor claridad
            instrucciones = f"Eres el Chef Cómplice. Usa este conocimiento: {contexto_biblioteca}"
            # Llamada al modelo con manejo de errores
            response = model.generate_content([instrucciones, prompt])
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Hubo un error al generar la respuesta: {e}")
