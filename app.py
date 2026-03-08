import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
import time

# 1. ESTILO VISUAL: Profesional y con letras para celular
st.set_page_config(page_title="Chefcito 👨‍🍳", page_icon="👨‍🍳")

st.markdown("""
    <style>
    .stChatMessage, p, li, div {
        font-size: 24px !important;
        line-height: 1.5 !important;
    }
    .recetario-chef {
        font-size: 24px !important;
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 2px solid #FF4B4B;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Chefcito")

# 2. CARGA DE LIBROS (Optimización de estabilidad)
@st.cache_resource
def cargar_biblioteca():
    texto = ""
    archivos = [f for f in os.listdir('.') if f.endswith('.pdf')]
    for arc in archivos:
        try:
            lector = PdfReader(arc)
            for pag in lector.pages:
                texto += pag.extract_text() + "\n"
                if len(texto) > 30000: break 
        except: continue
    return texto[:30000]

conocimiento_pdf = cargar_biblioteca()

# 3. CONFIGURACIÓN DE IA
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la llave en Secrets.")
    st.stop()

model = genai.GenerativeModel('models/gemini-flash-latest')

# 4. HISTORIAL
if "messages" not in st.session_state:
    st.session_state.messages = []
    saludo = "¡Hola! Soy Chefcito. 👨‍🍳✨ Es un gusto saludarte. Cuéntame, ¿de dónde nos escribes y qué tienes en tu cocina hoy?"
    st.session_state.messages.append({"role": "assistant", "content": saludo})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# 5. LÓGICA DE DIÁLOGO PROFESIONAL
if prompt := st.chat_input("Escribe aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        instruccion = (
            f"Eres 'Chefcito (15 años de exp.)'. Hablas de forma respetuosa, clara y profesional. "
            f"NO uses términos como 'mi vida', 'mi cielo' o 'corazón'. "
            f"Referencia de libros: {conocimiento_pdf}. "
            f"REGLAS:\n"
            f"1. GRAMÁTICA: Usa siempre Mayúsculas al iniciar oraciones y después de cada punto.\n"
            f"2. COMENSALES: Si no sabes para cuántos es, pregunta con respeto.\n"
            f"3. DESPEDIDA: Si dicen adiós o gracias, despídete con amabilidad.\n"
            f"4. FORMATO: Nombre, Valor Nutritivo, Regla 50/25/25, Paso a Paso, Residuo Cero y Toque Maestro.\n"
            f"5. No repitas saludos constantes. Sé directo y servicial.\n"
            f"6. Termina preguntando si desean algo más."
        )

        try:
            # Enviamos solo el mensaje actual para evitar errores de saturación
            response = model.generate_content([instruccion, prompt], stream=True)
            
            def stream_data():
                for chunk in response:
                    try:
                        if chunk.text:
                            for word in chunk.text.split(" "):
                                yield word + " "
                                time.sleep(0.04)
                    except: continue

            full_response = st.write_stream(stream_data())
            
            if "Paso a Paso" in full_response:
                final_output = f'<div class="recetario-chef">{full_response}</div>'
            else:
                final_output = full_response
                
            st.session_state.messages.append({"role": "assistant", "content": final_output})
            
        except Exception as e:
            st.error(f"Ocurrió un inconveniente técnico: {e}")
