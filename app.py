import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
import time

# 1. ESTILO VISUAL PROFESIONAL
st.set_page_config(page_title="Chefcito 👨‍🍳", page_icon="👨‍🍳")
st.markdown("<style>.stChatMessage, p, li, div { font-size: 24px !important; }</style>", unsafe_allow_html=True)
st.title("👨‍🍳 Chefcito - Experto Culinario")

# 2. CONEXIÓN SEGURA
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Error: Falta la API Key en los Secrets.")
    st.stop()

@st.cache_resource
def configurar_modelo():
    try:
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for p in ['models/gemini-1.5-flash', 'models/gemini-pro']:
            if p in modelos: return genai.GenerativeModel(p)
        return genai.GenerativeModel(modelos[0])
    except: return genai.GenerativeModel('gemini-1.5-flash')

model = configurar_modelo()

# 3. LECTURA DE PDF (CONOCIMIENTO)
@st.cache_resource
def cargar_biblioteca():
    texto = ""
    for arc in [f for f in os.listdir('.') if f.endswith('.pdf')]:
        try:
            lector = PdfReader(arc)
            for pag in lector.pages[:10]: texto += pag.extract_text() + "\n"
        except: continue
    return texto[:20000]

biblioteca = cargar_biblioteca()

# 4. MEMORIA DE CHAT (REFORMADA)
if "messages" not in st.session_state:
    st.session_state.messages = []
    bienvenida = "¡Hola! Soy Chefcito. 👨‍🍳 Es un gusto saludarte. Cuéntame, ¿desde dónde escribes y qué platillo tienes en mente hoy?"
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# 5. LÓGICA DE RESPUESTA (SIN ERRORES DE ROLE)
if prompt := st.chat_input("Escribe aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # INSTRUCCIONES MEJORADAS
        instrucciones = (
            f"Eres 'Chefcito', Chef Senior (15 años exp). Personalidad amigable y profesional. "
            f"REGLAS:\n"
            f"1. SI pides receta y NO hay número de comensales, PREGUNTA: '¿Para cuántos comensales cocinaremos?'.\n"
            f"2. SI el usuario es de PERÚ, dale sabor peruano auténtico. El PDF ({biblioteca}) es secundario.\n"
            f"3. PROHIBIDO lenguaje cursi o romántico.\n"
            f"4. FORMATO: Nombre, Nutrición, Regla 50/25/25, Paso a Paso, Residuo Cero y Toque Maestro.\n"
            f"5. GRAMÁTICA: Mayúsculas tras puntos e inicio de frase.\n\n"
        )
        
        try:
            # TRADUCCIÓN DE ROLES PARA GOOGLE (Aquí estaba el fallo 400)
            historial_google = []
            for m in st.session_state.messages[:-1]:
                # Google solo acepta 'user' o 'model'
                rol_google = "user" if m["role"] == "user" else "model"
                historial_google.append({"role": rol_google, "parts": [m["content"]]})

            chat = model.start_chat(history=historial_google)
            response = chat.send_message(instrucciones + prompt, stream=True)
            
            def stream_text():
                for chunk in response:
                    if chunk.text:
                        for word in chunk.text.split(" "):
                            yield word + " "
                            time.sleep(0.02)

            full_text = st.write_stream(stream_text())
            
            # Formato estético para recetas
            if "Paso a Paso" in full_text:
                output = f'<div style="background-color:#F9F9F9; padding:20px; border-radius:12px; border:2px solid #D0021B;">{full_text}</div>'
            else:
                output = full_text
                
            st.session_state.messages.append({"role": "assistant", "content": output})
        except Exception as e:
            st.error(f"Inconveniente técnico: {e}")
