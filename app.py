import streamlit as st
import google.generativeai as genai

# 1. CONFIGURACIÓN VISUAL (24px para lectura clara en móviles)
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

# 2. CONEXIÓN ESTABLE (Corregido para evitar ValueError)
if "GOOGLE_API_KEY" in st.secrets:
    # Usamos la configuración estándar que reconoce créditos automáticamente
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"], transport='rest')
else:
    st.error("Error: Configura la GOOGLE_API_KEY en los Secrets.")
    st.stop()

# Definición del modelo de producción
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. GESTIÓN DE LA CONVERSACIÓN
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Mensaje de presentación guía solicitado
    bienvenida = (
        "¡Hola! Soy **Tu Chefcito** 👨‍🍳. Para ayudarte mejor, dime:\n\n"
        "* ¿En qué **país o región** estás?\n"
        "* ¿Qué **ingredientes** tienes?\n"
        "* ¿Para **cuántos comensales** cocinamos hoy?"
    )
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. LÓGICA DE RESPUESTA MAESTRA
if prompt := st.chat_input("Tengo arroz, papas y pollo..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Instrucciones de comportamiento y estilo
        instrucciones = (
            "Eres 'Tu Chefcito'. Habla siempre en PRIMERA PERSONA ('Yo te sugiero', 'Te ayudo').\n\n"
            "REGLAS CRÍTICAS:\n"
            "* Usa viñetas para cada párrafo y lista de pasos.\n"
            "* COMBINA en un solo bloque breve: El equilibrio 50/25/25 y la información nutricional.\n"
            "* PASOS: Sé breve y usa lenguaje sensorial (aromas, texturas, colores).\n"
            "* GRAMÁTICA: Escribe con fluidez natural, sin separar palabras por error.\n"
            "* CIERRE: Finaliza con: '¿Desea que le asista con algún otro platillo?'."
        )
        
        try:
            # Generación sin streaming para máxima estabilidad en la red
            response = model.generate_content(instrucciones + prompt)
            respuesta_texto = response.text
            
            st.markdown(respuesta_texto)
            st.session_state.messages.append({"role": "assistant", "content": respuesta_texto})
            
        except Exception as e:
            st.error(f"¡Chispazo! Google está terminando de vincular tus créditos. Intenta de nuevo en un minuto. (Error: {e})")
