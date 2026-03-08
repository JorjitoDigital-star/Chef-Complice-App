import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
import time

# 1. ESTILO VISUAL: Gramática clara y letras para celular
st.set_page_config(page_title="Chef-cito 👨‍🍳", page_icon="👨‍🍳")

st.markdown("""
    <style>
    .stChatMessage, p, li, div {
        font-size: 24px !important;
        line-height: 1.5 !important;
        color: #333333;
    }
    .recetario-chef {
        font-size: 24px !important;
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #FF4B4B;
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

# 2. CARGA TURBO (Optimización de 50k caracteres)
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

# 3. CONEXIÓN CON EL CEREBRO DE GOOGLE
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la configuración de seguridad en Secrets.")
    st.stop()

model = genai.GenerativeModel('models/gemini-flash-latest')

# 4. MEMORIA DEL CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
    saludo_inicial = "¡Hola! Soy Chef-cito. 👨‍🍳✨ Es un gusto saludarte. Cuéntame, ¿de qué parte nos escribes y qué tienes en tu cocina hoy?"
    st.session_state.messages.append({"role": "assistant", "content": saludo_inicial})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# 5. LÓGICA DE RESPUESTA Y EFECTO DE ESCRITURA
if prompt := st.chat_input("Escribe aquí tu mensaje..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        instruccion = (
            f"Eres 'Chef-cito'. Hablas con personas mayores de forma dulce, breve y natural. "
            f"Usa tus libros ({conocimiento_pdf}) y la web. "
            f"REGLAS:\n"
            f"1. Usa gramática perfecta: Mayúsculas al inicio y después de punto.\n"
            f"2. NO repitas saludos constantes. Sé natural y varía tus frases.\n"
            f"3. Formato receta: Nombre, Valor Nutritivo, Regla 50/25/25, Paso a Paso, Residuo Cero y Toque Maestro.\n"
            f"4. Termina siempre con: '¿Te gustaría preparar algún otro platillo?'\n"
            f"5. Sé breve y usa viñetas."
        )

        try:
            # Generación con flujo de datos (Stream)
            response = model.generate_content([instruccion, prompt], stream=True)
            
            def stream_data():
                for chunk in response:
                    for word in chunk.text.split(" "):
                        yield word + " "
                        time.sleep(0.04)

            # Efecto de escritura
            full_response = st.write_stream(stream_data())
            
            # Formateo visual del recetario
            if "paso a paso" in full_response.lower():
                final_html = f'<div class="recetario-chef">{full_response}</div>'
                st.session_state.messages.append({"role": "assistant", "content": final_html})
            else:
                st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        except Exception as e:
            st.error(f"Hubo un pequeño inconveniente en la cocina: {e}")
