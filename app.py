import streamlit as st
import google.generativeai as genai
# Forzamos la importación del cliente de producción (v1)
from google.generativeai import v1 as genai_v1

# 1. ESTILO VISUAL (24px para tu comodidad)
st.set_page_config(page_title="Tu Chefcito 👨‍🍳", page_icon="👨‍🍳")
st.markdown("<style>.stChatMessage, p, li { font-size: 24px !important; line-height: 1.5; }</style>", unsafe_allow_html=True)

st.title("👨‍🍳 Tu Chefcito")

# 2. CONEXIÓN FORZADA A PRODUCCIÓN (v1)
if "GOOGLE_API_KEY" in st.secrets:
    # Usamos genai_v1 para asegurar que no toque la puerta de 'v1beta'
    genai_v1.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Configura la nueva API Key en los Secrets.")
    st.stop()

# Inicializamos el modelo usando el cliente de producción
model = genai_v1.GenerativeModel('gemini-1.5-flash')

# 3. GESTIÓN DEL CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
    bienvenida = ("¡Hola! Soy **Tu Chefcito** 👨‍🍳. Para ayudarte en **Perú**, dime: "
                  "¿Qué **país**, **ingredientes** y **comensales**?")
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. LÓGICA DE RESPUESTA
if prompt := st.chat_input("Tengo arroz, pollo y papas..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        instrucciones = (
            "Eres 'Tu Chefcito'. Responde en PRIMERA PERSONA.\n\n"
            "REGLAS:\n"
            "* Usa viñetas para cada párrafo.\n"
            "* FUSIONA en un solo bloque: Nutrición y Balance 50/25/25.\n"
            "* PASOS: Breves y sensoriales.\n"
            "* CIERRE: '¿Desea que le asista con algún otro platillo?'."
        )
        
        try:
            # Llamada directa al motor estable
            response = model.generate_content(instrucciones + prompt)
            
            if response.text:
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"Error técnico: {e}. Intenta refrescar la página.")
