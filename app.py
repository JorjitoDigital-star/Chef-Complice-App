import streamlit as st
import google.generativeai as genai
import time

# 1. ESTILO VISUAL: Optimizado para legibilidad y elegancia en móviles
st.set_page_config(page_title="Tu Chefcito 👨‍🍳", page_icon="👨‍🍳")

st.markdown("""
    <style>
    /* Tipografía grande y clara */
    .stChatMessage, p, li, div {
        font-size: 24px !important;
        line-height: 1.5 !important;
        color: #1A1A1A;
    }
    /* El Recetario: Caja destacada con estilo profesional */
    .recetario-chef {
        background-color: #FDFDFD;
        padding: 25px;
        border-radius: 15px;
        border-left: 8px solid #D0021B;
        margin-top: 15px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.08);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Tu Chefcito")

# 2. CONEXIÓN SEGURA A GOOGLE AI
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Error: Configure la API Key en los Secrets de Streamlit.")
    st.stop()

@st.cache_resource
def configurar_modelo():
    try:
        # Buscamos el modelo más estable y rápido
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for p in ['models/gemini-1.5-flash', 'models/gemini-pro']:
            if p in modelos: return genai.GenerativeModel(p)
        return genai.GenerativeModel(modelos[0])
    except: return genai.GenerativeModel('gemini-1.5-flash')

model = configurar_modelo()

# 3. GESTIÓN DE LA CONVERSACIÓN
if "messages" not in st.session_state:
    st.session_state.messages = []
    bienvenida = "¡Hola, hola! 👨‍🍳✨ ¡Qué alegría saludarte! Soy **Tu Chefcito**, tu guía culinario personal. Cuéntame, ¿qué ingredientes tienes a la mano hoy y qué vamos a crear juntos?"
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# 4. LÓGICA DE INTELIGENCIA Y PERSONALIDAD (CERO PDFS)
if prompt := st.chat_input("¿Qué cocinamos hoy?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # EL MANIFIESTO DE TU CHEFCITO
        instrucciones = (
            "Eres 'Tu Chefcito', un experto culinario con 15 años de experiencia. Tu misión es ayudar a personas con pocos ingredientes o falta de ideas, dándoles soluciones sabrosas, nutritivas e ingeniosas.\n\n"
            "REGLAS CRÍTICAS DE CALIDAD:\n"
            "1. IDENTIDAD: Tú eres 'Tu Chefcito'. No te saludes a ti mismo. Sé directo y alegre.\n"
            "2. GRAMÁTICA: Texto fluido. PROHIBIDO separar palabras en sílabas (ej. NO 'Pol lo'). Escribe con elegancia y mayúsculas tras puntos.\n"
            "3. DINERS (COMENSALES): Si piden receta y no sabes para cuántos es, PREGUNTA: '¡Excelente! Pero antes de empezar, ¿para cuántas personas cocinaremos hoy?'. Si ya lo sabes, no lo repitas.\n"
            "4. NUTRICIÓN Y 50/25/25: Sé muy breve. Una sola línea para nutrición y una lista simple para el equilibrio. No des teorías largas.\n"
            "5. PASOS SENSORIALES: No escribas testamentos, pero describe colores y aromas. Que se sienta el toque humano y experto. Usa máximo 2 líneas por paso.\n"
            "6. NO REPETIR: Si ya diste una receta, no la vuelvas a escribir. Si piden postre o sopa después, ve directo a esa preparación de forma ágil.\n"
            "7. CIERRE DINÁMICO: Si el usuario sigue preguntando, termina con: '¿Desea que le asista con algún otro platillo?'.\n"
            "8. DESPEDIDA CORDIAL: Si el usuario indica que terminó (ej. 'gracias', 'es todo'), despidete con calidez dejando saber que estarás ahí para lo que necesite siempre.\n"
            "9. TONO: Amigable, divertido y recursivo (Chef MacGyver). CERO lenguaje cursi (nada de 'mi vida' o 'corazón').\n\n"
        )
        
        try:
            # Construcción de historial compatible (User -> Model)
            historial_google = []
            for m in st.session_state.messages[:-1]:
                rol = "user" if m["role"] == "user" else "model"
                historial_google.append({"role": rol, "parts": [m["content"]]})

            chat = model.start_chat(history=historial_google)
            response = chat.send_message(instrucciones + prompt, stream=True)
            
            def stream_data():
                for chunk in response:
                    if chunk.text:
                        # Limpieza de espacios dobles para evitar tartamudez gramatical
                        texto_limpio = chunk.text.replace("  ", " ").replace(" .", ".")
                        for word in texto_limpio.split(" "):
                            yield word + " "
                            time.sleep(0.01)

            full_text = st.write_stream(stream_data())
            
            # Formateo estético para platos principales
            if "Paso a Paso" in full_text:
                output = f'<div class="recetario-chef">{full_text}</div>'
            else:
                output = full_text
                
            st.session_state.messages.append({"role": "assistant", "content": output})
            
        except Exception as e:
            st.error(f"¡Vaya! Hubo un pequeño chispazo en el fogón. ¿Podrías repetirme eso? (Error: {e})")
