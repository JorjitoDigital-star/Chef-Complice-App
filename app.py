import streamlit as st
import google.generativeai as genai

# 1. ESTILO Y CONFIGURACIÓN (24px para tu comodidad)
st.set_page_config(page_title="Tu Chefcito 👨‍🍳", page_icon="👨‍🍳")
st.markdown("<style>.stChatMessage, p, li { font-size: 24px !important; line-height: 1.5; }</style>", unsafe_allow_html=True)

st.title("👨‍🍳 Tu Chefcito")

# 2. EL AJUSTE EXPERTO (Aquí está la magia)
if "GOOGLE_API_KEY" in st.secrets:
    # Forzamos la versión 'v1' mediante client_options para evitar el error 404 de v1beta
    genai.configure(
        api_key=st.secrets["GOOGLE_API_KEY"], 
        transport='rest',
        client_options={'api_version': 'v1'} # <-- ESTA ES LA SOLUCIÓN DEFINITIVA
    )
else:
    st.error("Falta la API Key en los Secrets.")
    st.stop()

# Usamos el nombre del modelo estándar
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. INTERFAZ DE CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Saludo guía que diseñamos
    bienvenida = (
        "¡Hola! Soy **Tu Chefcito** 👨‍🍳. Para cocinar algo increíble hoy en **Perú**, dime:\n\n"
        "* ¿En qué **país o región** estás?\n"
        "* ¿Qué **ingredientes** tienes?\n"
        "* ¿Para **cuántos comensales** cocinamos?"
    )
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. PROCESAMIENTO DE RECETA
if prompt := st.chat_input("Tengo arroz, papas y pollo..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        instrucciones = (
            "Eres 'Tu Chefcito'. Responde siempre en PRIMERA PERSONA.\n\n"
            "REGLAS:\n"
            "* Usa viñetas para cada párrafo o paso.\n"
            "* FUSIONA en un solo bloque: Valor nutricional y el equilibrio 50/25/25.\n"
            "* PASOS: Sé breve, describe aromas y texturas.\n"
            "* CIERRE: '¿Desea que le asista con algún otro platillo?'."
        )
        
        try:
            # Llamada directa (ahora irá por v1 gracias al configure)
            response = model.generate_content(instrucciones + prompt)
            
            if response.text:
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            else:
                st.warning("El chef se quedó pensativo. Intenta reformular tu lista de ingredientes.")
                
        except Exception as e:
            st.error(f"Error de conexión: {e}. Verifica que tu API Key sea del proyecto 'Mi primer proyecto'.")
