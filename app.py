import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
import time

# 1. INTERFAZ PROFESIONAL
st.set_page_config(page_title="Chefcito 👨‍🍳", page_icon="👨‍🍳")

st.markdown("""
    <style>
    .stChatMessage, p, li, div {
        font-size: 26px !important;
        line-height: 1.6 !important;
        color: #1A1A1A;
    }
    .recetario-chef {
        font-size: 26px !important;
        background-color: #FDFDFD;
        padding: 25px;
        border-radius: 12px;
        border: 2px solid #D0021B;
        margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Chefcito")

# 2. CONOCIMIENTO TÉCNICO
@st.cache_resource
def cargar_biblioteca():
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

biblioteca = cargar_biblioteca()

# 3. MOTOR DE INTELIGENCIA (Configuración Directa)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Error: Falta la API Key en los Secrets.")
    st.stop()

# Instrucción de Sistema: Profesional y Rigurosa
instrucciones_chef = (
    f"Eres 'Chefcito', experto culinario con 15 años de trayectoria. Trato formal, respetuoso y profesional. "
    f"PROHIBIDO el uso de lenguaje afectivo (mi vida, mi cielo, corazón, etc.). "
    f"Normas:\n"
    f"1. GRAMÁTICA: Uso estricto de Mayúsculas al iniciar cada oración y después de puntos.\n"
    f"2. COMENSALES: Si el usuario no indica para cuántos cocinará, debe solicitar la cantidad antes de dar la receta.\n"
    f"3. BASE TÉCNICA: Utilice este contexto: {biblioteca}. Complemente con conocimientos actuales.\n"
    f"4. FORMATO: Nombre, Valor Nutritivo, Regla 50/25/25, Paso a Paso, Residuo Cero, Plus y Toque Maestro.\n"
    f"5. FINALIZACIÓN: Siempre pregunte si requiere asistencia con otro platillo."
)

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=instrucciones_chef
)

# 4. GESTIÓN DE SESIÓN NATIVA
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])
    st.session_state.messages = []
    bienvenida = "¡Hola! Soy Chefcito. 👨‍🍳✨ Es un gusto saludarle. Por favor, indique desde qué lugar nos escribe y qué desea cocinar hoy."
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# 5. FLUJO DE DIÁLOGO
if prompt := st.chat_input("Escriba su consulta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Respuesta fluida como en AI Studio
            response = st.session_state.chat_session.send_message(prompt, stream=True)
            
            def stream_text():
                for chunk in response:
                    if chunk.text:
                        for word in chunk.text.split(" "):
                            yield word + " "
                            time.sleep(0.03)

            full_text = st.write_stream(stream_text())
            
            if "Paso a Paso" in full_text:
                output = f'<div class="recetario-chef">{full_text}</div>'
            else:
                output = full_text
                
            st.session_state.messages.append({"role": "assistant", "content": output})
            
        except Exception as e:
            st.error(f"Se produjo un inconveniente técnico. Detalles: {e}")
