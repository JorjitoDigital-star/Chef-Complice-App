import streamlit as st
import google.generativeai as genai
import time

# 1. ESTILO VISUAL: Maximizado para lectura cómoda (24px)
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

# 2. CONFIGURACIÓN MAESTRA DE CONEXIÓN (El "Puente" Directo)
if "GOOGLE_API_KEY" in st.secrets:
    # AGREGAMOS transport='rest' para forzar la conexión estable y evitar el error v1beta
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"], transport='rest')
else:
    st.error("Falta la API Key en los Secrets de Streamlit.")
    st.stop()

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

@st.cache_resource
def configurar_modelo():
    # Usamos el nombre base del modelo para mayor compatibilidad con la cuota de pago
    return genai.GenerativeModel(
        model_name='gemini-1.5-flash',
        safety_settings=safety_settings
    )

model = configurar_modelo()

# 3. GESTIÓN DE LA CONVERSACIÓN
if "messages" not in st.session_state:
    st.session_state.messages = []
    bienvenida = (
        "¡Hola! Soy **Tu Chefcito** 👨‍🍳. Para cocinar algo increíble hoy en **Perú** o donde estés, dime:\n\n"
        "* ¿En qué **país o región** te encuentras?\n"
        "* ¿Qué **ingredientes** tienes a la mano?\n"
        "* ¿Para **cuántos comensales** vamos a cocinar?"
    )
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# 4. LÓGICA DE RESPUESTA
if prompt := st.chat_input("Dime tus ingredientes..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # INSTRUCCIONES DEL CHEF
        instrucciones = (
            "Eres 'Tu Chefcito'. Habla en PRIMERA PERSONA.\n\n"
            "REGLAS:\n"
            "* Usa viñetas para organizar los párrafos y listas.\n"
            "* FUSIONA Nutrición y Balance 50/25/25 en una sola sección minimalista.\n"
            "* PASOS: Breves y sensoriales. Describe aromas y texturas.\n"
            "* GRAMÁTICA: Escribe con fluidez natural. NUNCA separes sílabas con espacios.\n"
            "* CIERRE: Finaliza con: '¿Desea que le asista con algún otro platillo?'.\n"
        )
        
        try:
            historial_google = []
            for m in st.session_state.messages[:-1]:
                rol = "user" if m["role"] == "user" else "model"
                historial_google.append({"role": rol, "parts": [m["content"]]})

            chat = model.start_chat(history=historial_google)
            response = chat.send_message(instrucciones + prompt, stream=True)
            
            def stream_data():
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
                        time.sleep(0.01)

            full_text = st.write_stream(stream_data())
            
            # Formato visual para recetas
            if "Equilibrio" in full_text:
                output = f'<div class="recetario-chef">{full_text}</div>'
            else:
                output = full_text
                
            st.session_state.messages.append({"role": "assistant", "content": output})
            
        except Exception as e:
            st.error(f"¡Vaya chispazo! Revisa si la 'Generative Language API' está activa en tu consola. (Error: {e})")
