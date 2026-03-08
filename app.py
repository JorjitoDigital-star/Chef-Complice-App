import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os

# 1. Configuración visual
st.set_page_config(page_title="Chef Cómplice 👨‍🍳", page_icon="👨‍🍳")
st.title("👨‍🍳 Chef Cómplice")
st.markdown("---")

# 2. LEER TODOS LOS PDFS EN LA CARPETA
@st.cache_resource
def get_all_pdfs_text():
    full_text = ""
    # Busca todos los archivos que terminen en .pdf
    files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    for file in files:
        try:
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                full_text += page.extract_text()
        except:
            continue # Si un PDF da error, pasa al siguiente
    return full_text

contexto_biblioteca = get_all_pdfs_text()

# 3. Configurar Gemini
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la configuración de la API Key en Secrets.")

model = genai.GenerativeModel('gemini-1.5-flash')

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
        # Ahora el Chef usa TODA la biblioteca de PDFs
        instrucciones_chef = f"Eres el Chef Cómplice. Usa este conocimiento de mis 6 PDFs: {contexto_biblioteca}. Responde de forma creativa, breve y entusiasta."
        response = model.generate_content([instrucciones_chef, prompt])
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
