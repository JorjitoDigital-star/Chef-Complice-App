import streamlit as st
import google.generativeai as genai

# 1. ESTILO VISUAL (24px para tu comodidad en móviles)
st.set_page_config(page_title="Tu Chefcito 👨‍🍳", page_icon="👨‍🍳")
st.markdown("<style>.stChatMessage, p, li { font-size: 24px !important; line-height: 1.5; }</style>", unsafe_allow_html=True)

st.title("👨‍🍳 Tu Chefcito")

# 2. CONEXIÓN LIMPIA (Sin forzar transporte para evitar el 404 de v1beta)
if "GOOGLE_API_KEY" in st.secrets:
    # Dejamos que la librería elija el mejor camino automáticamente hacia v1
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la API Key en los Secrets.")
    st.stop()

# 3. DEFINICIÓN DEL MODELO
# Usamos el nombre puro. La versión de la librería se encargará del resto.
model = genai.GenerativeModel('gemini-1.5-flash')

# 4. GESTIÓN DEL CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Saludo guía solicitado
    bienvenida = (
        "¡Hola! Soy **Tu Chefcito** 👨‍🍳. Para ayudarte en **Perú**, dime:\n\n"
        "* ¿En qué **país o región** estás?\n"
        "* ¿Qué **ingredientes** tienes?\n"
        "* ¿Para **cuántos comensales** cocinamos?"
    )
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. LÓGICA DE COCINA
if prompt := st.chat_input("Dime tus ingredientes..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        instrucciones = (
            "Eres 'Tu Chefcito'. Responde siempre en PRIMERA PERSONA.\n\n"
            "REGLAS:\n"
            "* Usa viñetas para cada párrafo.\n"
            "* FUSIONA en un solo bloque: Nutrición y Balance 50/25/25.\n"
            "* PASOS: Breves y sensoriales.\n"
            "* CIERRE: '¿Desea que le asista con algún otro platillo?'."
        )
        
        try:
            # Llamada directa al contenido
            response = model.generate_content(instrucciones + prompt)
            
            if response.text:
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            else:
                st.warning("El chef está pensando. Prueba a darle ingredientes más específicos.")
                
        except Exception as e:
            st.error(f"Error técnico: {e}. Por favor, verifica que tu API Key sea nueva.")
