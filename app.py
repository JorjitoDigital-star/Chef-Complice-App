import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader

# 1. Configuración visual de la App
st.set_page_config(page_title="Chef Cómplice 👨‍🍳", page_icon="👨‍🍳")
st.title("👨‍🍳 Chef Cómplice")
st.markdown("---")

# 2. Leer el PDF de comida peruana
@st.cache_resource
def get_pdf_text():
    pdf_reader = PdfReader("comida peruana_compressed.pdf")
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

contexto_pdf = get_pdf_text()

# 3. Configurar Gemini (Usaremos la llave de forma segura luego)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la configuración de la API Key.")

model = genai.GenerativeModel('gemini-1.5-flash')

# 4. Lógica del Chat
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Mensaje de bienvenida del Chef
    st.session_state.messages.append({"role": "assistant", "content": "¡Hola! Soy tu Chef Cómplice! 👨‍🍳 Sea que tengas mucho o solo dos cositas, ¡aquí hacemos magia! ✨ Dime de dónde me escribes, cuántos son y qué ingredientes tienes."})

# Mostrar historial
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada del usuario
if prompt := st.chat_input("Escribe tus ingredientes aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Respuesta de la IA con el contexto del PDF
    with st.chat_message("assistant"):
        instrucciones_chef = f"Eres el Chef Cómplice. Usa este conocimiento: {contexto_pdf}. Responde de forma creativa, breve y entusiasta."
        response = model.generate_content([instrucciones_chef, prompt])
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
