import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
import time

# 1. ESTILO VISUAL: Letras grandes para celular
st.set_page_config(page_title="Chef-cito 👨‍🍳", page_icon="👨‍🍳")

st.markdown("""
    <style>
    .stChatMessage, p, li, div {
        font-size: 24px !important;
        line-height: 1.5 !important;
    }
    .recetario-chef {
        font-size: 26px !important;
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border: 3px solid #FF4B4B;
        margin-top: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Chef-cito")

# 2. CARGA TURBO (Límite para velocidad)
@st.cache_resource
def cargar_biblioteca():
    texto = ""
    archivos = [f for f in os.listdir('.') if f.endswith('.pdf')]
    for arc in archivos:
        try:
            lector = PdfReader(arc)
            for pag in lector.pages:
                texto += pag.extract_text() + "\n"
                if len(texto) > 40000: break
        except: continue
    return texto[:40000]

conocimiento_pdf = cargar_biblioteca()

# 3. CONFIGURACIÓN DE IA
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Configura la llave en Secrets.")
    st.stop()

# USAMOS EL NOMBRE EXACTO DE TU CUENTA
model = genai.GenerativeModel('models/gemini-flash-latest')

# 4. HISTORIAL
if "messages" not in st.session_state:
    st.session_state.messages = []
    saludo = "¡Hola! Soy Chef-cito. 👨‍🍳✨ ¡Qué alegría! Cuéntame, ¿de dónde nos escribes y qué tienes hoy en tu cocina?"
    st.session_state.messages.append({"role": "assistant", "content": saludo})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# 5. LÓGICA SIN ERRORES
if prompt := st.chat_input("Escribe aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Instrucción limpia
        instruccion = (
            f"Eres 'Chef-cito (15 años de exp.)'. Dulce y breve con personas mayores. "
            f"Referencia: {conocimiento_pdf}. "
            f"REGLAS: 1. Gramática perfecta (Mayúsculas). 2. Pregunta siempre por comensales si no lo han dicho. "
            f"3. Si dicen adiós o gracias, despídete con amor. 4. Si es receta usa el formato: Nombre, "
            f"Valor Nutritivo, Regla 50/25/25, Paso a Paso, Residuo Cero y Toque Maestro. 5. Termina preguntando si desean algo más."
        )

        try:
            # Enviamos solo los últimos mensajes SIN el código HTML para no confundir a la IA
            contexto_limpio = ""
            for m in st.session_state.messages[-4:]:
                texto_sin_html = m['content'].replace('<div class="recetario-chef">', '').replace('</div>', '')
                contexto_limpio += f"{m['role']}: {texto_sin_html}\n"

            response = model.generate_content([instruccion, contexto_limpio, prompt], stream=True)
            
            def stream_data():
                for chunk in response:
                    if chunk.text:
                        for word in chunk.text.split(" "):
                            yield word + " "
                            time.sleep(0.04)

            full_response = st.write_stream(stream_data())
            
            if "Paso a Paso" in full_response:
                final_output = f'<div class="recetario-chef">{full_response}</div>'
            else:
                final_output = full_response
                
            st.session_state.messages.append({"role": "assistant", "content": final_output})
            
        except Exception as e:
            st.warning("¡Ay! El fogón se apagó un segundo. ¿Podrías repetirme tu mensaje, por favor?")
