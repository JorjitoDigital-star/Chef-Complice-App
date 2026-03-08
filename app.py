import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
import time

# 1. INTERFAZ: Letras grandes y legibles (Sin cursilerías)
st.set_page_config(page_title="Chefcito 👨‍🍳", page_icon="👨‍🍳")

st.markdown("""
    <style>
    .stChatMessage, p, li, div {
        font-size: 26px !important;
        line-height: 1.6 !important;
        color: #2D2D2D;
    }
    .recetario-chef {
        font-size: 26px !important;
        background-color: #FAFAFA;
        padding: 20px;
        border-radius: 12px;
        border: 2px solid #E63946;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Chefcito")

# 2. BACKEND: Carga de Conocimiento (Límite técnico para evitar errores)
@st.cache_resource
def cargar_datos():
    texto = ""
    archivos = [f for f in os.listdir('.') if f.endswith('.pdf')]
    for arc in archivos:
        try:
            lector = PdfReader(arc)
            for pag in lector.pages[:15]: # Leemos lo justo para no saturar la memoria
                ext = pag.extract_text()
                if ext: texto += ext + "\n"
        except: continue
    return texto[:25000] # Buffer optimizado

conocimiento = cargar_datos()

# 3. CONFIGURACIÓN DEL MOTOR (Gemini 1.5 Flash)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Error: Falta la API Key en los Secrets.")
    st.stop()

# Instrucción Maestra: Define la personalidad y reglas de gramática
instruccion_maestra = (
    f"Eres 'Chefcito', experto con 15 años de experiencia. Tu trato es profesional y respetuoso. "
    f"REGLA CRÍTICA: PROHIBIDO usar palabras como 'mi vida', 'mi cielo' o 'corazón'. "
    f"REGLAS DE ESCRITURA:\n"
    f"1. GRAMÁTICA: Mayúsculas siempre al iniciar oraciones y después de cada punto.\n"
    f"2. COMENSALES: Si el usuario no dice para cuántos es, pregunta amablemente antes de dar la receta.\n"
    f"3. SALUD: Para malestares, sugiere solo infusiones o caldos ligeros.\n"
    f"4. FORMATO: Nombre, Valor Nutritivo, Regla 50/25/25, Paso a Paso, Residuo Cero, Plus y Toque Maestro.\n"
    f"5. CONTEXTO: Usa esta base: {conocimiento}.\n"
    f"6. Siempre termina preguntando si desean preparar algo más."
)

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction=instruccion_maestra
)

# 4. GESTIÓN DE SESIÓN
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
    st.session_state.messages = []
    bienvenida = "¡Hola! Soy Chefcito. 👨‍🍳✨ Es un gusto saludarle. Por favor, indíqueme desde dónde nos escribe y qué desea cocinar hoy."
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# 5. EJECUCIÓN DEL DIÁLOGO
if prompt := st.chat_input("Escriba aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Respuesta en streaming (Maquinita de escribir)
            response = st.session_state.chat.send_message(prompt, stream=True)
            
            def stream_handler():
                for chunk in response:
                    if chunk.text:
                        for word in chunk.text.split(" "):
                            yield word + " "
                            time.sleep(0.03)

            full_text = st.write_stream(stream_handler())
            
            # Formateo si es receta
            if "Paso a Paso" in full_text:
                final_content = f'<div class="recetario-chef">{full_text}</div>'
            else:
                final_content = full_text
                
            st.session_state.messages.append({"role": "assistant", "content": final_content})
            
        except Exception as e:
            st.error("La conexión es inestable. Por favor, reintente su mensaje.")
            print(f"Error técnico: {e}")
