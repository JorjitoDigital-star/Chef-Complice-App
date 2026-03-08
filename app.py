import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
import time

# 1. ESTILO VISUAL: Letras grandes y legibles
st.set_page_config(page_title="Chef-cito 👨‍🍳", page_icon="👨‍🍳")

st.markdown("""
    <style>
    .stChatMessage, p, li, div {
        font-size: 24px !important;
        line-height: 1.5 !important;
    }
    .recetario-chef {
        font-size: 24px !important;
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        border: 2px solid #FF4B4B;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Chef-cito")

# 2. CARGA DE LIBROS (Optimización de velocidad)
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

# Usamos el nombre de modelo más estable
model = genai.GenerativeModel('models/gemini-flash-latest')

# 4. MEMORIA
if "messages" not in st.session_state:
    st.session_state.messages = []
    saludo = "¡Hola! Soy Chef-cito. 👨‍🍳✨ ¡Qué alegría! Cuéntame, ¿de dónde nos escribes y qué tienes hoy en tu cocina?"
    st.session_state.messages.append({"role": "assistant", "content": saludo})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# 5. LÓGICA DE DIÁLOGO RESISTENTE
if prompt := st.chat_input("Escribe aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Preparamos una instrucción que combine todo de forma simple para la IA
        instruccion = (
            f"Eres 'Chef-cito (15 años de exp.)'. Dulce y breve con personas mayores. "
            f"Referencia de libros: {conocimiento_pdf}. "
            f"REGLAS: 1. Gramática perfecta (Mayúsculas iniciales). 2. Si no sabes para cuántos es, pregunta amablemente. "
            f"3. Si dicen adiós o gracias, despídete con amor. 4. Si das receta usa el formato: Nombre, "
            f"Valor Nutritivo, Regla 50/25/25, Paso a Paso, Residuo Cero y Toque Maestro. "
            f"5. No repitas saludos si ya están hablando. 6. Siempre termina preguntando si desean algo más."
        )

        try:
            # Enviamos el mensaje actual con el contexto de forma simplificada
            response = model.generate_content(f"{instruccion}\n\nUsuario dice: {prompt}", stream=True)
            
            def stream_data():
                for chunk in response:
                    # Validamos que el fragmento tenga texto antes de procesarlo
                    if chunk.text:
                        for word in chunk.text.split(" "):
                            yield word + " "
                            time.sleep(0.04)

            full_response = st.write_stream(stream_data())
            
            # Guardamos la respuesta con o sin formato según corresponda
            if "Paso a Paso" in full_response:
                final_output = f'<div class="recetario-chef">{full_response}</div>'
            else:
                final_output = full_response
                
            st.session_state.messages.append({"role": "assistant", "content": final_output})
            
        except Exception as e:
            st.error("¡Ay! El fogón chispeó un poco. ¿Me podrías repetir tu mensaje?")
