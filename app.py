import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
import time

# 1. ESTILO PROFESIONAL Y LEGIBLE
st.set_page_config(page_title="Chefcito 👨‍🍳", page_icon="👨‍🍳")

st.markdown("""
    <style>
    .stChatMessage, p, li, div {
        font-size: 24px !important;
        line-height: 1.6 !important;
        color: #1A1A1A;
    }
    .recetario-chef {
        background-color: #FDFDFD;
        padding: 20px;
        border-radius: 12px;
        border: 2px solid #D0021B;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Chefcito")

# 2. CONEXIÓN Y DESCUBRIMIENTO DE MODELO
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Error: Falta la configuración de seguridad (API Key).")
    st.stop()

# Función inteligente para evitar el Error 404
@st.cache_resource
def configurar_modelo_seguro():
    try:
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Intentamos en orden de calidad: 1.5 Flash es el ideal
        for preferido in ['models/gemini-1.5-flash', 'models/gemini-pro']:
            if preferido in modelos:
                return genai.GenerativeModel(preferido)
        return genai.GenerativeModel(modelos[0])
    except:
        return genai.GenerativeModel('gemini-pro')

model = configurar_modelo_seguro()

# 3. CARGA DE CONOCIMIENTO (PDFs)
@st.cache_resource
def cargar_biblioteca():
    texto = ""
    archivos_pdf = [f for f in os.listdir('.') if f.endswith('.pdf')]
    for arc in archivos_pdf:
        try:
            lector = PdfReader(arc)
            for pag in lector.pages[:10]:
                texto += pag.extract_text() + "\n"
        except: continue
    return texto[:25000]

biblioteca = cargar_biblioteca()

# 4. HISTORIAL DE CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
    saludo = "¡Hola! Soy Chefcito. 👨‍🍳✨ Es un gusto saludarle. Por favor, dígame desde dónde nos escribe y qué desea cocinar hoy."
    st.session_state.messages.append({"role": "assistant", "content": saludo})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# 5. LÓGICA DE RESPUESTA
if prompt := st.chat_input("Escriba aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        instrucciones = (
            f"Eres 'Chefcito', experto culinario (15 años exp). Trato formal y respetuoso. "
            f"PROHIBIDO usar lenguaje cursi. Gramática impecable (Mayúsculas iniciales). "
            f"Contexto técnico: {biblioteca}. "
            f"Si es receta: Nombre, Nutrición, Pasos, Residuo Cero y Toque Maestro. "
            f"Pregunta siempre cuántos comensales son si no lo indican. Responde: "
        )
        
        try:
            response = model.generate_content(instrucciones + prompt, stream=True)
            
            def stream_data():
                for chunk in response:
                    if chunk.text:
                        for word in chunk.text.split(" "):
                            yield word + " "
                            time.sleep(0.03)

            full_response = st.write_stream(stream_data())
            
            if "Paso a Paso" in full_response:
                final_output = f'<div class="recetario-chef">{full_response}</div>'
            else:
                final_output = full_response
                
            st.session_state.messages.append({"role": "assistant", "content": final_output})
        except Exception as e:
            st.error(f"Inconveniente técnico: {e}")
