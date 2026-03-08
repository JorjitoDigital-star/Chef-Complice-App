import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
import time

# 1. ESTILO
st.set_page_config(page_title="Chefcito 👨‍🍳", page_icon="👨‍🍳")
st.markdown("<style>.stChatMessage, p, li, div { font-size: 26px !important; }</style>", unsafe_allow_html=True)
st.title("👨‍🍳 Chefcito")

# 2. CARGA LIGERA (Solo 10 páginas para asegurar velocidad)
@st.cache_resource
def cargar_datos():
    texto = ""
    archivos = [f for f in os.listdir('.') if f.endswith('.pdf')]
    for arc in archivos:
        try:
            lector = PdfReader(arc)
            for pag in lector.pages[:10]:
                ext = pag.extract_text()
                if ext: texto += ext + "\n"
        except: continue
    return texto[:20000]

conocimiento = cargar_datos()

# 3. CONFIGURACIÓN
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Error: Falta la API Key.")
    st.stop()

# Instrucción profesional
instruccion_maestra = (
    f"Eres 'Chefcito', experto con 15 años de experiencia. Trato profesional y respetuoso. "
    f"PROHIBIDO usar palabras cursis. Mayúsculas correctas. "
    f"Pregunta siempre cuántos comensales son. Usa esta base: {conocimiento}."
)

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=instruccion_maestra
)

# 4. SESIÓN
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "¡Hola! Soy Chefcito. 👨‍🍳✨ ¿Desde dónde nos escribe y qué desea cocinar?"})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# 5. EJECUCIÓN CON DIAGNÓSTICO
if prompt := st.chat_input("Escriba aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = st.session_state.chat.send_message(prompt, stream=True)
            
            def stream_handler():
                for chunk in response:
                    if chunk.text:
                        for word in chunk.text.split(" "):
                            yield word + " "
                            time.sleep(0.02)

            full_text = st.write_stream(stream_handler())
            st.session_state.messages.append({"role": "assistant", "content": full_text})
            
        except Exception as e:
            # ESTA LÍNEA NOS DIRÁ LA VERDAD:
            st.error(f"Error detectado: {e}")
            if "403" in str(e) or "location" in str(e).lower():
                st.warning("⚠️ Parece que hay una restricción regional. Si está en Cuba, la API de Google podría estar bloqueada.")
