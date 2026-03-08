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

# 2. PROCESAMIENTO DE CONOCIMIENTO
@st.cache_resource
def cargar_conocimiento():
    texto = ""
    archivos = [f for f in os.listdir('.') if f.endswith('.pdf')]
    for arc in archivos:
        try:
            lector = PdfReader(arc)
            for pag in lector.pages[:10]:
                ext = pag.extract_text()
                if ext: texto += ext + "\n"
        except: continue
    return texto[:25000]

conocimiento_base = cargar_conocimiento()

# 3. CONFIGURACIÓN DEL MOTOR DE IA
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Error Crítico: GOOGLE_API_KEY no configurada.")
    st.stop()

# Instrucción de Sistema: Profesionalismo y Rigor
instrucciones = (
    f"Eres 'Chefcito', experto culinario con 15 años de trayectoria. Trato formal y respetuoso. "
    f"ESTÁ PROHIBIDO el uso de lenguaje afectivo como 'mi vida', 'mi cielo' o 'corazón'. "
    f"Normas de respuesta:\n"
    f"1. GRAMÁTICA: Uso estricto de Mayúsculas al iniciar oraciones y tras puntos.\n"
    f"2. COMENSALES: Si el usuario no especifica cantidad, debe solicitarla antes de entregar la receta.\n"
    f"3. BASE TÉCNICA: Utilice este contexto: {conocimiento_base}.\n"
    f"4. FORMATO: Nombre, Valor Nutritivo, Regla 50/25/25, Paso a Paso, Residuo Cero y Toque Maestro.\n"
    f"5. FINALIZACIÓN: Siempre pregunte si se requiere asistencia con otro platillo."
)

# SELECCIÓN DE MODELO ESTABLE
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=instrucciones
)

# 4. GESTIÓN DE SESIÓN
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.messages = []
    bienvenida = "¡Hola! Soy Chefcito. 👨‍🍳✨ Es un gusto saludarle. Por favor, indique su ubicación y los ingredientes que desea preparar hoy."
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# 5. FLUJO DE TRABAJO
if prompt := st.chat_input("Escriba su consulta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Llamada al modelo con gestión de errores mejorada
            response = st.session_state.chat.send_message(prompt, stream=True)
            
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
            st.error(f"Error de comunicación con el motor de IA. Detalles: {e}")
