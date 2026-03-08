import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os

st.set_page_config(page_title="Chef Cómplice 👨‍🍳", page_icon="👨‍🍳")
st.title("👨‍🍳 Chef Cómplice")
st.markdown("---")

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
        except:
            continue
    return full_text[:500000] 

contexto_biblioteca = get_all_pdfs_text()

if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la configuración de la API Key en Secrets.")

# NOMBRE CORREGIDO AQUÍ:
model = genai.GenerativeModel('gemini-1.5-flash')

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
            instrucciones = f"Eres el Chef Cómplice. Usa este conocimiento: {contexto_biblioteca}"
            response = model.generate_content([instrucciones, prompt])
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"Hubo un error: {e}")
