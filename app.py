import streamlit as st
import google.generativeai as genai
import time

# 1. ESTILO VISUAL: Maximizado para móviles (24px)
st.set_page_config(page_title="Tu Chefcito 👨‍🍳", page_icon="👨‍🍳")

st.markdown("""
    <style>
    .stChatMessage, p, li, div {
        font-size: 24px !important;
        line-height: 1.5 !important;
        color: #1A1A1A;
    }
    .recetario-chef {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 10px;
        border-left: 8px solid #E63946;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Tu Chefcito")

# 2. CONFIGURACIÓN DE SEGURIDAD Y MOTOR
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la API Key en los Secrets.")
    st.stop()

# Ajuste para evitar bloqueos por palabras de cocina
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

@st.cache_resource
def configurar_modelo():
    # Usamos el nombre de modelo estable para evitar el error 404
    return genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        safety_settings=safety_settings
    )

model = configurar_modelo()

# 3. GESTIÓN DE LA CONVERSACIÓN
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Saludo guía solicitado
    bienvenida = (
        "¡Hola! Soy **Tu Chefcito** 👨‍🍳. Para cocinar algo increíble, dime:\n\n"
        "* ¿En qué **país o región** estás?\n"
        "* ¿Qué **ingredientes** tienes?\n"
        "* ¿Para **cuántos comensales** cocinamos?"
    )
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# 4. INTELIGENCIA CULINARIA
if prompt := st.chat_input("Dime tus ingredientes..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Instrucciones para la IA
        instrucciones = (
            "Eres 'Tu Chefcito'. Responde siempre en PRIMERA PERSONA.\n\n"
            "REGLAS:\n"
            "* Usa viñetas para cada párrafo o paso.\n"
            "* FUSIONA Nutrición y Balance 50/25/25 en una sola sección muy breve.\n"
            "* PASOS: Sé específico pero sensorial (olores, texturas). Máximo 2 líneas por paso.\n"
            "* GRAMÁTICA: No separes palabras. Escribe con fluidez natural.\n"
            "* CIERRE: Pregunta: '¿Desea que le asista con algún otro platillo?'.\n"
            "* DESPEDIDA: Si terminan, despídete con calidez profesional."
        )
        
        try:
            historial_google = []
            for m in st.session_state.messages[:-1]:
                rol = "user" if m["role"] == "user" else "model"
                historial_google.append({"role": rol, "parts": [m["content"]]})

            chat = model.start_chat(history=historial_google)
            # Forzamos la respuesta para evitar problemas de versión v1beta
            response = chat.send_message(instrucciones + prompt, stream=True)
            
            def stream_data():
                for chunk in response:
                    if chunk.text:
                        yield chunk.text.replace("  ", " ")
                        time.sleep(0.01)

            full_text = st.write_stream(stream_data())
            
            if "Equilibrio" in full_text:
                output = f'<div class="recetario-chef">{full_text}</div>'
            else:
                output = full_text
                
            st.session_state.messages.append({"role": "assistant", "content": output})
            
        except Exception as e:
            st.error(f"¡Chispazo en el fogón! Intenta de nuevo. (Error: {e})")
