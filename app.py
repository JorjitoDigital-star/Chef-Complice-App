import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
import time

# 1. ESTILO PROFESIONAL
st.set_page_config(page_title="Chefcito 👨‍🍳", page_icon="👨‍🍳")
st.markdown("<style>.stChatMessage, p, li, div { font-size: 26px !important; line-height: 1.6; }</style>", unsafe_allow_html=True)
st.title("👨‍🍳 Chefcito")

# 2. CARGA DE DATOS
@st.cache_resource
def cargar_datos():
    texto = ""
    archivos = [f for f in os.listdir('.') if f.endswith('.pdf')]
    for arc in archivos:
        try:
            lector = PdfReader(arc)
            for pag in lector.pages[:15]:
                ext = pag.extract_text()
                if ext: texto += ext + "\n"
        except: continue
    return texto[:30000]

conocimiento = cargar_datos()

# 3. CONFIGURACIÓN DEL MOTOR
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la API Key en los Secrets.")
    st.stop()

# Instrucción Maestra (Sin cursilerías)
instruccion_maestra = (
    f"Eres 'Chefcito', experto culinario con 15 años de experiencia. Trato profesional y respetuoso. "
    f"PROHIBIDO usar palabras como 'mi vida', 'mi cielo' o 'corazón'. "
    f"Reglas: 1. Mayúsculas siempre al iniciar oraciones y después de punto. "
    f"2. Pregunta siempre cuántos comensales son. 3. Usa esta base: {conocimiento}. "
    f"4. Formato: Nombre, Valor Nutritivo, Regla 50/25/25, Paso a Paso, Residuo Cero, Plus y Toque Maestro. "
    f"5. Termina siempre preguntando si desean preparar algo más."
)

# CAMBIO CLAVE: Nombre de modelo estándar
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=instruccion_maestra
)

# 4. SESIÓN DE CHAT
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "¡Hola! Soy Chefcito. 👨‍🍳✨ Es un gusto saludarle. ¿Desde dónde nos escribe y qué desea cocinar hoy?"})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# 5. EJECUCIÓN
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
                            time.sleep(0.03)

            full_text = st.write_stream(stream_handler())
            st.session_state.messages.append({"role": "assistant", "content": full_text})
            
        except Exception as e:
            # Diagnóstico detallado por si acaso
            st.error(f"Error de comunicación: {e}")
