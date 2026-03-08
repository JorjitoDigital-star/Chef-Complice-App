import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
import time

# 1. ESTILO VISUAL: Letras claras para celular (sin gritar)
st.set_page_config(page_title="Chef-cito 👨‍🍳", page_icon="👨‍🍳")

st.markdown("""
    <style>
    /* Letra grande pero cómoda para celular */
    .stChatMessage, p, li, div {
        font-size: 24px !important;
        line-height: 1.4 !important;
        color: #333333;
    }
    /* Recetario: Destacado pero sin ser gigante */
    .recetario-chef {
        font-size: 24px !important;
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        border: 2px solid #FF4B4B;
        margin-top: 10px;
        color: #000000;
    }
    /* Títulos suaves, no gritados */
    .recetario-chef h2 {
        font-size: 28px !important;
        color: #FF4B4B !important;
        text-transform: lowercase;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Chef-cito")

# 2. CARGA TURBO (Solo lo esencial para máxima velocidad)
@st.cache_resource
def cargar_biblioteca():
    texto_total = ""
    archivos_pdf = [f for f in os.listdir('.') if f.endswith('.pdf')]
    for archivo in archivos_pdf:
        try:
            lector = PdfReader(archivo)
            # Solo cargamos 50k caracteres para que vuele
            for pagina in lector.pages:
                texto_total += pagina.extract_text() + "\n"
                if len(texto_total) > 50000: break
        except:
            continue
    return texto_total[:50000]

conocimiento_pdf = cargar_biblioteca()

# 3. CONEXIÓN CON GEMINI
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("falta la llave en secrets.")
    st.stop()

model = genai.GenerativeModel('models/gemini-flash-latest')

# 4. HISTORIAL DE MENSAJES
if "messages" not in st.session_state:
    st.session_state.messages = []
    saludo = "¡hola! soy chef-cito. 👨‍🍳✨ ¿de qué parte nos escribes y qué tienes en tu cocina hoy?"
    st.session_state.messages.append({"role": "assistant", "content": saludo})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# 5. LÓGICA DE RESPUESTA CON EFECTO MAQUINA DE ESCRIBIR
if prompt := st.chat_input("escribe aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Detectamos si es una charla fluida para no repetir el nombre
        es_primera_vez = len(st.session_state.messages) < 3
        
        instruccion = (
            f"eres 'chef-cito'. hablas con personas mayores de forma dulce y breve. "
            f"usa tus libros ({conocimiento_pdf}) y la web. "
            f"REGLAS:\n"
            f"1. si ya se presentaron, NO digas 'soy tu chef-cito', solo responde con cariño.\n"
            f"2. usa minúsculas mayormente, que se sienta suave al leer.\n"
            f"3. si es receta, usa el formato: nombre, valor nutritivo, regla 50/25/25, paso a paso, residuo cero y toque maestro.\n"
            f"4. termina siempre preguntando: '¿te gustaría preparar algún otro platillo?'\n"
            f"5. sé muy breve y usa viñetas."
        )

        try:
            # Generar respuesta con efecto de escritura fluida
            response = model.generate_content([instruccion, prompt], stream=True)
            
            def stream_data():
                for chunk in response:
                    for word in chunk.text.split(" "):
                        yield word + " "
                        time.sleep(0.04) # velocidad de escritura

            # Mostramos el texto con el efecto
            full_response = st.write_stream(stream_data())
            
            # Si detectamos que es receta, le ponemos el estilo visual después
            if "paso a paso" in full_response.lower():
                final_html = f'<div class="recetario-chef">{full_response}</div>'
                # Guardamos con el estilo
                st.session_state.messages.append({"role": "assistant", "content": final_html})
            else:
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
        except Exception:
            st.error("un pequeño error en la cocina, ¿me lo repites?")
