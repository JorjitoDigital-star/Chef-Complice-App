import streamlit as st
import google.generativeai as genai

# 1. ESTILO VISUAL: 24px para tu comodidad
st.set_page_config(page_title="Tu Chefcito 👨‍🍳", page_icon="👨‍🍳")
st.markdown("""
    <style>
    .stChatMessage, p, li, div {
        font-size: 24px !important;
        line-height: 1.6 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Tu Chefcito")

# 2. CONEXIÓN ESTÁNDAR (La forma oficial)
if "GOOGLE_API_KEY" in st.secrets:
    # No forzamos transporte ni versiones extrañas
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Configura la nueva API Key en los Secrets.")
    st.stop()

# Usamos el nombre del modelo sin rutas largas
model = genai.GenerativeModel('gemini-1.5-flash')

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
            # Petición directa al grano
            response = model.generate_content(instrucciones + prompt)
            
            if response.text:
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            # Este mensaje te dirá si sigue intentando usar v1beta
            st.error(f"Error técnico detectado: {e}")
