import streamlit as st
import google.generativeai as genai
import time

# 1. CONFIGURACIÓN VISUAL (Optimizado para móvil)
st.set_page_config(page_title="Tu Chefcito 👨‍🍳", page_icon="👨‍🍳")

st.markdown("""
    <style>
    .stChatMessage, p, li, div {
        font-size: 26px !important;
        line-height: 1.5 !important;
        color: #1A1A1A;
    }
    .recetario-chef {
        background-color: #F9F9F9;
        padding: 25px;
        border-radius: 15px;
        border: 3px solid #D0021B;
        margin-top: 15px;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Tu Chefcito")

# 2. CONEXIÓN SEGURA
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Falta la API Key en los Secrets.")
    st.stop()

@st.cache_resource
def configurar_modelo():
    try:
        modelos = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for p in ['models/gemini-1.5-flash', 'models/gemini-pro']:
            if p in modelos: return genai.GenerativeModel(p)
        return genai.GenerativeModel(modelos[0])
    except: return genai.GenerativeModel('gemini-1.5-flash')

model = configurar_modelo()

# 3. GESTIÓN DE MEMORIA
if "messages" not in st.session_state:
    st.session_state.messages = []
    bienvenida = "¡Hola, hola! 👨‍🍳✨ ¡Qué alegría saludarte! Soy **Tu Chefcito**, tu guía culinario personal. Cuéntame, ¿qué ingredientes tienes a la mano hoy y qué rincón del mundo quieres saborear?"
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# 4. LÓGICA DE PERSONALIDAD Y RESPUESTA
if prompt := st.chat_input("¿Qué cocinamos con lo que hay?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # INSTRUCCIÓN MAESTRA DE IDENTIDAD Y CALIDAD
        instrucciones = (
            "Eres 'Tu Chefcito', un experto culinario global con 15 años de experiencia. Tu misión es ayudar a personas que no saben qué cocinar o que tienen pocos ingredientes, dándoles soluciones sabrosas y nutritivas.\n\n"
            "REGLAS CRÍTICAS:\n"
            "1. IDENTIDAD: Tú eres Tu Chefcito. NO te saludes a ti mismo (no digas 'Hola Chefcito'). Empieza directo con alegría.\n"
            "2. GRAMÁTICA: Escribe de forma fluida y profesional. Prohibido separar palabras en sílabas (ej. NO 'Pol lo', NO 'Pa pas'). Mayúsculas siempre al inicio y tras puntos.\n"
            "3. COMENSALES: Si el usuario pide una receta y NO ha dicho cuántos son, PREGUNTA: '¡Excelente idea! Pero antes de empezar, ¿para cuántas personas vamos a cocinar hoy?'. Si YA lo sabes por el historial, no lo repitas.\n"
            "4. NO REPETIR: Si ya diste una receta antes, NO la vuelvas a escribir. Si te piden un postre o sopa, da solo la información del postre o sopa de forma concisa.\n"
            "5. FORMATO: Solo para el PLATO PRINCIPAL usa: Nombre, Nutrición, 50/25/25, Paso a Paso, Residuo Cero y Toque Maestro. Para postres o bebidas, sé breve y ágil.\n"
            "6. TONO: Amigable, divertido y carismático, pero CERO CURSILERÍAS (nada de 'mi vida', 'corazón').\n"
            "7. CIERRE: Siempre termina preguntando: '¿Desea que le asista con algún otro platillo?'\n\n"
        )
        
        try:
            # Traducción de roles para Google
            historial_google = []
            for m in st.session_state.messages[:-1]:
                rol = "user" if m["role"] == "user" else "model"
                historial_google.append({"role": rol, "parts": [m["content"]]})

            chat = model.start_chat(history=historial_google)
            response = chat.send_message(instrucciones + prompt, stream=True)
            
            def stream_text():
                for chunk in response:
                    if chunk.text:
                        # Limpieza final de espacios dobles
                        texto_limpio = chunk.text.replace("  ", " ")
                        for word in texto_limpio.split(" "):
                            yield word + " "
                            time.sleep(0.01)

            full_text = st.write_stream(stream_text())
            
            # Formato estético para platos principales
            if "Paso a Paso" in full_text:
                output = f'<div class="recetario-chef">{full_text}</div>'
            else:
                output = full_text
                
            st.session_state.messages.append({"role": "assistant", "content": output})
        except Exception as e:
            st.error(f"¡Vaya! Hubo un pequeño chispazo en el fogón. ¿Podrías repetir eso? (Error: {e})")
