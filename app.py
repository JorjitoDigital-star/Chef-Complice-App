import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os

# 1. Configuración de la interfaz (Tu marca personal)
st.set_page_config(page_title="Chef Cómplice 👨‍🍳", page_icon="👨‍🍳", layout="centered")
st.title("👨‍🍳 Chef Cómplice")
st.subheader("Tu guía de cocina inteligente")
st.markdown("---")

# 2. Función para leer la biblioteca de PDFs
@st.cache_resource
def cargar_biblioteca():
    texto_total = ""
    # Escanea la carpeta en busca de todos los archivos PDF
    archivos_pdf = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    for archivo in archivos_pdf:
        try:
            lector = PdfReader(archivo)
            for pagina in lector.pages:
                extraido = pagina.extract_text()
                if extraido:
                    texto_total += extraido + "\n"
        except Exception as e:
            st.error(f"Error leyendo {archivo}: {e}")
    
    # Limitamos el texto para no saturar la memoria (aprox. 150-200 páginas)
    return texto_total[:400000] 

# Cargamos el conocimiento de tus 6 PDFs
conocimiento_chef = cargar_biblioteca()

# 3. Configuración de Seguridad y API
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("⚠️ Configuración incompleta: Por favor, agrega la GOOGLE_API_KEY en los Secrets de Streamlit.")
    st.stop()

# Inicializamos el modelo (usamos el nombre estándar para evitar el error 404)
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Error al inicializar Gemini: {e}")
    st.stop()

# 4. Gestión del historial del Chat
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Saludo inicial personalizado
    bienvenida = "¡Hola! Soy tu Chef Cómplice! 👨‍🍳 Tengo mis 6 libros listos para ayudarte. Dime qué ingredientes tienes a mano y de qué parte de Chile me escribes."
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

# Mostrar los mensajes previos en pantalla
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Lógica de interacción
if prompt := st.chat_input("¿Qué cocinamos hoy?"):
    # Agregar mensaje del usuario al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generar respuesta del Chef
    with st.chat_message("assistant"):
        try:
            # Construimos la instrucción maestra combinando el PDF y la pregunta
            contexto_instrucciones = (
                f"Eres el 'Chef Cómplice', un experto en cocina peruana y nutrición. "
                f"Utiliza exclusivamente este conocimiento para responder: {conocimiento_chef}. "
                f"Sé entusiasta, breve y creativo. Si te preguntan algo fuera de cocina, "
                f"vuelve a llevar la conversación a las recetas de tus libros."
            )
            
            # Llamada oficial a la API
            response = model.generate_content([contexto_instrucciones, prompt])
            
            # Mostrar y guardar respuesta
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"El Chef tuvo un pequeño problema técnico: {e}")
            st.info("Revisa que tu API Key sea válida y no tenga restricciones de facturación.")
