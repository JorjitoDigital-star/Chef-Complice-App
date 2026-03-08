import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os

# 1. Configuración de estilo
st.set_page_config(page_title="Chef Cómplice 👨‍🍳", page_icon="👨‍🍳")
st.title("👨‍🍳 Chef Cómplice")
st.markdown("---")

# 2. Carga silenciosa de PDFs (Cerebro de fondo)
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
    return texto_total[:120000] # Límite optimizado para no saturar

conocimiento_chef = cargar_biblioteca()

# 3. Conexión con Gemini
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la API Key en Secrets.")
    st.stop()

model = genai.GenerativeModel('models/gemini-flash-latest')

# 4. PERSONALIDAD: El Saludo y el Historial
if "messages" not in st.session_state:
    st.session_state.messages = []
    # ESTE ES EL SALUDO AMIGABLE QUE KERÍAS
    saludo_inicial = (
        "¡Hola! ¡Soy tu Chef Cómplice! 👨‍🍳✨\n\n"
        "Sea que tengas mucho o solo dos cositas en la refri, ¡aquí hacemos magia!\n\n"
        "Para empezar, cuéntame: **¿De dónde me escribes, cuántos comensales son y qué ingredientes tienes hoy?**"
    )
    st.session_state.messages.append({"role": "assistant", "content": saludo_inicial})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Lógica del Chat con Instrucciones de Personalidad
if prompt := st.chat_input("Escribe tus ingredientes aquí..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # INSTRUCCIONES DE COMPORTAMIENTO (The "Secret Sauce")
            system_instruction = (
                f"Eres el 'Chef Cómplice', un asistente de cocina extremadamente amigable, entusiasta y creativo. "
                f"Tu objetivo es ayudar a las personas a cocinar con lo que tienen a mano. "
                f"REGLAS DE ORO:\n"
                f"1. NO menciones que estás leyendo PDFs ni nombres archivos como 'LATINFOODS'. Eso es tu secreto.\n"
                f"2. Usa el conocimiento de tus libros ({conocimiento_chef}) para dar recetas precisas, pero habla de forma natural.\n"
                f"3. Siempre pregunta o ten en cuenta la ubicación del usuario, los ingredientes y cuántos son.\n"
                f"4. Usa viñetas para que tus recetas sean fáciles de leer.\n"
                f"5. Mantén un tono de 'complicidad' y alegría."
            )
            
            response = model.generate_content([system_instruction, prompt])
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"¡Vaya! Hubo un problema en la hornilla: {e}")
