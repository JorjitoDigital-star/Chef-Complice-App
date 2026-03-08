import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
import time

# 1. ESTILO VISUAL
st.set_page_config(page_title="Chefcito 👨‍🍳", page_icon="👨‍🍳")

st.markdown("""
    <style>
    .stChatMessage, p, li, div {
        font-size: 24px !important;
        line-height: 1.5 !important;
        color: #1A1A1A;
    }
    .recetario-chef {
        background-color: #F9F9F9;
        padding: 20px;
        border-radius: 12px;
        border: 2px solid #D0021B;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Chefcito - Experto Culinario")

# 2. CONEXIÓN (Mantenemos la forma segura)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Error: Falta la API Key.")
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

# 3. CONOCIMIENTO PDF
@st.cache_resource
def cargar_biblioteca():
    texto = ""
    archivos = [f for f in os.listdir('.') if f.endswith('.pdf')]
    for arc in archivos:
        try:
            lector = PdfReader(arc)
            for pag in lector.pages[:10]: texto += pag.extract_text() + "\n"
        except: continue
    return texto[:20000]

biblioteca = cargar_biblioteca()

# 4. HISTORIAL
if "messages" not in st.session_state:
    st.session_state.messages = []
    bienvenida = "¡Hola! Soy Chefcito. 👨‍🍳 Es un gusto saludarte. Cuéntame, ¿desde dónde escribes y qué platillo tienes en mente hoy?"
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# 5. LÓGICA DE INTELIGENCIA CORREGIDA
if prompt := st.chat_input("Escribe aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # INSTRUCCIONES MEJORADAS (Evitan el bucle y respetan el pedido)
        instrucciones = (
            f"Eres 'Chefcito', un Chef Senior con 15 años de experiencia. Tu personalidad es amigable y profesional, pero sin ser exagerada. "
            f"REGLAS DE ORO:\n"
            f"1. PRIORIDAD TOTAL: Si el usuario pide un plato específico (ej. Saltado de Pollo), DEBES dar esa receta. No intentes fusionarla con nada del PDF a menos que te lo pidan.\n"
            f"2. FILTRO DE COMENSALES: SI el usuario pide una receta y NO ha dicho para cuántos es, PREGUNTA: '¿Para cuántas personas cocinaremos hoy?'. SI YA DIJO el número, NO vuelvas a preguntar y procede con la receta.\n"
            f"3. ORIGEN: El usuario es de PERÚ. Prioriza el sabor auténtico peruano. El PDF ({biblioteca}) es solo una referencia secundaria.\n"
            f"4. PROHIBIDO: Usar 'mi vida', 'corazón', 'estimado' o lenguaje romántico/cursi.\n"
            f"5. FORMATO RECETA: Nombre, Valor Nutritivo, Regla 50/25/25, Paso a Paso, Residuo Cero y Toque Maestro.\n"
            f"6. GRAMÁTICA: Uso estricto de Mayúsculas al iniciar y tras puntos.\n\n"
            f"Basado en nuestra charla, responde al usuario: "
        )
        
        try:
            # Enviamos el historial completo para que recuerde que ya dijiste "5 personas"
            chat = model.start_chat(history=[{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages[:-1]])
            response = chat.send_message(instrucciones + prompt, stream=True)
            
            def stream_text():
                for chunk in response:
                    if chunk.text:
                        for word in chunk.text.split(" "):
                            yield word + " "
                            time.sleep(0.02)

            full_text = st.write_stream(stream_text())
            
            if "Paso a Paso" in full_text:
                output = f'<div class="recetario-chef">{full_text}</div>'
            else:
                output = full_text
                
            st.session_state.messages.append({"role": "assistant", "content": output})
        except Exception as e:
            st.error(f"Error técnico: {e}")
