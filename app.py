import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
import time

# 1. ESTILO VISUAL: Profesional, alegre y legible para celular
st.set_page_config(page_title="Chefcito 👨‍🍳", page_icon="👨‍🍳")

st.markdown("""
    <style>
    /* Tipografía grande para evitar fatiga visual */
    .stChatMessage, p, li, div {
        font-size: 26px !important;
        line-height: 1.6 !important;
        color: #1A1A1A;
    }
    /* El toque maestro: Recetario destacado */
    .recetario-chef {
        background-color: #FFF9F9;
        padding: 25px;
        border-radius: 15px;
        border: 3px solid #FF4B4B;
        margin-top: 15px;
        box-shadow: 4px 4px 15px rgba(0,0,0,0.1);
    }
    .recetario-chef h2 {
        color: #FF4B4B !important;
        font-size: 30px !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 ¡Bienvenidos a la cocina de Chefcito!")

# 2. CONEXIÓN Y DETECCIÓN DE MODELO (Blindado contra Error 404)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("¡Ups! Falta la llave de la cocina (API Key) en los Secrets.")
    st.stop()

@st.cache_resource
def configurar_modelo_seguro():
    try:
        # Detectamos qué modelos tiene habilitada tu cuenta
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for preferido in ['models/gemini-1.5-flash', 'models/gemini-pro']:
            if preferido in modelos:
                return genai.GenerativeModel(preferido)
        return genai.GenerativeModel(modelos[0])
    except:
        return genai.GenerativeModel('gemini-1.5-flash')

model = configurar_modelo_seguro()

# 3. CARGA DE CONOCIMIENTO (PDFs)
@st.cache_resource
def cargar_biblioteca():
    texto = ""
    archivos_pdf = [f for f in os.listdir('.') if f.endswith('.pdf')]
    for arc in archivos_pdf:
        try:
            lector = PdfReader(arc)
            for pag in lector.pages[:15]:
                texto += pag.extract_text() + "\n"
        except: continue
    return texto[:25000]

biblioteca = cargar_biblioteca()

# 4. GESTIÓN DEL CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
    saludo_inicial = "¡Hola, hola! 👨‍🍳✨ ¡Qué alegría saludarte! Soy Chefcito, tu guía culinario con 15 años de sazón. Cuéntame, ¿desde qué rincón del mundo me escribes y qué ingredientes tienes a mano para hoy?"
    st.session_state.messages.append({"role": "assistant", "content": saludo_inicial})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# 5. LÓGICA DE PERSONALIDAD Y RESPUESTA
if prompt := st.chat_input("¿Qué cocinamos hoy?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # La "Receta" de la personalidad de Chefcito
        instrucciones = (
            f"Eres 'Chefcito'. Tu personalidad es vibrante, amigable, divertida y carismática. "
            f"Eres un experto con 15 años de experiencia que ama enseñar con alegría. "
            f"REGLAS DE ORO:\n"
            f"1. CERO CURSILERÍAS: Prohibido usar 'mi vida', 'mi cielo', 'corazón' o 'estimado usuario'.\n"
            f"2. PREGUNTA OBLIGATORIA: Si te piden una receta o consejo, ANTES de dar ingredientes o pasos, "
            f"debes preguntar con entusiasmo: '¡Excelente elección! Pero antes de encender el fogón, ¿para cuántos comensales vamos a cocinar esta delicia?'.\n"
            f"3. GRAMÁTICA: Escribe con elegancia. Mayúsculas siempre al iniciar cada frase y después de puntos.\n"
            f"4. CONTEXTO: Usa tu sabiduría global y apóyate en este manual técnico si es necesario: {biblioteca}.\n"
            f"5. FORMATO RECETA: Cuando sepas los comensales, entrega: Nombre, Valor Nutritivo, Regla 50/25/25, Paso a Paso, Residuo Cero y Toque Maestro.\n"
            f"6. CIERRE: Siempre termina con: '¿Desea que le asista con algún otro platillo?'\n\n"
            f"Responde con chispa y profesionalismo a: "
        )
        
        try:
            # Generación con flujo (Stream) para efecto de máquina de escribir
            response = model.generate_content(instrucciones + prompt, stream=True)
            
            def stream_handler():
                for chunk in response:
                    if chunk.text:
                        for word in chunk.text.split(" "):
                            yield word + " "
                            time.sleep(0.02)

            full_response = st.write_stream(stream_handler())
            
            # Formato visual si hay una receta completa
            if "Paso a Paso" in full_response:
                final_output = f'<div class="recetario-chef">{full_response}</div>'
            else:
                final_output = full_response
                
            st.session_state.messages.append({"role": "assistant", "content": final_output})
            
        except Exception as e:
            st.error(f"¡Vaya! El fogón chispeó un poco. Intentemos de nuevo. (Error: {e})")
