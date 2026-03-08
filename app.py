import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os

# 1. Configuración de Pantalla y ESTILO VISUAL (Letras Extra Grandes)
st.set_page_config(page_title="Chef-cito 👨‍🍳", page_icon="👨‍🍳")

st.markdown("""
    <style>
    /* Tamaño de letra para toda la conversación */
    .stChatMessage, p, li {
        font-size: 26px !important;
        line-height: 1.4 !important;
    }
    /* Estilo especial para que el RECETARIO sea aún más grande */
    .recetario-chef {
        font-size: 32px !important;
        font-weight: bold !important;
        color: #1E1E1E;
        background-color: #F0F2F6;
        padding: 20px;
        border-radius: 10px;
        border-left: 10px solid #FF4B4B;
    }
    /* Títulos dentro del recetario */
    .recetario-chef h1, .recetario-chef h2 {
        font-size: 38px !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Chef-cito")
st.markdown("---")

# 2. Carga del conocimiento de tus 6 PDFs
@st.cache_resource
def cargar_biblioteca():
    texto_total = ""
    archivos_pdf = [f for f in os.listdir('.') if f.endswith('.pdf')]
    for archivo in archivos_pdf:
        try:
            lector = PdfReader(archivo)
            for pagina in lector.pages:
                extraido = pagina.extract_text()
                if extraido:
                    texto_total += extraido + "\n"
        except:
            continue
    return texto_total[:120000]

conocimiento_pdf = cargar_biblioteca()

# 3. Configuración de la IA de Google (Gemini)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("⚠️ Falta la llave secreta en los Secrets de Streamlit.")
    st.stop()

# Usamos el modelo más potente y rápido detectado en tu cuenta
model = genai.GenerativeModel('models/gemini-flash-latest')

# 4. El Saludo Amistoso de Chef-cito
if "messages" not in st.session_state:
    st.session_state.messages = []
    saludo = (
        "¡Hola! Soy Chef-cito. 👨‍🍳✨\n\n"
        "¡Vamos a cocinar rico y sano!\n\n"
        "* ¿De dónde me escribes?\n"
        "* ¿Cuántos van a comer?\n"
        "* ¿Qué tienes en tu cocina hoy?"
    )
    st.session_state.messages.append({"role": "assistant", "content": saludo})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# 5. Generación de Recetas con Formato Gourmet y Letra Gigante
if prompt := st.chat_input("Escribe aquí tus ingredientes..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # INSTRUCCIÓN MAESTRA: PDF + WEB + FORMATO GOURMET
            system_instruction = (
                f"Eres 'Chef-cito (15 años de exp.)'. Hablas con personas mayores de forma dulce y simple. "
                f"Usa el conocimiento técnico de estos PDFs: {conocimiento_pdf} Y TAMBIÉN toda la información de la web para mejorar la receta. "
                f"REGLA DE FORMATO: Debes responder usando EXACTAMENTE esta estructura y envolver todo el recetario en un div con clase 'recetario-chef':\n"
                f"1. Saludo breve: 'Soy tu Chef-cito 👨‍🍳. vamos a preparar este ícono...'\n"
                f"2. Nombre del Plato + Autor: Chef-Cito.\n"
                f"3. Valor Nutritivo 💪.\n"
                f"4. Proporciones (Regla Nutritiva 50/25/25).\n"
                f"5. Paso a Paso 🍳 (usa verbos inspiradores como 'Sella la magia').\n"
                f"6. Residuo Cero.\n"
                f"7. El Plus del Chef-Cito 💡.\n"
                f"8. Toque Maestro 🌟.\n"
                f"IMPORTANTE: No menciones nunca la palabra 'PDF'. Mantén las instrucciones breves y sencillas."
            )
            
            response = model.generate_content([system_instruction, prompt])
            
            # Envolvemos la respuesta en el formato de letra extra grande
            respuesta_formateada = f'<div class="recetario-chef">{response.text}</div>'
            
            st.markdown(respuesta_formateada, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": respuesta_formateada})
            
        except Exception as e:
            st.error("¡Ay! Hubo un problema en la cocina. Por favor, intenta de nuevo en unos segundos.")
