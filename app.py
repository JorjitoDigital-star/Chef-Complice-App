import streamlit as st
import google.generativeai as genai

# 1. ESTILO VISUAL: 24px para lectura cómoda mientras cocinas
st.set_page_config(page_title="Tu Chefcito 👨+🍳", page_icon="👨‍🍳")
st.markdown("""
    <style>
    .stChatMessage, p, li, div {
        font-size: 24px !important;
        line-height: 1.6 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍🍳 Tu Chefcito")

# 2. CONEXIÓN PROFESIONAL (Ruta Limpia)
# Usamos la nueva API Key que configuraste en los Secrets
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("Error: No se encontró la nueva GOOGLE_API_KEY en los Secrets.")
    st.stop()

# Definimos el modelo estándar de producción
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. GESTIÓN DEL CHAT (Historial en sesión)
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Saludo guía que me pediste
    bienvenida = (
        "¡Hola! Soy **Tu Chefcito** 👨‍🍳. Para ayudarte hoy en **Perú**, dime:\n\n"
        "* ¿En qué **país o región** te encuentras?\n"
        "* ¿Qué **ingredientes** tienes a la mano?\n"
        "* ¿Para **cuántos comensales** vamos a cocinar?"
    )
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})

# Mostrar mensajes previos
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 4. LÓGICA DE RESPUESTA DEL CHEF
if prompt := st.chat_input("Tengo arroz, pollo y papas..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Instrucciones de comportamiento del modelo
        instrucciones = (
            "Eres 'Tu Chefcito'. Habla siempre en PRIMERA PERSONA ('Yo te recomiendo', 'He pensado').\n\n"
            "REGLAS DE ORO:\n"
            "* Usa viñetas para cada párrafo y lista de pasos.\n"
            "* FUSIONA en un solo bloque breve: El equilibrio 50% vegetales / 25% proteína / 25% carbohidratos y el valor nutricional.\n"
            "* PASOS: Sé breve, usa lenguaje sensorial (aromas, texturas, colores).\n"
            "* GRAMÁTICA: Fluidez total, sin palabras cortadas ni errores de espaciado.\n"
            "* CIERRE: Finaliza siempre con: '¿Desea que le asista con algún otro platillo?'."
        )
        
        try:
            # Petición directa para máxima estabilidad
            response = model.generate_content(instrucciones + prompt)
            texto_respuesta = response.text
            
            st.markdown(texto_respuesta)
            st.session_state.messages.append({"role": "assistant", "content": texto_respuesta})
            
        except Exception as e:
            st.error(f"¡Chispazo! Google está sincronizando tu nueva llave. Reintenta en 10 segundos. (Error: {e})")
