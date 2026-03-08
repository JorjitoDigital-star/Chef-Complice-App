import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
import time

# 1. ARQUITECTURA VISUAL (CSS Optimizado para móviles y legibilidad)
st.set_page_config(page_title="Chefcito 👨‍🍳", page_icon="👨‍🍳", layout="centered")

st.markdown("""
    <style>
    /* Tipografía de alta legibilidad para adultos mayores */
    .stChatMessage, p, li, div {
        font-size: 26px !important;
        line-height: 1.6 !important;
        color: #2D2D2D;
    }
    /* Contenedor de Receta: Diseño profesional y limpio */
    .recetario-chef {
        font-size: 26px !important;
        background-color: #FAFAFA;
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #E63946;
        margin-top: 15px;
        color: #1A1A1A;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    .recetario-chef h2 {
        font-size: 32px !important;
        color: #E63946 !important;
        margin-bottom: 15px;
        text-transform: capitalize;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Chefcito")

# 2. PROCESAMIENTO DE DATOS (Backend)
@st.cache_resource
def preparar_conocimiento():
    texto = ""
    archivos = [f for f in os.listdir('.') if f.endswith('.pdf')]
    for arc in archivos:
        try:
            lector = PdfReader(arc)
            for pag in lector.pages[:20]: # Límite de páginas por libro para estabilidad
                extraido = pag.extract_text()
                if extraido: texto += extraido + "\n"
        except: continue
    return texto[:30000] # Buffer optimizado para el contexto de Gemini

contexto_pdf = preparar_conocimiento()

# 3. CONFIGURACIÓN DEL MOTOR DE IA (Gemini API)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Error de Sistema: API Key no detectada.")
    st.stop()

# Definición de las Instrucciones del Sistema (Personalidad y Reglas)
instrucciones_sistema = (
    f"Eres 'Chefcito', un experto culinario con 15 años de experiencia. Tu trato es profesional y respetuoso. "
    f"ESTÁ PROHIBIDO usar lenguaje cursi (mi vida, mi cielo, corazón, etc.). "
    f"Reglas estrictas:\n"
    f"1. GRAMÁTICA: Usa siempre Mayúsculas al iniciar cada oración y después de cada punto.\n"
    f"2. COMENSALES: Si el usuario no indica para cuántos cocinará, debes preguntar de forma directa y amable antes de proceder.\n"
    f"3. CONTEXTO: Usa esta base técnica: {contexto_pdf}. Si la información es antigua, compleméntala con conocimientos actuales de la web.\n"
    f"4. FORMATO DE RECETA: Nombre, Valor Nutritivo, Regla 50/25/25, Paso a Paso, Residuo Cero, Plus y Toque Maestro.\n"
    f"5. DESPEDIDA: Si el usuario dice 'no', 'gracias' o 'adiós', despídete con profesionalismo y cierra la charla.\n"
    f"6. Siempre termina preguntando si se requiere asistencia con algún otro platillo."
)

# Inicialización del modelo con la instrucción del sistema integrada
model = genai.GenerativeModel(
    model_name='models/gemini-flash-latest',
    system_instruction=instrucciones_sistema
)

# 4. GESTIÓN DE SESIÓN Y CHAT NATIVO
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.messages = []
    bienvenida = "¡Hola! Soy Chefcito. 👨‍🍳✨ Es un gusto saludarle. Por favor, indíqueme desde dónde nos escribe y qué ingredientes desea utilizar hoy."
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

# Renderizado de mensajes previos
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# 5. FLUJO DE TRABAJO (Frontend -> API -> Frontend)
if prompt := st.chat_input("Escriba su mensaje aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Llamada al chat nativo con streaming
            response = st.session_state.chat.send_message(prompt, stream=True)
            
            # Generador para el efecto máquina de escribir
            def generar_texto():
                for chunk in response:
                    if chunk.text:
                        for word in chunk.text.split(" "):
                            yield word + " "
                            time.sleep(0.04)

            # Salida visual dinámica
            respuesta_final = st.write_stream(generar_texto())
            
            # Post-procesamiento: Aplicar formato de recetario si es necesario
            if "Paso a Paso" in respuesta_final:
                html_output = f'<div class="recetario-chef">{respuesta_final}</div>'
            else:
                html_output = respuesta_final
                
            st.session_state.messages.append({"role": "assistant", "content": html_output})
            
        except Exception as e:
            st.error("Error de comunicación con el servidor. Por favor, reintente en unos segundos.")
            # Registro técnico para depuración (solo visible en logs)
            print(f"DEBUG ERROR: {e}")
