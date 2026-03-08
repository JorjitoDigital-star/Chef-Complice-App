import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
import time

# 1. ESTILO VISUAL: Letras grandes y gramática profesional
st.set_page_config(page_title="Chef-cito 👨‍🍳", page_icon="👨‍🍳")

st.markdown("""
    <style>
    .stChatMessage, p, li, div {
        font-size: 24px !important;
        line-height: 1.5 !important;
        color: #333333;
    }
    .recetario-chef {
        font-size: 26px !important;
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border: 3px solid #FF4B4B;
        margin-top: 15px;
        color: #000000;
    }
    .recetario-chef h2 {
        font-size: 30px !important;
        color: #FF4B4B !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Chef-cito")

# 2. CARGA TURBO (Límite de 50k para velocidad)
@st.cache_resource
def cargar_biblioteca():
    texto_total = ""
    archivos_pdf = [f for f in os.listdir('.') if f.endswith('.pdf')]
    for archivo in archivos_pdf:
        try:
            lector = PdfReader(archivo)
            for pagina in lector.pages:
                texto_total += pagina.extract_text() + "\n"
                if len(texto_total) > 50000: break
        except:
            continue
    return texto_total[:50000]

conocimiento_pdf = cargar_biblioteca()

# 3. CONFIGURACIÓN DE IA
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Por favor, configura la llave en Secrets.")
    st.stop()

model = genai.GenerativeModel('gemini-1.5-flash-latest')

# 4. MEMORIA DEL CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
    saludo_inicial = "¡Hola! Soy Chef-cito. 👨‍🍳✨ ¡Qué alegría encontrarte! Cuéntame, ¿de dónde nos escribes y qué tienes hoy en tu cocina?"
    st.session_state.messages.append({"role": "assistant", "content": saludo_inicial})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# 5. LÓGICA DE RESPUESTA
if prompt := st.chat_input("Escribe aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Instrucciones de personalidad
        instruccion = (
            f"Eres 'Chef-cito (15 años de exp.)'. Hablas con personas mayores de forma dulce y respetuosa. "
            f"Conocimiento base: {conocimiento_pdf}. "
            f"REGLAS:\n"
            f"1. GRAMÁTICA: Siempre Mayúsculas al iniciar y después de punto.\n"
            f"2. SIEMPRE PREGUNTA para cuántos comensales si no lo han dicho.\n"
            f"3. Si dicen 'no', 'gracias' o 'adiós', despídete con amor.\n"
            f"4. Si es receta, usa el formato: Nombre, Valor Nutritivo, Regla 50/25/25, Paso a Paso, Residuo Cero, Plus y Toque Maestro.\n"
            f"5. Termina siempre preguntando si desean algo más."
        )

        try:
            # Llamada a la IA (Pasamos el historial simplificado para evitar errores)
            history_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-3:]])
            response = model.generate_content([instruccion, history_context, prompt], stream=True)
            
            def stream_data():
                for chunk in response:
                    if chunk.text:
                        for word in chunk.text.split(" "):
                            yield word + " "
                            time.sleep(0.04)

            full_response = st.write_stream(stream_data())
            
            # Formateo si es receta
            if "Paso a Paso" in full_response:
                final_output = f'<div class="recetario-chef">{full_response}</div>'
            else:
                final_output = full_response
                
            st.session_state.messages.append({"role": "assistant", "content": final_output})
            
        except Exception as e:
            st.warning("¡Uy! Hubo un pequeño error de conexión. ¿Me lo repites con cariño?")
            print(f"Error: {e}")
