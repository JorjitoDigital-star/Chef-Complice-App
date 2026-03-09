import streamlit as st
import google.generativeai as genai

# 1. ESTILO VISUAL (24px para lectura cómoda en móviles)
st.set_page_config(page_title="Tu Chefcito 👨‍🍳", page_icon="👨‍🍳")
st.markdown("<style>.stChatMessage, p, li { font-size: 24px !important; line-height: 1.5; }</style>", unsafe_allow_html=True)

st.title("👨‍🍳 Tu Chefcito")

# 2. CONFIGURACIÓN MAESTRA (Forzando la Versión Estable)
if "GOOGLE_API_KEY" in st.secrets:
    # El transporte 'rest' es el más estable para validar créditos en Google Cloud
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"], transport='rest')
else:
    st.error("Falta la API Key en los Secrets.")
    st.stop()

# Usamos el nombre del modelo sin prefijos para que la versión 0.8.3 use 'v1' automáticamente
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. GESTIÓN DEL CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Saludo guía solicitado para [país], [ingredientes] y [comensales]
    bienvenida = (
        "¡Hola! Soy **Tu Chefcito** 👨‍🍳. Para ayudarte hoy en **Perú**, dime:\n\n"
        "* ¿En qué **país o región** estás?\n"
        "* ¿Qué **ingredientes** tienes?\n"
        "* ¿Para **cuántos comensales** cocinamos?"
    )
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. LÓGICA DE RESPUESTA (Sin streaming para asegurar estabilidad)
if prompt := st.chat_input("Dime qué tienes en la cocina..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Instrucciones Maestras FUSIONADAS
        instrucciones = (
            "Eres 'Tu Chefcito', experto en cocina peruana y del mundo. Habla en PRIMERA PERSONA.\n\n"
            "REGLAS:\n"
            "* Usa viñetas para cada párrafo o paso.\n"
            "* FUSIONA en un solo bloque breve: El equilibrio 50/25/25 y el valor nutricional.\n"
            "* PASOS: Breves y sensoriales (menciona aromas y texturas).\n"
            "* GRAMÁTICA: Fluidez total, sin palabras cortadas ni espacios extra.\n"
            "* CIERRE: Finaliza siempre con: '¿Desea que le asista con algún otro platillo?'."
        )
        
        try:
            # Llamada a la API estable (v1)
            response = model.generate_content(instrucciones + prompt)
            texto_final = response.text
            
            st.markdown(texto_final)
            st.session_state.messages.append({"role": "assistant", "content": texto_final})
            
        except Exception as e:
            st.error(f"¡Chispazo! Google está validando tus créditos. Intenta en un momento. (Error: {e})")
