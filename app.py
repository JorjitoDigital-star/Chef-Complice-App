import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os

# 1. Configuración de Estilo y Letras Grandes
st.set_page_config(page_title="Chef-cito 👨‍🍳", page_icon="👨‍🍳")

# Código para agrandar la letra de los mensajes y del chat
st.markdown("""
    <style>
    .stChatMessage {
        font-size: 22px !important;
    }
    .stChatInput textarea {
        font-size: 22px !important;
    }
    p {
        font-size: 22px !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Chef-cito")
st.markdown("---")

# 2. Carga silenciosa de los libros
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
    return texto_total[:120000]

conocimiento_chef = cargar_biblioteca()

# 3. Conexión con Gemini
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la llave secreta.")
    st.stop()

model = genai.GenerativeModel('models/gemini-flash-latest')

# 4. Diálogo de Chef-cito
if "messages" not in st.session_state:
    st.session_state.messages = []
    saludo = (
        "¡Hola! Soy Chef-cito. 👨‍🍳✨\n\n"
        "* ¿De dónde me escribes?\n"
        "* ¿Cuántas personas van a comer?\n"
        "* ¿Qué tienes en tu cocina?"
    )
    st.session_state.messages.append({"role": "assistant", "content": saludo})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Respuesta Sencilla y Breve
if prompt := st.chat_input("Escribe aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Instrucciones para que sea breve y no mencione PDFs
            system_instruction = (
                f"Eres 'Chef-cito'. Hablas con personas mayores de forma dulce, breve y simple. "
                f"Usa viñetas para que se lea fácil. "
                f"Usa este conocimiento pero NO digas que lo sacaste de un PDF o libro: {conocimiento_chef}. "
                f"Responde máximo en dos párrafos cortos."
            )
            
            response = model.generate_content([system_instruction, prompt])
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error("¡Ay! Algo pasó en la cocina. Intenta de nuevo.")
