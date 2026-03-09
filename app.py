import streamlit as st
import google.generativeai as genai

# 1. ESTILO VISUAL: Maximizado para lectura cómoda (24px)
st.set_page_config(page_title="Tu Chefcito 👨‍🍳", page_icon="👨‍🍳")
st.markdown("<style>.stChatMessage, p, li { font-size: 24px !important; line-height: 1.5; }</style>", unsafe_allow_html=True)

st.title("👨‍🍳 Tu Chefcito")

# 2. CONEXIÓN PROFESIONAL (Forzando versión estable)
if "GOOGLE_API_KEY" in st.secrets:
    # Usamos transport='rest' para saltar errores de red en la región
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"], transport='rest')
else:
    st.error("Configura la API Key en los Secrets de Streamlit.")
    st.stop()

# Especificamos la ruta completa del modelo de producción
model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')

# 3. GESTIÓN DEL CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Saludo guía que me pediste
    bienvenida = ("¡Hola! Soy **Tu Chefcito** 👨‍🍳. Para ayudarte hoy en **Perú**, dime: "
                  "¿Qué **ingredientes** tienes y para **cuántos** cocinamos?")
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. LÓGICA DE RESPUESTA (Sin streaming para evitar cortes)
if prompt := st.chat_input("Tengo arroz, yuca y pollo..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        instrucciones = (
            "Eres 'Tu Chefcito'. Responde en PRIMERA PERSONA.\n"
            "* Usa viñetas para cada párrafo o paso.\n"
            "* Fusiona Nutrición y Balance 50/25/25 en un solo bloque minimalista.\n"
            "* Cierre: '¿Desea que le asista con algún otro platillo?'."
        )
        
        try:
            # Llamada directa al contenido (v1 estable)
            response = model.generate_content(instrucciones + prompt)
            texto_final = response.text
            
            st.markdown(texto_final)
            st.session_state.messages.append({"role": "assistant", "content": texto_final})
            
        except Exception as e:
            st.error(f"Ajuste necesario en la consola: {e}")
