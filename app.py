import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
import time

# 1. INTERFAZ PROFESIONAL (Letras Grandes)
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

# 2. CARGA DE CONOCIMIENTO (PDFs)
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

# 3. CONFIGURACIÓN DEL MOTOR
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Error: Configure la GOOGLE_API_KEY en los Secrets.")
    st.stop()

# USAMOS GEMINI-PRO PARA EVITAR EL ERROR 404 DEFINITIVAMENTE
model = genai.GenerativeModel('gemini-pro')

# 4. GESTIÓN DE SESIÓN
if "messages" not in st.session_state:
    st.session_state.messages = []
    bienvenida = "¡Hola! Soy Chefcito. 👨‍🍳✨ Es un gusto saludarle. Por favor, indique su ubicación y los ingredientes que desea preparar hoy."
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# 5. LÓGICA DE RESPUESTA
if prompt := st.chat_input("Escriba su consulta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Instrucciones profesionales inyectadas
        instrucciones = (
            f"Instrucción: Actúa como 'Chefcito', experto culinario (15 años de exp). Trato formal y respetuoso. "
            f"PROHIBIDO el lenguaje cursi (mi vida, mi cielo o corazón). "
            f"Reglas: 1. Gramática perfecta (Mayúsculas iniciales). 2. Pregunta siempre cuántos comensales son si no lo dicen. "
            f"3. Referencia técnica: {conocimiento_base}. 4. Formato: Nombre, Valor Nutritivo, Regla 50/25/25, "
            f"Paso a Paso, Residuo Cero y Toque Maestro. 5. Termina preguntando si hay algo más. "
            f"Mensaje del usuario: "
        )

        try:
            # Generación estable
            response = model.generate_content(instrucciones + prompt, stream=True)
            
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
            st.error(f"Inconveniente técnico: {e}")
